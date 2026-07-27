# 维度名：编排循环（Agent Loop / Orchestration Loop）

## 1. 一句话定位

编排循环是 nanobot 的"心脏泵"——它从消息总线消费一条用户消息后，把"调用 LLM、执行工具、再调用 LLM"这条 ReAct 链路反复推进，直到模型不再请求工具或达到 40 轮上限，最终把回答推回总线。在它之上，还套了一层"任务派发 + 全局锁 + /stop 取消"的并发外壳，使得"长时推理"和"对中断信号的即时响应"得以共存。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果把 `_run_agent_loop()`（`nanobot/agent/loop.py:183-254`）剥掉，单次 `provider.chat_with_retry()` 只能拿到一个 LLM 响应——一旦模型返回 `tool_calls`，调用方会得到一个"未消化的工具调用列表"，没有人执行它、没有人把结果灌回模型，对话直接断在 ReAct 的"Act"步骤上，用户视角就是"机器人说要查日历，然后没了下文"。

如果再剥掉外层的 `run()` + `_dispatch()`（`loop.py:256-331`），系统退化成"同步消费 → 同步处理 → 下一条"。这意味着：
- `/stop` 永远等不到处理时机：当主循环正在 `await chat_with_retry()` 时，下一条 `consume_inbound()` 不会被调用，`/stop` 滞留在队列里，直到当前任务跑满 40 轮。
- 后台记忆固化（`_schedule_background(...)`）没有寄主，`close_mcp()` 中的 `_background_tasks` 列表无从存在。
- `_processing_lock` 不存在，会导致同一会话两条消息并发改 `session.messages`，触发交错写入和持久化竞态。

如果再去掉 `finish_reason == "error"` 这条分支（`loop.py:236-239`），错误响应会被 `add_assistant_message` 写入 `messages` 并最终 `_save_turn` 持久化到 JSONL；下一轮 LLM 看到一个 role=assistant、content=错误字符串的消息，常常会反复触发 400（issue #1303 的根因），形成"毒消息→永久 400"循环。

### 2.2 nanobot 的具体触发条件

| 触发点 | 条件 | 代码位置 |
|--------|------|----------|
| 进入主循环 | `run()` 被 gateway 启动后 `_running=True` 时常驻 | `loop.py:262` |
| 派发新任务 | `cmd` 不是 `/stop`/`/restart` 时 `asyncio.create_task(_dispatch(msg))` | `loop.py:277-279` |
| 一轮 LLM 调用 | `iteration < self.max_iterations`（默认 40） | `loop.py:194-203` |
| 继续下一轮 | `response.has_tool_calls` 为真，工具执行完后回到 `while` 顶 | `loop.py:205-231` |
| 终止循环 | 模型不再请求工具（普通回复）或 `finish_reason == "error"` | `loop.py:232-245` |
| 强制兜底 | `iteration >= self.max_iterations` 后输出"达到最大轮次"文本 | `loop.py:247-252` |
| 中断现有任务 | inbound 消息内容 strip+lower == `/stop` | `loop.py:272-273` |
| 进程级重启 | `/restart` → `os.execv` 替换镜像 | `loop.py:274-275, 297-309` |

---

## 3. 核心设计思路

### 3.1 抽象模型

伪代码视角：编排循环是**两层嵌套**——外层是 actor 风格的"消息泵 + 并发任务表"，内层是经典的 ReAct 状态机。

```python
# 外层：actor / dispatcher 模式
loop forever:
    msg = bus.consume_inbound(timeout=1s)        # 1s 心跳，让 _running 翻转可被察觉
    match msg.cmd:
        "/stop":    cancel(active_tasks[msg.session_key])   # 同步处理，不下派
        "/restart": schedule(os.execv)                       # 同步处理
        else:       task = create_task(_dispatch(msg))       # 异步派发
                    active_tasks[session_key] += [task]      # 登记，供 /stop 找到

# _dispatch：每会话进入全局锁，串行化所有真正的 LLM 工作
async def _dispatch(msg):
    async with _processing_lock:
        _process_message(msg)

# 内层：ReAct 状态机
async def _run_agent_loop(messages):
    for iter in range(max_iterations):
        resp = provider.chat_with_retry(messages, tools)
        if resp.has_tool_calls:
            messages += assistant(resp.content, tool_calls)
            for tc in resp.tool_calls:
                result = tools.execute(tc.name, tc.arguments)
                messages += tool_result(tc.id, result)
            continue
        if resp.finish_reason == "error":
            return clean(resp.content)            # 不持久化，不写历史
        return clean(resp.content)                # 正常回复，持久化
    return "达到最大轮次"                          # 兜底
```

