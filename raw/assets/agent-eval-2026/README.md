# 2026 Agent Eval 最新资料集

> 收集截止日期：2026-09-01。共 20 篇一手资料：国外 15 篇、国内团队/产品 5 篇。
>
> 外文资料保留原文链接，并以中文译介主要内容；本目录不复制或逐字翻译原文全文。

## 阅读目标

这组资料服务于一个明确问题：如何为企业搭建能够贯通研发、发布和生产的 Agent Eval 平台，而不只是做一次 Benchmark 或模型排行榜。

推荐路径：

```text
方法论
  ↓
平台产品
  ↓
Judge / 评测资产治理
  ↓
场景 Benchmark 与长程环境
  ↓
国内基础设施与生产实践
  ↓
企业级平台综合方案
```

## 日期与范围口径

- 论文采用 arXiv **首次提交日期**；若官方页只给月份，则文件中以月初作为机器校验占位，并显式标注 `publication_date_precision: month`。
- 官方文档采用页面显示的**最后更新时间**时，会标注 `publication_date_kind: last-updated`；更新时间不等于首次发布日期。
- “国内”按中国团队主导、国内机构参与或国内云产品官方实践划分，不要求原文必须为中文。
- 所有条目的日期均不晚于本次收集截止日 2026-09-01。

## 国外资料（15）

| # | 日期 | 机构 | 资料 | 类型 | 核心关注 |
|---|---|---|---|---|---|
| 01 | 2026-01-09 | Anthropic | [揭开 AI Agent 评估的神秘面纱](international/01-anthropic-demystifying-agent-evals.md) | 官方方法论 | Task/Trial/Trajectory/Outcome、混合 Grader、稳定性 |
| 02 | 2026-02-18 | Amazon | [构建 Agent 系统的真实评估经验](international/02-amazon-real-world-agent-evaluation.md) | 官方实践 | 真实任务、失败分类、端到端质量闭环 |
| 03 | 2026-03-31 | AWS | [AgentCore Evaluations](international/03-aws-agentcore-evaluations.md) | 产品实践 | 内置与自定义评估器、线上质量监控 |
| 04 | 2026-05-18 | AWS | [自定义代码评估器](international/04-aws-custom-code-evaluators.md) | 产品实践 | 确定性检查、企业规则、代码 Grader |
| 05 | 2026-08-26 | AWS | [评估任意 Agent 框架](international/05-aws-framework-neutral-evaluation.md) | 产品实践 | 框架中立、Trace 接入、同一口径复用 |
| 06 | 2026-09-01* | Microsoft | [Microsoft Foundry 评估 AI Agent](international/06-microsoft-foundry-evaluate-agents.md) | 官方文档 | 离线/持续评估、评估器、可观测性 |
| 07 | 2026-04-22 | Google Cloud | [Gemini Enterprise Agent Platform](international/07-google-gemini-enterprise-agent-platform.md) | 产品发布 | 企业 Agent 生命周期、治理、开放生态 |
| 08 | 2026-07-30 | Google Cloud | [Agent Platform 评估与治理更新](international/08-google-agent-platform-updates.md) | 产品更新 | 仿真、评估、可观测、身份与安全 |
| 09 | 2026-05-19 | NVIDIA | [AI Agent 评估实践](international/09-nvidia-agent-evaluation.md) | 官方方法论 | 任务、轨迹、工具、效率、自定义指标 |
| 10 | 2026-01-29 | OpenAI | [内部数据 Agent 的持续评估](international/10-openai-in-house-data-agent.md) | 官方实践 | Golden SQL、可验证结果、生产金丝雀 |
| 11 | 2026-08-06 | IBM Research | [评估 Benchmark 本身](international/11-ibm-benchmarking-the-benchmarks.md) | 研究论文 | 数据集一致性、复杂度、策略覆盖、Judge 校准 |
| 12 | 2026-06* | Microsoft Research | [WeaveBench](international/12-microsoft-weavebench.md) | Benchmark | 长程 Computer Use、混合接口、轨迹与反作弊 |
| 13 | 2026-05* | Microsoft Research | [ExCyTIn-Bench](international/13-microsoft-excytin-bench.md) | Benchmark | 安全调查、SQL、多跳证据链、可解释 Ground Truth |
| 14 | 2026-02-18 | OpenAI / Paradigm | [EVMbench](international/14-openai-evmbench.md) | Benchmark | 沙箱、副作用、程序评分、确定性重放 |
| 15 | 2026-08-28 | 研究合作团队 | [AcCoRD](international/15-accord-user-agent-collaboration.md) | Benchmark | 用户偏好变化、澄清、记忆与协作 |

`*` Microsoft Foundry 的 2026-09-01 是页面最后更新时间；WeaveBench 与 ExCyTIn-Bench 的官方页仅精确到月份。

## 国内资料（5）

| # | 日期 | 团队/机构 | 资料 | 类型 | 核心关注 |
|---|---|---|---|---|---|
| 01 | 2026-07-15 | OpenCompass 等 | [AgentCompass](china/01-agentcompass.md) | 论文 / 开源基础设施 | Benchmark、Harness、Environment 解耦 |
| 02 | 2026-08-31 | Qwen 等 | [E-CommerceBench](china/02-ecommerce-bench.md) | Benchmark | 365 天经营、多目标 KPI、长期状态 |
| 03 | 2026-08-31 | 中科大 / 美团等 | [ATLAS](china/03-atlas-industrial-tool-agents.md) | 论文 / 生产实践 | 双时间尺度、生产日志、离线回放、A/B |
| 04 | 2026-08-06 | 清华 / 腾讯混元等 | [TRAJDEBUG](china/04-trajdebug.md) | Benchmark | 最早关键错误、错误传播、轨迹根因 |
| 05 | 2026-08-29* | 华为云 | [复杂工具调用智能体评估](china/05-huawei-complex-tool-agent-evaluation.md) | 官方产品实践 | 工具选择、参数、轨迹、在线评估 |

`*` 华为云日期是页面最后更新时间，不代表首次发布日期。

## 企业级综合报告

- [企业级 Agent Eval 平台：技术认知、架构与建设路线](enterprise-agent-eval.md)

## 快速结论

```text
Agent Eval ≠ 最终答案打分

Agent Eval
  = 结果正确性
  + 执行轨迹质量
  + 工具与环境状态
  + 安全与权限边界
  + 成本、时延与稳定性
  + BadCase 根因和持续回归
```

企业平台的核心不是再造一个 Benchmark 网站，而是建设一条可审计的质量证据链：同一套评测定义贯通本地调试、离线对比、CI/CD 门禁、灰度/A-B 和线上持续评估。
