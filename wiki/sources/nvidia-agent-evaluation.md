---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/09-nvidia-agent-evaluation.md
tags: [agent-eval, metrics, trajectory]
---

# NVIDIA：AI Agent 评估实践

## 摘要

NVIDIA 2026-05-19 的实践指南区分模型评测和 Agent 系统评测。它给出五类落地方向：任务成功、完整轨迹、工具使用、推理效率和业务自定义指标。

## 核心要点

- 只评模型回答，评不到工具是否用对、轨迹是否合理、推理是否浪费。
- 指标体系要同时容纳质量和效率，而不是只留一个正确率。
- 业务自定义指标被当成一等方向，不是通用榜单的附加项。

## 局限

这是工程实践指南，不是严格对照实验。LLM Judge 校准、统计显著性、数据版本治理和多租户权限写得少。页面含 AI 生成摘要，关键结论应以正文为准。

## 关联

- [[hybrid-agent-evaluator]]
- [[agent-trace]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/09-nvidia-agent-evaluation.md)
