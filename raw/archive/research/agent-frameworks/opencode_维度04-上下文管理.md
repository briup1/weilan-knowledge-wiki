# 维度：上下文管理 (Context Management)

## 1. 一句话定位

上下文管理是 OpenCode 的"信息组装车间"，将环境信息、项目指令、历史消息、文件附件等多源异构数据，按模型能力裁剪拼接为 LLM 可用的标准消息格式。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **模型不知道自己在哪工作**：如果没有 `SystemPrompt.environment`，LLM 不知道当前工作目录、git 状态、平台信息，可能读取错误的文件路径或执行不兼容的命令。
- **项目特定指令丢失**：如果没有 `InstructionPrompt.system`，AGENTS.md/CLAUDE.md 中的项目规范不会被加载，Agent 行为退化为通用模式，无法遵循团队约定。
- **消息格式错误导致 API 拒绝**：不同 provider 对 tool result 中的媒体支持不同（OpenAI 只支持字符串，Anthropic 支持 content 数组）。如果没有 `toModelMessages` 的适配层，调用 OpenAI 时传入媒体内容会直接报错。
- **上下文膨胀**：如果没有 `MessageV2.filterCompacted`， compaction 后的旧消息仍会被加载，浪费 token。

### 2.2 OpenCode 的具体触发条件

- **每次 loop 启动时**：`SystemPrompt.environment(model)` 和 `InstructionPrompt.system()` 被调用（`prompt.ts:L653`）
- **消息加载时**：`MessageV2.filterCompacted(MessageV2.stream(sessionID))` 过滤已压缩消息（`prompt.ts:L299`）
- **发送给 LLM 前**：`MessageV2.toModelMessages(msgs, model)` 转换格式（`prompt.ts:L666`）
- **读取文件时**：`InstructionPrompt.resolve` 按文件路径向上查找邻近指令文件（`instruction.ts:L168-191`）

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────────────────────────────────────────────────┐
│                    上下文组装流水线                            │
│                                                              │
│  [环境信息] ──► SystemPrompt.environment()                   │
│       │                                                      │
│  [项目指令] ──► InstructionPrompt.system()                   │
│       │                                                      │
│  [历史消息] ──► MessageV2.filterCompacted()                  │
│       │                                                      │
│  [格式转换] ──► MessageV2.toModelMessages()                  │
│       │                                                      │
│       ▼                                                      │
│  [Provider 适配] ──► ProviderTransform.schema()              │
│       │                                                      │
│       ▼                                                      │
│  [LLM 调用] ──► streamText({ messages, system, tools })      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **指令文件发现** | 按文件路径向上查找 AGENTS.md/CLAUDE.md | 固定位置或配置路径 | `instruction.ts:L177-188` 的 `while (current.startsWith(root))` 实现了邻近指令发现，适合 monorepo 中不同子项目有不同规范的场景 |
| **Provider 适配** | 在 `toModelMessages` 中硬编码 provider 能力判断 | 统一抽象层或配置驱动 | `message-v2.ts:L512-522` 按 `model.api.npm` 判断媒体支持，直接且精确 |
| **环境信息实时生成** | 每次 loop 重新生成 `environment()` | 缓存环境信息 | `system.ts:L29-53` 在每次调用时重新生成，确保工作目录、日期等信息始终最新 |
| **指令去重** | 用 `Map<messageID, Set<filepath>>` 跟踪已加载指令 | 不跟踪或每次全量加载 | `instruction.ts:L46-70` 的 `claims` 机制防止同一指令文件被重复加载 |

### 3.3 数据流/控制流

