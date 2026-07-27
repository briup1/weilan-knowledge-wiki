# 维度名：状态管理

## 1. 一句话定位

状态管理负责在 nanobot 单进程、单线程（asyncio）的运行时中，维护会话生命周期、内存缓存与磁盘持久化的一致性，并通过全局锁与后台任务调度保证并发安全与响应性。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **没有 Session 与 SessionManager**：每次消息处理都会丢失历史上下文。`AgentLoop._process_message()` 在 L388 通过 `self.sessions.get_or_create(key)` 获取会话，若此处返回空列表，则 `build_messages()` 的 `history` 参数为空，LLM 将完全遗忘用户之前的指令与工具结果。
- **没有内存缓存**：同一会话的连续消息（如工具调用链中的多轮迭代）会反复触发磁盘 I/O。`SessionManager.save()` 在每次 `_process_message()` 结束时被调用（L445），若缺少 `_cache`，高频写入将拖慢整个 ReAct 循环。
- **没有全局锁 `_processing_lock`**：当用户快速发送多条消息或渠道并发推送时，`AgentLoop._dispatch()` 中的 `asyncio.create_task()` 会生成多个并行的 `_process_message()` 协程。若它们同时读写同一 `Session` 对象的 `messages` 列表并调用 `save()`，将导致 JSONL 文件内容交错损坏，或 `last_consolidated` 索引漂移。
- **没有 `last_consolidated` 索引**：记忆固化（consolidation）后，`Session.messages` 仍保留原始消息，但 `get_history()` 需要知道从哪里开始返回。若该索引丢失或外置，则 `get_history()` 与 `MemoryConsolidator.pick_consolidation_boundary()` 的边界计算将失去同步，导致重复固化或遗漏消息。

### 2.2 nanobot 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 收到新消息时获取/创建会话 | `nanobot/agent/loop.py:L388` | `session = self.sessions.get_or_create(key)` |
| 每轮处理结束时持久化 | `nanobot/agent/loop.py:L445` | `self.sessions.save(session)` |
| 消息派发时获取全局锁 | `nanobot/agent/loop.py:L313` | `async with self._processing_lock:` |
| Token 超限时触发固化 | `nanobot/agent/memory.py:L302-L357` | `maybe_consolidate_by_tokens()` 更新 `last_consolidated` 后调用 `save()` |
| `/new` 命令清空会话 | `nanobot/agent/loop.py:L392-L396` | `session.clear()` 重置 `last_consolidated = 0` |

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────┐     get_or_create()      ┌─────────────────┐
│   MessageBus    │ ───────────────────────> │  SessionManager │
│  (inbound msg)  │                          │   (_cache)      │
└─────────────────┘                          └────────┬────────┘
                                                      │
                              ┌───────────────────────┼───────────────────────┐
                              │ cache hit             │ cache miss            │
                              ▼                       ▼                       ▼
                        ┌──────────┐            ┌──────────┐           ┌──────────┐
                        │ 返回内存  │            │ _load()  │           │ 新建空   │
                        │ Session  │            │ JSONL    │           │ Session  │
                        └──────────┘            └──────────┘           └──────────┘
                                                       │
                                                       ▼
                                                ┌──────────────┐
                                                │ 磁盘 JSONL   │
                                                │ (metadata +  │
                                                │  messages)   │
                                                └──────────────┘
```

控制流：

1. **读路径**：`get_or_create(key)` 先查 `_cache`，未命中则 `_load()` 从 JSONL 反序列化，再放入缓存。
2. **写路径**：`_save_turn()` 追加消息到 `session.messages` → `save()` 全量覆写 JSONL → 更新 `_cache`。
3. **锁路径**：`_dispatch()` 持有全局 `_processing_lock`，确保同一时刻只有一个消息在处理（但子任务和后台任务可并发）。
4. **后台路径**：`_schedule_background()` 将记忆固化等耗时操作移出主响应路径，避免阻塞用户回复。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 持久化格式 | **JSONL**（每会话一个文件，首行为 metadata，后续为消息行） | SQLite / 纯内存 / 单文件 JSON | `manager.py:L163-178` 直接用 `json.dumps` 逐行写入，无需 schema 迁移；`list_sessions()` 只需读首行即可获取元数据，避免加载全部消息；纯内存方案在进程重启后会丢失所有上下文 |
| 缓存策略 | **进程内 dict 缓存（`_cache`）**，无过期、无大小限制 | LRU / TTL / 外部缓存（Redis） | `manager.py:L96-114` 的 `get_or_create()` 直接返回 `_cache[key]`，代码极简；nanobot 是单用户个人助手，会话数量有限，内存压力可控 |
| 并发控制 | **全局单锁 `_processing_lock`** | 每会话一把锁 / 无锁并发 | `loop.py:L311-331` 的 `_dispatch()` 用全局锁包裹整个处理流程；放弃每会话锁是因为：① 子 Agent 可能跨会话操作（如 `spawn` 工具），② 记忆固化需要全局 Token 估算，③ 单用户场景下全局锁足够且更简单 |
| 固化索引位置 | **`last_consolidated` 放在 `Session` 内部** | 外部索引表 / 不记录索引 | `manager.py:L33` 将 `last_consolidated` 作为 dataclass 字段；`get_history()` 直接切片 `self.messages[self.last_consolidated:]`；若外置，则 `Session` 与索引的同步将成为新的一致性难题 |

### 3.3 数据流/控制流

```
InboundMessage (Bus)
    │
    ▼
