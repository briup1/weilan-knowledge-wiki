# Knowledge Forest 日志

## [2026-08-02] synthesis | 创建 Agent 系统概念地图

**操作**: 创建 `wiki/synthesis/agent-concept-map.md`，用四级 Mermaid 思维导图呈现 Agent 系统概念体系。

**完成项**:
- 新建 `wiki/synthesis/agent-concept-map.md`，覆盖 10 个一级模块、17 个二级概念、四级深度。
- Mermaid 图中二级节点链接到对应 `wiki/concepts/` 页面。
- 更新 `index.md`，在 Synthesis 分类下加入 `[[agent-concept-map]]`。

**规范遵循**:
- 页面 `sources` 字段列出 17 个引用的 concept 页面。
- 所有 `[[page-name]]` 均指向已存在的 wiki 页面。

## [2026-08-02] draft published | Agent 系统入门书稿发布归档

**操作**: 将 `drafts/agent-book-beginner/` 标记为 `published` 并移出 `drafts/`。

**完成项**:
- 更新 `raw/archive/drafts/agent-book-beginner/README.md`：状态从 `writing` 改为 `published`。
- 将 `drafts/agent-book-beginner/` 移动到 `raw/archive/drafts/agent-book-beginner/`。
- 更新 `index.md`：Drafts 分类清空，当前无进行中的 draft 项目。

**规范遵循**:
- 按 `CLAUDE.md` 约定，`published` 项目已在 30 天内移出 `drafts/`，归档至 `raw/archive/drafts/<project>/`。

## [2026-07-27] policy | 制定 drafts/ 生命周期治理规范

**操作**: 制定并落地轻量约定型的 `drafts/` 治理规范。

**完成项**:
- 更新 `CLAUDE.md`：明确 `drafts/` 目录结构、README 模板、状态标签、与 wiki 的关系、完成后的去向。
- 更新 `drafts/agent-book-beginner/README.md`：补充状态标签 `writing`、当前进度、来源说明。
- 删除 `drafts/agent-book-beginner/research/`：原始调研资料已与 `raw/research/agent-frameworks/` 重复。
- 更新 `index.md`：Drafts 分类改用 Markdown 链接 `[agent-book-beginner](drafts/agent-book-beginner/README.md)`（原计划使用 wiki-link `[[agent-book-beginner]]`，但审查发现该链接指向 `wiki/` 中不存在的页面，故恢复为 Markdown 链接）。

**规范要点**:
- `drafts/` 是 wiki 的下游产物，不是原始资料存储层。
- 每个 draft 项目必须有 `README.md` 并标注五种状态之一：`planning` / `writing` / `review` / `published` / `archived`。
- `published` 或 `archived` 项目应在 30 天内移出 `drafts/`，归档到 `raw/archive/drafts/<project>/`。

## [2026-07-26] query | Agent 中的 Turn 和 Trace 是什么

**问题**: Agent 中的 Turn 和 Trace 分别指什么？它们有什么关系？

**操作**: 查询并综合了现有调研资料，创建了 2 个新 concept 页面和 1 个 query 页面：
- 新增 `wiki/concepts/agent-turn.md` —— Turn 的定义、生命周期、四框架实现
- 新增 `wiki/concepts/agent-trace.md` —— Trace 的 Span 结构、Agent 特殊性、设计建议
- 新增 `wiki/queries/what-are-turn-and-trace-in-agents.md` —— 问答归档
- 更新 `index.md` 加入新页面

**结论摘要**: 
- **Turn** = 用户输入到 Agent 最终响应的完整业务交互回合，是预算、延迟、状态持久化的边界。
- **Trace** = Agent 一次执行的结构化可观测记录，通常以树状 Span 呈现（LLM Call、Tool Call、Validation 等）。
- 一个 Session 含多个 Turn，一个 Turn 通常对应一个顶层 Trace。

## [2026-07-26] lint | 修复 ai-video-media-landscape.md 中的死链

**问题**: `wiki/synthesis/ai-video-media-landscape.md` 存在 8 个带尾部反斜杠的 wiki-link（如 `[[aidc-aipixelle-video\|...]]`），导致链接失效。

**修复**: 将 `\|` 替换为标准 `|`，并更新 `updated` 日期。

**验证**: 全站死链检查通过，无失效链接。

