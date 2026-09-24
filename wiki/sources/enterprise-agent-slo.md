---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch42-slo.md
tags: [enterprise-agent-platform, slo, rate-limit, resilience]
---

# 第42章 SLO 管理、限流与系统韧性

## 摘要

本章把 Agent 的 SLO 定在任务上，而不是单次接口调用。平台要承诺的是：用户能在可接受的时间和成本内完成有质量的任务。这个承诺要拆到首响应、最终完成、任务成功、质量、安全、成本和恢复能力。

## 核心要点

- 先分场景再定指标。不同场景的等待语义不同。目标和护栏分开写。SLI 是测量，SLO 是目标，SLA 是对外承诺。
- 延迟拆到链路阶段，成功率分层算。看板汇总和发布门禁不要混成一个数。
- 错误预算同时约束质量、成本和风险，用来决定还能不能发布。
- 限流管进入量，熔断隔离不健康下游，降级给替代路径。降级不能绕过权限、脱敏、审批和审计。
- 长任务和单次 HTTP 生命周期解开：用状态机、检查点、幂等键和进度查询。容量规划要算步骤放大、重试放大、缓存命中和评测抽样。

## 局限

本章的高峰报表案例是机制说明，没有给出可复现的容量数字。具体 SLO 数值必须按业务场景另定，不能把书里的例子当门禁。

## 关联

- [[agent-task-slo]]
- [[human-in-the-loop]]
- [[agent-cost-governance]]
- [[enterprise-agent-runtime]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch42-slo.md)
