# Drafts 生命周期治理规范实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将轻量约定型的 `drafts/` 治理规范落地到仓库，清理当前 `agent-book-beginner` 项目的混合结构。

**Architecture:** 在 `CLAUDE.md` 中替换原有 `drafts/` 一节为包含状态标签、README 模板、去向规则的治理规范；更新 `drafts/agent-book-beginner/README.md` 以符合新模板；删除重复的 `drafts/agent-book-beginner/research/` 目录；同步更新 `index.md` 和 `log.md`。

**Tech Stack:** Markdown, Git

## Global Constraints

- 所有 markdown 文件必须保持 Obsidian 兼容（wiki-link `[[page-name]]`、YAML frontmatter）。
- 禁止手动编辑 `raw/` 中的源文件（本计划只删除 `drafts/` 中的重复资料，不涉及 `raw/`）。
- 每个任务完成后必须通过读取文件验证内容正确性。
- 提交信息使用中文，格式为 `<类型>: <摘要>`。

---

### Task 1: 更新 CLAUDE.md 中的 drafts/ 治理规范

**Files:**
- Modify: `CLAUDE.md`
- Test: 读取 `CLAUDE.md` 中 `drafts/` 相关段落

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-07-27-drafts-governance-design.md`
- Produces: 更新后的 `CLAUDE.md` 章节

- [ ] **Step 1: 读取现有 `CLAUDE.md` 中 `半成品输出：drafts/` 一节**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/CLAUDE.md`
Expected: 定位到 `半成品输出：drafts/` 小节

- [ ] **Step 2: 用新规范替换原有 drafts/ 小节**

修改内容：将原 `半成品输出：drafts/` 一节替换为以下内容（保留前后章节）：

```markdown
## 半成品输出：drafts/

`drafts/` 目录存放基于 wiki 知识产出的**半成品**：书稿、长文章、演讲稿、课程大纲等。它与 `wiki/` 的关键区别在于：

| 维度 | `wiki/` | `drafts/` |
|------|---------|-----------|
| 内容 | 结构化知识卡片 | 面向特定读者/目标的成篇内容 |
| 编辑者 | LLM 维护，人类审阅 | 人类主导，LLM 辅助 |
| 来源 | `raw/` 中的原始资料 | `wiki/synthesis/` + `raw/` |
| 生命周期 | 持续迭代 | 完成后发布或归档 |

### 目录结构

```
drafts/
├── agent-book-beginner/
│   ├── README.md      # 项目说明 + 状态标签
│   └── chapters/      # 章节/正文
└── another-project/
    ├── README.md
    └── ...
```

**约束**：

- 每个 `drafts/<project>/` 是一个独立的创作项目。
- `drafts/<project>/` 下只保留与当前创作直接相关的文件。
- **禁止在 `drafts/` 中囤积原始资料**。原始资料属于 `raw/`。

### 项目 README 模板

每个 draft 项目的 `README.md` 必须包含以下小节：

```markdown
# 项目标题

**状态**: `planning` | `writing` | `review` | `published` | `archived`

## 目标

一句话说明这个半成品的目标：读者是谁、要解决什么问题、最终形态是什么。

## 与 wiki 的关系

列出主要依赖的 wiki 页面：

- [[synthesis-page]]
- [[concept-page]]

## 当前进度

- [ ] 第 1 章
- [x] 第 2 章

## 来源

- 优先引用：`wiki/synthesis/`、`wiki/concepts/`
- 必要时回查：`raw/archive/` 中的原始文件
```

### 状态标签

每个项目同一时刻只能有一个状态：

| 状态 | 含义 |
|------|------|
| `planning` | 还在构思、列大纲，没有正式开写 |
| `writing` | 正在撰写主体内容 |
| `review` | 内容基本完成，正在审阅/修改 |
| `published` | 已发布到外部平台，准备从 `drafts/` 移出 |
| `archived` | 不再继续，准备归档 |

### 与 wiki 的关系

- **drafts 是下游**：可以引用 wiki，但 wiki 不反向依赖 drafts。
- **发现新结论时向上游迁移**：如果写作过程中产生值得长期保留的洞察，应把它提取成 `wiki/concepts/` 或 `wiki/synthesis/`，而不是让它只存在于 draft 中。
- **引用方式**：章节中优先用 `[[page-name]]` wiki-link 引用 wiki 页面；外部链接用普通 Markdown 链接。

### 完成后的去向

一旦项目达到 `published` 或 `archived` 状态，应在 30 天内移出 `drafts/`：

- **`published`**：发布到外部平台后，将最终版本移到 `raw/archive/drafts/<project>/` 作为历史作品存档，或直接从仓库中删除。
- **`archived`**：未发布但不再继续，直接移到 `raw/archive/drafts/<project>/`。

`index.md` 的 Drafts 分类只保留 `planning` / `writing` / `review` 状态的项目。
```

