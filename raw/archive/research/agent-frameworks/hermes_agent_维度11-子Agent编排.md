# 维度名：子 Agent 编排（Sub-Agent Orchestration）

## 1. 一句话定位

Hermes 通过 `delegate_task` 把"目标 + 受限工具集 + 隔离终端会话"打包成一个**临时的、同步阻塞的子 AIAgent 实例**，让父代理在不污染自身上下文的前提下并行/串行地把"会消耗大量中间状态的子任务"外包出去；父代理拿到的只是子代理写回的最终摘要。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果直接把所有子任务放进父代理的同一个对话循环里：

1. **上下文窗口爆炸**：每一次 `tool_call` 的结果都会被 `_run_agent_loop()` 回灌进 `messages`。一个"读 50 个文件 + 跑 grep"的子任务会让上下文一次性增加上万 tokens，触发 `context_compressor` 的强制压缩，丢失父代理真正关心的早期决策。`delegate_tool.py:566` 的注释说得很直接——"intermediate tool calls or reasoning"完全不会进父上下文。
2. **工具污染**：父代理的工具集（`enabled_toolsets`）通常包含 `memory`、`send_message`、`clarify`、`execute_code` 这些**有跨会话副作用的能力**。一旦让子任务直接在父循环里继续，模型有可能以"探索性"为由调用 `memory.add` 写入 `MEMORY.md`、或者用 `send_message` 真的把"试探性结果"发给用户。`DELEGATE_BLOCKED_TOOLS` (`delegate_tool.py:40-48`) 明确列出 5 个必须切断的能力。
3. **并行无从谈起**：单循环天然串行。如果用户希望"同时调研 A 和 B"，父代理只能先做 A 再做 B，子任务之间还要共享 `_current_task_id`、终端 `cwd`、文件操作缓存——并行执行会在 `terminal_tool` 里互相覆盖会话状态。
4. **中断扩散失败**：用户按 Ctrl+C 时，父代理 `interrupt()` 设置 `_interrupt_requested=True`。如果没有"父子代理"的概念，那些已经发出的子任务（嵌套 LLM 调用 + 工具调用）都没办法被打断——它们只是普通的工具调用栈，必须自然结束。`run_agent.py:4651` 的级联 `child.interrupt(message)` 只有在"子代理是独立 AIAgent 实例"的前提下才成立。
5. **审批回调死锁**：父代理的 dangerous-command 审批回调通过 `threading.local()` 持有；ThreadPoolExecutor 的工作线程不会继承。如果子任务直接在父循环里跑（没有 worker thread 切换）这本来不是问题，但只要你想并行，就会撞到这个边界——`delegate_tool.py:60-67` 注释里说 "the worker thread does NOT inherit it ... falls back to input() ... deadlocks against the parent's prompt_toolkit TUI that owns stdin"。

### 2.2 具体触发条件

| 触发点 | 代码位置 | 判断逻辑 |
|--------|---------|---------|
| 模型调用 `delegate_task` 工具 | `run_agent.py:10358` | `_run_agent_loop` 在 dispatch 阶段拿 `function_name == "delegate_task"` 作为分支条件 |
| 单 vs 批量分流 | `delegate_tool.py:1954-1969` | `if tasks and isinstance(tasks, list): ... elif goal and isinstance(goal, str)` —— 二选一 |
| 深度限制硬中断 | `delegate_tool.py:1912-1924` | `depth = getattr(parent_agent, "_delegate_depth", 0); if depth >= max_spawn: return error` |
| 全局暂停 | `delegate_tool.py:1901-1905` | `if is_spawn_paused(): return tool_error(...)` —— TUI 通过 `delegation.pause` RPC 拨动 |
| 角色降级 | `delegate_tool.py:907-908` | `orchestrator_ok = _get_orchestrator_enabled() and child_depth < max_spawn` —— 任一条件不满足，请求的 `orchestrator` 静默退化为 `leaf` |

---

## 3. 核心设计思路

### 3.1 抽象模型

子代理 = "受限子 AIAgent 实例 + 独立 task_id + 独立 worker thread + 同步 future"。父循环对外暴露的是一次工具调用，对内是：

