# 维度：记忆系统 (Memory System)

## 1. 一句话定位

记忆系统是 OpenCode 的"时间机器"，通过 SQLite 三层存储持久化会话历史，并借助 Prune、Compaction、Overflow 三级压缩策略，在 LLM 上下文窗口的硬约束下最大化保留有用信息。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **会话丢失**：如果关闭终端后没有持久化，用户之前的对话、文件修改记录、工具执行结果全部消失。代码中 `SessionTable`、`MessageTable`、`PartTable` 的级联存储确保即使进程崩溃，数据也能从 SQLite 恢复。
- **上下文溢出硬失败**：当消息历史超过模型上下文窗口时，`LLM.stream` 会抛出 `ContextOverflowError`。如果没有 compaction 机制，这个错误会直接终止循环（`processor.ts:L359`），用户被迫重新开始。
- **历史消息无限膨胀**：工具结果（如 `cat` 大文件、`grep` 全仓库）可能产生巨量输出，如果不做 prune，每轮循环都会将这些冗余数据送入 LLM，既浪费 token 又降低响应质量。
- **消息顺序混乱**：多轮对话中 user/assistant/tool 的交错关系如果没有严格的 Schema 约束，LLM 可能收到格式错误的消息序列（如 tool-call 没有对应的 tool-result）。

### 2.2 OpenCode 的具体触发条件

记忆系统相关的触发条件分布在多个文件中：

- **会话创建**：`Session.create` 在数据库中插入 `SessionTable` 记录（`session/index.ts`）
- **消息加载**：每次 loop 开始时 `MessageV2.filterCompacted(MessageV2.stream(sessionID))`（`prompt.ts:L299`）
- **上下文溢出检测**：`SessionCompaction.isOverflow` 在 token 数超过 `usable` 阈值时返回 true（`compaction.ts:L32-48`）
- **Prune 触发**：`SessionCompaction.prune` 在 loop 结束后调用（`prompt.ts:L717`）
- **Compaction 创建**：检测到 overflow 或用户手动触发时，`SessionCompaction.create` 插入 `compaction` part（`compaction.ts:L296-327`）

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────────────────────────────────────────────────┐
│                    三级存储模型                               │
│  SessionTable (1) ──► MessageTable (N) ──► PartTable (N)   │
│       │                    │                    │            │
│       ▼                    ▼                    ▼            │
│  会话元数据            消息元数据             消息内容片段      │
│  (id, title,          (id, role,             (text, tool,    │
│   project_id,          parent_id,             reasoning,      │
│   permission)          data)                  compaction...)   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    三级压缩策略                               │
│                                                              │
│  Level 1: Prune     ──► 丢弃老旧 tool 输出（标记 compacted） │
│  Level 2: Compaction ──► 用 compaction agent 生成结构化摘要  │
│  Level 3: Overflow   ──► 剥离媒体附件，保留文本              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **存储引擎** | SQLite + Drizzle ORM | 纯内存、JSON 文件、PostgreSQL | SQLite 零配置、单文件、支持 SQL 查询；Drizzle 提供类型安全。`session.sql.ts` 中 `onDelete: "cascade"` 保证数据一致性 |
| **三层表结构** | Session → Message → Part 级联 | 扁平化存储（一个表存所有） | 分离关注点：Session 存元数据、Message 存角色关系、Part 存内容。`PartTable` 冗余 `session_id` 避免 JOIN |
| **压缩策略分级** | Prune → Compaction → Overflow 三级 | 直接截断旧消息 | `compaction.ts:L173-199` 的 prompt 要求保留 Goal/Instructions/Discoveries/Accomplished/Relevant files，简单截断会丢失文件关系 |
| **Compaction Agent** | 用专门的 agent 生成结构化摘要 | 直接截断或固定模板摘要 | 代码中 compaction 使用 `compaction` agent（`compaction.ts:L131`），其 prompt 明确要求五部分信息，比模板更灵活 |

### 3.3 数据流/控制流

