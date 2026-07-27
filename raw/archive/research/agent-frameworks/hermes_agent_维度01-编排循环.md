# 维度01：编排循环（Orchestration Loop）

## 1. 一句话定位

Hermes Agent 的编排循环是一个**带预算控制、可中断、支持并发工具执行的 ReAct 风格主循环**，核心职责是：在 LLM 推理与工具执行之间反复迭代，直到任务完成、预算耗尽或用户主动中断。

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **LLM 无法自主行动**：没有循环，模型只能做一次性问答，无法根据工具反馈调整策略、修复错误、继续探索。
- **资源失控**：模型可能无限调用工具（尤其是遇到错误时反复重试），导致 API 费用爆炸、上下文窗口撑满。
- **用户体验断裂**：长任务阻塞 UI，用户无法中途干预、修正方向或取消操作。
- **并发浪费**：串行执行独立工具（如同时读多个文件、搜多个关键词）会成倍增加等待时间。

### 2.2 具体触发条件

| 场景 | 触发行为 |
|------|----------|
| 用户发送新消息 | `process_loop` 将消息送入 `_interrupt_queue`，`chat()` 监控队列并调用 `agent.interrupt()` |
| 用户输入 `/steer` | 绕过 `process_loop`，直接调用 `agent.steer()` 注入中途指导 |
| 用户按 Ctrl+C 或关闭终端 | SIGTERM/SIGHUP 处理器调用 `agent.interrupt()`，并等待 grace 窗口 |
| 工具批次包含多个独立调用 | `_should_parallelize_tool_batch()` 返回 True，进入并发路径 |
| API 调用次数达到 `max_iterations` | 注入预算耗尽提示，请求模型总结后退出 |
| 单次 API 调用超过 stale timeout | `_interruptible_api_call()` 杀死连接，进入重试逻辑 |

## 3. 核心设计思路

### 3.1 抽象模型（伪代码）

```python
class AIAgent:
    def run_conversation(self, user_message):
        messages = init_messages(user_message)
        api_call_count = 0
        bind_execution_thread()          # 注册当前线程用于中断定向

        while (api_call_count < max_iterations
               and iteration_budget.remaining > 0)
              or budget_grace_call:       # 预算耗尽后允许最后一次总结调用

            if interrupt_requested:       # 用户中断 → 立即退出
                break

            iteration_budget.consume()    # 消耗一次迭代额度

            steer = drain_pending_steer() # 取出中途用户指导
            api_messages = build_api_messages(messages, steer)
            api_messages = sanitize(api_messages)   # 修复孤儿 tool_call、合并相邻 user

            response = interruptible_api_call(api_messages)  # 可中断的 API 调用

            if response.has_tool_calls:
                if should_parallelize(tool_calls):
                    execute_concurrent(tool_calls, messages)
                else:
                    execute_sequential(tool_calls, messages)
                apply_steer_to_last_tool_result(messages)  # steer 注入最后一个 tool 结果
            else:
                final_response = response.content
                break

        if final_response is None and budget_exhausted:
            final_response = handle_max_iterations(messages)  # 强制总结

        persist_session(messages)
        cleanup_task_resources(task_id)
        return result
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃 | 理由 |
|------|------|------|------|
| 循环终止条件 | `max_iterations` + `IterationBudget` 双保险 + `_budget_grace_call` | 仅单一计数器或纯时间限制 | 防止模型无限循环；grace call 给模型一次体面总结的机会，避免生硬截断 |
| 中断粒度 | **线程级** `_set_interrupt(tid)` + 标志位 `_interrupt_requested` | 全局 Event / 进程信号 | 网关多会话并发场景下，中断必须精确到单个 Agent 会话，不影响其他会话 |
| 并发工具执行 | `ThreadPoolExecutor(max_workers=8)`，静态白名单决策 | asyncio / 进程池 | 工具多为同步 IO（文件、子进程），线程池足够；白名单策略简单可靠 |
| steer 机制 | 不中断循环，将文本注入**最后一个 tool 结果** | 插入新 user message | 保持 role alternation 合法；避免模型将 steer 视为独立用户轮次 |
| API 调用隔离 | 每次请求新建 worker-local client，中断时关闭该 client | 共享全局 client | 防止中断关闭连接污染后续重试或 fallback 请求 |
| 消息清理 | 每次 API 调用前复制 `api_messages`，清理后再发送 | 直接修改原始 messages | 保持持久化历史完整，UI  transcript 与 API 请求解耦 |

### 3.3 数据流 / 控制流

> **整体走向**：用户输入 → CLI 主循环分发 → agent 对话循环（LLM 调用 + 工具执行）→ 会话持久化。
> 左侧是正常对话路径，右侧是运行时中断路径。

```
用户输入
  │
  ▼
