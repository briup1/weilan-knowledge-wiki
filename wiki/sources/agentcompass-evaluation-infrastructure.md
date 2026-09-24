---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/china/01-agentcompass.md
tags: [agent-eval, agentcompass, harness]
---

# AgentCompass：统一 Agent 能力评估基础设施

## 摘要

AgentCompass 是 OpenCompass 等机构 2026-07-15 提交的开源评测基础设施论文。它把 Benchmark、Harness、Environment 拆开，用来解决评测各自绑定运行逻辑、接口不一致、难以复用和横向比较的问题。

## 核心要点

- Benchmark 定义测什么：任务、数据和评分标准。Harness 定义怎么运行和记录。Environment 定义 Agent 能操作什么：工具、状态和外部世界。
- 一个 Benchmark 可以换不同 Harness，同一个 Agent 也可以换环境。论文中的基础设施支持 20 多个 Benchmark，按 Search、Deep Research、Coding、Tool Use、GUI Interaction 五类组织。
- 运行层用异步、流式和容错处理长任务，支持中间状态、重试、异常隔离和并发。分析层可以从总分下钻到轨迹、任务结果和跨 Benchmark 汇总。

## 局限

它是研究评测基础设施，不是开箱即用的企业质量平台。生产在线评估、A/B、告警、审批、多租户和合规治理仍要另建。Benchmark 数量不等于覆盖了企业真实流程。接入后还要核对任务版本、环境镜像和评分一致性。

## 关联

- [[agentcompass]]
- [[evaluation-asset]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/china/01-agentcompass.md)