```
用户发送消息
    │
    v
[Session.updateMessage] ──► 写入 MessageTable
[Session.updatePart]    ──► 写入 PartTable
    │
    v
[MessageV2.stream]      ──► 分页查询 MessageTable + PartTable
    │
    v
[MessageV2.filterCompacted] ──► 过滤已压缩消息，只保留未压缩部分
    │
    v
[MessageV2.toModelMessages] ──► 转换为 AI SDK ModelMessage 格式
    │                          （处理 media 注入、provider 差异）
    v
[LLM.stream]            ──► 发送给模型
    │
    v
模型响应 + 工具结果
    │
    v
[Session.updatePart]    ──► 更新 tool part 状态 (running → completed/error)
    │
    v
[SessionCompaction.isOverflow]?
    ├──► true ──► [SessionCompaction.create] ──► 插入 compaction part
    │                    │
    │                    v
    │             [SessionCompaction.process] ──► compaction agent 生成摘要
    │                    │
    │                    v
    │             [MessageV2.filterCompacted] ──► 下次 loop 只读到摘要
    │
    └──► false ──► 继续正常循环

Loop 结束
    │
    v
[SessionCompaction.prune] ──► 逆向扫描，标记老旧 tool 输出为 compacted
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：三层存储模型（SessionTable/MessageTable/PartTable）

**作用**：将会话数据分离为三个层级，支持级联删除和独立查询。

**设计意图**：
- SessionTable 存储会话级元数据（标题、权限、摘要统计），独立查询时不需加载所有消息。
- MessageTable 存储消息级元数据（角色、父子关系），支持按 session 分页加载。
- PartTable 存储消息内容片段（文本、工具调用、文件附件等），支持按 message 批量加载。

**关键源码**（`packages/opencode/src/session/session.sql.ts:11-67`）：
```typescript
export const SessionTable = sqliteTable("session", {
  id: text().primaryKey(),
  project_id: text().notNull().references(() => ProjectTable.id, { onDelete: "cascade" }),
  // ... title, version, permission, timestamps
})

export const MessageTable = sqliteTable("message", {
  id: text().primaryKey(),
  session_id: text().notNull().references(() => SessionTable.id, { onDelete: "cascade" }),
  data: text({ mode: "json" }).notNull().$type<InfoData>(),
})

export const PartTable = sqliteTable("part", {
  id: text().primaryKey(),
  message_id: text().notNull().references(() => MessageTable.id, { onDelete: "cascade" }),
  session_id: text().notNull(),  // 冗余存储，避免 JOIN
  data: text({ mode: "json" }).notNull().$type<PartData>(),
})
```

**这段代码为什么值得看**：
- `onDelete: "cascade"` 确保删除 Session 时自动清理关联的 Message 和 Part。
- `PartTable` 冗余 `session_id`（而非仅通过 `message_id` 外键关联），使得按 session 查询 part 时不需要 JOIN MessageTable。
- 所有复杂类型（`InfoData`, `PartData`, `PermissionNext.Ruleset`）都通过 `$type<>` 标注，Drizzle 负责 JSON 序列化/反序列化。

### 机制 B：消息流式加载与过滤（stream + filterCompacted）

**作用**：按时间倒序分页加载消息，并在加载过程中过滤掉已被压缩的消息。

**设计意图**：
- 倒序加载（`orderBy(desc(MessageTable.time_created))`）使得最新的消息先被处理，符合对话的自然阅读顺序。
- `filterCompacted` 在流式加载中实时判断终止条件，避免加载不必要的旧消息。

**关键源码**（`packages/opencode/src/session/message-v2.ts:731-782, 809-825`）：
```typescript
export const stream = fn(Identifier.schema("session"), async function* (sessionID) {
  const size = 50
  let offset = 0
  while (true) {
    const rows = Database.use((db) =>
      db.select().from(MessageTable)
        .where(eq(MessageTable.session_id, sessionID))
        .orderBy(desc(MessageTable.time_created))
        .limit(size).offset(offset).all()
    )
    if (rows.length === 0) break
    // ... 加载 parts
    for (const row of rows) {
      yield { info, parts: partsByMessage.get(row.id) ?? [] }
    }
    offset += rows.length
  }
})

export async function filterCompacted(stream: AsyncIterable<MessageV2.WithParts>) {
  const result = [] as MessageV2.WithParts[]
  const completed = new Set<string>()
  for await (const msg of stream) {
    result.push(msg)
    if (msg.info.role === "user" && completed.has(msg.info.id) &&
        msg.parts.some((p) => p.type === "compaction"))
      break
    if (msg.info.role === "assistant" && msg.info.summary && msg.info.finish && !msg.info.error)
      completed.add(msg.info.parentID)
  }
  result.reverse()
  return result
}
```

**这段代码为什么值得看**：
- `stream` 使用分页（`size = 50`）避免一次性加载大量消息，适合长会话场景。
- `filterCompacted` 的核心逻辑：当遇到一个 user 消息，其 parent assistant 已被标记为 `summary`（即被压缩过），且该 user 消息包含 `compaction` part 时，停止加载。这意味着 compaction 后的旧消息被完全跳过。
- `result.reverse()` 将倒序加载的结果恢复为正序，因为 loop 需要按时间正序处理消息。

### 机制 C：上下文压缩（SessionCompaction）

**作用**：当上下文 token 数超过阈值时，用专门的 compaction agent 生成结构化摘要，替换旧消息。

**设计意图**：
- 不是简单截断，而是生成保留关键信息（目标、指令、发现、已完成工作、相关文件）的摘要。
- 使用 agent 做 compaction 可以复用现有的 tool 调用能力，让 compaction 过程本身也能读取文件。

**关键源码**（`packages/opencode/src/session/compaction.ts:32-48, 101-199`）：
```typescript
export async function isOverflow(input: { tokens: MessageV2.Assistant["tokens"]; model: Provider.Model }) {
  const config = await Config.get()
  if (config.compaction?.auto === false) return false
  const context = input.model.limit.context
  if (context === 0) return false
  const count = input.tokens.total || input.tokens.input + input.tokens.output + 
                input.tokens.cache.read + input.tokens.cache.write
  const reserved = config.compaction?.reserved ?? Math.min(COMPACTION_BUFFER, ProviderTransform.maxOutputTokens(input.model))
  const usable = input.model.limit.input
    ? input.model.limit.input - reserved
    : context - ProviderTransform.maxOutputTokens(input.model)
  return count >= usable
}

