# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供在本仓库中工作时的指导。

## 这是什么

一个以 Obsidian 仓库形式运作的 **LLM Wiki**（也称为知识森林）。LLM 逐步构建并维护一个持久的 wiki —— 结构化、相互关联的 markdown 文件，它们位于用户与原始来源之间。wiki 是一种复利式产物：交叉引用、矛盾点和综合结论只需编译一次并持续保持最新，而无需在每次查询时重新推导。

## 目录结构

```
.
├── CLAUDE.md          # 本文件 —— wiki 的架构与约定
├── index.md           # 所有 wiki 页面的内容型目录
├── log.md             # 只追加的时间线记录（入库/查询/巡检）
├── raw/               # 不可变的原始文档（文章、论文、转录稿）
│   ├── assets/        # 待入库的新文章 + 本地图片/附件
│   └── archive/       # 已入库并处理完毕的文章
├── wiki/              # 由 LLM 生成的 markdown（请勿手动编辑）
│   ├── sources/       # 每个被入库的来源对应一个页面（摘要 + 核心要点）
│   ├── entities/      # 谁/什么工具：产品、公司、项目、开源库、具体的人
│   ├── concepts/      # 什么思想/方法：抽象概念、设计模式、方法论、技术范式
│   ├── synthesis/     # 跨来源的综合：领域内知识全景 + 跨领域分析对比
│   ├── threads/       # 知识脉络：模块化技能树 + 面试题（纵向学习路径）
│   └── queries/       # 问题的答案，归档以备复用
```

### 分类标准：entities vs concepts

一句话区分：**entities 是"谁/什么工具"，concepts 是"什么思想/方法"**。

| 维度 | entities | concepts |
|------|----------|----------|
| 本质 | 具体存在物（工具、项目、人、公司） | 抽象知识（思想、模式、方法论） |
| 判断标准 | 有 GitHub 仓库、官网、版本号、作者 | 是一种做法、理念、技术范式 |
| 示例 | Docker、Celery、FastAPI、Boris Cherny | 容器化、异步任务、JWT 认证、依赖注入 |
| 页面内容 | 基本信息、核心组件、使用指南、最佳实践 | 定义、原理、与其他概念的对比、适用场景 |

**铁律**：一个具体的工具/项目**只能**出现在 entities 中，不能同时在 concepts 中另开一页。该工具的使用方法、最佳实践应作为 entity 页面的一部分，而不是拆成独立的 concept 页面。

## 页面规范

每个 wiki 页面都应包含 YAML frontmatter：

```yaml
---
type: source | entity | concept | synthesis | thread | query
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [source-slug-1, source-slug-2]  # 用于 entity/concept/synthesis/query 页面
raw: raw/archive/<原始文件名>.md       # 仅 source 页面必填，指向原始文件路径
tags: [tag1, tag2]
---
```

页面标题使用句首字母大写（sentence case）。Slug 与文件名一致（`wiki/concepts/knowledge-graph.md` → `[[knowledge-graph]]`）。内部链接优先使用 wiki-link `[[page-name]]` 而非 Markdown 超链接。

### 原始文件导航

wiki 是分层的提炼系统，原始文件（含代码细节）保存在 `raw/archive/` 中。三层导航路径如下：

```
entity/concept/synthesis 页面
        ↓  sources 字段 + wiki-link
    source 页面（摘要层）
        ↓  页面内"原始文件"链接
    raw/archive/ 原始文件（细节层）
```

**source 页面**作为桥梁，必须在页面底部提供一个**"原始文件"**小节，使用相对路径的 Markdown 链接指向原始文件：

```markdown
## 原始文件

- [原始文件](../../raw/archive/<原始文件名>.md)
```

**entity / concept / synthesis / query 页面**通过 `sources: [slug]` 字段和正文中的 `[[source-slug]]` 链接引用 source 页面，不直接链接 raw 文件。读者始终通过 source 页面这一中转层回到原始细节。

## 核心工作流

### 入库（Ingest）

当用户向 `raw/` 添加来源并要求处理时触发。

1. 从 `raw/` 中读取来源。
2. 与用户讨论核心要点。
3. 创建或更新 `wiki/sources/<slug>.md`，写入摘要与核心主张。
   - frontmatter 中填写 `raw: raw/archive/<原始文件名>.md`。
   - 页面底部添加"原始文件"小节，链接回 `raw/archive/` 中的原始文件。
4. 更新受该来源影响的 `wiki/entities/` 和 `wiki/concepts/` 页面。记录与现有主张的矛盾之处。
   - **禁止死链**：如果新页面或更新后的页面中包含 `[[page-name]]` 形式的 wiki-link，必须确保该链接指向的页面在 `wiki/` 中**已经存在**，或者**同时创建**该页面。不能留下指向空白页面的链接。
