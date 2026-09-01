# LLM Wiki 摄取（Ingest）参考文档

基于 Knowledge Forest（LLM Wiki）模式的摄取操作详细指南。

---

## 核心概念

**摄取（Ingest）** 是 LLM Wiki 三大操作之一（Ingest / Query / Lint）。
它将一份新的原始资料「编译」进 wiki，建立关联、更新索引、追加日志。

---

## 目录结构约定

```
<kb_root>/
├── raw/                     # 原始来源（只读，LLM 永不修改）
│   ├── assets/              # 待处理的新文章 + 图片等媒体
│   └── archive/             # 已入库并处理完毕的文章
├── wiki/                    # LLM 编译产物（LLM 完全拥有）
│   ├── sources/             # 每个被入库的来源对应一个页面
│   ├── entities/            # 实体：谁/什么工具
│   ├── concepts/            # 概念：什么思想/方法
│   ├── synthesis/           # 综合：领域全景与对比分析
│   └── queries/             # 优质问答归档
├── index.md                 # 全局目录（每页一行摘要）
├── log.md                   # 操作日志（append-only）
└── CLAUDE.md                # Schema：告诉 LLM wiki 结构和约定
```

---

## 核心原则：raw/ 存放完整原文，不做摘要

**raw/ 目录是知识库的「源代码」层，必须满足：**

1. **完整**：存入 raw/ 的是完整原始内容，不是摘要。不是「提炼」「总结」「提取要点」。
   - 一篇 5000 词的文章 → 存入 raw/ 的是 5000 词完整内容（可翻译为中文）

2. **原始**：raw/ 中的内容代表原始来源本身。LLM 只负责整理格式/翻译语言，不压缩信息。

3. **不可修改**：LLM 永不编辑 raw/ 目录。如果需要更正，只能新增一个版本，并在 log.md 中注明。

4. **有状态**：`raw/assets/` 只保留待处理的新文章；处理完成后移动到 `raw/archive/`。

**为什么这样做？**
- 完整原文才能支持未来可能的重新编译（如 wiki 结构改变）
- 翻译本身是一种深度理解过程，有助于 LLM 建立更准确的概念关联
- `assets/` 作为「待处理缓冲区」，让批量摄取有明确触发信号

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

```yaml
---
type: source | entity | concept | synthesis | query
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [source-slug-1, source-slug-2]  # 用于 entity/concept/synthesis/query 页面
raw: raw/archive/<原始文件名>.md           # 仅 source 页面必填
tags: [tag1, tag2]
---
```

- `type`：页面类型，五选一
- `created` / `updated`：创建和最后更新日期
- `sources`：本页面引用的 source 页面 slug 列表
- `raw`：仅 source 页面填写，指向 raw/archive/ 中的原始文件
- `tags`：主题标签，便于聚类

---

## 摄取操作标准流程（SOP）

### 步骤 1：读取来源

- 从 `raw/assets/` 中读取新来源
- 识别文件类型（文章/论文/笔记/数据/代码）以决定提取策略
- 如有图片，先读文本部分，再单独读取图片文件

### 步骤 2：创建/更新 source 页面

- 在 `wiki/sources/<slug>.md` 创建页面
- 写入摘要、核心主张、关键发现
- frontmatter 中填写 `raw: raw/archive/<原始文件名>.md`
- 页面底部添加「原始文件」小节，链接回 `raw/archive/`

### 步骤 3：创建/更新 entity 和 concept 页面

- 从来源中提取关键实体（工具、项目、人）和概念（思想、模式）
- 更新 `wiki/entities/` 和 `wiki/concepts/` 中的对应页面
- 使用 `[[source-slug]]` 引用 source 页面
- 记录与现有主张的矛盾之处

### 步骤 4：综合（Synthesis）—— 不可省略

主动审视新来源与现有知识体系之间的关系：

- **领域内知识全景**：将同一领域的多个来源、entity、concept 汇总梳理
- **跨领域分析对比**：工具选型、架构演进、方法论冲突等
- **更新现有 synthesis**：当新来源补充、验证或挑战已有综合结论时
- **记录"无新增综合"**：如果确实没有新的综合空间，在 log.md 中简要记录

### 步骤 5：更新 index.md

按 entities / concepts / sources / synthesis / queries 分类追加新页面条目：

```markdown
[[page-name]] —— 一行摘要
```

### 步骤 6：追加日志 + 归档源文件

- 在 `log.md` 追加记录：`## [YYYY-MM-DD] ingest | <来源标题>`
- 使用脚本：`python scripts/ingest.py log <kb_root> "ingest | <来源标题>"`
- 将源文件从 `raw/assets/` 移动到 `raw/archive/`

---

## 处理特殊情况

### 矛盾信息

当新来源与现有 wiki 内容矛盾时：
1. 不要直接覆盖旧结论
2. 在相关页面添加「⚠️ 矛盾注记」
3. 在 log.md 中记录矛盾点及来源

### 批量摄取

一次处理多个文件时：
1. 按主题分批（避免概念跨度过大）
2. 每批都完整执行 index 更新和 log 追加
3. 同一批内避免重复创建相同 entity/concept 页面

### 死链预防

如果新页面包含 `[[page-name]]`：
- 确保目标页面已存在，或
- 同时创建目标页面
- 不能留下指向空白页面的链接

### 查询答案归档

用户提问后得到的高质量答案：
1. 如果具有复用价值，归档为 `wiki/queries/<slug>.md`
2. frontmatter 中 `type: query`，并标注引用的 sources
3. 更新 index.md 的 Queries 部分

---

## 与 Query、Lint 的关系

- **Ingest**：把外部信息写入 wiki，建立结构
- **Query**：从 wiki 中读取并综合答案，优质答案回流到 queries/
- **Lint**：检查 wiki 健康状态（孤立页面、死链、矛盾、陈旧主张）

三个操作形成闭环：Ingest 扩大知识库 → Query 提取价值 → Lint 保持健康。
