---
type: concept
created: 2026-05-18
updated: 2026-05-18
sources: [ai-knowledge-evolution]
tags: [knowledge-management, llm-wiki, rag, knowledge-base, karpathy]
---

# LLM Wiki

LLM Wiki 是 Andrej Karpathy 于 2026 年 4 月提出的知识管理范式，核心思想是：**不是「查询时拼答案」，而是「提前把知识编译成可持续演化的知识结构」**。

## 核心问题

传统 RAG / NotebookLM / ChatGPT 文件上传的模式是：
> 上传资料 → 查询时召回相关片段 → 临时综合回答

问题是：每次问问题，模型都在重新从碎片里**现拼答案**，知识没有持续沉淀。同一类问题问 10 次，模型拼 10 次，且每次拼法可能不同。

LLM Wiki 的模式是：
> 原始资料不动 → LLM 读取资料 → 增量维护结构化 Wiki → 不断更新实体页、主题页、交叉引用、矛盾点和综合结论

## 与 RAG 的关系

| 维度 | 传统 RAG | NotebookLM（产品化 RAG）| LLM Wiki |
|------|---------|----------------------|---------|
| 核心动作 | 查询时检索+生成 | 查询时检索+生成+引用 | 提前编译+持续演化 |
| 知识沉淀 | 无，每次重新拼 | 弱，有摘要和笔记 | 强，结构化 Wiki 持续更新 |
| 矛盾检测 | 无 | 无 | 有，显式标记矛盾 |
| 交叉引用 | 无 | 弱 | 强，实体-关系-主题网络 |
| 演进性 | 无 | 弱 | 强，随新资料增量更新 |

NotebookLM 已经有一些 Wiki 化倾向（摘要、Study Guide、Briefing Doc、用户笔记、引用回溯），但还未达到 LLM Wiki 的「知识结构沉淀」层次。

## AI 知识库三阶段演进

```
第一阶段：低配 RAG
    资料切块 → 向量化 → 检索 → 回答

第二阶段：产品化 RAG（NotebookLM）
    文档理解 → 多索引 → 检索排序 → 上下文工程 → Source Grounding → 知识产品输出

第三阶段：LLM Wiki / 深度知识库
    知识抽取 → 实体识别 → 主题页生成 → 关系链接 → 冲突检测 → 增量更新 → 持续演化
```

三个阶段是**逐层叠加**而非替代关系：
1. 低配 RAG 是底座
2. NotebookLM 把底座产品化、自动化、可信化
3. LLM Wiki 再进一步，把知识结构沉淀为长期资产

## 关键设计原则

- **原始资料不可变**：作为事实来源永不修改，所有提炼都在 Wiki 层进行
- **增量维护**：新资料加入时，不是重建整个 Wiki，而是更新受影响的实体页和主题页
- **矛盾显式化**：当不同来源对同一事实给出矛盾信息时，在 Wiki 中显式标注，而非让模型自行「调和」
- **交叉引用网络化**：实体之间、实体与主题之间、主题与来源之间建立双向链接，形成可导航的知识网络

## 与现有知识的关联

- [[rag]] —— LLM Wiki 是 RAG 的演进方向之一
- [[notebooklm]] —— 产品化 RAG 的代表，已具 Wiki 化倾向
- [[knowledge-graph]] —— LLM Wiki 的实体-关系网络与知识图谱理念一致
- [[agent-memory-system]] —— Claude Code 的文件式记忆系统（MEMORY.md / USER.md）与 LLM Wiki 在「结构化、可增量更新」上有架构趋同
- [[obsidian]] —— 人类策展的知识管理工具，LLM Wiki 是 AI 自动维护的对应物

## 相关来源

- [[ai-knowledge-evolution]] —— AI 知识库技术演进拆解：从 RAG 到 NotebookLM，再到 LLM Wiki
