---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Hyper-Extract：一条命令把杂乱文档变成知识图谱.md
tags: [knowledge-graph, cli-tool, llm, document-processing]
---

# Hyper-Extract：一条命令把杂乱文档变成知识图谱

## 摘要

Hyper-Extract 是一个基于大语言模型的智能知识提取 CLI 工具，由 yifanfeng97 开发。用户只需一行命令即可将非结构化文档（如行业报告、论文、新闻）转换成 8 种结构化格式，包括知识图谱、时序图、超图、空间图等。工具内置 80 多个领域模板（覆盖金融、法律、医学、中医、工业等），支持中英文，并可通过 `he feed` 命令持续追加新文档让知识图谱"生长"。其核心思路是让 AI 直接输出结构化知识而非原始文本，解决传统文档处理中阅读效率低、信息孤岛、手工整理耗时等问题。

## 核心要点

- **8 种提取格式**：基础类型（AutoModel、AutoList、AutoSet）和进阶类型（AutoGraph、AutoHypergraph、AutoTemporalGraph、AutoSpatialGraph、AutoSpatioTemporalGraph），覆盖从简单结构化数据到复杂时空关系的多种场景
- **80+ 领域模板**：覆盖金融（财报分析、投资组合）、法律（合同条款、案例关系）、医学（病历结构、药品信息）、中医（方剂组成、经络穴位）、工业（设备参数、供应链）和通用（人物传记、事件时间线）六大领域
- **技术集成**：底层集成了 KG-Gen、iText2KG、GraphRAG、LightRAG、Hyper-RAG、Cog-RAG 等 10 余种前沿知识提取算法，自动选择最合适的方法
- **对比优势**：相比 GraphRAG 仅支持知识图谱，Hyper-Extract 支持时序、空间、超图等多维格式；相比传统 NLP 工具，使用 YAML 模板实现零代码定义
- **使用方式**：通过 `uv tool install hyperextract` 安装，配置 API Key 后使用 `he parse`、`he search`、`he show`、`he feed` 等命令完成从文档到知识图谱的完整工作流
- **项目地址**：github.com/yifanfeng97/Hyper-Extract

## 原始文件

- [原始文件](../../raw/archive/Hyper-Extract：一条命令把杂乱文档变成知识图谱.md)
