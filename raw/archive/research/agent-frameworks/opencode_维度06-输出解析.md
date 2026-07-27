# 维度：输出解析 (Output Parsing)

## 1. 一句话定位

输出解析是 OpenCode 的"流式翻译官"，将 AI SDK 的原始流式事件（text-delta、tool-call、reasoning 等）翻译为内部 Part 状态更新，并内建非法工具调用修复和 Doom Loop 检测等防御机制。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **流式输出丢失**：如果没有 `for await...of stream.fullStream` 消费流式事件，LLM 的回复只会作为整体返回，用户看不到实时打字效果，也无法在工具执行时看到进度。
- **工具调用无法执行**：如果没有解析 `tool-call` 事件并提取工具名和参数，LLM 生成的工具调用意图永远不会被执行，Agent 无法与外部世界交互。
- **非法工具调用导致硬失败**：LLM 可能拼错工具名（大小写错误）或传入无效参数。如果没有 `experimental_repairToolCall`，这些错误会直接终止流，用户体验极差。
- **Doom Loop 无限制**：如果 LLM 陷入循环（连续多次调用同一工具），没有检测机制的话会无限消耗 token 和 API 配额。

### 2.2 OpenCode 的具体触发条件

- **每次 LLM 流式响应时**：`processor.ts:L55` 开始消费 `stream.fullStream`
- **工具名大小写不匹配时**：`llm.ts:L178-198` 的 `experimental_repairToolCall` 触发
- **LLM 调用不存在的工具时**：`llm.ts:L190-197` 降级为 `invalid` 工具
- **连续 3 次相同工具调用时**：`processor.ts:L152-176` 的 Doom Loop 检测触发
- **流式过程中发生错误时**：`message-v2.ts:L827-913` 的 `fromError` 统一转换

---

## 3. 核心设计思路

### 3.1 抽象模型

```
AI SDK Stream Event ──► Event Router ──► Part State Machine
                                          │
    ├─► text-delta      ──► text part 追加
    ├─► tool-call       ──► tool part 创建 + 执行
    ├─► tool-result     ──► tool part 更新为 completed
    ├─► tool-error      ──► tool part 更新为 error
    ├─► reasoning-delta ──► reasoning part 追加
    ├─► step-start      ──► step-start part 创建（快照追踪）
    ├─► step-finish     ──► step-finish part 创建（统计+快照）
    └─► error           ──► 抛出异常，进入 catch 块
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **流式消费** | `for await...of stream.fullStream` | 等待完整响应后解析 | 流式消费支持实时 UI 更新，减少用户等待感知 |
| **事件路由** | `switch(value.type)` 硬编码处理 | 插件化事件处理器注册表 | 简单直接，但新增事件类型需要修改核心代码 |
| **工具修复** | `experimental_repairToolCall`（大小写纠正 + 降级） | 直接报错终止 | `llm.ts:L178-198` 将常见错误（大小写）自动修复，将严重错误（不存在工具）降级为 `invalid` 工具返回友好错误 |
| **Doom Loop 检测** | 连续 3 次相同工具调用触发权限询问 | 固定次数限制或超时 | `processor.ts:L152-176` 在运行时动态检测，比静态限制更灵活 |

### 3.3 数据流/控制流

```
[LLM.stream] ──► 返回 StreamTextResult
    │
    ▼
