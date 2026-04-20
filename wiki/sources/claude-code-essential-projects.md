---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Claude Code 必备的三个开源项目.md
tags: [claude-code, open-source, claude-howto, oh-my-claudecode, best-practice, ai-programming]
---

# Claude Code 必备的三个开源项目

## 摘要

本文介绍了三个在 GitHub Trending 上同时出现并霸榜多日的 Claude Code 配套开源项目，标志着 AI 编程正在从「更聪明的自动补全」进化成「AI 团队协作」。第一个项目是 Claude How-To（25.4k+ stars），提供 10 个从基础到高级的交互式教程模块，覆盖 slash commands、memory、skills、subagents、MCP、hooks、plugins、checkpoints 等功能，配有 Mermaid 图、自测 quiz 和生产级模板，全程约 11-13 小时。第二个是 oh-my-claudecode（OMC），将 Claude Code 从单打独斗的工具变成多智能体协作系统，标准流程为 team-plan → team-prd → team-exec → team-verify → team-fix，含 19 个专业角色，支持智能模型路由（简单任务自动用 Haiku 节省 30-50% token 成本）。第三个是 claude-code-best-practice，由 Claude Code 核心团队成员 Boris Cherny、Thariq、Cat 等人的经验汇总，包含 50+ 实战技巧、工作流编排模板、9 种主流编码工作流横向对比。

## 核心要点

- **Claude How-To**：官方文档的「实战补全」，10 个模块覆盖 Claude Code 90% 的能力，配有生产级模板和自测 quiz，25.4k+ stars。
- **oh-my-claudecode（OMC）**：多智能体协作框架，标准流程 team-plan → team-prd → team-exec → team-verify → team-fix，19 个专业角色，底层用 tmux 运行多个 CLI worker 支持并行执行。
- **智能模型路由**：OMC 自动将简单任务路由到 Haiku 模型，节省 30-50% token 成本。
- **claude-code-best-practice**：核心团队内部经验汇总，50+ 技巧、工作流模板、9 种编码工作流对比，覆盖 Claude Code 2.1+ 所有能力。
- **趋势判断**：AI 编程从 autocomplete 进化到 team collaboration，多智能体 orchestration 开始有生产级框架出现（LangChain、Microsoft Agent Framework 等）。
- **行动建议**：Claude How-To 适合系统学习；OMC 适合复杂任务的多 Agent 协作；best-practice 适合当参考手册查阅。

## 原始文件

- [原始文件](../../raw/archive/Claude%20Code%20必备的三个开源项目.md)
