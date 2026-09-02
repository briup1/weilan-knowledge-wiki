---
type: synthesis
created: 2026-09-02
updated: 2026-09-02
sources: []
tags:
  - agent-eval
  - evaluation-platform
  - observability
  - quality-engineering
  - platform-architecture
---

# Agent Eval 通用平台全景图

> 调研与产品能力核对截止：2026-09-02。本文面向资源有限的小企业，目标不是一次性建设“大而全”的平台，而是先形成开发期稳定回归能力，再逐步连接 CI/CD 和生产监控。

## 核心结论

Agent Eval 平台由 **8 个业务模块和 1 个基础模块**组成。其中最小闭环必须优先具备四个核心模块：

```text
★ 评测资产管理
★ 可复现执行环境
★ Trace 与证据采集
★ 混合评估器
```

完整闭环如下：

```text
真实业务需求 / 历史故障 / 生产流量
                 │
                 ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. Agent 接入与契约                                          │
│ Adapter｜统一事件模型｜框架中立 Trace                         │
└──────────────────────────────┬────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. 评测控制面                                                │
│ Run 编排｜版本绑定｜并发｜重试｜采样｜预算                    │
└──────────────┬────────────────────────────────────────────────┘
               ├───────────────────────────┐
               ▼                           ▼
┌────────────────────────────┐  ┌───────────────────────────────┐
│ ★ 3. 评测资产管理         │  │ ★ 4. 可复现执行环境          │
│ Dataset / Task             │─→│ Harness / Sandbox / Snapshot  │
│ Rubric / Ground Truth      │  │ Seed / Mock / Replay          │
│ Golden Set / BadCase       │  └──────────────┬────────────────┘
└──────────────┬─────────────┘                 ▼
               │                 ┌───────────────────────────────┐
               │                 │ ★ 5. Trace 与证据采集        │
               │                 │ Session → Trace → Span        │
               │                 │ 模型/工具/检索/状态/成本       │
               │                 └──────────────┬────────────────┘
               └───────────────────────┐        │
                                       ▼        ▼
                         ┌───────────────────────────────────────┐
                         │ ★ 6. 混合评估器                      │
                         │ Rule / Code / LLM Judge / Human       │
                         └──────────────────┬────────────────────┘
                                            ▼
┌───────────────────────────────────────────────────────────────┐
│ 7. 分析与质量决策                                            │
│ 实验对比｜Baseline｜根因分析｜报告｜Release Gate              │
└──────────────────────────────┬────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│ 8. 生产监控与反馈闭环                                        │
│ 在线采样评估｜质量趋势｜漂移｜告警｜BadCase 回流              │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               └──────────回流到 3. 评测资产管理

┌───────────────────────────────────────────────────────────────┐
│ 9. 数据与治理基础（横向支撑 1–8）                            │
│ 元数据｜Trace 库｜指标库｜对象存储｜RBAC｜审计｜脱敏｜保留策略 │
└───────────────────────────────────────────────────────────────┘
```

## 能力概念地图

`★` 表示构成 Agent Eval 最小闭环的核心模块。一级是模块，二级是稳定能力，三级是实现方法，四级才是具体技术或产品。

