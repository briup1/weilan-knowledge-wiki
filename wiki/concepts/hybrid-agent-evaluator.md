---
type: concept
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
sources: [anthropic-agent-evals, aws-custom-code-evaluators, aws-agentcore-evaluations, nvidia-agent-evaluation, openai-in-house-data-agent-eval, openai-evmbench, atlas-industrial-tool-agents, microsoft-weavebench, enterprise-agent-eval-platform-report, enterprise-agent-dataagent-eval, enterprise-agent-online-eval]
tags: [agent-eval, grader, llm-judge, code-grader]
---

# 混合评估器

混合评估器按问题类型选择评分器：能确定核对的用规则或代码，开放式质量用带 Rubric 的 LLM Judge，高风险、有争议和需要校准的样本用人工。它评的是整次任务的结果、轨迹和副作用，不是模型输出格式。

## 优先级

[[enterprise-agent-eval-platform-report]] 把这组 2026 年资料收成一条顺序：

```text
确定性状态 / Schema / 权限 / 副作用
        → 规则、SQL、单元测试、代码 Grader
语义质量 / 帮助性 / 解释是否充分
        → Rubric + LLM Judge
高风险、争议、Judge 校准
        → 人工专家
```

[[aws-custom-code-evaluators]] 把硬约束写具体了：金融数值、JSON Schema、工具顺序、审批流程、PII 和外部事实不交给 Judge。[[openai-in-house-data-agent-eval]] 用 Golden SQL 和结果比较保护数据 Agent。[[openai-evmbench]] 用隔离链上的状态和交易回放给 Exploit 打分，并主动红队测试评分器，防止 Agent 绕过它。

## 和验证循环不是一件事

[[validation-loop]] 挡在单次工具调用前面，检查参数格式、危险命令和重复失败。混合评估器站在一次任务跑完之后，判断这整次做对了没有、路径是否可接受、环境是否被改坏。格式通过，任务仍可能失败；任务终态看起来成功，路径仍可能是捷径。

## Judge 不能只看最终文本

[[nvidia-agent-evaluation]] 把任务成功、完整轨迹、工具使用、推理效率和业务指标并列。[[aws-agentcore-evaluations]] 用 Session、Trace、Tool 多粒度消费 [[agent-trace]]。[[microsoft-weavebench]] 说明只看终态会高估 Computer Use Agent，因为成功可能来自伪造证据或硬编码结果。

Judge 要校准。[[atlas-industrial-tool-agents]] 用生产流量校准，并报告了与人工判断的一致性，但阈值绑在他们的业务上。[[microsoft-weavebench]] 提醒轨迹 Judge 会把合法的高效路径误判成捷径。

## 代码评分器也要被测试

确定性不等于正确。错误规则、陈旧参考数据和脆弱正则都会稳定地判错。[[aws-custom-code-evaluators]] 要求代码评分器有单元测试、参考用例、版本审查和运行监控。

## 不适用

- 没有 Rubric 和 Ground Truth 时，不要先堆评估器。先建 [[evaluation-asset]]。
- 把 Trace 发给外部 Judge 前，要单独处理数据驻留、权限和隐私。托管评估服务不代替这件事。
- 重复试验仍要做。[[anthropic-agent-evals]] 要求同一任务报告均值、方差、`pass@k`、`pass^k` 和置信区间。一个评估器的一次分数不是稳定性结论。

## 在线流量不改优先级

[[enterprise-agent-dataagent-eval]] 和 [[enterprise-agent-online-eval]] 把同一条优先级用到 DataAgent 和真实流量上：能执行核对的用规则，开放式报告才用模型裁判和人工。在线评测用来发现离线集里没有的问题和分布漂移，不把线上反馈直接当成标准答案。

模型裁判还要有黄金样本、版本、选项顺序随机化、一致性监控和人工抽检。A/B 只回答体验有没有变好、安全成本和稳定性有没有变坏。变好的结论要先回到离线回归，再小流量，再回到线上。不要用一个线上总分代替这条链路。

