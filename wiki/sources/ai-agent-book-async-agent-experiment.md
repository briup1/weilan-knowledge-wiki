---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/ai-agent-book-async-agent/README.md
tags: [agent, async-runtime, event-driven, interruption, cancellation, python, asyncio]
---

# AI Agent Book 实验 4-5：并行和可打断的异步 Agent

## 来源信息

- 来源项目：`/home/weilan/workdir/self_project/ai-agent-book/chapter4/async-agent`
- 实验名称：实验 4-5「带并行执行和打断能力的异步 Agent」
- 核心实现：Python `asyncio`
- 快照日期：2026-08-05
- 核心文件：`events.py`、`runtime.py`、`tasks.py`
- 验证方式：通过 `python3 -m py_compile`，并实际运行 `python3 demo.py parallel` 与 `python3 demo.py interrupt`

## 摘要

该实验把 Agent 的长任务执行改造成事件驱动异步运行时：所有用户消息和工具完成通知先进入 `inbox`，`_dispatcher` 根据紧急度分流到立即处理、排队或打断路径，`_worker` 将事件批次写入轨迹后运行一轮可取消的 LLM turn。耗时工具由 `TaskManager` 以后台 `asyncio.Task` 运行，启动时立即返回 `task_id`，完成时再以 `async.result` 新事件回注 `inbox`。

## 核心主张

1. **事件分类应发生在主 Agent 循环之外。** 明确的停止请求必须由 Runtime 及时识别，不能等待正在工作的主模型自行判断。
2. **Agent turn 与后台工具是两个独立取消对象。** `turn_task.cancel()` 终止当前本地 LLM 协程，`TaskManager.cancel_all()` 取消后台工具协程。
3. **异步工具调用分为启动和完成两个阶段。** 启动阶段返回 `task_id` 占位符；完成阶段通过 `async.result` 事件重新触发 Agent。
4. **事件队列按职责分层。** `inbox` 接收原始事件，`work` 保存待处理批次，`pending` 暂存非紧急补充要求。
5. **取消必须留下轨迹。** 打断事件和系统取消回执都会写入 trajectory，保证后续模型知道发生过什么。

## 实现边界

- `run_terminal_command` 是模拟的异步终端任务，不会启动真实 Shell 进程。
- `asyncio.Task.cancel()` 只能可靠取消 Python 协程；真实子进程、容器或远程任务还需要各自的终止接口。
- `IMMEDIATE` 事件进入同一个单 Worker 的 `work` 队列，因此不会抢占正在执行的 LLM turn；它的含义是“不等待后台工具完成”。
- 取消本地 LLM await 不保证模型供应商服务器上的推理已经停止。
- 实验中的紧急度分类是关键词规则，只区分 `INTERRUPT`、`IMMEDIATE`、`DEFERRED`，没有完整判断请求与当前任务的依赖关系。

## 关联知识

- [[parallel-interruptible-async-agent]]
- [[orchestration-loop]]
- [[agent-runtime-event-stream]]
- [[agent-tool-system]]
- [[state-management]]

## 原始文件

- [实验说明](../../raw/archive/ai-agent-book-async-agent/README.md)
- [框架设计](../../raw/archive/ai-agent-book-async-agent/agent_framework_design.md)
- [事件模型与分类](../../raw/archive/ai-agent-book-async-agent/events.py)
- [Agent Runtime](../../raw/archive/ai-agent-book-async-agent/runtime.py)
- [异步任务管理器](../../raw/archive/ai-agent-book-async-agent/tasks.py)
- [离线演示](../../raw/archive/ai-agent-book-async-agent/async_demos.py)
- [命令行入口](../../raw/archive/ai-agent-book-async-agent/demo.py)
- [文件校验值](../../raw/archive/ai-agent-book-async-agent/SHA256SUMS)
