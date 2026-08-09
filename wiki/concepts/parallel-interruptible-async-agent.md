---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [ai-agent-book-async-agent-experiment]
tags: [agent, async-runtime, event-driven, parallelism, interruption, cancellation, asyncio]
---

# 并行和可打断的异步 Agent

并行和可打断的异步 Agent 是一种把**事件接收、模型决策和工具执行解耦**的 Agent Runtime：耗时工具在后台运行，Agent 继续接收新请求；紧急事件可以取消当前 Agent turn 和后台工具；工具完成后再以新事件恢复决策。

## 为什么它不是“同时调用几个工具”

真正需要解决的是三个独立控制问题：

```text
新 Query
   ↓
事件路由器：请求是取消、独立问题还是补充要求？
   ↓
Agent Runtime：是否打断当前 LLM turn？
   ↓
Task Manager：是否终止后台工具及底层资源？
```

因此最小运行时需要：

- 事件分类与路由；
- 分层事件队列；
- 可取消的 Agent turn；
- 带 `task_id` 的异步工具；
- 查询、取消和完成回注；
- 轨迹与任务状态管理。

## 总体架构

```text
用户消息 / 用户打断 / 工具完成事件
                 ↓
              inbox
                 ↓
            _dispatcher
       ┌─────────┼──────────┐
       ↓         ↓          ↓
   INTERRUPT  IMMEDIATE  DEFERRED
   取消当前轮   进入 work   进入 pending
   取消后台任务              等结果到达
       └─────────┬──────────┘
                 ↓
               work
                 ↓
              _worker
                 ↓
      可取消的 turn_task
                 ↓
         LLM → Tool → LLM
                 ↓
     异步工具完成后生成 async.result
                 └──────────→ inbox
```

来源实现使用 Python `asyncio` 单线程协作，详见 [[ai-agent-book-async-agent-experiment]]。

## 1. 新 Query 的属性如何确认

### 实验代码：基于规则的紧急度分类

原始实现位于 `events.py:27-57`：

```python
class Urgency:
    """事件紧急度：决定采用哪种事件处理机制。"""

    INTERRUPT = "interrupt"  # 取消式处理：立刻打断当前执行并取消异步工具
    IMMEDIATE = "immediate"  # 立即处理：不打断后台异步任务，但马上回应（如用户提问）
    DEFERRED = "deferred"    # 排队处理：累积到 pending 队列，任务完成时批量追加


# 打断类关键词：命中即视为紧急打断
_INTERRUPT_KEYWORDS = ["取消", "停止", "中止", "打住", "别做了", "stop", "cancel", "abort"]

# 疑问类信号：命中即视为需要"立即回应"（而不是排队）
_QUESTION_MARKS = ("?", "？")
_QUESTION_KEYWORDS = ["几点", "多少", "怎么", "如何", "为什么", "是不是", "有没有",
                      "吗", "呢", "what", "when", "how", "why", "which"]


def classify_urgency(text: str) -> str:
    """根据用户消息内容判定紧急度。

    规则（简单、可解释，便于书中讲清楚）：
      1. 含打断关键词（取消/停止/stop...） -> INTERRUPT（紧急，取消式处理）
      2. 是一个提问（带问号或疑问词）      -> IMMEDIATE（立即回应，但不打断后台任务）
      3. 其它（补充性指令，如"用日语回复"）-> DEFERRED（排队，批量处理）
    """
    low = text.lower()
    if any(kw in text or kw in low for kw in _INTERRUPT_KEYWORDS):
        return Urgency.INTERRUPT
    if text.strip().endswith(_QUESTION_MARKS) or any(kw in text or kw in low for kw in _QUESTION_KEYWORDS):
        return Urgency.IMMEDIATE
    return Urgency.DEFERRED
```

这套规则对应：

```text
“取消、停止、stop”       → INTERRUPT
“几点、如何、为什么、？” → IMMEDIATE
其他补充性要求            → DEFERRED
```

消息提交时先分类，再放入 `inbox`。原始实现位于 `runtime.py:155-178`：