```text
delegate_task(goal | tasks):
    # ── 准入控制 ─────────────────────
    if spawn_paused or depth >= max_spawn:
        return error_string

    # ── 资源准备 ─────────────────────
    creds = resolve_delegation_credentials(cfg, parent)   # provider 切换或继承
    save_global_tool_names(parent_tool_names)             # 保护 model_tools 全局

    # ── 主线程构建所有子代理 ─────────
    children = []
    for task in tasks:
        child = AIAgent(
            ephemeral_system_prompt = build_focused_prompt(goal, context, role, depth),
            enabled_toolsets        = intersect_with_parent(task.toolsets) - blocked,
            session_db              = parent._session_db,
            parent_session_id       = parent.session_id,
            tool_progress_callback  = relay_to_parent_spinner,
            quiet_mode              = True,
            skip_context_files      = True,
            skip_memory             = True,
            iteration_budget        = None,         # 全新预算
        )
        child._delegate_depth = parent.depth + 1
        child._subagent_id    = "sa-{i}-{uuid}"
        parent._active_children.append(child)
        children.append(child)

    # ── ThreadPoolExecutor 并发执行 ──
    with ThreadPoolExecutor(max_workers=max_concurrent_children,
                            initializer=install_subagent_approval_callback) as pool:
        futures = [pool.submit(run_single_child, child) for child in children]
        while pending:
            if parent._interrupt_requested:           # 取消未完成的
                for child in pending: child.interrupt()
                break
            done, pending = wait(pending, timeout=0.5)
            for f in done:
                results.append(f.result())            # 含 summary、cost、tokens、tool_trace

    # ── 父级回滚 ─────────────────────
    restore_global_tool_names(parent_tool_names)
    fold_subagent_costs_into_parent()
    fire_subagent_stop_hooks()                        # 在父线程串行触发

    return json.dumps({"results": [...], "total_duration_seconds": ...})
```

每个子代理本质上是一次"重新跑了一次 `run_conversation()`"，只是带着上面那一坨被裁剪过的配置；父循环把它当作一次不寻常的"大工具调用"。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 子代理与父代理的关系 | **完整独立的 AIAgent 实例**（再走一遍 `run_conversation()`） | 共享 messages 列表、用一个特殊"作用域"标记隔离 | `delegate_tool.py:1086-1116` 显式 `child = AIAgent(...)` 并把 `quiet_mode=True / skip_context_files=True / skip_memory=True / ephemeral_system_prompt=child_prompt` 全部注入。隔离粒度做到了"连系统提示都不一样"——共享 messages 没法做到 |
| 同步 vs 异步 | **同步阻塞**：父循环停在 `delegate_task` 这次工具调用直到所有子结果回来 | 让子代理跑后台，父代理继续推理 | `delegate_tool.py:2418-2441` 工具描述里写明 "WHEN NOT TO USE: Durable long-running work...delegate_task runs SYNCHRONOUSLY inside the parent turn"——选择权放回到 `cronjob`/`terminal(background=True)`。同步语义换来"父子上下文一致性"和"中断点可预测" |
| 并发模型 | **ThreadPoolExecutor + 父代理轮询 0.5s 检查 interrupt** | `as_completed()` 阻塞等待 / `asyncio` 协程 | `delegate_tool.py:2103-2107` 用 `wait(pending, timeout=0.5, return_when=FIRST_COMPLETED)` 而不是 `as_completed()`。注释明说"as_completed() blocks until ALL futures finish — if a child agent gets stuck, the parent blocks forever even after interrupt propagation" |
| 角色分层 | **leaf vs orchestrator 二态**，由 role 字符串 + depth + 全局开关三方约束 | 完全平等的子代理（都能再 delegate）/ 多级分类（worker/manager/director） | `delegate_tool.py:900-908` 三方判定：`role == "orchestrator" and orchestrator_ok and child_depth < max_spawn` 才保留 delegation 工具集；其他全部强制为 `leaf`。**不是把权限拆成 N 个原子能力**，而是只挑"能否再 delegate"这一个最危险的开关——简化心智模型 |
| 工具集继承 | **取交集（child ∩ parent）+ 始终剥离 5 个 blocked 工具 + MCP 工具 opt-in 保留** | 子代理可以请求父代理没有的任意工具集 | `delegate_tool.py:940-956` 显式 intersect，注释 "subagent must not gain tools the parent lacks"。同时 `_strip_blocked_tools` 总是去掉 `delegation/clarify/memory/code_execution`，再由 orchestrator 角色把 `delegation` 加回来 —— **白名单交集 + 黑名单减法**两道防线 |
| 失败语义 | **子超时 → 写诊断日志 + 设 status=timeout 但不抛**；父级把它当成一条普通的 result | 父级把超时直接抛回模型 | `delegate_tool.py:1494-1584` 把 timeout/异常都包成 dict，`results.append(entry)`。配合 `_dump_subagent_timeout_diagnostic()` 写 `~/.hermes/logs/subagent-timeout-...log` 保留现场 —— 让"3 个并发子任务里 1 个挂了"不会让整个工具调用失败 |

