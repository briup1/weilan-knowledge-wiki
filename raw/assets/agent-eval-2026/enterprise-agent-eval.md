# 企业级 Agent Eval 平台：技术认知、架构与建设路线

> 研究截止：2026-09-01。本文综合本目录 20 篇一手资料，目标是形成可用于企业平台立项、技术选型和 MVP 设计的判断。

## 一、结论

企业级 Agent Eval 的本质不是“给模型答案打分”，而是建设一个覆盖**结果、轨迹、工具、环境状态、安全、成本、稳定性和根因**的全生命周期质量系统。

真正的平台闭环应是：

```text
真实业务失败/产品需求
        ↓
评测集、Rubric、Ground Truth 与版本治理
        ↓
隔离且可复现的 Agent Harness
        ↓
统一 Trace：模型、工具、检索、记忆、状态、副作用
        ↓
规则/代码 + LLM Judge + 人工专家混合评分
        ↓
结果、轨迹、工具、安全、成本、时延、稳定性分析
        ↓
开发回归 → CI/CD 门禁 → 生产在线评估
        ↓
BadCase 回流 → 根因定位 → 优化建议 → 批量验证/A-B
```

平台成败不取决于评估器数量，而取决于四件事：任务是否代表真实业务、执行是否可复现、分数是否可信、结果是否能进入发布决策和生产闭环。

## 二、2026 年技术演进判断

### 2.1 从 Outcome-only 转向 Outcome + Trajectory

[Anthropic](international/01-anthropic-demystifying-agent-evals.md) 将 Task、Trial、Trajectory、Outcome 和 Grader 拆开；[NVIDIA](international/09-nvidia-agent-evaluation.md) 将任务、工具、轨迹和效率并列；[WeaveBench](international/12-microsoft-weavebench.md) 进一步说明只看终态会高估 Agent。

平台必须同时回答：

- 最终目标是否达成？
- Agent 通过什么步骤达成？
- 是否调用正确工具和参数？
- 是否产生错误、危险或未经授权的副作用？
- 是否通过伪造证据、硬编码结果或绕开环境“投机成功”？

### 2.2 从离线 Benchmark 转向全生命周期评估

[AWS AgentCore](international/03-aws-agentcore-evaluations.md)、[Microsoft Foundry](international/06-microsoft-foundry-evaluate-agents.md)、[华为云 AgentArts](china/05-huawei-complex-tool-agent-evaluation.md) 均把评测做成产品能力；[ATLAS](china/03-atlas-industrial-tool-agents.md) 更明确连接生产日志、离线回放和在线 A/B。

企业目标不是每季度跑一次大测，而是：

```text
开发者本地小样本
   ↓
PR / CI 回归
   ↓
候选版本全量离线评测
   ↓
发布硬门禁
   ↓
灰度与 A/B
   ↓
线上采样评估、漂移与告警
   ↓
BadCase 转回回归集
```

### 2.3 从单一 LLM Judge 转向混合评估器

[Anthropic](international/01-anthropic-demystifying-agent-evals.md)、[AWS 自定义代码评估器](international/04-aws-custom-code-evaluators.md)、[OpenAI 数据 Agent](international/10-openai-in-house-data-agent.md) 和 [EVMbench](international/14-openai-evmbench.md) 共同支持一个原则：**可确定验证的问题优先用代码，开放式质量才使用 LLM Judge，人工负责金标准与校准。**

推荐优先级：

```text
确定性状态/Schema/权限/副作用
        → 规则、SQL、单元测试、代码 Grader
语义质量/帮助性/解释充分性
        → Rubric + LLM Judge
高风险、争议、Judge 校准
        → 人工专家
```

### 2.4 从评 Agent 转向同时评评测资产

[IBM Benchmarking the Benchmarks](international/11-ibm-benchmarking-the-benchmarks.md) 表明任务描述、期望行为和领域策略可能互相矛盾；错误 Benchmark 会产生错误排名和发布决策。因此 Dataset、Task、Rubric、Ground Truth 和 Evaluator 都必须版本化、测试和审核。

### 2.5 从单轮成功转向长程可靠性

[E-CommerceBench](china/02-ecommerce-bench.md) 评估 365 天经营，[AcCoRD](international/15-accord-user-agent-collaboration.md) 评估用户偏好形成与变化，[ATLAS](china/03-atlas-industrial-tool-agents.md) 同时观察请求内和跨请求体验。企业平台的数据模型必须原生支持 Session、Journey、状态快照和延迟结果，不能把所有任务压缩为 input/output。

### 2.6 从失败统计转向轨迹根因

