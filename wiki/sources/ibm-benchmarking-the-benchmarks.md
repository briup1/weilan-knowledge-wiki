---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/11-ibm-benchmarking-the-benchmarks.md
tags: [agent-eval, benchmark-quality, judge-calibration]
---

# IBM Research：不仅评 Agent，也要评 Benchmark 本身

## 摘要

IBM Research 2026-08-06 的论文把评测集从“不会错的真相”改成也要被评估的对象。题目不一致、期望行为写错、策略覆盖有洞，会直接造成错误排名和错误发布决策。

## 核心要点

- 检查方向包括数据集一致性、复杂度、领域策略覆盖，以及 Judge 是否校准。
- 任务描述、期望行为和领域策略可能互相矛盾。矛盾没被发现时，分数没有意义。
- Dataset、Task、Rubric、Ground Truth 和 Evaluator 都要版本化、测试和审核。

## 局限

研究对象是有明确领域政策的任务型对话 Benchmark。没有证明同一套质检能直接覆盖开放式研究、编码或多模态 Computer Use。部分质量指标仍用 LLM Judge，人工验证样本有限。高风险门禁不能只靠这篇的自动指标。

## 关联

- [[evaluation-asset]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/11-ibm-benchmarking-the-benchmarks.md)