### 3.3 数据流/控制流

```
[父代理 _run_agent_loop]
        │  function_name == "delegate_task"
        ▼
run_agent.py:10358  KawaiiSpinner 启动 + 把 spinner 挂到 parent._delegate_spinner
        │
        ▼
run_agent.py:9655  _dispatch_delegate_task(args)
        │
        ▼
delegate_tool.py:1870  delegate_task(goal/tasks/...)
        │
        ├─ 准入检查（spawn_paused / depth）
        ├─ _resolve_delegation_credentials(cfg, parent)  → 决定子代理用谁的凭证
        ├─ 主线程循环：_build_child_agent(...) × N
        │     │
        │     ├─ _build_child_system_prompt    (含 role-aware delegation 段)
        │     ├─ AIAgent(...)                  (子代理实例化, quiet/skip_*)
        │     ├─ child._delegate_depth = parent + 1
        │     ├─ child._subagent_id   = "sa-{i}-{uuid8}"
        │     └─ parent._active_children.append(child)   ← interrupt 级联点
        │
        ▼
ThreadPoolExecutor(max_workers=max_concurrent_children,
                   initializer=_set_subagent_approval_cb)   ← 工人线程预装审批回调
        │
        ├─ submit(_run_single_child, child) × N
        │     │
        │     ├─ _heartbeat_loop (30s 周期 → parent._touch_activity)
        │     ├─ _register_subagent({sid, parent_id, depth, goal, agent})  ← TUI 用
        │     ├─ ThreadPoolExecutor(max_workers=1).submit(_run_with_thread_capture)
        │     │     └─ child.run_conversation(user_message=goal, task_id=child_task_id)
        │     ├─ 超时 → child.interrupt() + 写诊断 + 返回 status=timeout
        │     ├─ file_state.writes_since(parent_task_id, snapshot, paths)
        │     │     └─ 子写过父读过的文件 → 把 "[NOTE: subagent modified files...]" 拼到 summary
        │     └─ 收尾：_unregister_subagent / child.close() / 恢复 model_tools 全局
        │
        ▼
父级 wait() 轮询，每 0.5s 检查 parent._interrupt_requested
        │
        ▼
results = sorted, 折叠子代理花费到 parent.session_estimated_cost_usd
        │
        ▼
serialise → JSON {results: [{summary, status, tool_trace, tokens, ...}]}
        │
        ▼
回到 run_agent.py:10373 → 这条 JSON 作为 tool result 进父 messages
        │
        ▼
父代理拿 summary 进入下一轮推理
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：父子代理双阈值降级（leaf vs orchestrator）

**作用**：在"模型说什么角色"和"运行时实际给什么角色"之间插一层降级，把权限决策从 LLM 手里夺回到 config + depth。

**设计意图**：让 LLM 可以乐观地传 `role="orchestrator"`，但运行时通过**深度计数 × 全局 kill 开关**决定是否真的给——不需要让模型"自己感知是否到了底层"。这种"先信再降级"的模式比"在 prompt 里告诉模型规则"更可靠（模型经常忘）。

**关键源码**（`tools/delegate_tool.py:900-963`）：

```python
# Honor the caller's role only when BOTH the kill switch and the
# child's depth allow it.  This is the single point where role
# degrades to 'leaf' — keeps the rule predictable.
child_depth   = getattr(parent_agent, "_delegate_depth", 0) + 1
max_spawn     = _get_max_spawn_depth()
orchestrator_ok = _get_orchestrator_enabled() and child_depth < max_spawn
effective_role = role if (role == "orchestrator" and orchestrator_ok) else "leaf"
# ...
child_toolsets = _strip_blocked_tools(child_toolsets)   # ① 默认剥离 delegation 等
if effective_role == "orchestrator" and "delegation" not in child_toolsets:
    child_toolsets.append("delegation")                  # ② 仅 orchestrator 加回