[TRAJDEBUG](china/04-trajdebug.md) 关注最早关键错误和错误传播，[ExCyTIn-Bench](international/13-microsoft-excytin-bench.md) 用调查图保存证据链。成熟平台需要从“失败率 12%”进一步回答：哪一步、哪个组件、什么证据、是否恢复、如何复现和应该由谁修复。

## 三、平台目标架构

```text
┌──────────────────────────────────────────────────────────────┐
│  体验层                                                      │
│  数据集/任务管理 | 实验对比 | BadCase | 报告 | 发布门禁 | 审计 │
└───────────────────────────────┬──────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────┐
│  评测控制面                                                  │
│  Run 编排 | 版本绑定 | 采样 | 预算 | 重试 | 并发 | 审批 | RBAC │
└──────────┬───────────────────┬───────────────────┬───────────┘
           ↓                   ↓                   ↓
┌────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ 资产注册中心   │   │ 评估器注册中心   │   │ 发布与实验中心   │
│ Dataset/Task   │   │ Rule/Code/Judge  │   │ Baseline/Gate/A-B│
│ Rubric/GT      │   │ Human/Composite  │   │ Drift/Alert      │
└───────┬────────┘   └─────────┬────────┘   └─────────┬────────┘
        └──────────────────────┼──────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│  框架中立执行面                                              │
│  Agent Adapter | Harness | Environment Provider | Sandbox    │
│  Snapshot | Seed | Secret Broker | Checkpoint | Replay       │
└───────────────────────────────┬──────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────┐
│  统一 Trace 与证据层                                         │
│  Model | Tool | Retrieval | Memory | State | File/GUI | Cost │
│  OpenTelemetry/OpenInference 兼容采集 + Artifact/Object Store │
└───────────────────────────────┬──────────────────────────────┘
                                ↓
┌──────────────────────────────────────────────────────────────┐
│  数据与治理层                                                │
│  元数据 DB | 指标库 | Trace 库 | 对象存储 | 脱敏 | 保留策略  │
└──────────────────────────────────────────────────────────────┘
```

### 架构原则

1. **框架中立**：通过 Adapter 接入 LangGraph、OpenAI Agents SDK、AutoGen、自研 Agent 等；评测定义不绑定框架。
2. **Trace 优先**：先统一可观测数据，再扩展高级 Judge；没有证据的分数不可审计。
3. **环境可复现**：保存镜像、数据快照、随机种子、依赖、工具版本与外部事实快照。
4. **评估器即代码资产**：版本、测试、Owner、适用范围、成本、校准集和变更审核均可追踪。
5. **硬风险独立门禁**：越权、数据泄露、危险副作用等不能被平均高分抵消。
6. **聚合与证据并存**：高层看趋势和门禁，工程师能下钻到任务、Trial、Step 和原始 Artifact。

## 四、五个核心能力域

### 4.1 评测资产治理

包含 Dataset、Task、Rubric、Ground Truth、Policy、切片、难度、Owner、审批和版本。必须支持：

- 真实业务样本、专家构造、合成生成和生产 BadCase 四类来源。
- 去重、脱敏、污染检查、可解性检查和参考解验证。
- Policy/Risk/Tool/Language/User Segment 覆盖矩阵。
- 能力集与回归集分离；稳定能力从探索集转入回归集。
- Dataset 版本 Diff：新增、删除、修改、难度和分布变化。

### 4.2 框架中立执行与 Trace 接入

借鉴 [AgentCompass](china/01-agentcompass.md) 的 Benchmark/Harness/Environment 解耦和 [AWS 框架中立评估](international/05-aws-framework-neutral-evaluation.md)：

- Agent Adapter：标准化输入、输出、会话和取消协议。
- Harness：调度 Trial，管理超时、重试、并发、预算和检查点。
- Environment Provider：数据库、浏览器、桌面、代码沙箱、SaaS 仿真和 Mock 工具。
- Trace Collector：统一模型、工具、检索、记忆、状态、副作用和成本 Span。
- Replay：重建环境与输入，确定性地复现工具响应或明确标记不可确定部分。

### 4.3 评估器注册中心

| 类型 | 最适合 | 优点 | 风险/治理 |
|---|---|---|---|
| 规则/代码 | Schema、状态、权限、精确结果、单测 | 快、便宜、可复现 | 维护成本、易漏开放式质量 |
| LLM Judge | 语义正确、帮助性、完整性、Rubric | 灵活、扩展快 | 偏差、漂移、成本、提示注入 |
| 人工专家 | 高风险、金标准、争议、校准 | 可信、能处理复杂语境 | 贵、慢、一致性需管理 |
| 复合评估器 | 发布门禁、多维质量 | 可表达复杂策略 | 权重可能掩盖硬失败 |
| 统计评估器 | 稳定性、显著性、漂移 | 控制随机性和误报 | 需要足够样本与正确假设 |

