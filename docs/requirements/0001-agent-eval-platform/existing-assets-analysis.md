# 企业内部 Agent 测试平台：既有资产分析

> 分析日期：2026-09-04  
> 来源仓库：`/home/weilan/workdir/remote_project/eyun_assist_bot`  
> 分析方式：只读检查 Git refs、提交、源码、文档和历史产物；未切换分支，未修改来源仓库，未调用真实 Agent 或外部服务。  
> 本文是需求共识文档的证据附件；需求状态与最终边界仍以 `requirement.md` 为准。

## 1. 结论

既有资产不是一段简陋评分逻辑，而是三组互补资产：

1. **Session 级 Agent 评测闭环**：完整保存于专用远端分支，覆盖真实 Agent 旁路采集、多轮场景、工具流程评估、回答评估、多次运行稳定性、报告和 Web 控制台。
2. **后续增强的 Runner 与控制台**：专用分支合入其他特性分支后，增加批量场景采集、多 Benchmark 选择、运行进度、刷新恢复和场景转正式基准等能力。
3. **模型横向评测脚本**：独立分支中存在 28 条单轮黑盒用例、多模型批量执行、启发式评分、稳定性、时延和 Token/成本采集。

这些资产证明了下列方向已经经过实践验证：

```text
真实 Agent 旁路执行
  → 采集回答与 Tool Trace
  → 分离评估结果和工具过程
  → 对同一场景重复运行
  → 输出稳定性与失败证据
```

但它们尚未形成通用企业平台：Session Collector 与 `eyun_assist_bot` 的 DeepAgents 实现、内部环境和业务身份强耦合；没有自动生成用例、通用 Agent 接入契约、完整跨版本比较、评估器校准、持久化治理和正式发布门禁。

## 2. 资产定位

### 2.1 Session 级评测专用分支

| 项目 | 事实 |
|---|---|
| Git ref | `origin/feature/agent-multi-session-evaluation-management` |
| 分支 tip | `ae34056a3ce5aa12080cfbf19fd5dca5007a1efc` |
| 主要开发时间 | 2026-07-16 至 2026-07-20 |
| 资产目录 | `agent_session_eval/` |
| 规模 | 137 个相关文件、约 2.9 万新增行（含历史 Session、报告和 HTML） |
| 当前 master | 不包含该资产 |

该分支最适合还原设计意图和读取完整历史样本，因为它仍保留：

- 3 条上下文业务场景；
- 每条场景 4 次以上真实运行；
- Expected Toolflow；
- Expected LLM Answer；
- `summary.json`、`stability.json` 和单文件 Dashboard；
- 原始 PRD、结构规范及 PoC 归档。

### 2.2 后续增强版本

专用分支之后，评测代码继续在 `origin/feature/dev` 等分支演进，最后一个相关提交为：

| 项目 | 事实 |
|---|---|
| 最新相关提交 | `4a50d1d`，2026-07-22 |
| 增强能力 | 批量场景采集、多 Benchmark 选择、当前任务进度、刷新恢复、标记正式基准 |
| 代码保留 | Runner、Web 控制台、文档、PoC 归档 |
| 业务资产处理 | `agent_session_eval/benchmarks/` 改为本地目录并被 `.gitignore` 忽略，Git 中的 Benchmark 定义和样本被删除 |

因此，“最新代码”和“完整业务资产”不在同一个 Git tree 中：

```text
专用分支 ae34056
  ├─ 完整 Benchmark 资产
  ├─ 历史运行结果
  └─ 较早 Runner / Web

feature/dev（截至 4a50d1d）
  ├─ 增强 Runner / Web
  └─ Benchmark 改为本地、不再由 Git 保存
```

后续迁移不能简单复制某个分支目录，应分别提取“完整资产”和“最新执行代码”。

### 2.3 多模型评测分支

| 项目 | 事实 |
|---|---|
| Git ref | `origin/task/model-eval-scripts` |
| 分支 tip | `a55f309d7782cf3224703af90fe10f1b240617e6` |
| 用途 | 比较不同主模型和 Skill 优化前后的表现 |
| 测试输入 | 28 条单轮标准用例 |
| 历史结果 | 40 个结果文件，每个文件 28 条用例 |
| 执行方式 | 通过 `/chat` SSE 接口进行黑盒测试 |

该资产与 Session 级评测目的不同：

- Session 评测关注多轮上下文、Toolflow、开放回答和业务连续性。
- 模型评测关注首轮输入、输出格式、港口/日期等确定性规则、速度和 Token 成本。

它适合作为未来“黑盒 HTTP Agent 接入”和“性能/成本指标”的参考，不应与 Session Benchmark 强行合并成同一种用例。

## 3. Session 评测的数据流

