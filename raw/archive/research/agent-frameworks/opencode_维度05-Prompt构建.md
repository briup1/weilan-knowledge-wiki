# 维度：Prompt 构建 (Prompt Building)

## 1. 一句话定位

Prompt 构建是 OpenCode 的"指令编译器"，将 Agent 配置、Provider 特性、项目指令、用户自定义提示等多层异构来源，按严格优先级组装为最终的 system prompt 序列。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **模型行为不可预测**：如果没有 provider-specific prompt，不同模型（Claude/GPT/Gemini）收到相同的 prompt 可能产生截然不同的行为。例如 Claude 支持 todo 列表，而 Qwen 不需要，混淆会导致无效输出。
- **Agent 角色混淆**：如果没有 Agent-specific prompt，`build` agent 和 `plan` agent 会收到相同的指令，导致 plan agent 意外执行编辑操作。
- **项目上下文丢失**：如果没有指令文件加载机制，AGENTS.md 中的团队规范不会被注入，Agent 无法遵循项目约定（如编码风格、测试框架选择）。
- **Prompt 缓存失效**：如果没有 2-part system 结构维护，Anthropic/Gemini 的 prompt caching 优化无法生效，每次请求都重新计费。

### 2.2 OpenCode 的具体触发条件

- **每次 LLM 调用前**：`llm.ts:L67-93` 组装 system prompt
- **Agent 切换时**：不同 agent 的 `prompt` 字段被注入（`agent.ts:L42`）
- **用户发送带 `@agent` 的消息时**：`prompt.ts:L1263-1285` 自动追加 task 工具调用提示
- **结构化输出模式时**：`prompt.ts:L655-657` 注入 `STRUCTURED_OUTPUT_SYSTEM_PROMPT`

---

## 3. 核心设计思路

### 3.1 抽象模型

```
system prompt 分层组装（优先级从高到低）：

Layer 1: Plugin transform      ──► experimental.chat.system.transform
Layer 2: User message system   ──► input.user.system
Layer 3: Call-level system     ──► input.system
Layer 4: Agent prompt          ──► input.agent.prompt
Layer 5: Provider prompt       ──► SystemPrompt.provider(model)

注意：LLM.ts 的 system 数组是逆序组装的（provider 先 push），
      但 Plugin transform 可以重新排列。
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **Agent prompt 优先于 provider prompt** | 如果 agent 定义了 prompt，跳过 provider prompt | 总是合并两者 | `llm.ts:L72` 的 `input.agent.prompt ? [input.agent.prompt] : ... SystemPrompt.provider()`，让 agent 可以完全覆盖 provider 行为 |
| **2-part system 结构** | 维护 header + rest 两部分，header 不变时缓存命中 | 单一部分或按来源分多部分 | `llm.ts:L82-93` 的 2-part 结构专门用于 Anthropic/Gemini 的 prompt caching |
| **指令文件向上查找** | 按文件路径向上查找 AGENTS.md/CLAUDE.md | 固定路径或配置 | `instruction.ts:L177-188` 支持 monorepo 中不同子项目的不同规范 |
| **Plugin 可修改 system** | `experimental.chat.system.transform` hook | 不可修改的静态组装 | 提供扩展点，让插件可以注入额外上下文（如企业策略） |

### 3.3 数据流/控制流

```
[Agent.get(lastUser.agent)] ──► 获取 agent 配置（包含 prompt）
    │
    ├─► [SystemPrompt.provider(model)] ──► provider-specific prompt
    │
    ├─► [input.system] ──► 调用方传入的 system
    │
    ├─► [input.user.system] ──► 用户消息附带的 system
    │
    ▼
[组装为 system 数组] ──► llm.ts:L67-80
    │
    ▼
[Plugin.trigger("experimental.chat.system.transform")] ──► 插件可修改
    │
    ▼
[维护 2-part 结构] ──► llm.ts:L82-93
    │
    ▼
[注入结构化输出指令] ──► prompt.ts:L655-657
    │
    ▼
[streamText({ messages: [...system.map(...), ...input.messages] })]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：System Prompt 分层组装

**作用**：将多层来源的 prompt 按优先级组装为 system 消息数组。

