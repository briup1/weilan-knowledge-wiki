---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/06-microsoft-foundry-evaluate-agents.md
tags: [agent-eval, microsoft, rubric]
---

# Microsoft Foundry：评估 AI Agent

## 摘要

Microsoft Foundry 文档给出企业产品里的一条标准操作链：从 Agent 上下文生成 Rubric，上传版本化测试集，跑多个评估器，同时看聚合结果和逐行证据，再接到 GitHub Actions 和生产持续评估。页面日期 2026-09-01 是最后更新时间，不是首次发布日。

## 核心要点

- Rubric 可以从 Agent 上下文生成，但测试集仍然要版本化上传。
- 报告要同时有聚合指标和逐行证据，否则无法复核某一条为什么失败。
- 离线评估和持续评估被放进同一产品流程，而不是两套无关工具。

## 局限

部分能力受区域、权限和预览状态限制。文档主要是 API 流程，没有给出 Judge 与人工一致性、统计显著性和评测集污染治理的完整方法。

## 关联

- [[evaluation-asset]]
- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/06-microsoft-foundry-evaluate-agents.md)