```text
Scenario YAML
  │  多轮用户输入、来源、风险点
  ▼
collect_real_session.py
  │  直接创建 eyun DeepAgents Agent
  │  通过 astream_events 旁路执行
  ▼
real_session.json
  ├─ assistant_text
  ├─ tool name / args / result preview / error
  ├─ turn_id / trace_id / run_id
  └─ started_at / ended_at
       │
       ├──────────────┐
       ▼              ▼
Expected Toolflow   Expected LLM Answer
       │              │
agentevals matcher   LLM Judge
       │              │
       └──────┬───────┘
              ▼
run-NN 评估明细
              ▼
stability.json + summary.json/.md + Dashboard
```

### 3.1 资产分层

旧系统已经形成了清晰的职责分离：

| 资产 | 职责 |
|---|---|
| Scenario | 只描述用户输入、来源和风险点 |
| Expected Toolflow | 描述必须/禁止的工具调用、参数、轮次和匹配模式 |
| Expected LLM Answer | 描述每轮及整段 Session 的语义期望 |
| Real Session | 保存真实 Agent 回答和工具证据 |
| Run Report | 保存单次流程评估与回答评估结果 |
| Stability | 聚合同一场景多次 Run 的通过率、均值和标准差 |
| Benchmark Set | 组织场景，并区分 `official`、`review`、`skipped` |

该分层与当前项目“沉淀场景、识别退化、保证稳定”的目标高度一致，应优先继承其领域概念，而不是重新发明一套命名。

### 3.2 执行与副作用控制

旧 Collector 采用旁路方式：

- 直接调用真实 `create_deep_agent()`；
- 使用 `astream_events(version="v2")` 捕获模型输出和工具事件；
- 不经过 `chat_service.stream()`，避免写聊天历史；
- 默认 Mock 港口识别审计写入；
- 可连接 MongoDB、MySQL，并调用开发环境服务；
- 不保存完整 Tool 输出，只保留截断预览。

这证明“旁路执行真实 Agent、避免污染主聊天链路”可行。但它只处理了该业务已知的一个审计副作用，并不等于具备通用沙箱或环境重置能力。

### 3.3 评估方法

旧系统采用两条独立评估链：

1. **Toolflow**：通过 `langchain-ai/agentevals` 进行 `strict / unordered / subset / superset` 轨迹匹配，并扩展业务参数 Matcher；支持禁止工具调用。
2. **回答质量**：使用前缀上下文评估当前轮回答，并追加 whole-session LLM Judge；通过条件是平均分达到阈值且所有阻断项通过。

这个分工应保留：工具是否调用正确应优先确定性判断，开放回答质量再交给语义评估器。

## 4. 历史结果说明

专用分支保存的 `R-20260706-H001` 报告包含 3 条 Review 场景，每条汇总 4 次 Run：

| 场景 | Toolflow 通过率 | 回答通过率 | 综合通过率 | LLM 分数均值 | 标准差 |
|---|---:|---:|---:|---:|---:|
| 同日多航线回看 | 75% | 0% | 0% | 0.817 | 0.037 |
| 跨 Session 边界 | 25% | 25% | 25% | 0.708 | 0.097 |
| 多票上下文切换 | 100% | 0% | 0% | 0.742 | 0.089 |

重要解释：

- 三条场景当时都处于 `review`，正式 `official` 场景数为 0，不能把该报告解释为正式发布基准。
- 报告确实捕获了关键要求遗漏、工具流程波动、上下文和记忆错误，证明了评测链路有诊断价值。
- 结果也显示“分数看似不低但阻断项失败”的情况，说明不能只看平均分。
- 旧 Runner 采用“所有 Run 均通过才算场景通过”，对随机 Agent 很严格；是否适合新平台需要重新决策。

机械验证发现历史资产存在一处漂移：

```text
scenario_101 sessions 目录有 run-00..run-05
stability.json 只汇总 run-00..run-03
```

`lint_assets.py` 能正确报告该错误，证明 Asset Lint 有价值；同时说明旧产物不能不经治理直接转为正式 Golden Dataset。

## 5. 可复用性分类

### 5.1 直接继承领域设计

以下内容已经经过实践，应作为新项目的默认起点：

- Scenario、Expected Toolflow、Expected Answer、Real Session、Run、Stability、Benchmark Set 的分层。
- 过程评估和结果评估职责分离。
- `official / review / skipped` 的资产与报告分区。
- 真实高风险场景优先于纯合成假场景。
- 小场景验证单条规则、少量长 Session 验证上下文组合风险。
- 所有结果保留 `scenario_id / turn_id / run_id / trace_id` 以便追溯。
- 多次 Run 评估随机性，而不是单次运行即判定稳定。
- Asset Lint 检查 Scenario、Expected、Session 和 Report 漂移。
- 评测旁路于生产 Agent 主链路，不直接修改 Agent 行为。

