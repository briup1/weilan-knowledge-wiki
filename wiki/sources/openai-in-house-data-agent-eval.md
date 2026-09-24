---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/10-openai-in-house-data-agent.md
tags: [agent-eval, openai, data-agent]
---

# OpenAI：内部数据 Agent 的建设与持续评估

## 摘要

OpenAI 2026-01-29 写的是内部数据 Agent，不是对外产品。评测在这里的角色是保护持续演进系统的单元测试和生产金丝雀，并与企业语义、数据权限和可验证结果放在同一架构里。

## 核心要点

- 能对上结果的检查优先用可验证结果，例如 Golden SQL 和结果比较，而不是让模型评价模型。
- 数据 Agent 的评估必须带上语义上下文和数据权限，否则“答对了”可能是越权查到的。
- 评测要跟着系统持续演进，上线后仍用金丝雀看新版本是否变坏。

## 局限

没有公开完整评测集、阈值和对照结果。正文写了 Golden SQL 和结果比较，但没有给出跨时间数据快照怎么做。可复现的数据版本要企业自己补。

## 关联

- [[hybrid-agent-evaluator]]
- [[evaluation-asset]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/10-openai-in-house-data-agent.md)
