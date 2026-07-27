# 维度：记忆系统

## 1. 一句话定位

nanobot 的记忆系统通过 **MEMORY.md（长期事实）+ HISTORY.md（可检索日志）** 的双层文件存储，配合 **LLM 驱动的智能固化** 与 **Token 超限触发策略**，在超轻量级架构中实现了上下文窗口的自动管理与会话历史的语义级压缩。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有记忆系统，nanobot 将面临三重系统性故障：

1. **上下文溢出导致请求失败**：当 `Session.messages` 持续增长时，`ContextBuilder.build_messages()` 会将全部历史注入 LLM 请求。`estimate_prompt_tokens_chain()` 估算的 prompt tokens 会超过 `context_window_tokens`（默认 65,536），导致 LLM Provider 返回 400/413 错误，循环直接终止。

2. **历史信息不可检索**：会话历史仅存于 `sessions/{key}.jsonl`，没有全局 grep 能力。用户询问"上周我让你做了什么"时，Agent 无法跨会话检索历史事件。

3. **进程重启后丢失长期上下文**：`SessionManager` 的 `_cache` 是内存字典，进程重启后虽然 JSONL 文件可恢复，但未经压缩的原始消息列表会迅速膨胀，且 Agent 无法继承跨会话的"事实"（如用户偏好、项目结构认知）。

### 2.2 OpenCode 的具体触发条件

- **触发条件 1**：单条消息处理前，`maybe_consolidate_by_tokens()` 检查 `estimated >= context_window_tokens`（`nanobot/agent/memory.py:L313`）
- **触发条件 2**：单条消息处理后，`_schedule_background()` 异步触发二次检查（`nanobot/agent/loop.py:L446`）
- **触发条件 3**：用户发送 `/new` 命令时，`archive_messages()` 将当前会话快照强制归档（`nanobot/agent/loop.py:L399`）

---

## 3. 核心设计思路

> **多轮对话上下文 ≠ 记忆系统**
>
> 多轮对话上下文是完整的原始消息记录，直接注入 LLM 请求；记忆系统则是从中提取、压缩、固化的长期存储。二者对比如下：

| 维度 | 多轮对话上下文 | 记忆系统 |
|------|--------------|---------|
| 存储位置 | `sessions/{key}.jsonl` + 内存 `Session.messages` | `memory/MEMORY.md` + `memory/HISTORY.md` |
| 内容形态 | 原始消息（含 tool_calls、tool 结果等完整链） | LLM 摘要后的结构化事实 + 时间线日志 |
| 如何进入 LLM | 直接作为 `messages` 数组传入 | 通过 `ContextBuilder` 注入 system prompt 的 `# Memory` 区块 |
| 生命周期 | 随会话持续累积，可能溢出 | 跨会话持久，进程重启后仍保留 |
| 触发条件 | 无，始终存在 | token 超限时触发 `consolidate()`，或 `/new` 命令强制归档 |

### 3.1 抽象模型

```
[Session.messages] ──(未固化区)──> [MemoryConsolidator]
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            [Token 估算]      [边界选择]           [LLM 固化]
                    │             │                    │
                    ▼             ▼                    ▼
            超限? ──Yes──> 找用户轮次边界 ──> 调用 save_memory 工具
                    │                                    │
                    No                                   ▼
                    │                            ┌──────────────┐
                    ▼                            ▼              ▼
            保持现状                      [MEMORY.md]    [HISTORY.md]
            (last_consolidated 不变)      (长期事实)      (时间线日志)
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **存储结构** | 双层文件：MEMORY.md（结构化事实）+ HISTORY.md（时间线日志） | 单文件存储或数据库存储 | `memory.py:L76` 注释明确说明："Two-layer memory"；`_get_identity()` (`context.py:L84-85`) 向 LLM 暴露两个文件路径，分别用于"write important facts"和"grep-searchable"，职责分离清晰 |
| **固化策略** | LLM 驱动：通过 `save_memory` 工具调用让 LLM 自主决定如何摘要和更新 | 简单截断旧消息或基于规则的摘要 | `memory.py:L114-199` 的 `consolidate()` 方法构造完整 prompt 并强制 `tool_choice=save_memory`，让 LLM 理解上下文后生成语义摘要；`_format_messages()` (`L103-112`) 保留工具使用痕迹，供 LLM 判断事件重要性 |
| **边界选择** | 以**用户轮次**（`role == "user"`）为最小固化单元 | 按固定消息数截断或按字符数截断 | `memory.py:L266-272`：`pick_consolidation_boundary()` 只在 `idx > start and message.get("role") == "user"` 时标记边界，确保不截断在 assistant-tool 调用中间 |
| **降级策略** | 连续失败 3 次后降级为原始消息归档 (`_raw_archive`) | 失败即丢弃或无限重试 | `memory.py:L78` 定义 `_MAX_FAILURES_BEFORE_RAW_ARCHIVE = 3`；`L201-208` 的 `_fail_or_raw_archive()` 在阈值到达时调用 `_raw_archive()`，保证数据不丢失 |

### 3.3 数据流/控制流

```
输入: Session.messages + last_consolidated
  │
  ▼