- Agent Eval 通用平台
  - 1. Agent 接入与契约
    - 1.1 框架中立接入：让不同 Agent 以统一协议提交运行数据和接受评测任务
      - 1.1.1 Adapter 适配模式
        - 1.1.1.1 OpenTelemetry
        - 1.1.1.2 OpenInference
        - 1.1.1.3 Agent SDK Adapter
    - 1.2 版本身份绑定：明确每次评测对应的代码、模型、提示词、工具和配置
      - 1.2.1 不可变运行清单
        - 1.2.1.1 Git Commit
        - 1.2.1.2 Model / Prompt / Tool Version
  - 2. 评测控制面
    - 2.1 评测运行编排：统一创建、调度、停止、恢复和追踪评测运行
      - 2.1.1 队列化任务调度
        - 2.1.1.1 Run / Trial / Job
    - 2.2 运行资源控制：控制并发、重试、超时、采样和成本预算
      - 2.2.1 策略化资源约束
        - 2.2.1.1 Concurrency / Retry / Timeout / Budget
  - 3. ★ 评测资产管理
    - 3.1 任务与数据集管理：沉淀具有明确输入、成功条件和风险标签的业务测试资产
      - 3.1.1 版本化数据集
        - 3.1.1.1 Dataset / Task / Slice
    - 3.2 期望行为定义：定义结果、过程、约束和业务状态的判定依据
      - 3.2.1 Rubric 与参考事实
        - 3.2.1.1 Ground Truth / Golden Set
    - 3.3 失败资产回流：把生产失败和人工发现的问题固化为长期回归用例
      - 3.3.1 BadCase 生命周期
        - 3.3.1.1 Discover / Review / Approve / Regression
  - 4. ★ 可复现执行环境
    - 4.1 Agent 执行适配：以统一 Harness 调用不同 Agent 并收集结果
      - 4.1.1 Harness 解耦模式
        - 4.1.1.1 AgentCompass Harness
    - 4.2 环境隔离与恢复：让工具调用、状态修改和外部副作用可控、可重置
      - 4.2.1 沙箱与环境快照
        - 4.2.1.1 Docker / Remote Sandbox
        - 4.2.1.2 Snapshot / Seed / Mock
    - 4.3 失败复现：用相同版本、输入和环境重新执行问题轨迹
      - 4.3.1 Checkpoint 与 Replay
        - 4.3.1.1 Environment State / Artifact
  - 5. ★ Trace 与证据采集
    - 5.1 全链路轨迹记录：保存模型、工具、检索、记忆和业务状态变化
      - 5.1.1 分层 Trace 模型
        - 5.1.1.1 Session / Trace / Span
    - 5.2 终态与副作用验证：验证真实环境结果，而不是只相信 Agent 的文本回答
      - 5.2.1 状态差异与证据归档
        - 5.2.1.1 State Diff / Artifact / Tool Result
    - 5.3 性能与成本度量：同时记录质量、时延、Token 和工具成本
      - 5.3.1 统一运行指标
        - 5.3.1.1 Latency / Token / Cost / Error
  - 6. ★ 混合评估器
    - 6.1 确定性验证：对结构、权限、工具参数和环境状态执行可复现检查
      - 6.1.1 规则与代码评估
        - 6.1.1.1 Assertion / SQL / Schema / Unit Test
    - 6.2 语义质量判断：依据明确 Rubric 评价正确性、帮助性和过程合理性
      - 6.2.1 LLM-as-a-Judge
        - 6.2.1.1 Judge Prompt / Structured Output
    - 6.3 人工金标准：处理高风险、争议样本并校准自动评估器
      - 6.3.1 专家标注与一致性检查
        - 6.3.1.1 Annotation / Agreement / Calibration Set
    - 6.4 稳定性判断：通过重复 Trial 和统计方法识别偶然成功或退化
      - 6.4.1 重复试验与差异检验
        - 6.4.1.1 pass@k / pass^k / Confidence Interval
  - 7. 分析与质量决策
    - 7.1 版本实验对比：在相同数据和指标下比较 Agent 版本
      - 7.1.1 Baseline 对照实验
        - 7.1.1.1 Candidate Run / Baseline Run
    - 7.2 发布门禁：把严重失败、核心指标和统计退化转为发布决策
      - 7.2.1 硬门槛与趋势门槛
        - 7.2.1.1 CI Check / Release Gate / Waiver
    - 7.3 失败根因定位：定位最早关键错误、传播路径和责任组件
      - 7.3.1 错误树与证据下钻
        - 7.3.1.1 Finding / First Error Span / Owner
  - 8. 生产监控与反馈闭环
    - 8.1 在线质量评估：对生产流量按规则和预算持续采样评分
      - 8.1.1 异步采样评估
        - 8.1.1.1 Filter / Sampling Rate / Online Evaluator
    - 8.2 质量趋势与告警：识别关键指标恶化、分布变化和风险事件
      - 8.2.1 SLO 与漂移检测
        - 8.2.1.1 Dashboard / Threshold / Alert
    - 8.3 生产失败回流：把低分 Trace 转为可审核、可复现的回归任务
      - 8.3.1 Trace-to-Dataset
        - 8.3.1.1 BadCase Queue
  - 9. 数据与治理基础
    - 9.1 评测数据存储：分别管理结构化元数据、轨迹、指标和大对象
      - 9.1.1 多模态分层存储
        - 9.1.1.1 SQL / Trace Store / Object Store
    - 9.2 权限与合规：保护敏感数据并记录关键操作
      - 9.2.1 最小权限与审计
        - 9.2.1.1 RBAC / Audit Log / Data Masking
    - 9.3 生命周期治理：管理资产 Owner、版本、审批、保留和删除策略
      - 9.3.1 策略化治理
        - 9.3.1.1 Tenant / Retention / Approval

