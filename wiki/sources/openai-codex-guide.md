---
type: source
created: 2026-05-14
updated: 2026-05-18
raw: raw/archive/OpenAI Codex 完全新手指南：Codex 凭什么和 Claude Code 抢饭碗？.md
tags: [openai-codex, codex, ai-programming, claude-code, openai]
---

# OpenAI Codex 完全新手指南：Codex 凭什么和 Claude Code 抢饭碗？

**来源**：微信公众号 / 程康健
**链接**：https://mp.weixin.qq.com/s/LwJpfvnZkqsKvk1HtddWGw

## 摘要

本文是 OpenAI Codex CLI（开源终端 AI 编程助手）和 Codex 桌面端 App 的完整新手教程。Codex 与 Claude Code 差异化竞争：Claude Code 在深度编码和复杂重构上更强，Codex 则在生态绑定（ChatGPT 订阅通用）、桌面端扩展能力（多 Thread 并行、Computer Use、自动化调度）和可拓展性上占优。

## 核心主张

1. **Codex CLI 三种操作模式**：Suggest（每次操作前确认，最安全，默认）/ Auto-edit（自动改文件，执行命令前确认）/ Full-auto（完全自主，仅建议在隔离环境使用）。通过 `--approval-mode` 或 `config.toml` 配置。
2. **Codex 桌面端 App 是「AI Agent 指挥中心」**（2026 年 2 月推出）：不是 CLI 的图形化包装，而是专为并行管理多 Agent 任务设计的全新产品。核心工作单元是 Thread（任务线程），支持 Local 模式和 Worktree 模式。
3. **桌面端独有功能**：
   - 多 Thread 并行运行（修复 Bug / 写测试 / 重构同时进行）
   - 内置浏览器（前端开发调试、截图给 Codex 参考视觉效果）
   - Computer Use（macOS 上操控 GUI 应用，截图理解 + 自动点击输入）
   - 自动化任务（Automations，定时或触发式后台任务）
   - 图像生成（GPT-image-1.5，生成 UI 设计稿、游戏素材）
   - 90+ 插件（GitHub、JIRA、Linear、Slack、Notion、Vercel 等）
4. **AGENTS.md 项目上下文**：类似 Claude Code 的 CLAUDE.md，Codex 会在 `~/.codex/AGENTS.md`、项目根目录、当前工作目录三个层级查找并合并，项目级配置优先级最高。
5. **MCP 完整支持**：通过 `config.toml` 配置 MCP 服务器，可接入 GitHub、PostgreSQL、文件系统、Slack 等外部工具。

## 关键洞察

- **与 Claude Code 的分工建议**：日常精细编码、大型重构 → Claude Code；多任务并行、团队自动化、桌面工作流 → Codex。
- **ChatGPT 订阅用户的零成本优势**：Plus/Pro 订阅已包含 Codex CLI 使用权限，无需额外 API Key。Plus 每 5 小时 30-150 条消息，Pro 300-1500 条。
- **Codex Cloud 云端 Agent**：运行在云端沙盒，支持并行多任务，每项任务在独立容器中运行，适合长时间后台任务。
- **Windows 桌面端比 CLI 更完善**：CLI 在 Windows 上仅实验性支持（推荐 WSL2），但桌面端 App 的 Windows 版可直接在 PowerShell 原生运行。
- **多智能体并行工作流**：Codex 支持将大型任务拆分为多个子 Agent 并行处理不同模块，但仍处于实验阶段。

## 与现有知识的关联

- 是 [[codex]] entity 的核心信息来源
- 与 [[claude-code]] 形成直接的竞品/互补对比关系
- AGENTS.md / MCP 与 [[agent-harness]]、[[mcp]] 概念一致
- 桌面端多 Thread 并行与 [[multi-agent-collaboration]] 的并行模式呼应

## 原始文件

- [原始文件](../../raw/archive/OpenAI%20Codex%20%E5%AE%8C%E5%85%A8%E6%96%B0%E6%89%8B%E6%8C%87%E5%8D%97%EF%BC%9ACodex%20%E5%87%AD%E4%BB%80%E4%B9%88%E5%92%8C%20Claude%20Code%20%E6%8A%A2%E9%A5%AD%E7%A2%97%EF%BC%9F.md)
