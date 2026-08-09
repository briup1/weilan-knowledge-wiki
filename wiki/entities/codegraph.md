---
type: entity
created: 2026-08-09
updated: 2026-08-09
sources: []
tags: [code-knowledge-graph, ai-coding, mcp, local-first, tree-sitter]
---

# CodeGraph

面向 AI coding agent 的本地代码知识图工具，通过 tree-sitter 解析代码结构，把文件、函数、类、调用关系等建模成图，供 Agent 精确导航。

## 基本信息

- **作者**：colbymchenry（社区项目）
- **仓库**：[github.com/colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
- **产品形态**：本地 CLI + MCP server
- **存储后端**：SQLite
- **解析引擎**：tree-sitter

## 核心能力

- **预索引代码知识图**：在 Agent 提问前就把代码结构解析成图
- **减少 Agent 开销**：宣称可减少 47% token 消耗和 58% tool call 次数
- **100% 本地**：无需上传代码到云端
- **MCP 集成**：可作为 MCP server 被 Claude Code、Cursor、Codex 等调用
- **多 Agent 支持**：兼容 Claude Code、Codex、Gemini、Cursor、OpenCode、AntiGravity、Kiro、Hermes 等

## 图模型

CodeGraph 把代码中的实体建模为节点，关系建模为边，典型元素包括：

- 文件（file）
- 函数（function）
- 类（class）
- 导入/依赖（import / dependency）
- 调用关系（calls）
- 继承/实现关系（extends / implements）

## 与 OpenWiki / DeepWiki 的关系

| 维度 | OpenWiki / DeepWiki | CodeGraph |
|---|---|---|
| 输出 | markdown 文档 | 代码知识图 |
| 回答的问题 | “这个模块是做什么的？” | “这个函数被谁调用了？” |
| 知识形态 | 语义摘要 | 显式结构关系 |
| 最佳使用阶段 | 任务开始前建立上下文 | 任务执行中精确定位 |

三者可组合使用：OpenWiki 提供高层语义，CodeGraph 提供精确导航，Mem0 提供用户记忆。

## 局限

- 解析质量受 tree-sitter 语法支持和代码复杂度影响
- 图的规模和密度可能影响查询性能
- 主要面向 Agent 工具调用，对人类直接可读性较低

## 相关概念

- [[knowledge-graph]] —— 知识图谱的通用概念与代码知识图谱特化
- [[ai-coding-context-stack]] —— AI 辅助编程中的上下文基础设施分层

## 参考

- 官方 GitHub 仓库：[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
- 本仓库相关概念页：[[knowledge-graph-tools-comparison]]