注册信息至少包含：版本、Owner、输入契约、输出 Schema、Rubric、模型与提示词、成本、延迟、校准集、人工一致性、适用/禁用场景、依赖和审计记录。

### 4.4 全生命周期评估

| 阶段 | 目的 | 数据量 | 运行频率 | 典型门槛 |
|---|---|---:|---|---|
| 本地调试 | 快速发现明显失败 | 20–50 | 每次改动 | 无严重失败、关键题通过 |
| PR/CI | 防回归 | 关键回归集 | 每次提交/合并 | 硬指标零退化 |
| 候选版本 | 完整对比 | 全量 + 重复 Trial | 发布前 | 对 Baseline 显著改善或不退化 |
| 灰度/A-B | 检查真实业务效果 | 生产样本 | 持续 | 护栏无恶化、目标指标改善 |
| 在线评估 | 质量与漂移 | 分层采样 | 实时/小时/天 | SLO、风险、成本、分布告警 |
| 事故回流 | 固化已知失败 | 新 BadCase | 事故后 | 修复后转入回归集 |

### 4.5 轨迹回放、根因与 Judge 校准

- BadCase 按错误树分类：任务/数据、模型、提示词、工具、检索、记忆、环境、权限、评估器。
- 标记最早关键错误、后续传播、自动恢复和最终症状。
- 对长轨迹生成多粒度摘要，但保留原始证据和可定位 Step ID。
- 使用 Golden Set 定期测 Judge 的准确率、召回率、排序一致性和与专家的一致性。
- Judge 版本升级先 Shadow 运行，与旧版本和专家对比后再切换。
- 对 LLM Judge 做提示注入、防位置偏差、顺序交换、自一致性和异常输出测试。

## 五、核心数据模型

```text
Dataset
  └─ Task ────────────────┐
       ├─ Rubric          │
       ├─ Ground Truth    │
       └─ Environment Spec│
                          ↓
Agent Version + Config → Run
                          └─ Trial（同一 Task 的一次尝试）
                               ├─ Trace
                               │    └─ Step/Span + Artifact + State Diff
                               ├─ Score ← Evaluator Version
                               └─ Finding（根因、证据、严重性、归属）

Baseline ← 一组已批准 Run
Release Gate ← Baseline + 指标规则 + 风险硬约束
```

### 建议实体

| 实体 | 关键字段 |
|---|---|
| Dataset | id、version、owner、source、policy、slice、approval、retention |
| Task | prompt/input、expected outcome、constraints、risk、tags、environment spec |
| Trial | task、run、seed、attempt、status、start/end、budget、environment snapshot |
| Run | agent/config/model/evaluator/dataset 版本、执行策略、commit、trigger |
| Trace | trace/span id、event type、timestamp、parent、payload ref、cost、latency |
| Evaluator | type、version、input contract、rubric/model/prompt/code、calibration |
| Rubric | dimension、definition、scale、examples、hard/soft、weight |
| Score | evaluator、trial、dimension、value、reason、evidence refs、confidence |
| Finding | category、first error step、severity、root cause、propagation、owner |
| Baseline | approved run、scope、metrics、effective time、approver |
| Release Gate | metric expression、slice、threshold、hard failure、decision、waiver |

## 六、指标体系

### 6.1 结果指标

- 任务成功率、业务状态正确率、约束满足率。
- `pass@k`：多次尝试至少成功一次，适合探索能力。
- `pass^k`：多次尝试全部成功，适合企业稳定性要求。
- 平均分、分位数、方差、置信区间及与 Baseline 的统计差异。

### 6.2 过程和工具指标

- 工具选择精确率/召回率、参数和 Schema 合规率。
- 必需步骤召回、禁止步骤/工具调用率、无效重试和循环率。
- 首个关键错误位置、错误恢复率和错误传播深度。
- 轨迹效率：成功任务步骤数、工具次数和冗余路径。

### 6.3 安全与治理指标

- 越权调用、敏感数据泄露、危险副作用、提示注入成功率。
- 权限拒绝正确率、审计完整率、敏感字段脱敏率。
- Reward Hacking、伪造证据和环境逃逸率。
- 高风险问题全部采用独立硬门禁，不进入可被抵消的加权总分。

### 6.4 性能与成本指标

- 端到端时延、首 Token、工具等待、P50/P95/P99。
- 每 Trial Token、模型成本、工具/API 成本和沙箱成本。
- 每成功任务成本、预算超限率、并发吞吐和队列等待。

