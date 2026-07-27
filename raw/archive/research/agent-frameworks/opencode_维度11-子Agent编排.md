# 维度：子 Agent 编排 (Sub-Agent Orchestration)

## 1. 一句话定位

子 Agent 编排是 OpenCode 的"任务委派系统"，通过 `TaskTool` 创建隔离的 child session，让专门的子 Agent（如 explore/general）处理特定类型的任务，并将结果汇总回父会话。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **单一 Agent 能力过载**：一个 Agent 需要同时处理代码编辑、文件探索、网络搜索等多种任务，prompt 变得冗长且冲突。
- **上下文污染**：子任务的大量工具输出（如全局搜索）会污染父会话的上下文，影响后续对话。
- **任务无法并行**：如果没有子 Agent，所有任务必须串行执行，效率低下。
- **权限无法隔离**：子任务可能需要不同的权限集合（如网络搜索需要 webfetch 权限，但主 Agent 不需要）。

### 2.2 OpenCode 的具体触发条件

- **用户发送 `@agent` 消息时**：`prompt.ts:L1263-1285` 自动追加 task 工具调用提示
- **主循环检测到 pending subtask 时**：`prompt.ts:L353-527` 直接内联执行
- **LLM 主动调用 `task` 工具时**：`TaskTool.execute` 被触发

---

## 3. 核心设计思路

### 3.1 抽象模型

```
父 Session
    │
    ├──► [主 Agent 循环]
    │       │
    │       └──► 检测到 subtask part / 用户 @agent
    │               │
    │               ▼
    │       [TaskTool.execute]
    │               │
    │               ├──► [Session.create({ parentID })] ──► child session
    │               │
    │               ├──► [权限继承 + 限制]
    │               │       └──► 禁用 todowrite/todoread，可选禁用 task（防递归）
    │               │
    │               ├──► [SessionPrompt.prompt] ──► 在 child session 运行子 Agent
    │               │
    │               └──► [结果汇总] ──► 返回 task_id + 输出文本
    │                       │
    │                       ▼
    │               [父会话继续]
    │
    └──► [父 Agent 继续主任务]
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **Child Session 隔离** | 创建独立的 Session（`parentID` 关联） | 在同一会话中内联执行 | 隔离上下文，避免子任务输出污染父会话 |
| **权限继承 + 限制** | 继承父会话权限，但禁用 todowrite/todoread | 完全独立权限或完全继承 | 防止子 Agent 修改父会话的 todo 列表，避免递归调用 task |
| **内联执行 subtask** | 主循环直接检测 subtask part 并执行 | 让 LLM 再次生成 tool-call | 减少 LLM 调用开销，精确控制上下文继承 |
| **任务可恢复** | `task_id` 支持恢复继续 | 一次性任务 | `task.ts:L67-70` 支持通过 task_id 恢复已有子会话 |

### 3.3 数据流/控制流

```
[用户 @agent 或系统插入 subtask]
    │
    ▼
[主循环检测到 subtask part]
    │
    ├──► [TaskTool.init()] ──► 获取工具定义
    │
    ├──► [Session.create({ parentID: ctx.sessionID })]
    │       │
    │       ├──► 继承父 session 上下文
    │       ├──► 设置 title: "description (@agent subagent)"
    │       └──► 配置权限（禁用 todo，可选禁用 task）
    │
    ├──► [SessionPrompt.prompt({ sessionID: child.id, agent: subagent_type })]
    │       │
    │       └──► 子 Agent 在 child session 中独立运行 loop
    │
    └──► [结果返回父会话]
            │
            ├──► task_id: child.id
            ├──► task_result: 子 Agent 的文本输出
            └──► 父 Agent 继续执行
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：TaskTool（子 Agent 调度）

**作用**：创建 child session，在子会话中运行子 Agent，并返回结果。

**关键源码**（`packages/opencode/src/tool/task.ts:45-102`）：
```typescript
async execute(params: z.infer<typeof parameters>, ctx) {
  // 权限检查（除非用户通过 @agent 显式调用）
  if (!ctx.extra?.bypassAgentCheck) {
    await ctx.ask({ permission: "task", patterns: [params.subagent_type], always: ["*"] })
  }

  const agent = await Agent.get(params.subagent_type)
  const hasTaskPermission = agent.permission.some((rule) => rule.permission === "task")

  // 创建 child session
  const session = await iife(async () => {
    if (params.task_id) {
      const found = await Session.get(params.task_id).catch(() => {})
      if (found) return found
    }
    return await Session.create({
      parentID: ctx.sessionID,
      title: params.description + ` (@${agent.name} subagent)`,
      permission: [
        { permission: "todowrite", pattern: "*", action: "deny" },
        { permission: "todoread", pattern: "*", action: "deny" },
        ...(hasTaskPermission ? [] : [{ permission: "task", pattern: "*", action: "deny" }]),
      ],
    })
  })

  // 在 child session 中运行子 Agent
  const result = await SessionPrompt.prompt({
    sessionID: session.id,
    model: agent.model ?? { modelID: msg.info.modelID, providerID: msg.info.providerID },
    agent: agent.name,
    tools: { todowrite: false, todoread: false, ...(hasTaskPermission ? {} : { task: false }) },
    parts: promptParts,
  })

  return {
    title: params.description,
    metadata: { sessionId: session.id },
    output: `task_id: ${session.id}\n\n<task_result>${text}</task_result>`,
  }
}
```

**这段代码为什么值得看**：
- `bypassAgentCheck` 支持用户通过 `@agent` 显式调用时跳过权限检查。
- `todowrite`/`todoread` 被禁用，防止子 Agent 修改父会话的 todo 列表。
- `hasTaskPermission` 控制是否允许子 Agent 递归创建子 Agent，默认禁止（防止无限递归）。
- `task_id` 支持恢复已有子会话，实现任务的连续性。

