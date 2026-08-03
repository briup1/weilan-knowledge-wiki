# Knowledge Forest 日志

## [2026-05-18] ingest | Superpowers 完全指南：AI 编程代理技能框架与四工具横向对比

**操作**: 入库（ingest）
**源文件数**: 1
**新增 source 页面**: 1
- `wiki/sources/superpowers-guide.md` —— Superpowers 安装教程、四框架横向对比、七阶段工作流详解

**新增 entity 页面**: 4
- `wiki/entities/superpowers.md` —— AI 编程代理技能框架（146k Star，TDD 强制工作流）
- `wiki/entities/bmad-method.md` —— 文档驱动敏捷框架（44k Star，12+ 专业角色）
- `wiki/entities/openspec.md` —— 规格驱动开发框架（39k Star，轻量需求规格层）
- `wiki/entities/openharness.md` —— AI 代理运行引擎（8.6k Star，支持国内模型）

**更新 synthesis 页面**: 1
- `wiki/synthesis/claude-code-agent-ecosystem-landscape.md` —— 新增 AI 编程代理框架选型小节，纳入 Superpowers/BMAD/OpenSpec/OpenHarness 四款工具

**更新 concept 页面**: 1
- `wiki/concepts/claude-code-skills.md` —— 新增 Superpowers 横向对比表格与叠加使用建议

**更新 entity 页面**: 1
- `wiki/entities/claude-code.md` —— 生态插件章节新增 Superpowers 上架信息

## [2026-05-18] ingest | 7篇文章入库：Codex/Warp/Hermes/Harness/Agent Teams/OMC/LLM Wiki

**操作**: 批量入库（ingest）
**源文件数**: 7
**新增 source 页面**: 7
- `wiki/sources/ai-knowledge-evolution.md` —— NotebookLM 七层架构与 LLM Wiki 演进
- `wiki/sources/agent-teams-tmux-worktrees.md` —— tmux + worktrees 跑 4 个 Claude 并行交付
- `wiki/sources/harness-engineering-guide.md` —— Harness Engineering 完全指南
- `wiki/sources/hermes-agent-guide.md` —— Hermes Agent 完全新手指南
- `wiki/sources/openai-codex-guide.md` —— OpenAI Codex 完全新手指南
- `wiki/sources/warp-guide.md` —— Warp 完全指南
- `wiki/sources/oh-my-claudecode-guide.md` —— oh-my-claudecode 深度实战

**新增 entity 页面**: 4
- `wiki/entities/codex.md` —— OpenAI Codex（CLI + 桌面端）
- `wiki/entities/warp.md` —— Warp 智能终端
- `wiki/entities/oh-my-claudecode.md` —— OMC 多 Agent 编排插件
- `wiki/entities/hermes-agent.md` —— Hermes 持久化自主 Agent

**新增 concept 页面**: 1
- `wiki/concepts/llm-wiki.md` —— Karpathy 提出的知识沉淀范式

**更新 entity 页面**: 1
- `wiki/entities/claude-code.md` —— 新增 Agent Teams、Harness Engineering、OMC 集成章节

**更新 concept 页面**: 3
- `wiki/concepts/agent-harness.md` —— 新增 Harness Engineering 四要素、3-Agent 架构、Sprint Contract
- `wiki/concepts/multi-agent-collaboration.md` —— 新增 Agent Teams 工程模式、OMC 19 Agent 体系
- `wiki/concepts/rag.md` —— 新增 NotebookLM 七层架构、AI 知识库三阶段演进

**新增 synthesis 页面**: 1
- `wiki/synthesis/ai-terminal-tools-comparison.md` —— 四工具七维对比矩阵 + 选型决策树 + 推荐组合方案

**更新 synthesis 页面**: 1
- `wiki/synthesis/claude-code-agent-ecosystem-landscape.md` —— 扩展终端层、IDE 层、常驻 Agent 层，新增 Claude Code vs Codex/Warp/Hermes 对比

**关键发现**:
- 终端 AI 工具正在分化：Claude Code（深度编码）↔ Codex（生态+桌面）↔ Warp（终端体验）↔ Hermes（常驻运维），四者占据不同 niche
- LLM Wiki 是 RAG 的进化方向：从「查询时组装」到「预编译知识」
- Harness Engineering 四要素（Prompt 结构 + 状态文件 + 工具配置 + 验证机制）使 Agent 产出可靠性提升 2-3 倍
- OMC 的 19 Agent + 3 级模型路由代表了「编排层」的崛起

---

## [2026-05-08] thread | 引入知识脉络（Thread）页面类型

**操作**: 架构升级 + 内容创建
**新增页面类型**: `type: thread`，存储于 `wiki/threads/`
**新增 thread 页面**: 2
- `wiki/threads/rag-thread.md` —— RAG 技术栈 5 模块技能树（Chunking→Embedding→Retrieval→Generation→Evaluation），含 15+ 面试题
- `wiki/threads/agent-harness-thread.md` —— Agent Harness 12 模块技能树，含 20+ 面试题

**架构变更**:
- `CLAUDE.md`: 目录结构增加 `threads/`，type 枚举增加 `thread`，入库流程增加"知识脉络（纵向）"方向
- `index.md`: 增加 "Threads" 分类
- 反向链接: `rag.md` / `agent-harness.md` 增加"相关脉络"小节
- 交叉引用: `rag-knowledge-retrieval-landscape.md` / `claude-code-agent-ecosystem-landscape.md` 增加"技能树脉络"小节

**Thread 格式规范**:
- 模块关系图（Mermaid）+ 模块速查表
- 每模块包含：核心概念、具体实现表格、面试题/关注问题、相关来源
- 学习路径建议 + 推荐实践项目
- 版本记录（可追加更新）

---

## [2026-05-08] ingest | 万字讲透Agent Harness的十二大模块

**操作**: 入库（ingest）
**源文件**: raw/万字讲透Agent Harness的十二大模块：2026 年 AI 工程化最核心的基础设施.md
**新增页面**: 4
- `wiki/sources/agent-harness-anatomy.md`（source 页面）
- `wiki/concepts/agent-harness.md`（核心概念：Agent Harness）
- `wiki/entities/langgraph.md`（实体：LangGraph 框架）
- `wiki/entities/openai-agents-sdk.md`（实体：OpenAI Agents SDK）
**更新页面**: 4
- `wiki/entities/claude-code.md`（添加 Harness 架构章节）
- `wiki/concepts/agent-memory-system.md`（添加 Harness 三层记忆架构 + 8 优先级层级）
- `wiki/concepts/multi-agent-collaboration.md`（添加子 Agent 编排模式 + Token 经济学）
- `wiki/synthesis/claude-code-agent-ecosystem-landscape.md`（添加 Harness 层视角）

**关键发现**:
- Agent Harness 是 2026 年 AI 工程领域最核心的新概念——"如果你不是模型，你就是 Harness"
- LangChain TerminalBench 2.0：同一模型通过 Harness 优化，排名从 30+ 跃升至第 5
- 生态分化为薄 Harness（Claude Code）vs 厚 Harness（LangGraph）两条路线
- "脚手架原则"（为移除而构建）提供了两者的调和框架

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
