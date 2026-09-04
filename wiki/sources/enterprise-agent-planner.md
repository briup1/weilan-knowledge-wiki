---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch25-planner.md
tags: [enterprise-agent-platform, planner, react, plan-and-execute, orchestration]
---

# 第25章 Planner 与编排模式

## 摘要

本章把 Planner 定位为可替换的**决策组件**：读取用户目标、受控上下文、工具视图与历史 Observation，输出结构化 `PlannerDecision`；它只提议下一步，不执行工具、不决定 Run 终态。Runtime 负责 Policy/schema/幂等/超时、Registry 调用、事件、检查点与最终状态。编排模式按任务结构选择：ReAct 适合探索性、多跳和信息不完整任务；Plan-and-Execute 适合路径清楚、需事前审计与计划审批的任务；状态图仅用于确有复用、回放或独立评测价值的复杂节点。

## 核心要点

- **输入受控**：用户任务与租户上下文、Registry 同源 tools schema/版本、Runtime/Memory 保存的工具结果与错误；按状态、租户、角色和 Policy 裁剪工具视图，发布类工具不应在问数阶段可见。
- **输出最小结构化**：`finish/answer` 或 `tool/version/args`。`finish=True` 只是结束提议；Runtime 确认无未完成 Tool Call 后才进入 `succeeded`。
- **提议/执行分离**：副作用只出现在 Runtime 的 `action/result` 事件；工具错误作为 Observation 回到 Planner；更换规则、LLM 或状态图实现不改变外层 Run 契约。
- **ReAct**：每轮「准备上下文→模型生成意图→解析 Decision→Runtime 执行→观察回灌」。适合探索任务，但必须配 `max_steps`、参数规范化摘要、重复调用阈值和预算；空结果不等于业务结论，需携带数据质量与过滤信号。
- **Plan-and-Execute**：Plan 阶段生成结构化计划 artifact，不执行工具；审批后按 `plan_cursor` 执行，前提被推翻时版本化 Replan。适合财务、法务、跨系统高风险任务；计划至少含步骤目标、依赖、工具提示与完成条件。
- **状态图边界**：图内节点折叠到平台六态；模型节点可映射 `planning/executing`，工具产出映射 `action`，人工中断映射 `waiting_human`，反思/重排仍是 `executing` 并进 Trace。普通分支不必强行建图。
- **模式版本化**：`planner.mode`、模型、工具版本、重试/预算/计划 schema 写入 Agent manifest；切换模式视为新版本，不能在同一 `run_id` 中途切换。Run 启动时 pin 工具视图版本到检查点。
- **计划冻结与回放**：高风险计划执行前冻结为审计对象；变更产生新版本并记录原因。计划节点映射 Step，回放可展示决策/证据/状态迁移，但不得重新执行外部副作用。
- **成本共同治理**：生成计划前设最大步骤/工具调用/Planner LLM 调用与重试上限；执行中把剩余预算反馈给 Planner。重试不得悄悄改变用户意图。
- **停止也是正确决策**：权限不足、口径歧义、证据不足、预算耗尽、工具连续失败时，期望动作可能是澄清、拒答、转人工或失败退出，而非继续调用。
- **评测按模式拆分**：ReAct 看步数/循环率/参数修复；Plan-and-Execute 看计划可读性/审批通过率/Replan/执行偏差；状态图看分支覆盖/状态映射/恢复一致性。失败分层到目标理解、拆解、工具选择、参数、Observation 解释、停止、审批和预算。
- **运行台账与回滚**：记录 Planner 模式、模型、工具视图、预算、重试、冻结开关、评测集与 owner；异常时可局部回滚工具裁剪、重试阈值或 Planner 类型，不必回退整个 Agent。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch25-planner.md)