CLI.process_loop() ──► _pending_input / _interrupt_queue
  │                          │
  │ (idle)                   │ (agent running)
  │ 闲等用户输入              │ agent 执行中，用户可打断
  ▼                          ▼
chat() ◄───────────────────── interrupt()          ← 两条路径最终汇合回 chat()
  │                              │
  ▼                              ▼
run_conversation()          _interrupt_requested = True     ← 设置中断标记
  │                         _set_interrupt(True, tid)       ← 通过事件通知运行中的线程
  │                         └──► 子 agent.interrupt() 级联  ← 递归打断嵌套子 agent
  ▼
┌─────────────────────────────────────────┐
│  while 循环 (budget + max_iterations)   │  ← agent 的核心循环，受预算和迭代次数约束
│  ├── drain_pending_steer()              │  ← 处理用户中途追加的 steer 指令
│  ├── build_api_messages()               │  ← 将 transcript 转为 API 格式的消息列表
│  ├── sanitize (orphan repair, merge)    │  ← 修复断链的工具调用、合并相邻文本块
│  ├── _interruptible_api_call()          │  ← 调用 LLM（支持中途打断）
│  │   └── 后台线程 + stale timeout       │  ← 超时未响应则视为过期
│  ├── 解析 response (content / tool_calls)│  ← 区分纯文本回复和工具调用请求
│  ├── _execute_tool_calls()              │  ← 执行 LLM 返回的工具调用
│  │   ├── sequential 路径               │  ← 串行执行（适用于有依赖的工具）
│  │   └── concurrent 路径 (ThreadPool)  │  ← 并行执行（独立工具可同时跑）
│  └── apply_steer_to_tool_results()      │  ← 将 steer 指令注入工具返回结果
└─────────────────────────────────────────┘
  │
  ▼
_handle_max_iterations() (budget 耗尽时)   ← 迭代用尽时的收尾处理
  │
  ▼
_persist_session() + _cleanup_task_resources()   ← 保存会话 + 释放线程等资源
```

## 4. 关键机制拆解（含源码）

### 4.1 核心循环与预算控制

**文件**: `run_agent.py:11158`

```python
while (api_call_count < self.max_iterations and self.iteration_budget.remaining > 0) or self._budget_grace_call:
    # ...
    if self._budget_grace_call:
        self._budget_grace_call = False
    elif not self.iteration_budget.consume():
        break
```

**为什么值得看**：双条件循环 + grace call 是防止模型"猝死"的关键设计。预算耗尽后不立即杀死循环，而是设置 `_budget_grace_call = True`，允许最后一次无工具的总结调用（`_handle_max_iterations`）。这避免了用户看到"预算耗尽"的硬错误，而是获得一个自然收尾。

**IterationBudget 实现** (`run_agent.py:272`)：

```python
class IterationBudget:
    def __init__(self, max_total: int):
        self.max_total = max_total
        self._used = 0
        self._lock = threading.Lock()

    def consume(self) -> bool:
        with self._lock:
            if self._used >= self.max_total:
                return False
            self._used += 1
            return True
```

线程安全、可退款（`refund()` 用于 `execute_code` 等程序化调用），父子 Agent 各自独立预算。

### 4.2 可中断的 API 调用

**文件**: `run_agent.py:6661`

```python
def _interruptible_api_call(self, api_kwargs: dict):
    result = {"response": None, "error": None}
    request_client_holder = {"client": None}

    def _call():
        request_client_holder["client"] = self._create_request_openai_client(...)
        result["response"] = request_client_holder["client"].chat.completions.create(**api_kwargs)

    t = threading.Thread(target=_call, daemon=True)
    t.start()
    while t.is_alive():
        t.join(timeout=0.3)
        if self._interrupt_requested:
            self._close_request_openai_client(request_client_holder["client"], reason="interrupt_abort")
            raise InterruptedError("Agent interrupted during API call")