要点：
- "派发"是异步的（`create_task`），但"执行"是串行的（`_processing_lock` 是单例 Lock，跨所有会话共享）。这意味着 nanobot 在任意时刻只跑一个 `_process_message`，而 `/stop` 因为不进锁，可以在工作进行中被"插队"处理——这是一个明确的吞吐 vs 可中断性权衡。
- 内层循环把"是否还要继续"完全交给 LLM 的 `has_tool_calls` 判断，nanobot 自己不做任何"任务完成度"评估。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 派发并发模型 | `create_task` 派发 + 全局 `asyncio.Lock` 串行 | (a) 完全串行（loop 内同步处理）；(b) 完全并发（每会话一个 lock 或无锁） | `loop.py:277-279` 派发为 task，但 `loop.py:313` 又立刻 `async with self._processing_lock`——作者要的是"派发即返回主循环"以保证 `/stop` 可被消费，而不是"多会话并行推理"。代价是吞吐天花板=1，但单进程个人助手场景下 LLM 是瓶颈，不是 CPU |
| 控制信号通路 | `/stop`、`/restart` 走"同一个 inbound 队列"、字符串前缀识别 | 单独开 control queue / signal handler / RPC | `loop.py:271-275` 把 `cmd = msg.content.strip().lower()` 作为开关。优势：渠道无需特殊化 control 路径，任何聊天界面 (Telegram/Discord/CLI) 直接打 `/stop` 即可；劣势：无法在 LLM 推理 await 中插入——必须等 `consume_inbound` 拿到下一条 |
| 主循环阻塞策略 | `wait_for(consume_inbound(), timeout=1.0)` 超时再循环 | `await consume_inbound()` 直接阻塞 | `loop.py:264` 的 1s 超时是为了让 `self._running = False` 能在 1s 内被察觉而退出，而不是让线程挂死在 queue 上。这是个朴素的 polling 解决"优雅关停"问题 |
| ReAct 终止判据 | `has_tool_calls` 为假即视为最终回复 | 解析 `<final_answer>` 标签 / 模型 self-report 完成 | `loop.py:205, 232` 完全依赖 OpenAI 风格的 tool_calls 字段——这是把"何时收尾"的判断**完全外包给 LLM 协议层**，不引入任何自定义协议。代价是必须信任 provider 把 `finish_reason` 返成 `tool_calls` 还是 `stop` 是准确的 |
| 最大轮次上限 | 硬编码默认 40，作为兜底而非主出口 | 不设上限 / token 上限 / 时间上限 | `loop.py:57, 247-252` 选了"轮次"这个最直观的预算单位。40 这个值能让一个非平凡任务（找文件、读、改、再确认）跑完，但能拦住"模型死循环调用同一个工具"的退化。注意这里给用户的兜底文案是建议"拆小步骤"而不是抛异常 |
| Error 响应隔离 | `finish_reason=="error"` 时 `break` 但**不写入 messages** | 跟普通响应一视同仁地持久化 | `loop.py:236-239` 注释明确指向 issue #1303："error responses 会 poison context 导致永久 400 loop"。错误内容只回传给用户当一次性反馈，session 状态保持干净 |
| `/new` 命令的副作用 | 立即清空 + 立即返回 + **后台**归档快照 | 同步归档（用户等待）/ 异步清空 | `loop.py:392-402`：先 `session.clear() / save() / invalidate()` 三连，然后 `_schedule_background(archive_messages(snapshot))`。这是用 `_background_tasks` 列表 + `close_mcp()` drain 的方式，保证"快速响应"和"不丢数据"同时成立 |
| `_run_agent_loop` 返回三元组 | `(final_content, tools_used, all_msgs)` | 把 messages 直接 mutate 进 session | 内层循环对 messages 是**纯函数式拼接**（`add_assistant_message`、`add_tool_result` 都返回新列表，参见 `loop.py:218, 229`），session 的写入在外层 `_save_turn` 完成。这让"会话状态"和"模型推理状态"解耦——内循环失败不会污染 session |