[SessionProcessor.process] ──► for await (value of stream.fullStream)
    │
    ├─► "start" ──► SessionStatus.set(busy)
    │
    ├─► "reasoning-start/delta/end" ──► 创建/更新/关闭 reasoning part
    │
    ├─► "tool-input-start" ──► 创建 tool part（status: pending）
    │
    ├─► "tool-call" ──► 更新 tool part（status: running）
    │       │
    │       ├─► Doom Loop 检测？──► PermissionNext.ask()
    │       │
    │       └─► 执行工具 ──► 返回 result
    │
    ├─► "tool-result" ──► 更新 tool part（status: completed）
    │
    ├─► "tool-error" ──► 更新 tool part（status: error）
    │       │
    │       └─► RejectedError/Question.RejectedError？──► blocked = true
    │
    ├─► "step-start" ──► 创建 step-start part（记录快照）
    │
    ├─► "step-finish" ──► 创建 step-finish part（统计 token/cost）
    │       │
    │       └─► Snapshot.patch() ──► 如果有文件变更，创建 patch part
    │
    ├─► "text-start/delta/end" ──► 创建/追加/关闭 text part
    │
    └─► "error" ──► 抛出异常
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：流式事件解析

**作用**：消费 AI SDK 的流式事件，按类型路由到对应的处理逻辑。

**关键源码**（`packages/opencode/src/session/processor.ts:55-176`）：
```typescript
for await (const value of stream.fullStream) {
  input.abort.throwIfAborted()
  switch (value.type) {
    case "start":
      SessionStatus.set(input.sessionID, { type: "busy" })
      break
    case "reasoning-start":
      // 创建 reasoning part
    case "tool-call": {
      const match = toolcalls[value.toolCallId]
      if (match) {
        const part = await Session.updatePart({...match, state: { status: "running", input: value.input }})
        toolcalls[value.toolCallId] = part as MessageV2.ToolPart
        // Doom Loop 检测
        const lastThree = parts.slice(-DOOM_LOOP_THRESHOLD)
        if (lastThree.length === DOOM_LOOP_THRESHOLD &&
            lastThree.every(p => p.tool === value.toolName &&
              JSON.stringify(p.state.input) === JSON.stringify(value.input))) {
          await PermissionNext.ask({ permission: "doom_loop", ... })
        }
      }
      break
    }
    // ... 更多 case
  }
}
```

**这段代码为什么值得看**：
- `input.abort.throwIfAborted()` 在每个事件开始时检查取消信号，确保及时响应。
- Doom Loop 检测在 `tool-call` 事件处理中内联执行，不增加额外扫描开销。
- `toolcalls[value.toolCallId]` 用 Map 追踪 pending 工具调用，支持并行工具执行。

### 机制 B：工具调用修复

**作用**：当 LLM 调用非法工具时，尝试自动修复或降级为 `invalid` 工具。

**关键源码**（`packages/opencode/src/session/llm.ts:178-198`）：
```typescript
async experimental_repairToolCall(failed) {
  const lower = failed.toolCall.toolName.toLowerCase()
  if (lower !== failed.toolCall.toolName && tools[lower]) {
    // 大小写不匹配，修复为小写
    return { ...failed.toolCall, toolName: lower }
  }
  // 工具不存在，降级为 invalid 工具
  return {
    ...failed.toolCall,
    input: JSON.stringify({ tool: failed.toolCall.toolName, error: failed.error.message }),
    toolName: "invalid",
  }
}
```

**这段代码为什么值得看**：
- 大小写错误是 LLM 常见的"手滑"，自动修复比报错更优雅。
- 降级为 `invalid` 工具而非直接终止，保留了流式输出的连续性。
- `invalid` 工具的 execute 返回错误信息作为 output，让 LLM 在下一轮知道调用失败了。

### 机制 C：错误统一转换

**作用**：将 AI SDK 的各种异常统一转换为内部 `NamedError` 类型。

**关键源码**（`packages/opencode/src/session/message-v2.ts:827-913`）：
```typescript
export function fromError(e: unknown, ctx: { providerID: string }) {
  switch (true) {
    case e instanceof DOMException && e.name === "AbortError":
      return new MessageV2.AbortedError({ message: e.message }).toObject()
    case LoadAPIKeyError.isInstance(e):
      return new MessageV2.AuthError({ providerID: ctx.providerID, message: e.message }).toObject()
    case (e as SystemError)?.code === "ECONNRESET":
      return new MessageV2.APIError({ message: "Connection reset by server", isRetryable: true }).toObject()
    case APICallError.isInstance(e):
      const parsed = ProviderError.parseAPICallError({ providerID: ctx.providerID, error: e })
      if (parsed.type === "context_overflow")
        return new MessageV2.ContextOverflowError({ message: parsed.message }).toObject()
      return new MessageV2.APIError({...parsed}).toObject()
    // ...
  }
}
```

