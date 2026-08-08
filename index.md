# Knowledge Forest 索引

> 按类别组织的 wiki 页面目录。每页格式：`[[page-name]] —— 一行摘要`。

---

## Entities

[[boris-cherny]] —— Claude Code 之父，分享 13 个高效使用技巧
[[celery]] —— Python 分布式任务队列，支持异步任务和定时任务
[[claude-code]] —— Anthropic 的终端 AI 编程助手
[[cursor]] —— AI 驱动的代码编辑器，VS Code 分支
[[docker]] —— 容器化平台，支持镜像、容器、Compose 编排
[[fastapi]] —— 现代、高性能的 Python Web 框架
[[fastapi-users]] —— FastAPI 的用户认证库，支持 OAuth/JWT
[[hermes-agent]] —— NousResearch 开源的 Python AI Agent 框架，强调生产级错误恢复与可扩展工具体系
[[moneyprinterturbo]] —— AI 一键生成高清短视频
[[obsidian]] —— 本地优先的知识管理工具，支持双向链接
[[pi-coding-agent]] —— 开源 LLM Agent Harness，覆盖 Runtime、Provider、Tool、Extension 与 Session
[[redis]] —— 内存数据结构存储，用作缓存和消息队列
[[remotion]] —— React 编程式视频创作库
[[yt-dlp]] —— 视频下载与字幕提取工具，支持 1800+ 站点

## Concepts

[[agent-memory-system]] —— Agent 记忆系统：user/feedback/project/reference 四类结构化记忆
[[ai-video-generation]] —— AI 视频生成：文本/图片到视频的自动化工作流
[[async-tasks]] —— 异步任务：Celery 架构与适用场景
[[claude-code-skills]] —— Claude Code Skills：通过 SKILL.md 扩展 AI 助手能力
[[wechat-article-ingestion]] —— 微信文章批量摄取：从合集页面自动化下载到 raw/assets
[[containerization]] —— 容器化：Docker 与虚拟机的对比及微服务部署
[[jwt-authentication]] —— JWT 认证：结构与原理，及与 Session 认证对比
[[knowledge-graph]] —— 知识图谱：实体-关系模型，与向量检索对比
[[load-testing]] —— 负载测试：Locust 并发模拟与性能指标
[[mcp]] —— MCP (Model Context Protocol)：标准化工具调用协议
[[multi-agent-collaboration]] —— 多 Agent 协作：Team Mode、子 Agent 与角色分工
[[rag]] —— RAG (Retrieval-Augmented Generation)：检索增强生成流程
[[react-pattern]] —— ReAct：推理-行动交替的 Agent 执行模式
[[vibe-coding]] —— Vibe Coding：信任 AI、减少微观管理的编程范式

### Agent 架构

[[agent-trace]] —— Agent 执行过程的结构化可观测记录（Trace/Span/Event）
[[agent-runtime-event-stream]] —— Agent、Runtime Turn、消息与工具执行的类型化事件协议
[[agent-turn]] —— 区分 Business/User Turn 与 Runtime/Model Turn 的双层回合语义
[[agent-memory-system]] —— Agent 记忆系统：内置 MemoryStore + 外部 MemoryProvider 插件
[[agent-security]] —— Agent 安全防护：分层纵深防御与 fail-closed 原则
[[agent-tool-system]] —— Agent 工具系统：发现、注册、schema 编排与调度分发
[[agent-extension-system]] —— Agent 插件系统：能力注册、ResourceLoader 与生命周期 Hook
[[context-management]] —— 上下文管理：把 token 当作受限资源主动经营
[[context-compaction]] —— 上下文压缩：时机、目标、切点、方法和增量更新的五维决策模型
[[context-compaction-checkpoint]] —— 上下文压缩检查点：追加摘要节点，投影时替代旧消息
[[error-handling]] —— 错误处理：结构化分类器与六类恢复动作
[[initialization-environment]] —— 初始化与环境：profile、配置合并、沙箱后端
[[orchestration-loop]] —— 编排循环：LLM 推理与工具执行的迭代主控制流
[[parallel-interruptible-async-agent]] —— 并行和可打断的异步 Agent：事件路由、可取消 Turn 与异步任务管理
[[output-parsing]] —— 输出解析：多 provider 响应归一化与防御性修复
[[provider-protocol-normalization]] —— Provider 厂商身份与 API wire format 的双向协议归一化
[[prompt-building-for-agents]] —— Agent 的 Prompt 构建：洋葱式 system prompt 组装
[[state-management]] —— 状态管理：运行时与持久化状态的双轨生命周期、并发控制和恢复
[[session-persistence]] —— 会话持久化：事务型存储、Append-only 日志、恢复与 Schema 演进
[[append-only-session-persistence]] —— 只追加会话持久化：用 JSONL 事件日志增量写入与恢复
[[session-entry-tree]] —— 会话条目树：用 parentId 和 leaf 保存可分支历史
[[session-context-projection]] —— 会话上下文投影：从当前 leaf 生成模型可见 messages
[[session-branching-and-forking]] —— 会话分支与派生：移动 leaf 或复制路径创建独立 Session
[[tool-call-lifecycle]] —— ToolCall 从模型意图到校验、授权、执行和 ToolResult 回填
[[sub-agent-orchestration]] —— 子 Agent 编排：受限临时实例的任务外包
[[validation-loop]] —— 验证循环：LLM 决策到实际执行的多层把关

