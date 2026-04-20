---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/fireworks-tech-graph：用自然语言生成工业级架构图，Claude Code 绘图神器！.md
tags: [fireworks-tech-graph, claude-code-skills, architecture-diagram, svg, ai-drawing, mermaid]
---

# fireworks-tech-graph：用自然语言生成工业级架构图

## 摘要

本文介绍了 fireworks-tech-graph，一个 Claude Code Skill，允许用户用自然语言描述系统，即可生成专业级的 SVG + PNG 架构图。相比 Mermaid 需要学习 DSL 语法、draw.io 需要手动操作，fireworks-tech-graph 完全通过自然语言输入即可产出精美图表。它提供 5 种视觉风格（Flat Icon、Dark Terminal、Blueprint、Notion Clean、Glassmorphism）、8 种图表类型（架构图、数据流图、流程图、Agent 架构图、记忆架构图、序列图、对比图、思维导图），内置 AI/Agent 领域知识（RAG Pipeline、Agentic RAG、Mem0、Multi-Agent 等模式），语义化的形状和箭头系统，以及 40+ 产品图标（OpenAI、Anthropic、LangChain、Pinecone、AWS 等）。输出为 SVG（可编辑）+ PNG（1920px，可直接嵌入）。

## 核心要点

- **核心优势**：自然语言输入即可生成工业级架构图，无需学习 Mermaid DSL 或在 GUI 中手动操作。
- **5 种视觉风格**：Flat Icon（默认，博客/文档）、Dark Terminal（GitHub README/开发者文章）、Blueprint（架构文档/工程图）、Notion Clean（Notion/Confluence/Wiki）、Glassmorphism（产品网站/演讲）。
- **8 种图表类型**：架构图、数据流图、流程图、Agent 架构图、记忆架构图、序列图、对比图、思维导图。
- **AI/Agent 内置模式**：RAG Pipeline、Agentic RAG、Agentic Search、Mem0 Memory Layer、Agent Memory Types（感知/工作/情景/语义/程序）、Multi-Agent、Tool Call Flow。
- **语义形状词汇**：用户/人类（圆形+身体）、LLM（圆角矩形双边框+闪电）、Agent/编排器（六边形）、Vector Store（带内环圆柱）、Graph DB（三圆簇）等，形状语义在所有风格中保持一致。
- **箭头语义系统**：主数据流（2px 实线）、控制触发（1.5px 实线）、记忆读取（1.5px 实线）、记忆写入（1.5px 虚线）、异步事件（1.5px 虚线）、反馈循环（1.5px 曲线）。
- **40+ 产品图标**：覆盖 AI/ML（OpenAI、Anthropic、Gemini、LLaMA）、AI 框架（LangChain、LlamaIndex、CrewAI）、向量数据库（Pinecone、Weaviate、Chroma）、数据库（PostgreSQL、MongoDB、Redis）、消息队列（Kafka、RabbitMQ）、云服务（AWS、GCP、Azure、Vercel）等。
- **安装方式**：Claude Skills 安装（`claude skills install fireworks-tech-graph`）或手动克隆到 `~/.claude/skills/`。
- **触发词**：「画图」「帮我画」「生成图」「架构图」「流程图」「可视化一下」「generate diagram」「draw diagram」等。

## 原始文件

- [原始文件](../../raw/archive/fireworks-tech-graph：用自然语言生成工业级架构图，Claude%20Code%20绘图神器！.md)
