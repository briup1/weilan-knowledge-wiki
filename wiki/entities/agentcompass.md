---
type: entity
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
sources: [agentcompass-evaluation-infrastructure]
tags: [agent-eval, open-source, harness, benchmark]
---

# AgentCompass

OpenCompass 等机构的开源 Agent 评测基础设施。它把「测什么」「怎么跑」「能操作什么」拆成三层，让不同 Benchmark 和 Agent 可以交叉复用。

## 基本信息

- **论文**：AgentCompass: A Unified Evaluation Infrastructure for Agent Capabilities
- **arXiv 首次提交**：2026-07-15，https://arxiv.org/abs/2607.13705
- **仓库**：https://github.com/open-compass/AgentCompass
- **形态**：研究评测基础设施，不是企业质量门户

## 三层

| 层 | 管什么 |
|---|---|
| Benchmark | 任务、数据和评分标准 |
| Harness | 模型或 Agent 与环境之间的执行和记录协议 |
| Environment | 工具、状态和外部世界 |

论文中的基础设施支持 20 多个 Benchmark，按 Search、Deep Research、Coding、Tool Use、GUI Interaction 组织。运行层支持异步、流式、中间状态、重试、异常隔离和并发。分析层可以从总分下钻到轨迹和跨 Benchmark 结果。

## 在企业平台里放哪

来源主张它解决的是研究评测接口不统一。它不包含生产在线评估、A/B、告警、审批、多租户和合规治理。[[agent-eval-platform-landscape]] 因此把它放在可复现执行环境的 Harness，而不是整座 Eval 平台。接入后仍要核对任务版本、环境镜像和评分是否一致。详见 [[agentcompass-evaluation-infrastructure]]。
