# DeepEval 与 Langfuse 接入比较

> 调研日期：2026-09-04  
> 目的：比较企业内部 Agent 测试平台在端到端评估、组件级评估、单例调试和内部事件采集方面的接入成本。  
> 状态：Langfuse Trace 数据面已获需求方确认；DeepEval 是否作为评测器库引入，仍需在方案阶段最小验证。

## 1. 结论

不能简单回答“DeepEval 和 Langfuse 哪个更容易接入”，因为它们主要解决不同问题：

```text
Langfuse
  └─ Trace / Span / Dataset / Experiment / Score 的平台与数据面

DeepEval
  └─ TestCase / Metric / evaluate / assert_test 的测试执行与指标层
```

针对当前 MVP：

1. **内部事件采集确定使用 Langfuse**：`eyun_assist_bot` 已有 Langfuse 接入和内部部署，实际验证过 Session、Generation、Tool Span 和企业元数据；增量接入成本最低。
2. **开发者评测体验优先借鉴 DeepEval**：`LLMTestCase` 可统一承载端到端、组件级和单例调试；`evaluate()` 适合批量实验，`assert_test()` 适合 CI，`metric.measure()` 适合单例调试。
3. **MVP 不应同时采用两套 `@observe`**：重复埋点会带来两套 Trace、上下文传播、数据模型、配置和调试入口。
4. **建议采用可替换边界**：平台定义自己的 Evaluation Case 和 Trace Contract，Langfuse 作为首个 Trace Provider，DeepEval Metric 作为可选 Evaluator Adapter。

## 2. 用户文章的关键信息

用户提供的文章《agent 评测框架入门：长文谈 deepEval 评测框架》把 `LLMTestCase` 用于三种方式：

- End-to-end：把 LLM 应用视为黑盒，评估整体输入和输出。
- Component-level：在被 `@observe` 的内部组件 Span 上绑定测试用例和指标。
- One-Off Standalone：对单个测试用例执行单个指标，用于调试或自定义评测流水线。

文章作者也明确表达了对组件级 `@observe` 侵入性的担忧。该担忧与本项目相关：如果 Agent 已经有 Langfuse/OTel Trace，再引入 DeepEval Trace，不只是增加一个装饰器，而是形成第二套观测链路。