### 5.2 抽象后复用代码或交互

| 资产 | 可复用部分 | 必须抽象的耦合 |
|---|---|---|
| `collect_real_session.py` | 多轮驱动、事件采集、并发 Run、Trace 输出 | `create_deep_agent()`、LangChain 事件、eyun 配置、固定身份、内部服务和数据库 |
| `evaluate_toolflow.py` | 轨迹匹配、禁止调用、结构化 Diff | agentevals 数据格式、业务 Matcher 注册方式 |
| `evaluate_llm_answer.py` | 逐轮前缀上下文 + Session Judge、结构化结果、失败即显式报错 | 项目 LLM 工厂、Judge 与被测模型可能同源、缺少校准和版本身份 |
| `run_benchmark_set.py` | 批量评估、Official/Review、稳定性聚合、机器退出码 | 本地文件目录、串行 Judge、缺少跨版本 Run 模型 |
| `lint_assets.py` | 资产一致性规则和单写者思想 | 仅支持当前文件 Schema 和路径结构 |
| Web 控制台 | 启动采集/评估、SSE 日志、进度恢复、报告入口 | 无用户认证、无 RBAC、任务仅内存、文件直接写回 |
| HTML Dashboard | 场景/Run/Turn 下钻、稳定性和失败展示 | 数据模型固定、生成器体量较大、缺少跨版本比较 |
| 模型评测脚本 | HTTP/SSE 黑盒接入、时延与 Token、模型横向比较 | 业务规则写死、只测首轮、依赖本地服务和环境修改 |

### 5.3 仅作为历史证据

以下内容不应直接成为新平台通用实现：

- 运价业务专用港口、箱型和航线 Matcher。
- 固定测试账号、企业、请求头和开发环境地址。
- 旧 Agent 的 3 条上下文场景及 28 条模型用例本身；它们只能成为首个迁移样本。
- 历史 Dashboard 和 Run 结果；它们是能力与问题证据，不是当前基线。
- 以特定 Sonnet 输出为 100 分参照的启发式模型评分。

## 6. 与当前目标的覆盖映射

图例：`已验证` 表示旧资产已通过代码和产物证明；`部分` 表示只覆盖单一 Agent 或简化场景；`缺失` 表示未发现对应能力。

| 当前关注点 | 旧资产覆盖 | 说明 |
|---|---|---|
| 对话问答 Agent | 已验证 | 多轮回答和 Session 级 LLM Judge 已落地 |
| 工具执行 Agent | 已验证 | Tool 调用、参数、轮次、禁止调用和 Diff 已落地 |
| 同一版本重复稳定性 | 已验证 | 多 Run 通过率、均值、标准差和区间已落地 |
| 通用 Agent 接入 | 部分 | 模型脚本支持 HTTP/SSE 黑盒；Session Collector 直接绑定 eyun DeepAgents |
| 自动生成候选用例 | 缺失 | 旧 PRD 明确首期不做大规模自动生成 |
| 人工审核 | 部分 | 有 Review/Official 状态和“转正式”动作，但无完整审核记录和多人责任链 |
| Baseline/Candidate 比较 | 缺失 | 旧 Run 是同一条件的重复样本；Agent 或 Expected 变化后要求 Reset，不保存跨版本对照 |
| CI 发布门禁 | 部分 | Runner 有机器退出码和 `--fail-on-review`，但未接入 CI 或发布系统 |
| 灰度/线上评估 | 缺失 | 旧设计明确以离线评测为主 |
| Trace 与失败定位 | 已验证 | 可定位到 Scenario、Run、Turn、Tool 和回答检查项 |
| Agent/Prompt/Tool 版本追溯 | 缺失 | Trace 仅保存模型覆盖值和运行时间，未绑定 Git、Prompt、Tool、环境清单 |
| 成本和时延 | 部分 | 模型评测脚本有时延和可选 Token 代理；Session 评测未纳入统一指标 |
| 环境与副作用隔离 | 部分 | 避免聊天持久化并 Mock 一个审计写入，但仍访问开发数据库和内部服务 |
| 权限、审计、敏感数据治理 | 缺失 | Web 仅绑定 localhost，无登录/RBAC；文件资产无正式审计模型 |
| 资产持久化与共享 | 部分 | 文件 Schema 清晰，但后续 Benchmark 改为 local-only，团队级资产存储未解决 |

## 7. 关键缺口与风险

### 7.1 通用性缺口

旧 `adapter.py` 的名称容易误导：它只把本地 Tool Trace 转换成 agentevals 接受的 OpenAI-style messages，不是“任意 Agent 接入 Adapter”。

新平台若继承旧设计，必须把下列边界拆开：

