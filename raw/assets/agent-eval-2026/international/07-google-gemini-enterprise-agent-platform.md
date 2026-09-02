---
type: research-source
region: international
publication_date: 2026-04-22
collected: 2026-09-01
source_type: official-blog
organization: Google Cloud
original_language: en
original_url: https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform
tags: [agent-eval, enterprise-platform, simulation, observability, governance]
---

# Google Cloud：Gemini Enterprise Agent Platform

## 资料信息

- 原文标题：Introducing Gemini Enterprise Agent Platform, powering the next wave of agents
- 发布机构：Google Cloud
- 发布日期：2026-04-22
- 原文链接：https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform
- 资料类型：官方企业平台发布说明

## 为什么值得阅读

它把 Agent Evaluation 放进更大的企业 Agent 控制平面：开发、长时运行、记忆、身份、注册表、网关、仿真、观测、安全与优化共同构成可信 Agent 平台。对自建 Eval 平台而言，这说明评估不能脱离身份、工具治理、执行环境和生产观测单独建设。

## 主要内容中文译介

Google 将平台能力分成 Build、Scale、Govern、Optimize。开发层提供低代码 Agent Studio、代码优先 ADK、模型选择和沙箱；运行层支持长达多日的有状态工作流、持久记忆、多 Agent 编排和事件驱动任务；治理层通过 Agent Identity、Agent Registry 和 Agent Gateway 管理身份、发现、工具连接与策略；优化层由 Agent Simulation、Agent Evaluation、Agent Observability 和 Agent Optimizer 组成。

与评估直接相关的能力包括：

- **Agent Simulation**：在受控环境中，用接近真实用户的合成交互和虚拟工具测试多轮任务，并按任务成功与安全自动评分。
- **Agent Evaluation**：对生产流量持续评分，使用多轮自动评分器判断整段对话逻辑，而非仅看单条回复。
- **Agent Observability**：提供完整执行 Trace 和实时视图，帮助调试推理、工具与性能问题。
- **Agent Optimizer**：聚类真实失败并建议优化系统指令，再进入后续验证。

治理能力与评估形成依赖关系。Agent Identity 使每个动作可归属和审计；Registry 记录组织内 Agent、工具、技能及其批准状态；Gateway 统一执行权限、自然语言策略、Prompt Injection 与数据泄漏防护。没有这些资产标识和策略版本，评估分数无法准确关联“谁、使用了什么、在什么权限下、执行了哪条规则”。

## 方法与评估设计

- **评测对象**：低代码/代码 Agent、多 Agent、长时工作流、Computer Use 与批处理 Agent。
- **数据/环境**：合成用户、虚拟工具、受控沙箱和生产实时流量。
- **评估器**：任务成功、安全评分、多轮 autorater、异常检测中的 LLM Judge。
- **指标**：目标达成、安全、推理与工具行为、运行性能和漂移。
- **执行与回放**：上线前仿真；上线后 Trace 观测、持续评估和失败聚类。
- **关键机制**：Identity、Registry、Gateway 与 Evaluation/Observability 共用控制面。

## 对企业级平台的启示

1. Eval 平台应与 Agent Registry 联动，所有 Run 必须绑定 Agent、工具、模型、提示词、策略和环境版本。
2. 上线前不仅跑静态数据集，还要支持用户模拟器、虚拟工具和多轮场景状态机。
3. 生产评估需要身份与权限上下文，才能识别越权、错误委托和责任归属。
4. Trace、Eval、异常检测和安全事件应使用统一关联 ID，减少跨系统根因分析成本。
5. 失败聚类与优化建议只能作为候选改动，必须重新进入批量评估和 A/B 验证，不能直接自动上线。
6. 平台路线应预留长时任务、多 Agent 和异步事件的评估，而非只围绕聊天 Session。

## 局限与阅读警告

这是产品发布文章，强调能力全景而非公开底层评估算法、数据 Schema 和实验结果。部分功能可能处于分阶段开放或地区限制，不能仅凭产品描述判断可用性和效果；Build vs Buy 决策还需结合官方文档、试用和安全合规审查。
