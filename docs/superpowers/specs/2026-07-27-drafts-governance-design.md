# 设计：Drafts 生命周期治理规范（轻量约定型）

## 背景

`drafts/` 是 LLM Wiki 的**下游产物层**：存放基于 `wiki/` 知识产出的半成品，如书稿、长文章、演讲稿、课程大纲等。它与 `wiki/` 的关键区别在于：

| 维度 | `wiki/` | `drafts/` |
|------|---------|-----------|
| 内容 | 结构化知识卡片 | 面向特定读者/目标的成篇内容 |
| 编辑者 | LLM 维护，人类审阅 | 人类主导，LLM 辅助 |
| 来源 | `raw/` 中的原始资料 | `wiki/synthesis/` + `raw/` |
| 生命周期 | 持续迭代 | 完成后发布或归档 |

本设计采用**轻量约定型**治理：不引入额外工具、注册表或自动化检查，仅通过目录结构、`README.md` 状态标签和清晰的去向规则，保持 `drafts/` 清爽、避免腐烂。

## 目录结构

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

## README.md 模板

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

## 状态标签

每个项目同一时刻只能有一个状态：

| 状态 | 含义 |
|------|------|
| `planning` | 还在构思、列大纲，没有正式开写 |
| `writing` | 正在撰写主体内容 |
| `review` | 内容基本完成，正在审阅/修改 |
| `published` | 已发布到外部平台，准备从 `drafts/` 移出 |
| `archived` | 不再继续，准备归档 |

## 与 wiki 的关系

- **drafts 是下游**：可以引用 wiki，但 wiki 不反向依赖 drafts。
- **发现新结论时向上游迁移**：如果写作过程中产生值得长期保留的洞察，应把它提取成 `wiki/concepts/` 或 `wiki/synthesis/`，而不是让它只存在于 draft 中。
- **引用方式**：章节中优先用 `[[page-name]]` wiki-link 引用 wiki 页面；外部链接用普通 Markdown 链接。

## 完成后的去向

一旦项目达到 `published` 或 `archived` 状态，应在 30 天内移出 `drafts/`：

- **`published`**：发布到外部平台后，将最终版本移到 `raw/archive/drafts/<project>/` 作为历史作品存档，或直接从仓库中删除。
- **`archived`**：未发布但不再继续，直接移到 `raw/archive/drafts/<project>/`。

`index.md` 的 Drafts 分类只保留 `planning` / `writing` / `review` 状态的项目。

## 对当前 `agent-book-beginner` 的处理

按照本规范，当前项目需要做一次清理：

1. **`research/` 目录应删除**：这些原始调研资料已经与 `raw/research/agent-frameworks/` 重复，不属于 drafts。
2. **`README.md` 补充状态标签和进度**：当前状态为 `writing`，需要明确章节完成情况。
3. **后续章节写作中**：遇到新结论时，判断是否应该提取到 wiki。

## 决策记录

- 选择轻量约定型而非结构型/出版流水线性，是因为当前只有一个 draft 项目，复杂治理的收益不足以抵消维护成本。
- 归档位置选择 `raw/archive/drafts/`，是因为已完成 drafts 本质上成为"历史资料"，与 `raw/archive/` 的"不可变历史资料"定位一致。
