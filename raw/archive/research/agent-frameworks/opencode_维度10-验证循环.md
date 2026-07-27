# 维度：验证循环 (Validation Loop)

## 1. 一句话定位

验证循环是 OpenCode 的"质量守门员"，通过结构化输出强制、工具调用修复、参数校验和 Doom Loop 检测，确保 LLM 的输出符合预期格式和行为约束。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **结构化输出失败**：用户请求 JSON Schema 输出时，如果 LLM 直接返回文本而非调用 `StructuredOutput` 工具，下游解析会失败。
- **非法工具调用导致硬失败**：LLM 拼错工具名或传入无效参数时，如果没有修复机制，流会直接终止。
- **参数类型错误**：LLM 可能传入字符串而非数字，或遗漏必填字段，导致工具执行时崩溃。
- **无限循环**：LLM 可能陷入连续调用同一工具的循环，无限消耗 token。

### 2.2 OpenCode 的具体触发条件

- **用户请求 json_schema 输出时**：`prompt.ts:L614-622` 注入 `StructuredOutput` 工具
- **LLM 未调用 StructuredOutput 时**：`prompt.ts:L683-703` 设置 `StructuredOutputError`
- **工具名大小写不匹配时**：`llm.ts:L178-198` 自动修复
- **LLM 调用不存在工具时**：`llm.ts:L190-197` 降级为 `invalid` 工具
- **参数校验失败时**：`tool.ts:L48-88` 的 zod 校验抛出错误
- **连续 3 次相同工具调用时**：`processor.ts:L152-176` 触发 Doom Loop 检测

---

## 3. 核心设计思路

### 3.1 抽象模型

```
验证层级（从外到内）：

Layer 1: 结构化输出强制
    └──► 注入 StructuredOutput 工具 + toolChoice: "required"

Layer 2: 工具调用修复
    └──► 大小写纠正 / 降级为 invalid 工具

Layer 3: 参数校验
    └──► zod schema parse（Tool.define 自动包装）

Layer 4: 行为检测
    └──► Doom Loop 检测（连续相同工具调用）
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **结构化输出用工具模式** | 注入 `StructuredOutput` 工具 + `toolChoice: "required"` | 传统的 JSON mode 或 response_format | 工具模式有 schema 校验，比 JSON mode 更可靠 |
| **工具修复而非终止** | 大小写纠正 + 降级为 `invalid` | 直接报错终止 | 生产环境需要容错，小错误不应中断整个会话 |
| **zod 参数校验** | `Tool.define` 自动包装 `parameters.parse` | 手动校验或依赖模型自检 | zod 提供运行时类型安全，错误信息对 LLM 友好 |
| **Doom Loop 运行时检测** | 连续 3 次相同调用触发权限询问 | 静态限制或超时 | 运行时检测更灵活，不需要预设限制 |

### 3.3 数据流/控制流

```
[用户请求 json_schema]
    │
    ▼
[createStructuredOutputTool] ──► 注入工具 + toolChoice: "required"
    │
    ▼
[LLM 生成响应]
    │
    ├──► 调用了 StructuredOutput？
    │       ├──► YES ──► 执行工具，onSuccess 捕获输出 ──► break
    │       └──► NO ──► 设置 StructuredOutputError ──► break
    │
    ├──► 工具名大小写错误？
    │       └──► experimental_repairToolCall ──► 修复为小写
    │
    ├──► 工具不存在？
    │       └──► experimental_repairToolCall ──► 降级为 invalid
    │
    ├──► 参数无效？
    │       └──► zod parse ──► 抛出带 schema 提示的错误
    │
    └──► 连续 3 次相同调用？
            └──► Doom Loop 检测 ──► PermissionNext.ask
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：结构化输出强制

**作用**：当用户请求 JSON Schema 输出时，注入 `StructuredOutput` 工具并强制 LLM 调用它。

**关键源码**（`packages/opencode/src/session/prompt.ts:614-622, 683-703`）：
```typescript
// 注入 StructuredOutput 工具
if (lastUser.format?.type === "json_schema") {
  tools["StructuredOutput"] = createStructuredOutputTool({
    schema: lastUser.format.schema,
    onSuccess(output) { structuredOutput = output },
  })
}

// 检查是否调用了 StructuredOutput
if (structuredOutput !== undefined) {
  processor.message.structured = structuredOutput
  processor.message.finish = processor.message.finish ?? "stop"
  await Session.updateMessage(processor.message)
  break
}

// 模型未调用 StructuredOutput
if (modelFinished && !processor.message.error) {
  if (format.type === "json_schema") {
    processor.message.error = new MessageV2.StructuredOutputError({
      message: "Model did not produce structured output",
      retries: 0,
    }).toObject()
    await Session.updateMessage(processor.message)
    break
  }
}
```

**这段代码为什么值得看**：
- `toolChoice: "required"`（`prompt.ts:L678`）确保 LLM 必须调用某个工具（这里是 `StructuredOutput`）。
- `onSuccess` 回调将捕获的输出通过闭包传递给外层 loop。
- 如果 LLM 未调用 `StructuredOutput` 直接结束，设置 `StructuredOutputError` 并终止循环。