## [2026-07-26] ingest | 完成 agent-frameworks 全部 49 份调研笔记入库（方案 A）

**操作**: 将 nanobot / OpenClaw / OpenCode 三个框架的 37 份维度调研笔记按「框架级 source + 12 个 concept 多框架对比 + 1 个 synthesis」策略入库。

**新增 source 页面**: 3 个
- `wiki/sources/nanobot-framework-analysis.md` —— 综合 12 份 nanobot 维度调研
- `wiki/sources/openclaw-framework-analysis.md` —— 综合 12 份 OpenClaw 维度调研
- `wiki/sources/opencode-framework-analysis.md` —— 综合 12 份 OpenCode 维度调研

**新增 synthesis 页面**: 1 个
- `wiki/synthesis/agent-framework-12-dimensions-comparison.md` —— 四大框架 12 维度总对比表 + 选型建议 + 对书稿写作的启示

**更新的 concept 页面**: 12 个
所有 concept 页面新增「四框架实现对比」小节：
- `orchestration-loop`
- `agent-tool-system`
- `agent-memory-system`
- `context-management`
- `prompt-building-for-agents`
- `output-parsing`
- `state-management`
- `error-handling`
- `agent-security`
- `validation-loop`
- `sub-agent-orchestration`
- `initialization-environment`

**源文件归档**: 37 个文件从 `raw/research/agent-frameworks/` 移动到 `raw/archive/research/agent-frameworks/`

**状态**: `raw/research/agent-frameworks/` 已空；全部 49 个 research 文件已标记为「已摄取」

**索引更新**: `index.md` 新增 3 个 source 条目和 1 个 synthesis 条目

## [2026-07-26] ingest | Hermes Agent 12 维度调研笔记入库

**操作**: 将 `raw/research/agent-frameworks/` 中 Hermes Agent 的 12 份维度调研笔记编译进 wiki。

**源文件**: 12 个，从 `raw/research/agent-frameworks/` 移动到 `raw/archive/research/agent-frameworks/`

**新增 source 页面**: 12 个
- `wiki/sources/hermes-agent-orchestration-loop.md`
- `wiki/sources/hermes-agent-tool-system.md`
- `wiki/sources/hermes-agent-memory-system.md`
- `wiki/sources/hermes-agent-context-management.md`
- `wiki/sources/hermes-agent-prompt-building.md`
- `wiki/sources/hermes-agent-output-parsing.md`
- `wiki/sources/hermes-agent-state-management.md`
- `wiki/sources/hermes-agent-error-handling.md`
- `wiki/sources/hermes-agent-security.md`
- `wiki/sources/hermes-agent-validation-loop.md`
- `wiki/sources/hermes-agent-sub-agent-orchestration.md`
- `wiki/sources/hermes-agent-initialization-environment.md`

**新增 entity 页面**: 1 个
- `wiki/entities/hermes-agent.md` —— Hermes Agent 实体总览

**新增 concept 页面**: 11 个
- `wiki/concepts/orchestration-loop.md`
- `wiki/concepts/agent-tool-system.md`
- `wiki/concepts/context-management.md`
- `wiki/concepts/prompt-building-for-agents.md`
- `wiki/concepts/output-parsing.md`
- `wiki/concepts/state-management.md`
- `wiki/concepts/error-handling.md`
- `wiki/concepts/agent-security.md`
- `wiki/concepts/validation-loop.md`
- `wiki/concepts/sub-agent-orchestration.md`
- `wiki/concepts/initialization-environment.md`

**更新 concept 页面**: 2 个
- `wiki/concepts/agent-memory-system.md` —— 新增 Hermes 记忆系统视角对比
- `wiki/concepts/multi-agent-collaboration.md` —— 新增 Hermes `delegate_task` 子 Agent 编排

**更新 synthesis 页面**: 1 个
- `wiki/synthesis/multi-agent-architecture-comparison.md` —— 细化 Hermes 协作模式与机制

**更新索引**: `index.md` 新增 Entities、Concepts、Sources 条目

**待处理**: nanobot / OpenClaw / OpenCode / comparison 共 37 个文件仍待摄取

## [2026-07-26] integrate | 整合 Harness_agent_docs：书稿与调研文档迁入 drafts/