### 3.3 数据流/控制流

```
渠道 (Telegram/Discord/...)
   │ publish_inbound(InboundMessage)
   ▼
MessageBus.inbound (asyncio.Queue)         <─── /stop /restart /new 也走这里
   │ consume_inbound() in run()              loop.py:264
   ▼
run() [loop.py:256]
   ├──> if /stop:    _handle_stop  (同步处理，cancel active_tasks)
   ├──> if /restart: _handle_restart (os.execv)
   └──> else: create_task(_dispatch(msg))   [loop.py:277]
                │
                ▼
            _dispatch [loop.py:311]
                │  async with _processing_lock:
                ▼
            _process_message [loop.py:356]
                ├── /new /help 短路
                ├── memory_consolidator.maybe_consolidate_by_tokens(session)  # 入口前压缩
                ├── _set_tool_context (channel/chat_id 注入工具)
                ├── context.build_messages(history, current_message)
                │
                ▼
            _run_agent_loop [loop.py:183]
                │  iter += 1
                │  response = provider.chat_with_retry(messages, tools)
                │
                ├── has_tool_calls:
                │     messages = add_assistant_message(...)
                │     for tc: result = tools.execute(tc); messages = add_tool_result(...)
                │     loop
                │
                └── 普通回复 / error:
                      final_content = clean
                      break
                │
                ▼
        _save_turn (持久化新增 messages，截断超大 tool 结果)
        sessions.save(session)
        _schedule_background(maybe_consolidate_by_tokens)
                │
                ▼
        bus.publish_outbound(OutboundMessage)   ── 渠道消费
```

值得注意的是"压缩调用"出现两次：进入 `_process_message` 前同步调一次（确保本次推理上下文不爆），完成后再后台调一次（为下一次缩短上下文，但不阻塞用户）。这种"前置 + 后置"的双调，把延迟与新鲜度做了均衡。

---

## 4. 关键机制拆解（含源码）

### 机制 A：ReAct 内循环——纯函数式 messages 拼接

**作用**：在一次用户输入到一次最终回复之间，反复"调 LLM → 执行工具 → 把工具结果灌回 LLM"，直到模型不再请求工具。

**设计意图**：作者刻意让 `_run_agent_loop` 既不读 session 也不写 session——它接收一个 `initial_messages`，所有中间态只通过 `add_assistant_message` / `add_tool_result` 返回新的 messages 列表。这样 ReAct 状态机就是一个**可独立测试、可被任何外层调用方复用**的纯逻辑：CLI 单次任务 (`process_direct`)、聊天会话 (`_process_message`)、cron / heartbeat 触发都共享它，只是各自决定要不要持久化。

**关键源码**（`nanobot/agent/loop.py:194-245`）：
```python
while iteration < self.max_iterations:
    iteration += 1
    tool_defs = self.tools.get_definitions()                # ① 每轮都重取 —— 让 MCP/spawn 等动态工具生效
    response = await self.provider.chat_with_retry(
        messages=messages, tools=tool_defs, model=self.model,
    )
    if response.has_tool_calls:                              # ② 决策点：模型说还要继续
        # ...progress 回调（边推理边推送 thought / tool_hint）...
        tool_call_dicts = [tc.to_openai_tool_call() for tc in response.tool_calls]
        messages = self.context.add_assistant_message(       # ③ 纯函数：返回新 list
            messages, response.content, tool_call_dicts,
            reasoning_content=response.reasoning_content,
            thinking_blocks=response.thinking_blocks,
        )
        for tool_call in response.tool_calls:
            tools_used.append(tool_call.name)
            result = await self.tools.execute(tool_call.name, tool_call.arguments)
            messages = self.context.add_tool_result(
                messages, tool_call.id, tool_call.name, result
            )
    else:
        clean = self._strip_think(response.content)
        if response.finish_reason == "error":                # ④ Error 隔离：不进 messages
            final_content = clean or "Sorry, I encountered an error calling the AI model."
            break
        messages = self.context.add_assistant_message(...)
        final_content = clean
        break
```