[estimate_session_prompt_tokens] ──> 计算当前 prompt 大小
  │
  ▼
[maybe_consolidate_by_tokens] (memory.py:L302)
  │
  ├── estimated < context_window_tokens ──> 空闲，直接返回
  │
  └── estimated >= context_window_tokens ──> 进入循环归档
        │
        ▼
  [pick_consolidation_boundary] (memory.py:L254)
        │
        ├── 找到用户轮次边界 ──> 提取 chunk
        │                         │
        │                         ▼
        │                   [consolidate] (memory.py:L114)
        │                         │
        │                         ├── LLM 调用 save_memory 成功
        │                         │       ├── 更新 MEMORY.md
        │                         │       ├── 追加 HISTORY.md
        │                         │       └── 更新 last_consolidated
        │                         │
        │                         └── LLM 调用失败（3次）
        │                                 └── [_raw_archive] 原始归档
        │
        └── 无安全边界 ──> 终止循环
```

---

## 3.4 关键术语速查

| 术语 | 一句话定义 | 为什么重要 |
|------|-----------|-----------|
| **边界选择** | 在 `Session.messages` 中找到合适的截断点，将待固化的消息划分为语义完整的 chunk | 不能随意截断——Provider 要求 `tool` 消息必须紧跟 `assistant` 的 `tool_calls`，否则会产生"孤儿工具结果"导致 API 错误 |
| **用户轮次** | 以 `role == "user"` 的消息为起点的最小对话单元（用户请求 → Agent 工具调用 → 工具结果 → Agent 回复） | 一个轮次内的因果链不可拆分；`pick_consolidation_boundary` 只在 `role == "user"` 处切割，确保每次归档的都是完整意图 |
| **固化（Consolidation）** | 将一段原始消息历史交给 LLM，由其生成结构化摘要并更新 `MEMORY.md` + `HISTORY.md` 的过程 | 区别于简单截断：用一次 LLM API 调用换取上下文空间的智能压缩，保留可检索的关键事实 |

### 机制 A：双层记忆存储（MemoryStore）

**作用**：提供长期事实存储（MEMORY.md）与可检索历史日志（HISTORY.md）的持久化读写能力。

**设计意图**：为什么不用 SQLite 或 JSON？代码中体现的是"小而美"哲学——直接用 Markdown 文件，用户可用任何文本编辑器查看/编辑，且 `HISTORY.md` 的 `[YYYY-MM-DD HH:MM]` 前缀天然支持 `grep` 检索（`context.py:L85` 明确提示"grep-searchable"）。

**关键源码**（`nanobot/agent/memory.py:75-100`）：
```python
class MemoryStore:
    """Two-layer memory: MEMORY.md (long-term facts) + HISTORY.md (grep-searchable log)."""

    _MAX_FAILURES_BEFORE_RAW_ARCHIVE = 3

    def __init__(self, workspace: Path):
        self.memory_dir = ensure_dir(workspace / "memory")
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.history_file = self.memory_dir / "HISTORY.md"
        self._consecutive_failures = 0

    def read_long_term(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write_long_term(self, content: str) -> None:
        self.memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str) -> None:
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(entry.rstrip() + "\n\n")
```

**MEMORY.md 与 HISTORY.md 的职责对比**：

| | MEMORY.md（结构化事实） | HISTORY.md（时间线日志） |
|---|------------------------|------------------------|
| **组织方式** | 按主题/类别聚合（如 User Preferences、Project Structure） | 按时间顺序排列 |
| **内容粒度** | 结论性、概括性（如"用户偏好 snake_case"） | 事件性、描述性（如"2024-01-15 重构了 auth 模块"） |
| **用途** | 直接注入 system prompt，让 LLM 立即知道"用户是谁、偏好什么" | 供 `grep` 检索，回答"上周做了什么"这类问题 |
| **更新方式** | 覆盖写（LLM 返回完整更新后的内容） | 追加写 |
| **典型示例** | `# User Preferences\n- prefers async/await over callbacks` | `[2024-01-15 14:32] Refactored auth module...` |

