---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/04-aws-custom-code-evaluators.md
tags: [agent-eval, code-grader, deterministic-check]
---

# AWS：构建自定义代码评估器

## 摘要

AWS 2026-05-18 的实践把“不该交给 LLM Judge 的问题”说清楚了：金融数值、JSON Schema、工具顺序、审批流程、PII 和外部事实用确定性代码评分；语言质量和开放式任务再用模型评分。

## 核心要点

- 硬约束优先用代码评分器，开放式质量才用模型评分器。两者一起才构成生产级评估。
- 代码评分器本身也会错。错误规则、陈旧参考数据和脆弱正则都会误判。
- 代码评分器需要单元测试、参考用例、版本审查和运行监控，不能因为“是代码”就免检。

## 局限

示例实现绑在 Lambda、CloudWatch 和 AgentCore 控制面上。可迁移的是分工，不是那套云资源。

## 关联

- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/04-aws-custom-code-evaluators.md)