```

为什么值得看：白名单交集（与父代理工具集求交）+ 无条件黑名单（`_strip_blocked_tools`）+ 角色按需放行（仅 orchestrator 把 `delegation` 加回） —— **三层叠加**让"减法"和"加法"职责正交。`delegation` 工具集就是这个机制的杠杆，单一开关就能开/关嵌套委托。

### 机制 B：并发执行与中断的协作式取消

**作用**：让父代理在"等所有子代理完成"和"立即响应用户中断"之间不二选一。

**设计意图**：`as_completed()` 是阻塞的——一旦有一个子代理卡死，父代理就再也不能响应用户。换成 `wait(timeout=0.5)` 让父代理每半秒可以醒来一次检查 `_interrupt_requested`，一旦置位就**主动收尾**：已完成的 future 取结果，未完成的造一条 `status="interrupted"` 的伪记录。中断信号本身已经在 `interrupt()` 里通过 `_active_children` 列表级联给所有子代理（`run_agent.py:4651-4657`）。

**关键源码**（`tools/delegate_tool.py:2064-2107`）：

```python
pending = set(futures.keys())
while pending:
    if getattr(parent_agent, "_interrupt_requested", False) is True:
        # Parent interrupted — collect whatever finished and abandon the rest.
        for f in pending:
            idx = futures[f]
            if f.done():
                entry = f.result()
            else:
                entry = {"task_index": idx, "status": "interrupted",
                         "summary": None,
                         "error": "Parent agent interrupted — child did not finish in time",
                         ...}
            results.append(entry); completed_count += 1
        break
    done, pending = _cf_wait(pending, timeout=0.5, return_when=FIRST_COMPLETED)
    for future in done:
        ...   # 正常收集
```

为什么值得看：这是**协作式取消的最简形态** —— 没有 `Thread.kill`（Python 也做不到），靠的是 `_interrupt_requested` 这个 boolean 在每一层都被反复检查（父循环每 0.5s、子代理每个工具间、`interrupt()` 内部级联到 `child._interrupt_requested`），最终汇成一个一致的"准备退出"状态。

### 机制 C：父子文件状态交叉提醒

**作用**：当子代理写了父代理之前读过的文件时，主动在 summary 后面追加 "[NOTE: subagent modified files the parent previously read — re-read before editing: ...]"。

**设计意图**：父代理的 `file_state` 缓存让它"以为自己手里有文件最新内容"，但子代理可能修改了它。如果父代理后续直接 `edit` 那个文件，会撞到 stale-content 检查并失败。Hermes 用了 `file_state.writes_since(exclude_task_id, since_ts, paths)` 这个 API：在 delegate_task 启动时**快照父代理当前已读路径**，结束时反查"这些路径上有谁（不是父）在快照时间之后写过"——有就把警告塞进 summary。

**关键源码**（`tools/delegate_tool.py:1462-1733`，剖面）：

```python
parent_task_id = getattr(parent_agent, "_current_task_id", None)
wall_start = time.time()
parent_reads_snapshot = (
    list(file_state.known_reads(parent_task_id)) if parent_task_id else []
)
# ... child runs ...
sibling_writes = file_state.writes_since(
    parent_task_id, wall_start, parent_reads_snapshot
)
if sibling_writes:
    mod_paths = sorted({p for paths in sibling_writes.values() for p in paths})
    reminder = ("\n\n[NOTE: subagent modified files the parent "
                "previously read — re-read before editing: "
                + ", ".join(mod_paths[:8]) + ...)
    entry["summary"] = entry["summary"] + reminder