```

**为什么值得看**：API 调用在独立后台线程执行，主循环通过 `join(timeout=0.3)` 轮询检测中断。中断时关闭**该次请求专用的 client**，不影响共享 client 或后续重试。这是网关模式下多会话并发不互相干扰的基石。

### 4.3 线程级中断信号

**文件**: `tools/interrupt.py:35-70`

```python
_interrupted_threads: set[int] = set()
_lock = threading.Lock()

def set_interrupt(active: bool, thread_id: int | None = None) -> None:
    tid = thread_id if thread_id is not None else threading.current_thread().ident
    with _lock:
        if active:
            _interrupted_threads.add(tid)
        else:
            _interrupted_threads.discard(tid)

def is_interrupted() -> bool:
    tid = threading.current_thread().ident
    with _lock:
        return tid in _interrupted_threads
```

**为什么值得看**：全局 `threading.Event` 在网关多会话场景下是灾难——一个会话的中断会杀死所有会话的工具。Hermes 用 `set[int]` 精确到线程 ID，Agent 在 `run_conversation` 开头绑定 `_execution_thread_id`，`interrupt()` 只向该线程及子工作线程传播。

### 4.4 中断传播与级联

**文件**: `run_agent.py:4593`

```python
def interrupt(self, message: str = None) -> None:
    self._interrupt_requested = True
    self._interrupt_message = message
    # 1. 主执行线程
    if self._execution_thread_id is not None:
        _set_interrupt(True, self._execution_thread_id)
    # 2. 并发工具工作线程
    _tracker = getattr(self, "_tool_worker_threads", None)
    if _tracker is not None and _tracker_lock is not None:
        with _tracker_lock:
            _worker_tids = list(_tracker)
        for _wtid in _worker_tids:
            _set_interrupt(True, _wtid)
    # 3. 子 Agent 级联
    with self._active_children_lock:
        children_copy = list(self._active_children)
    for child in children_copy:
        child.interrupt(message)
```

**为什么值得看**：三层传播——主线程、并发工具线程、子 Agent——确保任何深度嵌套的任务树都能被干净中断。`_tool_worker_threads` 在 `ThreadPoolExecutor` 的 worker 函数 `_run_tool` 中动态注册/注销，防止线程复用时残留中断状态。

### 4.5 并发工具执行

**文件**: `run_agent.py:9784`

```python
def _execute_tool_calls_concurrent(self, assistant_message, messages, effective_task_id, api_call_count=0):
    # ...
    max_workers = min(len(runnable_calls), _MAX_TOOL_WORKERS)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, tc, name, args in runnable_calls:
            ctx = contextvars.copy_context()
            f = executor.submit(ctx.run, _run_tool, i, tc, name, args)
            futures.append(f)

        while True:
            done, not_done = concurrent.futures.wait(futures, timeout=5.0)
            if not not_done:
                break
            if self._interrupt_requested:
                for f in not_done:
                    f.cancel()
                concurrent.futures.wait(not_done, timeout=3.0)
                break
```

**为什么值得看**：`contextvars.copy_context()` 确保 worker 线程继承主线程的 ContextVar（如 approval session key）；`timeout=5.0` 轮询既支持心跳（`_touch_activity`）又支持及时响应中断。未启动的 future 被取消，已运行的通过 per-thread interrupt 信号优雅退出。

### 4.6 并行化决策

**文件**: `run_agent.py:377`

```python
def _should_parallelize_tool_batch(tool_calls) -> bool:
    if len(tool_calls) <= 1:
        return False
    tool_names = [tc.function.name for tc in tool_calls]
    if any(name in _NEVER_PARALLEL_TOOLS for name in tool_names):
        return False
    reserved_paths: list[Path] = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        if tool_name in _PATH_SCOPED_TOOLS:
            scoped_path = _extract_parallel_scope_path(tool_name, function_args)
            if any(_paths_overlap(scoped_path, existing) for existing in reserved_paths):
                return False
            reserved_paths.append(scoped_path)
            continue
        if tool_name not in _PARALLEL_SAFE_TOOLS:
            return False
    return True
```

**为什么值得看**：静态白名单 + 路径重叠检测的组合策略。`clarify` 等交互式工具永不并行；`read_file`/`write_file`/`patch` 仅在目标路径不重叠时才并行。这种保守策略避免了并发写冲突和交互死锁。

### 4.7 /steer 中途指导

**文件**: `run_agent.py:4715-4746`

```python
def steer(self, text: str) -> bool:
    with self._pending_steer_lock:
        if self._pending_steer:
            self._pending_steer = self._pending_steer + "\n" + cleaned
        else:
            self._pending_steer = cleaned