### 6.5 长程与用户协作指标

- 跨会话目标保持率、记忆正确率和过期偏好清理率。
- 必要澄清召回、无效澄清次数、偏好冲突检测率。
- 长期 KPI 趋势、策略漂移、状态一致性和延迟风险。

## 七、典型发布门禁

```yaml
release_gate: customer-service-agent-v3
baseline: v2.8-approved
scope: regression-suite-2026-09
trials_per_task: 3
hard_fail:
  unauthorized_tool_call_rate: 0
  sensitive_data_leak_count: 0
  dangerous_side_effect_count: 0
  critical_task_pass_pow_3: ">= 0.98"
non_regression:
  overall_task_success_delta: ">= -0.01"
  required_tool_schema_rate: ">= 0.995"
  p95_latency_delta: "<= +10%"
  cost_per_success_delta: "<= +15%"
improvement:
  target_slice_success_delta: ">= +0.03"
judge_quality:
  golden_set_agreement: ">= 0.90"
decision:
  - hard_fail 命中：自动拒绝，不允许平均分抵消
  - 非回归失败：需责任人修复或有时效的审批豁免
  - 统计样本不足：结果标为 inconclusive，不自动批准
```

## 八、Build vs Buy

| 方案 | 优势 | 局限 | 适合情况 |
|---|---|---|---|
| 云厂商原生：AWS / Microsoft / Google / 华为 | 与云上模型、Trace、身份和运维集成快 | 锁定生态、跨云和自研框架适配需验证 | 已深度绑定单一云、优先快速上线 |
| 开源底座：AgentCompass 等 | Harness/Benchmark 可控，便于私有化和扩展 | 企业治理、线上闭环、UI、SLA 需自建 | 算法平台强、数据敏感、框架多样 |
| 自研平台 | 完全贴合发布流程、权限和业务规则 | 建设与持续维护成本最高 | Agent 数量多、风险高、已有平台工程能力 |
| 混合方案（推荐） | 复用云/开源 Runner 与可观测能力，自建资产和治理控制面 | 需要稳定接口和集成治理 | 大多数中大型企业 |

### 推荐边界

**优先购买/复用**：模型调用、基础 Trace、沙箱基础设施、通用安全扫描、批量调度组件。

**优先自建**：业务 Dataset/Rubric、Ground Truth、发布门禁、权限策略、BadCase 闭环、Judge 校准和跨框架统一数据模型。这些构成企业长期质量资产和差异化能力。

产品 POC 必须实测：

1. 是否能导出完整原始 Trace 和 Score 证据，避免数据锁定。
2. 是否支持自定义代码评估器与私有 Judge。
3. 是否能接入非厂商框架、自研 Agent 和外部模型。
4. 是否支持离线、在线、A/B 和发布门禁复用同一评估器定义。
5. 多租户、RBAC、SSO、审计、加密、数据驻留和保留策略。
6. 运行成本、并发、长任务、超时、重试和私有化部署。

## 九、建设路线

### 阶段 0：两周验证

目标：验证评测是否能稳定区分当前版本和已知坏版本。

- 选择一个高价值 Agent 和 20–50 条真实任务。
- 接入模型、工具和最终状态 Trace。
- 实现 3–5 个代码/规则评估器与 1 个 Rubric Judge。
- 对每题运行 3 次，输出逐题证据与 `pass^3`。
- 用历史 BadCase 构造一个故意退化版本，验证平台能阻止发布。

### 阶段 1：MVP（6–10 周）

目标：进入日常研发与发布门禁。

- Dataset/Task/Rubric/Evaluator/Run/Trial/Trace/Score 基础模型。
- 框架 Adapter、批量 Runner、超时重试、成本预算和 Artifact 存储。
- 版本对比、切片指标、BadCase 下钻和基础 Release Gate。
- Golden Set、人工抽检和 Judge 版本记录。
- CI API/CLI 与结果回写。

**MVP 不做**：通用低代码题目生成市场、复杂自动根因 Agent、全行业 Benchmark 商店、跨云全自动编排和高度可配置工作流引擎。

### 阶段 2：生产闭环（2–4 个月）

目标：让评测覆盖线上质量和优化验证。

- OpenTelemetry/OpenInference 兼容 Trace 接入。
- 生产采样、脱敏、反馈和 BadCase 入库审批。
- 在线指标、漂移告警、灰度/A-B 关联。
- 环境快照与 Replay；长轨迹多粒度查看。
- Judge Shadow、校准仪表盘与评估器契约测试。

### 阶段 3：企业治理（4–8 个月）

