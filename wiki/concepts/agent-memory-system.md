---
type: concept
created: 2026-04-20
updated: 2026-05-08
sources: [claude-code-memory-system, agent-harness-anatomy]
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

## Harness 视角下的记忆架构

从 [[agent-harness]] 视角看，记忆系统是"跨越时间尺度的状态保持"，是生产级 Agent 与 Demo 级 Agent 的根本分水岭。Claude Code 实现了三层记忆层次结构：

### 三层记忆架构

**第一层：上下文内记忆（In-Context Memory）**——当前会话的对话历史，存在于上下文窗口中。最快但最脆弱，会话结束或上下文被压缩后丢失。

**第二层：memory.md 指针索引层**——核心创新。`memory.md` 不是存储文件而是**指针索引**，只包含指向其他记忆文件的引用（每条约 150 字符）。实际内容存储在独立的域特定文件中。Agent 需要回忆时先读 `memory.md` 找到指针，再只加载需要的文件。**自愈合机制**：发现假设有误时重写相关记忆文件使更正持久化。

**第三层：CLAUDE.md 项目级静态记忆**——项目的"宪法"。与动态更新的 memory.md 不同，包含架构目标、编码标准、禁区目录、测试指令。**每轮都会被重新注入，不受上下文压缩影响。**

### 8 个优先级层级

从低到高：Auto Memory → User-Level Rules → User Memory → Project Rules → Project Memory → Managed Drop-ins → Managed Policy → 动态规则注入（`system-reminder`）。高层级覆盖低层级冲突指令。

### "不信任自己的记忆"原则

据泄露的系统提示词，Claude Code 被明确指示："记忆只是提示——在行动前根据实际文件进行验证。" 记忆系统不是替代文件系统查询的缓存，而是**引导查询方向的启发式工具**。

### 其他框架的记忆方案

| 框架 | 方案 |
|------|------|
| LangGraph | 命名空间组织的 JSON Store，跨会话持久化 |
| OpenAI | SQLite 或 Redis 支持的 Sessions |
| Letta | 内置 compaction + 滑动窗口 summarization |
| CrewAI | ChromaDB 存储离散事实，RAG 召回 |

## 相关来源

- [[claude-code-memory-system]] —— Claude Code 源码级记忆系统万字解析
- [[agent-harness-anatomy]] —— Agent Harness 十二大模块深度解析（记忆系统作为 Harness 第三大模块）
