---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch38-trace.md
tags: [enterprise-agent-platform, trace, observability]
---

# 第38章 Agent 可观测性与运行诊断

## 摘要

本章把 Agent 可观测性定义成一次任务的证据链，不是单次 API 日志。Session、Run、Context Package、Trace、Checkpoint 和 Artifact 必须分开，否则会把用户会话、任务执行、模型看到的上下文和业务产物混成一件东西。

## 核心要点

- Session 是连续会话，可以包含多轮 Turn 和多次 Run。Run 是一次具体任务。Trace 描述这次 Run 里每一步。Checkpoint 用于中断恢复。Artifact 是图表、SQL、报告等产物的引用。
- 一次可诊断的 Run 至少记下身份、上下文、步骤、模型调用、工具调用、状态迁移、产物和成本。要能回答任务从哪来、模型看到了什么、选了什么工具、参数是什么、下游返回了什么、产物从哪来。
- 失败要归因到上下文、规划、工具、数据、权限、下游或成本中的一环，而不是只留一条报错。
- 线上失败要能转成可评测、可修复、可回归的样本。Trace 字段变更要保持兼容，采样和保留要单独处理隐私。

## 局限

本章给出的是记录边界和诊断问题清单，没有给出一套已测量的字段规范和保留期限。文中图片未下载。它不替代第30章的业务回放包：技术 Trace 证明系统做了什么，业务回放证明谁批准了什么。

## 关联

- [[agent-trace]]
- [[evaluation-asset]]
- [[enterprise-agent-hitl]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part07-observability-eval/ch/ch38-trace.md)
