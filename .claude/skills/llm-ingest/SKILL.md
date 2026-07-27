---
name: llm-ingest
description: "This skill should be used when the user wants to add new documents to the LLM Wiki (Knowledge Forest). It implements the Ingest phase of the Ingest/Query/Lint cycle: reading raw source files, compiling them into structured wiki Markdown pages (sources/entities/concepts/synthesis/queries), updating the index, and appending to the operation log. Use this skill when the user says things like 摄取这篇文章, 把这个加入知识库, ingest this paper, 更新我的 wiki, 处理 raw 目录里的新文件, or asks to build or maintain a personal knowledge base powered by LLMs."
---

# LLM Wiki 摄取技能（llm-ingest）

将原始资料「编译」进结构化知识森林。

---

## 核心定位

**摄取（Ingest）= 将一份新来源编译进 wiki，建立 source → entity → concept → synthesis 的关联，更新索引、追加日志。**

这是 LLM Wiki 三大核心操作（Ingest / Query / Lint）中的第一环，也是知识积累的起点。

---

## 触发场景

- 用户说「把这篇文章/论文/笔记加入我的知识库」
- 用户说「处理 raw/ 里的新文件」
- 用户说「ingest 这个来源」
- 用户希望初始化一个新的 LLM Wiki 知识库
- 用户希望了解哪些文件还没有被处理

---

## 知识库结构（必须遵守）

```
<kb_root>/
├── raw/                     # 原始来源（只读，永不修改）
│   ├── assets/              # 待处理的新文章 + 图片等资产
│   └── archive/             # 已入库并处理完毕的文章
├── wiki/                    # LLM 编译产物（LLM 完全拥有）
│   ├── sources/             # 每个被入库的来源对应一个页面（摘要 + 核心要点）
│   ├── entities/            # 实体：谁/什么工具（产品、公司、项目、开源库、具体的人）
│   ├── concepts/            # 概念：什么思想/方法（抽象概念、设计模式、方法论、技术范式）
│   ├── synthesis/           # 综合：领域内知识全景 + 跨领域分析对比
│   └── queries/             # 问题的答案，归档以备复用
├── index.md                 # 全局目录
├── log.md                   # append-only 操作日志
└── CLAUDE.md                # Schema 配置（约定 + 工作流）
```

**严格原则**：
- `raw/` 只读，LLM 永不编辑
- `wiki/` 由 LLM 完全拥有，人类不直接手动编辑
- 每个 wiki 页面必须可追溯到 `raw/` 中的来源文件
- 原始文件入库后，从 `raw/assets/` 移动到 `raw/archive/`

---

## 分类标准：entities vs concepts

一句话区分：**entities 是"谁/什么工具"，concepts 是"什么思想/方法"**。

| 维度 | entities | concepts |
|------|----------|----------|
| 本质 | 具体存在物（工具、项目、人、公司） | 抽象知识（思想、模式、方法论） |
| 判断标准 | 有 GitHub 仓库、官网、版本号、作者 | 是一种做法、理念、技术范式 |
| 示例 | Docker、Celery、FastAPI、Boris Cherny | 容器化、异步任务、JWT 认证、依赖注入 |
| 页面内容 | 基本信息、核心组件、使用指南、最佳实践 | 定义、原理、与其他概念的对比、适用场景 |

**铁律**：一个具体的工具/项目**只能**出现在 entities 中，不能同时在 concepts 中另开一页。

---

## Wiki 页面 Frontmatter 标准

每个 wiki 页面都应包含以下 YAML frontmatter：

```yaml
---
type: source | entity | concept | synthesis | query
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [source-slug-1, source-slug-2]  # 用于 entity/concept/synthesis/query 页面
raw: raw/archive/<原始文件名>.md           # 仅 source 页面必填，指向原始文件路径
tags: [tag1, tag2]
---
```

页面标题使用句首字母大写（sentence case）。Slug 与文件名一致（`wiki/concepts/knowledge-graph.md` → `[[knowledge-graph]]`）。内部链接优先使用 wiki-link `[[page-name]]` 而非 Markdown 超链接。

---

## 执行摄取的标准流程

### 第 1 步：使用脚本了解当前状态

运行辅助脚本（位于此 skill 的 `scripts/ingest.py`）来获取准确的状态信息：

```bash
# 如果是新知识库，先初始化
python <skill_scripts_dir>/ingest.py init <kb_root>

# 查看待处理文件列表
python <skill_scripts_dir>/ingest.py scan <kb_root>

# 查看整体状态摘要
python <skill_scripts_dir>/ingest.py status <kb_root>
```

`<skill_scripts_dir>` 是此 skill 的 `scripts/` 目录绝对路径。

### 第 2 步：读取来源文件