---

### 机制 B：LLM 驱动的记忆固化（consolidate）

**作用**：将一段消息历史交给 LLM，让其生成结构化摘要并更新长期记忆。

**设计意图**：为什么不用简单截断或规则摘要？因为 LLM 需要理解**工具调用链的因果关系**（如"用户要求搜索 -> Agent 调用 web_search -> 返回结果 -> Agent 总结"），简单截断会丢失"为什么做了这个决定"的上下文。代码中通过 `_format_messages()` 保留 `tools_used` 信息，让 LLM 在摘要时知道事件全貌。

**关键源码**（`nanobot/agent/memory.py:114-199`）：
```python
    async def consolidate(
        self,
        messages: list[dict],
        provider: LLMProvider,
        model: str,
    ) -> bool:
        """Consolidate the provided message chunk into MEMORY.md + HISTORY.md."""
        if not messages:
            return True

        current_memory = self.read_long_term()
        prompt = f"""Process this conversation and call the save_memory tool with your consolidation.

## Current Long-term Memory
{current_memory or "(empty)"}

## Conversation to Process
{self._format_messages(messages)}"""

        chat_messages = [
            {"role": "system", "content": "You are a memory consolidation agent. Call the save_memory tool with your consolidation of the conversation."},
            {"role": "user", "content": prompt},
        ]

        try:
            forced = {"type": "function", "function": {"name": "save_memory"}}
            response = await provider.chat_with_retry(
                messages=chat_messages,
                tools=_SAVE_MEMORY_TOOL,
                model=model,
                tool_choice=forced,
            )

            if response.finish_reason == "error" and _is_tool_choice_unsupported(
                response.content
            ):
                logger.warning("Forced tool_choice unsupported, retrying with auto")
                response = await provider.chat_with_retry(
                    messages=chat_messages,
                    tools=_SAVE_MEMORY_TOOL,
                    model=model,
                    tool_choice="auto",
                )

            if not response.has_tool_calls:
                logger.warning(
                    "Memory consolidation: LLM did not call save_memory ..."
                )
                return self._fail_or_raw_archive(messages)
            # ... 参数校验与文件写入 ...
```

---

### 机制 C：用户轮次边界选择（pick_consolidation_boundary）

**作用**：在消息列表中找到合适的截断点，确保被固化的 chunk 是语义完整的。

**设计意图**：为什么必须是用户轮次边界？因为 OpenAI/Anthropic 等 Provider 要求消息序列中 `tool` 消息必须紧跟在 `assistant` 的 `tool_calls` 之后。如果在 assistant-tool 中间截断，会导致 `get_history()` 返回"孤儿工具结果"，引发 API 错误。代码中 `Session.get_history()` (`session/manager.py:L51-55`) 也做了同样的保护："Drop leading non-user messages to avoid orphaned tool_result blocks"。

**关键源码**（`nanobot/agent/memory.py:254-274`）：
```python
    def pick_consolidation_boundary(
        self,
        session: Session,
        tokens_to_remove: int,
    ) -> tuple[int, int] | None:
        """Pick a user-turn boundary that removes enough old prompt tokens."""
        start = session.last_consolidated
        if start >= len(session.messages) or tokens_to_remove <= 0:
            return None

        removed_tokens = 0
        last_boundary: tuple[int, int] | None = None
        for idx in range(start, len(session.messages)):
            message = session.messages[idx]
            if idx > start and message.get("role") == "user":
                last_boundary = (idx, removed_tokens)
                if removed_tokens >= tokens_to_remove:
                    return last_boundary
            removed_tokens += estimate_message_tokens(message)

        return last_boundary
```

---

### 机制 D：降级归档（_fail_or_raw_archive / _raw_archive）