值得指出的几处"为什么这样写"：
- ① `tool_defs` 每轮重取而非循环外缓存：是为支持子 Agent 在中途注册工具、MCP 在 `_connect_mcp()` 完成后追加工具——动态工具集是 nanobot 的一等公民。
- ③ 把 `provider_specific_fields` 通过 `to_openai_tool_call()` 序列化进 messages：这是为了把 Anthropic / Bedrock 等 provider 的"思考块"原样回灌，让下一轮 LLM 能看到自己的推理痕迹（兼容 Anthropic 的 extended thinking）。
- ④ error 分支只 `break` 不持久化是 #1303 的修复——一个表层简单的早返，背后是一段事故学习。

### 机制 B：派发并发模型——异步 task + 全局锁

**作用**：让消息消费循环永远活跃，但同时保证"真正的工作"是串行的。

**设计意图**：直观做法是 `await self._process_message(msg)` 直接同步执行，但那样 `/stop` 永远等不到处理。直观的反向做法是给每个会话一个独立 lock，但作者放弃了——nanobot 是"个人助手 + 单 LLM 后端"，并发执行多会话只会让 token 配额和 provider rate-limit 拥塞。所以选了一个**第三条路**：派发用 task（让外层循环立即解放），执行用全局锁（让真正干活的部分串行）。`/stop` 不进锁，所以即使有任务在跑它也能立即生效。

**关键源码**（`nanobot/agent/loop.py:262-279, 311-331`）：
```python
while self._running:
    try:
        msg = await asyncio.wait_for(self.bus.consume_inbound(), timeout=1.0)  # 1s 心跳
    except asyncio.TimeoutError:
        continue
    cmd = msg.content.strip().lower()
    if cmd == "/stop":
        await self._handle_stop(msg)         # 同步处理：cancel _active_tasks[session_key]
    elif cmd == "/restart":
        await self._handle_restart(msg)      # 同步处理：os.execv
    else:
        task = asyncio.create_task(self._dispatch(msg))            # 派发：立即返回
        self._active_tasks.setdefault(msg.session_key, []).append(task)
        task.add_done_callback(lambda t, k=msg.session_key:
            self._active_tasks.get(k, []) and self._active_tasks[k].remove(t)
            if t in self._active_tasks.get(k, []) else None)        # 任务表自清理

async def _dispatch(self, msg: InboundMessage) -> None:
    async with self._processing_lock:                              # 全局锁，单实例
        try:
            response = await self._process_message(msg)
            if response is not None:
                await self.bus.publish_outbound(response)
            elif msg.channel == "cli":
                # CLI 即使空响应也要回个 sentinel，防止 CLI 端死等
                await self.bus.publish_outbound(OutboundMessage(...content="",...))
        except asyncio.CancelledError:
            logger.info("Task cancelled for session {}", msg.session_key); raise
        except Exception:
            logger.exception("Error processing message ...")
            await self.bus.publish_outbound(OutboundMessage(... content="Sorry, ..."))
```

值得指出的设计细节：
- `_active_tasks` 按 `session_key` 分桶，是为 `/stop` 提供"按会话取消"的能力——`_handle_stop` 只取出 `pop(msg.session_key)` 那一组，不会误伤其他会话的任务。
- `done_callback` 用 lambda 自动从 `_active_tasks` 移除：避免内存中堆积已完成 task 的引用，简单却必要。
- `_processing_lock` 是 `asyncio.Lock()`（`loop.py:104`），是"全局单例"——这意味着即使两个 channel 各发了一条消息，第二条也要等第一条跑完。这个权衡的合理性来源于：nanobot 的 provider 通常是"一个 API key，一个 rate limit"，并发执行没有真正的吞吐收益。

### 机制 C：`/new` 的"立即返回 + 后台归档"

**作用**：用户敲 `/new`，应该立刻看到"新会话"提示而不是等几十秒的 LLM 摘要；但已有的对话不应该直接丢弃，需要归档以便后续记忆系统使用。

**设计意图**：早期版本是同步压缩 → 用户阻塞，体验差；naive fix 是 `asyncio.create_task` 然后忘掉它，但进程退出时归档可能没跑完，造成数据丢失。最终方案是引入 `_background_tasks` 列表 + `close_mcp()` 的 drain 阶段，把"快速响应"和"不丢数据"做成两个不冲突的承诺。