**这段代码为什么值得看**：
- `switch(true)` 配合 `case` 条件判断，是一种简洁的多类型分发模式。
- 每种错误类型都保留了原始错误作为 `cause`，便于调试。
- `ContextOverflowError` 被单独识别，触发 compaction 而非重试。

### 机制 D：结构化输出工具

**作用**：当用户请求 JSON Schema 输出时，注入 `StructuredOutput` 工具并强制模型调用它。

**关键源码**（`packages/opencode/src/session/prompt.ts:928-955`）：
```typescript
export function createStructuredOutputTool(input: { schema: Record<string, any>; onSuccess: (output: unknown) => void }): AITool {
  const { $schema, ...toolSchema } = input.schema
  return tool({
    id: "StructuredOutput",
    description: STRUCTURED_OUTPUT_DESCRIPTION,
    inputSchema: jsonSchema(toolSchema),
    async execute(args) {
      input.onSuccess(args)
      return { output: "Structured output captured successfully.", title: "Structured Output", metadata: { valid: true } }
    },
  })
}
```

**这段代码为什么值得看**：
- 用"工具调用"模式实现结构化输出，比传统的 JSON 模式更可靠（因为工具参数有 schema 校验）。
- `onSuccess` 回调将捕获的输出传递给外层 loop。
- `$schema` 被剥离，因为工具参数不需要 JSON Schema 的 `$schema` 属性。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 依赖 | 编排循环 | 消费 LLM 流式输出 | `SessionProcessor.process` |
| 输出到 | 工具系统 | 执行工具调用 | `tool-call` 事件处理 |
| 输出到 | 记忆系统 | 更新 Part 状态 | `Session.updatePart` |
| 依赖 | 错误处理 | 错误分类与恢复 | `fromError`, `catch` 块 |
| 依赖 | 安全防护 | Doom Loop 检测触发权限询问 | `PermissionNext.ask` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **LLM 输出是不完美的**：大小写错误、非法工具名、无效参数是常态而非异常，因此需要修复机制。
2. **流式消费是必需的**：用户需要实时反馈，不能等完整响应后再统一处理。
3. **工具调用是副作用的主要来源**：所有与外部世界的交互都通过工具调用，因此输出解析的核心是工具事件处理。

### 6.2 这个设计的代价/风险

1. **事件类型硬编码**：`switch(value.type)` 中的每个 case 都对应 AI SDK 的一个事件类型，SDK 升级时可能需要同步修改。
2. **Doom Loop 阈值固定**：`DOOM_LOOP_THRESHOLD` 是常量（3），没有根据场景动态调整。
3. **工具修复有副作用**：自动修复大小写可能掩盖模型理解问题；降级为 `invalid` 可能让模型困惑。

### 6.3 如果要重新设计，可能会改变什么

1. **事件处理插件化**：将事件处理逻辑注册为插件，便于扩展新的事件类型。
2. **Doom Loop 动态阈值**：根据工具类型和历史成功率动态调整阈值。
3. **工具修复增加日志**：记录每次修复的详细信息，便于分析模型质量。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：输出解析不是"读取 LLM 回复"那么简单，而是一个**容错翻译层**。OpenCode 的设计表明，生产级 Agent 必须内建三种防御机制：(1) 常见错误的自动修复（大小写纠正）、(2) 无法修复错误的优雅降级（invalid 工具）、(3) 异常行为的动态检测（Doom Loop）。这三种机制让系统在面对"不完美"的 LLM 时仍能保持稳定和可用。
