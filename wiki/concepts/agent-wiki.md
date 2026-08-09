---
type: concept
created: 2026-08-09
updated: 2026-08-09
sources: [mem0-in-context-17]
tags: [agent-wiki, knowledge-management, ai-agent, llm-wiki, rag]
---

# Agent Wiki

一种知识管理范式：让 LLM 在**摄入阶段**一次性编译来源文档，生成结构化的 markdown wiki，并在来源变化时持续维护，从而避免每次查询都重新从原始文档中检索信息。

## 核心思想

传统 RAG 的工作方式是：

> 每次提问 → 切分文档 → 嵌入检索 → 拼接上下文 → 生成答案

Agent Wiki 的工作方式是：

> 摄入来源 → LLM 生成/更新 wiki 页面 → 查询时直接读 wiki

把计算成本从“每次查询”转移到“摄入时”，同时产生一个**持久、复利增长**的知识产物。

## 三层结构

典型的 Agent Wiki 系统包含三层：

1. **来源层（Source Documents）**：原始文章、论文、代码库，只读
2. **Wiki 层（Markdown Wiki）**：LLM 生成的 markdown 页面，包含摘要、专题页、交叉链接
3. **Schema 层（Schema File）**：如 `CLAUDE.md`、`AGENTS.md`，定义 wiki 结构和维护任务

## 三个核心操作

- **Ingest（入库）**：LLM 读取新来源，更新相关 wiki 页面
- **Query（查询）**：用户提问，Agent 读取 wiki 生成答案
- **Lint（巡检）**：LLM 检查 wiki 内部矛盾、过时信息、孤立页面

## 与 RAG 的对比

| 维度 | RAG | Agent Wiki |
|---|---|---|
| 成本发生时机 | 每次查询 | 摄入时 |
| 产物 | 无持久产物 | 持久的 markdown wiki |
| 第十次回答 | 和第一次一样从零构建 | 基于持续维护的 wiki，可能更优 |
| 规模边界 | 可扩展到大文档集 | 中等规模（~100 sources）效果最佳，更大需加检索层 |
| 准确性风险 | 低（基于原始文本） | 中（摘要可能丢失细节，错误会累积） |

## 典型实现

| 产品 | 特点 |
|---|---|
| [[deepwiki]] | Cognition 的公开云服务，编译 GitHub 公开仓库 |
| [[openwiki]] | LangChain 的开源 CLI，支持代码库和个人来源 |
| GBrain | Garry Tan 的开源个人知识仓库版本 |

## 关键限制

1. **规模限制**：无检索层时适合约 100 个来源/数百页面
2. **准确性风险**：编译时丢失的细节会在后续回答中持续存在
3. **时效性**：页面只和上次更新一样新
4. **成本**：生成和维护页面需要 token，可能产生无人阅读的页面

## 不是记忆

Agent Wiki 存储的是**文档集知识**，不是**用户记忆**。它回答“这些文档包含什么”，不回答“这个用户上周做了什么决定”。后者属于 [[agent-memory-system|Agent 记忆系统]] 的范畴。

## 来源

- [[mem0-in-context-17]] —— mem0.ai In Context #17 对 Agent Wikis 的综述
