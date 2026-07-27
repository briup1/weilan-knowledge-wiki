# 维度01：编排循环（Orchestration Loop）

## 1. 一句话定位

编排循环是 OpenCode Agent 系统的核心调度中枢，它通过 `while(true)` 主循环将单次 LLM 调用无法完成的复杂任务，拆解为多轮“LLM 推理 → 工具执行 → 状态更新 → 再推理”的自治迭代过程，直到任务完成或外部干预终止。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有编排循环，系统将退化为“单轮问答机”，具体故障如下：

- **工具链断裂**：LLM 单次输出若包含工具调用意图，但系统不将其结果回注到对话上下文，后续推理将失去工具执行结果，导致任务半途而废。代码层面，`SessionProcessor.process` 中的 `tool-call` / `tool-result` 事件解析将失去意义，因为不会有下一轮将结果喂给模型。
- **上下文爆炸**：多轮工具调用后，token 消耗会迅速超出模型窗口上限。没有循环中的 `SessionCompaction.isOverflow` 检测与自动触发 compaction，API 将直接抛出上下文溢出错误（`ContextOverflowError`），会话崩溃。
- **子任务无法内联**：`task` 工具（子 Agent 调用）产生的子任务需要被主循环识别、执行、结果回写。没有循环，子任务将永远停留在 `pending` 状态，主 Agent 永远看不到子 Agent 的产出。
- **用户体验劣化**：用户发送一条消息后，若模型需要 5 轮工具调用来完成，没有循环则用户需要手动发送 5 次“继续”，每次还要手动粘贴上一轮结果。

### 2.2 OpenCode 的具体触发条件

编排循环在 `SessionPrompt.loop`（`packages/opencode/src/session/prompt.ts` L275）中启动，其持续运行的核心判断逻辑如下：

```typescript
// packages/opencode/src/session/prompt.ts L319-326
if (
  lastAssistant?.finish &&
  !["tool-calls", "unknown"].includes(lastAssistant.finish) &&
  lastUser.id < lastAssistant.id
) {
  log.info("exiting loop", { sessionID })
  break
}
```

这段代码说明：只有当上一轮 assistant 消息的 `finish` 原因不是 `"tool-calls"` 也不是 `"unknown"`，且 assistant 消息确实是在最后一条用户消息之后生成时，循环才退出。换言之，只要模型还在调用工具（finish 为 tool-calls），或者还没给出最终答案，循环就必须继续。

此外，循环还会因为以下原因提前退出或跳转：
- `abort.aborted` 为 true（用户取消）
- `result === "stop"`（权限拒绝或错误）
- `result === "compact"`（上下文溢出，触发 compaction 后 continue）
- `structuredOutput !== undefined`（结构化输出已捕获）

---

## 3. 核心设计思路

### 3.1 抽象模型

编排循环本质上是一个**带状态检查的事件驱动状态机**，可抽象为以下伪代码：

```
state = IDLE
while state != DONE:
  if abort: break

  # 1. 扫描历史消息，识别待处理任务
  task = detect_pending_subtask_or_compaction(history)

  # 2. 优先处理系统级中断任务
  if task == SUBTASK:
    execute_subtask_inline(task)
    continue
  if task == COMPACTION:
    execute_compaction(task)
    continue

  # 3. 检查上下文是否溢出
  if context_overflow(history):
    create_compaction_task()
    continue

  # 4. 正常推理轮次
  result = process_single_turn(agent, tools, messages)

  # 5. 根据结果决定状态转移
  if result == STOP: state = DONE
  if result == COMPACT: create_compaction_task(); continue
  if model_finished_without_tool_calls: state = DONE
  else: continue  # 还有工具要执行，继续循环
```

### 3.2 关键设计决策

| 决策 | 选了什么 | 放弃了什么 |
|------|---------|-----------|
| **单线程顺序循环 vs 并行多轮** | 选了单线程 `while(true)`，每轮只有一个 LLM stream 在处理 | 放弃了并行发起多个 LLM 调用以加速的潜力，简化了状态一致性管理 |
| **流式事件驱动 vs 批量等待** | 选了基于 AI SDK `fullStream` 的流式事件解析（text-delta / tool-call / reasoning-start 等） | 放弃了等 LLM 返回完整响应后再统一处理的方式，失去了更早的交互反馈延迟，但获得了实时 UI 更新能力 |
| **子任务内联执行 vs 异步队列** | 选了在主循环中同步阻塞执行子任务（`taskTool.execute`），完成后立即 `continue` | 放弃了将子任务放入后台队列、主循环继续处理其他事情的并发模型，换取了更简单的因果顺序和调试体验 |
| **Compaction 作为循环内跳转 vs 外部定时器** | 选在循环内检测溢出并触发 compaction，通过 `continue` 重新进入循环 | 放弃了外部 cron 或定时清理的策略，确保 compaction 总是在最需要的时候发生，且不会打断正在进行的工具链 |

