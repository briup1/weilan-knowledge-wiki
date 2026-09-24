---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/01-anthropic-demystifying-agent-evals.md
tags: [agent-eval, methodology, grader]
---

# Anthropic：揭开 AI Agent 评估的神秘面纱

## 摘要

Anthropic 这篇 2026-01-09 的方法论不把评估等同于给最终回答打分。它把任务、重复试验、完整轨迹、环境终态、评分器和运行基础设施拆开，说明非确定性、工具使用和状态修改为什么会让传统测试不够用。

## 核心要点

- 评估对象分开：Task、Trial、Trajectory、Outcome、Grader。一次成功不能代表能力。
- 同一任务应重复运行，报告均值、方差、`pass@k`、`pass^k` 和置信区间。
- 能力集和回归集分开演进；能力稳定后再提议转入回归集。线上投诉、人工测试和生产 Trace 应回流成 BadCase。
- 要做参考解校验和任务可解性检查，避免把评测设计缺陷误判成模型能力问题。

## 局限

这是通用方法论，不是企业产品规范。多租户、权限、审计、成本核算、数据脱敏和高并发调度没有展开。文中阈值来自 Anthropic 及客户实践，不能直接当作本业务门禁。

## 关联

- [[hybrid-agent-evaluator]]
- [[evaluation-asset]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/01-anthropic-demystifying-agent-evals.md)