### 机制 B：Subtask 内联执行

**作用**：主循环直接检测 pending `subtask` part 并实例化 `TaskTool` 执行，无需 LLM 再次生成工具调用。

**关键源码**（`packages/opencode/src/session/prompt.ts:353-527`）：
```typescript
if (task?.type === "subtask") {
  const taskTool = await TaskTool.init()
  const taskModel = task.model ? await Provider.getModel(...) : model
  const assistantMessage = await Session.updateMessage({...})
  let part = await Session.updatePart({...})

  const taskCtx: Tool.Context = {
    agent: task.agent,
    messages: msgs,
    extra: { bypassAgentCheck: true },
    async ask(req) {
      await PermissionNext.ask({
        ...req,
        ruleset: PermissionNext.merge(taskAgent.permission, session.permission ?? []),
      })
    },
  }
  const result = await taskTool.execute(taskArgs, taskCtx)

  if (task.command) {
    // 插入 synthetic user message 兼容 Gemini
    await Session.updateMessage(summaryUserMsg)
    await Session.updatePart({ type: "text", text: "Summarize the task tool output..." })
  }
  continue
}
```

**这段代码为什么值得看**：
- 直接执行避免了额外的 LLM 调用开销和延迟。
- `bypassAgentCheck: true` 因为子任务的意图已经明确（由系统或用户触发）。
- `task.command` 存在时插入 synthetic user message，是为了兼容某些推理模型（如 Gemini）对消息序列的要求。

### 机制 C：子 Agent 定义与权限

**作用**：内置子 Agent（general/explore/compaction）有各自的 prompt 和权限配置。

**关键源码**（`packages/opencode/src/agent/agent.ts:115-156`）：
```typescript
general: {
  name: "general",
  description: "General-purpose agent for researching complex questions...",
  permission: PermissionNext.merge(
    defaults,
    PermissionNext.fromConfig({ todoread: "deny", todowrite: "deny" }),
  ),
  mode: "subagent",
},
explore: {
  name: "explore",
  description: "Exploration agent for investigating large codebases...",
  permission: PermissionNext.merge(
    defaults,
    PermissionNext.fromConfig({ todoread: "deny", todowrite: "deny", edit: { "*": "deny" }, write: { "*": "deny" } }),
  ),
  mode: "subagent",
},
```

**这段代码为什么值得看**：
- `explore` agent 禁用 edit/write，确保只读探索不修改代码。
- `general` agent 保留编辑权限，可以执行多步任务。
- `mode: "subagent"` 标记这些 Agent 只能作为子 Agent 使用，不能作为主 Agent。

### 机制 D：@agent 触发机制

**作用**：用户消息中包含 `@agent` part 时，自动追加提示引导 LLM 调用 `task` 工具。

**关键源码**（`packages/opencode/src/session/prompt.ts:1263-1285`）：
```typescript
// 当用户消息中包含 @agent part 时，自动追加提示
const lastUserMsg = msgs.findLast((m) => m.info.role === "user")
const bypassAgentCheck = lastUserMsg?.parts.some((p) => p.type === "agent") ?? false
```

**这段代码为什么值得看**：
- `@agent` 是用户显式调用子 Agent 的语法糖。
- `bypassAgentCheck` 标记跳过了 task 工具的权限检查，因为用户已明确授权。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 依赖 | 编排循环 | 主循环内联执行 subtask | `prompt.ts:L353-527` |
| 依赖 | 工具系统 | TaskTool 是内置工具之一 | `tool/task.ts` |
| 输出到 | 记忆系统 | 创建 child session | `Session.create({ parentID })` |
| 依赖 | 安全防护 | 子 Agent 权限继承与限制 | `PermissionNext.merge` |
| 依赖 | 上下文管理 | 子 Agent 使用自己的 model/agent | `Agent.get(params.subagent_type)` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **任务可以明确分类**：general/explore/compaction 等子 Agent 有清晰的分工边界。
2. **子任务应该隔离**：child session 避免上下文污染。
3. **用户知道何时调用子 Agent**：`@agent` 语法假设用户了解子 Agent 的存在和用途。

### 6.2 这个设计的代价/风险

1. **子 Agent 创建开销**：每次创建 child session 都有数据库操作和上下文初始化开销。
2. **上下文继承不完整**：child session 只能看到父 session 的 message，但看不到内存状态（如 Instance.state）。
3. **递归风险**：虽然默认禁用子 Agent 的 task 权限，但如果配置不当仍可能无限递归。
4. **结果汇总依赖文本**：子 Agent 的结果通过文本输出返回，结构化信息可能丢失。

### 6.3 如果要重新设计，可能会改变什么

1. **子 Agent 结果结构化**：除了文本输出，还支持返回结构化数据（如文件列表、代码片段）。
2. **子 Agent 并行执行**：当前子任务是串行的，可以考虑并行调度多个子 Agent。
3. **子 Agent 上下文选择性继承**：让子 Agent 可以选择继承父会话的某些状态（如已读取的文件缓存）。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：子 Agent 编排不是"多开几个会话"那么简单，而是一个**任务分解与隔离系统**。OpenCode 的设计表明，生产级 Agent 需要三个能力：(1) 明确的任务分类（不同子 Agent 有不同权限和能力）、(2) 上下文隔离（child session 防止污染）、(3) 权限继承与限制（继承父会话基础权限但限制危险操作）。缺少任何一点，子 Agent 要么无法完成复杂任务，要么会成为安全漏洞。
