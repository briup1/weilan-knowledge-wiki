---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch39-dataagent-eval-benchmark.md
tags: [enterprise-agent-platform, dataagent, benchmark]
---

# 第39章 企业级 DataAgent 评测体系与 Benchmark

## 摘要

本章认为 DataAgent 评测不能只看最终答案。答案只是第一层证据。指标口径、上下文来源、工具调用、权限检查、状态更新和产物引用都要进入评分。企业 Benchmark 用来画出能力边界，公开排行榜不能代替自己的数据和权限。

## 核心要点

- 可执行校验和规则校验优先。LLM-as-a-Judge 和人工专家用来处理开放式报告和复杂解释。
- 任务空间要覆盖指标口径、跨源冲突、定义改版、旧记忆失效、用户纠正、权限限制和多产物交付。
- 不强迫所有 Agent 走同一条脚本。要判断路径是否合理、证据是否覆盖、危险动作是否被拦住。
- 持续评测要绑住模型、Prompt、工具、语义层、权限策略、数据快照、Runtime 和 Trace 版本。线上失败转成回归样本，发布放在私有对照上比较。
- Spider、BIRD、BEAVER、HELM、MTEB、SWE-bench 被当作协议和榜单参照。Ragas、TruLens、DeepEval、Promptfoo、Langfuse、Phoenix 被当作可参考工具，本章没有给出选型结论。

## 局限

文中点名的第33章语义层和第34章 NL2SQL 不在本次原文集里，那些工程细节这里没有证据。公开榜单的当前分数未核验。企业阈值需要用自己的数据、权限和用户任务重做。

## 关联

- [[evaluation-asset]]
- [[hybrid-agent-evaluator]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch39-dataagent-eval-benchmark.md)
