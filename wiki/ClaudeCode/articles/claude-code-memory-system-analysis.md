---
title: "Claude Code 源码阅读：万字解析记忆系统"
source: "https://mp.weixin.qq.com/s/QULcRMDebSbmIQJQ3nxKjQ"
created: 2026-04-16
category: "ClaudeCode"
tags: ["ClaudeCode", "type/concept", "Claude-Code", "Memory", "Agent", "Architecture"]
status: "archived"
references: "Archive/前沿重器85  Claude Code源码阅读：万字解析记忆系统.md"
---

> Claude Code 的记忆系统是一套**基于本地文件**的记忆系统，不依赖云端数据库，支持个人/团队/项目三层隔离。本文基于其开源的 TypeScript 第一版代码，从类型、格式到加载、提取、检索全流程进行拆解。

## 系统概况

### 代码结构

```
src/
├── memdir/                              # 记忆目录模块
│   ├── memdir.ts                        # 核心协调器，加载入口
│   ├── memoryScan.ts                    # 文件扫描器
│   ├── memoryTypes.ts                   # 类型定义与 Prompt 指令
│   ├── paths.ts                         # 路径解析
│   ├── teamMemPaths.ts                  # 团队记忆路径
│   ├── teamMemPrompts.ts                # 团队记忆 Prompt
│   ├── findRelevantMemories.ts          # 相关性检索
│   └── memoryAge.ts                     # 新鲜度检测
│
├── services/
│   ├── extractMemories/                 # 记忆提取服务
│   │   ├── extractMemories.ts           # 主服务，触发逻辑
│   │   └── prompts.ts                   # Prompt 构建
│   │
│   ├── autoDream/                       # 自动整理服务
│   │   ├── autoDream.ts                 # 主服务，三重门控
│   │   ├── consolidationPrompt.ts       # 四阶段整固 Prompt
│   │   ├── DreamTask.ts                 # 任务状态追踪
│   │   └── config.ts                    # 配置管理
│   │
│   └── SessionMemory/                   # 会话记忆模块
│       ├── sessionMemory.ts             # 主服务，阈值检测
│       ├── prompts.ts                   # 更新 Prompt
│       └── template.ts                  # 默认模板
│
└── screens/
    └── REPL.tsx                         # REPL 启动时的记忆加载
```

## 记忆的四种类型

记忆不再是统一的大锅饭，而是有明确的模块化定义，位于 `src/memdir/memoryTypes.ts` 的 `TYPES_SECTION_COMBINED` 中。

### 1. 用户记忆（user）

构建用户画像，理解"用户是谁"以及"如何最有效地帮助他们"。

```
user: I'm a data scientist investigating what logging we have in place
assistant: [saves user memory: user is a data scientist, currently focused on observability/logging]
```

### 2. 反馈记忆（feedback）

记录用户的工作指导，保持一致性和响应性。

```
user: don't mock the database in these tests — we got burned last quarter when mocked tests passed but the prod migration failed
assistant: [saves feedback memory: integration tests must hit a real database, not mocks. Reason: prior incident where mock/prod divergence masked a broken migration]
```

### 3. 项目记忆（project）

理解工作的背景和动机，把握更广泛的上下文。需要把相对日期转为绝对日期，快速衰减、敏捷更新。

```
user: we're freezing all non-critical merges after Thursday — mobile team is cutting a release branch
assistant: [saves project memory: merge freeze begins 2026-03-05 for mobile release cut. Flag any non-critical PR work scheduled after that date]
```

### 4. 参考记忆（reference）

存储外部系统的资源指针，只记忆查询方法，而不是内容本身。

```
user: check the Linear project "INGEST" if you want context on these tickets, that's where we track all pipeline bugs
assistant: [saves reference memory: pipeline bugs are tracked in Linear project "INGEST"]
```

### 不应保存的内容

`WHAT_NOT_TO_SAVE_SECTION` 明确排除了以下内容：

- 代码范式、规范、架构、文件路径或项目结构 —— 可通过读取当前项目状态获取。
- Git 历史记录、近期变更或修改人信息 —— `git log` / `git blame` 才是权威依据。
- 调试方案或修复方法 —— 修复逻辑体现在代码中。
- 任何已在 `CLAUDE.md` 文件中记录的内容。
- 临时任务细节：进行中的工作、临时状态、当前对话上下文。