```python
    async def submit_user_message(self, text: str, urgency: Optional[str] = None) -> None:
        """提交一条用户消息（demo 用它模拟用户输入）。"""
        u = urgency or classify_urgency(text)
        if u == Urgency.INTERRUPT:
            ev = Event(EventType.USER_INTERRUPT, urgency=u,
                       message={"role": "user", "content": f"[用户打断] {text}"},
                       label=f"用户打断：{text}")
        else:
            ev = Event(EventType.USER_INPUT, urgency=u,
                       message={"role": "user", "content": text},
                       label=f"用户消息（{u}）：{text}")
        self.log("USER", f"({u}) {text}")
        await self.inbox.put(ev)

    async def _on_task_complete(self, state: TaskState) -> None:
        """异步任务自然完成 -> 把真实结果作为【新事件】注入 inbox。"""
        ev = Event(
            EventType.ASYNC_RESULT, task_id=state.task_id,
            message={"role": "user",
                     "content": (f"[系统事件｜异步任务完成] task_id={state.task_id} "
                                 f"命令=`{state.command}` 结果：{state.result}")},
            label=f"异步完成 {state.task_id}",
        )
        await self.inbox.put(ev)
```

### 需要额外区分任务依赖性

紧急度不能完整表示 Query 属性。例如“这个脚本为什么这么慢？”是问句，但依赖当前任务；“顺便查一下天气”可能没有问号，却是独立任务。

生产路由至少应输出：

```text
intent       = cancel / new_task / modify_task / query_status / supplement
dependency   = independent / depends_on_current
urgency      = interrupt / immediate / deferred
target_task  = task_id 或 current
confidence   = 分类置信度
```

推荐使用分层路由：

```text
确定性规则
    → 停止、安全、权限和明确 task_id 等强约束
轻量 LLM / Sidecar
    → 判断语义意图、任务依赖和目标任务
低置信度
    → 保守排队或请求用户确认
```

明确停止事件不能只交给主 Agent 判断，因为主 Agent 此时可能正在等待模型或工具。

## 2. 事件如何进入不同处理路径

运行时维护三个容器，原始定义位于 `runtime.py:125-132`：

```python
        self.trajectory: list[Event] = []          # 轨迹（工作记忆）
        self.inbox: asyncio.Queue = asyncio.Queue()  # 所有进来的原始事件
        self.work: asyncio.Queue = asyncio.Queue()   # 待处理的事件批次
        self.pending: list[Event] = []               # 非紧急事件的排队缓冲

        self.tasks = TaskManager(on_complete=self._on_task_complete, log=self.log)
        self.turn_task: Optional[asyncio.Task] = None
        self.running = True
```

职责分别是：

| 容器 | 职责 |
|---|---|
| `inbox` | 接收全部原始事件 |
| `work` | 保存等待 Agent 处理的事件批次 |
| `pending` | 暂存非紧急补充要求 |

`serve()` 同时启动 Dispatcher 和 Worker，原始实现位于 `runtime.py:182-185`：

```python
    async def serve(self) -> None:
        dispatcher = asyncio.create_task(self._dispatcher())
        worker = asyncio.create_task(self._worker())
        await asyncio.gather(dispatcher, worker)
```

因此接收与分流新事件不依赖当前 Agent turn 执行完毕；但模型批次仍由单个 Worker 串行消费。

Dispatcher 的真实分流代码位于 `runtime.py:197-226`：

```python
    async def _dispatcher(self) -> None:
        """事件分流：实现设计文档 5.1 的两种处理机制。"""
        while self.running:
            ev = await self.inbox.get()
            if ev is self._STOP:
                await self.work.put(self._STOP)
                break

            if ev.type == EventType.USER_INTERRUPT:
                # —— 取消式处理：立刻打断当前 turn + 取消所有异步工具 ——
                await self._handle_interrupt(ev)

            elif ev.type == EventType.ASYNC_RESULT:
                # —— 异步结果到达：批量把 pending 一并追加，再触发 LLM ——
                batch = [ev] + self._drain_pending()
                if len(batch) > 1:
                    self.log("SYSTEM", f"异步结果到达，批量处理 {len(batch)-1} 条积压的非紧急事件")
                await self.work.put(batch)

            elif ev.type == EventType.USER_INPUT:
                if ev.urgency == Urgency.IMMEDIATE:
                    # 立即处理（如用户提问），不打断后台异步任务
                    await self.work.put([ev])
                elif self._is_idle():
                    # 空闲时，普通指令也直接处理（例如一开始下达的任务）
                    await self.work.put([ev])
                else:
                    # 排队处理：累积到 pending，等下一次异步结果时批量追加
                    self.pending.append(ev)
                    self.log("SYSTEM", f"事件进入排队缓冲（当前积压 {len(self.pending)} 条）")
```