**操作**: 将 `/home/weilan/workdir/selfcode/Harness_agent_docs` 的内容整合进本仓库，统一知识资产管理。

**完成项**:
- 创建 `drafts/agent-book-beginner/` 目录结构：
  - `chapters/`：17 个书稿章节（含 3 个部分引言）
  - `research/`：第一阶段调研文档
    - `hermes_agent/`：12 个维度分析
    - `nanobot/`：12 个维度分析
    - `openclaw/`：12 个维度分析
    - `opencode/`：12 个维度分析
    - `comparison/`：横向对比文档
- 撰写 `drafts/agent-book-beginner/README.md`：明确项目定位、目录结构、与 wiki 的关系、写作约定
- 将 49 个调研 markdown 文件复制到 `raw/research/agent-frameworks/`，作为 wiki 的潜在原始来源
- 更新 `CLAUDE.md`：新增「半成品输出：drafts/」一节，区分 wiki 与 drafts 的生命周期
- 更新 `index.md`：新增 Drafts 分类，加入 `[[agent-book-beginner]]`

**待办**:
- 将 `raw/research/agent-frameworks/` 中的 49 份调研笔记分批入库为 `wiki/sources/`
- 基于这些 source 页面更新/创建 entity、concept、synthesis 页面
- 书稿写作时优先引用 wiki synthesis，而非直接引用 research/ 中的调研笔记
- 保持 `Harness_agent_docs` 原仓库不动（作为备份），后续确认整合无误后再决定是否归档

## [2026-07-26] fix | 修复 wiki 基础设施：README、queries/、raw/assets/、skill 同步

**操作**: 统一 wiki 入口、补齐缺失目录、对齐 skill 与 CLAUDE.md 规范。

**完成项**:
- 撰写 `README.md`：说明仓库定位、目录结构、工作流、快速开始
- 创建 `wiki/queries/` 目录，使 query 归档机制可落地
- 创建 `raw/assets/` 目录，恢复「待处理源文件」缓冲区
- 重写 `.claude/skills/llm-ingest/SKILL.md`：目录结构与 frontmatter 与 `CLAUDE.md` 对齐
- 重写 `.claude/skills/llm-ingest/references/ingest-guide.md`：统一为 sources/entities/concepts/synthesis/queries 五类
- 更新 `.claude/skills/llm-ingest/scripts/ingest.py`：`init` 命令创建正确的目录和模板
- 在 `CLAUDE.md` 新增「技能与脚本约定」一节，明确 skill 必须与主规范同步

**待办**:
- 创建 `drafts/` 并把 `Harness_agent_docs` 整合进来（下一步）
- 运行一次 lint，处理可能的死链和孤立页面
- 将过往高质量问答归档为 `wiki/queries/` 页面

## [2026-07-25] lint + synthesis | 知识库现状诊断与飞轮设计

**操作**: 对仓库整体进行健康检查并输出综合建议
**新增 synthesis**: [[knowledge-base-audit-and-flywheel]]
**新增 concept**: [[wechat-article-ingestion]]
**新增工具**: `scripts/ingest/download_wechat_album.py`
**更新 index.md**: 加入新增 synthesis 与 concept 页面
**发现的问题**:
- `llm-ingest` skill 与 `CLAUDE.md` 的目录结构/frontmatter 不一致
- `wiki/queries/` 目录缺失，query 归档机制未落地
- `raw/assets/` 缺失，缺少“待处理源文件”缓冲区
- `README.md` 为空，仓库入口无说明
- 缺少轻量检索层，70+ 页面后纯浏览效率下降
**建议行动**:
1. 本周：统一 skill 与 CLAUDE.md、创建 queries/ 和 raw/assets/、写 README
2. 本月：把高质量问答归档为 query 页面、建立固定摄取流程、运行一次 lint
3. 本季度：将 synthesis 改写成公开文章、添加 tags/backlinks 索引、引入外部反馈

## [2026-04-20] ingest | 首批39篇文章入库

**操作**: 批量入库（ingest）
**源文件数**: 39
**创建 source 页面**: 39
**创建 entity 页面**: 12
**创建 concept 页面**: 12
**总 wiki 页面**: 63