5. **综合（Synthesis）—— 此步骤不可省略**：主动审视新来源与现有知识体系之间的关系，产出领域全景、知识脉络或跨领域洞察。三个方向：
   - **领域内知识全景（横向，优先）**：将同一领域的多个来源、entity、concept 汇总梳理，形成该领域的结构化知识地图。包括：模块依赖关系、能力分层、推荐学习路径、工具组合方案、技术演进脉络。让读者能从一张图中看到整个领域的全貌，而非散落在几十个独立页面中的碎片。产出至 `wiki/synthesis/`。
   - **领域内知识脉络（纵向）**：按模块拆解一个技术领域，每个模块下列举具体实现方案（链接到 entities/concepts）、面试题/关注问题、学习路径。持续迭代补充，是一个"活文档"。产出至 `wiki/threads/`。
   - **跨领域分析对比**：当新来源与不同领域的现有知识形成有意义的关联时（如工具选型对比、架构演进分析、方法论冲突、同一概念在不同领域的差异化实现）。产出至 `wiki/synthesis/`。
   - **更新现有 synthesis/thread**：当新来源补充、验证或挑战了已有综合结论或脉络模块时。
   - **记录"无新增综合"**：当新来源与现有知识体系暂无显著综合空间时，在 log.md 中简要记录此判断即可，无需创建页面。
   - **产出量视情况而定**——可以是一页领域全景/脉络，也可以是一句判断，但不能跳过审视过程。
6. 更新 `index.md`，加入新增或变更的页面。
7. 向 `log.md` 追加一条记录，格式为：`## [YYYY-MM-DD] ingest | <来源标题>`。
8. 将处理完毕的源文件从 `raw/assets/` 移动到 `raw/archive/`，使 `raw/assets/` 只保留待处理的新文章。

单个来源通常涉及 5–15 个 wiki 页面。就地更新已有页面，不要创建重复页面。

### 查询（Query）

当用户提出问题时触发。

1. 读取 `index.md` 定位相关页面。
2. 读取这些页面并使用 `[[page-name]]` 链接引用，综合出带引用的答案。
3. 如果答案具有复用价值或代表了新的综合结论，将其归档为 `wiki/queries/<slug>.md` 并更新 `index.md`。
4. 向 `log.md` 追加一条记录：`## [YYYY-MM-DD] query | <问题摘要>`。

### 巡检（Lint）

当用户要求 wiki 健康检查时触发。

1. 扫描没有入站 wiki-link 的孤立页面。
2. 识别在多个页面中被提及但缺少独立页面的重要概念。
3. 标记页面间的矛盾（注明每条主张的日期/来源）。
4. 检查是否有已被新来源取代的陈旧主张。
5. 验证 `index.md` 的完整性是否与实际文件一致。
6. **扫描死链**：检查所有 wiki 页面中的 `[[page-name]]` 链接，统计每个被引用但对应文件不存在的死链。对于发现的死链，选择以下一种方式处理：
   - 如果该概念/实体值得单独成页 → **创建对应页面**。
   - 如果只是顺带提及、无需深入 → **将 wiki-link 改为普通文本**，移除双方括号。
7. **检查原始文件导航**：验证每个 source 页面是否包含：
   - `raw` frontmatter 字段且指向的文件在 `raw/archive/` 中存在；
   - 正文中有"原始文件"小节且链接有效。
7. 向 `log.md` 追加一条记录：`## [YYYY-MM-DD] lint | <巡检摘要>`。

## 特殊文件

- **`index.md`** —— 内容目录。按类别组织（entities、concepts、sources、synthesis、queries）。每项格式：`[[page-name]] —— 一行摘要`。每次入库后更新。
- **`log.md`** —— 时间线。统一的前缀格式（`## [YYYY-MM-DD] <操作> | <摘要>`）使其可被 grep。可用于了解近期活动。

## 源文件处理

`raw/` 中的源文件是不可变的。永远不要编辑它们。来源入库后，将其从 `raw/assets/` 移动到 `raw/archive/`，以保持 `raw/assets/` 整洁并清晰显示哪些文章尚待处理。来源引用的图片应下载到 `raw/assets/`，以便 LLM 在需要时直接查看。如果来源包含图片，先阅读 markdown 文本，再单独查看具体图片以获取额外上下文。

## 工具说明

- 本仓库只是一个 markdown 文件的 git 仓库。版本历史可通过 git 查看。
- Obsidian 的图谱视图可展示页面之间的连接 —— 有助于发现孤立页面和核心枢纽。
- 如果安装了 Dataview 插件，可以查询 YAML frontmatter。
- 如果安装了 Marp 插件，可以从 wiki 内容生成幻灯片。