def _drain_pending_steer(self) -> Optional[str]:
    with self._pending_steer_lock:
        text = self._pending_steer
        self._pending_steer = None
        return text

def _apply_pending_steer_to_tool_results(self, messages: list, num_tool_msgs: int) -> None:
    steer_text = self._drain_pending_steer()
    # 找到最近的一个 tool message，将 steer 追加到其 content
    for j in range(len(messages) - 1, max(len(messages) - num_tool_msgs - 1, -1), -1):
        if messages[j].get("role") == "tool":
            messages[j]["content"] += f"\n\nUser guidance: {steer_text}"
            break
```

**为什么值得看**：`steer` 不中断循环，而是将用户备注缓存到 `_pending_steer`。在工具批次结束后，将备注注入**最后一个 tool 结果**的 content 中，附以 `"User guidance:"` 标记。这样既让模型在下一轮看到用户意图，又不破坏 `user/assistant/tool` 的 role alternation 约束。

### 4.8 消息清理与防御

**文件**: `run_agent.py:5332`

```python
def _sanitize_api_messages(messages):
    # 1. 丢弃孤儿 tool result（没有对应 assistant tool_call）
    orphaned_results = result_call_ids - surviving_call_ids
    messages = [m for m in messages if not (orphan condition)]
    # 2. 为缺失结果的 tool_call 注入 stub
    missing_results = surviving_call_ids - result_call_ids
    for tc in missing_results:
        messages.append({"role": "tool", "content": "[Result unavailable]", "tool_call_id": cid})
```

**文件**: `run_agent.py:5457`

```python
def _drop_thinking_only_and_merge_users(messages):
    # 丢弃只有 reasoning 没有 content/tool_calls 的 assistant 消息
    # 合并因此相邻的 user 消息
```

**为什么值得看**：压缩、会话恢复、错误重试等操作可能破坏消息序列的合法性。`_sanitize_api_messages` 修复孤儿 tool result；`_drop_thinking_only_and_merge_users` 处理 Anthropic 拒绝的 "thinking-only" 消息。两者都在**API 请求的副本**上操作，不污染持久化历史。

### 4.9 CLI 层面的循环编排

**文件**: `cli.py:11969`

```python
def process_loop():
    while not self._should_exit:
        try:
            user_input = self._pending_input.get(timeout=0.1)
        except queue.Empty:
            if not self._agent_running:
                self._check_config_mcp_changes()
            continue
        # ...
        if _looks_like_slash_command(user_input):
            self.process_command(user_input)
            continue
        self._agent_running = True
        self.chat(user_input)
        self._agent_running = False
```

**文件**: `cli.py:9625`

```python
def run_agent():
    result = self.agent.run_conversation(...)

agent_thread = threading.Thread(target=run_agent, daemon=True)
agent_thread.start()

interrupt_msg = None
while agent_thread.is_alive():
    try:
        interrupt_msg = self._interrupt_queue.get(timeout=0.1)
        if interrupt_msg:
            self.agent.interrupt(interrupt_msg)
            break
    except queue.Empty:
        self._invalidate(min_interval=0.15)