**源文件主题分布**:
- FastAPI 技术栈（10篇）: Docker/Celery/Redis/Locust + FastAPI-Users 系列教程
- AI 视频/内容生成（12篇）: MoneyPrinterTurbo、AutoClip、ViMax、Remotion 等
- Claude Code / Agent / 开发工具（10篇）: gstack、Skills、MCP、记忆系统等
- 知识管理 / 多 Agent / 其他（7篇）: Obsidian、Hyper-Extract、GitNexus、TreeSearch 等

**创建的核心实体**: FastAPI、FastAPI-Users、Celery、Redis、Docker、Claude Code、Boris Cherny、Cursor、Obsidian、MoneyPrinterTurbo、yt-dlp、Remotion

**创建的核心概念**: 容器化、异步任务、JWT认证、负载测试、Vibe Coding、Agent记忆系统、MCP、Claude Code Skills、多Agent协作、RAG、知识图谱、AI视频生成

**并行处理**: 4个agent分主题并行处理source页面 → 3个agent分主题并行创建entity/concept页面

## [2026-04-20] synthesis | 首批4个跨领域综合页面

**操作**: 扫描现有知识体系，创建跨领域 synthesis 页面
**新增 synthesis**: 4
**总 wiki 页面**: 67

**创建的 synthesis 页面**:
- [[knowledge-graph-tools-comparison]] —— Hyper-Extract（NLP文档抽取）、GitNexus（浏览器端代码图谱）、Understand-Anything（Claude Skill交互式代码图谱）的选型对比
- [[ai-memory-vs-human-km]] —— Claude Code 文件式记忆系统与 Obsidian LLM Wiki 在架构趋同（本地Markdown/YAML frontmatter/索引机制）与维护分野（AI自动维护 vs 人类策展）的对比
- [[multi-agent-architecture-comparison]] —— gstack（28角色工程团队）、Hermes（Skills插件化）、OpenMAIC（教育剧本编排）、Agent-Reach（单Agent能力扩展）四种多Agent设计哲学对比
- [[ai-video-tools-comparison]] —— MoneyPrinterTurbo/ViMax/AutoClip/Remotion/AIDC 覆盖「一键生成→Agentic导演→高光提取→编程式控制」的完整光谱

**工作流修改**: CLAUDE.md 入库流程中新增第5步「跨领域综合（Synthesis）—— 此步骤不可省略」，明确产出量视情况而定，但不能跳过审视过程。

## [2026-04-20] synthesis | AI 视频/媒体创作领域全景

**操作**: 读取 10 篇 AI 视频/媒体相关 source 页面及 entity/concept 页面，创建领域内知识全景
**新增 synthesis**: [[ai-video-media-landscape]]

**覆盖范围**:
- 内容生成层: MoneyPrinterTurbo / AIDC-AIPixelle / ViMax / AIComicBuilder
- 内容编辑层: AutoClip / flycut-caption / auto-video-slicing
- 内容控制层: Remotion / Hyperframes
- 内容分发/短剧层: open-source-short-drama-projects

**关键发现**:
- AI 视频工具正经历「单点自动化 → 模块化 Pipeline → 多 Agent 协作」三阶段演进
- ViMax 的多 Agent 导演制预示竞争焦点从「模型质量」转向「Agent 协作流程可靠性」
- 能力光谱从「一键生成（最低干预）」到「编程控制（完全可控）」形成完整连续体

## [2026-04-20] synthesis | Claude Code/Agent 生态领域全景

**操作**: 读取 11 篇 Claude Code/Agent 相关 source 页面及 entity/concept 页面，创建领域内知识全景
**新增 synthesis**: [[claude-code-agent-ecosystem-landscape]]

**覆盖范围**:
- 终端层: Claude Code
- IDE 层: Cursor
- 技能扩展层: Skills / Hermes / fireworks-tech-graph / last30days-skill
- 协议层: MCP
- 多 Agent 协作层: gstack / OpenMAIC
- 能力扩展层: Agent-Reach
- 记忆层: Agent 记忆系统
- 方法论层: Vibe Coding

**关键发现**:
- 生态演进四阶段: 单个 AI 助手 → 能力扩展(Skills+MCP) → 记忆与连续性 → 多 Agent 协作
- Claude Code vs Cursor 是互补关系（终端做自动化/批量重构，IDE 做日常编码）
- Skills 解决「做什么」，MCP 解决「怎么连」，两者是「角色定义」与「工具协议」的分层
- Boris Cherny 的 13 个技巧恰好映射到四个演进阶段的实践要点

