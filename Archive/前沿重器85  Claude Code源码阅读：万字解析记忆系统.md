---
title: "前沿重器[85] | Claude Code源码阅读：万字解析记忆系统"
source: "https://mp.weixin.qq.com/s/QULcRMDebSbmIQJQ3nxKjQ"
author:
  - "[[机智的叉烧]]"
published:
created: 2026-04-06
description: "深度拆解 Claude Code 本地文件式记忆系统：四类结构化记忆 + KAIROS 日志 + 会话记忆分层设计，从存储、提取到检索全流程解析其长上下文实现逻辑。"
tags:
  - "clippings"
---
原创 机智的叉烧 2026-04-05 21:00:29

精确发文时间由壹伴提供

手机阅读

**前沿重器**

栏目主要给大家分享各种大厂、顶会的论文和分享，从中抽取关键精华的部分和大家分享，和大家一起把握前沿技术。具体介绍： [仓颉专项：飞机大炮我都会，利器心法我还有](http://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247485934&idx=1&sn=5b9d1379862da3682f3e75a4de7e9028&chksm=e8825170dff5d8666cdcff55a85bbc6d9ae432de9606129642f4611d754f45ddbfb765635355&scene=21#wechat_redirect) 。（算起来，专项启动已经是20年的事了！）

2024年文章合集最新发布！在这里： [再添近20万字-CS的陋室2024年文章合集更新](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247491870&idx=1&sn=b978e4fff9922c12fe43495f48f42831&scene=21#wechat_redirect)

往期回顾

- [前沿重器\[80\] | DeepTravel：滴滴的 RL Planning 落地实践](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247492188&idx=1&sn=9fc069e006978f79f36f530f2f3d3dd2&scene=21#wechat_redirect)
- [前沿重器\[81\] | Manus 如何用上下文工程释放大模型能力](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247492204&idx=1&sn=4cf7802268a37da7e6f9cccaeb3125aa&scene=21#wechat_redirect)
- [前沿重器\[82\] | 淘宝LREM——先思考再embeding](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247492216&idx=1&sn=8785ab39c25e4a29a5c8d32de484779b&scene=21#wechat_redirect)
- [前沿重器\[83\] | nanobot：万字长文解读OpenClaw平替项目源码](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247492266&idx=1&sn=779a071fdb30dc173eb5188b0df4c778&scene=21#wechat_redirect)
- [前沿重器\[84\] | QP-OneModel：一个大模型搞定所有 Query 理解任务](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247492274&idx=1&sn=a950ec4d21aec1cd3b5ceed88c8dc4f8&scene=21#wechat_redirect)

刚写完nanobot的源码阅读（ [前沿重器\[83\] | nanobot：万字长文解读OpenClaw平替项目源码](https://mp.weixin.qq.com/s?__biz=MzIzMzYwNzY2NQ==&mid=2247492266&idx=1&sn=779a071fdb30dc173eb5188b0df4c778&scene=21#wechat_redirect) ），近期claude code也有源码公开，一石激起千层浪，冷静下来，为了更好地进步，我们要珍惜这来之不易的机会，还是要多去研究和学习他的技术优势。

本次给大家分享的是Memory这部分，Agent系统内，长context下，Memory的维护非常重要，早在之前，我也有不少文章提过讲过Memory的有关技术，今天让我们来重点看看Memory这部分，claude code是怎么做的。

先说明，今天我给大家分享的依据是Claude code开源的第一版代码，即typescript的版本，并非后续有过修改的python版本，确保原汁原味，避免错漏。

目录

- 概况
- 记忆的类型和格式
- 核心流程
- 思考

开始之前有几个说明。

- 里面很多代码我是借助 AI 来阅读的，有些笔记也是 AI 生成的，大家注意鉴别。
- 这次的讲解，我会减少源码的粘贴，更多是讲逻辑和技巧，贴代码只是为了佐证逻辑。

## 概况

claude code的记忆系统，是一套基于文件的记忆系统，完全落地在本地目录，不依赖云端数据库，支持个人/团队/ 项目三层隔离，让 AI 可以长期保存用户偏好、项目规则、工作习惯、外部资源入口等关键信息，并在后续对话中自动召回使用。

涉及到记忆的部分，代码结构是这样的，除了内部的记忆的处理，还有外部触发，以及相关配置，大家关注的要就是记忆的部分，那看下面这些即可。

```
src/
├── memdir/                              # 记忆目录模块
│   ├── memdir.ts                        # 核心协调器，加载入口
│   ├── memoryScan.ts                    # 文件扫描器
│   ├── memoryTypes.ts                   #  类型定义与 Prompt 指令
│   ├── paths.ts                         #  路径解析
│   ├── teamMemPaths.ts                  # 团队记忆路径
│   ├── teamMemPrompts.ts                # 团队记忆 Prompt
│   ├── findRelevantMemories.ts          # 相关性检索
│   └── memoryAge.ts                     # 新鲜度检测
│
├── services/
│   ├── extractMemories/                 # 记忆提取服务（~35KB）
│   │   ├── extractMemories.ts           # 主服务，触发逻辑
│   │   └── prompts.ts                   # Prompt 构建
│   │
│   ├── autoDream/                       # 自动整理服务（~27KB）
│   │   ├── autoDream.ts                 # 主服务，三重门控
│   │   ├── consolidationPrompt.ts       # 四阶段整固 Prompt
│   │   ├── DreamTask.ts                 # 任务状态追踪
│   │   └── config.ts                    # 配置管理
│   │
│   └── SessionMemory/                   # 会话记忆模块（~18KB）
│       ├── sessionMemory.ts             # 主服务，阈值检测
│       ├── prompts.ts                   # 更新 Prompt
│       └── template.ts                  # 默认模板
│
└── screens/
    └── REPL.tsx                         # REPL 启动时的记忆加载
```

大家有个初步的概念即可，后面我会带着大家去看去了解的。

## 记忆的类型和格式

这一章主要是讲记忆的分类和格式，即最终存储的规范和模式，代码的意义只在于把内容转化为这些格式，都是逻辑代码，所以这一章我尽量少将代码，而是给例子，告诉大家记忆被存成什么样子了。

### 记忆的分类

在claude中，记忆不再是统一的大锅饭，而是有非常具体的模块化定义，这些定义都放在了这里 `src/memdir/memoryTypes.ts` ，记忆的定义则都在变量 `TYPES_SECTION_COMBINED` 里面，每一种记忆都会有名称、作用域、使用时机、使用方法、案例。

首先是用户记忆，构建用户画像，理解"用户是谁"以及"如何最有效地帮助他们"，需要记录用户的角色、偏好、职责或知识，而当任务需要基于用户的背景调整解释方式时，就会被拿来使用。下面是例子，记录了用户的身份、经历、近期关心的关注点等。

```
user: I'm a data scientist investigating what logging we have in place
assistant: [saves user memory: user is a data scientist, currently focused on observability/logging]

user: I've been writing Go for ten years but this is my first time touching the React side of this repo
assistant: [saves user memory: deep Go expertise, new to React and this project's frontend — frame frontend explanations in terms of backend analogues]
```

反馈记忆，记录用户的工作指导，保持一致性和响应性，这个记忆会在用户进行纠正、确认、验证任务执行过程的操作时进行记录，记录工作流程，成功失败的都会记录，同时也需要关注原因以及边界，甚至还包括那些“quieter confirmations”，我理解就是默认。

```
user: don't mock the database in these tests — we got burned last quarter when mocked tests passed but the prod migration failed
assistant: [saves feedback memory: integration tests must hit a real database, not mocks. Reason: prior incident where mock/prod divergence masked a broken migration]
```

项目记忆，目标是理解工作的背景和动机，把握更广泛的上下文，记录谁在做什么、为什么做、何时完成，还有截止日期、法律合规要求、利益相关者需求等，也及时发现正在进行的工作、目标、bug、事件，这里还有一些细节。

- 将相对日期转绝对日期。
- 记录动机。
- 快速衰减。这里是指，要随着项目进展，敏捷更新。
```
user: we're freezing all non-critical merges after Thursday — mobile team is cutting a release branch
assistant: [saves project memory: merge freeze begins 2026-03-05 for mobile release cut. Flag any non-critical PR work scheduled after that date]
```

最后是参考记忆。存储外部系统的资源指针，便于查找最新信息，如外部资源的路径、获取方式等，注意，此处只记忆查询方法，而不是内容本身。

```
user: check the Linear project "INGEST" if you want context on these tickets, that's where we track all pipeline bugs
assistant: [saves reference memory: pipeline bugs are tracked in Linear project "INGEST"]
```

除此以外，项目内还约束了，有些内容是不需要记忆的，这个记录在变量 `WHAT_NOT_TO_SAVE_SECTION` 里面，甚至还很贴心的给了理由。

- 代码范式、规范、架构、文件路径或项目结构 —— 这些均可通过读取当前项目状态获取。
- Git 历史记录、近期变更或修改人信息 —— `git log` / `git blame` 才是权威依据。
- 调试方案或修复方法 —— 修复逻辑体现在代码中，提交信息已包含上下文。
- 任何已在 CLAUDE.md 文件中记录的内容。
- 临时任务细节：进行中的工作、临时状态、当前对话上下文。

### 记忆的格式

前文有提到，claude code是一个基于文件的记忆结构，现在我们看看，内部记忆是以一个什么样的格式来进行保存的，一个基础的记忆，是这样的一个存储方式。

```
~/.claude/
└── projects/
    └── <sanitized-project-root>/
        └── memory/                    # 自动记忆目录
            ├── MEMORY.md              # 记忆索引文件（入口）
            ├── user_expertise_profile.md
            ├── integration_testing_database_policy.md
            ├── mobile_release_merge_freeze.md
            ├── pipeline_bug_tracking_linear_project.md
            └── team/                  # 团队记忆子目录（可选）
                ├── MEMORY.md
                ├── coding_standards.md
                └── api_design_principles.md
```

里面的 `user_expertise_profile.md` 就是一个记忆片段，他是一个markdown文件。他的存储结构，和大家熟知的 `SKILL.md` 非常接近。

```
---
name: {{记忆名称}}
description: {{一行描述 - 用于判断相关性}}
type: {{user|feedback|project|reference}}
---

{{记忆内容}}
```

我以用户记忆为例，给出一个具体的记忆片段。

```
---
name: user_expertise_profile
description: 用户的技术背景和专业知识画像
type: user
---

用户是数据科学家，专注于可观察性和日志分析领域。

**技术栈**:
- 深度 Go 语言专家（10 年经验）
- React 和前端开发新手（本项目首次接触）

**协作建议**:
- 解释前端概念时使用后端类比
- 在日志和监控相关任务中发挥其数据科学优势
```

这只是一份记忆片段，随着使用，这种记忆片段肯定会越来越多，肯定需要维护，尤其在实际对话过程，我们要有选择的“唤醒”记忆，而不是简单的把他们都放到模型里，于是，就需要构造索引，方便在对话过程中快速找到所需的记忆，并调取使用。

### 记忆索引

在每个记忆的根路径，有一个 `MEMORY.md` 文件，这便是记忆索引，是的，这部分充分证明了，此处并没有用什么数据库。

它内部每一行是就对记忆片段做一个简单的记录。

```
- [Title](file.md) — one-line hook
```
- 使用 Markdown 链接语法指向具体的记忆文件
- 破折号后跟一行描述（hook），概括该记忆的核心内容
- 无 frontmatter：索引本身不包含 YAML frontmatter

此处还有行数（200）、大小（25kb）、每行长度（<150字符）的约束。下面给出一个例子。

```
- [用户技术背景](user_expertise_profile.md) — 数据科学家，Go 专家，React 新手
- [测试策略偏好](testing_preferences.md) — 集成测试用真实 DB，不 mock
- [移动端发布冻结](mobile_release_merge_freeze.md) — 2026-03-05 起非关键合并冻结
- [管道 bug 追踪](pipeline_bug_tracking_linear_project.md) — Linear 项目 "INGEST"
- [API 延迟仪表板](grafana_api_latency_dashboard.md) — oncall 监控的关键指标
```

那么，他是如何维护，如何增删改的呢。他是每次保存新记忆时，都会自动更新，在 `src/services/extractMemories/prompts.ts` 内有提及。

```
## How to save memories

Saving a memory is a two-step process:

**Step 1** — write the memory to its own file using frontmatter format

**Step 2** — add a pointer to that file in \`MEMORY.md\`. 
\`MEMORY.md\` is an index, not a memory — each entry should be one line, 
under ~150 characters: \`- [Title](file.md) — one-line hook\`. 
It has no frontmatter. Never write memory content directly into \`MEMORY.md\`.

- \`MEMORY.md\` is always loaded into your system prompt — lines after 200 will be truncated
- Organize memory semantically by topic, not chronologically
- Update or remove memories that turn out to be wrong or outdated
- Do not write duplicate memories. First check if there is an existing memory you can update before writing a new one.
```

### KAIROS 日志模式

KAIROS 是 Claude Code 的助手模式（Assistant Mode），专为长生命周期会话设计。在这里会有一个日度的记忆。

```
**路径** (KAIROS 模式特有):
\`\`\`
~/.claude/
└── projects/
    └── <sanitized-project-root>/
        └── memory/
            └── logs/
                └── YYYY/
                    └── MM/
                        └── DD/
                            └── YYYY-MM-DD.md    # 每日日志文件
\`\`\`
```

他有如下特点。

- append-only（只追加）的日志流
- /dream 技能可以将日志蒸馏为 MEMORY.md 和主题文件
- 长生命周期会话、高频交互场景
- 避免频繁更新主题文件导致的冲突

他的实现在 `src/memdir/memdir.ts:327-370` ，函数 `buildAssistantDailyLogPrompt` ，从prompt来看，主要记录如下内容。

- 用户的更正内容与偏好设置。
- 与用户相关的基本信息、其角色或目标。
- 无法从代码中推导得出的项目背景信息（截止日期、突发事件、决策及其理由）。
- 外部系统的指引信息（数据面板、Linear 项目、Slack 频道）。
- 用户明确要求你记住的任何内容。

记录完以后，大概是下面这样的格式。

```
# 2026-04-01

- [10:30] User prefers using \`bun\` instead of \`npm\` for package management
- [14:15] Database migration failed due to missing index on \`users.email\` — added index in PR #123
- [16:45] User asked to remember: team uses Linear project "INGEST" for tracking pipeline bugs
- [18:20] Refactored auth middleware to use Redis sessions instead of JWT (compliance requirement)
```

这个模式我是挺喜欢的，像是一个速记的日志，他能很大程度避免频繁对上述结构化的记忆进行修改，把临时的修改降级为定时的修改（通过dream模式定期更新）。

完成流程如下。

```
\`\`\`
┌─────────────────────────────────────────┐
│         长会话进行中                     │
│                                         │
│  用户: 帮我修复这个 bug                  │
│  Claude: 正在分析...                    │
│  用户: 对了，记住我们用 bun 不用 npm     │
│  Claude: 好的，记录下来                  │
│         ↓                               │
│  FileWrite logs/2026/04/2026-04-02.md  │
│  "- [14:30] User prefers bun over npm"  │
│                                         │
│  ... 继续对话 ...                        │
│                                         │
│  用户: 数据库迁移失败了                  │
│  Claude: 看到错误了，修复中              │
│         ↓                               │
│  FileWrite logs/2026/04/2026-04-02.md  │
│  "- [16:45] DB migration failed..."     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         夜间 /dream 执行                 │
│                                         │
│  Phase 1: Orient                        │
│  → ls memory/logs/2026/04/              │
│  → 发现 2026-04-01.md, 2026-04-02.md   │
│                                         │
│  Phase 2: Gather                        │
│  → cat logs/2026/04/2026-04-02.md      │
│  → 提取: bun preference, DB migration   │
│                                         │
│  Phase 3: Consolidate                   │
│  → Update user_preferences.md           │
│  → Update project_context.md            │
│                                         │
│  Phase 4: Prune                         │
│  → Update MEMORY.md index               │
│  → (可选) 删除已整理的日志               │
└─────────────────────────────────────────┘
\`\`\`
```

### 会话记忆

上面基本都是有一定持续性，跨对话的记忆，大家当然别忘了最基础的会话记忆，聚焦于会话本身的长期和短期记忆。他和长期的4大记忆肯定不同，然而和KAIROS 日志还不太明显，我先给出他和KAIROS 日志的差异对比。

| 特性 | KAIROS Daily logs | Session Memory |
| --- | --- | --- |
| **作用域** | 项目级（跨会话持久化） | 会话级（当前会话临时） |
| **文件路径** | `~/.claude/projects/<git-root>/memory/logs/YYYY/MM/YYYY-MM-DD.md` | `~/.claude/session-memory.md` |
| **持久性** | ✅ 永久保存，/dream 整理后成为持久记忆 | ❌ 会话结束后不再更新，下次会话新建 |
| **写入方式** | 模型主动追加（append-only） | 后台子代理定期更新（覆盖写入） |
| **触发时机** | 模型识别到值得记录的内容时 | 阈值触发（token 数 + 工具调用数） |
| **内容格式** | 时间戳 bullet points（非结构化） | 固定模板 10 个章节（半结构化） |
| **主要用途** | 长期知识积累，夜间蒸馏为主题文件 | 支持对话压缩（compaction），维护当前上下文 |
| **整理机制** | /dream 夜间整理 → MEMORY.md + 主题文件 | 无整理，直接用于 compaction |
| **激活条件** | `feature('KAIROS') && getKairosActive()` | `feature('tengu_session_memory')` |
| **适用场景** | Agent SDK daemon、长期监控任务 | 所有长对话会话（无论是否 KAIROS） |

他的构造会相对比较简单一些。

- 触发。当上下文窗口超过阈值时，系统优先使用会话记忆进行压缩，构造Session Memory（ `~/.claude/session-memory.md` ）。
- 这个结构是存在模板的，包括标题、当前状态、任务说明、文件和函数、工作流程、错误和修正、代码库和系统文档、经验总结、关键结果、工作记录。
- 更新 `session-memory.md` 。

prompt内，大概是如下内容。

- 只根据用户真实对话内容更新会话笔记文件，不包含本指令、系统提示、CLAUDE.md、历史摘要等信息。
- 仅使用编辑工修改 `{{notesPath}}` 文件，一次性并行完成所有编辑，不调用其他工具，编辑完就停止。
- 关键文件格式内容。
- 必要的约束。
- 如单节内容控制在约 2000 token / 词 以内，超了就精简
	- 内容聚焦可执行、可复现的工作信息。
	- 必须更新 Current State，保证流程连贯。
	- 文件超过 12000 token 时必须压缩。

## 核心流程

上面主要讲的是记忆的类型和格式，是静态的存储，下面开始讲流程，记忆是怎么触发、提取、检索和更新的。

### 加载

#### 启动时加载

在 `src/screens/REPL.tsx` 里面（Read-Eval-Print Loop），启动服务的时候会初始化。

```
// 启动时预加载所有记忆文件到 readFileState 缓存
const memoryFiles = await getMemoryFiles()
for (const file of memoryFiles) {
  // 如果内容与磁盘不同（被截断/剥离 frontmatter）
  // 缓存原始磁盘字节，标记为部分视图
  readFileState.current.set(file.path, {
    content: file.contentDiffersFromDisk 
      ? file.rawContent ?? file.content 
      : file.content,
    timestamp: Date.now(),
    isPartialView: file.contentDiffersFromDisk
  })
}
```

这个 `getMemoryFiles` ，是 `src/utils/claudemd.ts` 内的工具函数，加载Memory文件的，把各类型的记忆和记忆索引都给加载到内存里。

```
export asyncfunction getMemoryFiles(includeExternal = false): Promise<MemoryFileInfo[]> {
const result: MemoryFileInfo[] = []

// 收集所有记忆源
if (isAutoMemoryEnabled()) {
    const { info: memdirEntry } = await safelyReadMemoryFileAsync(
      getAutoMemEntrypoint(),  // ~/.claude/projects/<path>/memory/MEMORY.md
      'AutoMem',
    )
    if (memdirEntry) result.push(memdirEntry)
  }

if (feature('TEAMMEM') && teamMemPaths!.isTeamMemoryEnabled()) {
    const { info: teamMemEntry } = await safelyReadMemoryFileAsync(
      teamMemPaths!.getTeamMemEntrypoint(),  // ~/.claude/team/memory/MEMORY.md
      'TeamMem',
    )
    if (teamMemEntry) result.push(teamMemEntry)
  }

return result
}
```

#### 执行前加载

在每次用户发起新查询之前，系统会重新读取记忆文件，将最新的 MEMORY.md 索引和记忆内容注入到系统提示中。这个触发是在 `context.ts:getUserContext` 内。

```
const getUserContext = defineMemoizedGetter(
'getUserContext',
async () => {
    const startTime = Date.now()
    
    // 禁用检查
    const shouldDisableClaudeMd =
      isEnvTruthy(process.env.CLAUDE_CODE_DISABLE_CLAUDE_MDS) ||
      (isBareMode() && getAdditionalDirectoriesForClaudeMd().length === 0)
    
    // 获取并过滤记忆文件
    const claudeMd = shouldDisableClaudeMd
      ? null
      : getClaudeMds(filterInjectedMemoryFiles(await getMemoryFiles()))
    
    // 缓存结果供后续使用
    setCachedClaudeMdContent(claudeMd || null)
    
    return {
      ...(claudeMd && { claudeMd }),
      currentDate: \`Today's date is ${getLocalISODate()}\`,
    }
  },
)
```

留意到，这里依旧会去跑一次 `getMemoryFiles` 。

这里对比一下启动前和执行前的加载有什么区别。

| 特性 | 启动时加载 | 运行时注入 |
| --- | --- | --- |
| **时机** | REPL 启动时一次性 | 每次查询前动态 |
| **目的** | 预加载到 readFileState 缓存 | 构建当次查询的 System Prompt |
| **频率** | 仅一次 | 每次用户输入后 |
| **数据来源** | 磁盘文件直接读取 | 可能从缓存读取 |
| **作用** | 为后续 Edit/Write 做准备 | 让 AI 看到最新记忆 |

主要是因为，记忆文件可能在会话期间被修改，而每次查询都是需要知道最新的记忆的，此时可以通过缓存机制平衡性能和实时性。

#### 注入

然后，我们看看整个记忆是怎么被注入到prompt内并被使用的，调用逻辑在这里。

```
用户输入查询
    ↓
REPL.tsx:2535 - 并行获取上下文
    ├── getSystemPrompt(...)          // 构建基础系统提示
    ├── getUserContext()              // 加载记忆文件
    └── getSystemContext()            // Git 状态等
    ↓
prompts.ts:495 - getSystemPrompt 内部
    systemPromptSection('memory', () => loadMemoryPrompt())
    ↓
memdir.ts:419 - loadMemoryPrompt() 此处生成记忆系统的使用指令（如何保存、四种类型、MEMORY.md 索引内容）
    ├── 检查 KAIROS 模式 → buildAssistantDailyLogPrompt()
    ├── 检查 TEAMMEM → buildCombinedMemoryPrompt()
    └── 默认 → buildMemoryLines().join('\n')
    ↓
memdir.ts:199 - buildMemoryLines()
    ├── 生成记忆指令（如何保存、四种类型、不应保存的内容）
    ├── buildSearchingPastContextSection(memoryDir)  ← 关键！
    │   └── 读取 MEMORY.md 索引文件
    │   └── 扫描最多 200 个记忆文件
    │   └── 格式化输出到 prompt
    └── 返回字符串数组
    ↓
systemPrompt.ts:115 - buildEffectiveSystemPrompt()
    asSystemPrompt([
      agentSystemPrompt || customSystemPrompt || defaultSystemPrompt,
      ...(appendSystemPrompt ? [appendSystemPrompt] : [])
    ])
    ↓
claude.ts:1358 - 最终组装
    systemPrompt = asSystemPrompt([
      getAttributionHeader(fingerprint),
      getCLISyspromptPrefix({...}),
      ...systemPrompt,  // ← 这里包含记忆内容
      ...(advisorModel ? [ADVISOR_TOOL_INSTRUCTIONS] : []),
      ...(injectChromeHere ? [CHROME_TOOL_SEARCH_INSTRUCTIONS] : []),
    ].filter(Boolean))
    ↓
claude.ts:1376 - 发送给 API
    const system = buildSystemPromptBlocks(systemPrompt, enablePromptCaching, {...})
```

最后的systemPrompt，就会有如下内容。

```
// systemPrompt 数组包含：
[
    baseSystemPrompt,           // 模型行为定义
    toolDefinitions,            // 工具定义
    loadMemoryPrompt(),         // ← 记忆使用指令 + MEMORY.md 索引
    getClaudeMds(),             // ← 记忆文件实际内容
    currentDate,                // 当前日期
]
```

如此一来，大家应该能想象到，token的消耗是多么的可怕。

### 提取

整个提取的过程如下。

```
handleStopHooks (stopHooks.ts)
    ↓
executeExtractMemories (extractMemories.ts)
    ↓
runExtraction (closure function)
    ├── 检查互斥性 (hasMemoryWritesSince)
    ├── 节流检查 (turnsSinceLastExtraction)
    ├── 扫描现有记忆 (scanMemoryFiles)
    ├── 构建 Prompt (buildExtractAutoOnlyPrompt / buildExtractCombinedPrompt)
    └── 执行分叉agent (runForkedAgent)
        ├── 创建受限工具集 (createAutoMemCanUseTool)
        ├── 注入现有记忆清单
        ├── 执行 LLM 对话（最多 5 轮）
        ├── 写入记忆文件
        └── 更新 MEMORY.md 索引
            ↓
记录提取事件 (logEvent)
    ↓
追加系统消息（"已保存 X 个记忆"）
```

#### 触发条件

记忆的提取，肯定不是随意的，这里 `handleStopHooks` 内有大量提取约束的逻辑。总结下来大概有如下内容。

- 源限制。仅在主线程查询 (`repl_main_thread`) 或 SDK 调用时触发，子agent不触发。
- 特性门控。可配置的记忆模式触发逻辑。代码里大家会看到 `feature('EXTRACT_MEMORIES')` 、 `isExtractModeActive()` 之类的控制。
- 节流。并非每一轮都会触发，需要满足特定轮数积累才会触发。
- 互斥。如果已经提取过就不提了。
- 特定场景约束，例如 `/compact` 、 `/rewind` 指令时，上下文压缩执行后的第一轮，特定配置下就不触发。
- 用户可以通过命令 `/memory save` 来触发。

具体的，在内部，会触发这个提取的，会有如下情况。

- 主agent直接写入，即用户明确要求、主动识别，“记住这个”、“把这个加到记忆中”时，就会触发主agent写入。
- 后台提取agent，这个在每次查询结束的时候触发。
- `/dream` 机制触发。

#### 提取prompt构造

这里的记忆提取，是通过大模型来完成的，那prompt就是重点工作了。简单地可以这么总结。

```
const userPrompt = teamMemoryEnabled
  ? buildExtractCombinedPrompt(newMessageCount, existingMemories, skipIndex)
  : buildExtractAutoOnlyPrompt(newMessageCount, existingMemories, skipIndex)

// Prompt 结构:
// 1. 角色定义：记忆提取子agent
// 2. 可用工具：Read/Grep/Glob/只读 Bash/Edit/Write（仅限记忆目录）
// 3. 分析范围：最近 ~N 条消息
// 4. 四种记忆类型的完整指令（XML 格式）
// 5. 两步保存流程（写文件 → 更新索引）
```

里面大概是这样的。

```
export function buildExtractAutoOnlyPrompt(
  newMessageCount: number,
  existingMemories: string,
  skipIndex = false,
): string {
  return [
    opener(newMessageCount, existingMemories),  // 1. 开场白 + 工具限制 + Turn 预算
    '',
    'If the user explicitly asks you to remember something, save it immediately as whichever type fits best. If they ask you to forget something, find and remove the relevant entry.',  // 2. 显式保存指令
    '',
    ...TYPES_SECTION_INDIVIDUAL,  // 3. 四种记忆类型的 XML 指令，前文有提及
    ...WHAT_NOT_TO_SAVE_SECTION,  // 4. 不应保存的内容，前文有提及
    '',
    ...howToSave,  // 5. 两步保存流程（写文件 + 更新索引），前文有提及
  ].join('\n')
}
```

继续往深处看。 `opener` 有这些内容。（不粘贴代码了，直接说里面有什么）

- 角色限定。 `You are now acting as the memory extraction subagent`
- 分析范围。 `Analyze the most recent ~${newMessageCount} messages above and use them to update your persistent memory systems.`
- 可用工具: Read/Grep/Glob/只读 Bash/Edit/Write（仅限记忆目录）
- 轮数预算约束。要求2轮完成记忆提取任务，这里是指第一轮并行读取所有记忆 `FileRead` ，第二轮并行执行所有 `FileWrite` / `FileEdit` 调用。
- 内容来源限制。只能使用最近 ~N 条消息的内容、禁止 `grep` 源码、阅读代码验证模式、执行 `git` 命令。
- 如果存在记忆文件，预注入清单，避免提取agent浪费轮数执行。

工具的权限控制，这里单独把代码拿出来，大家可以看看这个约束是什么样的。

```
export function createAutoMemCanUseTool(memoryDir: string): CanUseToolFn {
returnasync (tool: Tool, input: Record<string, unknown>) => {
    // Read/Grep/Glob 无限制
    if (tool.name === FILE_READ_TOOL_NAME || 
        tool.name === GREP_TOOL_NAME || 
        tool.name === GLOB_TOOL_NAME) {
      return { behavior: 'allow' }
    }
    
    // Bash 仅限只读命令
    if (tool.name === BASH_TOOL_NAME) {
      if (tool.isReadOnly(input)) {
        return { behavior: 'allow' }
      }
      return denyAutoMemTool(tool, 'non-read-only bash command')
    }
    
    // Edit/Write 仅限记忆目录
    if (tool.name === FILE_EDIT_TOOL_NAME || tool.name === FILE_WRITE_TOOL_NAME) {
      const filePath = input.file_path asstring
      if (filePath.startsWith(memoryDir)) {
        return { behavior: 'allow' }
      }
      return denyAutoMemTool(tool, \`write outside memory dir: ${filePath}\`)
    }
  }
}
```

#### dream机制

重点说一下dream机制，这是一个定期执行的任务，会定期的对日志进行数据的梳理，而不会伴随query请求和执行来触发。

这里，会有3层门控来进行控制。 `autoDream.ts`

```
// 三重门控机制（按成本从低到高检查）

// 1. 时间门控：距离上次整理 >= minHours（默认 24 小时）
const hoursSince = (Date.now() - lastAt) / 3_600_000
if (!force && hoursSince < cfg.minHours) return

// 2. 扫描节流：避免频繁扫描会话目录
const sinceScanMs = Date.now() - lastSessionScanAt
if (!force && sinceScanMs < SESSION_SCAN_INTERVAL_MS) return

// 3. 会话门控：自上次以来有 >= minSessions 个新会话
let sessionIds = await listSessionsTouchedSince(lastAt)
sessionIds = sessionIds.filter(id => id !== currentSession)  // 排除当前会话
if (!force && sessionIds.length < cfg.minSessions) return

// 4. 锁机制：确保单进程执行
let priorMtime = await tryAcquireConsolidationLock()
```

在经过这个判断后，就会开始进行dream。dream内部是一个完整的prompt去执行的，主要有如下内容，prompt我就不粘上来了。

- 了解现状，通过 `MEMORY.md` 以及对应内部的内容。
- 收集近期信号，寻找值得持久保存的信息，一般按照每日日志、发生漂移的已有记忆、对话记录检索的顺序进行查看。
- 整合，对每条值得记忆的内容，在记忆目录根目录下新建或更新对应记忆文件，重点关注避免创建近似重复文件、把相对日期改成绝对日期、删除已被更新的内容。
- 修剪或者建立索引，即更新 `MEMORY.md` 。

这里我把一般的记忆和dream做一个对比。

| 特性 | extractMemories | /dream |
| --- | --- | --- |
| **触发频率** | 每次查询结束 | 每天一次（+ 手动） |
| **作用范围** | 单次会话的最近 N 条消息 | 多个历史会话 + 全部记忆 |
| **执行时机** | 查询循环内（blocking） | 后台异步（non-blocking） |
| **处理深度** | 浅层提取（≤5 轮） | 深层整固（无硬性轮次限制） |
| **视野** | 仅当前会话 | 跨会话 + 历史日志 |
| **主要动作** | 创建新记忆 | 合并、删除、重构 |
| **工具权限** | 受限（仅记忆目录） | 受限（只读 Bash + 记忆目录） |
| **用户可见性** | 简单通知 | 任务状态 + 进度追踪 |

### 查询

记忆存在文件里，我们在合适的时候要把他调取出来，具体这个调用流程是这样的。

```
用户输入查询
    ↓
attachments.ts:2196 - getRelevantMemoryAttachments()
    ├── 提取 Agent @mentions（如果有）
    ├── 确定搜索目录（agent memory 或 auto memory）
    └── 并行搜索多个目录
        ↓
findRelevantMemories.ts:39 - findRelevantMemories()
    ├── scanMemoryFiles()  // 扫描最多 200 个记忆文件
    ├── filter(alreadySurfaced)  // 过滤已展示的记忆
    └── selectRelevantMemories()  // Sonnet 侧边查询
        ↓
memoryScan.ts:84 - formatMemoryManifest()
    └── 格式化记忆清单：\`- [type] filename (timestamp): description\`
        ↓
sideQuery API - Sonnet 模型选择
    ├── system: SELECT_MEMORIES_SYSTEM_PROMPT
    ├── user: Query + Available memories + Recently used tools
    └── output: JSON Schema → { selected_memories: [...] }
        ↓
findRelevantMemories.ts:74 - 返回结果
    └── 映射文件名 → 绝对路径 + mtime
        ↓
attachments.ts:2236 - readMemoriesForSurfacing()
    ├── 过滤已读过的文件（readFileState）
    ├── 限制最多 5 个
    └── 读取文件内容（带截断保护）
        ↓
创建 attachment: relevant_memories
    ↓
注入到系统提示（作为 attachments 部分）
    ↓
主模型看到完整的记忆内容（带 freshness 标记）
```

此处， `getRelevantMemoryAttachments` 是整个记忆检索的关键流程，总结下来就是这些内容。

- 确定检索目录。
- 并行搜索多个目录。
- 合并结果并去重。
- 读取文件内容。

其中，我们最关注的，应该是并行搜索多个目录这一步，函数是 `findRelevantMemories` 。这里的大致流程。

- 扫描记忆文件（每个路径最多 200 个）。同时，还会提前过滤已展示的， `alreadySurfaced` 会记录。
- 调用 Sonnet 进行选择。
- 记录选择率、空选择比例等指标。
- 将文件名映射回完整路径 + mtime。

注意，此处的记忆选择，是通过大模型Sonnet来选择的，在 `selectRelevantMemories` 函数内。prompt的设计同样有说法，为了方便阅读，我翻译成了中文。

```
你需要挑选出在 Claude Code 处理用户查询时有用的记忆内容。系统会提供用户查询，以及一组包含文件名和描述的可用记忆文件列表。返回 Claude Code 处理该查询时明显有用的记忆文件名列表（最多 5 个）。仅根据文件名与描述，把你确定有帮助的记忆加入列表。

- 若不确定某条记忆是否有助于处理用户查询，则不要列入。请谨慎筛选、严格判断。
- 若列表中没有明显有用的记忆，可返回空列表。
- 若提供了近期使用过的工具列表，不要选择这些工具的用法参考或 API 文档类记忆（Claude Code 已在使用这些工具）。但仍需选择包含这些工具的警告、注意事项或已知问题的记忆 —— 工具正在使用时，这类信息恰恰最为关键。
```

而\`user message部分，我也给个例子。

```
Query: 帮我修复数据库连接超时的问题

Available memories:
- [user] user_expertise_profile.md (2026-04-01T10:30:00.000Z): User is a senior backend engineer with deep PostgreSQL expertise
- [feedback] testing_preferences.md (2026-03-28T15:45:00.000Z): Integration tests must hit real database, not mocks. Reason: prior incident where mock/prod divergence masked broken migrations

Recently used tools: FileReadTool, GrepTool
```

预期输出是这样的。

```
{
  "selected_memories": [
    "connection_pool_config.md",
    "db_monitoring_grafana_dashboard.md",
    "preferred_debugging_tools.md",
    "testing_preferences.md"
  ]
}
```

另外，还会再做个后校验，确保选择的记忆都在列表里，避免幻觉。

```
const parsed: { selected_memories: string[] } = jsonParse(textBlock.text)
return parsed.selected_memories.filter(f => validFilenames.has(f))
// 只返回存在于原始列表中的文件名（防止幻觉）
```

这里也体现了渐进式披露的思想，在做记忆选择的时候，只考虑最简单的摘要，也就是前文所说的索引。

选择完以后，就需要注入到推理的prompt里面了，在主流程里，大模型看到有关记忆的部分是这样的。

```
## Relevant Memories

[user] user_expertise_profile.md (2 days ago)
_Some content here..._

[feedback] testing_preferences.md (5 days ago)
_Some content here..._

> This memory is 5 days ago. Memories are point-in-time observations,
> not live state — claims about code behavior or file:line citations
> may be outdated. Verify against current code before asserting as fact.
```

### 记忆维护挑战

在核心流程的最后，讲一下记忆维护的挑战。一般的，记忆库的维护会有如下3个难点。

- 内容冲突。多个记忆描述同一事物，会存在冲突。
- 信息过时。记忆内容过于陈旧。
- 重复冗余。相似或相同的记忆存多份

下面我们来看看这些难点claude code是怎么做的。

#### 冲突处理

对于问题，我们一般关注亮点，检测和处理。

检测上，会在创建时（prompt内要求， `extractMemories/prompts.ts` 和 `memdir.ts` ）、dream模式整理时（ `autoDream/consolidationPrompt.ts` ）触发检测。

在发现了冲突后，会遵循如下逻辑进行处理。

- 最新胜出策略。主要是针对同一事物状态冲突的处理。
- 特异性优先。更具体的记忆更有价值。
- 合并去重。相似内容合并为一个文件。
- 明确适用范围。看似冲突的记忆可能是适用范围不同。

#### 信息过时

代码里会做新鲜度检测，对大于1天的添加 `<system-reminder>` 标签，代码在读取到记忆的时候也会做过期检验，在这/dream模式内也会有，另外则是用户通过prompt的直接提醒。

过时信息的处理如下。

```
1. 检测到潜在过时
   ↓
   - 新鲜度警告 (>1 天)
   - 用户纠正
   - /dream 扫描发现矛盾
   - 模型使用时发现冲突
   ↓
2. 验证当前状态
   ↓
   - 读取相关代码文件
   - 检查 git 历史
   - 对比记忆内容
   ↓
3. 判断是否需要更新
   ↓
   - 确认过时 → 进入步骤 4
   - 仍然有效 → 保持不动
   ↓
4. 执行更新操作
   ↓
   - 选项 A: 更新现有文件（保留历史信息）
   - 选项 B: 删除过时文件（完全移除）
   - 选项 C: 标记为历史参考（添加 deprecated 标记）
   ↓
5. 更新索引
   ↓
   - 修改 MEMORY.md
   - 移除过时条目
   - 添加新条目（如有）
   ↓
6. 记录遥测
   ↓
   - tengu_memdir_file_edit
   - tengu_extract_memories_extraction
   - tengu_auto_dream_consolidation
```

## 思考

源码读下来，收获还是很大的，里面很多小操作都很让人眼前一亮，例如记忆的分类拆解模式，KAIROS日志模式、dream模式、记忆内容的边界约束等，很有借鉴的价值，能很明显感受到开发人员的开发实力和思路的开阔。

不过可能是因为项目还是比较新，功能的开发比较赶，所以没有足够的打磨和优化，未来还有很多提升的空间。

- 现在的记忆个数，约束在200，更多是权宜之计，因为Sonnet吃不下，日志一多效果就容易查。后续估计会借助搜索策略可以缩小范围，减少大模型约束的能力。
- 本地存储，从安全角度是个不错的方案，代码也确实是比较敏感，但在更多领域，我还是更喜欢云端的存储方案，用数据库存储增删改查起来会更方便。
- 记忆的模式还是相对单一，分字段分类型还可以进一步细拆，尤其对于code场景，甚至其他场景，定制的更加精细会对后续的优化有更多提升。
- 很多动作，都是简单的依靠大模型来处理，好消息是很泛用也很简单，可能处理的轮数会很多，很浪费token，时间也很长，效果层面上限也不会很高，在更多更加精细的应用上，微调模型说不定可以有更多的提升价值。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  

**微信扫一扫赞赏作者**

作者提示: 内容由AI生成

免费版会员每日查看限额30次，升级成为壹伴会员可享每日150次的查看次数

今日150次的查看限额已用完，请明日再试噢

CS的陋室

文章工具

已发文1天

0 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-mutil-icon.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-mutil-hover-icon.svg)

合成多图文

查看

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/save-nor.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/save-hover.svg)

生成长图

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-style-icon.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-style-hover-icon.svg)

采集样式

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/split-long-article.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/split-long-article-hover.svg)

长文转图片

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/wx-editor-tools-panel/forever-link.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/wx-editor-tools-panel/forever-link-hover.svg)

永久链接

拖动以选取样式（按ECS退出）

继续滑动看下一个

CS的陋室

向上滑动看下一个

0 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-mutil-icon.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-mutil-hover-icon.svg)

合成多图文

查看

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-style-icon.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/gather-style-hover-icon.svg)

采集样式

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/save-nor.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/save-hover.svg)

生成长图

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/check-cover-icon.svg) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/article-gatherer/check-cover-hover-icon.svg)

查看封面

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/common/close-white.png) ![公众号头像](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/yiban-add-btn.png)

添加到我的壹伴云笔记

登录公众号并进行授权后即可拖拽采集图片至公众号素材库

0 × 0(0,0)

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/common/close.svg)

隐藏文摘采集按钮？

提示

你可以在 设置->功能开关->采集素材功能 中重新打开文摘采集按钮 ^\_^

试试长按拖拽移动位置 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/common/close-gray.png) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/panel-entry.png) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/panel-entry-new.gif) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/sidebar_entry_newtip_icon1.png) 壹伴AI侧边栏全新升级 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/sidebar_entry_newtip_bg.png)

- 推送自动消失
- 关键词订阅推送
- 系统消息推送

当前版本() 无新版

全部消息 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/message_icon.png) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/empty/message.svg)

暂无消息

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/edit-icon.png) 展开编辑 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/search.png) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/close.png) ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/empty/note-empty.svg)

暂无笔记

没有更多了(oﾟ▽ﾟ)o'

正在加载中 ![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/common/loading.gif)

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/external/sidepanel_close_tip_icon-BZZIRJWS.png) 若有干扰，可在「设置」关闭悬浮球

👋 Hi，想聊点什么～

下笔没话说？

告诉我主题，文案、标题、Slogan我都行

名词听不懂？

别自己搜了，直接问我，三秒给你讲明白

脑袋空空了？

一起脑暴，给产品起名、给活动想点子

方案没头绪？

思路我来理，框架我来搭，你来做决策

新会话

历史

内容由AI生成，仅供参考

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/empty/message.svg)

暂无消息

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/close-panel.png)

### 壹伴·小插件

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/side-function-panel/login-image.png)

要使用小插件，请先登录哦

![](chrome-extension://ibefaeehajgcpooopoegkifhgecigeeg/assets/imgs/data-enhance/isok.svg) 订阅成功

![kimi](data:image/png;base64,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)