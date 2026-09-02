---
type: research-source
region: international
publication_date: 2026-05-18
collected: 2026-09-01
source_type: official-blog
organization: Amazon Web Services
original_language: en
original_url: https://aws.amazon.com/blogs/machine-learning/build-custom-code-based-evaluators-in-amazon-bedrock-agentcore/
tags: [agent-eval, deterministic-grader, schema, pii, compliance]
---

# AWS：构建自定义代码评估器

## 资料信息

- 原文标题：Build custom code-based evaluators in Amazon Bedrock AgentCore
- 发布机构：Amazon Web Services
- 发布日期：2026-05-18
- 原文链接：https://aws.amazon.com/blogs/machine-learning/build-custom-code-based-evaluators-in-amazon-bedrock-agentcore/
- 资料类型：官方技术实现指南

## 为什么值得阅读

它清楚回答了企业平台中“哪些问题不应该交给 LLM Judge”。金融数值、JSON Schema、工具顺序、审批流程、PII 和外部事实等硬约束应使用确定性代码评分器；语言质量和开放式任务再交给模型评分器。两者组合才是生产级评估。

## 主要内容中文译介

文章以金融市场情报 Agent 为例，说明语言听起来合理不等于业务正确。股票价格必须落在实时参考值容差内，工具返回必须符合结构，访问敏感资料前必须完成身份识别，回答不得泄露 PII。这些要求若用 LLM Judge 检查，会增加成本且可能不稳定，而代码能在相同输入下产生一致结果。

AgentCore 允许将 Lambda 注册为代码评估器。运行时向 Lambda 传入包含 OpenTelemetry spans 的固定载荷，评估器在 TRACE、TOOL_CALL 或 SESSION 级运行，返回 label、可选 0–1 分数和解释；错误则返回错误码与消息。相同评估器可在按需开发/CI 门禁和线上采样中复用。

示例实现四类评估器：

- **工具响应 Schema 校验**：检测合同变更、解析问题或上游异常造成的结构错误。
- **数值漂移校验**：从回答抽取证券和价格，查询外部权威源并计算容差。
- **工作流契约校验**：从 Session Span 重建工具顺序，确认“识别用户 → 访问资料 → 查询市场数据”等步骤按序完成。
- **PII 泄漏检测**：调用识别服务或正则扫描全部回复，对高风险身份/账户信息执行硬失败，对低风险联系方式按数量部分扣分。

文章建议把代码评估器与帮助性、正确性等模型评估器放在同一次评估中，形成语言质量、结构完整性、事实数值、流程合规和隐私安全的组合证据。

## 方法与评估设计

- **评测对象**：工具型金融 Agent 的 Trace、工具调用和完整 Session。
- **数据/环境**：代表性 Session、历史失败、外部市场数据源、PII 检测服务。
- **评估器**：Lambda 自定义代码 + 内置/自定义 LLM Judge。
- **指标**：PASS/FAIL、0–1 分数、Schema 合规、数值偏差、顺序合规、PII 类型与数量。
- **执行与回放**：同一 evaluator 用于开发、回归、部署门禁和生产采样。
- **关键机制**：评估器固定输入输出契约、独立版本、IAM 权限、日志与指标上报。

## 对企业级平台的启示

1. 建立“确定性优先”路由规则：可由代码、数据库或业务系统验证的问题，不默认使用 LLM Judge。
2. 评估器注册中心需声明执行层级、输入 Schema、输出 Schema、依赖、超时、权限、成本和版本。
3. 外部事实校验器要保存参考源版本/查询时间，避免事后无法重放当时真值。
4. 流程合规评估应基于结构化工具事件，而不是从最终文本推测是否执行过审批。
5. PII、越权、资金、删除等高风险维度应设硬门禁，不能被其他高分加权抵消。
6. 自定义代码应在受限沙箱运行，限制网络、资源和凭证，并记录可审计的执行证据。

## 局限与阅读警告

实现强绑定 Lambda、CloudWatch 与 AgentCore 控制面，但模式可迁移。代码评分器虽确定，却可能因错误规则、陈旧参考数据或脆弱正则产生误判，因此也必须有单元测试、参考用例、版本审查和运行监控。