- [ ] **Step 3: 验证替换结果**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/CLAUDE.md` 相关段落
Expected: 新规范完整、格式正确、无重复旧内容

- [ ] **Step 4: 提交**

```bash
git add CLAUDE.md
git commit -m "docs: 更新 drafts/ 生命周期治理规范（轻量约定型）"
```

---

### Task 2: 更新 agent-book-beginner 的 README.md

**Files:**
- Modify: `drafts/agent-book-beginner/README.md`
- Test: 读取更新后的 README.md

**Interfaces:**
- Consumes: 新规范中的 README 模板
- Produces: 符合规范的 `drafts/agent-book-beginner/README.md`

- [ ] **Step 1: 读取现有 `drafts/agent-book-beginner/README.md`**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/drafts/agent-book-beginner/README.md`
Expected: 文件已加载到上下文

- [ ] **Step 2: 在文件顶部插入状态标签**

在 `# 项目：Agent 系统入门书（实习生比喻版）` 下方插入：

```markdown
**状态**: `writing`
```

- [ ] **Step 3: 添加"当前进度"小节**

在 "## 与 wiki 的关系" 之后插入 "## 当前进度" 小节：

```markdown
## 当前进度

- [x] 第 0 章：初识 Agent
- [x] 第一部分：Agent 的骨架
- [x] 第 1 章：工作节奏——编排循环
- [x] 第 2 章：双手——工具系统
- [x] 第 3 章：笔记本——记忆系统
- [x] 第 4 章：理解任务——Prompt 构建
- [x] 第 5 章：汇报成果——输出解析
- [x] 第二部分：Agent 的韧性
- [x] 第 6 章：工作台——状态管理
- [x] 第 7 章：抗压与纠错——错误处理
- [x] 第 8 章：注意力分配——上下文管理
- [x] 第 9 章：职业底线——安全防护
- [x] 第三部分：Agent 的进阶
- [x] 第 10 章：自我检查——验证循环
- [x] 第 11 章：团队协作——子 Agent 编排
- [x] 第 12 章：入职第一天——初始化与环境
```

注意：17 个章节文件均已存在，所以全部标记为 `[x]`。

- [ ] **Step 4: 更新"当前状态"小节**

将原有 "## 当前状态" 小节中的 `research/` 相关描述删除，替换为：

```markdown
## 当前状态

- 17 个章节文件已就位，整体处于 `writing` 阶段。
- 下一步：按章节推进写作，优先引用 `wiki/synthesis/` 中的综合结论。
- `drafts/agent-book-beginner/research/` 中的原始调研资料已与 `raw/research/agent-frameworks/` 重复，将在 Task 3 中删除。
```

