---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch28-agent.md
tags: [enterprise-agent-platform, multi-agent, handoff, agent-catalog, routing]
---

# 第28章 多 Agent 协作

## 摘要

本章把多 Agent 定义为同一个可审计 Run 内的职责、权限与交付物分工，而非多个模型自由群聊。多 Agent 不是默认架构；只有任务跨专业角色、鉴权域、组织责任、交付物或确有并行收益时，拆分才值得。Router 选择 Agent，Planner 选择当前 Agent 的工具；Handoff 是同一 `run_id` 下的结构化 Tool Call，Runtime 继续统一管理六态、检查点、审批、工具副作用与 Trace。

## 核心要点

- **拆分判据**：单 Agent 能用清晰工具链和状态图完成、权限简单、失败后果低时不拆；角色提示、工具权限、责任团队、产物或并行来源天然不同时才拆。
- **角色收窄**：Workflow/Router（选角色）、Question（澄清口径）、Data（事实与证据）、Report（草稿）、Reviewer/Policy（复核/审批）。每个 Agent 有独立输入输出 schema、工具白名单和 owner。
- **Router ≠ Planner**：Router 选择由哪个 Agent 处理；Planner 决定当前 Agent 调哪个工具。一个全局 Planner 不应同时理解所有角色和所有工具。
- **一个外层 Run**：子角色不得各自启动独立 `/run`。检查点增加 `active_agent_id` 和 `handoff_stack`，Agent 切换不改变平台六态。
- **Handoff 契约**：最小字段 `from_agent_id/to_agent_id/handoff_id/payload/reason/return_policy`；携带目标、已完成/未完成步骤、EvidenceRef、权限上下文、失败历史和期望输出。大结果传 `result_ref`/schema/sample/hash，不复制原始数据。
- **Handoff 是特殊 Tool Call**：可被 Policy 拦截、检查点恢复、Trace 回放；`handoff_id`+幂等键+payload hash 防恢复后重复创建报告/工单。目标不存在、schema 错、租户不匹配、队列超时和环路返回结构化错误。
- **Agent Catalog**：声明 `agent_id`、能力、输入输出 schema、工具白名单、SLA、租户范围、版本和 owner。Router 先做租户/权限/健康过滤，再按规则+分类+Catalog 混合路由；低置信度进入澄清或拒绝，不勉强选 Agent。
- **路由可回放**：记录候选、过滤原因、最终 Agent、置信度、规则版本和 Catalog 版本；过期、重复、无 owner、长期失败的 Agent 退出候选集。
- **冲突不能让模型平均**：事实冲突回权威源/人工，口径冲突重算，Reviewer 以批注退回而非静默覆盖，artifact 单写者+乐观锁，Handoff 环由栈深和 payload hash 检测。
- **共享状态类型化**：事实（带证据，可继续使用）/推断（关键动作前再校验）/草稿（可修改，不能当确认结果）；不同角色仅有对应写权限，原始用户目标不可静默覆盖。
- **权限取交集而非相加**：一个 Agent 能查数、另一个能外发，不代表组合后可查敏感数据再外发；Handoff 重新计算接收方可见信息与动作。上游不可信内容只能作为证据，不能升级为下游系统指令。
- **最小形态与退出**：从 Router+专业执行 Agent 两个角色开始。若长期只路由同一角色、Handoff 失败或成本/延迟不优于单 Agent，应合并回工具链；架构可收缩，历史 Trace 仍可解释。
- **版本组合验收**：每个 Run 保存 Agent version set、Router/Catalog/Handoff schema/策略版本；正常、恢复、拒绝、环路、权限、冲突样本都通过后再扩角色。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch28-agent.md)