## 小企业建设顺序

原则是先解决“改完以后是否退化”，再解决“上线以后是否变坏”，最后补齐规模化治理。

```text
阶段 0：统一契约
    ↓
阶段 1：离线回归 MVP
    ↓
阶段 2：CI/CD 发布门禁
    ↓
阶段 3：生产在线评估
    ↓
阶段 4：治理与规模化
```

### 阶段 0：统一接入和数据契约

**先做**：

- 只选择 1 个真实 Agent 作为首个接入对象。
- 定义最小数据模型：`Dataset → Task → Run → Trial → Trace → Score → Finding`。
- 统一模型调用、工具调用、最终输出、错误、时延和成本字段。
- 绑定 Agent 代码、模型、Prompt、工具和评估器版本。

**暂不做**：多 Agent 框架全覆盖、多租户计费、复杂审批流。

**阶段验收**：

- 一个真实 Agent 可以完整产生 Session、Trace 和 Span。
- 模型调用、工具调用、最终输出和错误四类关键证据完整率达到 95% 以上。
- 任意一次评测结果都能追溯到代码与配置版本。

### 阶段 1：离线回归 MVP

**先做**：

- 建立 50–100 条来自真实业务和历史故障的核心评测任务。
- 支持 Dataset 版本、单次 Run、多次 Trial 和结果对比。
- 至少提供一种确定性代码评估器和一种 LLM Judge。
- 提供单条 Trace 下钻、失败原因和 BadCase 标记。

**暂不做**：评估器市场、复杂权重配置、大规模人工标注平台。

**阶段验收**：

- 开发者可以用一个命令或一次页面操作完成回归评测。
- 失败任务可以下钻到具体模型或工具 Span。
- 相同 Agent 版本重复运行时能够展示成功率、方差和成本差异。

### 阶段 2：CI/CD 发布门禁

**先做**：

- 保存一个经过批准的 Baseline Run。
- 支持硬门槛：越权、危险副作用、关键任务失败不得被平均分抵消。
- 支持候选版本与 Baseline 的指标和 BadCase 差异对比。
- 将关键回归集接入 Pull Request 或发布流水线。

**暂不做**：复杂灰度编排和自动流量调度。

**阶段验收**：

- 每个候选版本自动生成可追溯的评测报告。
- 已知 P0/P1 BadCase 不允许静默退化。
- 门禁结果明确输出通过、拒绝或人工豁免，并保留原因。

### 阶段 3：生产在线评估

**后做**：

- 生产 Trace 分层采样和异步评分，避免阻塞 Agent 主链路。
- 复用开发阶段的评估器版本，避免离线和线上指标定义不一致。
- 建设质量、成本、时延和安全指标 Dashboard 与告警。
- 支持低分 Trace 一键进入 BadCase 审核队列，再转为回归任务。

