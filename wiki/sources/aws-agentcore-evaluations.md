---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/03-aws-agentcore-evaluations.md
tags: [agent-eval, aws, opentelemetry]
---

# AWS：用 AgentCore Evaluations 构建可靠 Agent

## 摘要

AWS 在 2026-03-31 展示的是托管产品形态：用 OpenTelemetry Trace 做统一输入，按 Session、Trace、Tool 多粒度评分，并把同一套标准用到开发、CI/CD 和生产采样。

## 核心要点

- 评分输入是 Trace，不是最终一段文本。粒度可以落到会话、单次轨迹和单次工具调用。
- 评估器同时包括 LLM Judge、Ground Truth 和代码评估器。
- 开发、发布流水线和生产在线采样复用同一套评分标准。

## 局限

配额、评估器数量和区域能力会随托管服务变化。把 Trace 送给 Judge 还要处理数据驻留、跨区域推理、权限和隐私。平台托管了评估，也不代替 Judge 校准和业务 Ground Truth。

## 关联

- [[agent-trace]]
- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/03-aws-agentcore-evaluations.md)