AgentLoop.run() ──asyncio.create_task──> _dispatch(msg)
    │                                          │
    │                                          ▼
    │                              async with _processing_lock
    │                                          │
    │                                          ▼
    │                              _process_message(msg)
    │                                          │
    │                    ┌─────────────────────┼─────────────────────┐
    │                    │                     │                     │
    │                    ▼                     ▼                     ▼
    │         sessions.get_or_create()  memory.maybe_consolidate()  tools.execute()
    │                    │                     │                     │
    │                    ▼                     ▼                     ▼
    │         Session (内存 + _cache)    last_consolidated 更新    tool results
    │                    │                     │                     │
    │                    └─────────────────────┼─────────────────────┘
    │                                          │
    │                              _save_turn(session, messages)
    │                                          │
    │                              sessions.save(session) ──> JSONL 覆写
    │                                          │
    │                              _schedule_background(consolidate)
    │                                          │
    │                                          ▼
    │                              OutboundMessage (Bus)
    │
    ▼
Background tasks drained in close_mcp() / graceful shutdown
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：Session 数据结构 —— 为什么 `last_consolidated` 必须是内部字段

**作用**：标记已固化到 `MEMORY.md/HISTORY.md` 的消息数量，使 `get_history()` 能精确返回未固化消息，避免重复提交已归档内容给 LLM。

**设计意图**：将索引与消息列表绑定在同一对象内，消除“索引-数据”分离带来的同步风险。`Session.clear()` 在重置消息列表时同步重置索引（`L68-69`），保证二者始终一致。

**关键源码**（`nanobot/session/manager.py:16-70`）：
```python
@dataclass
class Session:
    key: str  # channel:chat_id
    messages: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    last_consolidated: int = 0  # Number of messages already consolidated to files

    def get_history(self, max_messages: int = 500) -> list[dict[str, Any]]:
        """Return unconsolidated messages for LLM input, aligned to a user turn."""
        unconsolidated = self.messages[self.last_consolidated:]   # ① 从索引处切片
        sliced = unconsolidated[-max_messages:]

        # Drop leading non-user messages to avoid orphaned tool_result blocks
        for i, m in enumerate(sliced):
            if m.get("role") == "user":
                sliced = sliced[i:]
                break
        # ... 构建输出

    def clear(self) -> None:
        """Clear all messages and reset session to initial state."""
        self.messages = []
        self.last_consolidated = 0          # ② 清空时索引同步归零
        self.updated_at = datetime.now()
```

> 若 `last_consolidated` 外置（如在 `SessionManager` 中维护一个 `dict[str, int]`），则 `clear()` 需要跨对象更新两处状态，任何遗漏都会导致 `get_history()` 返回越界切片或空历史。

---

### 机制 B：JSONL 持久化 —— 为什么不用 SQLite

**作用**：将会话状态以人类可读、逐行追加友好的格式持久化到磁盘，支持进程重启后的完整恢复。

**设计意图**：nanobot 的“小而美”哲学在存储层体现为——用文件系统原语替代数据库依赖，消除 schema 迁移、连接池、SQL 注入等复杂度。JSONL 的“每行独立 JSON”特性使得：① 损坏只影响单行，② `list_sessions()` 只需读首行元数据，③ 用户可直接用 `cat`/`grep` 查看会话历史。

**关键源码**（`nanobot/session/manager.py:163-180`）：
```python
def save(self, session: Session) -> None:
    """Save a session to disk."""
    path = self._get_session_path(session.key)

    with open(path, "w", encoding="utf-8") as f:
        metadata_line = {
            "_type": "metadata",
            "key": session.key,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "metadata": session.metadata,
            "last_consolidated": session.last_consolidated   # ① 索引随元数据持久化
        }
        f.write(json.dumps(metadata_line, ensure_ascii=False) + "\n")
        for msg in session.messages:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")   # ② 每消息一行，顺序即语义

    self._cache[session.key] = session   # ③ 写盘后更新缓存，保证缓存-磁盘一致
```

