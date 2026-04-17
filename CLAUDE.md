# Weilan Knowledge Wiki — Claude Code 工作流规则

> 本文件定义 Claude Code 与本知识库交互时的完整工作流。所有操作必须遵循以下规则。

---

## 1. 总体流程：三阶段工作流

本知识库遵循 **采集 → 整理 → 消费** 的闭环流程。

| 阶段                | 触发方式                    | 说明                                                                                    |
| ----------------- | ----------------------- | ------------------------------------------------------------------------------------- |
| **采集 (Ingest)**   | 用户主动将原始内容放入 `Clipping/` | 仅收集，不做任何处理。                                                                           |
| **整理 (Organize)** | 用户说 **"整理 Clippings"**  | Claude 读取 `Clipping/` 中的内容，分类、去重、撰写文章到 `wiki/{category}/articles/`，更新索引，并将已处理的原始素材移入 `Archive/`。 |
| **消费 (Consume)**  | 用户向 Claude 提问或请求总结      | Claude 先读 `wiki/INDEX.md` 理解知识结构，再按需读取相关文章，综合答案后保存到 `outputs/`。                       |

---

## 2. 整理阶段：分步操作规则

当用户说 **"整理 Clippings"** 时，按以下顺序执行：

### Step 1: 扫描 (Scan)
读取 `Clipping/` 中所有文件，识别哪些素材**尚未被整理**（即还未移入 `Archive/` 的）。

### Step 2: 分类 (Categorize)
为每个未整理素材判定一个**主分类**，必须从以下预设分类中选择：
- `Rag`
- `Fastapi`
- `AICoding`
- `ClaudeCode`
- `Median-tools`

若素材不适合以上分类，可创建新分类文件夹 `wiki/{new-category}/`，并在索引中注册。

### Step 3: 去重与合并 (Resolve Duplicates)
将当前素材与 `wiki/{category}/articles/` 中已有文章进行对比，检查是否存在**高度重合**的内容。具体规则见第 3.2 节。

### Step 4: 撰写文章 (Write Articles)
将最终确定的内容输出为文章，存放路径：
```
wiki/{category}/articles/{article-title}.md
```

文章必须包含符合规范的 YAML frontmatter（见第 5 节）。

### Step 5: 更新索引 (Update Indexes)
更新所有相关的 `index.md` 文件，包括根索引、分类索引和子分类索引。具体规则见第 4 节。

### Step 6: 归档原始素材并更新文章状态 (Archive Originals & Update Status)
**仅将已整理成文章的原始素材**从 `Clipping/` 移入 `Archive/`。未处理完的素材必须保留在 `Clipping/` 中。

归档完成后，必须更新对应文章的 frontmatter：
- `status` 设为 `"archived"`
- `references` 设为原始素材在 `Archive/` 中的相对路径（如 `Archive/original-file.md`）

同时在文章末尾添加「来源与归档」段落，放可点击的 Markdown 链接指向 `Archive/` 中的原始素材。

### Step 7: 确认反馈 (Confirm)
向用户汇报整理结果：
- 处理了多少篇素材
- 涉及了哪些分类
- 是否发生合并、新建分类
- 是否有未处理的素材及其原因

### 2.1 并行整理规则（Parallel Organization）
当 `Clipping/` 中待整理的素材数量 **≥ 3** 时，主代理可以启动最多 **3 个子代理**并行处理，以提升效率：

- **任务拆分**：主代理将待整理素材按分类或按数量均衡拆分为最多 3 组，每组分配给一个子代理。
- **子代理职责**：每组子代理独立完成分类、去重、撰写文章（直接写入 `wiki/{category}/articles/`）。
- **主代理职责**：
  1. 汇总所有子代理产出的文章；
  2. 统一检查跨组重复（如两组写成了同一主题）；
  3. 集中更新所有 `index.md` 索引；
  4. 统一将已处理的原始素材移入 `Archive/` 并更新各文章的 `references` 与 `status`。
- **限制**：每个子代理最多处理一组素材，禁止多个子代理同时修改同一篇文章或同一索引文件。

---

## 3. 边界情况处理规则

### 3.1 多分类文章 (Multi-Category)
当一篇素材明显属于**多个分类**时：

- **物理位置**：仅存放在**主分类**对应的文件夹下，即 `wiki/{主分类}/articles/`。
- **交叉索引**：在所有相关的分类 `index.md` 中建立链接，标注为跨分类引用。
- **标签标注**：在文章 frontmatter 的 `tags` 字段中列出所有相关分类。

