---
type: entity
created: 2026-08-09
updated: 2026-08-09
sources: [mem0-in-context-17]
tags: [agent-wiki, code-documentation, cognition, devin, ai-coding]
---

# DeepWiki

Cognition 推出的公开代码库 wiki 服务，把 GitHub 仓库自动编译成结构化的 markdown 文档，供人类开发者和 AI coding agent 查阅。

## 基本信息

- **开发商**：Cognition
- **产品形态**：公开 Web 服务
- **使用方式**：将 GitHub 仓库 URL 中的 `github.com` 替换为 `deepwiki.com`，例如 `github.com/langchain-ai/langchain` → `deepwiki.com/langchain-ai/langchain`
- **覆盖范围**：超过 50,000 个最大的公开仓库（包括 MCP、LangChain 等）

## 核心组成

DeepWiki 为每个仓库生成：

- **架构摘要**（architecture overview）
- **文件索引**（file index）
- **依赖图**（dependency graph）
- **搜索功能**
- **源码链接**（每个 wiki 页面链接回原始代码）

## 关键定位：检索基础设施

DeepWiki 本身不是终端产品，而是 **Devin 的检索基础设施**。Devin 在理解或修改代码库时，先读取 DeepWiki 编译好的 wiki 页面，再定位到具体源码，从而减少重复读取整个代码库的成本。

这一模式体现了 Agent Wiki 的核心思想：在**摄入时编译知识**，而不是在每次查询时重新检索原始文件。

## 与类似产品对比

| 维度 | DeepWiki | [[openwiki]] | [[codegraph]] |
|---|---|---|---|
| 开发商 | Cognition | LangChain | 社区（colbymchenry） |
| 部署方式 | 公开云服务 | 本地 CLI | 本地 CLI / MCP server |
| 输出形态 | markdown 页面 | markdown 页面 | 代码知识图 |
| 隐私 | 仅支持公开仓库 | 本地，支持私有仓库 | 本地，支持私有仓库 |
| 主要读者 | Agent（Devin） | Agent + 人 | Agent |

## 局限

- 仅支持公开 GitHub 仓库
- 更新频率取决于 Cognition 的重编译周期
- 本质是文档型知识层，不提供代码级精确依赖关系

## 原始来源

- [[mem0-in-context-17]] —— mem0.ai In Context #17 对 Agent Wikis 的综述
