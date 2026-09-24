---
type: research-source
region: international
publication_date: 2026-02-18
collected: 2026-09-01
source_type: official-blog
organization: Amazon Web Services
original_language: en
original_url: https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/
tags: [agent-eval, enterprise, tool-use, memory, multi-agent, monitoring]
---

# Amazon：构建 Agent 系统的真实评估经验

## 资料信息

- 原文标题：Evaluating AI agents: Real-world lessons from building agentic systems at Amazon
- 发布机构：Amazon / AWS
- 发布日期：2026-02-18
- 原文链接：https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/
- 资料类型：企业实践与评估框架

## 为什么值得阅读

这篇文章来自 Amazon 大规模内部 Agent 建设经验，覆盖购物、客服和多 Agent 等生产场景。它最有价值的地方是把 Agent 失败拆到模型、意图、规划、工具、记忆、异常恢复、最终任务和责任安全等层级，并提出框架中立、持续监控、人工审计的企业评估流程。

## 主要内容中文译介

Amazon 认为传统 LLM 黑盒评估只检查最终输出，无法回答 Agent 为什么失败。生产 Agent 必须同时评估：基础模型、Agent 组件和业务结果。文章提出两部分框架：标准化的自动评估工作流，以及可为不同业务场景扩展指标的评估库。

工作流从离线或在线 Trace 开始，经统一入口进入评估库，生成默认与自定义指标，再将结果写入存储或可视化面板，最后由审计、监控、告警和人工抽检形成处置闭环。指标分三层：

- **底层模型**：比较基础模型的质量和时延，判断其对整体 Agent 的影响。
- **中层组件**：意图识别、多轮对话、记忆检索、推理规划、工具选择、参数与执行顺序。
- **上层结果**：最终回答、目标完成、责任与安全、成本和用户体验。

工具评估包括选择准确率、参数准确率、调用错误率和多轮调用顺序。记忆评估强调检索的相关性、精确率与召回率。推理评估关注规划是否被上下文与工具结果支撑。生产可靠性还需测试认证失败、错误参数、工具返回格式变化、记忆错误等异常，以及 Agent 能否检测、分类并恢复。

Amazon 的购物助手要接入数百至数千个工具，工具 Schema 和描述不一致会导致误选、上下文膨胀、延迟和成本上升。因此其内部先治理工具接口与描述，再用历史调用日志和合成数据建立黄金回归集。客服场景则用 LLM 用户模拟器和匿名历史交互，验证意图识别、路由到正确子 Agent、任务完成和多轮主题遵从。

## 方法与评估设计

- **评测对象**：购物助手、客服 Agent、多 Agent 系统及其模型与组件。
- **数据/环境**：生产 Trace、历史 API 调用日志、匿名客服交互、LLM 合成黄金数据和虚拟用户。
- **评估器**：内置指标、自定义指标、Ground Truth 比较、人工定期审核。
- **指标**：正确性、忠实性、帮助性、目标成功、工具选择/参数/顺序、记忆检索、主题遵从、幻觉、有害性、成本和体验。
- **执行与回放**：离线 Trace 批量评估与在线 Trace 持续评分；面板展示并配置退化告警。
- **关键机制**：跨组织工具 Schema 治理；按最终结果、组件和模型分层定位问题。

## 对企业级平台的启示

1. 评估平台不能依赖某个 Agent 框架，应以标准 Trace 和适配器隔离执行框架差异。
2. 指标目录必须支持“通用指标 + 业务专属指标”，并按模型、组件、结果三级组织。
3. 工具注册中心应保存版本化 Schema、描述、输入输出契约和策略约束，并与评测任务绑定。
4. 异常恢复是独立能力域，应构造错误返回、超时、认证失败、空结果和错误格式等故障注入任务。
5. 线上质量需要与技术可用性同时监控：HTTP 成功不代表工具选择、目标完成或用户体验合格。
6. 人工抽检应进入正式流程，用于审计 LLM Judge、发现未覆盖失败和调整阈值。

## 局限与阅读警告

文章带有 AWS AgentCore 产品背景，公开内容无法完整披露 Amazon 内部数据规模、评估器实现和效果数据。部分推理质量指标依赖可获得的轨迹信息，企业落地时还要考虑敏感推理内容、隐私和不同模型的可观测性限制。
