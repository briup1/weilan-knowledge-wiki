---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/05-aws-framework-neutral-evaluation.md
tags: [agent-eval, opentelemetry, openinference]
---

# AWS：评估任意 Agent 框架

## 摘要

AWS 2026-08-26 的结论是：企业里会同时存在多种 Agent 框架，评估平台不应为每个框架重做一套采集协议。中立数据平面用 OpenTelemetry / OpenInference 的语义约定。

## 核心要点

- LangGraph、LlamaIndex、OpenAI Agents SDK、Google ADK、Claude Agent SDK 和内部框架可以接到同一套遥测，再复用评估口径。
- 统一的是遥测结构，不是业务语义。权限、工具副作用和 Ground Truth 仍要单独定义。
- “任意框架”的前提是埋点正确，并且框架真的暴露了推理内容、消息事件和工具返回。

## 局限

没有埋点或字段缺失时，框架中立只是口号。不同框架对推理内容的暴露程度不一样。

## 关联

- [[agent-trace]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/05-aws-framework-neutral-evaluation.md)