## Sources

[[ai-agent-book-async-agent-experiment]] —— AI Agent Book 实验 4-5：并行和可打断的异步 Agent
[[agent-skills-design]] —— Agent Skills 实战：把设计文档写成 Skill
[[aicomicbuilder]] —— AIComicBuilder：AI 驱动的动画漫画生成器
[[aidc-aipixelle-video]] —— AIDC AI Pixelle Video：全自动短视频引擎
[[aitoearn]] —— AiToEarn：AI 变现项目
[[auto-video-slicing]] —— B站/YouTube 视频自动切片工具分析
[[autoclip]] —— AutoClip：智能高光提取与二创剪辑工具
[[boris-cherny-tips]] —— Boris Cherny 分享的 13 个 Claude Code 高效使用技巧
[[claude-code-essential-projects]] —— Claude Code 必备的三个开源项目
[[claude-code-gstack]] —— Claude Code + gstack 多 Agent 协作实战
[[claude-code-memory-system]] —— Claude Code 记忆系统源码万字解析
[[claudian-baoyu-modelscope]] —— Claudian + baoyu-skills + ModelScope 免费 AI 绘图
[[fastapi-celery-redis]] —— FastAPI + Celery + Redis 异步任务实战
[[fastapi-docker-compose-deploy]] —— FastAPI 从 Dockerfile 到 Compose 容器化部署
[[fastapi-locust-load-test]] —— FastAPI Locust 压力测试与优化
[[fastapi-users-auth-transport-strategy-1]] —— FastAPI-Users 认证后端揭秘（上）
[[fastapi-users-auth-transport-strategy-2]] —— FastAPI-Users 认证后端揭秘（下）
[[fastapi-users-concepts]] —— FastAPI-Users 核心概念与快速上手
[[fastapi-users-project-template]] —— FastAPI-Users 实战项目模板构建
[[fastapi-users-schemas-routers]] —— FastAPI-Users Schemas 与 Routers
[[fastapi-users-user-model]] —— FastAPI-Users 用户模型与数据库集成
[[fastapi-users-usermanager]] —— FastAPI-Users UserManager 深入解析
[[fireworks-tech-graph]] —— 用自然语言生成工业级架构图的 Claude Code Skill
[[flycut-caption]] —— Flycut：AI 语音识别视频字幕编辑 React 组件
[[gitnexus]] —— GitNexus：浏览器端代码知识图谱生成器
[[hermes-agent-setup]] —— Hermes Agent 本地启动与项目结构
[[hermes-agent-orchestration-loop]] —— Hermes Agent 编排循环调研
[[hermes-agent-tool-system]] —— Hermes Agent 工具系统调研
[[hermes-agent-memory-system]] —— Hermes Agent 记忆系统调研
[[hermes-agent-context-management]] —— Hermes Agent 上下文管理调研
[[hermes-agent-prompt-building]] —— Hermes Agent Prompt 构建调研
[[hermes-agent-output-parsing]] —— Hermes Agent 输出解析调研
[[hermes-agent-state-management]] —— Hermes Agent 状态管理调研
[[hermes-agent-error-handling]] —— Hermes Agent 错误处理调研
[[hermes-agent-security]] —— Hermes Agent 安全防护调研
[[hermes-agent-validation-loop]] —— Hermes Agent 验证循环调研
[[hermes-agent-sub-agent-orchestration]] —— Hermes Agent 子 Agent 编排调研
[[hermes-agent-initialization-environment]] —— Hermes Agent 初始化与环境调研
[[nanobot-framework-analysis]] —— nanobot 12 维度综合调研
[[openclaw-framework-analysis]] —— OpenClaw 12 维度综合调研
[[opencode-framework-analysis]] —— OpenCode 12 维度综合调研
[[hyper-extract]] —— Hyper-Extract：一条命令将杂乱文档转为知识图谱
[[hyperframes]] —— Hyperframes：HTML 渲染视频的 Agent 工具
[[last30days-skill]] —— last30days-cn：搜索中国互联网 8 大平台近期内容
[[moneyprinterturbo]] —— MoneyPrinterTurbo：AI 一键生成高清短视频
[[obsidian-knowledge-base]] —— 个人如何用 Obsidian 搭建本地知识库
[[open-source-short-drama-projects]] —— 35+ 开源视频短剧项目合集
[[opencode-remotion]] —— 用 OpenCode 玩转 Remotion 动画视频
[[openmaic]] —— OpenMAIC：多 Agent 沉浸式互动课堂
[[openmontage]] —— OpenMontage 项目
[[openscreen]] —— OpenScreen：免费开源录屏神器
[[panniantong-agent]] —— Agent-Reach：给 AI Agent 一键装上互联网能力
[[pi-agent-runtime-event-flow]] —— Pi 01：Agent Runtime 的类型化事件流
[[pi-agent-loop-and-turn]] —— Pi 02：Business Turn、Runtime Turn 与双层 Agent loop
[[pi-provider-unified-event-protocol]] —— Pi 03：Provider 抽象与统一流式事件协议
[[pi-tool-call-lifecycle]] —— Pi 04：ToolCall 的查找、校验、授权、执行与结果回填
[[pi-tool-registration-and-extension]] —— Pi 05：工具 Registry、模型暴露、权限与 Extension
[[pi-custom-tools-and-extension]] —— Pi 06：customTools 与 Extension 两种工具注册入口
[[pi-session-system]] —— Pi Session 系统：Entry 树、上下文投影、分支、压缩与 JSONL 恢复
[[treesearch-retrieval]] —— TreeSearch：让文档检索回归本质
[[understand-anything-mcp]] —— Understand-Anything：代码库转交互式知识图谱
[[vimax-agentic-video]] —— ViMax：Agentic 视频生成（导演+编剧+制片人）