**作用**：当 LLM 固化连续失败时，保证数据不丢失，以原始格式归档。

**设计意图**：为什么不是"失败就放弃"？因为消息历史是用户数据的唯一副本（`/new` 命令会 `session.clear()`），丢失意味着不可逆的信息缺失。`_raw_archive()` 保留了完整消息内容，虽然不可读性较差，但保证了审计追踪的完整性。

**关键源码**（`nanobot/agent/memory.py:201-219`）：
```python
    def _fail_or_raw_archive(self, messages: list[dict]) -> bool:
        """Increment failure count; after threshold, raw-archive messages and return True."""
        self._consecutive_failures += 1
        if self._consecutive_failures < self._MAX_FAILURES_BEFORE_RAW_ARCHIVE:
            return False
        self._raw_archive(messages)
        self._consecutive_failures = 0
        return True

    def _raw_archive(self, messages: list[dict]) -> None:
        """Fallback: dump raw messages to HISTORY.md without LLM summarization."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.append_history(
            f"[{ts}] [RAW] {len(messages)} messages\n"
            f"{self._format_messages(messages)}"
        )
        logger.warning(
            "Memory consolidation degraded: raw-archived {} messages", len(messages)
        )
```

---

### 机制 E：Token 超限触发与并发安全（maybe_consolidate_by_tokens）

**作用**：在消息处理前后自动检测并执行记忆固化，同时保证同一会话的并发安全。

**设计意图**：为什么是"处理前+后台"双触发？处理前触发防止当前请求直接溢出；后台触发（`_schedule_background`）是为了不阻塞用户响应——`loop.py:L446` 在 `_save_turn()` 和 `sessions.save()` 之后才调度后台任务，确保用户先收到回复，固化在后台完成。

**关键源码**（`nanobot/agent/memory.py:302-357`）：
```python
    async def maybe_consolidate_by_tokens(self, session: Session) -> None:
        """Loop: archive old messages until prompt fits within half the context window."""
        if not session.messages or self.context_window_tokens <= 0:
            return

        lock = self.get_lock(session.key)
        async with lock:
            target = self.context_window_tokens // 2
            estimated, source = self.estimate_session_prompt_tokens(session)
            if estimated <= 0:
                return
            if estimated < self.context_window_tokens:
                # 空闲状态，直接返回
                return

            for round_num in range(self._MAX_CONSOLIDATION_ROUNDS):
                if estimated <= target:
                    return

                boundary = self.pick_consolidation_boundary(session, max(1, estimated - target))
                if boundary is None:
                    return

                end_idx = boundary[0]
                chunk = session.messages[session.last_consolidated:end_idx]
                if not chunk:
                    return

                if not await self.consolidate_messages(chunk):
                    return
                session.last_consolidated = end_idx
                self.sessions.save(session)

                estimated, source = self.estimate_session_prompt_tokens(session)
```

### 机制 E 补充：`_schedule_background` 的后台化原理

机制 E 中提到"后台触发"，其核心实现（`loop.py:L345-349`）非常精简：

```python
def _schedule_background(self, coro) -> None:
    task = asyncio.create_task(coro)           # 1. 创建任务，不 await，立即"后台"执行
    self._background_tasks.append(task)         # 2. 加入跟踪列表
    task.add_done_callback(self._background_tasks.remove)  # 3. 完成后自动清理
```

**关键点**：
- `asyncio.create_task(coro)` 把协程包装成 `Task` 并立即丢进事件循环执行，函数本身同步返回，不会阻塞当前消息处理
- `_background_tasks` 用于生命周期管理：`__aexit__` 时会 `await asyncio.gather(...)` 等待所有后台任务完成，确保进程关闭前固化不丢数据
- `add_done_callback` 避免列表无限膨胀

注意：这不是真多线程，所有代码仍跑在单个事件循环中；`create_task` 只是让协程并发调度，遇到 IO（LLM API 调用）时让出执行权。对于记忆固化这种 IO 密集型后台工作，这是最合适的选择。

---

## 5. 与其他维度的交互

