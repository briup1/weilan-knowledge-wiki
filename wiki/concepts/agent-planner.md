---
type: concept
created: 2026-09-04
updated: 2026-09-04
sources: [enterprise-agent-planner]
tags: [agent-architecture, planner, orchestration, react, plan-and-execute]
---

# Agent Planner

> Planner 是「只提议、不执行」的可替换决策组件：从受控上下文与工具视图中选择下一步，Runtime 才拥有执行权和终态判定权。

## 稳定接口

```text
用户目标 + 租户上下文 + Registry 同源工具视图 + Observation/Memory
                              │
                              ▼
                           Planner
                              │
             PlannerDecision(FINISH | ASK | TOOL_CALL)
                              │
                              ▼
          Runtime: Policy → schema → Registry → event/checkpoint
```

`finish=True` 只是结束提议；Runtime 确认无未完成 Tool Call 后才进入成功终态。Planner 不 import handler、不调用 Registry `invoke`，否则会绕过版本、权限、错误分类与审计。

## 三种编排选择

| 模式 | 适用 | 必要约束 |
|---|---|---|
| ReAct | 探索性、多跳、信息不完整 | `max_steps`、重复参数检测、错误结构化回灌 |
| Plan-and-Execute | 路径清楚、需计划审批/事前审计 | 结构化计划、版本化 Replan、计划冻结 |
| 状态图 | 多角色、可复用子图、多 HITL 闸口、节点级回放/A-B | 图内状态折叠为平台 Run 六态 |

状态图不是默认升级路径：节点不需要复用、回放或独立评测时，普通分支更简单。模式、模型、工具视图和预算都要版本化；同一 Run 中途不切模式。

## 工具视图与停止决策

Planner 看到的工具应随状态、租户、角色与 Policy 裁剪，并与 Registry schema 同源。问数阶段不暴露邮件/工单等发布工具，审批等待时不继续暴露写操作。权限不足、口径歧义、证据不足、预算耗尽或重复失败时，「澄清/拒答/转人工/失败退出」是正确决策，不应只奖励任务完成。

## 回放与评测

高风险计划先冻结为版本化 artifact，计划节点映射 Runtime Step；变更记录原因。回放保存 Planner 输入摘要、工具候选与版本、决策 JSON、错误码、预算和 Trace 引用，不必永久保存完整 prompt，也不能重新执行副作用。

评测按模式拆分：ReAct 看循环与修复，Plan-and-Execute 看计划与偏差，状态图看分支/映射/恢复；失败按目标理解、拆解、工具选择、参数、Observation、停止、审批、预算分层归因。

## 关联

- [[orchestration-loop]]：承载模型—工具—观察的循环
- [[agent-run-lifecycle]]：执行、状态、恢复与终态的外层契约
- [[agent-tool-system]]：Planner 可见工具契约的事实来源
- [[react-pattern]]：探索性规划的典型模式
- [[agentic-workflow-enhancements]]：Planner 内部可选的局部增强
- 来源：[[enterprise-agent-planner]]