## 记忆的存储格式

### 文件结构

```
~/.claude/
└── projects/
    └── <sanitized-project-root>/
        └── memory/
            ├── MEMORY.md              # 记忆索引文件（入口）
            ├── user_expertise_profile.md
            ├── integration_testing_database_policy.md
            └── team/                  # 团队记忆子目录（可选）
                ├── MEMORY.md
                ├── coding_standards.md
                └── api_design_principles.md
```

### 单条记忆的 frontmatter 格式

```markdown
---
name: {{记忆名称}}
description: {{一行描述 - 用于判断相关性}}
type: {{user|feedback|project|reference}}
---

{{记忆内容}}
```

### MEMORY.md 索引格式

- 无 frontmatter
- 每行一条：`- [Title](file.md) — one-line hook`
- 行数上限约 200 行，每行长度 < 150 字符
- 始终加载到系统提示中，超过 200 行会被截断

保存新记忆时采用**两步流程**：先写记忆文件，再在 `MEMORY.md` 中添加指针。

## KAIROS 日志模式

KAIROS 是 Claude Code 的助手模式，专为长生命周期会话设计。

### 日志路径

```
~/.claude/projects/<project-root>/memory/logs/YYYY/MM/YYYY-MM-DD.md
```

### 特点

- **append-only**（只追加）的日志流
- `/dream` 技能可以将日志蒸馏为 `MEMORY.md` 和主题文件
- 适用于长生命周期会话、高频交互场景
- 避免频繁更新主题文件导致的冲突

### 记录内容

- 用户的更正内容与偏好设置
- 与用户相关的基本信息、其角色或目标
- 无法从代码中推导得出的项目背景信息（截止日期、突发事件、决策及其理由）
- 外部系统的指引信息（数据面板、Linear 项目、Slack 频道）
- 用户明确要求记住的任何内容

### `/dream` 整理流程

| 阶段 | 动作 |
| --- | --- |
| Phase 1: Orient | 扫描日志目录 |
| Phase 2: Gather | 读取日志，提取关键信息 |
| Phase 3: Consolidate | 更新或新建记忆文件 |
| Phase 4: Prune | 更新 `MEMORY.md` 索引，可选删除已整理日志 |

## 会话记忆（Session Memory）

| 特性 | KAIROS Daily logs | Session Memory |
| --- | --- | --- |
| **作用域** | 项目级（跨会话持久化） | 会话级（当前会话临时） |
| **文件路径** | `memory/logs/YYYY/MM/YYYY-MM-DD.md` | `~/.claude/session-memory.md` |
| **持久性** | 永久保存 | 会话结束后不再更新 |
| **写入方式** | 模型主动追加 | 后台子代理定期更新（覆盖写入） |
| **触发时机** | 模型识别到值得记录的内容时 | 阈值触发（token 数 + 工具调用数） |
| **内容格式** | 时间戳 bullet points | 固定模板 10 个章节 |
| **主要用途** | 长期知识积累 | 支持对话压缩（compaction） |

Session Memory 模板包括：标题、当前状态、任务说明、文件和函数、工作流程、错误和修正、代码库和系统文档、经验总结、关键结果、工作记录。

## 核心流程

### 1. 加载

#### 启动时加载

在 `src/screens/REPL.tsx` 中，启动服务时预加载所有记忆文件到 `readFileState` 缓存。

#### 执行前加载

每次用户发起新查询前，`context.ts:getUserContext` 会重新读取记忆文件，将最新的 `MEMORY.md` 索引和记忆内容注入系统提示。

#### 注入流程

```
用户输入查询
  → REPL.tsx 并行获取上下文
    → getSystemPrompt()      // 构建基础系统提示
    → getUserContext()       // 加载记忆文件
    → getSystemContext()     // Git 状态等
  → memdir.ts:loadMemoryPrompt()
    → 检查 KAIROS 模式 → buildAssistantDailyLogPrompt()
    → 检查 TEAMMEM → buildCombinedMemoryPrompt()
    → 默认 → buildMemoryLines()
  → 最终组装 systemPrompt 并发送给 API
```

### 2. 提取

```
handleStopHooks
  → executeExtractMemories
    → runExtraction
      → 检查互斥性、节流、扫描现有记忆
      → 构建 Prompt
      → 执行分叉 agent（最多 5 轮）
        → 写入记忆文件 + 更新 MEMORY.md
```