**关键源码**（`nanobot/agent/loop.py:392-402, 333-349`）：
```python
if cmd == "/new":
    snapshot = session.messages[session.last_consolidated:]   # 抓未固化的部分
    session.clear()
    self.sessions.save(session)
    self.sessions.invalidate(session.key)                     # 缓存也清
    if snapshot:
        self._schedule_background(self.memory_consolidator.archive_messages(snapshot))
    return OutboundMessage(channel=msg.channel, chat_id=msg.chat_id,
                          content="New session started.")     # 立即返回

def _schedule_background(self, coro) -> None:
    task = asyncio.create_task(coro)
    self._background_tasks.append(task)
    task.add_done_callback(self._background_tasks.remove)     # 完成自摘除

async def close_mcp(self) -> None:
    if self._background_tasks:
        await asyncio.gather(*self._background_tasks, return_exceptions=True)  # 必须等完
        self._background_tasks.clear()
    if self._mcp_stack:
        try:
            await self._mcp_stack.aclose()
        except (RuntimeError, BaseExceptionGroup):
            pass  # MCP SDK cancel scope cleanup is noisy but harmless
```

要点：
- `snapshot = messages[last_consolidated:]`：只归档"还没固化过的部分"，避免重复归档已经压缩进 MEMORY.md 的内容——这是和记忆系统的契约性 handshake。
- `close_mcp()` 在 drain 完后才关闭 MCP，是因为归档过程本身可能调用 LLM；如果 MCP 先关，归档可能因为工具不可用失败。顺序敏感。
- 这套 `_schedule_background` 还被 `_process_message` 末尾的"后台再压一次记忆"复用（`loop.py:446`），本质上是 nanobot 自己的"轻量 fire-and-forget with shutdown drain"机制。

### 机制 D：进度回调与 `<think>` 剥离

**作用**：在多轮工具调用之间向用户推送"思考片段"和"正在调什么工具"，让长时任务有可观察性。

**设计意图**：如果不报告进度，用户面对一个 30 秒沉默的机器人会失去信心。但 raw 模型输出常带 `<think>...</think>` 块（DeepSeek-R1、Kimi 等），不能直接发给用户。`_strip_think` + `_tool_hint` 把"渲染层逻辑"集中在 loop 里而不是污染 provider 层。

**关键源码**（`nanobot/agent/loop.py:165-181, 205-212, 429-435`）：
```python
@staticmethod
def _strip_think(text: str | None) -> str | None:
    if not text:
        return None
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip() or None

@staticmethod
def _tool_hint(tool_calls: list) -> str:
    def _fmt(tc):
        args = (tc.arguments[0] if isinstance(tc.arguments, list) else tc.arguments) or {}
        val = next(iter(args.values()), None) if isinstance(args, dict) else None
        if not isinstance(val, str):
            return tc.name
        return f'{tc.name}("{val[:40]}…")' if len(val) > 40 else f'{tc.name}("{val}")'
    return ", ".join(_fmt(tc) for tc in tool_calls)

# 在 _run_agent_loop 中：
if on_progress:
    thought = self._strip_think(response.content)
    if thought:
        await on_progress(thought)                             # 推思考摘要
    tool_hint = self._tool_hint(response.tool_calls)
    tool_hint = self._strip_think(tool_hint)
    await on_progress(tool_hint, tool_hint=True)               # 推工具调用提示

# 在 _process_message 中定义的 _bus_progress：
async def _bus_progress(content: str, *, tool_hint: bool = False) -> None:
    meta = dict(msg.metadata or {})
    meta["_progress"] = True
    meta["_tool_hint"] = tool_hint
    await self.bus.publish_outbound(OutboundMessage(
        channel=msg.channel, chat_id=msg.chat_id, content=content, metadata=meta,
    ))
```

设计细节：
- `_tool_hint` 取第一个参数的值并截断到 40 字符——这是个"够用就好"的启发式，模型大部分工具调用的第一个参数就是最有信息量的（query / path / message），不必通用化。
- progress 通过 `metadata["_progress"]=True` 标志和最终回复区分，由渠道层决定是流式更新一条消息还是发新消息——loop 不假设 channel 的 UI 模型。
- 该机制只在 `_process_message` 的 `bus` 入口启用；`process_direct`（CLI/Cron）走自己传入的 `on_progress`，可以是 print 也可以是 None。

