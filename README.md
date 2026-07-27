# Knowledge Forest（知识森林）

一个以 Obsidian 仓库形式运作的 **LLM Wiki**——结构化、相互关联的 markdown 文件，位于用户与原始来源之间。

## 这是什么

这不是简单的笔记堆积，而是一个有明确架构、有工作流、有综合产出的个人知识系统：

- **raw/**：不可变的原始来源（文章、论文、转录稿、调研笔记）
  - `raw/assets/`：待入库的新文章和图片
  - `raw/archive/`：已入库并处理完毕的原始文件
- **wiki/**：由 LLM 生成和维护的结构化知识
  - `sources/`：每个被入库的来源摘要
  - `entities/`：谁/什么工具（产品、公司、项目、开源库、人）
  - `concepts/`：什么思想/方法（概念、模式、方法论）
  - `synthesis/`：跨来源的综合与领域全景
  - `queries/`：优质问答的归档
- **drafts/**：基于 wiki 产出的半成品（书稿、文章、演讲稿）
- **CLAUDE.md**：本仓库的架构、约定与工作流
- **index.md**：所有 wiki 页面和 draft 的目录
- **log.md**：只追加的操作日志

## 核心工作流

```
Ingest（摄取） → Query（查询） → Lint（巡检）
     ↑                                ↓
     └────── 知识复利循环 ←─────────┘
```

1. **Ingest**：将 `raw/assets/` 中的新来源编译进 wiki，创建 sources/entities/concepts/synthesis 页面
2. **Query**：基于 wiki 回答问题，优质答案归档到 `wiki/queries/`
3. **Lint**：定期检查死链、孤立页面、矛盾和陈旧主张

## 快速开始

1. 打开本仓库作为 Obsidian Vault（可选，但图谱视图很有用）
2. 将想学习的新文章放入 `raw/assets/`
3. 运行摄取脚本查看待处理文件：

   ```bash
   python .claude/skills/llm-ingest/scripts/ingest.py scan .
   ```

4. 让 Claude Code 执行 Ingest 流程，处理完成后源文件会自动移动到 `raw/archive/`
5. 查阅 `index.md` 浏览已有知识，或用 `log.md` 查看近期活动

## 关键约定

- **raw/ 只读**：原始来源一旦放入就不修改，需要更新时新增版本并注明
- **wiki/ 由 LLM 维护**：人类通过提问和审阅参与，不直接手动编辑页面
- **禁止死链**：所有 `[[page-name]]` 必须指向已存在的页面，或同时创建该页面
- **综合不可省略**：每篇新来源入库后，必须审视与现有知识体系的关系，产出或更新 synthesis

## 规模

- 约 39 个原始来源
- 约 70 个 wiki 页面
- 8 个跨领域 synthesis 全景图
- 持续增长的 queries/ 和 drafts/

详见 `CLAUDE.md` 了解完整规范。
