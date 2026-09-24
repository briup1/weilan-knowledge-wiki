---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch40-llm-as-judge.md
tags: [enterprise-agent-platform, online-eval, llm-judge]
---

# 第40章 在线评测、模型裁判与持续优化

## 摘要

本章把在线评测放在离线 Benchmark 旁边，用来发现真实流量里的未知问题和分布漂移。线上反馈不能直接当标签。模型裁判可以补开放式语义，但必须被 Rubric、黄金样本、版本、顺序随机化、一致性监控和人工抽检约束住。

## 核心要点

- 线上一条反馈要和 Trace、任务类型、业务上下文、版本信息和权限结果一起解释。
- A/B 回答的是新方案有没有改善真实体验，以及有没有破坏安全、成本和稳定性。它不代替离线回归。
- 不要追一个线上总分。质量链路是：真实失败进入离线回归，裁判判断变成工程修复，小流量灰度再回到线上监控。
- 这条链路依赖第38章的运行证据和第39章的 Benchmark 资产。

## 局限

本章引用 MT-Bench、Chatbot Arena、G-Eval 以及裁判偏差研究作为方法线索，没有复现它们的实验，也没有给出本平台的裁判一致率。工具名同样不是选型结论。

## 关联

- [[hybrid-agent-evaluator]]
- [[evaluation-asset]]
- [[enterprise-agent-observability]]
- [[enterprise-agent-dataagent-eval]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch40-llm-as-judge.md)
