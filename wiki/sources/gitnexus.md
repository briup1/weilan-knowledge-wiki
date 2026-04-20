---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/GitNexus Zero-Server Code Intelligence Engine.md
tags: [code-intelligence, knowledge-graph, mcp, code-exploration, graph-rag]
---

# GitNexus：零服务器代码智能引擎

## 摘要

GitNexus 是一个客户端代码知识图谱构建工具，由 abhigyanpatwari 开发，可在浏览器中完全运行（零服务器）。用户只需拖入 GitHub 仓库或 ZIP 文件，即可获得交互式代码知识图谱，并内置 Graph RAG Agent 用于代码探索。项目提供 CLI + MCP 和 Web UI 两种使用方式：CLI 通过 MCP 协议为 Cursor、Claude Code、Codex 等 AI 编辑器提供深度代码库感知能力；Web UI 则提供浏览器内的可视化图谱探索和 AI 对话。核心技术包括 Tree-sitter AST 解析、LadybugDB 图数据库、Leiden 社区检测、BM25+语义+RRF 混合搜索，支持 14 种编程语言。

## 核心要点

- **两种使用模式**：CLI + MCP（本地索引，连接 AI Agent，适合日常开发）和 Web UI（浏览器内可视化探索，无需安装，受限于浏览器内存约 5k 文件）
- **MCP 集成**：为 AI Agent 暴露 16 个工具（11 个单仓库 + 5 个多仓库组），包括 query（混合搜索）、context（360 度符号视图）、impact（影响范围分析）、detect_changes（Git diff 影响映射）、rename（多文件协调重命名）、cypher（原始 Cypher 图查询）
- **核心创新——预计算关系智能**：在索引时预计算聚类、调用链追踪和置信度评分，工具一次调用返回完整上下文，避免传统 Graph RAG 中 LLM 需要多次查询的问题
- **六阶段索引流水线**：Structure（文件树）→ Parsing（Tree-sitter AST）→ Resolution（跨文件导入/调用解析）→ Clustering（Leiden 社区检测功能聚类）→ Processes（执行流追踪）→ Search（混合搜索索引）
- **14 种语言支持**：TypeScript、JavaScript、Python、Java、Kotlin、C#、Go、Rust、PHP、Ruby、Swift、C、C++、Dart，涵盖导入解析、命名绑定、导出检测、继承关系、类型注解等
- **Agent Skills**：自动安装 4 个技能（Exploring、Debugging、Impact Analysis、Refactoring）到 `.claude/skills/`，`--skills` 模式下还会为每个检测到的功能区域生成 repo-specific SKILL.md
- **Wiki 生成**：`gitnexus wiki` 命令可基于知识图谱自动生成 LLM 驱动的仓库文档
- **多仓库架构**：全局注册表 `~/.gitnexus/registry.json`，一个 MCP 服务器可服务多个已索引仓库，无需每个项目单独配置
- **技术栈**：Node.js/Tree-sitter native（CLI）、Browser/WASM（Web）、LadybugDB 图数据库、Sigma.js 可视化、transformers.js 嵌入

## 原始文件

- [原始文件](../../raw/archive/GitNexus Zero-Server Code Intelligence Engine.md)
