---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [openai-codex-guide]
tags: [openai, codex, ai-programming, terminal, agent]
---

# OpenAI Codex

OpenAI Codex 是 OpenAI 官方推出的 AI 编程助手生态，包含 Codex CLI（开源终端工具）和 Codex 桌面端 App（2026 年 2 月推出）。与 Claude Code 差异化竞争：Codex 在生态绑定、桌面端扩展能力和可拓展性上占优，Claude Code 在深度编码和复杂重构上更强。

## 核心组件

### Codex CLI
开源终端 AI 编程助手，托管于 GitHub `openai/codex`，Rust 编写。

**三种操作模式**：
| 模式 | 说明 | 适用场景 |
|------|------|---------|
| Suggest（建议） | 每次操作前展示计划并等待确认 | 新手默认，最安全 |
| Auto-edit | 自动修改文件，执行命令前确认 | 对 AI 有一定信任的场景 |
| Full-auto | 完全自主执行，无需确认 | 仅建议在隔离环境或 CI/CD 中使用 |

### Codex 桌面端 App
专为并行管理多 Agent 任务设计的「AI Agent 指挥中心」，不只是 CLI 的图形化包装。

| 特性 | CLI | 桌面端 App |
|------|-----|-----------|
| 多任务 | 单线程 | 多 Thread 并行 |
| Git 集成 | 手动 | 内置 diff/commit/PR |
| 浏览器 | 不支持 | 内置浏览器 |
| Computer Use | 不支持 | 支持（macOS） |
| 图像生成 | 不支持 | GPT-image-1.5 |
| 自动化调度 | 不支持 | 定时/长期任务 |

**桌面端独有功能**：
- **Thread（任务线程）**：Local 模式（直接操作项目）或 Worktree 模式（独立 Git 分支隔离变更）
- **内置浏览器**：前端调试、截图给 Codex 参考视觉效果
- **Computer Use**：macOS 上操控 GUI 应用（截图理解 + 自动点击输入）
- **自动化任务（Automations）**：定时或触发式后台任务（如每天早上检查 GitHub Issues）
- **90+ 插件**：GitHub、JIRA、Linear、Slack、Notion、Vercel 等

## 项目上下文：AGENTS.md

类似 Claude Code 的 CLAUDE.md，Codex 在三个层级查找并合并 AGENTS.md：
1. `~/.codex/AGENTS.md`（全局）
2. 项目根目录 `AGENTS.md`（项目级，优先级最高）
3. 当前工作目录 `AGENTS.md`（细粒度）

## 认证与成本

- **ChatGPT 订阅用户零成本**：Plus/Pro/Business/Edu/Enterprise 订阅已包含 Codex CLI 权限
- Plus：每 5 小时 30-150 条消息；Pro：300-1500 条
- Plus 额外赠送 $5 API 额度，Pro 赠送 $50（30 天内有效）
- 也支持 OpenAI API Key 方式（更灵活，但部分云端功能不可用）

## 与 Claude Code 的分工

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 日常精细编码、大型重构 | [[claude-code]] | 深度代码理解，同类最强 |
| 多任务并行、桌面自动化 | Codex | 多 Thread 并行、Computer Use |
| 已有 ChatGPT 订阅 | Codex | 零额外成本 |
| Windows 原生开发 | Codex 桌面端 | Windows 支持比 CLI 更完善 |

## MCP 支持

通过 `~/.codex/config.toml` 配置 MCP 服务器，完整支持 [[mcp]] 协议，可接入 GitHub、PostgreSQL、文件系统、Slack 等。

## 相关来源

- [[openai-codex-guide]] —— OpenAI Codex 完全新手指南
