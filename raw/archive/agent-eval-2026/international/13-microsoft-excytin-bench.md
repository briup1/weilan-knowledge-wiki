---
type: research-source
region: international
publication_date: 2026-05-01
publication_date_precision: month
collected: 2026-09-01
source_type: research-paper
organization: Microsoft Research
original_language: en
original_url: https://www.microsoft.com/en-us/research/publication/excytin-bench-evaluating-llm-agents-on-cyber-threat-investigation/
repository_url: https://github.com/microsoft/SecRL
tags: [agent-eval, cybersecurity, evidence-chain, sql-agent, explainable-ground-truth]
---

# Microsoft Research：ExCyTIn-Bench 网络威胁调查 Agent 评测

## 资料信息

- 原文标题：ExCyTIn-Bench: Evaluating LLM Agents on Cyber Threat Investigation
- 发布机构：Microsoft Research
- 发布日期：2026-05（ICML 2026；官方页仅精确到月份）
- 原文链接：https://www.microsoft.com/en-us/research/publication/excytin-bench-evaluating-llm-agents-on-cyber-threat-investigation/
- 官方仓库：https://github.com/microsoft/SecRL
- 资料类型：研究论文 / 安全 Benchmark

## 为什么值得阅读

网络安全调查要求 Agent 在大量异构日志中执行 SQL、多跳追踪证据并给出可解释结论。该研究展示了如何用调查图构造自动且可解释的 Ground Truth，特别适合企业高风险场景的证据链、审计和复杂环境评测。

## 主要内容中文译介

ExCyTIn-Bench 面向 Cyber Threat Investigation。研究在受控 Azure Tenant 中构建 SQL 环境，覆盖 Microsoft Sentinel 及相关服务的 57 张日志表，并生成 7,542 个安全调查问题。

作者先使用专家编写的检测逻辑从安全日志中提取调查图，再选择图上的起点和终点生成多跳问题：起点提供背景上下文，终点作为答案，节点与边构成明确证据链。这样既能自动得到可解释 Ground Truth，也便于把同一流程扩展到新的日志类型和调查场景。

实验表明任务仍然困难，最佳模型的 Reward 为 0.606。该结果提醒企业：即使 Agent 能写 SQL 或检索日志，也不代表它能可靠完成完整调查；真正需要评价的是证据发现、跨表关联、多跳推理、答案正确性和调查过程可解释性。

## 方法与评估设计

- **环境**：受控 Azure Tenant 与包含 57 张安全日志表的 SQL 环境。
- **任务规模**：7,542 个由调查图派生的问题。
- **Ground Truth**：专家检测逻辑生成的图节点、边和目标答案。
- **核心能力**：日志检索、SQL 工具使用、多跳证据关联、威胁调查和解释。
- **评估信号**：答案/Reward 与显式调查图证据链。
- **可扩展性**：把新日志映射为调查图后，可沿同一方法生成任务和答案。

## 对企业级平台的启示

1. 高风险领域应优先建设结构化 Ground Truth，例如图、交易链、工单流转或规则执行链。
2. Score 必须关联 Evidence，报告需要展示结论由哪些日志、表、步骤和关系支持。
3. 平台要支持受控数据环境、只读 SQL、安全查询限制和敏感字段脱敏。
4. 可将业务专家规则转化为任务生成器，批量覆盖不同起点、终点和多跳难度。
5. 发布门禁应同时检查答案正确、证据完整、禁止访问、查询成本和可解释性。
6. 安全 Agent 的失败应按检索、关联、推理、工具执行和结论五层归因。

## 局限与阅读警告

Benchmark 在受控 Azure/Sentinel 环境中构建，生成问题与真实分析师的开放式调查仍有差异；Reward 不能完整代表误报成本、漏报风险和处置副作用。官方页面只提供 2026 年 5 月，frontmatter 的月初日期是机器可校验占位，不代表论文在 5 月 1 日发布。