关键行为：

- `USER_INTERRUPT`：立即进入取消式处理；
- `ASYNC_RESULT`：把工具结果与 `pending` 一次性合并；
- `IMMEDIATE`：直接进入 `work`，不等待后台工具；
- `DEFERRED`：系统忙碌时进入 `pending`。

需要准确理解：当前实现只有一个 `_worker`，因此 `IMMEDIATE` 不会并行抢占正在执行的 LLM turn，只会绕过 `pending`，等待 Worker 的下一次处理机会。

## 3. Agent 循环如何打断

每个事件批次都包装成独立的 `turn_task`，打断时直接取消。原始实现位于 `runtime.py:228-260`：

```python
    async def _handle_interrupt(self, ev: Event) -> None:
        # 1) 取消正在进行的 LLM turn
        if self.turn_task and not self.turn_task.done():
            self.turn_task.cancel()
        # 2) 取消所有后台异步工具
        cancelled = self.tasks.cancel_all()
        # 3) 组装打断批次：打断事件 + 系统回执 + 被丢弃的积压事件（留痕）
        note = Event(
            EventType.SYSTEM_NOTE,
            message={"role": "user",
                     "content": (f"[系统] 已执行打断：取消了后台任务 {cancelled or '（无）'}。"
                                 f"请向用户简短确认已停止。")},
            label=f"打断回执，取消任务 {cancelled or '（无）'}",
        )
        batch = [ev, note] + self._drain_pending()
        await self.work.put(batch)

    async def _worker(self) -> None:
        """逐批处理事件：追加到轨迹后跑一轮可被取消的 LLM。"""
        while self.running:
            batch = await self.work.get()
            if batch is self._STOP:
                break
            self.turn_task = asyncio.create_task(self._process_batch(batch))
            try:
                await self.turn_task
            except asyncio.CancelledError:
                self.log("SYSTEM", "当前 LLM turn 已被打断取消")

    async def _process_batch(self, batch: list[Event]) -> None:
        for e in batch:
            self._append(e)
        await self.run_llm_turn()
```

打断流程：

```text
用户发送“取消”
    ↓
分类为 USER_INTERRUPT
    ↓
turn_task.cancel()
    ↓
当前 LLM await 收到 CancelledError
    ↓
TaskManager.cancel_all()
    ↓
写入打断事件和系统取消回执
    ↓
重新触发一轮 Agent
    ↓
Agent 向用户确认已停止
```

`turn_task.cancel()` 取消的是本地协程。如果它正在等待 `self.client.chat.completions.create()`，本地等待会被取消，但模型供应商是否停止后台推理取决于客户端和供应商是否支持请求取消。

## 4. Agent turn 如何执行模型与工具循环

原始实现位于 `runtime.py:264-309`：

```python
    async def run_llm_turn(self) -> None:
        """调用 LLM 做决策；同步工具就地执行并回填，异步工具启动后回占位符。"""
        for _ in range(MAX_STEPS):
            messages = self.build_messages()
            _t = time.time()
            resp = await self.client.chat.completions.create(
                model=self.model, messages=messages,
                tools=TOOL_SCHEMAS, tool_choice="auto", **self.completion_params,
            )
            self.log("SYSTEM", f"LLM 调用耗时 {time.time()-_t:.2f}s（{len(messages)} 条消息）")
            msg = resp.choices[0].message

            assistant_msg: dict = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                assistant_msg["tool_calls"] = [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ]

            self._append(Event(
                EventType.AGENT_TOOL_CALL if msg.tool_calls else EventType.AGENT_OUTPUT,
                message=assistant_msg,
                label=("调用工具 " + ", ".join(tc.function.name for tc in msg.tool_calls)
                       if msg.tool_calls else "回复用户"),
            ))

            if msg.content and msg.content.strip():
                self.log("AGENT", msg.content.strip())

            if not msg.tool_calls:
                return  # 本轮结束：Agent 给出了最终回复

            # 执行每个工具调用
            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result_text = self._exec_tool(name, args)
                self._append(Event(
                    EventType.TOOL_RESULT,
                    message={"role": "tool", "tool_call_id": tc.id, "content": result_text},
                    label=f"工具结果 {name}",
                ))
```