## Synthesis

[[ai-memory-vs-human-km]] —— AI 记忆系统与 Obsidian 知识管理的趋同与分野
[[ai-video-media-landscape]] —— AI 视频/媒体创作领域全景：生成→编辑→控制→分发的能力分层与工作流组合
[[claude-code-agent-ecosystem-landscape]] —— Claude Code/AI Agent 辅助开发生态全景：从终端助手到工程团队的演进
[[fastapi-ecosystem-landscape]] —— FastAPI 技术栈知识全景图：分层结构、学习路径与实战组合
[[knowledge-graph-tools-comparison]] —— Hyper-Extract/GitNexus/Understand-Anything 选型对比
[[multi-agent-architecture-comparison]] —— gstack/Hermes/OpenMAIC/Agent-Reach 架构对比
[[rag-knowledge-retrieval-landscape]] —— RAG 与知识检索领域全景：从向量检索到知识网络的演进
[[knowledge-base-audit-and-flywheel]] —— 知识库现状诊断与知识飞轮设计：从资料库到复利系统的闭环
[[agent-framework-12-dimensions-comparison]] —— 四大开源 Agent 框架 12 维度对比：Hermes / nanobot / OpenClaw / OpenCode
[[agent-concept-map]] —— Agent 系统四级概念地图：模块 → 能力 → 方法 → 技术
[[agent-session-storage-and-context-views]] —— Agent 会话事实存储、Session 视图与模型上下文的三层架构
[[pi-agent-runtime-architecture]] —— Pi 01–07 Runtime、Provider、Tool、Extension 与 Session 的端到端架构

## Drafts

（当前没有进行中的 draft 项目）

## Queries

[[what-are-turn-and-trace-in-agents]] —— Agent 中的 Turn 和 Trace 是什么？