```

**为什么值得看**：CLI 有两层循环——`process_loop` 负责输入分发（命令 vs 聊天），`chat()` 内部将 Agent 运行在 daemon 线程中，主线程通过 `_interrupt_queue` 监控新消息。这种分离使得用户可以在 Agent 运行时输入新消息（触发中断）或 `/steer`（绕过队列直接注入）。

## 5. 与其他维度的交互

| 交互方向 | 维度 | 内容 | 代码交互点 |
|----------|------|------|-----------|
| 编排循环 → 工具系统 | 维度02-工具系统 | 循环调用 `_execute_tool_calls`，分发到具体 tool handler | `run_agent.py:9635` `_execute_tool_calls` → `model_tools.py:679` `handle_function_call` |
| 编排循环 → 记忆系统 | 维度03-记忆系统 | 每 turn 前 `prefetch_all` 注入记忆上下文；`memory` 工具重置 nudge 计数器 | `run_agent.py:10808` `_ext_prefetch_cache`；`run_agent.py:9900` nudge reset |
| 编排循环 → 上下文管理 | 维度04-上下文管理 | 循环内更新 `context_compressor`，触发压缩时分裂 session | `run_agent.py:11260` `update_from_response`；压缩后新 session 继续循环 |
| 编排循环 → Prompt构建 | 维度05-Prompt构建 | 每次 API 调用前组装 `api_messages`，注入 ephemeral system prompt、prefill、memory | `run_agent.py:11220-11300` `api_messages` 构建 |
| 编排循环 → 输出解析 | 维度06-输出解析 | 解析 response 的 `content` vs `tool_calls`，决定循环分支 | `run_agent.py:11500+` response 解析 |
| 编排循环 → 错误处理 | 维度08-错误处理 | API 错误触发重试循环（`retry_count < max_retries`），含 provider fallback | `run_agent.py:11600+` retry loop |
| 编排循环 → 验证循环 | 维度10-验证循环 | tool guardrail 在工具执行前后拦截/观察，可能 halt 循环 | `run_agent.py:9650` `_tool_guardrails.before_call` |
| 编排循环 → 子Agent编排 | 维度11-子Agent编排 | `delegate_task` 创建子 Agent，共享/独立预算，中断级联 | `run_agent.py:9680` `_dispatch_delegate_task`；`run_agent.py:4650` 子 agent interrupt |

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **同步工具为主**：工具大多是文件 IO、子进程、网络请求，ThreadPoolExecutor 足够；没有假设工具是 async-native。
2. **用户可能随时干预**：所有长操作（API 调用、工具执行）都必须可中断，且中断不能泄漏到其他会话。
3. **Provider 不可靠**：API 可能 hung、返回畸形数据、突然变更 schema，因此每次请求前都要 sanitize messages。
4. **Role alternation 是硬约束**：OpenAI/Anthropic 都要求严格的 user/assistant/tool 交替，任何破坏都会导致空响应或 400 错误。

### 6.2 代价/风险

| 风险 | 说明 |
|------|------|
| 线程爆炸 | ThreadPoolExecutor + daemon agent thread + 可能的子 Agent 线程，在极端并发下可能触及系统线程限制（已通过 `_openrouter_prewarm_done` 等 guard 缓解） |
| GIL 瓶颈 | Python GIL 限制了纯 CPU 工具的并发收益，但 IO-bound 工具（网络、文件）受益明显 |
| 中断延迟 | 不支持中断的工具（如没有轮询 `is_interrupted()` 的 web_search）必须跑完，用户可能等待数秒 |
| 状态复杂 | `_interrupt_requested`、`_budget_grace_call`、`_pending_steer`、`_tool_worker_threads` 等多个状态标志相互交织，增加维护难度 |
| 消息清理开销 | 每次 API 调用前遍历全部消息进行 sanitize，长会话时 O(n) 开销不可忽视 |

### 6.3 重新设计可能改变什么

- **引入结构化状态机**：当前循环是 flat while + 大量标志位，可重构为显式状态机（`IDLE → API_CALL → TOOL_EXEC → STEER_INJECTED → ...`），降低认知负担。
- **async-native 重写**：如果工具生态向 async 迁移，可用 `asyncio.gather` 替代 ThreadPoolExecutor，统一取消语义（`asyncio.Task.cancel()`），省去 per-thread interrupt 的复杂性。
- **流式工具结果**：当前工具结果在全部完成后才 append 到 messages，可考虑流式 partial result，让模型更早开始"思考"下一步。
- **预算动态调整**：当前预算是静态的，可根据任务复杂度、历史成功率动态调整 `max_iterations`。

### 6.4 对自己设计 Agent 的启示

1. **预算不是可选功能**：任何生产级 Agent 都必须有迭代预算，且预算耗尽时的用户体验（grace call / 总结）比硬截断重要得多。
2. **中断是架构级设计，不是补丁**：从中断信号 → 线程级传播 → client 关闭 → 子 Agent 级联，每一层都要在设计初期预留接口，事后补极其困难。
3. **保守并发优于激进并发**：Hermes 的静态白名单 + 路径重叠检测虽然不够"智能"，但零误伤、可预测、易调试。并发策略的可靠性比覆盖率更重要。
4. **API 请求副本与持久化历史分离**：`messages`（持久化） vs `api_messages`（请求）的双轨制，是应对 provider schema 差异、压缩、清理的通用模式。
5. **CLI 与 Agent 的线程分离**：将 Agent 放在 daemon 线程中，主线程保持 UI 响应，是交互式 Agent 的经典模式，但队列设计和状态同步需要极其谨慎。