> 注意 `save()` 是全量覆写（`"w"` 模式），而非追加。这是因为 `_save_turn()` 可能在消息中插入截断后的 tool result（`loop.py:L466-467`），追加模式无法处理修改已有消息的场景。

---

### 机制 C：全局锁 `_processing_lock` —— 为什么不是每会话锁

**作用**：保证 `_dispatch()` 内整个消息处理流程的原子性，防止并发修改同一 `Session` 状态或交错写入 JSONL。

**设计意图**：在单用户、单进程、单事件循环的假设下，全局锁是最简单的正确方案。每会话锁虽然粒度更细，但会引入：① 子 Agent 跨会话通信的锁顺序死锁风险，② 记忆固化时全局 Token 估算的竞态条件，③ 代码复杂度上升而收益有限（个人助手极少真正并发）。

**关键源码**（`nanobot/agent/loop.py:97-104, 311-331`）：
```python
# 初始化：一把锁，所有会话共享
self._active_tasks: dict[str, list[asyncio.Task]] = {}  # session_key -> tasks
self._background_tasks: list[asyncio.Task] = []
self._processing_lock = asyncio.Lock()                  # ① 全局唯一锁

async def _dispatch(self, msg: InboundMessage) -> None:
    """Process a message under the global lock."""
    async with self._processing_lock:                     # ② 任何消息处理前必须先获取
        try:
            response = await self._process_message(msg)
            if response is not None:
                await self.bus.publish_outbound(response)
            elif msg.channel == "cli":
                await self.bus.publish_outbound(OutboundMessage(
                    channel=msg.channel, chat_id=msg.chat_id,
                    content="", metadata=msg.metadata or {},
                ))
        except asyncio.CancelledError:
            logger.info("Task cancelled for session {}", msg.session_key)
            raise
        except Exception:
            logger.exception("Error processing message for session {}", msg.session_key)
            await self.bus.publish_outbound(OutboundMessage(
                channel=msg.channel, chat_id=msg.chat_id,
                content="Sorry, I encountered an error.",
            ))
```

> 全局锁的代价是消息串行处理，但 `_process_message()` 内部会创建子任务（如工具调用的 `asyncio.create_task` 在 `SubagentManager` 中），这些子任务不受 `_processing_lock` 约束，因此子 Agent 仍可并发执行。锁保护的是“会话状态的读写”而非“所有异步操作”。

---

### 机制 D：后台任务调度 —— 为什么固化要移出主路径

**作用**：将耗时的记忆固化（LLM 调用 + 磁盘写入）从用户响应路径中剥离，保证 `/new` 等命令的即时反馈。

**设计意图**：`maybe_consolidate_by_tokens()` 涉及完整的 LLM 调用链（`provider.chat_with_retry`），若阻塞在 `_process_message()` 内，用户会感知到明显的回复延迟。`_schedule_background()` 利用 asyncio 的并发能力，在事件循环空闲时执行，同时通过 `_background_tasks` 列表保证优雅关闭时的任务排空。

**关键源码**（`nanobot/agent/loop.py:345-349, 379-380, 446`）：
```python
def _schedule_background(self, coro) -> None:
    """Schedule a coroutine as a tracked background task (drained on shutdown)."""
    task = asyncio.create_task(coro)
    self._background_tasks.append(task)
    task.add_done_callback(self._background_tasks.remove)   # ① 自动清理已完成任务

# 在 _process_message 中，主响应发出后才调度后台固化
self._save_turn(session, all_msgs, 1 + len(history))
self.sessions.save(session)
self._schedule_background(self.memory_consolidator.maybe_consolidate_by_tokens(session))  # ② 非阻塞
```

> 对比 `/new` 命令的处理（`L392-400`）：`session.clear()` 和 `save()` 是同步执行的，确保用户立即看到“New session started.”；而旧消息的 `archive_messages()` 则通过 `_schedule_background` 延后执行。

---

## 5. 与其他维度的交互