// Compaction Agent 的 Prompt（L173-199）
const defaultPrompt = `Provide a detailed prompt for continuing our conversation above.
Focus on information that would be helpful for continuing the conversation...

When constructing the summary, try to stick to this template:
---
## Goal
[What goal(s) is the user trying to accomplish?]
## Instructions
- [What important instructions did the user give you...]
## Discoveries
[What notable things were learned...]
## Accomplished
[What work has been completed...]
## Relevant files / directories
[Construct a structured list of relevant files...]
---`
```

**这段代码为什么值得看**：
- `isOverflow` 的阈值计算考虑了 `reserved` 缓冲区和 `maxOutputTokens`，确保为模型输出预留空间。
- `config.compaction?.auto === false` 允许用户禁用自动压缩。
- Compaction agent 的 prompt 明确要求五部分结构化信息，比简单摘要更有用：后续 agent 可以从"Goal"知道用户意图，从"Relevant files"知道文件关系。

### 机制 D：Prune 策略

**作用**：逆向扫描消息历史，将超过 40k tokens 的旧工具输出标记为 `compacted`，在不生成摘要的情况下直接丢弃冗余输出。

**设计意图**：
- Prune 比 Compaction 更轻量，不需要调用 LLM。
- 只针对工具输出（`part.type === "tool"`），不影响用户消息和 assistant 的文本回复。
- 保护 `skill` 工具的输出（`PRUNE_PROTECTED_TOOLS`），因为 skill 结果通常包含重要上下文。

**关键源码**（`packages/opencode/src/session/compaction.ts:50-99`）：
```typescript
export const PRUNE_MINIMUM = 20_000
export const PRUNE_PROTECT = 40_000
const PRUNE_PROTECTED_TOOLS = ["skill"]

