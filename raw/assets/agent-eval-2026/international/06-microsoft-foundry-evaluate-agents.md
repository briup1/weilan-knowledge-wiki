---
type: research-source
region: international
publication_date: 2026-09-01
publication_date_kind: last-updated
collected: 2026-09-01
source_type: official-doc
organization: Microsoft
original_language: en
original_url: https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent
tags: [agent-eval, rubric, dataset, cicd, continuous-evaluation]
---

# Microsoft Foundry：评估 AI Agent

## 资料信息

- 原文标题：Evaluate your AI agents
- 发布机构：Microsoft Learn / Microsoft Foundry
- 页面日期：2026-09-01
- 日期性质：**官方文档最后更新时间，不代表首次发布日期**
- 原文链接：https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent
- 资料类型：官方产品文档

## 为什么值得阅读

这份文档展示了企业产品中的标准用户流程：从 Agent 上下文生成 Rubric，上传版本化测试集，运行多个评估器，查看聚合与逐行证据，再接入 GitHub Actions 和生产持续评估。它对平台交互、对象模型和报告格式有直接参考价值。

## 主要内容中文译介

Microsoft 建议用 Rubric evaluator 作为 Agent 评估的主度量：Rubric 由若干带权重的维度组成，LLM Judge 对每条响应按策略遵守、工具使用准确性、沟通清晰度等要求评分。Rubric 可以手工编写，也能从 Agent 的名称、指令和工具上下文生成，但生成后仍应人工审阅。

为了覆盖完整风险，需要叠加多类评估器：Agent 专项评估器检查任务、工具和用户意图；质量评估器检查回答质量；文本相似度与参考答案比较；安全评估器识别内容和安全风险；自定义评估器覆盖组织专属标准。

数据集使用版本化 JSONL。无人工数据时可以从合成数据或生产 Trace 启动。Evaluation 对象定义输入 Schema 和评估标准，是多个 Run 的稳定容器；同一 Evaluation 下的 Run 使用相同字段和指标，便于跨版本比较。数据映射可选择纯文本回复或包含工具调用的完整 output items，说明评估输入必须区分“最终文本”和“结构化执行过程”。

报告包含聚合通过/失败/错误数量、不同 Judge 模型的 Token 使用、逐评估器结果；行级结果保留查询、Agent 版本、回复、分数、label、threshold、reason、Rubric 各维度分数和评估调用成本。文档进一步建议将评估接入 CI/CD 门禁和生产持续评估，并通过错误聚类、修改指令/工具、重新评估和 Run 对比迭代。

## 方法与评估设计

- **评测对象**：Foundry Agent 和 Hosted Agent。
- **数据/环境**：人工 JSONL、合成数据、生产 Trace；数据集有名称和版本。
- **评估器**：Rubric、Agent、质量、相似度、安全和自定义评估器。
- **指标**：通过/失败、0–1 总分、1–5 维度分、阈值、理由、Token 使用。
- **执行与回放**：Evaluation 固定 Schema，Run 执行具体 Agent 版本；支持 Trace 评估。
- **关键机制**：从 Agent 上下文生成 Rubric；CI/CD、持续评估和跨 Run 对比。

## 对企业级平台的启示

1. Evaluation Definition 与 Evaluation Run 必须分离，前者冻结数据 Schema 和评估标准，后者绑定 Agent/模型/提示词版本。
2. Rubric 应成为可版本化资产，记录来源、维度、权重、Judge、阈值、审核人和生效范围。
3. 数据映射层要让评估器声明读取 final text、完整 output items、Trace 或业务状态。
4. 报告必须同时支持汇总、单样本、单维度、Judge 理由和 Token/成本下钻。
5. 生产 Trace 转数据集和合成数据生成应是资产流水线的一部分，但都要人工抽查质量。
6. 接入 CI/CD 时应固定 Agent 版本和评估定义，避免“latest”导致结果不可复现。

## 局限与阅读警告

该页面日期是 2026-09-01 的最后更新时间，不能当作功能首次发布日。部分能力受区域、权限和预览状态限制；文档示例主要展示产品 API 流程，没有给出 Judge 与人工专家一致性、统计显著性和评测集污染治理的完整方法。