```
用户发送消息
    │
    v
[SessionPrompt.loop]
    │
    ├─► [MessageV2.stream] ──► 分页加载历史消息
    │       │
    │       ▼
    │   [MessageV2.filterCompacted] ──► 过滤已压缩消息
    │       │
    │       ▼
    │   返回 msgs（WithParts[]）
    │
    ├─► [SystemPrompt.environment(model)] ──► 生成环境信息
    │       │
    │       ▼
    │   ["Working directory: ...", "Platform: ..."]
    │
    ├─► [InstructionPrompt.system()] ──► 加载项目指令
    │       │
    │       ▼
    │   [AGENTS.md, CLAUDE.md, 远程 URL 指令]
    │
    ├─► 组装 system prompt ──► [...environment, ...instruction]
    │
    └─► [MessageV2.toModelMessages(msgs, model)] ──► 转换为 ModelMessage[]
            │
            ▼
    [LLM.stream] ──► 发送给模型
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：环境信息组装（SystemPrompt.environment）

**作用**：生成包含工作目录、git 状态、平台、日期等环境信息的 system prompt 片段。

**关键源码**（`packages/opencode/src/session/system.ts:29-53`）：
```typescript
export async function environment(model: Provider.Model) {
  const project = Instance.project
  return [
    [
      `You are powered by the model named ${model.api.id}. The exact model ID is ${model.providerID}/${model.api.id}`,
      `Here is some useful information about the environment you are running in:`,
      `<env>`,
      `  Working directory: ${Instance.directory}`,
      `  Is directory a git repo: ${project.vcs === "git" ? "yes" : "no"}`,
      `  Platform: ${process.platform}`,
      `  Today's date: ${new Date().toDateString()}`,
      `</env>`,
      `<directories>`,
      `  ${project.vcs === "git" && false ? await Ripgrep.tree({ cwd: Instance.directory, limit: 50 }) : ""}`,
      `</directories>`,
    ].join("\n"),
  ]
}
```

**这段代码为什么值得看**：
- 环境信息是实时生成的（`new Date().toDateString()`），不是缓存的，确保日期始终准确。
- `project.vcs === "git" && false` 是一个被禁用但保留代码的目录树展示功能，可能是性能考虑。
- 信息用 XML 标签（`<env>`, `<directories>`）包裹，便于 LLM 识别结构化信息。

### 机制 B：Provider-specific Prompt

**作用**：根据模型类型注入 provider 特定的 prompt 片段。

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
- 按模型 ID 字符串匹配（而非 provider 配置），简单直接。
- 不同 provider 的 prompt 以 `.txt` 文件形式导入（`import PROMPT_ANTHROPIC from "./prompt/anthropic.txt"`），便于维护。
- 默认回退到 `PROMPT_ANTHROPIC_WITHOUT_TODO`，说明项目最初为 Claude 设计，其他 provider 是后续适配的。

### 机制 C：指令文件动态加载（InstructionPrompt）

**作用**：动态加载项目级、全局和远程 URL 的指令文件，并去重。

**关键源码**（`packages/opencode/src/session/instruction.ts:72-115`）：
```typescript
export async function systemPaths() {
  const paths = new Set<string>()
  if (!Flag.OPENCODE_DISABLE_PROJECT_CONFIG) {
    for (const file of FILES) {
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
  // ... 处理 config.instructions
  return paths
}
```

**这段代码为什么值得看**：
- `break` 语句确保只加载第一个找到的指令文件（AGENTS.md > CLAUDE.md > CONTEXT.md），避免冲突。
- `Filesystem.findUp` 从当前目录向上查找，支持 monorepo 场景。
- 远程 URL 指令通过 `fetch` 加载，带 5 秒超时，防止阻塞。

### 机制 D：邻近指令发现（resolve）

**作用**：当 Agent 读取某个文件时，自动查找该文件所在路径及上级目录的指令文件。

**关键源码**（`packages/opencode/src/session/instruction.ts:168-191`）：
```typescript
export async function resolve(messages: MessageV2.WithParts[], filepath: string, messageID: string) {
  const system = await systemPaths()
  const already = loaded(messages)
  const results = []
  const target = path.resolve(filepath)
  let current = path.dirname(target)
  const root = path.resolve(Instance.directory)
  while (current.startsWith(root) && current !== root) {
    const found = await find(current)
    if (found && found !== target && !system.has(found) && !already.has(found) && !isClaimed(messageID, found)) {
      claim(messageID, found)
      const content = await Filesystem.readText(found).catch(() => undefined)
      if (content) results.push({ filepath: found, content: "Instructions from: " + found + "\n" + content })
    }
    current = path.dirname(current)
  }
  return results
}
```

**这段代码为什么值得看**：
- 实现了"邻近原则"：文件附近的指令比项目根目录的指令更相关。
- `isClaimed` / `claim` 机制防止同一消息中重复加载同一指令文件。
- 遍历到 `Instance.directory` 为止，不越界到项目外部。

### 机制 E：消息格式转换（toModelMessages）

**作用**：将内部 Part 格式转换为 AI SDK 兼容的 `ModelMessage` 格式，处理媒体注入和 provider 差异。

**关键源码**（`packages/opencode/src/session/message-v2.ts:496-555`）：
```typescript
export function toModelMessages(input: WithParts[], model: Provider.Model, options?: { stripMedia?: boolean }) {
  const supportsMediaInToolResults = (() => {
    if (model.api.npm === "@ai-sdk/anthropic") return true
    if (model.api.npm === "@ai-sdk/openai") return true
    if (model.api.npm === "@ai-sdk/amazon-bedrock") return true
    if (model.api.npm === "@ai-sdk/google") {
      const id = model.api.id.toLowerCase()
      return id.includes("gemini-3") && !id.includes("gemini-2")
    }
    return false
  })()
  // ... 遍历消息和 part，按 provider 能力转换格式
}
```

**这段代码为什么值得看**：
- 按 `model.api.npm` 硬编码判断，精确但不够灵活。新增 provider 需要修改此处。
- `stripMedia` 选项在 compaction 时使用，剥离媒体以减少 token。
- 对不支持的 provider，媒体附件会被转换为 `[Attached mime: filename]` 的文本占位符。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 依赖 | 初始化与环境 | 工作目录、git 状态、平台信息 | `Instance.directory`, `Instance.project` |
| 依赖 | 记忆系统 | 历史消息作为上下文输入 | `MessageV2.filterCompacted` |
| 输出到 | Prompt构建 | system prompt 片段 | `SystemPrompt.environment`, `InstructionPrompt.system` |
| 输出到 | LLM调用 | ModelMessage 数组 | `MessageV2.toModelMessages` |
| 依赖 | 配置系统 | 指令文件路径配置 | `Config.get().instructions` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **项目指令文件是稳定且少量的**：`break` 只加载第一个找到的指令文件，假设不会有大量冲突的指令文件。
2. **Provider 能力差异是静态的**：`supportsMediaInToolResults` 按 provider npm 包名硬编码，假设能力不会频繁变化。
3. **邻近指令比全局指令更相关**：`resolve` 从文件所在目录向上查找，假设局部规范优先于全局规范。

### 6.2 这个设计的代价/风险

1. **Provider 适配代码分散**：`toModelMessages` 的 provider 判断、llm.ts 的 `isCodex` 判断、system.ts 的 provider prompt 分发，多处硬编码导致新增 provider 时需要修改多个文件。
2. **指令文件加载顺序不透明**：用户可能不清楚 AGENTS.md、CLAUDE.md、远程 URL 的优先级和去重规则。
3. **环境信息没有缓存**：每次 loop 都重新生成，虽然数据量小，但 `Ripgrep.tree` 如果启用会有性能开销。

### 6.3 如果要重新设计，可能会改变什么

1. **Provider 能力抽象为配置**：将媒体支持、tool format 等能力声明移到 provider 配置中，而非硬编码在消息转换逻辑中。
2. **指令文件支持合并而非替换**：当前 `break` 只加载第一个，可以考虑合并多个指令文件的内容。
3. **环境信息增量更新**：缓存基础信息（如 git repo 状态），只更新易变信息（如日期）。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：上下文管理不是"拼接字符串"，而是一个**信息策展（curation）过程**。OpenCode 的设计表明，好的上下文管理需要解决三个问题：(1) 信息从哪来（环境、指令、历史）、(2) 信息怎么选（过滤、去重、邻近发现）、(3) 信息怎么给（按 provider 能力适配）。这三个问题如果处理不好，要么导致 LLM 行为不可预测（缺少指令），要么导致 API 报错（格式错误），要么导致 token 浪费（冗余上下文）。
