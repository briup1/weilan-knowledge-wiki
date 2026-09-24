---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/13-microsoft-excytin-bench.md
tags: [agent-eval, security, ground-truth]
---

# Microsoft Research：ExCyTIn-Bench 网络威胁调查 Agent 评测

## 摘要

ExCyTIn-Bench 评网络安全调查 Agent：在大量日志里写 SQL、多跳追踪并给出可解释结论。官方页只精确到 2026 年 5 月。它展示了怎样用调查图自动生成可解释的 Ground Truth。

## 核心要点

- 受控 Azure Tenant 里有 57 张 Sentinel 及相关日志表，生成 7,542 个调查问题。
- 专家检测逻辑先抽出调查图，再选起点和终点生成多跳问题。起点是背景，终点是答案，节点和边是证据链。
- 实验里最佳模型 Reward 为 0.606。能写 SQL 不等于能完成调查。要评的是证据发现、跨表关联、多跳推理、答案正确性和过程可解释性。

## 局限

受控环境和真实分析师的开放式调查有差距。Reward 不能代表误报成本、漏报风险和处置副作用。frontmatter 里的月初日期只是机器校验占位。

## 关联

- [[evaluation-asset]]
- [[trajectory-root-cause]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/13-microsoft-excytin-bench.md)