```

为什么值得看：这是"全局可观测性 + 子模块自动响应"的实例。`file_state` 模块是工具系统的横切关注点（terminal/file_operations 等都在调用 `record_read/record_write`），delegate 借这层共享视图，**不需要让父子代理直接通信**就能实现"卫生级"的文件一致性提醒。

### 机制 D：批量子代理 worker 池 + 审批回调注入

**作用**：每个子代理工人线程在创建时自动安装一个"自动 deny / 自动 approve"的危险命令审批回调，避免子代理 prompt 父代理 TUI 死锁。

**设计意图**：这是个非常 Python 特定的坑——父代理的 `prompt_toolkit` TUI 持有 stdin。子代理跑 `terminal_tool` 时如果命中 dangerous pattern，会调用 `prompt_dangerous_approval()`，那个函数从 `threading.local()` 拿审批回调；ThreadPoolExecutor 的工人线程是空的 TLS，回退到 `input()`，**而 stdin 已经被父代理的 TUI 占了**——死锁。
解决方案：在 `ThreadPoolExecutor(initializer=...)` 时给每个工人线程**预装**一个非交互式的回调。具体装"自动 deny"还是"自动 approve"由 `delegation.subagent_auto_approve` 决定。

**关键源码**（`tools/delegate_tool.py:1471-1479`）：

```python
_timeout_executor = ThreadPoolExecutor(
    max_workers=1,
    # Install a non-interactive approval callback in the worker thread
    # so dangerous-command prompts from the subagent don't fall back to
    # input() and deadlock the parent's prompt_toolkit TUI.
    # Callback (deny vs approve) is governed by delegation.subagent_auto_approve.
    initializer=_set_subagent_approval_cb,
    initargs=(_get_subagent_approval_callback(),),
)
```

为什么值得看：暴露了一个一般文档不会写的边界——**TUI + 子线程 + TLS 状态**三件事叠在一起的 deadlock。读这段代码能学到：把 worker pool 当作"运行时 capability sandbox"——而不是单纯的"并发原语"。

### 机制 E：模块级活动子代理注册表 + 可中断的细粒度寻址

**作用**：让 TUI / 网关 RPC 能按 `subagent_id` 杀掉单个子代理（而不是杀整棵树）。

**设计意图**：`_active_children` 是父代理实例上的列表，只够做"自上而下的级联中断"。但用户在 TUI 里看到的是树状的 5 个并行子任务，可能想杀掉编号 #3——这需要一个**进程级**的扁平注册表，按 `subagent_id` 寻址。`delegate_tool.py:147-216` 维护了模块级 `_active_subagents` dict，并暴露 `interrupt_subagent(subagent_id)` / `list_active_subagents()` / `set_spawn_paused(bool)` 这套 RPC 表面。

**关键源码**（`tools/delegate_tool.py:183-216`）：

```python
def interrupt_subagent(subagent_id: str) -> bool:
    """Request that a single running subagent stop at its next iteration boundary.

    Does not hard-kill the worker thread (Python can't); sets the child's
    interrupt flag which propagates to in-flight tools and recurses into
    grandchildren via AIAgent.interrupt().  Returns True if a matching
    subagent was found.
    """
    with _active_subagents_lock:
        record = _active_subagents.get(subagent_id)
    if not record:  return False
    agent = record.get("agent")
    if agent is None:  return False
    try:
        agent.interrupt(f"Interrupted via TUI ({subagent_id})")
    except Exception as exc:
        logger.debug("interrupt_subagent(%s) failed: %s", subagent_id, exc)
        return False
    return True
