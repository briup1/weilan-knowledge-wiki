---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/china/04-trajdebug.md
tags: [agent-eval, root-cause, trajectory]
---

# TRAJDEBUG：定位 Agent 失败轨迹中的最早关键错误

## 摘要

TRAJDEBUG（清华 / 腾讯混元等，2026-08-06）解决的是“失败了”之后的下一步：找到最早那个关键错误，并区分它后来被修好了，还是继续往后传。

## 核心要点

- 诊断对象是多粒度轨迹历史，不是最终失败标签。
- 要识别最早关键错误，并分析错误是否传播。
- 自动诊断用来提高排查效率。高风险事故里，它不能代替工程师复核原始证据。

## 局限

论文使用的 486 条轨迹规模有限，错误类型和 Agent 框架覆盖可能不足。多因一果、并发调用或环境故障时，最早关键错误不一定唯一。

## 关联

- [[trajectory-root-cause]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/china/04-trajdebug.md)
