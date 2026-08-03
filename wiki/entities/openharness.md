---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [superpowers-guide]
tags: [openharness, ai-programming, agent-runtime, harness, python, domestic-models]
---

# OpenHarness

开源的 Python 实现 AI 代理运行时（Agent Harness），解决基础设施层的问题：模型提供智能，Harness 提供"手、眼睛、记忆和安全边界"。

## 基本信息

| 属性 | 内容 |
|------|------|
| 项目地址 | [github.com/HKUDS/OpenHarness](https://github.com/HKUDS/OpenHarness) |
| 当前版本 | v0.1.0（2026 年 4 月发布）|
| Star 数 | 8.6k+ |
| 本质定位 | 代理运行引擎（独立程序）|
| 启动命令 | `oh` |

## 核心特点

- **独立运行**：不依附于 Claude Code 或 Cursor 等现有工具
- **内置 43 个工具**：文件操作、Shell、Web 搜索、MCP 等
- **权限管控 + React TUI 界面 + 多代理调度**
- **多模型后端**：Anthropic、OpenAI 兼容、GitHub Copilot
- **国内模型原生支持**：通义千问、DeepSeek、Kimi 等
- **兼容 Superpowers Skills 格式**和 Claude Code 插件格式

## 与其他三款工具的定位差异

| 工具 | 定位 | 是否独立运行 |
|------|------|-------------|
| Superpowers | 工作流规范 | 否（寄生）|
| BMAD Method | 文档驱动框架 | 否（寄生）|
| OpenSpec | 需求规格框架 | 否（寄生）|
| **OpenHarness** | **代理运行引擎** | **是（独立）** |

## 适用场景

- **研究代理原理**：想深入理解代理内部运作机制的开发者
- **国内模型用户**：需要原生支持通义千问、DeepSeek、Kimi 等模型的类 Claude Code 体验
- **自建场景**：希望完全控制代理运行基础设施的团队

**注意**：OpenHarness 于 2026 年 4 月才发布 v0.1.0，是四款工具中最新的，生态尚不成熟。如果目标是"快速上手提升开发效率"，不建议从 OpenHarness 开始。

## 与 Agent Harness 概念的关系

OpenHarness 是 [[agent-harness]] 概念的一个具体实现，提供了完整的运行时基础设施——工具系统、权限管控、记忆管理、多代理调度等。

## 相关实体

- [[superpowers]] —— 兼容其 Skills 格式
- [[bmad-method]] —— 文档驱动敏捷框架
- [[openspec]] —— 需求规格框架
- [[claude-code]] —— 薄 Harness 哲学的代表
- [[langgraph]] —— 厚 Harness 哲学的代表

## 相关概念

- [[agent-harness]] —— Agent Harness 十二大模块的系统框架

## 相关来源

- [[superpowers-guide]] —— 四款工具的横向对比与选型建议
