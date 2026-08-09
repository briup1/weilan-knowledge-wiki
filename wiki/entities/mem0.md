---
type: entity
created: 2026-08-09
updated: 2026-08-09
sources: []
tags: [agent-memory, mem0, long-term-memory, ai-agent, personalization]
---

# Mem0

面向 LLM 和 AI Agent 的开源记忆层，用于提取、存储和检索用户级别的长期记忆，实现跨会话、跨应用的个性化上下文。

## 基本信息

- **名称**：Mem0（发音 mem-zero）
- **定位**：智能、开源的 Agent 记忆层
- **产品形态**：开源库 / 云服务 / 自托管
- **GitHub**：github.com/mem0ai/mem0
- **融资**：已获 2400 万美元 A 轮融资

## 核心能力

- **长期记忆**：突破固定上下文窗口，让 Agent 记住跨会话的信息
- **多作用域记忆**：
  - session-level（会话级）
  - user-level（用户级）
  - agent-level（Agent 级）
  - org-level（组织级）
  - 自定义 collection
- **混合检索**：向量嵌入 + BM25 + 实体/关系图
- **记忆维护**：自动执行 ADD / UPDATE / DELETE / NOOP 操作
- **框架无关**：可集成 LangChain、CrewAI、OpenAI Agents、AgentScope 等

## 记忆流水线

1. **提取（Extraction）**：从对话中提取关键事实
2. **更新（Update）**：动态维护记忆，处理冲突和过时信息
3. **检索（Retrieval）**：根据当前查询召回相关记忆
4. **注入（Injection）**：把相关记忆注入 Agent 上下文

## 典型用法

```python
from mem0 import Memory

m = Memory()
m.add("User prefers FastAPI over Django", user_id="u123")
results = m.search(query="web framework preference", user_id="u123")
```

## 与 Agent Wiki 的区别

这是 mem0 官方文章强调的核心区分：

| 维度 | Agent Wiki（DeepWiki / OpenWiki） | Agent Memory（Mem0） |
|---|---|---|
| 输入 | 文档/代码集 | 用户交互、对话、反馈 |
| 绑定对象 | 仓库/文档集 | 用户 / Agent |
| 回答的问题 | “这些文档/代码包含什么？” | “这个用户之前做过什么、偏好什么？” |
| 数据形态 | 知识（knowledge） | 记忆（memory） |

一句话：**Wiki 给你文档集知识；Memory 给你用户记忆。**

## 在编码场景中的作用

- 记住用户代码风格偏好（如“必须加类型提示”）
- 记住历史失败经验（如“上次同步 SQLAlchemy 导致死锁”）
- 记住项目约定和已被否决的方案
- 在跨会话、跨工具时保持一致性

## 与 Claude Code 内置记忆的关系

Claude Code 已有 [[agent-memory-system|文件式记忆系统]]（`~/.claude/projects/<project>/memory/`），分为 user / feedback / project / reference 四类。

选择 Mem0 的场景：
- 需要跨多个 Agent 工具共享记忆
- 需要跨应用记忆（不只是 Claude Code）
- 需要更结构化的 memory API
- 需要 user / agent / org 多层作用域

Claude Code 内置记忆已够用的场景：
- 只在 Claude Code 内工作
- 记忆主要服务于单个项目
- 偏好完全本地、无外部服务

## 相关概念

- [[agent-memory-system]] —— Agent 记忆系统的通用概念与 Claude Code 实现
- [[ai-memory-vs-human-km]] —— AI 记忆系统与人类知识管理的趋同与分野
- [[ai-coding-context-stack]] —— AI 辅助编程中的上下文基础设施分层

## 参考

- 官方博客：[Long-Term Memory for AI Agents](https://mem0.ai/blog/long-term-memory-ai-agents)
- 对比文章：[Mem0 vs Letta: AI Agent Memory Frameworks Compared](https://aiagentmemory.org/articles/mem0-vs-letta/)