**示例 frontmatter**：
```yaml
---
title: "在 FastAPI 中实现 RAG 流水线"
source: "https://example.com/blog-post"
created: 2026-04-16
category: "Rag"
tags: ["Rag", "Fastapi"]
---
```

在 `wiki/Rag/index.md` 中正常列出该文章。在 `wiki/Fastapi/index.md` 中添加跨分类链接：
```markdown
- [在 FastAPI 中实现 RAG 流水线](../Rag/articles/在-fastapi-中实现-rag-流水线.md) — (交叉引用: Rag)
```

### 3.2 高度重合素材 (Near-Duplicates)
当两篇素材内容高度重合但不完全相同时，Claude 按以下原则处理：

1. **对比核心观点**：如果核心观点/结论基本一致，**合并为一篇文章**。将不同视角或细节整合到同一篇文章中，保留原始来源，并在正文中注明合并来源。
2. **视角明显不同**：如果一篇是教程、另一篇是 critique，或面向不同层次读者，**保留两篇文章**，并在每篇文章底部增加 "相关阅读" 段落，互相建立链接。
3. **Claude 自主判断**：优先合并；若拿不准，**宁可保留两篇并互链，也不要强行合并导致信息丢失**。

**合并后的 frontmatter 示例**：
```yaml
---
title: "RAG 评估方法综述"
sources:
  - "https://example.com/post-a"
  - "https://example.com/post-b"
created: 2026-04-16
category: "Rag"
tags: ["Rag"]
---

> 本文合并自以下两篇素材：《RAG 评估指标》和《如何测试 RAG 系统》。
```

---

## 4. 索引维护规则

### 4.1 索引层级（最大 3 层）

```
wiki/INDEX.md                                        ← 第 1 层：根索引
wiki/{category}/{category}_index.md                  ← 第 2 层：分类索引
wiki/{category}/{subcategory}/{subcategory}_index.md ← 第 3 层：子分类索引
```

禁止创建第 3 层以下的索引文件。

### 4.2 何时创建子分类索引

仅当同时满足以下条件时才创建子分类索引：
- 该分类下已积累 **8 篇或以上文章**；
- 这些文章能自然地划分为 **2 个或以上不同的子主题**。

不足 8 篇文章的分类，不允许创建子分类索引。

### 4.3 单页条目上限

为控制单页长度，各层级索引的条目上限如下：
- **根索引 (`wiki/INDEX.md`)**：最多 20 个分类入口。
- **分类索引 (`wiki/{category}/index.md`)**：最多 30 个文章/子分类入口。
- **子分类索引 (`wiki/{category}/{subcategory}/index.md`)**：最多 40 个文章入口。

若某索引即将超过上限，应通过拆分子分类或将内容进一步归组来分流。

### 4.4 索引格式规范

每个 `index.md` 必须包含：
1. 一级标题（索引名称）
2. 简短的范围描述
3. 条目列表（使用 Markdown 无序列表，最多嵌套 2 层）

索引中的链接优先使用标准相对 Markdown 链接；跨分类引用必须明确标注来源分类。

---

## 5. 文件命名与 Frontmatter 规范

### 5.1 文件路径规则

| 内容类型 | 路径规则 |
|----------|----------|
| 原始剪藏 | `Clipping/{original-filename}` |
| 整理后的文章 | `wiki/{category}/articles/{article-title}.md` |
| 根索引 | `wiki/INDEX.md` |
| 分类索引 | `wiki/{category}/{category}_index.md` |
| 子分类索引 | `wiki/{category}/{subcategory}/{subcategory}_index.md` |
| 问答输出 | `outputs/YYYY-MM-DD-{topic-summary}.md` |

### 5.2 文章文件名规则

- 使用 **小写英文字母 + 数字 + 连字符 `-`**
- 不允许空格或特殊符号（除连字符和句点外）
- 标题长度控制在 3–7 个英文单词或对应中文长度
- 中文标题可转为拼音或保留英文关键词，以连字符分隔

**示例**：
- `rag-evaluation-methods.md`
- `fastapi-dependency-injection-guide.md`

### 5.3 文章 Frontmatter 模板

每篇 `wiki/{category}/articles/` 下的文章必须包含以下 frontmatter：

