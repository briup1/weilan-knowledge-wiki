---
type: concept
created: 2026-04-20
updated: 2026-07-26
sources: [claude-code-memory-system, hermes-agent-memory-system, hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-memory, memory-system, claude-code, context-management, ai-agent]
---

# Agent 记忆系统

AI Agent 用于持久化存储和检索上下文信息的机制，使 Agent 能够跨会话记住用户偏好、项目背景和交互历史，从而提供更加个性化和连贯的辅助体验。

## 定义

Agent 记忆系统是一套结构化的信息存储与检索架构，允许 AI Agent 在多次交互之间保持上下文连续性。与仅依赖当前会话窗口的短期记忆不同，记忆系统通过文件化、索引化的方式将关键信息持久化到本地存储，在后续会话中按需注入到系统提示中。

## 核心原理

### 四类结构化记忆

Claude Code 的记忆系统将信息分为四个维度：

- **User（用户画像）**：用户的角色、技术背景、知识水平、偏好设置。例如「我是 Python 后端开发者，偏好 FastAPI 而非 Django」。
- **Feedback（工作指导）**：用户对 AI 输出的纠正和确认。例如「不要用 list comprehension 处理大数据量，改用生成器」。
- **Project（项目背景）**：当前项目的架构决策、谁在做什么、截止日期、技术约束。例如「本项目使用 PostgreSQL + Redis，部署在 AWS ECS」。
- **Reference（外部资源指针）**：指向外部系统的链接和访问方式。例如「API 文档在 https://docs.example.com，用环境变量 API_KEY 访问」。

### 文件式存储结构

记忆完全落地在本地目录，不依赖云端数据库：

```
~/.claude/projects/<project>/memory/
├── MEMORY.md              # 索引文件：每行一条记忆引用
├── user-profile.md        # 用户画像
├── feedback/              # 工作指导片段
├── project/               # 项目背景片段
└── reference/             # 外部资源指针
```

团队记忆存放在 `team/` 子目录中，实现个人与团队记忆的分层隔离。

### MEMORY.md 索引机制

索引文件采用简洁的列表格式，每行一条：

```markdown
- [Title](file.md) — one-line hook
```

索引有 200 行 / 25KB 的上限，超过时触发修剪。记忆文件本身使用 YAML frontmatter（name、description、type）+ Markdown 内容。

### 记忆生命周期

1. **启动预加载**：Agent 启动时将记忆文件加载到 readFileState 缓存。
2. **动态注入**：每次查询前通过 `getUserContext` 将相关记忆注入系统提示。
3. **相关性检索**：`findRelevantMemories` 扫描最多 200 个记忆文件，通过 Sonnet 侧边查询选择最多 5 条相关记忆。
4. **提取与更新**：查询结束时通过 `extractMemories` 触发记忆提取，写入文件并更新索引。
5. **夜间整理**：`/dream` 命令四阶段（Orient→Gather→Consolidate→Prune）蒸馏 KAIROS 日志为结构化记忆。

### KAIROS 日志模式

长生命周期会话的 append-only 每日日志，记录用户更正、偏好、项目背景和外部系统指引。日志存放在 `logs/YYYY/MM/YYYY-MM-DD.md`，夜间通过 `/dream` 蒸馏为结构化记忆片段。

### 会话记忆（Session Memory）

`~/.claude/session-memory.md` 用于对话压缩（compaction），包含 10 个章节：当前状态、任务说明、文件和函数、工作流程、错误和修正、代码库文档、经验总结、关键结果、工作记录。当 token 数或工具调用数超过阈值时触发压缩。

## 记忆维护策略

- **冲突处理**：最新胜出、特异性优先、合并去重。
- **新鲜度检测**：超过 1 天的记忆添加 `system-reminder` 标签，提示 Agent 验证时效性。
- **过时信息验证**：定期扫描记忆文件，对可能过时的项目背景进行重新确认。

## 与其他记忆方案的对比

| 维度 | Claude Code 文件式记忆 | 传统数据库存储 | 纯提示注入 |
|------|----------------------|--------------|-----------|
| 隐私 | 完全本地，不上云 | 依赖服务端 | 无持久化 |
| 可移植性 | 随项目目录迁移 | 需导出导入 | 无 |
| 团队共享 | 通过 git 共享 team/ 目录 | 需额外权限系统 | 无 |
| 检索精度 | Sonnet 相关性选择 Top 5 | 向量检索 | 无 |
| 维护成本 | 低（文件 + 索引） | 中（数据库运维） | 无 |

## 适用场景

