---
type: concept
created: 2026-08-08
updated: 2026-08-08
sources: [ai-agent-book-async-agent-experiment, pi-tool-call-lifecycle, pi-agent-runtime-event-flow, hermes-agent-tool-system]
tags: [agent, async-tool, background-job, event-driven, wakeup, task-coordination, cancellation]
---

# Async Tool Execution and Wakeup（异步工具执行与完成唤醒）

## 定义

异步工具执行是把长耗时工具调用拆成**启动、后台执行、完成恢复**三个阶段的运行时模式。启动阶段立即返回任务标识，Agent 不占着执行线程干等；工具完成后，Runtime 用完成事件找回原任务上下文并恢复 Agent。

```text
ToolCall
  → start(args)
  → JobAccepted(job_id, queued)
  → 后台 Worker 执行
  → JobCompletionEvent(job_id, terminal status, result)
  → Runtime inbox
  → 恢复父任务或触发下一 Runtime Turn
```

它解决的不是“怎样写 `async def`”，而是**Agent 暂停等待期间谁保存状态、谁接收结果、谁重新开门**。

## 同步还是异步由谁决定

首选规则是：**工具契约声明能力，Runtime 根据策略作最终决定，Agent 不临场猜。**

```json
{
  "name": "start_report_generation",
  "execution_mode": "async",
  "cancellable": true,
  "progress_events": true
}
```

这只是通用设计示例，不是 Codex 或 MCP 的固定格式。Runtime 还应考虑：

- 预计耗时是否超过当前 Turn 的等待预算。
- 工具是否跨进程、跨容器或跨服务运行。
- 工具能否返回稳定的 `job_id` 并查询状态。
- 操作是否支持取消、重试和幂等。
- 用户是否明确要求阻塞等待。

短操作走同步快路；长操作进入后台任务系统。`auto` 模式可以由 Runtime 根据超时预算选择，但选择结果必须写入 Trace，不能静默变化。

## 两阶段调用协议

### 第一阶段：接受任务

启动调用只表示任务已被接收，不表示业务已经完成：

```json
{
  "job_id": "job-42",
  "status": "queued",
  "accepted_at": "2026-08-08T10:00:00Z",
  "poll_after_seconds": 30
}
```

Runtime 至少保存：

| 字段 | 作用 |
|---|---|
| `job_id` | 关联查询、取消、进度和最终结果 |
| `parent_run_id` / `parent_task_id` | 找回等待它的 Agent 任务 |
| `tool_call_id` | 保持工具调用配对和审计链 |
| `status` | queued、running 或终态 |
| `deadline` | 超时和清理依据 |
| `resume_policy` | 每个结果恢复，还是等待汇合条件 |
| `idempotency_key` | 防止重复启动副作用任务 |

### 第二阶段：完成任务

后台任务进入终态后产生规范化事件：

```json
{
  "event_id": "evt-901",
  "job_id": "job-42",
  "status": "completed",
  "result": {},
  "completed_at": "2026-08-08T10:05:00Z"
}
```

终态通常包括：`completed`、`failed`、`cancelled`、`timed_out`。进度更新不是终态，不应误触发最终汇总。

## 等待固定时间怎么做

不要让 Agent 或主循环执行 `sleep(300)`。那相当于工人抱着电话五分钟，别的活也不干。

正确做法是保存一个持久化定时事件：

```text
JobAccepted
  → 保存 next_check_at
  → Agent 释放执行槽
  → Scheduler 到点投递 TimerEvent
  → 查询状态
       ├─ 未完成：更新 next_check_at
       └─ 已完成：转成 CompletionEvent
```

固定等待适用于：

- 外部系统没有回调能力，只能轮询。
- 退避重试和限流等待。
- 软超时提醒。
- 完成事件可能丢失时的兜底核对。

轮询间隔应由 `poll_after`、指数退避和任务 deadline 控制。完成回调存在时，定时器只做保险，不应成为主通道。

## 工具完成如何唤醒 Agent

常见完成通道有四种：

| 通道 | 适用范围 | 风险 |
|---|---|---|
| 进程内 callback | 同进程协程或线程 | 进程退出后事件丢失 |
| Webhook | 外部 SaaS 或远程服务 | 鉴权、重放和重复投递 |
| Message Broker | 分布式 Worker | 至少一次投递导致重复事件 |
| 状态轮询 | 无推送能力的旧系统 | 延迟和额外请求 |

