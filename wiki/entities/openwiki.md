---
type: entity
created: 2026-08-09
updated: 2026-08-09
sources: [mem0-in-context-17]
tags: [agent-wiki, code-documentation, langchain, open-source, ai-coding]
---

# OpenWiki

LangChain 开源的 CLI 工具，用于为代码库或个人来源自动生成并维护 Agent 可读的 markdown wiki。

## 基本信息

- **开发商**：LangChain
- **许可证**：MIT
- **仓库**：[langchain-ai/openwiki](https://github.com/langchain-ai/openwiki)
- **产品形态**：本地 CLI
- **安装**：`npm install -g openwiki`

## 两种模式

### Code Brain（默认）

为当前代码仓库生成文档：

```bash
cd your-repo
openwiki --init     # 首次初始化
openwiki --update   # 代码变更后更新
```

输出位于仓库内的 `openwiki/` 目录，包含项目概览、架构说明、API 索引等 markdown 文件。

### Personal Brain

把个人来源统一编译成本地 wiki：

```bash
openwiki personal --init
openwiki personal --update
```

输出位于 `~/.openwiki/wiki`，支持从以下来源摄入：

- Gmail
- Notion
- X / Twitter
- Hacker News
- Web search（通过 Tavily）
- 本地 git 仓库

## 核心命令

```bash
openwiki                              # 代码库交互式问答
openwiki "generate docs"              # 带初始请求的生成
openwiki -p "what can you do?"        # 一次性输出后退出
openwiki visualize                    # 打开交互式图谱 + markdown 阅读器
openwiki auth notion                  # 认证连接器
openwiki ingest gmail                 # 从指定来源摄入
```

## 关键设计

- **Markdown-first**：所有输出都是普通 markdown，人类和 Agent 都能读
- **Local-first**：Personal Brain 完全本地运行
- **CI 集成**：提供 GitHub Actions、GitLab CI、Bitbucket Pipelines 模板，可在每次 push 时自动更新文档

## 与 DeepWiki 的关系

OpenWiki 可视为 **DeepWiki 的开源本地版**：

- DeepWiki 是 Cognition 的公开云服务，只支持公开仓库
- OpenWiki 是 LangChain 的开源 CLI，支持私有仓库和个人来源

## 局限

- 仍处于早期阶段，部分功能（全文搜索、MCP 集成等）在路线图上
- 大规模代码库可能需要额外接入检索层
- 本质是文档型知识，不能替代代码结构图谱或用户记忆层

## 相关概念

- [[agent-wiki]] —— Agent Wiki 范式的抽象定义
- [[deepwiki]] —— Cognition 的公开代码 wiki 服务
- [[ai-coding-context-stack]] —— AI 辅助编程中的上下文基础设施分层

## 来源

- [[mem0-in-context-17]] —— mem0.ai In Context #17 对 Agent Wikis 的综述