### 机制 E：`_save_turn` —— 持久化前的"消毒"

**作用**：把 `_run_agent_loop` 产出的新增 messages 写进 session，但同时做三件清理：截断超大 tool result、剥掉 runtime context 前缀、过滤空 assistant 消息和图片 base64。

**设计意图**：写入 session 的内容会成为下次推理的上下文。如果不消毒：(a) 一次 `cat` 大文件的 tool result 会被永久写入并每次重发，迅速耗光 token；(b) `RuntimeContext`（时间戳、当前渠道）每次都不一样，不剥掉的话会破坏 prompt cache；(c) 空 assistant 消息（无内容、无 tool_calls）会让某些 provider 报 400。

**关键源码**（`nanobot/agent/loop.py:458-491`）：
```python
def _save_turn(self, session: Session, messages: list[dict], skip: int) -> None:
    from datetime import datetime
    for m in messages[skip:]:                                  # ① skip = 1 + len(history)，跳过 system + history
        entry = dict(m)
        role, content = entry.get("role"), entry.get("content")
        if role == "assistant" and not content and not entry.get("tool_calls"):
            continue                                           # ② 空 assistant 直接丢
        if role == "tool" and isinstance(content, str) and len(content) > self._TOOL_RESULT_MAX_CHARS:
            entry["content"] = content[:self._TOOL_RESULT_MAX_CHARS] + "\n... (truncated)"  # ③ 16K 截断
        elif role == "user":
            if isinstance(content, str) and content.startswith(ContextBuilder._RUNTIME_CONTEXT_TAG):
                parts = content.split("\n\n", 1)
                if len(parts) > 1 and parts[1].strip():
                    entry["content"] = parts[1]                # ④ 剥 runtime 前缀，留用户原文
                else:
                    continue
            if isinstance(content, list):                       # 多模态：替换 image base64 为占位符
                filtered = []
                for c in content:
                    if c.get("type") == "text" and ... .startswith(ContextBuilder._RUNTIME_CONTEXT_TAG):
                        continue
                    if (c.get("type") == "image_url"
                            and c.get("image_url", {}).get("url", "").startswith("data:image/")):
                        filtered.append({"type": "text", "text": "[image]"})
                    else:
                        filtered.append(c)
                if not filtered:
                    continue
                entry["content"] = filtered
        entry.setdefault("timestamp", datetime.now().isoformat())
        session.messages.append(entry)
    session.updated_at = datetime.now()
```

值得指出：
- ① `skip = 1 + len(history)`：1 是 system message，`history` 是已存在的旧消息——只持久化"本轮新生成"的部分，避免重复写入。
- ③ `_TOOL_RESULT_MAX_CHARS = 16_000`（`loop.py:49`）是字符数而非 token 数，简单粗暴但够用——nanobot 不希望维护一个 token tokenizer 仅为了截断。
- ④ runtime context 剥离是 prompt cache 友好的关键：每次重新 build 时会用最新时间戳重新拼前缀，session 里只保留稳定的用户原文。

---

## 5. 与其他维度的交互

