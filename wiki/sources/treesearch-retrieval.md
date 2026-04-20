---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/告别向量模型！TreeSearch 让文档检索回归本质.md
tags: [document-retrieval, bm25, sqlite, rag-alternative, keyword-search]
---

# TreeSearch：无需向量模型的结构感知文档检索系统

## 摘要

TreeSearch 是由 shibing624 开发的开源文档检索系统，提供了一种完全不同于传统 RAG 的检索方案。它不使用任何向量模型或嵌入，仅依赖 Python 标准库和 SQLite 的 FTS5 全文搜索引擎，通过关键词匹配 + BM25 排序实现毫秒级（<50ms）的文档检索。其核心设计是保留文档的原始树状结构（Markdown 标题层级、代码 AST、JSON/XML 结构等），而非将文档切割成碎片。对于精确匹配需求强的场景（如法律法条库、医学文献库、代码库搜索），TreeSearch 在成本和性能上具有显著优势——1000 万文档的法条库场景下，成本仅为传统 RAG 方案的 1/1000。

## 核心要点

- **零向量依赖**：不使用任何嵌入模型或向量数据库，核心仅依赖 Python 标准库 + SQLite FTS5，实现真正的零外部依赖
- **结构感知索引**：解析并保留文档的原始层级结构——Markdown 的 H1-H6 标题树、Python AST（类/函数/方法）、TreeSitter 多语言代码（40+ 语言）、JSON/XML/CSV 结构
- **FTS5 + BM25**：利用 SQLite 内置的 FTS5 全文搜索引擎（倒排索引 + BM25 相关性排序，与 Elasticsearch 同款算法），查询复杂度 O(log N)
- **结构感知列权重**：title（权重 5.0）、body（10.0）、summary（2.0）、code_blocks（1.0）、front_matter（2.0），支持字段级精确搜索如 `title:authentication AND body:config`
- **多格式支持**：Markdown、Python、多语言代码（TreeSitter）、JSON、CSV、XML、PDF（可选）、DOCX（可选）、HTML（可选）
- **性能指标**：100 个 Markdown 文件索引 <1s；1000 个代码文件 <10s；单关键词查询 5-20ms；1000 万文档查询 50-200ms；内存占用仅为 Elasticsearch 的 1/10
- **成本对比**：1000 万文档法条库，传统 RAG 首年成本 $200,000+，TreeSearch 仅需 $100-200 存储成本
- **适用场景**：精确匹配需求强（法律、医学）、文档结构重要（法律层级、代码结构）、成本敏感、离线部署、中文为主（jieba 分词优化）
- **不适用场景**：超大规模（百亿+）、复杂聚合统计、语义理解（问答/推荐）、多语言混合

## 原始文件

- [原始文件](../../raw/archive/告别向量模型！TreeSearch 让文档检索回归本质.md)