循环规则是：

```text
构建 trajectory 对应的 messages
    ↓
调用 LLM
    ↓
没有 tool_calls → 本轮结束
    ↓ 有
执行工具并写入 TOOL_RESULT
    ↓
下一次 LLM step
```

`MAX_STEPS` 限制单轮最多八次工具往返，避免无限循环。

## 5. 异步工具如何启动和完成

当模型调用 `run_terminal_command` 时，Runtime 不等待命令完成，而是启动任务并把 `task_id` 占位结果立即回填给模型。原始实现位于 `runtime.py:311-318`：

```python
    def _exec_tool(self, name: str, args: dict) -> str:
        """执行工具，返回给 LLM 的文本结果。"""
        if name == "run_terminal_command":
            command = args.get("command", "")
            state = self.tasks.start(command)
            return (f"命令已在后台【异步】启动。task_id={state.task_id}，命令=`{command}`。"
                    f"我不会阻塞等待；任务完成后其结果会以系统事件形式返回。"
                    f"可用 query_task('{state.task_id}') 查询进度或 cancel_task('{state.task_id}') 取消。")
```

`TaskManager.start()` 使用 `asyncio.create_task()` 启动后台任务并立即返回 `TaskState`，其中包含 `task_id`。原始实现位于 `tasks.py:41-97`：

```python
@dataclass
class TaskState:
    """一个异步终端任务的实时状态。"""

    task_id: str
    command: str
    rate: float
    progress: float = 0.0
    status: str = "running"          # running | completed | cancelled
    result: str = ""
    _task: Optional[asyncio.Task] = field(default=None, repr=False)


class TaskManager:
    """管理所有异步终端任务：启动、查询进度、取消。

    on_complete 回调会在任务自然完成时被调用（用于把真实结果作为"新事件"注入对话）。
    """

    def __init__(self, on_complete: Callable[[TaskState], Awaitable[None]],
                 log: Callable[[str, str], None]):
        self._on_complete = on_complete
        self._log = log
        self._tasks: Dict[str, TaskState] = {}
        self._counter = 0

    def start(self, command: str) -> TaskState:
        """启动一个异步终端命令，立即返回其状态（含 task_id 占位符）。"""
        self._counter += 1
        task_id = f"T{self._counter}"
        state = TaskState(task_id=task_id, command=command, rate=resolve_rate(command))
        self._tasks[task_id] = state
        state._task = asyncio.create_task(self._run(state))
        self._log("TASK", f"启动异步任务 {task_id}: `{command}` (速度 {state.rate:.0f}%/模拟秒)")
        return state

    async def _run(self, state: TaskState) -> None:
        """后台推进进度，直到完成或被取消。"""
        next_milestone = 20.0
        try:
            while state.progress < 100.0:
                await asyncio.sleep(TICK_REAL)
                state.progress = min(100.0, state.progress + state.rate)
                if state.progress >= next_milestone:
                    self._log("TASK", f"{state.task_id} `{state.command}` 进度 {state.progress:.0f}%")
                    next_milestone += 20.0
            state.status = "completed"
            state.result = (f"命令 `{state.command}` 执行完毕：共扫描 12,840 条记录，"
                            f"发现 3 个异常峰值、1 处可疑错误码（HTTP 503 突增），"
                            f"平均响应时间 128ms。")
            self._log("TASK", f"{state.task_id} 完成 ✅")
            await self._on_complete(state)
        except asyncio.CancelledError:
            # 被取消：标记状态并静默退出（不再注入完成结果）
            state.status = "cancelled"
            self._log("TASK", f"{state.task_id} 已被取消 🛑（进度停在 {state.progress:.0f}%）")
            raise
```

任务自然完成时不会直接修改正在进行的模型调用，而是通过回调产生一条新事件。对应 `runtime.py:169-178`：

```python
    async def _on_task_complete(self, state: TaskState) -> None:
        """异步任务自然完成 -> 把真实结果作为【新事件】注入 inbox。"""
        ev = Event(
            EventType.ASYNC_RESULT, task_id=state.task_id,
            message={"role": "user",
                     "content": (f"[系统事件｜异步任务完成] task_id={state.task_id} "
                                 f"命令=`{state.command}` 结果：{state.result}")},
            label=f"异步完成 {state.task_id}",
        )
        await self.inbox.put(ev)
```