**关键源码**（`packages/opencode/src/session/llm.ts:67-93`）：
```typescript
const system = []
system.push(
  [
    // use agent prompt otherwise provider prompt
    ...(input.agent.prompt ? [input.agent.prompt] : isCodex ? [] : SystemPrompt.provider(input.model)),
    // any custom prompt passed into this call
    ...input.system,
    // any custom prompt from last user message
    ...(input.user.system ? [input.user.system] : []),
  ]
    .filter((x) => x)
    .join("\n"),
)

const header = system[0]
await Plugin.trigger("experimental.chat.system.transform", { sessionID: input.sessionID, model: input.model }, { system })
// rejoin to maintain 2-part structure for caching if header unchanged
if (system.length > 2 && system[0] === header) {
  const rest = system.slice(1)
  system.length = 0
  system.push(header, rest.join("\n"))
}
```

**这段代码为什么值得看**：
- Agent prompt 优先于 provider prompt，说明 agent 的角色定义比模型特性更重要。
- Codex 模式特殊处理：跳过 `SystemPrompt.provider()`，因为 Codex 通过 `options.instructions` 传入指令。
- Plugin hook 在 system 数组组装后触发，允许插件重新排列或修改内容。

### 机制 B：Provider-specific Prompt

**作用**：根据模型类型注入特定的行为指导 prompt。

**关键源码**（`packages/opencode/src/session/system.ts:19-27`）：
```typescript
export function provider(model: Provider.Model) {
  if (model.api.id.includes("gpt-5")) return [PROMPT_CODEX]
  if (model.api.id.includes("gpt-") || model.api.id.includes("o1") || model.api.id.includes("o3"))
    return [PROMPT_BEAST]
  if (model.api.id.includes("gemini-")) return [PROMPT_GEMINI]
  if (model.api.id.includes("claude")) return [PROMPT_ANTHROPIC]
  if (model.api.id.toLowerCase().includes("trinity")) return [PROMPT_TRINITY]
  return [PROMPT_ANTHROPIC_WITHOUT_TODO]
}
```

**这段代码为什么值得看**：
- 按模型 ID 子字符串匹配，简单直接。
- 不同 provider 的 prompt 存储在 `.txt` 文件中，通过 `import` 加载，便于维护。
- 默认回退到 `PROMPT_ANTHROPIC_WITHOUT_TODO`，说明项目最初为 Claude 优化。

### 机制 C：指令文件动态加载

**作用**：从项目目录和全局配置加载 AGENTS.md/CLAUDE.md 等指令文件。

**关键源码**（`packages/opencode/src/session/instruction.ts:72-115`）：
```typescript
export async function systemPaths() {
  const paths = new Set<string>()
  if (!Flag.OPENCODE_DISABLE_PROJECT_CONFIG) {
    for (const file of FILES) {  // ["AGENTS.md", "CLAUDE.md", "CONTEXT.md"]
      const matches = await Filesystem.findUp(file, Instance.directory, Instance.worktree)
      if (matches.length > 0) {
        matches.forEach((p) => paths.add(path.resolve(p)))
        break  // 只加载第一个找到的
      }
    }
  }
  for (const file of globalFiles()) {
    if (await Filesystem.exists(file)) {
      paths.add(path.resolve(file))
      break
    }
  }
  // ... 远程 URL 指令
  return paths
}
```

**这段代码为什么值得看**：
- `break` 确保只加载第一个找到的指令文件，优先级：AGENTS.md > CLAUDE.md > CONTEXT.md。
- `Filesystem.findUp` 从当前目录向上查找，支持 monorepo。
- 远程 URL 指令通过 `fetch` 加载，带 5 秒超时。

### 机制 D：Agent-specific Prompt

**作用**：每个内置 agent 有自己的 prompt 配置，定义其行为模式。

**关键源码**（`packages/opencode/src/agent/agent.ts:76-203`）：
```typescript
const result: Record<string, Info> = {
  build: {
    name: "build",
    description: "The default agent. Executes tools based on configured permissions.",
    options: {},
    permission: PermissionNext.merge(...),
    mode: "primary",
    native: true,
  },
  plan: {
    name: "plan",
    description: "Plan mode. Disallows all edit tools.",
    permission: PermissionNext.merge(
      defaults,
      PermissionNext.fromConfig({ edit: { "*": "deny" }, ... }),
    ),
    mode: "primary",
    native: true,
  },
  compaction: {
    name: "compaction",
    description: "...",
    prompt: `Provide a detailed prompt for continuing our conversation...`,
    mode: "subagent",
  },
  // ...
}
```