- 读取 `raw/assets/` 中用户指定（或 scan 发现的）文件
- 对于图片：先读文本部分，再单独读取图片文件获取视觉信息
- 识别文件类型（文章/论文/笔记/数据/代码）以决定提取策略

### 第 3 步：将完整原文存入 raw/（可保留原文或翻译为中文）

**raw/ 目录存放的是完整原始内容，不做摘要压缩。**

- 原始文章可以翻译为中文后存入 `raw/assets/`（若来源为外文）
- raw/ 中的文件**只写一次**，LLM 永不修改
- 来源引用的图片应下载到 `raw/assets/`，便于 LLM 查看

### 第 4 步：提取 + 编译到 wiki

从 raw/ 中的完整原文出发，按以下层级创建/更新 wiki 页面：

| 提取对象 | 目标路径 | 页面类型 | 说明 |
|---------|---------|---------|------|
| 来源摘要 | `wiki/sources/<slug>.md` | source | 摘要 + 核心主张 + 原始文件链接 |
| 关键概念（3-10 个） | `wiki/concepts/<name>.md` | concept | 定义 + 原理 + 关联链接 |
| 关键实体（人/产品/组织） | `wiki/entities/<name>.md` | entity | 描述 + 相关概念 + 来源 |
| 领域内/跨领域综合 | `wiki/synthesis/<topic>.md` | synthesis | 全景图、对比分析、趋势判断 |
| 优质问答 | `wiki/queries/<slug>.md` | query | 问题的答案，归档复用 |

**关键**：一份来源通常应影响 **5–15 个 wiki 页面**，而不只是一个摘要页面。

**source 页面**作为桥梁，必须在页面底部提供一个**"原始文件"**小节，使用相对路径的 Markdown 链接指向原始文件：

```markdown
## 原始文件

- [原始文件](../../raw/archive/<原始文件名>.md)
```

**entity / concept / synthesis / query** 页面通过 `sources: [slug]` 字段和正文中的 `[[source-slug]]` 链接引用 source 页面，不直接链接 raw 文件。

### 第 5 步：综合（Synthesis）—— 不可省略

主动审视新来源与现有知识体系之间的关系，产出领域全景或跨领域洞察：

- **领域内知识全景（优先）**：将同一领域的多个来源、entity、concept 汇总梳理，形成该领域的结构化知识地图。
- **跨领域分析对比**：当新来源与不同领域的现有知识形成有意义的关联时（如工具选型对比、架构演进分析、方法论冲突）。
- **更新现有 synthesis**：当新来源补充、验证或挑战了已有综合结论时。
- **记录"无新增综合"**：当新来源与现有知识体系暂无显著综合空间时，在 log.md 中简要记录此判断即可。

### 第 6 步：更新 index.md

在对应分类下追加新页面条目，格式：

```markdown
[[page-name]] —— 一行摘要
```

### 第 7 步：追加操作日志 + 移动源文件

使用脚本追加日志（同时自动标记文件为「已摄取」）：

```bash
python <skill_scripts_dir>/ingest.py log <kb_root> "ingest | <来源标题>"
```

或手动在 `log.md` 追加：

```markdown
## [YYYY-MM-DD] ingest | <来源标题>

- 新增/更新页面：...
- 关键发现：...
```

最后将处理完毕的源文件从 `raw/assets/` 移动到 `raw/archive/`，使 `raw/assets/` 只保留待处理的新文章。

---

## 处理特殊情况

**矛盾信息**：当新来源与现有 wiki 内容矛盾时，不要直接覆盖。在相关页面添加「⚠️ 矛盾注记」部分，并在 log.md 记录。

**批量摄取**：一次处理多个文件时，按相关性分批处理，保持每批都有完整的 index 和 log 更新。

**死链检查**：如果新页面或更新后的页面中包含 `[[page-name]]`，必须确保该页面已经存在或同时创建。不能留下指向空白页面的链接。

---

## 参考文档

详细的操作规范、SOP 流程、矛盾处理方法、规模扩展指南，参见：
`references/ingest-guide.md`（此 skill 的 references 目录）

---

## 脚本能力速查

`scripts/ingest.py` 提供以下命令（无需安装额外依赖，纯标准库）：

| 命令 | 功能 |
|------|------|
| `init <kb_root>` | 初始化知识库目录结构（raw/、wiki/、CLAUDE.md 等） |
| `scan <kb_root>` | 列出待处理文件（新增 + 已变更） |
| `status <kb_root>` | 显示整体状态摘要（文件数、页面数、最近日志） |
| `log <kb_root> <msg>` | 追加操作日志，若消息含 `ingest \|` 则自动标记文件 |
| `stale <kb_root>` | 检测自上次摄取以来内容已变更的文件 |
