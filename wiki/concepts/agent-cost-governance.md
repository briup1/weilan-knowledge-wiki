---
type: concept
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
sources: [enterprise-agent-cost-governance]
tags: [cost, cache, model-routing, enterprise-agent-platform]
---

# Agent 成本治理

Agent 成本治理是把一次任务花的钱贴回运行链路，并在花钱之前做路由、缓存和预算决定。对象是任务，不是一张模型 API 账单。

## 先归因，再优化

一次 Run 的成本来自模型、工具、检索、存储、评测和重试。这些事件要挂到 `run_id`、`step_id` 和 `trace_id` 上。看单位任务成本，不看总金额。总金额下降，可能只是把重试、人工返工或越权缓存挪到了别处。

## 三个控制点

1. **路由**：强模型用在高风险或评测证明值得的步骤上。任务风险和评测结果约束路由，不设一个全局默认大模型。
2. **缓存**：键的第一层是权限边界，至少包括租户、角色、版本、数据快照和权限策略。语义相近不能跨租户、跨权限复用答案。语义缓存宁可少命中，也不复用可能泄密或过期的结果。
3. **预算**：在步骤执行前决定能不能继续，并和 [[agent-task-slo]] 的限流、降级以及 [[human-in-the-loop]] 的审批连在一起。

## 上线判据

成本方案要同时拿出质量、安全、延迟和成本四项证据。只证明更便宜，不能上线。优化后的行为仍要能在 [[agent-trace]] 里解释钱花在哪一步。