- **长期项目协作**：Agent 记住项目架构和团队约定，避免每次会话重复交代背景。
- **个性化辅助**：根据用户技术背景和偏好调整回答风格和代码风格。
- **团队知识沉淀**：将团队规范、API 使用模式、常见陷阱固化为共享记忆。
- **复杂工作流追踪**：跨会话追踪多步骤任务的进度和中间结果。

## Hermes Agent 的记忆系统视角

[[hermes-agent]] 提供了另一种工程化的记忆系统实现，可与 Claude Code 的文件式记忆形成对比：

| 维度 | Claude Code | Hermes Agent |
|---|---|---|
| 存储形态 | 本地 Markdown 文件 + 索引 | 内置 MEMORY.md/USER.md + 外部 MemoryProvider 插件 |
| 跨会话稳定性 | 文件即持久化 | SQLite + 外部后端（Honcho/Mem0 等） |
| 注入位置 | system prompt | 内置记忆进 system prompt；外部 recall 进 user message |
| prefix cache 策略 | 不特别强调 | frozen snapshot：本会话内 system prompt 不变 |
| 扩展方式 | 文件 + git 共享 | MemoryProvider ABC 插件接口 |
| 失败处理 | 本地文件为主 | 外部 provider 失败不阻塞主流程 |

Hermes 的关键设计：
- **frozen snapshot**：`load_from_disk()` 一次性把 MEMORY/USER 渲染到 `_system_prompt_snapshot`，mid-session 写入落盘但不刷新 prompt，保护 prefix cache。
- **外部 recall 注入 user message**：通过 `<memory-context>` fence 拼到当前 user 消息末尾，不污染持久化 messages。
- **单 external provider 约束**：防止工具名冲突和 schema 膨胀。

## 四框架记忆系统对比

| 维度 | Claude Code | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|---|
| 存储形态 | 本地 Markdown 文件 + 索引 | 内置 MEMORY.md/USER.md + 外部 MemoryProvider | MEMORY.md + HISTORY.md 双层文件 | Markdown 文件为唯一事实来源，SQLite 仅索引 | SQLite + Drizzle ORM 三层表结构 |
| 跨会话稳定性 | 文件即持久化 | SQLite + 外部后端 | JSONL 会话 + 文件记忆 | 文件 + SQLite 索引 | SQLite |
| 注入位置 | system prompt | 内置进 system；外部 recall 进 user message | `# Memory` 区块进 system prompt | system prompt | system prompt |
| 压缩/固化策略 | KAIROS 日志 + `/dream` 四阶段蒸馏 | frozen snapshot 保护 prefix cache | LLM 驱动 `save_memory` 固化 | 专门 compaction agent | Prune → Compaction → Overflow 三级 |
| 检索方式 | Sonnet 侧边查询 Top 5 | FTS5 / 外部 provider | HISTORY.md 可 grep；MEMORY.md 结构化 | 向量 + BM25 hybrid | SQL 查询 + compaction 摘要 |
| 扩展方式 | 文件 + git 共享 | MemoryProvider ABC 插件 | 文件化 | 插件 + provider | Plugin hook |
| 失败处理 | 本地文件为主 | 外部 provider 失败不阻塞 | 连续失败 3 次降级为 raw archive | 自动降级到 FTS-only | — |

### nanobot

nanobot 采用 **MEMORY.md（长期事实）+ HISTORY.md（可检索日志）** 的双层文件结构。与 Claude Code 类似，都是文件式记忆，但职责更明确：MEMORY.md 存结构化事实，HISTORY.md 存时间线日志。固化由 LLM 通过 `save_memory` 工具主动完成，以用户轮次为最小单元，连续失败 3 次后降级为原始归档。

### OpenClaw

OpenClaw 选择 **Markdown 文件为唯一事实来源，SQLite 仅作索引**。这一设计与 Claude Code 的文件式记忆理念一致，但增加了混合检索（向量 + BM25）和原子化重索引。当 embedding provider 缺失或失败时，自动降级到 FTS-only，保证记忆系统不因配置问题而瘫痪。

### OpenCode

OpenCode 采用 **SQLite + Drizzle ORM 的三层表结构**（Session → Message → Part），更适合 IDE 场景中对历史消息的高效查询和级联删除。压缩策略分为 Prune、Compaction、Overflow 三级，并用专门的 compaction agent 生成结构化摘要。

## 相关来源

- [[claude-code-memory-system]] —— Claude Code 源码级记忆系统万字解析
- [[hermes-agent-memory-system]] —— Hermes Agent 记忆系统调研
- [[hermes-agent]] —— Hermes Agent 实体概述