```yaml
---
title: "文章标题"
source: "原始 URL 或文件路径"     # 合并时改用 sources 列表
created: YYYY-MM-DD              # 整理日期
category: "主分类名"             # 必须与文件夹名一致
tags: ["主分类名", "type/xxx", "其他标签"]
status: "draft" | "refined" | "archived"
references: "Archive/{original-filename}"  # 原始素材归档后的相对路径
---
```

**字段说明**：
- `tags`：必须包含主分类标签（与 `category` 一致），**必须包含至少一个标准类型标签**（如 `type/hands-on`、`type/tool` 等，见第 6.1 节），可追加技术关键词。一篇文章允许同时打多个类型标签。
- `status`：文章状态。`"draft"` 为初稿，`"refined"` 为已润色，`"archived"` 表示原始素材已移入 `Archive/` 且文章已最终定稿。
- `references`：指向 `Archive/` 中对应的原始剪藏文件，便于溯源。若合并了多篇素材，可用 `references` 列表。

**可选字段**：
- `sources`: 原始来源 URL 列表（合并多篇素材时使用）
- `merged_from`: 原始剪藏文件名列表
- `related`: 相关文章的相对路径列表（用于 "相关阅读"）

**文章末尾必须包含「来源与归档」段落**（status 为 archived 时），提供可点击的 Markdown 链接指向原始素材。示例：
```markdown
---

## 来源与归档

- 原始素材：[Archive/original-file.md](../../../Archive/original-file.md)
```

### 5.4 输出文件 Frontmatter 模板

每个保存到 `outputs/` 的文件必须包含：

```yaml
---
title: "主题摘要"
created: YYYY-MM-DD
query: "用户的原始问题或请求"
sources:
  - "wiki/{category}/articles/article-a.md"
  - "wiki/{category}/articles/article-b.md"
---
```

---

## 6. 预设分类说明

以下分类已预先建立，整理时优先使用。文件夹名必须严格匹配大小写：

| 文件夹名 | 覆盖范围 |
|----------|----------|
| `Rag` | RAG（检索增强生成）技术、工具、模式与最佳实践 |
| `Fastapi` | FastAPI 框架、设计模式、生态工具与部署 |
| `AICoding` | AI 辅助编程、智能体（Agents）、开发工作流、通用 Skill 设计模式与开发提效技巧。**不属于**：特定工具（Claude Code / Cursor / Windsurf）的源码解析、内部架构或独家特性深度剖析 |
| `ClaudeCode` | Claude Code 的源码解析、内部架构、记忆系统、REPL 机制、独家特性深度剖析 |
| `Median-tools` | Median 相关工具、视频/媒体类 AI 工具、实用脚本、集成方案 |

### 6.1 标准类型标签（文章类型）

整理时每篇文章必须在 `tags` 中标注至少一个标准类型标签，使用 Obsidian 嵌套标签格式 `type/xxx`：

| 嵌套标签 | 类型名称 | 判断标准 |
|----------|----------|----------|
| `type/hands-on` | 项目实战型 | 包含可运行代码、完整项目结构、部署配置，读者能直接动手复现 |
| `type/tool` | 工具/项目推荐型 | 介绍 GitHub 项目、开源工具、第三方服务，以"是什么+怎么用+优缺点"为主 |
| `type/concept` | 原理解析型 | 深入讲解架构、机制、源码、设计思想，偏"为什么"和"怎么做出来的" |
| `type/tips` | 技巧汇总型 | 收集快捷操作、最佳实践、使用窍门、效率技巧，通常是清单或经验总结 |
| `type/tutorial` | 教程/保姆级攻略 | Step-by-step 教学，有明确学习路径，适合从零开始跟做 |
| `type/news` | 资讯/动态型 | 纯新闻、产品发布、行业动态，知识密度低、时效性强 |

**规则**：
- 一篇文章可同时拥有多个类型标签（如 `type/tutorial` + `type/hands-on`）。
- 类型标签必须是**嵌套标签格式**（`type/xxx`），确保在 Obsidian Tag Pane 中自动折叠为树状结构。

---

## 7. Claude 快速参考

- **每次回答知识相关问题前，先读 `wiki/INDEX.md` 理解整体结构。**
- **整理时只处理 `Clipping/` 中未归档的内容，已处理的必须移入 `Archive/`。**
- **永远不要删除 `Clipping/` 中尚未处理的内容。**
- **永远不要修改 `Archive/` 中的文件。**
- **优先使用交叉链接，避免复制多份相同文章。**
- **生成消费类输出时，务必保存到 `outputs/YYYY-MM-DD-{topic-summary}.md`。**