### 3.3 数据流/控制流

```
[User Input]
  |
  v
SessionPrompt.prompt()  --创建 UserMessage-->  DB
  |
  v
SessionPrompt.loop()  [入口: packages/opencode/src/session/prompt.ts L275]
  |
  |--> 扫描历史消息 (L299-316)
  |       |--> 发现 Subtask? --> 内联执行 (L353-526) --> continue
  |       |--> 发现 Compaction? --> SessionCompaction.process (L530-541) --> continue
  |       |--> 上下文溢出? --> SessionCompaction.create (L543-556) --> continue
  |
  |--> 构建 tools (L604-612)
  |--> 构建 system prompt (L653-657)
  |
  v
SessionProcessor.process()  [入口: packages/opencode/src/session/processor.ts L45]
  |
  |--> LLM.stream()  [入口: packages/opencode/src/session/llm.ts L46]
  |       |--> AI SDK streamText()
  |
  |--> for await (value of stream.fullStream)
  |       |--> text-delta --> Session.updatePartDelta()
  |       |--> tool-call --> Session.updatePart() + 执行工具
  |       |--> tool-result --> Session.updatePart()
  |       |--> tool-error --> Session.updatePart() + blocked 标记
  |       |--> finish-step --> 更新 usage + snapshot patch
  |
  |--> 返回 "continue" | "stop" | "compact"
        |
        v
loop() 根据 result 决定 break / continue / compaction
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：主循环调度（while(true) 的调度逻辑）

**这段代码为什么值得看**：它是整个编排循环的"心脏"，展示了循环如何决定是继续、退出、还是处理系统级任务（子任务/compaction）。注意 `tasks.pop()` 的 LIFO 语义，以及 `lastFinished` 检测避免无限循环。

```typescript
// packages/opencode/src/session/prompt.ts L295-326
while (true) {
  SessionStatus.set(sessionID, { type: "busy" })
  log.info("loop", { step, sessionID })
  if (abort.aborted) break
  let msgs = await MessageV2.filterCompacted(MessageV2.stream(sessionID))

  let lastUser: MessageV2.User | undefined
  let lastAssistant: MessageV2.Assistant | undefined
  let lastFinished: MessageV2.Assistant | undefined
  let tasks: (MessageV2.CompactionPart | MessageV2.SubtaskPart)[] = []
  for (let i = msgs.length - 1; i >= 0; i--) {
    const msg = msgs[i]
    if (!lastUser && msg.info.role === "user") lastUser = msg.info as MessageV2.User
    if (!lastAssistant && msg.info.role === "assistant") lastAssistant = msg.info as MessageV2.Assistant
    if (!lastFinished && msg.info.role === "assistant" && msg.info.finish)
      lastFinished = msg.info as MessageV2.Assistant
    if (lastUser && lastFinished) break
    const task = msg.parts.filter((part) => part.type === "compaction" || part.type === "subtask")
    if (task && !lastFinished) {
      tasks.push(...task)
    }
  }

  if (!lastUser) throw new Error("No user message found in stream. This should never happen.")
  if (
    lastAssistant?.finish &&
    !["tool-calls", "unknown"].includes(lastAssistant.finish) &&
    lastUser.id < lastAssistant.id
  ) {
    log.info("exiting loop", { sessionID })
    break
  }
```

### 机制 B：单轮处理器（流式事件解析）

**这段代码为什么值得看**：它展示了 OpenCode 如何处理 AI SDK 的流式事件，将 LLM 的原始流转换为结构化的 Part 更新。特别值得注意的是 `tool-call` 事件中的 "doom loop" 检测（连续 3 次相同工具调用），以及 `tool-error` 中的权限拒绝处理逻辑。

```typescript
// packages/opencode/src/session/processor.ts L111-179
for await (const value of stream.fullStream) {
  input.abort.throwIfAborted()
  switch (value.type) {
    case "tool-call": {
      const match = toolcalls[value.toolCallId]
      if (match) {
        const part = await Session.updatePart({
          ...match,
          tool: value.toolName,
          state: {
            status: "running",
            input: value.input,
            time: { start: Date.now() },
          },
          metadata: value.providerMetadata,
        })
        toolcalls[value.toolCallId] = part as MessageV2.ToolPart

        const parts = await MessageV2.parts(input.assistantMessage.id)
        const lastThree = parts.slice(-DOOM_LOOP_THRESHOLD)
        if (
          lastThree.length === DOOM_LOOP_THRESHOLD &&
          lastThree.every(
            (p) =>
              p.type === "tool" &&
              p.tool === value.toolName &&
              p.state.status !== "pending" &&
              JSON.stringify(p.state.input) === JSON.stringify(value.input),
          )
        ) {
          const agent = await Agent.get(input.assistantMessage.agent)
          await PermissionNext.ask({
            permission: "doom_loop",
            patterns: [value.toolName],
            sessionID: input.assistantMessage.sessionID,
            metadata: { tool: value.toolName, input: value.input },
            always: [value.toolName],
            ruleset: agent.permission,
          })
        }
      }
      break
    }
```

### 机制 C：子任务内联执行

**这段代码为什么值得看**：它展示了 OpenCode 如何将子 Agent 调用（task 工具）内联到主循环中执行，而非异步派发。关键细节包括：创建独立的 assistantMessage 来承载子任务结果、使用 `TaskTool.execute` 同步执行、以及执行后插入 synthetic user message 来避免某些推理模型（如 Gemini）因缺少 user/assistant 交替而报错。

```typescript
// packages/opencode/src/session/prompt.ts L353-400, L444-524
if (task?.type === "subtask") {
  const taskTool = await TaskTool.init()
  const taskModel = task.model ? await Provider.getModel(task.model.providerID, task.model.modelID) : model
  const assistantMessage = (await Session.updateMessage({
    id: Identifier.ascending("message"),
    role: "assistant",
    parentID: lastUser.id,
    sessionID,
    mode: task.agent,
    agent: task.agent,
    // ... 省略其他字段
  })) as MessageV2.Assistant

  const taskCtx: Tool.Context = {
    agent: task.agent,
    messageID: assistantMessage.id,
    sessionID: sessionID,
    abort,
    callID: part.callID,
    extra: { bypassAgentCheck: true },
    messages: msgs,
    // ... ask / metadata callbacks
  }
  const result = await taskTool.execute(taskArgs, taskCtx).catch((error) => {
    executionError = error
    return undefined
  })

  // 为 Gemini 等模型插入 synthetic user message
  if (task.command) {
    const summaryUserMsg: MessageV2.User = {
      id: Identifier.ascending("message"),
      sessionID,
      role: "user",
      time: { created: Date.now() },
      agent: lastUser.agent,
      model: lastUser.model,
    }
    await Session.updateMessage(summaryUserMsg)
    await Session.updatePart({
      id: Identifier.ascending("part"),
      messageID: summaryUserMsg.id,
      sessionID,
      type: "text",
      text: "Summarize the task tool output above and continue with your task.",
      synthetic: true,
    })
  }
  continue
}
```

### 机制 D：Agent 选择与切换

**这段代码为什么值得看**：它展示了 Agent 选择的双重逻辑——默认从 `lastUser.agent` 读取，但允许用户通过 `@agent` 语法显式切换。`bypassAgentCheck` 标志用于处理用户显式指定 Agent 的场景，而 `Agent.get` 提供了基于配置文件的动态 Agent 解析。

```typescript
// packages/opencode/src/session/prompt.ts L559-562, L600-602
const agent = await Agent.get(lastUser.agent)
const maxSteps = agent.steps ?? Infinity
const isLastStep = step >= maxSteps

// Check if user explicitly invoked an agent via @ in this turn
const lastUserMsg = msgs.findLast((m) => m.info.role === "user")
const bypassAgentCheck = lastUserMsg?.parts.some((p) => p.type === "agent") ?? false
```

Agent 配置中心定义了不同 Agent 的权限、模式和能力边界：

```typescript
// packages/opencode/src/agent/agent.ts L76-92
const result: Record<string, Info> = {
  build: {
    name: "build",
    description: "The default agent. Executes tools based on configured permissions.",
    options: {},
    permission: PermissionNext.merge(
      defaults,
      PermissionNext.fromConfig({
        question: "allow",
        plan_enter: "allow",
      }),
      user,
    ),
    mode: "primary",
    native: true,
  },
  // ... explore, plan, general 等
}
```

---

## 5. 与其他维度的交互

| 交互维度 | 交互方式 | 代码位置 |
|---------|---------|---------|
| **工具系统** | `resolveTools()` 将 `ToolRegistry` + `MCP` 工具合并，并根据 Agent 权限过滤禁用工具 | `prompt.ts L737-925` |
| **记忆系统** | `MessageV2.filterCompacted()` 过滤已压缩消息，`SessionCompaction.isOverflow()` 检测上下文溢出 | `prompt.ts L299, L543-556` |
| **错误处理** | `SessionProcessor` 内捕获异常，区分 `ContextOverflowError`（触发 compaction）、可重试错误（指数退避）、致命错误（停止循环） | `processor.ts L353-386` |
| **验证循环** | `DOOM_LOOP_THRESHOLD` 检测连续相同工具调用，通过 `PermissionNext.ask` 弹窗确认 | `processor.ts L20, L151-176` |
| **子 Agent 编排** | `task` 工具通过 `TaskTool.execute` 内联执行子 Agent，子 Agent 拥有独立的权限规则集（`PermissionNext.merge(taskAgent.permission, session.permission)`） | `prompt.ts L353-526` |
| **快照系统** | `start-step` / `finish-step` 事件触发 `Snapshot.track()` 和 `Snapshot.patch()`，记录文件变更 | `processor.ts L233-276` |
| **插件系统** | `Plugin.trigger` 在工具执行前后、消息转换、系统提示构建等多个钩子点介入 | 多处调用 |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **LLM 是可靠的调度器**：系统假设模型能够根据工具返回结果自主决定下一步行动，因此不需要硬编码的工作流图。这体现在循环对 `finish` 原因的无条件信任——只要模型说 `"tool-calls"`，循环就继续。

2. **单会话单线程足够**：`state()` 使用 sessionID 级别的 AbortController，没有考虑同一 session 的并发请求。这假设用户不会在同一 session 中同时发起多个独立任务。

3. **工具执行是幂等或至少可重试的**：`SessionRetry` 对 API 错误进行指数退避重试，但没有对工具副作用进行回滚（除了 `Snapshot` 记录文件变更）。

4. **上下文压缩比长上下文更经济**：`SessionCompaction` 在溢出时触发，假设压缩历史消息的成本低于直接切换到更大窗口模型的成本。

### 6.2 这个设计的代价/风险

- **单线程阻塞**：子任务内联执行时，整个 session 被阻塞。如果子 Agent 需要执行大量文件搜索，主 session 的 UI 将完全无响应。
- **无限循环风险**：虽然 `DOOM_LOOP_THRESHOLD` 提供了保护，但模型仍可能以微小差异的工具输入陷入更长的循环（如反复读取相似文件）。
- **状态机隐式化**：循环逻辑散落在 `if/continue/break` 中，而非显式状态机。新增一种"系统级任务类型"需要修改 `loop()` 的核心逻辑，容易引入 bug。
- **Agent 切换的边界模糊**：`bypassAgentCheck` 标志的存在说明 Agent 切换逻辑是事后补丁式的，用户通过 `@agent` 切换后，后续轮次可能仍沿用旧 Agent 的上下文和工具集。

### 6.3 如果要重新设计，可能会改变什么

1. **显式状态机**：将 `IDLE / SUBTASK / COMPACTION / INFERENCE / ERROR` 等状态显式化，用状态转移表替代嵌套的 `if/continue`，提高可测试性。

2. **子任务异步化**：将子 Agent 调用放入独立的工作线程或微任务队列，主循环通过事件监听而非 `await` 等待结果，避免阻塞主 session。

3. **工具调用意图缓存**：在 `DOOM_LOOP_THRESHOLD` 基础上，增加语义相似度检测（而非简单的 `JSON.stringify` 比较），捕获"读取 A 文件后读取 B 文件再读取 A 文件"这类更隐蔽的循环。

4. **Agent 上下文隔离**：为每个 Agent 维护独立的 message buffer，切换 Agent 时做显式的上下文交接，而非简单地复用同一个 `msgs` 数组。

### 6.4 对我自己设计 Agent 系统的启示

1. **循环退出条件要尽早明确**：OpenCode 在循环顶部就检查 `lastAssistant.finish`，这比在底部检查更清晰。设计时应将"什么算完成"作为第一优先级定义。

2. **流式事件解析是必备能力**：不要等 LLM 返回完整响应再处理。`SessionProcessor` 的 `switch(value.type)` 模式展示了如何将 AI SDK 的抽象流映射到业务状态更新。

3. **系统级任务要插队**：`subtask` 和 `compaction` 在普通推理之前被处理，这种"高优先级任务插队"模式值得借鉴。任何 Agent 系统都需要一种机制让系统自身的需求（压缩、子任务、安全拦截）优先于模型推理。

4. **权限是循环的一部分，不是工具的一部分**：OpenCode 将 `PermissionNext.ask` 嵌入到循环和工具执行上下文中，而非在工具注册时静态决定。这使得权限决策可以基于运行时状态（如 doom loop 检测）。

5. **Synthetic message 是兼容层而非 hack**：为 Gemini 插入 synthetic user message 的做法看似 hack，实则是对 LLM API 约束的正式兼容层。设计 Agent 系统时，应为不同模型的对话格式要求预留适配空间。