#### 触发条件

- 仅在主线程查询或 SDK 调用时触发，子 agent 不触发
- 受特性门控 `feature('EXTRACT_MEMORIES')` 控制
- 满足特定轮数积累才会触发（节流）
- 用户可通过 `/memory save` 手动触发

#### 提取 agent 的约束

- **角色限定**：`You are now acting as the memory extraction subagent`
- **可用工具**：Read/Grep/Glob/只读 Bash/Edit/Write（仅限记忆目录）
- **轮数预算**：2 轮完成（第一轮并行读取，第二轮并行写入）
- **内容来源限制**：只能使用最近 ~N 条消息，禁止 grep 源码、执行 git 命令

### 3. `/dream` 自动整理

三重门控机制（按成本从低到高检查）：

1. **时间门控**：距离上次整理 >= `minHours`（默认 24 小时）
2. **扫描节流**：避免频繁扫描会话目录
3. **会话门控**：自上次以来有 >= `minSessions` 个新会话
4. **锁机制**：确保单进程执行

对比 `extractMemories` 与 `/dream`：

| 特性 | extractMemories | /dream |
| --- | --- | --- |
| **触发频率** | 每次查询结束 | 每天一次（+ 手动） |
| **作用范围** | 单次会话的最近 N 条消息 | 多个历史会话 + 全部记忆 |
| **执行时机** | 查询循环内（blocking） | 后台异步（non-blocking） |
| **处理深度** | 浅层提取（≤5 轮） | 深层整固（无硬性轮次限制） |
| **主要动作** | 创建新记忆 | 合并、删除、重构 |
| **用户可见性** | 简单通知 | 任务状态 + 进度追踪 |

### 4. 检索

```
用户输入查询
  → getRelevantMemoryAttachments()
    → 提取 Agent @mentions
    → 并行搜索多个目录
      → findRelevantMemories()
        → scanMemoryFiles()（最多 200 个）
        → filter(alreadySurfaced)
        → selectRelevantMemories() // Sonnet 侧边查询
      → readMemoriesForSurfacing()
        → 限制最多 5 个
        → 读取文件内容（带截断保护）
    → 注入到系统提示（relevant_memories attachment）
```

#### 相关性选择 Prompt 要点

- 仅根据**文件名与描述**选择明显有用的记忆（最多 5 个）。
- 若不确定是否有帮助，不要列入。
- 若记忆涉及近期使用工具的**警告、注意事项或已知问题**，即使工具正在使用，也要选择。
- 输出 JSON Schema：`{ selected_memories: [...] }`
- 后校验：只返回存在于原始列表中的文件名，防止幻觉。

## 记忆维护的挑战与处理

### 冲突处理

- **最新胜出策略**：针对同一事物状态冲突。
- **特异性优先**：更具体的记忆更有价值。
- **合并去重**：相似内容合并为一个文件。
- **明确适用范围**：看似冲突的记忆可能是适用范围不同。

### 信息过时

- 大于 1 天的记忆会添加 `<system-reminder>` 新鲜度标签。
- 过时处理流程：检测潜在过时 → 验证当前状态 → 判断是否需要更新 → 执行更新（更新/删除/标记 deprecated）→ 更新索引 → 记录遥测。

## 思考与启示

Claude Code 记忆系统的设计亮点：

- **分类拆解模式**：四种结构化记忆类型，职责清晰。
- **KAIROS 日志模式**：append-only 日志降低写冲突，夜间蒸馏减少实时开销。
- **边界约束**：明确什么不该记，避免记忆膨胀。
- **渐进式披露**：检索时先用索引做侧边查询，再读取完整内容。

可提升方向：

- 记忆 200 个上限是权宜之计，后续可借助更精细的搜索策略缩小范围。
- 纯本地文件存储虽安全，但在更多领域可探索云端/数据库存储方案。
- 记忆模式可进一步细分，尤其在 code 场景下做更精细的定制。
- 当前大量动作依赖大模型处理，在更精细的应用上，微调模型可能带来更高效率与上限。

---

## 来源与归档

- 原始素材：[Archive/前沿重器85  Claude Code源码阅读：万字解析记忆系统.md](../../../Archive/前沿重器85%20%20Claude%20Code源码阅读：万字解析记忆系统.md)
