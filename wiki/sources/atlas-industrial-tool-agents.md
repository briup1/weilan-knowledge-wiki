---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/china/03-atlas-industrial-tool-agents.md
tags: [agent-eval, tool-use, production]
---

# ATLAS：工业工具 Agent 的双时间尺度诊断评测

## 摘要

ATLAS（中科大 / 美团等，2026-08-31）同时评一次请求内的工具轨迹，和同一用户多次交互的长期体验。Judge 用生产流量校准，优化要用离线回放和在线 A/B 验证。

## 核心要点

- 短视野看单次请求：意图、工具选择、参数、调用顺序、结果利用和最终答复。
- 长视野看跨请求：目标是否延续、偏好是否保持、历史信息是否被用上、体验是否稳定。
- 闭环是从线上日志建任务、离线重放候选版本、按错误类型诊断，再用线上 A/B 看业务影响。
- 论文报告评估器与人工判断有较高一致性。这个一致性绑定在他们的业务、用户和工具生态上。

## 局限

不能直接复制论文阈值。线上 A/B 会受并发实验、季节性和策略变化影响。落地还要有隐私合规、实验护栏和因果分析，避免把相关当成改动的效果。

## 关联

- [[trajectory-root-cause]]
- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/china/03-atlas-industrial-tool-agents.md)