export async function prune(input: { sessionID: string }) {
  const msgs = await Session.messages({ sessionID: input.sessionID })
  let total = 0, pruned = 0
  const toPrune = []
  let turns = 0

  loop: for (let msgIndex = msgs.length - 1; msgIndex >= 0; msgIndex--) {
    const msg = msgs[msgIndex]
    if (msg.info.role === "user") turns++
    if (turns < 2) continue  // 保留最近两轮
    if (msg.info.role === "assistant" && msg.info.summary) break loop  // 遇到摘要停止
    for (let partIndex = msg.parts.length - 1; partIndex >= 0; partIndex--) {
      const part = msg.parts[partIndex]
      if (part.type === "tool" && part.state.status === "completed" &&
          !PRUNE_PROTECTED_TOOLS.includes(part.tool) && !part.state.time.compacted) {
        const estimate = Token.estimate(part.state.output)
        total += estimate
        if (total > PRUNE_PROTECT) {
          pruned += estimate
          toPrune.push(part)
        }
      }
    }
  }
  if (pruned > PRUNE_MINIMUM) {
    for (const part of toPrune) {
      part.state.time.compacted = Date.now()
      await Session.updatePart(part)
    }
  }
}
```

**这段代码为什么值得看**：
- `turns < 2` 保留最近两轮对话，避免 prune 影响当前进行中的任务。
- `msg.info.summary` 检查确保不会越过已压缩的摘要继续 prune。
- 标记方式为设置 `part.state.time.compacted = Date.now()`，而非删除记录，保留了审计能力。

### 机制 E：消息转换（toModelMessages）

**作用**：将内部 Part 格式转换为 AI SDK 兼容的 `ModelMessage` 格式，处理不同 provider 的媒体支持差异。

**设计意图**：
- 不同 provider 对 tool result 中的媒体支持不同（OpenAI 只支持字符串，Anthropic 支持 content 数组），需要适配层。
- 将内部 `file` part 转换为 AI SDK 的 `file` 或 `media` part。

**关键源码**（`packages/opencode/src/session/message-v2.ts:496-555`）：
```typescript
export function toModelMessages(input: WithParts[], model: Provider.Model, options?: { stripMedia?: boolean }) {
  const supportsMediaInToolResults = (() => {
    if (model.api.npm === "@ai-sdk/anthropic") return true
    if (model.api.npm === "@ai-sdk/openai") return true
    // ... 更多 provider 判断
  })()

  const toModelOutput = (output: unknown) => {
    if (typeof output === "string") return { type: "text", value: output }
    if (typeof output === "object") {
      const attachments = (outputObject.attachments ?? []).filter(...)
      return {
        type: "content",
        value: [
          { type: "text", text: outputObject.text },
          ...attachments.map((a) => ({ type: "media", mediaType: a.mime, data: ... })),
        ],
      }
    }
  }
  // ... 遍历消息和 part 进行转换
}
```

**这段代码为什么值得看**：
- `supportsMediaInToolResults` 按 provider 硬编码判断，这是一个"知识驱动的适配层"——作者必须了解每个 provider 的能力差异。
- `stripMedia` 选项在 compaction 时使用，剥离媒体附件以减少 token 消耗。

---

## 5. 与其他维度的交互

```
[记忆系统] <--(读取历史消息)-- [编排循环]
[记忆系统] --(写入消息/Part)--> [持久化存储]
[记忆系统] <--(触发压缩)-- [错误处理] (ContextOverflowError)
[记忆系统] --(转换格式)--> [上下文管理]
[记忆系统] <--(加载指令文件)-- [Prompt构建]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 输出到 | 编排循环 | 提供过滤后的历史消息 | `MessageV2.filterCompacted(MessageV2.stream(sessionID))` |
| 依赖 | 错误处理 | ContextOverflowError 触发 compaction | `processor.ts:L359`, `compaction.ts:L32-48` |
| 依赖 | 工具系统 | 工具结果作为 Part 存储 | `Session.updatePart` in `processor.ts` |
| 输出到 | 上下文管理 | toModelMessages 转换后供 LLM 使用 | `message-v2.ts:L496-729` |
| 依赖 | 状态管理 | Session.Info Schema 定义完整会话状态 | `session/index.ts:L119-161` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **Compaction 生成的摘要质量足够高**：作者假设 compaction agent 生成的五部分摘要能让后续 agent 继续工作，不需要保留原始消息。
2. **SQLite 足够应对单机场景**：没有引入 PostgreSQL 等外部数据库，假设 OpenCode 主要运行在单机/本地场景。
3. **Tool 输出是主要的 token 消耗来源**：prune 只针对 tool part，不针对 text part，假设用户消息和 assistant 回复相对较短。
4. **最近两轮对话不可压缩**：`turns < 2` 的硬编码假设最近两轮包含当前任务的上下文，不能被 prune。

### 6.2 这个设计的代价/风险

1. **Compaction 是"有损压缩"**：摘要可能丢失细节。代码中没有机制让用户审查或回滚 compaction。
2. **SQLite 的并发限制**：SQLite 的写锁在多个进程同时写入时可能成为瓶颈。虽然 OpenCode 主要是单进程，但未来的 client/server 分离可能需要迁移。
3. **Prune 的阈值是固定的**：`PRUNE_MINIMUM = 20_000` 和 `PRUNE_PROTECT = 40_000` 是硬编码的，没有根据模型上下文窗口动态调整。
4. **toModelMessages 的 provider 判断是硬编码的**：新增 provider 时需要修改 `message-v2.ts`，而不是配置化的。

### 6.3 如果要重新设计，可能会改变什么

1. **Compaction 的可审查性**：在 compaction 前让用户确认，或提供"查看原始消息"的功能。
2. **Prune 阈值动态化**：根据模型上下文窗口大小和用户配置动态计算 prune 阈值。
3. **Provider 适配配置化**：将 `supportsMediaInToolResults` 等判断移到 provider 配置中，而非硬编码在消息转换逻辑中。
4. **引入增量 compaction**：当前 compaction 处理全部历史消息，可以考虑只压缩超过阈值的部分。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：记忆系统不是"存储历史消息"那么简单，而是一个**在有限上下文窗口约束下的信息生命周期管理系统**。OpenCode 的三级压缩策略（Prune/Compaction/Overflow）分别对应了"快速丢弃冗余"、"智能保留关键信息"、"应急降级"三种场景，这种分层设计比单一的"截断"策略更优雅。在设计自己的 Agent 系统时，应该尽早考虑上下文管理策略，因为 LLM 的上下文窗口是有限的硬约束，且工具输出往往包含大量冗余信息。
