---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Claude Code + gstack 实战：如何用多 Agent 协作实现 10 倍提效.md
tags: [claude-code, gstack, multi-agent, team-mode, ai-programming, garry-tan]
---

# Claude Code + gstack 实战：如何用多 Agent 协作实现 10 倍提效

## 摘要

本文介绍了 Y Combinator 总裁 Garry Tan 开源的 Claude Code 技能包 gstack，其核心理念是将 Claude Code 从一个通用助手转变为完整的虚拟工程团队。gstack 提供 28 个专业角色（Skills），覆盖规划（/office-hours、/plan-ceo-review 等）、构建（/review、/investigate 等）、质量（/qa、/cso、/benchmark 等）、发布（/ship、/land-and-deploy、/canary 等）四个阶段。文章还详细介绍了 Team Mode（团队模式），允许同时启动多个 Agent 并行处理不同任务、相互通信、协作完成复杂项目。Garry Tan 声称用这套工作流 60 天写了 60 万行生产代码（35% 是测试）。文中给出了金融从业者 AI 内容创作工作流的实战案例，展示了从选题到发布的完整多 Agent 协作流程，将传统 4-6 小时的工作压缩到 40 分钟。

## 核心要点

- **gstack 的核心理念**：把 Claude Code 从「工具」变成「团队」，提供规划→构建→测试→发布的完整工程流程。
- **28 个专业角色**：通过 `/` 命令召唤，涵盖 CEO Review、架构设计、代码审查、QA 测试、安全审计、发布部署等全链路。
- **Team Mode（团队模式）**：支持多 Agent 并行处理不同任务、相互通信、协作完成复杂项目，典型场景如前端/后端/DevOps Agent 并行开发。
- **实际效果**：Garry Tan 60 天写 60 万行生产代码（35% 测试）；全栈应用开发从 8-10 小时缩短到 3-4 小时，总体提效 5-10 倍。
- **安装方式**：全局安装（`~/.claude/skills/gstack`）或项目级安装（`.claude/skills/gstack`，推荐用于团队协作）。
- **安全工具**：/careful（破坏性命令警告）、/freeze（编辑锁定）、/guard（全安全模式）、/codex（独立代码审查第二意见）。
- **实战工作流**：/office-hours（产品思路重构）→ /plan-ceo-review（需求审视）→ /plan-eng-review（架构把关）→ 编码 → /review（代码审查）→ /qa（自动化测试）→ /ship（发布）。
- **金融内容创作案例**：CEO Agent（选题）+ 数据分析 Agent（数据整理）+ 写作 Agent（撰写）+ 审核 Agent（校对），将 4-6 小时工作压缩到 40 分钟。

## 原始文件

- [原始文件](../../raw/archive/Claude%20Code%20+%20gstack%20实战：如何用多%20Agent%20协作实现%2010%20倍提效.md)