```
[记忆系统] --(MEMORY.md 内容)--> [Prompt 构建]
[记忆系统] --(last_consolidated 更新)--> [状态管理]
[记忆系统] <--(Session.messages + get_history)-- [状态管理]
[记忆系统] <--(build_messages + tool_definitions)-- [上下文管理 / 工具系统]
[记忆系统] <--(LLMProvider.chat_with_retry)-- [编排循环]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | Prompt 构建 | `MemoryStore.get_memory_context()` 返回的 `# Memory` 区块被注入 System Prompt | `nanobot/agent/context.py:L35-37` |
| 输出到 | 状态管理 | 固化成功后更新 `session.last_consolidated` 并持久化 | `nanobot/agent/memory.py:L352-353` |
| 依赖 | 状态管理 | 读取 `session.messages` 和 `last_consolidated` 计算待固化 chunk | `nanobot/agent/memory.py:L260, L337` |
| 依赖 | 上下文管理 | 调用 `build_messages()` 构建 probe 消息以估算 tokens | `nanobot/agent/memory.py:L280-285` |
| 依赖 | 工具系统 | 调用 `get_tool_definitions()` 将工具定义纳入 token 估算 | `nanobot/agent/memory.py:L290` |
| 依赖 | 编排循环 | 通过 `provider.chat_with_retry()` 调用 LLM 执行固化 | `nanobot/agent/memory.py:L140-156` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **作者假设 LLM 的摘要质量足够高**：`consolidate()` 没有后验校验（如对比摘要前后的事实一致性），直接信任 `save_memory` 返回的 `memory_update` 覆盖 MEMORY.md。
2. **作者假设用户轮次是自然的语义边界**：`pick_consolidation_boundary` 只在 `role == "user"` 处切割，隐含假设用户发起的新请求是一个独立话题单元。
3. **作者假设 Markdown 文件比数据库更"小而美"**：整个记忆系统零外部依赖（无 SQLite、无向量库），仅靠文件 IO 和 LLM 调用完成。

### 6.2 这个设计的代价/风险

1. **LLM 固化成本**：每次固化都是一次额外的 LLM API 调用（含 tool 定义），在高频对话场景下会产生不可忽略的延迟和费用。代码中通过 `_schedule_background` 将其异步化，但 API 调用本身无法避免。
2. **并发锁的粒度偏粗**：`get_lock(session.key)` 使用 `WeakValueDictionary` 管理锁，虽然避免了内存泄漏，但同一会话的所有消息处理（包括正常回复和后台固化）串行化，在高并发渠道（如群聊@）可能成为瓶颈。
3. **Token 估算的准确性**：`estimate_prompt_tokens_chain` 先尝试 provider counter 再 fallback 到 tiktoken，但 tiktoken 的 `cl100k_base` 与实际模型（如 Claude、Gemini）的 tokenizer 不一致，可能导致估算偏差，出现"预估未超限但实际请求超限"的 corner case。
4. **MEMORY.md 的覆盖写风险**：`write_long_term()` 是全量覆盖写入（`L92`），如果 LLM 在 `memory_update` 中遗漏了旧事实，则永久丢失。代码中没有 diff/merge 机制。

### 6.3 如果要重新设计，可能会改变什么

1. **增量更新 MEMORY.md**：将覆盖写改为基于段落/主题的增量更新，或要求 LLM 返回"新增/删除/修改"的结构化 diff，降低事实丢失风险。
2. **向量检索层**：当 HISTORY.md 增长到数万行时，线性 grep 效率下降。可考虑轻量级嵌入（如 ollama 本地 embedding）做语义检索，但会违背"超轻量"哲学。
3. **Token 估算前置缓存**：`estimate_session_prompt_tokens()` 每次构建 probe messages 并调用 tiktoken，开销可优化为增量计算（新消息 tokens = 上次估算 + delta）。
4. **固化策略参数化**：当前 `target = context_window_tokens // 2` 是硬编码，可暴露为配置项，让用户在"激进压缩（省 token）"和"保守压缩（保留上下文）"间权衡。

### 6.4 对我自己设计 Agent 系统的启示

> **"用 LLM 做压缩，用文件做存储，用用户轮次做边界"** —— 这三句话概括了 nanobot 记忆系统的核心智慧。在资源受限的场景下，不需要向量数据库或复杂的 RAG 管道：一个 Markdown 文件 + 一次 LLM tool call + 一个 `last_consolidated` 指针，就能实现可扩展、可审计、可人工干预的记忆管理。最关键的设计是**降级路径**：当智能固化失败时，原始归档保证了数据零丢失，这比"追求完美摘要"更务实。
