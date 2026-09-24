---
type: research-source
region: international
publication_date: 2026-08-26
collected: 2026-09-01
source_type: official-blog
organization: Amazon Web Services
original_language: en
original_url: https://aws.amazon.com/blogs/machine-learning/evaluate-any-agent-framework-with-amazon-bedrock-agentcore-evaluations/
tags: [agent-eval, opentelemetry, openinference, interoperability, tracing]
---

# AWS：评估任意 Agent 框架

## 资料信息

- 原文标题：Evaluate any agent framework with Amazon Bedrock AgentCore Evaluations
- 发布机构：Amazon Web Services
- 发布日期：2026-08-26
- 原文链接：https://aws.amazon.com/blogs/machine-learning/evaluate-any-agent-framework-with-amazon-bedrock-agentcore-evaluations/
- 资料类型：官方互操作与 Trace 架构说明

## 为什么值得阅读

企业通常同时存在 LangGraph、LlamaIndex、OpenAI Agents SDK、Google ADK、Claude Agent SDK 和内部框架。此文给出的关键答案是：评估平台不应为每个框架重建一套采集协议，而应以 OpenTelemetry/OpenInference 语义约定作为中立数据平面。

## 主要内容中文译介

AgentCore 通过解耦评估与 Agent SDK 来解决框架碎片化。一次 Agent 执行会产生模型调用、工具调用、检索、重排、Embedding、Guardrail、记忆和编排 Span。评估服务最少需要重建三种角色：

- **invoke agent span**：一次用户输入到最终回复的顶层往返。
- **inference span**：模型看到的消息历史与模型回复。
- **execute tool span**：工具名称、输入参数与结果。

服务既读取 OpenTelemetry GenAI semantic conventions，也读取 OpenInference。两者的 Span 类型与属性名不同，平台通过 instrumentation scope 和标准字段将其归一。Session 由 `session.id` 分组，每个 `trace_id` 对应一个用户回合，再把三类关键 Span 还原为可评分结构。检索、Guardrail、记忆等额外 Span 可以作为上下文存在，不会因未知 Span 类型而失败。

文章列出多框架兼容，并提供通用接入路径：只要 instrumentation scope 使用规范前缀并遵循标准语义，新框架无需专用评估逻辑即可进入同一套 Goal Success、Correctness、Helpfulness 与自定义 Judge。反之，即使字段近似符合标准，随意命名的私有 scope 也可能无法被自动识别。

它还指出两个常见数据完整性问题：Span 必须带能组装 Session 的标识；消息正文可能与 Span 分离保存，如果数据源只包含 span 元数据而没有相关 event record，回答质量评估器会因缺少内容失败。运行结束前也要 flush telemetry，避免容器挂起时缓冲数据尚未导出。

## 方法与评估设计

- **评测对象**：多种 Agent SDK 与自定义框架产生的执行 Trace。
- **数据/环境**：OTel/OTLP Trace、OpenInference 属性、消息事件记录。
- **评估器**：归一后复用同一内置或自定义评估器。
- **指标**：数据可评率、Trace 完整率、工具与模型内容覆盖率、评估结果。
- **执行与回放**：按 Session/Trace 组装；从统一观测后端读历史数据评估。
- **关键机制**：语义规范适配、scope 路由、Span 角色分类、缺失字段诊断。

## 对企业级平台的启示

1. 建设独立的 Trace Ingestion Gateway，以 OTel/OTLP 为主协议，兼容 OpenInference 并提供 SDK 适配器。
2. 内部定义规范化事件模型，但必须保留原始 Span 与属性，便于追溯和适配升级。
3. 接入验收应检查 Session 分组、父子关系、消息内容、工具输入输出、时钟和 flush 完整性。
4. 平台要报告“可评率”，明确多少生产 Trace 因缺字段、脱敏或采集失败无法评分。
5. 标准版本和映射规则要版本化；未知 Span 应可忽略但不能破坏整个 Session。
6. 评估器不直接依赖某个 SDK 的私有对象，否则会重新形成框架锁定。

## 局限与阅读警告

OpenTelemetry/OpenInference 能统一遥测结构，但不能自动统一业务语义、权限、工具副作用和 Ground Truth。不同框架对推理内容、消息事件和工具返回的暴露程度不同，所谓“任意框架”仍以正确埋点和支持的语义字段为前提。