来源：[微信公众号文章](https://mp.weixin.qq.com/s/LCUeqXVQdVvWwgflqwlWUA)。微信页面触发验证码，正文通过 Tavily URL Extract 获取；上述三类用法已由 DeepEval 官方文档交叉核验。

## 3. 官方能力核验

### 3.1 DeepEval

DeepEval 官方文档确认：

- `LLMTestCase` 同时用于端到端和组件级评估，可携带 `input`、`actual_output`、`retrieval_context`、`tools_called`、`expected_tools`、Token 成本和完成时间等信息。
- 多轮场景使用 `ConversationalTestCase`。
- 端到端评估可以完全不依赖 Tracing，手工构造 TestCase 后调用 `evaluate()` 或 `assert_test()`。
- 组件级评估需要 Trace；可用 `@observe(metrics=[...])` 装饰组件，并通过 `update_current_span(test_case=...)` 把 TestCase 绑定到 Span。
- One-Off 可直接调用 `metric.measure(test_case)`；官方说明它适合调试和自定义流水线，但缺少 `evaluate()` 的批量优化。
- `assert_test()` 在指标低于阈值时抛断言错误，适合 CI 门禁；`evaluate()` 收集结果，不以失败构建为目的。
- 本地评估不要求 Confident AI API Key；共享 Trace UI、团队检索和历史对比属于可选 Confident AI 平台体验。
- 本地结果可通过 `DisplayConfig(results_folder=...)` 保存到文件。

主要优势：

- 测试代码体验直接，天然贴近 pytest/CI。
- 指标库丰富，Agent、RAG、对话、安全均有现成 Metric。
- 同一个 TestCase 概念可以覆盖整体、组件和调试。
- 可完全本地运行，不强制使用托管平台。

主要代价：

- 组件级评估仍需对应用做 Trace 或框架 Instrumentation。
- 如果已有另一套 Trace，使用 `@observe` 会重复观测。
- 团队共享 UI、运行对比和治理需要 Confident AI，或由本项目自行建设。
- DeepEval TestCase 是执行库类型，直接作为企业平台领域模型会形成库绑定。

官方来源：

- [Test Cases](https://deepeval.com/docs/evaluation-test-cases)
- [End-to-End Evaluation](https://deepeval.com/docs/evaluation-end-to-end-llm-evals)
- [Component-Level Evaluation](https://deepeval.com/docs/evaluation-component-level-llm-evals)
- [Unit Testing in CI/CD](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd)
- [DeepEval GitHub](https://github.com/confident-ai/deepeval)

### 3.2 Langfuse

Langfuse 官方文档确认：

- Python SDK 使用 `@observe`、Context Manager 或底层 SDK 创建 Trace/Observation；嵌套通过 OpenTelemetry Context 自动关联。
- 可以混合装饰器、Context Manager、OpenTelemetry Instrumentation 和框架集成。
- Dataset Experiment 为每个 Dataset Item 执行 Task，自动创建 Trace；Evaluator 接收输入、输出、Expected Output 和 Metadata，产生 Score。
- 支持 Item Evaluator 与 Run Evaluator；后者可以计算集合级指标。
- 使用 Langfuse 托管 Dataset 时会创建可在 UI 中比较的 Dataset Run；本地 Dataset 实验目前只创建 Trace 和 Score，不生成正式 Dataset Run 对比视图。
- CI Gate 通过 Experiment Runner 和用户定义阈值/`RegressionError` 实现；Langfuse 提供 Runner、Trace、Score 和比较能力，但具体业务 Evaluator 仍需用户提供。
- 可以自托管在 VPC 或本地环境，但完整部署包括 Web、Worker、Postgres、ClickHouse、Redis/Valkey 和对象存储，运维成本明显高于本地 Python 库。

主要优势：

- 适合统一保存 Agent 内部事件、Trace/Span、模型与工具证据。
- Dataset、Experiment、Score 和 UI 适合团队协作及跨 Run 比较。
- 基于 OpenTelemetry，框架中立性和外部 Instrumentation 选择更丰富。
- `eyun_assist_bot` 已接入内部 Langfuse，存在真实可复用资产。

主要代价：

- 它不是以 `assert_test()` 为核心的本地测试框架；业务指标和断言仍需开发。
- 单个 Case + 单个 Metric 的即时调试没有 DeepEval `metric.measure()` 那么直接。
- 自托管生产级平台有数据库、分析存储、队列和对象存储的运维负担。
- 组件级观测即使支持自动 Instrumentation，也仍需检查 Trace 完整性和异步上下文传播。

官方来源：

- [Instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation)
- [Experiments via SDK](https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk)
- [Experiment Data Model](https://langfuse.com/docs/evaluation/experiments/data-model)
- [Experiments in CI/CD](https://langfuse.com/docs/evaluation/experiments/experiments-ci-cd)
- [Self-host Langfuse](https://langfuse.com/docs/deployment/self-host)
- [Langfuse GitHub](https://github.com/langfuse/langfuse)

## 4. 接入便利性对比

| 维度 | DeepEval | Langfuse | 当前项目判断 |
|---|---|---|---|
| E2E 黑盒 | 很方便；构造 TestCase 后运行 Metric | 方便；Experiment Task + Evaluator | DeepEval 开发者体验更短 |
| 多轮对话 | `ConversationalTestCase` 原生支持 | Trace/Session 可表达，Evaluator 自定义 | 两者可行；旧资产需映射 |
| 组件级内部事件 | `@observe` + Span TestCase，评测一体 | `@observe`/OTel/框架集成，观测更强 | 已有 Langfuse 时优先复用 |
| Tool/Agent 轨迹 | 有 Agent/Tool/Trajectory Metric | Trace 可保存，判定逻辑需自定义 | 沿用旧确定性 Toolflow 更可控 |
| One-Off Debug | `metric.measure()` 最直接 | 可对 Trace/Observation 加 Score，但需更多封装 | DeepEval 更方便 |
| 批量回归 | `evaluate()`/Dataset | Dataset Experiment Runner | 两者都可用 |
| CI 断言 | `assert_test()` / CLI 原生 | Experiment + 自定义 RegressionError | DeepEval 更自然 |
| 团队 UI 与历史 | 需 Confident AI 或自建 | Langfuse 原生强项 | Langfuse 更合适 |
| 自托管成本 | 仅库时很低；Confident AI 另算 | 完整平台运维较重 | 公司已有实例可显著降低边际成本 |
| 框架中立 | TestCase 可中立，Tracing 有框架适配 | OTel + SDK + 框架集成 | Langfuse 更适合作为 Trace Provider |
| 现有资产复用 | eyun 未接入 DeepEval | eyun 已有 Langfuse 4.x 接入 | Langfuse 明显占优 |

## 5. 与 eyun 既有资产的关系

`eyun_assist_bot` 当前 master 已存在：

```text
chat_service
  → Langfuse LangChain CallbackHandler
  → trace_scope(session_id, user_id, enterprise_id)
  → generation / tool span / external generation
```

仓库文档记录该链路在 2026-05-06 已验证 Trace 存在、Session ID 对齐、企业 Metadata 以及 Generation + Tool Span。旧 Session Eval Collector 反而另走 `astream_events()` 采集本地 JSON，没有复用 Langfuse 数据。

因此，新 MVP 的首个关键验证不应是“再给 eyun 加一个装饰器”，而应是：

1. 现有 Langfuse Trace 能否完整映射到统一 Trace Contract；
2. 是否覆盖回答、Tool Name/Args/Result/Error、轮次、Session 和版本身份；
3. 能否从指定 Trace 或 Span 构造统一 Evaluation Case；
4. 同一个 Case 能否进入 E2E、Component 和 Debug 三种运行方式；
5. 缺失事件是否通过 Adapter 补齐，而不是强迫业务代码采用某个评测库。

## 6. 推荐的产品边界

```text
Agent 侧
  ├─ 已有 Langfuse/OTel → 直接接 Trace Provider
  ├─ 框架回调/事件流   → Adapter 转统一事件
  └─ 仅 HTTP API       → 只能提供 E2E 黑盒

平台侧
  ├─ Unified Trace Contract
  ├─ Unified Evaluation Case
  ├─ E2E Runner
  ├─ Component Runner（指定 Span）
  ├─ One-Off Debug Runner
  └─ Evaluator Registry
       ├─ 确定性 Toolflow/Schema/状态断言
       ├─ 自有 LLM Judge
       └─ DeepEval Metric Adapter（候选）
```

该边界保证：

- Langfuse 可以替换为其他 OpenTelemetry/OpenInference 后端；
- DeepEval 可以只作为 Metric Provider，不拥有平台数据模型；
- 黑盒 Agent 仍能接入 E2E，只是无法凭空获得组件级证据；
- 同一个 Scenario 可在不同入口复用，而不是维护三份用例。

## 7. MVP 选型结论

### 已确认纳入

- Langfuse 作为 MVP 唯一 Trace 数据面；优先复用企业现有实例和 eyun 埋点。
- 定义与产品无关的 Trace Contract 和 Evaluation Case。
- E2E、Component、One-Off 三种 Runner 共享同一用例与评估器协议。
- 先迁移旧 Toolflow 确定性评估和 Expected Answer Judge。

### 仍需最小验证后决定

- DeepEval 是否作为第三方 Metric Adapter 引入。
- DeepEval Agentic/Conversation Metric 是否比现有自研 Judge 更稳定。
- Langfuse Dataset/Experiment 是否直接承载正式测试资产，还是只承载 Trace/Score。

### MVP 不建议

- 同时在 Agent 代码中使用 Langfuse `@observe` 和 DeepEval `@observe`。
- 把 `LLMTestCase` 直接作为数据库或 API 的核心 Schema。
- 为获得 One-Off Debug 而引入整套第二 Trace 平台。
- 因 eyun 已有 Langfuse 就把所有 Agent 强制绑定 Langfuse SDK；应允许 OTel、框架事件和黑盒 Adapter。

## 8. 待验证问题

1. 企业现有 Langfuse 的版本、可用 API、数据保留、RBAC 和 Dataset/Experiment 功能边界。
2. eyun 当前 Trace 是否完整覆盖多轮 User/Assistant、Tool Args/Result/Error，而不只是 LLM Token。
3. Langfuse Trace 导出为统一事件的实时性和批量查询成本。
4. DeepEval 指标在中文业务、工具参数和多轮 Session 上的稳定性、成本与可解释性。
5. Judge 模型是否与被测 Agent 隔离，如何建立人工校准集。
6. Component Evaluation 应在 Span 生成时运行，还是离线读取 Trace 后运行。
