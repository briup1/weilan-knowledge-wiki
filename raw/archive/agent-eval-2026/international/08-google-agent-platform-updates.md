---
type: research-source
region: international
publication_date: 2026-07-30
collected: 2026-09-01
source_type: official-blog
organization: Google Cloud
original_language: en
original_url: https://cloud.google.com/blog/products/ai-machine-learning/whats-new-in-gemini-enterprise-agent-platform
tags: [agent-eval, online-evaluation, adaptive-rubric, drift, observability]
---

# Google Cloud：Gemini Enterprise Agent Platform 评估与治理更新

## 资料信息

- 原文标题：What’s new in Gemini Enterprise Agent Platform
- 发布机构：Google Cloud
- 发布日期：2026-07-30
- 原文链接：https://cloud.google.com/blog/products/ai-machine-learning/whats-new-in-gemini-enterprise-agent-platform
- 资料类型：官方产品更新

## 为什么值得阅读

该更新明确提出：Observability 回答“Agent 做了什么”，Evaluation 回答“做得好不好”；开发期间优化的指标与上线后的评分由同一引擎执行。它是 2026 年企业 Agent Eval 从离线工具走向生产质量基础设施的代表。

## 主要内容中文译介

文章围绕长时运行、记忆、治理和生产优化更新平台。Agent Runtime 支持持续多日的工作，Memory Bank 用结构化 Schema 保存用户偏好、历史决策和账户上下文。治理方面，Agent Identity 提供最小权限和不可抵赖审计，Agent Gateway 统一连接、IAM 条件、自然语言规则与注入/数据泄漏防护，Agent Registry 则成为企业 Agent、服务器和连接的统一目录。

评估部分强调 Observability 与 Evaluation 共用引擎和数据：

- Agent Evaluation 可通过在线监控器持续评估生产性能，主动识别退化与行为漂移。
- 指标来源包括预置评估器、自定义 Python 代码、LLM-as-a-Judge，以及与 Google DeepMind 共同开发的自适应 Rubric。
- Agent Observability 通过端到端 Trace 和实时仪表盘展示推理、工具使用与执行性能。
- 开发时使用的度量可继续用于生产，避免阶段间指标不一致。

这表明成熟平台需要把“评估定义”视作可部署资产：同一规则先在受控数据集上建立基线，作为发布门禁，随后以可控采样率部署到生产监控。线上发现的漂移和失败再回流为数据集、Rubric 和修复候选。

## 方法与评估设计

- **评测对象**：长时 Agent、带记忆 Agent、企业工具 Agent 和生产 Agent Fleet。
- **数据/环境**：开发评测数据与生产在线流量。
- **评估器**：预置、自定义 Python、LLM Judge、自适应 Rubric。
- **指标**：质量、行为漂移、推理/工具轨迹、运行性能、安全治理信号。
- **执行与回放**：同一评估引擎贯穿开发与生产；实时 Trace 用于诊断。
- **关键机制**：Identity、Gateway、Registry 提供评估所需主体、策略和资产上下文。

## 对企业级平台的启示

1. 评估器应支持独立发布与灰度：草稿 → 校准 → 离线启用 → 门禁启用 → 线上监控。
2. 在线评估需配置采样、预算、过滤、告警和漂移基线，不应无差别调用高成本 Judge。
3. 自适应 Rubric 有潜力降低手工维护，但任何自动调整都必须保留变更审计和历史可比性。
4. 评估结果要关联 Agent Identity、调用者、工具权限与 Gateway 策略版本，支持合规追责。
5. 长时 Agent 需要窗口级、阶段级和最终目标级指标，并能识别记忆污染与跨日状态错误。
6. 统一引擎不等于单一分数；平台仍应保留多维指标和原始证据，避免综合分掩盖硬性风险。

## 局限与阅读警告

官方页面当前显示发布日期为 **2026-07-30**。该文属于产品更新说明，未公开自适应 Rubric 的训练、校准和偏差控制细节，也没有给出线上检测的统计方法与成本数据。实际选型需要进一步验证 API、地区可用性、数据处理边界和价格。
