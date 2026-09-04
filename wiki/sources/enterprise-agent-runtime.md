---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch22-agent-runtime.md
tags: [enterprise-agent-platform, agent-runtime, state-machine, checkpoint, sse]
---

# 第22章 Agent Runtime

## 摘要

本章定义企业 Agent 的**执行契约**：一次用户任务 = 一条可暂停、可恢复、可审计的 Run。Runtime 的职责是把 Runtime、Planner、Registry、Gateway、Console 等组件串成受控执行链，回答「任务当前处于什么状态、下一步由谁负责、失败后如何恢复」。最危险的做法是让每个 Agent 应用自己写执行循环——工具失败的处理、审批位置、日志字段各不相同，审计/SLO/复盘时没有统一事实来源。章节以 Run/Step/Tool Call 三对象为主线，展开 Run 六态状态机、SSE 事件流、检查点与恢复、失败分类/超时/取消，以及与队列、Trace 的分工。

## 核心要点

- **三对象分层**：Run（一次可审计任务：`run_id`/`agent_id`/`state`，服务 SLA/检查点/审批/审计）、Step（Planner 一轮决策：`step_index`/`planner_output`）、Tool Call（一次实际工具执行：`tool_call_id`/`tool`/`args`/`status`/`output`）。一次 Run 含多轮 Step，一轮 Step 产生 0..N 个 Tool Call；Planner 只提意图，执行由 Runtime 经 Registry 完成。
- **`/run` 契约**：`context`（user/tenant/scope）原样传给 Policy 与工具层；`idempotency_key` 防客户端重试重复副作用；`max_steps` 是死循环保护，每轮 Step 消耗模型调用/工具调用/耗时/上下文预算。
- **Run 六态**：`pending → planning → executing ⇄ waiting_human`，终态 `succeeded`/`failed`。关键规则：**终态只能由 Runtime 触发**——模型文本或 Planner 结束意图都不能直接判定；须确认工具队列为空、审批已完成。`waiting_human` 是有意暂停（审批等待单独统计、单独 `approval_timeout_s`）。编排图内部状态（如 LangGraph 节点）是 Planner 内部实现，不得暴露为平台契约。
- **SSE 事件流**：`state`/`action`/`result`/`approval_request` 四类；`action` 与 `result` 必须成对（只有 action 无 result 无法证明副作用是否发生）。断线后带 `Last-Event-ID` 重连、服务端增量补发，不得重新发起一次会产生副作用的 `/run`。聊天 token 流不能证明系统执行了哪个工具。
- **`run_id` vs trace-id**：前者面向业务任务（Console/审批/审计导出），后者面向可观测性（性能/拓扑/告警），在 Observability 层映射，不宜合并。
- **检查点与恢复**：保存 Runtime 状态、请求上下文、工具记录（未完成调用/已完成结果引用/错误码）、Memory 引用、事件位置；三类时机写入——状态迁移成功后、Tool `result` 落盘后、进出 `waiting_human` 时。存储分层：在线低延迟 KV（TTL 对齐 Run 上限）+ 审计归档（追加写）。恢复五步：加载检查点→重放历史与工具结果→`waiting_human` 等回调不自动续→未完成工具按幂等键查状态→按 `Last-Event-ID` 增量补事件。**写操作工具必须与检查点一起设计幂等语义**，否则重试即重复副作用。
- **失败分类**：`MODEL_TIMEOUT`/`TOOL_UNAVAILABLE`/`TOOL_ARGUMENT_INVALID`/`CONTEXT_OVERFLOW`/`LOOP_DETECTED`/`POLICY_DENIED`/`TOOL_NOT_FOUND` 各有默认恢复路径——参数错误反馈 Planner 修正（≤3 次），策略拒绝与死循环不能盲目重试。三档超时分开配置：Run 总超时/Tool Call 超时/LLM 请求超时，合并会造成长任务被模型超时误杀或短工具迟迟不失败。
- **取消语义**：不建第七个状态——取消 = `failed` + `RUN_CANCELLED` + `cancelled_at`；只停止后续动作、尽力取消进行中调用，已产生的副作用靠补偿或人工关闭，取消事件必须进 Trace。
- **Runtime 与队列分工**：Runtime 保存任务语义与状态，队列只接收可执行 Step 引用并带回结果；Worker 不直接推进业务状态。四类队列（交互查询/异步报告/高风险审批/批量评测）配独立并发超时告警。资源隔离四层面：租户用户并发限制、工具级限流、模型级预算、Run 级超时取消。
- **上线门禁三项**：状态一致性（API/SSE/检查点/数据库/前端同一组状态）、副作用控制（写工具必须有幂等键/超时/补偿/Tool Call 记录）、恢复验证（进程重启/队列重放/审批超时/用户取消/部分成功样例）。运行复盘看状态分布：大量 `waiting_human`→审批链路问题；大量 `max_steps`→Planner 循环；大量取消→前端预期管理不足。
- **演进纪律**：`runtime_schema_version` 版本字段、事件模型兼容承诺（稳定/实验/废弃字段），发布纪律接近数据库 schema 演进；修复入口（管理员改状态）须记录操作者/原因/前后状态/影响范围。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch22-agent-runtime.md)