目标：跨团队复用、审计和规模化运营。

- 多租户、RBAC、SSO、密钥代理、数据驻留与保留策略。
- 资产审批、Owner/SLA、评估器可信等级和审计导出。
- 成本中心、预算分配、配额和跨团队对比。
- 安全红队、Reward Hacking、环境污染和反作弊套件。
- 长程 Journey、动态用户模拟、状态/副作用图与根因知识库。

## 十、可量化成功标准

### MVP 验收

- 100% Run 绑定 Agent、Dataset、Evaluator、环境和代码版本。
- 100% Score 可追溯到 Trial、Evaluator 和至少一个证据引用。
- 已知退化版本在关键回归集中被门禁拦截率 ≥ 95%。
- 同一快照重复运行的确定性 Grader 结果一致率 = 100%。
- Judge 在 Golden Set 上与专家一致率 ≥ 90%，且按场景切片展示。
- 典型 100 条评测从发起到报告完成 ≤ 30 分钟（不含外部慢工具特例）。
- 失败样本从报告下钻到首个可疑 Step ≤ 3 次点击。

### 生产阶段验收

- ≥ 80% P0/P1 生产 Agent 接入统一 Trace 和发布门禁。
- ≥ 70% 经确认的生产 BadCase 在 5 个工作日内进入回归集。
- 因已知回归导致的线上事故数较上线前下降 ≥ 50%。
- 高风险指标漏报率按季度人工审计，目标 < 1%。
- 平台评测成本、单成功任务成本和 Judge 成本按团队可归集、可预算、可告警。
- 线上告警均可关联 Agent 版本、Trace、评估器版本和发布记录。

## 十一、安全、权限与审计

- 生产 Trace 默认最小化采集并执行字段级脱敏；敏感原文与派生指标分库存储。
- Runner 不直接持有长期 Secret，通过短期凭证和 Secret Broker 注入。
- 环境按任务隔离，网络、文件、数据库和工具权限采用白名单。
- 评测数据有租户、项目、环境和密级边界，严禁跨租户用作 Judge 示例。
- 人工标注页面按需展示最小上下文，并记录访问与导出审计。
- 评估器、Rubric、门禁和豁免全部版本化；豁免必须有 Owner、原因和到期时间。
- 对评测平台本身做提示注入、数据外泄、越权、环境逃逸、污染和评分欺骗测试。

## 十二、最容易失败的建设方式

1. **先做漂亮排行榜，再补真实任务**：结果与生产价值脱节。
2. **所有问题都交给 LLM Judge**：成本高、不可复现，且确定性错误难审计。
3. **只保留 input/output/score**：无法定位工具、状态和副作用失败。
4. **混用数据集、Agent 和 Judge 版本**：分数变化没有可解释性。
5. **只看平均总分**：严重安全失败被高分维度抵消。
6. **离线指标与线上口径两套系统**：无法形成发布和生产闭环。
7. **过早建设通用工作流和自动优化 Agent**：在数据、Trace 和门禁不可靠时扩大复杂度。
8. **忽略 Benchmark 与 Evaluator 质量**：把测试设计缺陷误判为 Agent 能力。

## 十三、最终建议

推荐采用“**混合方案 + Trace 优先 + 业务资产自建**”：

```text
复用云/开源执行与可观测组件
              +
自建 Dataset/Rubric/Ground Truth/Release Gate 控制面
              +
规则/代码、LLM Judge、人工专家混合评估
              +
生产 BadCase 与 A/B 闭环
```

第一阶段只选择一个真实 Agent，证明“已知坏版本能被稳定拦截、失败能定位、结果能进入发布流程”；做到这一点后，再扩展在线评估、长程场景和企业治理。不要从“支持多少评估器”定义平台价值，应从“减少多少回归事故、缩短多少定位时间、覆盖多少高风险发布”定义价值。

## 参考资料导航

完整 20 篇资料见 [README](README.md)。优先阅读：

1. [Anthropic：Agent Eval 方法论](international/01-anthropic-demystifying-agent-evals.md)
2. [Amazon：真实 Agent 评估经验](international/02-amazon-real-world-agent-evaluation.md)
3. [OpenAI：内部数据 Agent](international/10-openai-in-house-data-agent.md)
4. [IBM：评估 Benchmark 本身](international/11-ibm-benchmarking-the-benchmarks.md)
5. [AgentCompass：统一评测基础设施](china/01-agentcompass.md)
6. [ATLAS：生产双时间尺度评测](china/03-atlas-industrial-tool-agents.md)
7. [TRAJDEBUG：失败轨迹根因](china/04-trajdebug.md)