**阶段验收**：

- 采样率和 Judge 成本具有明确预算上限。
- 关键质量或安全异常能在 15 分钟内形成告警和证据链接。
- 线上 BadCase 经审核后能够进入下一轮 CI 回归集。

### 阶段 4：治理与规模化

**最后做**：

- 多团队、多项目隔离，RBAC、审计、脱敏和数据保留策略。
- 人工标注队列、Judge 校准集和评估器升级 Shadow 验证。
- 灰度/A-B、统计显著性、跨版本趋势和成本核算。
- 通用 Agent Adapter 与环境 Provider 注册机制。

**启动条件**：接入多个业务团队、出现敏感数据要求，或评测任务规模和成本已经需要统一治理。

## 三个开源项目简介

### AgentCompass

AgentCompass 是面向 Agent 能力评测的开源执行基础设施。其核心价值是将 Model、Benchmark、Harness 和 Environment 解耦，并提供并发调度、隔离执行、失败重试、结果持久化与轨迹分析。

**最值得借鉴**：

- Benchmark / Harness / Environment 的接口边界。
- 统一 Runner、并发执行、可恢复运行和环境 Provider。
- Agentic Coding、Deep Research、Tool Calling、GUI 等公开 Benchmark 接入方式。

**不适合直接承担**：

- 企业生产 Trace 接入和在线质量监控。
- 完整的业务 Dataset、人工标注、审批和 Release Gate 产品流程。
- 多租户、RBAC、审计、脱敏和告警中心。

### Arize Phoenix

Arize Phoenix 是基于 OpenTelemetry 与 OpenInference 的开源 AI 可观测和评估平台，提供 Trace、Dataset、Experiment、代码/LLM 评估器、人工标注、Prompt 管理和 Span Replay。

**最值得借鉴或复用**：

- 框架中立 Trace 采集、Trace 下钻和评估证据展示。
- 从生产 Trace 构建 Dataset，再执行 Experiment 的开发闭环。
- 代码评估器、LLM Judge 和人工标签统一附着到 Trace/Span。

**主要缺口**：

- 不负责通用 Agent Harness、工具沙箱、环境快照和完整状态 Replay。
- 开源 Phoenix 的生产持续评估、阈值触发和告警能力不完整，官方将完整在线评估指向商业产品 Arize AX。
- 缺少面向企业发布审批的完整 Baseline、Release Gate 和豁免工作流。

### Langfuse

Langfuse 是可自托管的 LLM/Agent 工程平台，覆盖 Trace、Session、Dataset、Experiment、Score、LLM Judge、代码评估、人工标注、Dashboard 和在线评估规则，并提供 CI/CD Experiment Gate。

**最值得借鉴或复用**：

- Offline Experiment → CI Gate → Online Evaluation → BadCase 回流的完整产品闭环。
- Dataset、Dataset Item、Experiment、Trace、Observation 和 Score 数据模型。
- 在线规则按过滤条件和采样率触发评估器，复用离线评估逻辑。

**主要缺口**：

- 不负责隔离执行 Agent、构建工具沙箱或重置外部业务环境。
- 对真实业务终态、副作用和复杂工具轨迹的验证仍需自定义 Runner 与代码评估器。
- 完整审计等治理能力存在版本或企业版边界，不能假设开源基础版全部具备。

## 与全景图的模块覆盖对比

图例：`●` 原生能力较完整；`◐` 有部分能力但需要扩展或外部系统；`○` 基本不覆盖。

