---
type: concept
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
sources: [ibm-benchmarking-the-benchmarks, anthropic-agent-evals, microsoft-foundry-evaluate-agents, ecommercebench, accord-user-agent-collaboration, microsoft-excytin-bench, enterprise-agent-eval-platform-report, enterprise-agent-dataagent-eval, enterprise-agent-online-eval]
tags: [agent-eval, dataset, rubric, ground-truth, badcase]
---

# 评测资产

评测资产是被版本化管理的「测什么、怎样算对、失败怎样回到回归集」。它包括 Dataset / Task、Rubric、Ground Truth、Golden Set 和 BadCase。没有这层，评估器只是在给一次临时运行打分。

## 要解决的问题

Agent 评测会把数据集当成不会错的真相。[[ibm-benchmarking-the-benchmarks]] 说明题目不一致、期望行为写错、策略覆盖有洞，会直接造成错误排名和错误发布。[[anthropic-agent-evals]] 则要求能力集和回归集分开，并在评分前检查任务是否真的可解。

## 资产里有什么

| 对象 | 回答的问题 | 不能代替的东西 |
|---|---|---|
| Task / Dataset | 输入是什么，风险标签是什么 | 评分规则 |
| Rubric | 结果、过程、约束、业务状态怎样算好 | 某一次运行的 Trace |
| Ground Truth / Golden Set | 可核对的参考事实或参考结果 | 模型自己的最终回答 |
| BadCase | 已经发生、经过审核、应长期回归的失败 | 未复核的低分日志 |

[[microsoft-foundry-evaluate-agents]] 的产品流是：生成 Rubric、上传版本化测试集、跑评估器、同时看聚合和逐行证据。[[microsoft-excytin-bench]] 给出另一种 Ground Truth：用调查图的起点、终点和证据链自动生成可解释答案，而不是只留一个最终标签。

## 长程任务不能压成一对输入输出

[[ecommercebench]] 的 365 天经营和 [[accord-user-agent-collaboration]] 的偏好变化都要求资产记住时间。早期进货会在后面变成现金流问题，用户偏好会在对话中途改变。只保存一组 input/output，这两类失败都看不见。[[enterprise-agent-eval-platform-report]] 因此要求数据模型能表达 Session、Journey、状态快照和延迟结果。

## 资产本身也要被检查

上线前至少核对四件事：

1. 任务描述、期望行为和领域策略没有互相矛盾。
2. 任务有参考解，而且确实可解。
3. 能力集和回归集分开版本；稳定能力再转入回归。
4. BadCase 经过发现、审核、批准，才进入回归集。

[[ibm-benchmarking-the-benchmarks]] 的质检对象是有明确政策的任务型对话。开放式研究、编码和多模态 Computer Use 不能直接套用同一套指标。

## 和相邻概念的边界

- 资产定义「怎样算对」。[[hybrid-agent-evaluator]] 选择谁来判。
- [[agent-trace]] 是某次运行的证据，不是资产本身。低分 Trace 要经过审核才变成 BadCase。
- [[trajectory-root-cause]] 解释某条轨迹为什么失败。它的结论可以提议新任务，但不能自动改写 Ground Truth。

## DataAgent 要多记的证据

[[enterprise-agent-dataagent-eval]] 补充的是企业数据任务，不是另一套资产类型。最终答案仍然只是第一层。评分还要看见指标口径、上下文来源、工具调用、权限检查、状态更新和产物引用。

任务不能只收“问一句、答一句”。至少要能放进这些情况：口径冲突、定义改过版、旧记忆失效、用户中途纠正、权限不够、一次交付多个产物。线上反馈不能直接变成标签，要连着 Trace、任务类型、版本和权限结果一起审，审过才进入回归集。见 [[enterprise-agent-online-eval]]。

公开榜单可以当题目怎么设计的参照，不能当本企业能不能上线的证据。