```
[状态管理] --(输出 Session 对象)--> [上下文管理]
[状态管理] <--(依赖 history 列表)-- [上下文管理]
[状态管理] --(输出 last_consolidated 边界)--> [记忆系统]
[状态管理] <--(依赖 save() 调用)-- [记忆系统]
[状态管理] --(输出 JSONL 文件)--> [文件系统]
[状态管理] <--(依赖 workspace 路径)-- [初始化与环境]
[状态管理] --(受 _processing_lock 保护)--> [编排循环]
[状态管理] <--(触发 get_or_create/save)-- [编排循环]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | 上下文管理 | `Session.get_history()` 返回未固化消息列表，供 `ContextBuilder.build_messages()` 组装 LLM 输入 | `manager.py:L46-64` → `context.py:L120-144` |
| 依赖 | 上下文管理 | `_save_turn()` 将 `ContextBuilder` 生成的完整消息链（含 tool results）回写 `session.messages` | `loop.py:L458-491` |
| 输出到 | 记忆系统 | `last_consolidated` 索引定义了固化边界，`MemoryConsolidator` 据此选择待归档消息块 | `manager.py:L33` → `memory.py:L260, L337` |
| 依赖 | 记忆系统 | 固化完成后 `MemoryConsolidator` 调用 `sessions.save(session)` 持久化更新后的索引 | `memory.py:L353` |
| 输出到 | 编排循环 | `_processing_lock` 保证 `AgentLoop` 对 `Session` 的读写原子性 | `loop.py:L313` |
| 依赖 | 编排循环 | `AgentLoop._process_message()` 在消息处理前后调用 `get_or_create()` 和 `save()` | `loop.py:L388, L445` |
| 输出到 | 初始化与环境 | `SessionManager` 以 `workspace/sessions/` 为根目录存储 JSONL | `manager.py:L80-82` |
| 依赖 | 初始化与环境 | `Config.workspace_path` 决定会话存储位置 | `schema.py:L164-166` → `manager.py:L80` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **单用户、单进程、低并发**：`_cache` 无大小限制、无过期策略；`_processing_lock` 是全局单锁而非分布式锁。作者假设 nanobot 运行在个人电脑或单容器内，同时只有一个用户在交互。
2. **会话数据量可控**：JSONL 全量覆写（`"w"` 模式）在会话很长时会有性能瓶颈，但作者假设个人助手的单会话消息数在数千条以内，磁盘写入耗时可忽略。
3. **人类可读性优先于机器效率**：选择 JSONL 而非 SQLite，是因为作者认为用户应该能直接用文本编辑器查看和修复会话文件，这是“个人助手”产品体验的一部分。
4. **LLM 调用是主要瓶颈**：后台任务调度（`_schedule_background`）的存在假设 LLM 调用（记忆固化）的耗时远大于状态管理本身，因此将固化移出主路径的收益显著。

### 6.2 这个设计的代价/风险

1. **JSONL 全量覆写的 O(n) 成本**：`save()` 每次都将整个 `session.messages` 序列化到磁盘。若会话积累上万条消息，每次工具调用后的保存都会重写整个文件。代码中未实现增量追加或分片存储。
2. **全局锁的串行瓶颈**：`_processing_lock` 使得所有渠道（CLI、Telegram、Slack 等）的消息完全串行处理。若某一消息触发长耗时工具调用（如大规模文件搜索），其他渠道的消息将被阻塞。虽然子 Agent 可并发，但主 Agent 的响应被锁住了。
3. **缓存无过期，内存泄漏风险**：`_cache` 是普通的 `dict`，`invalidate()` 仅在 `/new` 时调用（`loop.py:L396`）。长期运行的 nanobot 实例若与大量不同 `chat_id` 交互，缓存将持续增长。
4. **`last_consolidated` 与 `messages` 的隐式契约**：`pick_consolidation_boundary()` 假设 `last_consolidated` 之前的消息永远不会被修改或删除。若未来实现“编辑历史消息”功能，该假设将被打破。

### 6.3 如果要重新设计，可能会改变什么

1. **增量持久化**：将 `save()` 改为追加模式（`"a"`），仅在 `_save_turn()` 时写入新增消息；元数据更新（`last_consolidated`、`updated_at`）通过独立的 `.meta` 文件或定时快照处理。这能显著降低长会话的 I/O 成本。
2. **每会话锁 + 全局队列**：将 `_processing_lock` 拆分为 `dict[str, asyncio.Lock]`，允许不同会话的消息并行处理；但需要在 `MemoryConsolidator` 的 Token 估算中加入全局配额协调，防止多个会话同时触发固化导致 LLM API 限流。
3. **缓存 LRU + 持久化懒加载**：为 `_cache` 增加大小上限（如最近 50 个会话），冷会话自动落盘并从内存释放。`list_sessions()` 可直接扫描目录，无需加载全部消息。
4. **`last_consolidated` 改为不可变快照**：不再修改 `Session.messages` 列表，而是将固化后的消息移入只读归档列表，`get_history()` 始终返回“活跃列表”。这能彻底消除索引漂移风险，但会增加内存占用。

### 6.4 对我自己设计 Agent 系统的启示

> **对于个人级、单进程的 AI 助手，状态管理的最小可行方案是：内存 dict 缓存 + 人类可读的逐行文本持久化 + 一把全局锁保平安。** 不要过早引入数据库和分布式锁，除非你的场景明确需要多用户并发或海量历史查询。nanobot 用 213 行代码（`manager.py`）实现了足够好用的会话状态管理，证明了“简单即正确”在个人 Agent 领域的有效性。