| 全景模块 | AgentCompass | Arize Phoenix | Langfuse |
|---|:---:|:---:|:---:|
| 1. Agent 接入与契约 | ◐ | ● | ● |
| 2. 评测控制面 | ◐ | ◐ | ◐ |
| **3. ★ 评测资产管理** | ◐ | ● | ● |
| **4. ★ 可复现执行环境** | ● | ○ | ○ |
| **5. ★ Trace 与证据采集** | ◐ | ● | ● |
| **6. ★ 混合评估器** | ◐ | ● | ● |
| 7. 分析与质量决策 | ◐ | ◐ | ◐ |
| 8. 生产监控与反馈闭环 | ○ | ◐ | ◐ |
| 9. 数据与治理基础 | ◐ | ◐ | ◐ |

### 覆盖差异说明

| 项目 | 覆盖最强的部分 | 需要自行补齐的部分 |
|---|---|---|
| AgentCompass | Runner、Harness、Benchmark、环境隔离、并发与可恢复执行 | 业务资产治理、标准生产 Trace、在线评估、告警、发布门禁、企业治理 UI |
| Arize Phoenix | OTel/OpenInference Trace、Dataset、Experiment、评估器、调试 UI | Agent 执行 Harness、业务环境快照、正式发布门禁；完整在线告警通常需要 Arize AX |
| Langfuse | Trace、Dataset、Experiment、Score、离线/在线评估、CI 集成 | Agent 沙箱、环境终态恢复、复杂工具副作用验证、完整企业治理与漂移体系 |

因此，**三个项目都不能独立覆盖全景图的所有模块**：

```text
AgentCompass：执行强，平台闭环弱
Phoenix：     Trace 与调试强，执行环境和生产告警弱
Langfuse：    产品闭环最广，Agent 执行环境弱
```

## 小企业推荐组合

### 默认方案：Langfuse + 轻量自研 Runner

适合希望尽快获得“开发回归 + CI 门禁 + 生产观察”闭环的小企业。

```text
Langfuse
  ├─ Trace / Session / Dataset / Experiment / Score
  ├─ LLM Judge / Code Evaluator / 在线评估规则
  └─ Dashboard / CI Experiment Gate

轻量自研 Runner（参考 AgentCompass）
  ├─ Agent Adapter
  ├─ Trial 调度
  ├─ Sandbox / Mock / Environment Reset
  └─ 业务终态与副作用验证
```

### 替代方案：Phoenix + 轻量控制面

适合更重视 OpenTelemetry/OpenInference、Trace 调试和开放标准，并愿意自行建设 CI 门禁与在线告警的团队。

### 组合原则

- MVP 阶段在 Phoenix 和 Langfuse 中二选一，避免同时建设两套高度重叠的 Trace、Dataset 和 Experiment 系统。
- AgentCompass 更适合作为 Runner 与执行环境的架构参考，或按需复用部分 Harness，不应被当成完整企业 Eval 门户。
- 企业真正需要长期自建的是业务 Dataset、Rubric、Ground Truth、环境终态检查、Release Gate 策略和 BadCase 生命周期。

## 第一版范围建议

第一版只交付下面这条最短路径：

```text
1 个 Agent Adapter
      ↓
50–100 条业务 Task
      ↓
1 个可重复执行的 Runner
      ↓
完整模型/工具 Trace
      ↓
代码规则 + 1 个 LLM Judge
      ↓
Run 对比报告
      ↓
CI 硬门禁
```

第一版明确不做：多租户计费、评估器市场、复杂 A/B、全量实时 Judge、通用人工标注平台和所有 Agent 框架适配。

## 调研依据

- [AgentCompass 官方仓库](https://github.com/open-compass/AgentCompass)
- [Arize Phoenix 官方文档](https://arize.com/docs/phoenix)
- [Phoenix Evaluation](https://arize.com/docs/phoenix/evaluation/llm-evals/evaluator-traces)
- [Langfuse Evaluation 核心概念](https://langfuse.com/docs/evaluation/core-concepts)
- [Langfuse CI/CD Experiments](https://langfuse.com/docs/evaluation/experiments/experiments-ci-cd)
