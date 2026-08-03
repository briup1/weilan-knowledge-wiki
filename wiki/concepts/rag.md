---
type: concept
created: 2026-04-20
updated: 2026-05-18
sources: [obsidian-knowledge-base, treesearch-retrieval, ai-knowledge-evolution]
tags: [rag, llm, retrieval, vector-search, knowledge-management]
---

# RAG (Retrieval-Augmented Generation)

RAG（检索增强生成）是一种将外部知识检索与大语言模型生成能力相结合的架构，通过在生成回答前先从知识库中检索相关上下文，解决大模型的知识时效性、幻觉和领域专精问题。

## 核心原理

RAG 的核心流程分为两个阶段：

1. **检索阶段**：将用户查询转换为检索请求，从外部知识库（文档、笔记、数据库）中召回与问题相关的文本片段。
2. **生成阶段**：将检索到的上下文与用户原始问题拼接为增强提示（augmented prompt），送入大语言模型生成最终回答。

检索阶段通常涉及以下技术：
- **文档切分**：将长文档分割为适合模型上下文窗口的文本块（chunk）。
- **嵌入编码**：使用向量模型（如 OpenAI text-embedding、nomic-embed-text）将文本块编码为高维向量。
- **向量检索**：通过近似最近邻（ANN）算法在向量数据库中快速召回语义相似的文本块。
- **重排序（Rerank）**：对召回结果进行精排，提升相关性。

## 与其他检索方式的对比

| 维度 | 向量检索 RAG | TreeSearch（非向量检索） |
|------|-------------|------------------------|
| 核心机制 | 语义相似度（向量嵌入+余弦距离） | 关键词匹配 + BM25 排序 |
| 外部依赖 | 需嵌入模型 + 向量数据库 | 仅 Python 标准库 + SQLite FTS5 |
| 文档结构 | 切分为文本块，丢失原始层级 | 保留 Markdown 标题树、代码 AST 等结构 |
| 查询延迟 | 数十到数百毫秒 | 单关键词 5-20ms，千万级文档 50-200ms |
| 成本 | 高（嵌入 API + 向量存储） | 极低（仅文件存储成本） |
| 适用语言 | 多语言通用 | 中文优化（jieba 分词） |
| 最佳场景 | 语义理解、开放问答、推荐 | 精确匹配、法律法条、代码库搜索 |

## 适用场景

- **企业知识库问答**：将内部文档、手册、规范接入 RAG，员工可用自然语言查询。
- **个人笔记助手**：如 Obsidian 配合本地嵌入模型实现完全离线的笔记 RAG 对话。
- **领域专家系统**：医学、法律等专业领域，通过检索权威文献增强回答可信度。
- **时效性内容**：新闻、股价等动态信息，通过检索最新文档弥补模型训练数据的截止日期限制。

## 相关脉络

- [[rag-thread]] —— RAG 技术栈模块化技能树：Chunking → Embedding → Retrieval → Generation → Evaluation

## NotebookLM 的七层架构视角

NotebookLM 是 RAG 产品化的标杆，其隐藏的技术架构揭示了高阶 RAG 的完整链路：

```
Source 接入
    ↓
文档理解（最难）—— 恢复标题层级、章节树、表格结构、图注
    ↓
多粒度 Chunk —— Source/Chapter/Section/Paragraph/Chunk/Sentence 六级
    ↓
混合索引 —— 向量索引 + BM25 + 元数据索引 + 文档树索引 + 引用索引
    ↓
Retrieval and Ranking —— Query Plan → 多路召回 → 相关性/可信度/引用质量排序
    ↓
Context Engineering —— 组装上下文包（证据 + 章节摘要 + source 摘要 + 历史对话）
    ↓
答案生成 —— 只基于资料、保守回答、关键结论绑定证据、冲突时指出矛盾
```

**关键洞察**：NotebookLM 把「开发者工具链」变成「用户产品」——把分块、向量化、TopK、重排模型等复杂配置收进系统内部。用户只感知「上传资料 → 提问 → 获得带引用的回答」。

**文档理解是上限决定层**：如果文档结构不能被正确还原（标题层级、表格、章节树），后续所有检索和生成都在「垃圾进垃圾出」的循环中。Google 在搜索、OCR、网页理解领域的 T0 积累是其天然优势。

## AI 知识库三阶段演进

| 阶段 | 名称 | 核心特征 |
|------|------|---------|
| 第一阶段 | 低配 RAG | 资料切块 → 向量化 → 检索 → 回答 |
| 第二阶段 | 产品化 RAG | 文档理解 → 多索引 → 检索排序 → 上下文工程 → Source Grounding |
| 第三阶段 | LLM Wiki | 知识抽取 → 实体识别 → 主题页生成 → 关系链接 → 冲突检测 → 持续演化 |

三个阶段是**逐层叠加**关系。LLM Wiki 的核心差异见 [[llm-wiki]]。

## 相关来源

- [[obsidian-knowledge-base]] —— 个人知识库搭建
- [[treesearch-retrieval]] —— 非向量检索方案
- [[ai-knowledge-evolution]] —— NotebookLM 七层架构与 LLM Wiki 演进
