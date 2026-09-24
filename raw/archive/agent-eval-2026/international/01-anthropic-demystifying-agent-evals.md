---
type: research-source
region: international
publication_date: 2026-01-09
collected: 2026-09-01
source_type: official-blog
organization: Anthropic
original_language: en
original_url: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
tags: [agent-eval, methodology, grader, trajectory, reliability]
---

# Anthropic：揭开 AI Agent 评估的神秘面纱

## 资料信息

- 原文标题：Demystifying evals for AI agents
- 发布机构：Anthropic Engineering
- 发布日期：2026-01-09
- 原文链接：https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- 资料类型：官方工程方法论

## 为什么值得阅读

这是 2026 年 Agent Eval 最适合作为统一术语和方法论入口的文章。它不把评估等同于“给最终回答打分”，而是将任务、重复试验、完整轨迹、环境终态、评分器和运行基础设施拆成独立对象，并解释了为什么 Agent 的非确定性、工具使用和状态修改会改变传统测试方法。

## 主要内容中文译介

Anthropic 将一次 Agent 评估描述为：给 Agent 一个任务与可交互环境，由 Agent 多轮调用模型和工具，记录完整 transcript/trace/trajectory，最后由一个或多个 grader 对执行过程或环境 outcome 评分。关键术语包括：

- **Task**：有明确输入与成功标准的单个测试用例。
- **Trial**：对同一个 Task 的一次尝试；由于模型输出不稳定，需要重复多次。
- **Grader**：对某个质量维度执行评分的逻辑，可包含多个 assertion/check。
- **Trajectory**：模型输出、工具调用、推理、观察和中间结果构成的完整执行记录。
- **Outcome**：执行结束后环境中的真实状态，而不是 Agent 自称完成的文本。
- **Evaluation harness**：并发运行任务、记录步骤、调用评分器并汇总结果的基础设施。
- **Agent harness/scaffold**：把模型、提示词、工具和循环编排成 Agent 的系统；评估对象实际上是模型与 harness 的组合。

文章主张混合使用三类评分器：代码/规则评分器负责快速、便宜、可复现的确定性检查；模型评分器负责开放式质量和 Rubric 判断；人工专家负责金标准、抽检和校准。能力评估用于探索 Agent 能做到什么，初始通过率可以较低；回归评估用于保护已具备的能力，目标应接近稳定全通过。成熟能力题应逐步转入回归集。

对非确定性，文章区分 `pass@k` 与 `pass^k`：前者衡量多次尝试中至少成功一次的概率，后者衡量多次尝试全部成功的概率。面向用户、要求每次可靠的企业 Agent，更应关注一致性而不是“偶尔能成功”。

## 方法与评估设计

- **评测对象**：编码 Agent、对话 Agent、研究 Agent、Computer Use Agent。
- **数据/环境**：来自真实需求、人工测试、Bug/客服记录的任务；稳定、可复现且任务说明无歧义的环境。
- **评估器**：单元测试、状态检查、静态分析、工具调用检查、Rubric Judge、专家审核。
- **指标**：任务通过率、重复试验稳定性、轮次、工具调用数、Token、成本、首/末 Token 时延。
- **执行与回放**：保存完整轨迹与最终环境状态，支持复现、失败检查和多次 Trial。
- **关键实践**：从 20–50 条真实任务起步；为每个任务提供可通过全部评分器的参考解；模糊任务和错误评分器会制造虚假失败。

## 对企业级平台的启示

1. 数据模型必须原生区分 Task、Trial、Trajectory、Outcome 和 Grader，不能只保存 input/output/score。
2. 评分器需支持“过程评分”和“结果状态验证”，并允许混合加权、全量通过或混合门槛。
3. 每个版本应对同一任务重复运行，报告均值、方差、`pass@k`、`pass^k` 与置信区间。
4. 能力集和回归集应有独立生命周期，能力稳定后自动提议转入回归集。
5. BadCase 应从线上投诉、人工测试和生产 Trace 回流，形成可持续扩张的评测资产。
6. 平台应强制参考解校验和任务可解性检查，避免把评测设计缺陷误判为模型能力问题。

## 局限与阅读警告

文章提供通用方法论而非完整产品规范，对企业多租户、权限、审计、成本核算、数据脱敏和高并发调度的实现细节着墨有限。其部分案例来自 Anthropic 及客户实践，具体阈值仍需按业务风险和用户容忍度校准。
