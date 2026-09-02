---
type: research-source
region: international
publication_date: 2026-03-31
collected: 2026-09-01
source_type: official-blog
organization: Amazon Web Services
original_language: en
original_url: https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations/
tags: [agent-eval, managed-platform, opentelemetry, online-evaluation, cicd]
---

# AWS：用 AgentCore Evaluations 构建可靠 Agent

## 资料信息

- 原文标题：Build reliable AI agents with Amazon Bedrock AgentCore Evaluations
- 发布机构：Amazon Web Services
- 发布日期：2026-03-31
- 原文链接：https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations/
- 资料类型：官方产品架构与实践

## 为什么值得阅读

这篇文章展示了一个较完整的商业 Agent Eval 平台形态：用 OpenTelemetry Trace 作为统一输入，以 Session/Trace/Tool 多粒度评估，提供 LLM Judge、Ground Truth 和代码评估器，并让同一套评分标准贯通开发、CI/CD 和生产在线采样。

## 主要内容中文译介

AgentCore Evaluations 将 Agent 的一次完整对话建模为 Session，每个用户往返是 Trace，Trace 内的模型、检索和工具动作是 Span。服务读取带 GenAI 语义约定的 OpenTelemetry Trace，获得对话历史、可用工具、实际工具、参数、模型输入输出等上下文。

平台提供三种评分方式：

1. **LLM-as-a-Judge**：依据结构化 Rubric 检查完整交互并给出分数和解释。
2. **Ground Truth**：把输出、目标或工具轨迹与预定义/模拟数据比较。
3. **自定义代码评估器**：用 Lambda 实现业务规则和确定性验证。

生命周期分为两种模式。On-demand 用于开发、基准、组件验证、回归与 CI/CD 发布门禁；Online 从生产流量持续采样，复用同一评估器，在 CloudWatch 中展示质量趋势并告警。其重要设计原则是：开发中优化的指标与上线后监控的指标一致，减少“离线指标很好、线上质量不可见”的断层。

内置评估器按 Session、Trace 和 Tool 分层。Session 关注总体目标成功；Trace 关注帮助性、正确性、一致性、简洁性、忠实性、指令遵从、安全、拒答和上下文相关性；Tool 关注工具选择和参数，以及期望工具轨迹的精确顺序、保持顺序或任意顺序匹配。

## 方法与评估设计

- **评测对象**：任何能输出兼容 Trace 的 Agent。
- **数据/环境**：人工整理测试集、历史 Session、Ground Truth、生产采样 Trace。
- **评估器**：13 类预配置评估器、定制 LLM Judge、Lambda 代码评估器。
- **指标**：目标成功、回答质量、安全、上下文、工具选择/参数/轨迹、Token 使用和运行状态。
- **执行与回放**：按 Session/Trace/Span 选择待评对象；On-demand API 与 Online 定时采样。
- **关键机制**：同一 evaluator ID/定义复用于开发和生产；质量分数与运行可观测指标统一展示。

## 对企业级平台的启示

1. 核心 Trace 模型应采用 Session → Trace → Span 层级，并给每一层配置可用的评估器类型。
2. 评估运行要支持 dataset-driven 和 trace-driven 两种输入，覆盖预发布测试与生产历史回放。
3. 同一评估器版本必须可在本地、CI/CD、影子流量和线上采样复用，避免指标漂移。
4. 发布门禁应支持按核心指标设硬阈值、按非核心指标设趋势阈值，并保留逐条解释。
5. 在线评估要有采样率、过滤条件、会话完成判断、成本预算、告警和数据保留策略。
6. 平台界面应同时显示聚合趋势和行级证据，支持从低分下钻到原始 Span 和 Judge 理由。

## 局限与阅读警告

文章描述的是 AWS 托管产品，示例中的配额、评估器数量和区域能力可能随服务更新变化。把 Trace 内容发送给 Judge 还涉及数据驻留、跨区域推理、权限和隐私审查；不能因为平台托管了评估就省略 Judge 校准与业务 Ground Truth。
