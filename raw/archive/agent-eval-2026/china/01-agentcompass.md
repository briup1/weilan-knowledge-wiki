---
type: research-source
region: china
publication_date: 2026-07-15
collected: 2026-09-01
source_type: research-paper
organization: OpenCompass community and Chinese research institutions
original_language: en
original_url: https://arxiv.org/abs/2607.13705
repository_url: https://github.com/open-compass/AgentCompass
tags: [agent-eval, evaluation-infrastructure, harness, benchmark, environment]
---

# AgentCompass：统一 Agent 能力评估基础设施

## 资料信息

- 原文标题：AgentCompass: A Unified Evaluation Infrastructure for Agent Capabilities
- arXiv 首次提交：2026-07-15
- 原文链接：https://arxiv.org/abs/2607.13705
- 官方仓库：https://github.com/open-compass/AgentCompass
- 资料类型：国内团队研究论文 / 开源评测基础设施

## 为什么值得阅读

这是国内 2026 年最接近“通用 Agent Eval 平台底座”的开源工作之一。它明确拆分 Benchmark、Harness 与 Environment，试图解决不同评测各自绑定运行逻辑、接口不一致、难以复用和横向比较的问题。

## 主要内容中文译介

AgentCompass 将 Agent 评测拆为三个相互独立的层次：

- **Benchmark**：任务、数据和评分标准，定义要测什么。
- **Harness**：模型/Agent 与环境之间的执行协议，定义怎么运行和记录。
- **Environment**：工具、状态和外部世界，定义 Agent 可以操作什么。

这种解耦允许一个 Benchmark 复用不同 Agent Harness，也允许同一个 Agent 在不同环境中运行。论文展示的基础设施支持 20 多个 Benchmark，并按 Search、Deep Research、Coding、Tool Use、GUI Interaction 五类能力组织。

运行层采用异步、流式和容错机制处理长程 Agent 任务，支持中间状态保存、重试、异常隔离和并发执行。分析层提供轨迹查看、任务级结果和跨 Benchmark 汇总，使研究者可以从总分下钻到具体工具行为，而不是只比较排行榜。

## 方法与评估设计

- **架构原则**：Benchmark、Harness、Environment 三层解耦。
- **能力覆盖**：搜索、深度研究、编码、工具使用和 GUI 交互。
- **执行引擎**：异步并发、流式执行、容错和长任务管理。
- **适配机制**：用统一接口接入不同 Agent、模型、Benchmark 和环境。
- **分析能力**：聚合指标、任务明细与轨迹级诊断。
- **复现目标**：统一配置与执行入口，降低不同评测脚本造成的结果偏差。

## 对企业级平台的启示

1. 平台核心接口也应解耦 Dataset/Benchmark、Agent Adapter/Harness 与 Environment Provider。
2. Agent 框架接入层只负责协议转换，不应把业务 Rubric 或环境逻辑硬编码进适配器。
3. 长程任务调度需要检查点、超时、重试、幂等和失败恢复，不能沿用普通批量推理队列。
4. 评测结果要保留到 Task、Trial 和 Step 层级，排行榜只是最上层视图。
5. 可参考其开源实现建设本地 Runner，但企业仍需补齐权限、租户、审计、敏感数据和发布门禁。
6. Benchmark 适配器应有契约测试，确保评分口径没有因接入方式变化而失真。

## 局限与阅读警告

AgentCompass 主要面向研究评测基础设施，并不等于开箱即用的企业质量平台；生产在线评估、A/B、告警、审批、多租户和合规治理仍需另建。支持 Benchmark 的数量不代表覆盖企业实际流程，接入后仍要验证任务版本、环境镜像和评分一致性。