```text
Agent 执行接入
≠ Trace 事件标准化
≠ 评测器输入转换
```

### 7.2 回归模型缺口

旧系统主要回答“同一 Agent 在固定 Expected 下是否稳定”，还不能完整回答：

```text
批准的 Baseline Agent 版本
        vs
待发布 Candidate Agent 版本
```

Agent、Skill、Prompt、Tool 或 Expected 变化后清空旧 Run 的规则，会破坏跨版本历史比较。新平台必须明确哪些变化形成新版本、哪些结果仍可比较、何时禁止混比。

### 7.3 Judge 可信度缺口

- 默认 Judge 取项目主模型，可能与被测模型同源。
- 没有人工校准集、一致率或误报率统计。
- 评分阈值固定在资产中，但没有阈值批准与版本治理。
- 同一次 Session 逐轮调用 Judge 再做整段调用，成本和时延随场景长度、Run 数线性增长。
- “全部 Run 必须通过”的门槛没有统计置信度依据。

### 7.4 数据与安全风险

历史 Collector 源码包含硬编码测试身份、内部请求上下文和访问凭证；进一步只读扫描还发现仓库已跟踪的环境文件包含 Langfuse、LLM、SPOT、标准化服务等多类密钥变量。本文不复制任何具体凭证值。

处置要求：

- Git 历史中的全部真实凭证不得迁移到新项目；
- 需要由 eyun 项目责任方立即确认相关凭证已经失效或完成轮换；
- 测试身份和凭证必须由受控配置或短期凭证提供；
- Trace 中的用户输入、工具参数和输出预览必须有脱敏与保留策略；
- “不写聊天历史”不能作为“无业务副作用”的充分证明。

### 7.5 工程可靠性风险

- 未发现针对 `agent_session_eval` Runner 和 Web API 的自动化测试。
- Web 任务状态主要保存在进程内，服务重启后无法恢复执行状态。
- 文件系统是事实源，但后续把 Benchmark 整体设为 local-only，存在资产无法协作和丢失的风险。
- 旧资产 Lint 已出现 Run 与 Stability 不一致，说明必须把一致性检查纳入每次正式运行。
- 控制台无认证和 RBAC；虽然只监听 `127.0.0.1`，不能直接作为企业共享服务部署。

## 8. 对当前 MVP 定位的影响

基于既有资产，当前项目不应定位为“重新做一个 Agent 评分脚本”，而应定位为：

> **把已经验证过的单 Agent、文件级评测闭环，抽象成可接入多种 Agent、可治理测试资产、可稳定比较版本退化的企业内部评测产品。**

由此得到五项需求影响：

1. 首个迁移对象应包含 `eyun_assist_bot`，用旧场景和结果验证新平台没有丢失既有能力。
2. MVP 必须同时验证一种黑盒接入和一种可采集 Tool Trace 的深度接入，否则无法证明覆盖两类 Agent。
3. “重复结果稳定”不能只展示标准差，必须先定义稳定性的判定对象和可接受范围。
4. 自动用例生成应建立在现有能力清单、Scenario Schema、历史失败和 Trace 之上，而不是只读取角色 Prompt 凭空生成。
5. 旧 Runner/UI 可以作为原型和迁移来源，但新平台不能继续把业务身份、Agent 工厂、Matcher 和环境副作用写死在核心逻辑中。

## 9. 继承决策

### 已确认

1. `eyun_assist_bot` 是 MVP 第一个迁移和验收 Agent。
2. MVP 继承“工具过程评估与回答结果评估分离”的原则。
3. 新平台从旧 Benchmark Schema 演进，保留已验证概念并补齐平台字段，不完全重做，也不原样照搬。
4. 历史硬编码测试凭证及已跟踪环境文件中的全部真实凭证按已暴露凭证处理，由 eyun 项目责任方立即确认失效或完成轮换。

### 待确认

1. 多模型黑盒脚本纳入 MVP，还是只作为后续性能/成本评测参考。
2. 第二个代表性 Agent 的选择及其通用接入验收标准。
3. 历史凭证处置结果的记录人和闭环证据。

## 10. 验证证据

本次只读验证结果：

- Git 历史确认 Session 评测专用分支、后续增强提交和多模型评测分支均存在。
- Python `compileall`：旧 Runner、最新 Runner 和 Web 源码均通过语法编译。
- `lint_assets.py`：3 条场景中 2 条通过，1 条因 Stability 与 Session Run 列表不一致失败。
- 历史 Dashboard：可在浏览器中离线打开，场景和稳定性内容可见，无控制台错误。
- 未运行真实 Agent：旧实现依赖项目环境、内部数据库、内部服务和 LLM 凭证；在安全与副作用边界确认前不应执行。
