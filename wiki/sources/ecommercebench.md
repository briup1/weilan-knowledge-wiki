---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/china/02-ecommerce-bench.md
tags: [agent-eval, long-horizon, benchmark]
---

# E-CommerceBench：365 天自主经营 Agent 评测

## 摘要

E-CommerceBench（Qwen 等，2026-08-31）把评测从一次任务成功拉到 365 个模拟日的电商经营。短期完成率不能代表长期价值：Agent 可能先盈利，再在库存、现金流、欺诈、退货或客户体验上失败。

## 核心要点

- Agent 要连续处理采购、供应商谈判、定价、库存、订单、物流、退货、欺诈、客户关系和财务决策。环境会持续出现需求、供应和异常变化。
- 早期行为的后果会延迟进入评分。过量进货占用现金，过度降价损害利润，忽视退货积累服务风险，过严风控会丢掉正常订单。
- 评分要同时看收益、稳定性、库存健康、现金流、风险和客户体验。论文指出长期 Agent 仍有记忆退化、计划不一致、风险控制不足和短视优化。

## 局限

模拟覆盖不了真实市场、法律约束和人的策略互动。365 个模拟日也可能被 Agent 拟合环境规律。它是长期经营评测范式，不能代替真实业务 A/B 或风控审查。

## 关联

- [[evaluation-asset]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/china/02-ecommerce-bench.md)
