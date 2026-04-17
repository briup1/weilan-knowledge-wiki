---
title: "Hermes Agent 本地启动与项目结构"
source: "https://mp.weixin.qq.com/s/fO3muYwQ_BuM6e0ULFdX7A"
created: 2026-04-16
category: "AICoding"
tags: ["AICoding", "type/tutorial", "type/hands-on", "Hermes-Agent", "AI-Agent", "Project-Structure", "Local-Setup"]
status: "archived"
references: "Archive/Hermes Agent 教程（1）：本地启动与项目结构.md"
---

> Hermes Agent 是由 NousResearch 开源的 AI Agent 项目，具备丰富的技能扩展和插件系统。本文介绍其本地启动步骤与项目结构。

## 项目地址

- GitHub: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- mdBook 阅读链接: [AI-Fullstack-Notes/projects/hermes-agent](https://eva-dengyh.github.io/AI-Fullstack-Notes/projects/hermes-agent/index.html)

## 本地启动步骤

### 1. 拉取项目

```bash
git clone https://github.com/NousResearch/hermes-agent.git
```

### 2. 进入项目目录

```bash
cd hermes-agent
```

### 3. 创建并激活虚拟环境

```bash
uv venv
source .venv/bin/activate
```

### 4. 安装依赖

```bash
uv sync
```

### 5. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API 密钥
```

### 6. 模型选择与启动

```bash
hermes doctor    # 检查环境
hermes model     # 选择模型
hermes           # 启动 Agent
```

## 项目结构概览

```
hermes-agent/
├── agent/                    # Agent 核心逻辑和执行引擎
├── gateway/                  # API 网关、请求路由、钩子系统
│   ├── builtin_hooks/        # 内置钩子集合
│   └── platforms/            # 多平台适配
├── hermes_cli/               # CLI 命令行接口
├── tools/                    # 工具系统和工具调用解析器
│   ├── browser_providers/    # 浏览器供应商
│   ├── environments/         # 工具环境配置
│   └── neutts_samples/       # 神经 TTS 示例
├── acp_adapter/              # ACP 协议适配器
├── acp_registry/             # 服务注册表
├── plugins/                  # 插件系统
│   └── memory/               # 内存/记忆插件
│       ├── byterover/
│       ├── hindsight/
│       ├── holographic/
│       ├── honcho/
│       ├── mem0/
│       ├── openviking/
│       ├── retaindb/
│       └── supermemory/
├── skills/                   # 完整技能模块集合
│   ├── apple/                # 苹果生态（Notes、Reminders、FindMy、iMessage）
│   ├── autonomous-ai-agents/ # AI Agent 集成（Claude Code、Codex、OpenCode）
│   ├── creative/             # 创意工具（ASCII Art、Excalidraw、Manim、P5.js）
│   ├── data-science/         # 数据科学（Jupyter Live Kernel）
│   ├── devops/               # 运维和开发工具
│   ├── email/                # 邮件工具
│   ├── feeds/                # Feed 和 RSS
│   ├── gaming/               # 游戏工具
│   ├── github/               # GitHub 集成
│   ├── index-cache/          # 索引和缓存
│   ├── inference-sh/         # 推理工具
│   ├── leisure/              # 休闲娱乐
│   ├── mcp/                  # 模型上下文协议
│   ├── media/                # 媒体工具
│   ├── mlops/                # MLOps 工具
│   ├── note-taking/          # 笔记应用（Obsidian）
│   ├── productivity/         # 生产力工具（Google Workspace、Notion、Linear）
│   ├── red-teaming/          # 红队工具
│   ├── research/             # 研究工具（ArXiv、LLM Wiki、Polymarket）
│   ├── smart-home/           # 智能家居
│   ├── social-media/         # 社交媒体
│   └── software-development/ # 软件开发
├── optional-skills/          # 可选安装的高级技能包
│   ├── autonomous-ai-agents/
│   ├── blockchain/
│   ├── communication/
│   ├── creative/
│   ├── devops/
│   ├── email/
│   ├── health/
│   ├── mcp/
│   ├── migration/
│   ├── mlops/
│   ├── productivity/
│   ├── research/
│   └── security/
├── landingpage/              # 落地页面
├── website/                  # 项目官网
├── tests/                    # 完整测试套件
├── docker/                   # Docker 配置
├── nix/                      # Nix 声明式配置
├── packaging/                # 包管理配置
├── scripts/                  # 辅助脚本
├── assets/                   # 静态资源
├── plans/                    # 执行计划存储
├── cli.py                    # 主 CLI 入口
├── run_agent.py              # Agent 执行引擎
├── batch_runner.py           # 批量任务运行器
├── rl_cli.py                 # 强化学习 CLI
├── mcp_serve.py              # MCP 服务入口
├── hermes_state.py           # Agent 状态管理
├── pyproject.toml            # Python 项目配置
├── uv.lock                   # UV 包管理器锁定文件
├── Dockerfile
└── README.md
```

## 关键特点

- **模块化设计**：核心框架（agent、gateway、tools）与技能扩展（skills、optional-skills）分离，便于按需加载。
- **丰富的记忆插件**：支持 Mem0、Honcho、Hindsight 等多种记忆实现，方便根据场景切换。
- **广泛的第三方集成**：覆盖苹果生态、GitHub、Notion、Linear、Obsidian、Jupyter 等主流工具。
- **完整的测试体系**：包含单元测试、集成测试、端到端测试和基准测试。

---

## 来源与归档

- 原始素材：[Archive/Hermes Agent 教程（1）：本地启动与项目结构.md](../../../Archive/Hermes%20Agent%20教程（1）：本地启动与项目结构.md)
