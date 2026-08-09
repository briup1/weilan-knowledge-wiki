---
type: source
created: 2026-08-09
updated: 2026-08-09
raw: raw/archive/mem0-in-context-17-agent-wikis.md
tags: [agent-wiki, ai-coding, mem0, cognition, langchain, gbrain, deepwiki, openwiki]
---

# mem0 In Context #17：Agent Wikis

mem0.ai 发表于 2026 年 7 月的 In Context 系列博客第 17 期，系统介绍了 Agent Wiki 这一范式，比较了 Cognition DeepWiki、Factory AutoWiki、LangChain OpenWiki 和 Garry Tan GBrain 四个实现，并区分了 wiki（文档集知识）与 memory（用户记忆）的边界。

## 核心主张

1. **编译在摄入时，而非查询时**：传统 RAG 每次提问都重新检索原始文档；Agent Wiki 在来源进入时一次性编译成 markdown 页面并持续维护。
2. **LLM Wiki 是持久、复利增长的产物**：知识被编译一次并持续保持最新，不必每次重新推导。
3. **三层结构**：来源文档 → markdown wiki → schema 文件（如 CLAUDE.md / AGENTS.md）。
4. **三个操作**：Ingest（入库）、Query（查询）、Lint（巡检）。
5. **Wiki 不是 Memory**：Agent Wiki 存储文档集知识；Mem0 等记忆层存储用户偏好和交互历史。

## 四个实现对比

| 产品 | 开发商 | 特点 |
|---|---|---|
| DeepWiki | Cognition | 公开云服务，替换 github.com 为 deepwiki.com 即可查看仓库 wiki |
| AutoWiki | Factory | 文档作为构建产物，支持 CI 自动更新 |
| OpenWiki | LangChain | 开源 CLI，支持代码库和个人来源 |
| GBrain | Garry Tan | 个人知识仓库的开源实现 |

## 关键限制

- 规模：无检索层时约 100 sources/数百页面效果最佳
- 准确性：编译摘要可能丢失细节
- 时效性：页面只和上次更新一样新
- 成本：生成和维护页面需要 token

## 与本仓库的关系

本文为 [[agent-wiki]] 概念页和 [[ai-coding-context-stack]] 综合页提供了核心来源，也是理解 [[deepwiki]]、[[openwiki]]、[[mem0]] 三者关系的关键文本。

## 原始文件

- [原始文件](../../raw/archive/mem0-in-context-17-agent-wikis.md)