## [2026-04-20] synthesis | 工作流定位调整

**操作**: 将 synthesis 的定位从「跨领域分析对比」扩展为「跨来源的综合」，明确领域内知识全景为优先方向
**修改文件**: CLAUDE.md

**核心变化**:
- synthesis 不再只关注「跨领域对比」，更应关注「领域内整合」
- 优先产出: 把同一领域的多个来源编织成有结构、有层次、有演进脉络的知识全景图
- 次优先产出: 跨领域分析对比（工具选型、架构冲突、隐性关联、演进判断）
- 目标: 让读者打开 synthesis 页面就能一眼看清整个领域的全貌，而非散落在几十个独立页面中的碎片

## [2026-04-20] lint | synthesis 可视化增强

**操作**: 为全部 8 个 synthesis 页面增加 Mermaid 流程图、目录结构图、架构图等可视化元素
**增强页面**: 8

**新增可视化元素分布**:
- `fastapi-ecosystem-landscape`: Mermaid 架构依赖图 + Mermaid 学习路径图 + 生产项目目录结构
- `rag-knowledge-retrieval-landscape`: Mermaid 技术演进图 + Mermaid 能力叠加图 + 理想系统组件结构 + 五维能力定位
- `ai-video-media-landscape`: Mermaid 能力光谱图 + 4 条工作流流程图 + AI 视频项目目录结构 + Mermaid Agentic 演进图
- `claude-code-agent-ecosystem-landscape`: Mermaid 8 层生态架构图 + Mermaid 四阶段演进图 + Skills vs MCP 关系图 + `.claude/` 目录结构
- `ai-video-tools-comparison`: Mermaid 综合工作流图 + quadrantChart 能力矩阵
- `multi-agent-architecture-comparison`: Mermaid 四方架构对比图 + Mermaid 选型决策树
- `ai-memory-vs-human-km`: Mermaid 双架构对比图 + Mermaid 数据流互补图
- `knowledge-graph-tools-comparison`: Mermaid 三工具 Pipeline 对比图 + Mermaid 选型决策树

**设计原则**: 保留原有文字内容，在对应小节插入可视化；Mermaid subgraph + 颜色区分确保 Obsidian 可渲染；流程图替代大段叙述，目录树替代列表堆砌

## [2026-04-20] synthesis | FastAPI 技术栈领域全景

**操作**: 读取 10 篇 FastAPI 相关 source 页面及 8 个 entity/concept 页面，创建跨领域综合页面
**新增 synthesis**: [[fastapi-ecosystem-landscape]]

**覆盖范围**:
- 核心层: FastAPI 框架
- 认证层: fastapi-users（Transport + Strategy + UserManager + Schemas + Routers + User Model）
- 异步任务层: Celery + Redis
- 部署层: Docker + Docker Compose
- 测试层: Locust 负载测试

**关键发现**:
- 认证越来越插件化：2 种 Transport × 3 种 Strategy = 6 种可组合认证后端
- 安全策略从「无状态优先」回退到「可控优先」：生产模板推荐 DatabaseStrategy 而非 JWTStrategy
- 异步从框架层渗透到架构层：API → Worker → Broker → 数据库全面异步化
- 压测成为交付闭环的一部分：与每次大版本更新绑定的常态化工程实践

## [2026-04-20] synthesis | RAG/知识检索领域全景

**操作**: 创建跨领域 synthesis 页面
**新增 synthesis**: [[rag-knowledge-retrieval-landscape]]
**覆盖来源**: [[treesearch-retrieval]]、[[hyper-extract]]、[[gitnexus]]、[[understand-anything-mcp]]、[[obsidian-knowledge-base]]
**关联概念**: [[rag]]、[[knowledge-graph]]、[[agent-memory-system]]

**页面结构**:
- 领域概览（检索→抽取→图谱→管理四个层次）
- 技术演进脉络（传统RAG→NLP文档抽取→代码知识图谱→人类策展知识管理）
- 五方案对比矩阵（TreeSearch/Hyper-Extract/GitNexus/Understand-Anything/Obsidian）
- 三种组合方案（开发者场景/研究者场景/协作场景）
- 从RAG到知识网络的三大演进趋势（隐式→显式、静态→动态、自动化→人机协作）