### 机制 B：非法工具调用修复

**作用**：对工具名大小写不匹配或调用不存在工具的情况进行自动修复。

**关键源码**（`packages/opencode/src/session/llm.ts:178-198`）：
```typescript
async experimental_repairToolCall(failed) {
  const lower = failed.toolCall.toolName.toLowerCase()
  if (lower !== failed.toolCall.toolName && tools[lower]) {
    return { ...failed.toolCall, toolName: lower }
  }
  return {
    ...failed.toolCall,
    input: JSON.stringify({ tool: failed.toolCall.toolName, error: failed.error.message }),
    toolName: "invalid",
  }
}
```

**这段代码为什么值得看**：
- 大小写错误是 LLM 常见的"手滑"，自动修复比报错更优雅。
- 降级为 `invalid` 工具保留了流式输出的连续性，错误信息作为 output 返回给 LLM。

### 机制 C：参数校验（zod）

**作用**：`Tool.define` 在 execute 前自动执行 zod 参数校验。

**关键源码**（`packages/opencode/src/tool/tool.ts:48-88`）：
```typescript
toolInfo.execute = async (args, ctx) =>> {
  try {
    toolInfo.parameters.parse(args)
  } catch (error) {
    if (error instanceof z.ZodError && toolInfo.formatValidationError) {
      throw new Error(toolInfo.formatValidationError(error), { cause: error })
    }
    throw new Error(
      `The ${id} tool was called with invalid arguments: ${error}.\nPlease rewrite the input...`,
      { cause: error },
    )
  }
  // ... 执行真实逻辑
}
```

**这段代码为什么值得看**：
- AOP 式包装：工具开发者只需定义 schema，校验自动执行。
- 错误信息包含 schema 提示，指导 LLM 在下一轮修正参数。

### 机制 D：Doom Loop 检测

**作用**：检测连续 3 次相同工具调用（相同工具名+相同参数），触发权限询问。

**关键源码**（`packages/opencode/src/session/processor.ts:152-176`）：
```typescript
const lastThree = parts.slice(-DOOM_LOOP_THRESHOLD)
if (lastThree.length === DOOM_LOOP_THRESHOLD &&
    lastThree.every(
      (p) =>
        p.type === "tool" &&
        p.tool === value.toolName &&
        p.state.status !== "pending" &&
        JSON.stringify(p.state.input) === JSON.stringify(value.input),
    )) {
  await PermissionNext.ask({
    permission: "doom_loop",
    patterns: [value.toolName],
    sessionID: input.assistantMessage.sessionID,
    metadata: { tool: value.toolName, input: value.input },
    always: [value.toolName],
    ruleset: agent.permission,
  })
}
```

**这段代码为什么值得看**：
- 检测条件精确：工具名相同 + 输入参数相同（通过 `JSON.stringify` 比较）。
- 在 `tool-call` 事件处理中内联执行，不增加额外扫描开销。
- 触发 `PermissionNext.ask` 而非直接终止，给用户决策权。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 依赖 | 编排循环 | 结构化输出检测在 loop 中 | `prompt.ts:L614-703` |
| 依赖 | 工具系统 | 参数校验、工具修复 | `tool.ts`, `llm.ts` |
| 输出到 | 错误处理 | StructuredOutputError、参数错误 | `message-v2.ts` |
| 输出到 | 安全防护 | Doom Loop 触发权限询问 | `permission/next.ts` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **LLM 的输出是不完美的**：需要多层校验和修复机制。
2. **工具模式比 JSON mode 更可靠**：结构化输出通过工具调用实现。
3. **用户应该对异常行为有决策权**：Doom Loop 检测触发 `ask` 而非自动终止。

### 6.2 这个设计的代价/风险

1. **StructuredOutput 依赖 toolChoice**：某些 provider 可能不完全支持 `toolChoice: "required"`。
2. **zod 错误信息可能过长**：复杂 schema 的校验错误信息可能超出上下文窗口。
3. **Doom Loop 阈值固定**：3 次是经验值，不适合所有场景。

### 6.3 如果要重新设计，可能会改变什么

1. **结构化输出增加重试**：当前未调用 `StructuredOutput` 直接终止，可以增加重试机制。
2. **Doom Loop 动态阈值**：根据工具类型和历史成功率调整。
3. **参数校验错误分级**：区分"可修复错误"（类型不匹配）和"不可修复错误"（缺失必填字段）。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：验证循环不是"事后检查"，而是一个**内建于流程的多层防御体系**。OpenCode 的设计表明，生产级 Agent 需要从四个层面保证输出质量：(1) 强制正确输出格式（StructuredOutput 工具）、(2) 修复常见错误（大小写纠正）、(3) 拦截非法输入（zod 校验）、(4) 检测异常行为模式（Doom Loop）。这四层防线缺一不可，缺少任何一层都会让系统在面对"不完美"的 LLM 时变得脆弱。