**这段代码为什么值得看**：
- `compaction` agent 的 prompt 定义了五部分摘要模板（Goal/Instructions/Discoveries/Accomplished/Relevant files）。
- `plan` agent 通过权限配置禁用 edit 工具，而非在 prompt 中说明。
- Agent 的 `mode` 字段（"primary"/"subagent"/"all"）控制其在哪些场景可用。

### 机制 E：2-part System 缓存优化

**作用**：维护 "header + rest" 的 2-part system 结构，利用 Anthropic/Gemini 的 prompt caching。

**关键源码**（`packages/opencode/src/session/llm.ts:82-93`）：
```typescript
const header = system[0]
await Plugin.trigger("experimental.chat.system.transform", ..., { system })
// rejoin to maintain 2-part structure for caching if header unchanged
if (system.length > 2 && system[0] === header) {
  const rest = system.slice(1)
  system.length = 0
  system.push(header, rest.join("\n"))
}
```

**这段代码为什么值得看**：
- Prompt caching 要求 system prompt 分为 "static prefix" 和 "dynamic suffix" 两部分。
- `system[0] === header` 检查确保 plugin 没有修改 header，否则缓存失效。
- 这是针对特定 provider 优化的设计，但代码中并未检查 provider 是否支持 caching。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 依赖 | 上下文管理 | 环境信息、指令文件 | `SystemPrompt.environment`, `InstructionPrompt.system` |
| 依赖 | 编排循环 | 当前 agent 配置 | `Agent.get(lastUser.agent)` |
| 输出到 | LLM调用 | 最终 system prompt | `streamText({ messages: [...system...] })` |
| 依赖 | 插件系统 | Plugin 可修改 system | `experimental.chat.system.transform` |
| 输出到 | 验证循环 | 结构化输出指令注入 | `STRUCTURED_OUTPUT_SYSTEM_PROMPT` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **Agent 的角色定义优先于模型特性**：Agent prompt 覆盖 provider prompt，说明作者认为"做什么"比"用什么模型做"更重要。
2. **Prompt caching 是重要优化**：专门维护 2-part 结构，假设 caching 能显著降低成本。
3. **项目指令文件是稀缺的**：`break` 只加载第一个，假设不会有大量冲突的指令文件。
4. **Plugin 需要修改 system 的能力**：提供 `experimental.chat.system.transform` hook，假设插件需要注入额外上下文。

### 6.2 这个设计的代价/风险

1. **2-part 结构是隐式契约**：任何 plugin 修改 system 数组后都需要重新检查这个不变量，否则 caching 失效。
2. **Provider prompt 按字符串匹配**：模型 ID 变化（如新版本）可能导致匹配失败，回退到不合适的默认 prompt。
3. **指令文件加载顺序不透明**：用户可能不清楚 AGENTS.md 和 CLAUDE.md 的优先级。
4. **Agent prompt 和 provider prompt 互斥**：如果 agent 定义了 prompt，就完全跳过 provider prompt，可能丢失 provider 特有的行为指导。

### 6.3 如果要重新设计，可能会改变什么

1. **合并 Agent prompt 和 provider prompt**：而非二选一，让 agent prompt 作为 override 层，provider prompt 作为 base 层。
2. **Provider 匹配配置化**：将模型 ID 匹配规则移到配置文件中，而非硬编码在代码中。
3. **指令文件支持合并**：当前 `break` 只加载第一个，可以改为合并多个文件的内容。
4. **2-part 结构显式化**：用 `system: { header: string, rest: string }` 的结构替代数组操作，避免隐式契约。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：Prompt 构建不是"拼接文本"，而是一个**分层覆盖系统**。OpenCode 的五层优先级（Agent > Provider > Call-level > User > Plugin）确保了"最具体的定义覆盖最通用的定义"。在设计自己的 Agent 系统时，应该尽早定义 prompt 的分层体系，因为随着功能增加，prompt 来源会越来越多（模型适配、项目规范、用户偏好、插件扩展），没有分层体系会导致混乱和冲突。