```

为什么值得看：把"父子级联的树状结构"和"按 ID 寻址的扁平视图"通过同一个 `subagent_id` 串起来 —— `_subagent_id` 字段同时挂在 `child._subagent_id`、`_active_subagents` 注册表 key、`tool_progress_callback` 的事件 payload、TUI 树节点上。**一个稳定的字符串 ID 串联了 5 个不同子系统**。

---

## 5. 与其他维度的交互

```
[子 Agent 编排] --(spawn AIAgent 实例)--> [编排循环]   每子代理是新一轮 run_conversation()
[子 Agent 编排] --(filter/intersect)----> [工具系统]   _strip_blocked_tools + 父子 toolset 交集
[子 Agent 编排] --(record_read/writes_since)--> [状态管理]  file_state 跨代理一致性
[子 Agent 编排] --(KawaiiSpinner.print_above)-> [输出渲染]   spinner.print_above 上方树形展示
[子 Agent 编排] --(invoke_hook subagent_stop)--> [插件系统]  父线程串行触发 hook
[子 Agent 编排] <--(_interrupt_requested)----- [编排循环]   父中断级联给所有 _active_children
[子 Agent 编排] <--(_credential_pool)--------- [安全防护]   credential 租借/释放
[子 Agent 编排] <--(parent.tool_progress_callback)-- [输出渲染]  事件向上转发到父 spinner / 网关 SSE
[子 Agent 编排] <--(MAX_DEPTH / kill switch)--- [初始化与环境]  config.yaml delegation.* 节
[子 Agent 编排] <--(memory_manager.on_delegation)-- [记忆系统]  汇报每个 task 给 memory provider
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|---------------|
| 输出到 | 编排循环 | 每个子代理 = 一次完整 `run_conversation()` 调用，复用整套循环逻辑 | `delegate_tool.py:1486-1489` `child.run_conversation(user_message=goal, task_id=child_task_id)` |
| 输出到 | 工具系统 | 子代理收到的 enabled_toolsets = 父∩请求 - 黑名单 + (orchestrator → 加回 delegation) | `delegate_tool.py:940-963` |
| 输出到 | 状态管理 | 子代理写文件 → file_state 记录；delegate 收尾时查父读集合的交集，注入 stale 提醒 | `delegate_tool.py:1463-1733`, `tools/file_state.py:218-249` |
| 输出到 | 输出渲染 | 子代理工具调用通过 `tool_progress_callback` → spinner.print_above 在父 spinner 上方实时打印树状行 | `delegate_tool.py:678-862` `_build_child_progress_callback` |
| 输出到 | 插件系统 | 每个子结束在父线程串行触发 `subagent_stop` hook（避免 hook 作者处理并发）| `delegate_tool.py:2189-2219` |
| 输出到 | 记忆系统 | 把每个 (task, summary) 通知 `parent_agent._memory_manager.on_delegation(...)` | `delegate_tool.py:2158-2180` |
| 依赖 | 编排循环 | 共用 `_interrupt_requested` 标志、`_current_task_id`、`_active_children` 列表 | `run_agent.py:1204-1207, 4651-4657` |
| 依赖 | 安全防护 | 子代理获取/释放 `_credential_pool` 租约，避免多个子代理把同一个 key 顶到限额 | `delegate_tool.py:1326-1334`, `_resolve_child_credential_pool` |
| 依赖 | 初始化与环境 | `_load_config()` 读取 `delegation.*` 节决定并发/深度/超时/角色开关 | `delegate_tool.py:2387-2409` |
| 依赖 | 工具系统 | 在子代理构建期间会写 `model_tools._last_resolved_tool_names` 全局；父代理需要在前后保存/恢复 | `delegate_tool.py:1986-2031`, `1839-1844` |
| 依赖 | 状态管理 | 子代理共享父的 `_session_db` 和 `parent_session_id`，但有自己的 `task_id` | `delegate_tool.py:1108-1109` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **子代理摘要是父代理可消费的接口**：父代理不会再去看子代理的 messages（除了 `_extract_output_tail` 给 TUI 用的最后 8 条 tool result 预览）。整个机制押注 "summary 字段的质量足够支撑后续推理" —— 这就是 `_build_child_system_prompt` 末尾要求的"What you did / What you found / Files modified / Issues" 四件事。
2. **同步阻塞是合理的**：作者明确反对"后台子代理"。Schema 描述里写："delegate_task runs SYNCHRONOUSLY inside the parent turn"。代价是父代理在等子代理时占用 LLM 上下文不动，但换来了"父子状态一致性"。
3. **Python GIL 不是瓶颈**：所有子代理工作主要是 IO（API 调用、shell、HTTP），用 ThreadPoolExecutor 而不是 multiprocessing —— 这是合理的赌博。
4. **凭证池 thread-safe**：通过 `acquire_lease()/release_lease()` 把同一个 provider 的多个子代理串行绑定到不同的 key，但只在父代理已经初始化了 `_credential_pool` 时才工作；否则全部退化为继承父 key（可能撞限额）。
5. **磁盘任务不会真的需要 `execute_code`**：子代理被禁止 `execute_code` 是个相当强的假设——作者认为子代理应该"step-by-step reason with tools"而不是"写脚本批处理"。这一假设在数据处理类任务上会被违反（用户报告过类似抱怨）。

### 6.2 代价/风险