无论入口是什么，都应先归一化成 CompletionEvent，再进入 Runtime 的统一 `inbox`：

```text
callback / webhook / broker / poller
                 ↓
        CompletionEvent Adapter
                 ↓
           durable inbox
                 ↓
     去重 → 状态迁移 → 恢复策略
```

如果 Agent 正在处理别的 Turn，事件进入队列，不抢写上下文；等执行槽可用后再处理。恢复必须依赖持久化的父任务状态，不能只靠内存中的 Future。

## 两个异步工具相隔一分钟完成

假设两个任务同时启动，第一个五分钟完成，第二个六分钟完成：

```text
T+0m   启动 A、B，pending={A,B}
T+5m   A 完成 → 保存 result[A]，pending={B}
T+6m   B 完成 → 保存 result[B]，pending={}
```

处理方式取决于父任务的汇合策略：

| 策略 | A 完成时 | B 完成时 |
|---|---|---|
| `each` | 立即恢复一次 | 再恢复一次 |
| `all` | 保存结果，不做最终汇总 | 最后一个完成者唤醒父任务 |
| `race` | A 成为赢家并恢复，可取消 B | B 的迟到结果忽略或留档 |
| `quorum` | 达到数量门槛才恢复 | 门槛已满足则只留档 |
| `dependency` | 唤醒依赖 A 的下游节点 | 唤醒依赖 B 的下游节点 |

关键原则：**第一个任务不睡一分钟等第二个；它只把结果放进汇合表。最后一个满足条件的完成事件负责开门。**

一个可靠的汇合记录至少包含：

```text
JoinState
├─ expected_job_ids
├─ terminal_job_ids
├─ results_by_job_id
├─ join_policy
├─ resumed_at
└─ version
```

状态更新要用事务、CAS 或锁保护，防止两个完成事件同时判断自己是“最后一个”并重复恢复父任务。

## 完成事件的可靠性

完成唤醒通常采用至少一次投递，因此消费者必须幂等：

1. 按 `event_id` 去重。
2. 校验 `job_id` 是否属于该父任务。
3. 只允许合法状态迁移，例如 `running → completed`。
4. 原子写入结果和 JoinState。
5. 原子标记是否已经恢复。
6. 成功后再确认消息。

需要单独处理：

- **重复完成**：同一事件重投，不重复触发 Agent。
- **乱序进度**：终态之后到达的旧进度直接丢弃。
- **取消后迟到结果**：按策略忽略、留档或提示“取消未能终止远端工作”。
- **孤儿完成事件**：找不到父任务时进入隔离区或死信队列。
- **进程重启**：从 Job Store 和事件队列恢复，不能依赖内存 callback。

## 取消的三层语义

```text
取消 Agent Turn
  ≠ 取消工具协程
  ≠ 终止底层进程、容器或远程任务
```

`cancellable: true` 必须说明取消能到达哪一层。Runtime 应记录“已请求取消”和“底层确认取消”两个事实；没有远端确认时，后续完成结果仍可能到达。

## 与 Runtime Event Stream 的边界

- 进度事件服务 UI、Trace 和实时观察，可丢弃或聚合。
- Job Record 与终态事件是恢复事实，必须持久化。
- CompletionEvent 可以触发新的 Runtime Turn，但不应直接绕过编排循环修改最终回答。

详见 [[agent-runtime-event-stream]]、[[state-management]] 与 [[session-persistence]]。

## 原始实现位置

AI Agent Book 异步实验提供了进程内最小实现：

- `raw/archive/ai-agent-book-async-agent/tasks.py:54-75`：`TaskManager.start()` 创建后台任务并立即返回 `task_id`。
- `raw/archive/ai-agent-book-async-agent/tasks.py:77-92`：任务自然完成后调用 `on_complete`。
- `raw/archive/ai-agent-book-async-agent/runtime.py:197-214`：`ASYNC_RESULT` 进入 `inbox` 并触发后续处理。
- `raw/archive/ai-agent-book-async-agent/runtime.py:311-318`：工具启动后返回占位结果，不阻塞等待。

该实现证明了“启动—完成事件”主链，但只使用进程内 `asyncio.Task` 和内存队列。生产系统仍需持久化 Job Store、可靠消息、事件去重和重启恢复。

## 关联概念

- [[agent-tool-system]]
- [[tool-call-lifecycle]]
- [[parallel-interruptible-async-agent]]
- [[agent-runtime-event-stream]]
- [[orchestration-loop]]
- [[error-handling]]
- [[session-persistence]]
