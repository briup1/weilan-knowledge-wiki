---
type: concept
created: 2026-09-04
updated: 2026-09-04
sources: [enterprise-agent-runtime]
tags: [agent-architecture, runtime, state-machine, checkpoint, enterprise-agent-platform]
---

# Agent Run 生命周期

> 把一次用户任务变成一条可暂停、可恢复、可审计的 Run。回答「任务当前处于什么状态、下一步由谁负责、失败后如何恢复」——这是聊天原型走向生产任务时的核心缺口。

## 定义

Run 生命周期是平台对外暴露的**任务级执行契约**，区别于会话（面向 UI 的聊天窗口）与推理回合（单轮模型调用）。它把「Planner 提议 → 工具执行 → 审批等待 → 恢复 → 终态」串成一条受控执行链：模型文本或 Planner 结束意图都不能直接决定终态，工具副作用不能被重试悄悄重复，审批等待期间任务身份与上下文必须保留。

## 对象模型：Run / Step / Tool Call 分层

三个对象不能混成一个对象：

| 对象 | 代表什么 | 主要字段 |
|---|---|---|
| Run | 一次可审计任务 | `run_id`/`agent_id`/`input`/`context`/`state` |
| Step | Planner 的一轮决策 | `run_id`/`step_index`/`planner_output` |
| Tool Call | 一次实际工具执行 | `tool_call_id`/`tool`/`args`/`status`/`output` |

一次 Run 含多轮 Step，一轮 Step 产生 0..N 个 Tool Call。Planner 只提出调用意图，执行动作由 Runtime 通过 Registry 完成。`/run` 请求的 `context`（用户/租户/数据范围）原样传给 Policy 与工具层。

## Run 六态状态机

```text
pending ──> planning ──> executing ──> succeeded (终态)
                │            │
                │            └──> waiting_human ──> executing (审批通过/驳回→failed)
                └── plan_error └──> failed (终态：不可恢复/拒绝/取消/重试耗尽)
```

关键规则：
- **终态只能由 Runtime 触发**——须确认工具队列为空、审批已完成、失败已处理；
- `waiting_human` 是有意暂停而非卡死，审批等待单独统计、单独超时；
- 编排图内部状态（LangGraph 节点/子图）是 Planner 内部实现，**不得**作为平台契约暴露；内部可复杂，对外生命周期必须稳定。

## 事件、检查点与恢复

- **SSE 事件**：`state`/`action`/`result`/`approval_request`。`action` 与 `result` 必须成对——只有 action 无 result，审计无法证明副作用是否发生。断线重连用 `Last-Event-ID` 增量补发，不得重新发起会产生副作用的请求。
- **检查点**：保存 Runtime 状态、请求上下文、工具记录（未完成调用/已完成结果引用）、Memory 引用与事件位置；写入时机为状态迁移成功后、Tool result 落盘后、进出 `waiting_human` 时。在线低延迟 KV + 审计归档（追加写）两层存储。
- **恢复**：加载最近检查点 → 重放历史与工具结果重建 Planner 上下文 → `waiting_human` 等回调不自动续 → 未完成工具按幂等键查执行状态 → 增量补发事件。
- **幂等是前提**：写操作工具必须与检查点一起设计幂等语义（`idempotency_key` + 保存工具侧业务 ID），否则「恢复即重复副作用」。

## 失败、超时与取消

失败不能一律重试：参数错误反馈 Planner 修正（限次），策略拒绝与死循环不能盲目重试。三档超时分开配置：Run 总超时 / Tool Call 超时 / LLM 请求超时（+ 审批超时）。取消通常不另设状态：`failed` + `RUN_CANCELLED`，停止后续动作、尽力取消进行中调用，已产生副作用靠补偿或人工关闭，取消事件必须进 Trace。

## 边界与分工

- **Runtime ≠ 队列**：Runtime 保存任务语义与状态，队列只接收可执行 Step 引用、执行后回写，Worker 不直接推进业务状态。
- **Run 六态 ≠ 编排图状态**：前者是平台契约（前端/SLA/审计可见），后者是内部实现。
- **run_id ≠ trace-id**：业务任务标识与可观测标识分开，在 Observability 层映射。
- **状态模型演进按接口纪律**：`runtime_schema_version` 版本化，事件模型有兼容承诺，发布纪律接近数据库 schema 演进。

## 关联

- [[agent-turn]]：回合（单轮推理）是更细粒度；Run 是跨多轮/工具/审批的任务实例
- [[agent-runtime-event-stream]]：运行时类型化事件流的通用形态
- [[tool-call-lifecycle]]：Tool Call 从意图到执行的单点全流程
- [[session-persistence]] / [[state-management]]：会话与运行状态的持久化技术
- [[agent-trace]]：run_id 与 trace-id 映射后进入可观测
- 来源：[[enterprise-agent-runtime]]（第22章，含检查点字段表、错误码表、上线门禁清单）