- [ ] **Step 5: 验证更新后的 README.md**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/drafts/agent-book-beginner/README.md`
Expected: 包含状态标签、目标、与 wiki 的关系、当前进度、来源、当前状态小节；无 research/ 重复描述

- [ ] **Step 6: 提交**

```bash
git add drafts/agent-book-beginner/README.md
git commit -m "docs: 更新 agent-book-beginner README，补充状态标签与进度"
```

---

### Task 3: 删除重复的 research/ 目录

**Files:**
- Delete: `drafts/agent-book-beginner/research/` 及其所有子文件
- Test: 验证目录已删除

**Interfaces:**
- Consumes: 更新后的 README.md 中关于 research/ 的说明
- Produces: 清理后的 `drafts/agent-book-beginner/` 目录

- [ ] **Step 1: 确认重复资料已存在于 raw/research/agent-frameworks/**

Run: `ls /home/weilan/workdir/selfcode/weilan-knowledge-wiki/raw/research/agent-frameworks/ | head -20`
Expected: 显示调研文件存在

- [ ] **Step 2: 删除 drafts/agent-book-beginner/research/**

Run:
```bash
git rm -r drafts/agent-book-beginner/research/
```
Expected: 命令成功，文件进入 staged 状态

- [ ] **Step 3: 验证删除结果**

Run: `find /home/weilan/workdir/selfcode/weilan-knowledge-wiki/drafts/agent-book-beginner/research -type f 2>/dev/null || echo "目录已删除"`
Expected: 输出 "目录已删除"

- [ ] **Step 4: 提交**

```bash
git commit -m "chore: 删除 drafts/agent-book-beginner/research/ 重复资料"
```

---

### Task 4: 更新 index.md 中的 Drafts 分类

**Files:**
- Modify: `index.md`
- Test: 读取更新后的 index.md

**Interfaces:**
- Consumes: 当前 index.md 中的 Drafts 分类
- Produces: 使用 wiki-link 的 Drafts 分类条目

- [ ] **Step 1: 读取 `index.md` 中 Drafts 分类**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/index.md` 相关行
Expected: 定位到 `## Drafts` 小节

- [ ] **Step 2: 将 Markdown 链接改为 wiki-link**

将：
```markdown
[Agent 系统入门书稿](drafts/agent-book-beginner/README.md) —— 面向小白开发者的 Agent 系统入门书（实习生比喻版）
```

改为：
```markdown
[[agent-book-beginner]] —— 面向小白开发者的 Agent 系统入门书（实习生比喻版）
```

- [ ] **Step 3: 验证更新**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/index.md` 相关行
Expected: Drafts 条目使用 `[[agent-book-beginner]]`

- [ ] **Step 4: 提交**

```bash
git add index.md
git commit -m "docs: index.md Drafts 分类使用 wiki-link"
```

---

### Task 5: 在 log.md 中记录治理落地

**Files:**
- Modify: `log.md`
- Test: 读取更新后的 log.md

**Interfaces:**
- Consumes: 前述所有任务的完成状态
- Produces: 新的 log 条目

- [ ] **Step 1: 在 log.md 顶部追加记录**

在 `# Knowledge Forest 日志` 后的第一行插入：

```markdown
## [2026-07-27] policy | 制定 drafts/ 生命周期治理规范

**操作**: 制定并落地轻量约定型的 `drafts/` 治理规范。

**完成项**:
- 更新 `CLAUDE.md`：明确 `drafts/` 目录结构、README 模板、状态标签、与 wiki 的关系、完成后的去向。
- 更新 `drafts/agent-book-beginner/README.md`：补充状态标签 `writing`、当前进度、来源说明。
- 删除 `drafts/agent-book-beginner/research/`：原始调研资料已与 `raw/research/agent-frameworks/` 重复。
- 更新 `index.md`：Drafts 分类改用 wiki-link `[[agent-book-beginner]]`。

**规范要点**:
- `drafts/` 是 wiki 的下游产物，不是原始资料存储层。
- 每个 draft 项目必须有 `README.md` 并标注五种状态之一：`planning` / `writing` / `review` / `published` / `archived`。
- `published` 或 `archived` 项目应在 30 天内移出 `drafts/`，归档到 `raw/archive/drafts/<project>/`。
```

- [ ] **Step 2: 验证 log.md**

Run: `Read /home/weilan/workdir/selfcode/weilan-knowledge-wiki/log.md` 前 30 行
Expected: 新条目位于最顶部，格式正确

- [ ] **Step 3: 提交**

```bash
git add log.md
git commit -m "docs: 记录 drafts/ 生命周期治理规范落地"
```

---

## Self-Review

- **Spec coverage**: 设计文档中的规范要点（目录结构、README 模板、状态标签、与 wiki 关系、完成去向、当前项目清理）均已对应到 Task 1-5。
- **Placeholder scan**: 无 TBD/TODO/"适当处理"等模糊表述。
- **Type consistency**: 不涉及代码类型，文件路径和 frontmatter 字段与现有仓库一致。
- **No test placeholders**: 每个任务的验证步骤使用具体的 Read 命令和预期输出。
