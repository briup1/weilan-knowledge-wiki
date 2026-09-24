---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/02-amazon-real-world-agent-evaluation.md
tags: [agent-eval, failure-taxonomy, production]
---

# Amazon：构建 Agent 系统的真实评估经验

## 摘要

Amazon 2026-02-18 的内部实践覆盖购物、客服和多 Agent。它的增量是把失败拆到具体层级，并要求评估流程框架中立、持续监控、保留人工审计。

## 核心要点

- 失败不能只记一个总分。要分到模型、意图、规划、工具、记忆、异常恢复、最终任务和责任安全。
- 评估应能跨框架复用，并持续监控生产表现，而不是只在上线前跑一轮。
- 人工审计仍在流程里，用来核对自动评分覆盖不到的责任和安全问题。

## 局限

文章带有 AWS AgentCore 产品背景。公开内容没有给出内部数据规模、评估器实现和效果数据。依赖轨迹的推理质量指标还会碰到敏感推理内容、隐私，以及不同模型可观测性不一致的问题。

## 关联

- [[trajectory-root-cause]]
- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/02-amazon-real-world-agent-evaluation.md)
