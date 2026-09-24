---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/enterprise-agent-eval.md
tags: [agent-eval, platform, synthesis-source]
---

# 企业级 Agent Eval 平台：技术认知、架构与建设路线

## 摘要

这是截止 2026-09-01、综合同目录 20 篇一手译介写成的判断稿，用来支持企业平台立项、选型和 MVP。它主张 Agent Eval 不是给模型答案打分，而是覆盖结果、轨迹、工具、环境状态、安全、成本、稳定性和根因的全生命周期质量系统。Wiki 里的维护页是 [[agent-eval-platform-landscape]]，本页只保留这份报告自己的主张。

## 核心要点

- 闭环是：真实失败或需求 → 评测集、Rubric、Ground Truth 和版本治理 → 可复现 Harness → 统一 Trace → 规则/代码 + LLM Judge + 人工的混合评分 → 发布门禁和生产在线评估 → BadCase 回流。
- 平台成败看四件事：任务是否像真实业务、执行能否复现、分数是否可信、结果是否进入发布决策。不看评估器数量。
- 六个转向：终态加轨迹；离线榜单加全生命周期；单一 Judge 改成混合评估器；评 Agent 的同时也评评测资产；单轮成功改成长程可靠性；失败统计改成轨迹根因。
- 确定性状态、Schema、权限和副作用优先用规则、SQL、单元测试或代码 Grader。语义质量用 Rubric 加 LLM Judge。高风险、争议和 Judge 校准用人工。
- 数据模型要能表达 Session、Journey、状态快照和延迟结果，不能把所有任务压成一组 input/output。

## 局限

这是资料综合，不是对照实验。具体阈值、云产品配额和论文数字以各篇来源页的局限为准。Arize Phoenix 和 Langfuse 的产品对比不在这 20 篇原文里，不能从本报告推出来。

## 关联

- [[evaluation-asset]]
- [[hybrid-agent-evaluator]]
- [[trajectory-root-cause]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/enterprise-agent-eval.md)
