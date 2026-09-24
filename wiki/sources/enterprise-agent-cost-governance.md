---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch41-cost-governance-cache.md
tags: [enterprise-agent-platform, cost, cache, routing]
---

# 第41章 成本治理与缓存优化

## 摘要

本章要求从任务链路看 Agent 成本，而不是只看单次模型调用。一次运行的钱来自模型、工具、检索、存储、评测和重试。这些成本要贴回 `run_id`、`step_id` 和 `trace_id`，才能判断钱花在哪、质量收益值不值、优化有没有把风险挪走。

## 核心要点

- 单位任务成本比总账单更有用。异常账单先沿任务链路归因。
- 模型路由受任务风险和评测结果约束。强模型用在值得用的步骤上，而不是全局默认。
- 缓存键的第一层是权限边界。缓存要绑租户、角色、版本、数据快照和权限策略。语义缓存采取保守策略，避免跨权限复用答案。
- 预算在任务执行前介入，并和 SLO、限流、降级、人工审批联动。
- 成本优化能不能上线，要同时看质量、安全、延迟和成本。只证明更便宜不够。

## 局限

文中的财务 DataAgent 案例是教学回放，没有附独立测量数据。推理优化和结构化输出在第7章、第8章，那两章不在本次原文集。

## 关联

- [[agent-cost-governance]]
- [[agent-task-slo]]
- [[agent-trace]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch41-cost-governance-cache.md)