1. **配置膨胀**：`delegation.*` 一个节点已经有 8+ 个配置 key（`max_concurrent_children`、`max_spawn_depth`、`child_timeout_seconds`、`orchestrator_enabled`、`subagent_auto_approve`、`inherit_mcp_toolsets`、`max_iterations`、`reasoning_effort`、`provider/base_url/model/api_key`、`subagent_auto_approve`）。每个都有 env override + 默认值 + 边界 clamp 逻辑（见 `_get_max_spawn_depth` 里的 `_MIN_SPAWN_DEPTH=1, _MAX_SPAWN_DEPTH_CAP=3`），维护成本不低。
2. **诊断耦合**：`_dump_subagent_timeout_diagnostic` 把内部状态（system prompt 字节数、tool schema 字节数、worker 线程栈）dump 到日志文件，与 `child` 的私有属性紧耦合。子代理类一旦改名就会 silently degrade。
3. **`model_tools._last_resolved_tool_names` 是个共享的进程全局**：注释直接承认"any code that reads this global may be temporarily stale during child agent runs"（AGENTS.md:846）。delegate_task 在 try/finally 中保存/恢复，但 _execute_code_ 等其它代码路径如果碰巧在父代理 schedule 了一个子代理之后立即读这个 global，就会拿到子的工具集 —— 修复方式应该是改成 `ContextVar` 而非全局 list。
4. **嵌套 orchestrator → worker 的成本几何级增长**：max_spawn_depth=2 + max_concurrent_children=3 时，最坏情况是 1 → 3 → 9 = 13 个并行 LLM 上下文。`_get_max_concurrent_children` 在 `>10` 时只是 warn，不阻止。
5. **审批回调粒度只有 deny/approve 两态**：没有"重要的审批让父 TUI 处理，琐碎的子代理自动决定"这种分流。`delegation.subagent_auto_approve=true` 是个非常强的开关，要么全部 YOLO 要么全部 deny。
6. **批量并行的最大值由 schema 隐式硬编码？** 实际上不再硬编码（注释里写"No maxItems"），但 `if len(tasks) > max_children: return tool_error(...)` 仍然是同步 reject 而不是排队 —— LLM 经常会传 5 个 task 然后被打回去，是个常见的 UX 噪音。

### 6.3 如果要重新设计可能改变什么

1. **角色系统泛化为能力 token**：现在的二态（leaf/orchestrator）只能调一个开关——"能否再 delegate"。如果改成 `capabilities = {"delegate", "memory", "send_message", ...}` 集合，调用方可以更细粒度地放权。但代价是 prompt 工程更复杂，不一定值得。
2. **把 `_last_resolved_tool_names` 全局换成 `ContextVar`**：`ContextVar` 天然按线程/任务隔离，不需要 try/finally 手动 save/restore，直接消除一类潜在 bug。
3. **summary 之外保留可选的"子代理对话日志引用"**：现在 `_extract_output_tail` 只有 8 条 ×600 字符。重设计可以让父代理"按需展开"某个子代理的完整 messages（保存到 SQLite），通过工具按 sid 查询——把"摘要 vs 详情"做成 lazy load。
4. **超时分级**：现在 `child_timeout_seconds` 是单一值。但"在调用第一个 LLM 前超时"和"调用 30 次工具后超时"含义完全不同。可以拆成 `first_call_timeout`（短，5 分钟） vs `total_timeout`（长，30 分钟）。
5. **批量任务自动排队**：`if len(tasks) > max_children: error` 太粗暴。应当让 delegate 自己拆批次串行执行，结果合并返回。
6. **提供 "dry run" 模式**：当用户带 `--dry-run`，子代理只生成计划不调用工具，方便审视分解质量。

### 6.4 对自己设计 Agent 系统的启示

**最核心的一句**：让"子代理"成为**完整 agent 实例 + 受限工具集 + 同步 future**，而不是"父代理里的一个特殊 prompt 段"。这种"子代理是实例"的实现让所有横切关注点（中断、配额、审批回调、可观测性、文件状态、记忆通知）**自动复用了父代理已有的基础设施**——你只需要在边界上做"裁剪与包装"，不必重写 50% 的循环代码。

附加一句：**用一个稳定的字符串 ID（`subagent_id`）串联起注册表/事件 payload/TUI 节点/中断目标**——这是把"嵌套的运行树"与"扁平的运维视图"对齐的最小代价。