```
                       ┌────────────────────────────────────┐
                       │         编排循环 (AgentLoop)        │
                       └────────────────────────────────────┘
                          ▲          │           │      │
        InboundMessage    │          │           │      │ tool_call
        (consume_inbound) │          │           ▼      ▼
        ─────── [消息总线] │          │      [工具系统]──> 执行结果回灌
                          │          │
        OutboundMessage   │          │ build_messages
        (publish_outbound)│          ▼
                          │     [上下文管理]──── history
                          │     [Prompt 构建]    ▲
                          │                      │ get_history
                          │                      │
                          │                  [状态管理 / Session]
                          │                      ▲
                          │                      │ _save_turn
                          │                      │
                          │     [记忆系统]───────┘
                          │     maybe_consolidate_by_tokens
                          │     archive_messages (后台)
                          │
                          │     [子 Agent 编排]
                          │     SpawnTool 通过 tool 调用进入
                          │     完成后通过 bus 注入回主会话
                          │
                          │     [Provider]
                          │     chat_with_retry / has_tool_calls / finish_reason
                          │
                          └ [Cron / Heartbeat] ──> InboundMessage(channel="system")
                              process_direct() / 走 _process_message 同入口
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|---------------|
| 依赖 ← | 消息总线 | 取 inbound、推 outbound（含 progress 与最终回复） | `consume_inbound` (`loop.py:264`)、`publish_outbound` (`loop.py:317, 433`) |
| 依赖 ← | Provider | `chat_with_retry` 一次 LLM 调用；`has_tool_calls` / `finish_reason` 决定循环走向 | `loop.py:199-203, 205, 236` |
| 输出 → | 工具系统 | 每轮 `get_definitions()` 拉取最新工具列表；`execute(name, args)` 执行 | `loop.py:197, 228` |
| 输出 → | 上下文管理 | `build_messages(history, current_message, media)` 拼请求；`add_assistant_message` / `add_tool_result` 增量拼 | `loop.py:218, 229, 240, 422` |
| 输出 → | 状态管理 | `_save_turn(session, all_msgs, skip)` 持久化；`sessions.save(session)`；`sessions.invalidate(key)` | `loop.py:378, 444-445, 396` |
| 输出 → | 记忆系统 | 进入前 `maybe_consolidate_by_tokens`（同步）；完成后 `_schedule_background(maybe_consolidate)`（异步）；`/new` 触发 `archive_messages` | `loop.py:370, 414, 446, 399` |
| 双向 ↔ | 子 Agent 编排 | 主循环把 `SpawnTool` 注册到 registry（`loop.py:132`），子 Agent 通过 `bus.publish_inbound` 把结果回灌到主 session（subagent.py 的 `_announce_result`） | `loop.py:86-95, 132, 290` |
| 输入 ← | Cron / Heartbeat | 周期任务通过构造 `InboundMessage(channel="system", chat_id="origin_chan:origin_id")` 走同一入口；`process_direct` 提供 CLI 直接通道 | `loop.py:364-382, 493-505` |
| 输出 → | 工具上下文 | `_set_tool_context(channel, chat_id, message_id)` 给 message/spawn/cron 工具注入"我现在在哪里" | `loop.py:158-163, 371, 416` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

- **作者假设单 LLM 后端是瓶颈**：所以全局锁串行化所有会话推理是合理的。如果未来要做"多用户多 provider"的 SaaS 形态，这个 lock 必须改成 per-session/per-provider，否则 P95 延迟会爆炸。
- **作者假设模型能正确使用 OpenAI tool_calls 协议**：循环终止条件 `has_tool_calls` 完全依赖 provider 层的字段映射；如果某个新 provider 把"还要继续"塞在 content 里而不是 tool_calls 里，nanobot 会过早终止。`provider_specific_fields` 的全套穿透（`loop.py:218-222`）也表明作者愿意为 Anthropic 的 thinking blocks 这种偏移做特殊兼容。
- **作者假设 40 轮足够**：默认 `max_iterations=40` 在普通场景够用，但 `_run_agent_loop` 没有任何"提前认输"的机制（比如检测到模型连续 N 轮调同一个工具就主动 break）。这是个朴素的预算控制。
- **作者假设 `/stop` 是稀有事件**：所以 polling `consume_inbound` 用 1s timeout 是可接受延迟。如果是高频中断场景，应该改成基于 `asyncio.Event` 的真信号机制。
- **作者假设错误响应不应进历史**：`finish_reason=="error"` 直接 break 不持久化，背后是相信"绝大部分 LLM error 是 transient + 内容毒性高"。这个假设来自 issue #1303 的真实事故。

### 6.2 这个设计的代价/风险

- **吞吐天花板就是 1**：`_processing_lock` 是单例。即使有 10 个会话各发一条消息，也得排队跑——这在"个人助手"场景没问题，但在"小团队共享一个 nanobot"场景会感到延迟。代码中没有任何配置项能放宽这个锁，意味着扩展时需要改源码。
- **`/stop` 不能中断 LLM 调用本身**：`_handle_stop` cancel 的是 task，但 `provider.chat_with_retry` 内部如果正在 await HTTP，cancel 会抛 `asyncio.CancelledError` 进入。是否真的能立即停下取决于底层 HTTP 库——LiteLLM/httpx 通常能，但 cancel 后 token 已经消耗。这一点在 UX 上是可接受妥协。
- **`/restart` 是 `os.execv`，进程级粗暴**：所有 in-flight 任务都会被强杀，`_background_tasks` 没有 drain 机会（`_handle_restart` 只 `asyncio.sleep(1)` 后直接 execv，参见 `loop.py:303-307`）。`/new` 后的归档如果还没跑完会丢——作者用了 1s 的"祈祷期"作为 best-effort，没有 hard guarantee。
- **`_active_tasks` 用 lambda 自清理**：`task.add_done_callback(lambda t, k=msg.session_key: ...)`（`loop.py:279`），这一行可读性很差且容易写错（lambda 闭包陷阱已经用 `k=msg.session_key` 默认参数手工规避了）。维护时如果需要扩展逻辑会很容易出 bug。
- **runtime context 剥离散落两处**：构建在 `context.py` 加前缀，持久化在 `loop.py:469-488` 剥前缀。这种"约定耦合"如果有人改了前缀格式但只改一处，会导致历史里残留 runtime context，进而破坏 prompt cache。代码里也没有契约性的常量校验，靠 `ContextBuilder._RUNTIME_CONTEXT_TAG` 这一处的引用维系（实质是模块间隐性 ABI）。

### 6.3 如果要重新设计，可能会改变什么

- 把 `_processing_lock` 改成"每会话一个 lock"+"全局信号量限制总并发"，通过配置控制。目前的全局锁本质是"懒得做并发"，对未来扩展不友好。
- 把控制信号 (`/stop`、`/restart`、`/new`) 从字符串前缀识别改成 `InboundMessage` 加一个 `kind: Literal["chat", "control"]` 字段。这样就可以让控制信号绕过普通排队、走更高优先级队列，也避免用户消息正好以 `/stop` 开头时被误判。
- `max_iterations` 单一兜底太粗。可以引入"工具调用模式检测"——比如连续 3 轮调用相同的工具+相似参数就主动 break 并问用户是否需要换思路。这在长任务里能避免烧 token 烧到 40 轮才反应。
- `_save_turn` 的清理逻辑（截断、剥 runtime context、过滤图片 base64）应该作为 `Session` 的写入 hook，而不是 loop 的私有方法——这样 cron/heartbeat 等其他写入路径也能复用，不会有人忘了消毒。
- `_background_tasks` 只在 `close_mcp()` drain，而 `close_mcp` 是个偏内部命名。叫 `await loop.shutdown()` 更符合直觉，且应该在 SIGTERM handler 里被自动调用而不是仰赖 gateway 显式调用。
- progress 回调走 metadata flag (`_progress`/`_tool_hint`) 而不是单独 `OutboundProgress` 类型，让 channel 端必须每次解包 metadata 判断——一个独立的事件类型会让数据流意图更清晰。

### 6.4 对我自己设计 Agent 系统的启示

- **把"消息泵"和"推理状态机"分两层写**：外层 actor / dispatcher 只关心调度、并发、生命周期；内层 ReAct 状态机就是个无副作用的纯循环，吃 messages 吐 messages。这种分层让"加 progress、加 cancel、加 cron 入口、加 CLI 入口"都不用动核心循环——`_run_agent_loop` 至今 ~70 行，绝大多数复杂度都被推到外围。
- **错误响应一律不入历史**：这是个反直觉但极其重要的工程经验。任何 LLM error / 400 / 5xx 都属于"瞬时事件"，不该污染会话状态。`finish_reason=="error"` 的隔离分支只有 4 行，但能挡住整类"会话毒化"事故。
- **延迟敏感的副作用一律后台化，但要 drain**：`/new` 的归档、`_process_message` 末尾的记忆压缩，都用 `_schedule_background` 处理，配合 `close_mcp()` 的 `gather(*tasks)`。不要因为追求速度就让后台任务"裸奔"——给它一个能被 drain 的桶，进程退出时等一下。
- **控制信号可以和数据走同一条管道，但要给消息泵一个心跳**：`/stop` 和聊天消息共享 inbound queue 是对的，但 `wait_for(consume_inbound, timeout=1.0)` 这个 1s 心跳是关键——它让"`_running=False` 后多久退出"有了上限，简单到几乎不像设计，但避免了 graceful shutdown 永远卡死的事故模式。
