---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [hermes-agent-guide, harness-engineering-guide]
tags: [hermes-agent, open-source, agent-memory, skills, mcp, nous-research]
---

# Hermes Agent

Hermes Agent 是 NousResearch 于 2026 年 2 月开源的 AI 智能体框架，口号为「The agent that grows with you」（跟你一起成长的 Agent）。不到 3 个月 GitHub 突破 10 万星，是当前增速最猛的开源 AI Agent 项目之一。

## 核心定位

Hermes 解决的，是大多数 AI 工具「用完归零」的根本性缺陷。它通过**闭合学习循环**和**三层持久记忆**，实现跨会话持续积累——越用越懂你。

## 核心特性

### 闭合学习循环（Closed Learning Loop）
每次完成复杂任务后，Agent 自动将成功经验总结为「Skill」（SKILL.md），存入技能库。下次同类任务直接调用。

**自动创建 Skill 的触发条件**：
- 完成了需要 5 步以上工具调用的复杂任务
- 碰到错误并找到了可行的解决路径
- 被纠正了操作方式，学到了更好的方法
- 发现了一个非显而易见的工作流程

### 三层持久记忆
| 文件 | 用途 |
|------|------|
| `MEMORY.md` | 通用记忆：任务笔记、技术偏好、常用路径、重要发现 |
| `USER.md` | 用户画像：背景、习惯、偏好、工作方式 |
| `SOUL.md` | Agent 人格：角色、语气、行为风格 |

配合 SQLite + FTS5 全文搜索引擎，Agent 可在任意时刻召回历史对话。记忆文件位于 `~/.hermes/` 目录下，可直接用文本编辑器查看和编辑。

### Skills Hub 技能市场
内置完整的技能搜索、预览、安装机制：
- `hermes skills browse` —— 浏览所有技能
- `hermes skills search <关键词>` —— 搜索技能
- `hermes skills install <来源/技能名>` —— 安装技能

**支持来源**：official（官方）、skills-sh（Vercel 公开目录）、well-known（网站标准化端点）、github、clawhub、lobehub

**Skill 的三级加载**：Level 0（技能列表，~3000 tokens）→ Level 1（完整内容）→ Level 2（参考文件），渐进式披露，按需加载。

### 多平台网关
支持 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant 等平台。一个 Gateway 进程同时监听多个平台，实现「随时随地访问你的 Agent」。

### 20+ LLM 提供商自由切换
OpenAI、Anthropic Claude、DeepSeek、Qwen、Gemini、GLM、Kimi、Moonshot、xAI Grok、GitHub Copilot、AWS Bedrock、Ollama 等。通过 `hermes model` 一键切换，无需改代码。所有模型需支持至少 64K 上下文窗口。

### 定时自动化
内置 cron 调度器，用自然语言描述即可创建定时计划：
> 每天早上 9 点，查看 Hacker News 的 AI 相关新闻，整理成中文摘要发到我的 Telegram

### MCP 原生集成
完整支持 [[mcp]] 协议，通过 `~/.hermes/config.yaml` 配置 MCP Server，可接入 GitHub、PostgreSQL、文件系统、Slack 等外部工具。

### AGENTS.md 项目级配置
在任意项目目录下创建 AGENTS.md，可为该项目提供专属上下文和指令，每次在该目录启动 Hermes 时自动加载。

## 终端执行后端

| 后端 | 特点 | 配置命令 |
|------|------|---------|
| local | 直接在本机执行（默认） | `hermes config set terminal.backend local` |
| docker | Docker 容器内隔离执行（推荐） | `hermes config set terminal.backend docker` |
| ssh | 连接到远程服务器执行 | `hermes config set terminal.backend ssh` |
| daytona | Serverless 持久化环境 | `hermes config set terminal.backend daytona` |
| modal | 按需唤醒，几乎零成本 | `hermes config set terminal.backend modal` |

## 与 Claude Code 的关系：互补而非竞争

| 维度 | Claude Code | Hermes Agent |
|------|-------------|--------------|
| 核心定位 | 专业编码工具，深度理解代码库 | 持久化自主 Agent，长期积累记忆和技能 |
| 生命周期 | 会话式，用完即止 | 常驻守护进程，持续运行 |
| 记忆机制 | 手动维护 CLAUDE.md / AGENTS.md | 自动三层持久记忆，无需手动维护 |
| 编码能力 | 同类最强 | 通用能力，编码不是强项 |
| 访问方式 | 终端 + IDE | 终端 + 15+ 即时通讯平台 |
| 模型 | 仅 Claude | 200+ 模型自由切换 |
| 开源 | 否（Anthropic 闭源） | 是（MIT 协议） |

**最佳组合**：Hermes 做大脑和调度（感知任务、维护长期记忆、定时触发、跨平台通信），Claude Code 做执行引擎（繁重编码任务）。

## 与 Harness Engineering 的对应

[[agent-harness]] 中的 Harness Engineering 方法论，Hermes Agent 将其产品化内置：

| Harness Engineering（手工方案） | Hermes Agent（产品化实现） |
|------------------------------|--------------------------|
| 手动维护 claude-progress.txt 和 AGENTS.md | 内置三层持久记忆，自动跨会话积累 |
| 手工编写 SKILL.md | 内置学习循环，自动提炼、存储、优化 Skill |
| 每次会话开始手动读取状态文件 | 常驻守护进程，持续运行，无需手动恢复 |
| 通过 git commit 追踪进度 | 支持 15+ 平台随时访问 |
| 手动配置 Initializer + Coding Agent 分工 | 内置 Planner/Generator/Evaluator 多 Agent 编排（开发中）|
| 绑定 Claude 模型 | 200+ 模型自由切换 |

## 相关来源

- [[hermes-agent-guide]] —— Hermes Agent 完全新手指南
- [[harness-engineering-guide]] —— Harness Engineering 完全指南（含 Hermes 产品化对应关系）