完整过程：

```text
run_terminal_command
    ↓
TaskManager.start(command)
    ↓
立即返回 task_id
    ↓
后台 Task 继续推进
    ↓
_on_task_complete(state)
    ↓
生成 async.result
    ↓
inbox.put(event)
    ↓
重新触发 Agent
```

## 6. 工具如何终止

实验中的取消实现位于 `tasks.py:99-121`：

```python
    def query(self, task_id: str) -> Optional[TaskState]:
        return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> bool:
        """按 ID 取消单个任务。"""
        state = self._tasks.get(task_id)
        if state and state.status == "running":
            state.status = "cancelled"
            if state._task:
                state._task.cancel()
            return True
        return False

    def cancel_all(self) -> list[str]:
        """取消所有仍在运行的任务，返回被取消的 task_id 列表。"""
        cancelled = []
        for tid, state in self._tasks.items():
            if state.status == "running":
                state.status = "cancelled"
                if state._task:
                    state._task.cancel()
                cancelled.append(tid)
        return cancelled
```

这里的任务是模拟协程。调用：

```python
state._task.cancel()
```

会在协程下一个 `await` 点注入 `asyncio.CancelledError`，随后 `_run()` 将状态标记为 `cancelled`，并且不再注入完成事件。

### 必须区分三层取消

```text
1. 取消 Agent 思考
   turn_task.cancel()

2. 取消工具控制协程
   asyncio_task.cancel()

3. 终止底层真实资源
   进程信号 / 容器停止 / 远程 cancel API
```

实验只完整覆盖前两层，而且工具本身是模拟任务。不能从该代码推导出“真实 Shell 进程已经被杀死”。

真实工具应根据资源类型提供终止能力：

| 工具资源 | 必须具备的实际终止机制 |
|---|---|
| Python 协程 | `asyncio.Task.cancel()` |
| 本地进程或进程树 | 进程句柄、正常终止、超时后强制终止 |
| 容器任务 | 容器停止或强制结束接口 |
| 远程任务 | 服务端 cancel API |
| 不可逆外部操作 | 执行前审批和幂等保护，通常无法事后取消 |

状态也不应简单从 `running` 直接变成 `cancelled`，生产状态机应表达取消尚未确认：

```text
running
   ↓
cancel_requested
   ↓
cancelling
   ├── 底层确认退出 → cancelled
   ├── 任务抢先完成 → completed
   └── 终止失败     → cancel_failed
```

## 7. 并行执行的边界

适合并行的工具通常满足：

- 任务之间没有数据依赖；
- 只读或副作用彼此隔离；
- 可以独立查询和取消；
- 结果顺序不影响正确性。

并行降低的是墙钟时间：

```text
串行耗时 ≈ t1 + t2 + t3
并行耗时 ≈ max(t1, t2, t3)
```

有副作用、共享可变状态或严格先后依赖的工具不能简单并行。

## 8. 运行时必须保存的状态

每个异步任务至少需要：

```text
task_id
command / operation
status
progress
result / error
底层资源句柄
开始和更新时间
所属 session / turn
取消请求与确认状态
```

轨迹需要记录：

- 用户原始请求；
- 事件分类结果；
- Agent 工具调用；
- 异步占位结果；
- 工具完成事件；
- 用户打断；
- 取消回执与最终状态。

这让 [[agent-trace]]、[[state-management]] 和恢复机制能够重建“任务为什么启动、如何结束、是否真的被取消”。

## 与普通事件驱动 Agent 的区别

```text
普通事件驱动 Agent
    事件到达 → 串行处理 → 输出结果

并行和可打断的异步 Agent
    事件持续到达
       ├── 后台工具并行运行
       ├── 独立问题继续处理
       ├── 补充要求暂存合并
       ├── 紧急事件取消执行
       └── 工具完成后恢复决策
```

核心不只是“异步”，而是：**在并发、延迟、打断和迟到结果同时存在时，仍保持任务状态、上下文轨迹和外部副作用的一致性。**

## 关联概念

- [[orchestration-loop]]
- [[agent-runtime-event-stream]]
- [[agent-tool-system]]
- [[tool-call-lifecycle]]
- [[state-management]]
- [[agent-trace]]
