---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Hermes Agent 教程（1）：本地启动与项目结构.md
tags: [hermes-agent, nous-research, agent-framework, python, uv, open-source]
---

# Hermes Agent 教程（1）：本地启动与项目结构

## 摘要

本文是 Hermes Agent 系列教程的第一篇，介绍了由 NousResearch 开源的 Hermes Agent 项目的本地启动流程和详细项目结构。Hermes Agent 是一个功能丰富的 AI Agent 框架，使用 uv 进行 Python 包管理，支持通过 `hermes doctor` 检查环境、`hermes model` 选择模型后启动。文章详细展示了项目的树形结构，核心模块包括 agent（Agent 核心逻辑和执行引擎）、gateway（API 网关、请求路由、钩子系统）、hermes_cli（CLI 命令行接口）、tools（工具系统和工具调用解析器）。项目还拥有庞大的 skills 体系，覆盖苹果生态、AI Agent 集成、创意工具、数据科学、DevOps、GitHub 集成、MCP、MLOps、笔记应用、生产力工具、研究工具、智能家居、社交媒体、软件开发等数十个领域。此外还包含可选技能扩展（optional-skills）、插件系统（含 8 种内存实现）、ACP 协议适配器、完整的测试套件、Docker/Nix 部署配置等。

## 核心要点

- **Hermes Agent**：NousResearch 开源的 AI Agent 框架，GitHub 地址 github.com/NousResearch/hermes-agent。
- **本地启动流程**：git clone → cd 项目 → `uv venv` → `source .venv/bin/activate` → `uv sync` → 配置 .env → `hermes doctor` → `hermes model` → `hermes` 启动。
- **核心框架模块**：agent/（核心逻辑）、gateway/（API 网关 + 钩子 + 多平台适配）、hermes_cli/（CLI 接口）、tools/（工具系统 + 浏览器供应商 + 环境配置）。
- **Skills 体系**：覆盖苹果生态、AI Agent（Claude Code、Codex、OpenCode 等）、创意工具、数据科学、DevOps、GitHub 集成、MCP、MLOps、Obsidian/Notion 笔记、生产力工具、研究工具、智能家居、社交媒体、软件开发等。
- **内存插件**：8 种内存实现，包括 Byterover、Hindsight、Holographic、Honcho、Mem0、OpenViking、RetainDB、SuperMemory。
- **可选技能扩展**：自主 AI Agent、区块链、Blender 3D、Docker 管理、脑机接口、FastMCP、数据迁移、高级 MLOps（17 个子模块）、研究高级工具（7 个子模块）、安全工具等。
- **测试与部署**：完整测试套件（单元测试、集成测试、e2e、基准测试）、Docker 配置、Nix 声明式配置、Homebrew 公式。
- **根目录核心文件**：cli.py（~410KB 主入口）、run_agent.py（~500KB 执行引擎）、batch_runner.py（批量任务）、rl_cli.py（强化学习 CLI）、mcp_serve.py（MCP 服务入口）等。

## 原始文件

- [原始文件](../../raw/archive/Hermes%20Agent%20教程（1）：本地启动与项目结构.md)
