---
title: "OpenAI Codex 完全新手指南：Codex 凭什么和 Claude Code 抢饭碗？"
source: "https://mp.weixin.qq.com/s/LwJpfvnZkqsKvk1HtddWGw"
author:
  - "[[康健]]"
published:
created: 2026-05-14
description: "Codex 是一款开源的本地 AI 编程助手，支持在终端和桌面端用自然语言直接读取、修改、执行代码。本指南共 15 章，覆盖 CLI 安装配置、三种操作模式、AGENTS.md 项目上下文、MCP 扩展、以及桌面端（多线程并行、自动化调度、内置浏览器等独家功能）。"
tags:
  - "clippings"
---
康健 *2026年4月18日 10:37*

OpenAI 最近做了一个重要动作：

上个月，他们正式推出了 Codex 桌面端 App 的 Windows 版本——这意味着 Codex 不再只是 Linux / Mac 用户的工具，而是面向所有开发者开放。

但我发现一个现象：很多人听过 Codex 的名字，却说不清它和 ChatGPT、Cursor、Claude Code 的区别，也不知道该从哪里开始上手。

有人问我：Codex 凭什么和 Claude Code 竞争？  
好问题，Claude Code 打磨得这么成熟，Codex 能比吗？

先说 Claude Code 的优势依然存在：

- 上下文理解深
- 代码质量稳
- 对复杂重构的把控力强

但 Codex 也不是吃素的，它有几张独特的牌：

**首先是生态绑定**

如果你已经在使用 ChatGPT Plus/Pro，Codex CLI 可直接使用相同账户，降低额外成本。相比之下，Claude Code 需要单独调用 API，长期成本可能更高。

**然后是桌面端扩展能力**

Codex 桌面端 App 不仅提供命令行，还可以辅助执行一些桌面自动化和任务调度，帮助开发者并行处理任务，提高日常效率。这不是“更好的命令行”，而是在尝试向自动化助手方向拓展。

**可拓展性与自托管**

Codex CLI 支持与第三方模型和工具结合（例如 OpenRouter、Ollama 等），为企业用户提供更多选择，不被单一厂商绑定。

当然，Codex 也有短板：

- Windows 桌面端还在起步阶段
- 复杂逻辑和推理任务上，与 Claude Code 相比还有差距
- 社区生态积累相对较少

所以结论是：两者各有千秋，可以根据 **使用场景进行选择或分工：**

- 日常精细编码、大型重构 → Claude Code 更顺手
- 多任务并行、团队自动化、桌面工作流 → Codex 更有潜力

为了帮助大家更快上手，我整理了一份 **Codex 完全新手指南** （15 章），涵盖内容包括：

- 三种安装方式、两种认证方式
- Suggest / Auto-edit / Full-auto 三种操作模式的适用场景
- 如何撰写 AGENTS.md，让 AI 输出更高质量
- 桌面端 App 独有的辅助自动化、任务调度
- MCP 插件扩展、VS Code 集成、Codex Cloud
- 国内用户常遇问题及解决方案

不管你是 AI 编程工具的新手，还是已经在用 Cursor / Claude Code、想了解是否值得切换的老手，这篇指南都值得一读。🥷

---

OpenAI Codex

完全新手指南

从零开始，手把手带你入门 AI 终端编程助手

作者：程序员康健

2025年4月

---

目 录

前言

第一章 认识 Codex CLI

1.1 Codex CLI 是什么

1.2 核心能力

1.3 Codex CLI vs Claude Code vs Gemini CLI

第二章 环境准备与系统要求

2.1 支持的操作系统

2.2 Node.js 版本要求

2.3 其他依赖

2.4 Windows 用户：安装 WSL2

第三章 安装 Codex CLI

3.1 方法一：npm 安装（推荐）

3.2 方法二：Homebrew 安装（macOS 推荐）

3.3 方法三：下载二进制文件

3.4 升级 Codex CLI

第四章 账户认证与 API Key 配置

4.1 认证方式概览

4.2 方式一：ChatGPT 账户登录

4.3 方式二：API Key 配置

4.4 在服务器上使用认证

第五章 快速入门：第一次使用 Codex

5.1 启动 Codex CLI

5.2 初始化 Git 仓库（建议）

5.3 你的第一个 Codex 对话

5.4 常用快捷键

第六章 三种操作模式详解

6.1 模式概述

6.2 Suggest 模式（建议模式，默认）

6.3 Auto-edit 模式（自动编辑模式）

6.4 Full-auto 模式（全自动模式）

6.5 配置默认模式

第七章 配置文件详解

7.1 config.toml 全局配置

7.2 可用模型列表

7.3 自定义 API 提供商

第八章 AGENTS.md：项目上下文配置

8.1 什么是 AGENTS.md

8.2 AGENTS.md 的查找规则

8.3 AGENTS.md 示例

8.4 使用 Codex 自动生成 AGENTS.md

第九章 MCP 服务器：扩展 Codex 的能力边界

9.1 什么是 MCP

9.2 配置 MCP 服务器

9.3 使用 MCP 功能示例

第十章 VS Code 插件与 Codex Cloud

10.1 VS Code 插件安装

10.2 Codex VS Code 插件的特色功能

10.3 Codex Cloud（云端 Agent）

第十一章 Codex 桌面端 App 完全指南

11.1 桌面端 App 是什么

11.2 下载与安装

11.3 首次启动与登录

11.4 核心界面：Thread（任务线程）

11.5 并行多任务：同时运行多个 Thread

11.6 内置 Git 功能

11.7 内置浏览器

11.8 计算机控制（Computer Use）

11.9 图像生成

11.10 自动化任务（Automations）

11.11 插件（Plugins）与 Skills

11.12 桌面端 App 使用最佳实践

第十二章 实战案例：从零构建 Todo 应用

12.1 案例目标

12.2 初始化项目

12.3 生成基础 Todo 应用

12.4 运行和测试

12.5 添加新功能

12.6 生成测试

第十三章 进阶技巧与工作流优化

13.1 Exec 命令：自动化重复任务

13.2 代码审查工作流

13.3 多智能体并行工作流

13.4 Web 搜索集成

13.5 与其他工具结合

第十四章 常见问题与故障排查

14.1 安装问题

14.2 认证问题

14.3 网络问题（国内用户常见）

14.4 运行时问题

14.5 性能优化建议

第十五章 总结与学习路线

15.1 核心要点回顾

15.2 推荐学习路线

15.3 持续关注

---

前言

在 AI 编程工具爆发式增长的 2025 年，OpenAI 推出了 Codex CLI —— 一款可以在本地终端运行的 AI 编程助手。它把 ChatGPT 级别的推理能力带进了你的命令行，让你只需用自然语言描述需求，就能自动读取、修改并执行代码。

这份指南专为完全零基础的新手设计。无论你是刚刚接触终端的前端同学，还是想提升开发效率的后端工程师，都可以按照本指南一步一步完成安装、配置和上手使用，最终能够把 Codex CLI 真正融入自己的日常开发工作流。

本指南涵盖以下内容：

•Codex CLI 是什么、能做什么

•如何在 macOS / Linux / Windows 上安装

•账户认证与 API Key 配置

•三种操作模式的使用场景

•AGENTS.md 项目上下文配置

•MCP 服务器扩展与多智能体工作流

•VS Code 插件与 Codex Cloud

•实战案例：从零生成一个 Todo 应用

•常见问题排查与最佳实践

💡 阅读前提：你只需要会基础的终端命令（cd、ls 等），不需要任何 AI 开发经验。

第一章 认识 Codex CLI

1.1 Codex CLI 是什么

Codex CLI 是 OpenAI 官方开源的本地终端编程助手，托管在 GitHub 的 openai/codex 仓库。它使用 Rust 语言编写，主打性能与安全，能在本地终端读取、修改并执行代码文件。

与网页版 ChatGPT 最大的区别在于：Codex CLI 可以直接操作你电脑上的文件系统和终端命令，而不只是在对话框里产出文字。你描述想要什么，它帮你把代码写到对应的文件里，甚至帮你跑测试、提交代码。

💡 Codex CLI 与旧版"Codex API"（代码补全 API）是两个完全不同的产品。本指南介绍的是 2025 年新发布的终端 Agent 工具。

1.2 核心能力

Codex CLI 的核心能力可以概括为以下几点：

•自然语言编程：用中文或英文描述需求，自动生成可运行的代码

•文件操作：读取、创建、修改项目文件

•命令执行：运行测试、构建命令、Git 操作等

•代码审查：对当前代码库提供改进建议

•多智能体协作：并行运行多个子 Agent 处理复杂任务

•MCP 扩展：接入 GitHub、数据库等第三方工具

1.3 Codex CLI vs Claude Code vs Gemini CLI

目前市面上有三款主流终端 AI 编程助手，简要对比如下：

| 对比项 | Codex CLI | Claude Code | Gemini CLI |
| --- | --- | --- | --- |
| 开发方 | OpenAI | Anthropic | Google |
| 底层语言 | Rust | TypeScript | TypeScript |
| 默认模型 | GPT-5 / o4-mini | Claude 3.x | Gemini 2.0 |
| 免费使用 | Plus 订阅含 | 需 API Key | 有免费额度 |
| Windows 支持 | WSL2 实验性 | WSL2 推荐 | 支持 |

💡 没有"最好"的工具，只有最适合你当前项目和账户的工具。如果你已有 ChatGPT Plus 订阅，Codex CLI 几乎零成本上手。

第二章 环境准备与系统要求

2.1 支持的操作系统

Codex CLI 官方支持以下操作系统：

•macOS：完整支持，推荐首选

•Linux：完整支持（Ubuntu、Debian、CentOS 等主流发行版）

•Windows：实验性支持，推荐通过 WSL2 使用

⚠️ Windows 原生环境可能存在兼容性问题，强烈建议 Windows 用户先安装 WSL2（Windows Subsystem for Linux）。

2.2 Node.js 版本要求

Codex CLI 通过 npm 安装，要求 Node.js 版本 22 或更高。首先检查你当前的版本：

node --version

输出结果应该 >= v22.0.0。如果版本偏低，推荐使用 nvm（Node Version Manager）升级：

\# 安装 nvm（如尚未安装）

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

\# 安装并切换到 Node.js 22

nvm install 22

nvm use 22

nvm alias default 22 # 设为默认版本

2.3 其他依赖

•Git：建议安装，Codex CLI 在 Git 仓库内运行会更稳定（非必须）

•网络：需要可访问 OpenAI API（国内用户需确保网络畅通）

•内存：最低 4 GB，推荐 8 GB 以上

•磁盘：npm 包本身约 50 MB，会话数据保存在 ~/.codex/ 目录下

💡 macOS 用户可通过 Homebrew 安装 Node：brew install node。安装后 node --version 确认版本。

2.4 Windows 用户：安装 WSL2

如果你是 Windows 用户，请先完成以下步骤：

1.以管理员身份打开 PowerShell

2.运行安装命令：wsl --install

3.重启电脑

4.打开"Ubuntu"应用，完成 Linux 账户设置

5.后续所有操作均在 WSL2 的 Ubuntu 终端中进行

⚠️ 安装 WSL2 需要 Windows 10 版本 2004 及以上，或 Windows 11。

第三章 安装 Codex CLI

3.1 方法一：npm 安装（推荐）

确认 Node.js >= 22 后，一行命令即可全局安装：

npm install -g @openai/codex

国内网络较慢时，可使用淘宝镜像加速：

npm install -g @openai/codex --registry=https://registry.npmmirror.com

安装完成后，验证是否成功：

codex --version

正常情况会输出版本号，例如 0.36.0 或更新版本。

3.2 方法二：Homebrew 安装（macOS 推荐）

macOS 用户可以使用 Homebrew 安装，会自动处理依赖：

brew install --cask codex

更新到最新版本：

brew upgrade --cask codex

3.3 方法三：下载二进制文件

如果不想依赖 npm 或 Homebrew，可以直接从 GitHub Releases 页面下载对应平台的预编译二进制文件：

•访问：https://github.com/openai/codex/releases

•下载对应平台文件，例如：

macOS (Apple Silicon): codex-aarch64-apple-darwin.tar.gz

macOS (Intel): codex-x86\_64-apple-darwin.tar.gz

Linux (x86\_64): codex-x86\_64-unknown-linux-musl.tar.gz

解压后将可执行文件移动到系统 PATH 中：

tar -xzf codex-\*.tar.gz

mv codex /usr/local/bin/codex

chmod +x /usr/local/bin/codex

3.4 升级 Codex CLI

Codex CLI 会定期发布新版本。升级命令如下：

\# npm 安装的升级方式

npm update -g @openai/codex

\# Homebrew 安装的升级方式

brew upgrade --cask codex

💡 建议定期升级，新版本通常包含性能优化和新功能。可以在 GitHub 仓库的 CHANGELOG.md 查看详细更新记录。

第四章 账户认证与 API Key 配置

4.1 认证方式概览

Codex CLI 支持两种认证方式：

•方式一：ChatGPT 账户登录（推荐 Plus/Pro 用户）

•方式二：OpenAI API Key（适合开发者或无 ChatGPT 订阅用户）

4.2 方式一：ChatGPT 账户登录

ChatGPT Plus、Pro、Business、Edu 和 Enterprise 订阅用户可以直接使用账户登录，不需要额外的 API Key 费用：

6.在终端运行 codex，首次启动会提示登录

7.选择"Sign in with ChatGPT"

8.浏览器会自动打开 OpenAI 登录页面

9.登录成功后，认证信息会保存到 ~/.codex/auth.json

各订阅套餐的消息限额（每 5 小时）：

•Plus / Business / Enterprise / Edu：30 - 150 条消息

•Pro：300 - 1500 条消息

💡 ChatGPT Plus 用户还可以获得 5 美元免费 API 额度，Pro 用户可获得 50 美元免费 API 额度（30天内有效）。

4.3 方式二：API Key 配置

如果你没有 ChatGPT 订阅，或者希望使用 API 方式（更灵活），按如下步骤配置：

获取 API Key

10.访问 https://platform.openai.com/api-keys

11.点击"Create new secret key"

12.复制生成的 Key（只显示一次，请妥善保存）

配置环境变量

macOS / Linux 临时配置（当前终端会话有效）：

export OPENAI\_API\_KEY="sk-你的key"

永久配置（推荐），将以下内容添加到 ~/.zshrc 或 ~/.bashrc：

echo 'export OPENAI\_API\_KEY="sk-你的key"' >> ~/.zshrc

source ~/.zshrc

Windows PowerShell：

$env:OPENAI\_API\_KEY="sk-你的key"

⚠️ 不要把 API Key 提交到 Git 仓库！OpenAI 会自动扫描并禁用泄露的 Key。建议将 Key 写入环境变量而非配置文件。

4.4 在服务器上使用认证

如果你需要在没有浏览器的远程服务器上使用 Codex，可以将本地的认证文件复制过去：

\# 在本地机器完成认证后，复制认证文件到远程服务器

scp ~/.codex/auth.json user@your-server:~/.codex/auth.json

第五章 快速入门：第一次使用 Codex

5.1 启动 Codex CLI

完成安装和认证后，在终端中输入以下命令启动交互式界面：

codex

首次启动会加载默认模型（通常是 o4-mini），进入对话模式后，你就可以开始和 Codex 交互了。

5.2 初始化 Git 仓库（建议）

强烈建议在有 Git 仓库的目录下使用 Codex，这样可以：

•避免 Codex 意外修改重要文件

•通过 git diff 查看 AI 做了哪些修改

•随时通过 git checkout 回滚到之前的状态

mkdir my-project && cd my-project

git init

codex

5.3 你的第一个 Codex 对话

启动后，你可以直接用自然语言描述你想要的结果：

帮我创建一个 hello.js 文件，输出"Hello, Codex!"

Codex 会分析请求，展示它打算执行的操作，并在你确认后创建文件、写入代码。

也可以通过命令行直接传入提示词（非交互模式）：

codex "帮我审查当前目录的代码，给出改进建议"

5.4 常用快捷键

•Enter：发送消息

•Ctrl + C：取消当前操作

•Ctrl + D：退出 Codex

•/help：查看内置帮助

•/model：切换使用的模型

•/clear：清空当前会话

💡 使用 codex resume 可以打开历史会话选择器，方便回到之前未完成的对话。

第六章 三种操作模式详解

6.1 模式概述

Codex CLI 提供三种操作模式，用于控制 AI 执行操作时需要多少人工确认。通过 -a 或 --approval-mode 参数指定：

6.2 Suggest 模式（建议模式，默认）

在这种模式下，Codex 每次执行任何文件修改或命令操作前，都会先展示计划并等待你的确认。这是最安全的模式，适合新手使用。

codex --approval-mode suggest "帮我重构 utils.js"

Codex 会显示：

•它打算修改哪些文件

•具体的代码变更内容（diff 格式）

•等待你输入 y/n 确认

✅ 新手期间务必使用 Suggest 模式，先观察 AI 的行为，理解它的工作方式，再考虑放宽权限。

6.3 Auto-edit 模式（自动编辑模式）

Codex 可以自动修改文件，但执行 shell 命令（如安装依赖、运行测试）前仍需确认。适合对 AI 有一定信任的场景。

codex --approval-mode auto-edit "为所有函数添加 JSDoc 注释"

6.4 Full-auto 模式（全自动模式）

Codex 自主完成所有操作，包括文件修改和命令执行，无需任何确认。效率最高，但风险也最大，仅建议在隔离环境（如 Docker 容器）或已充分测试的 CI/CD 流水线中使用。

codex --approval-mode full-auto "运行所有测试并修复失败的用例"

⚠️ 全自动模式下 Codex 可以执行任意命令，请确保在有 Git 保护或隔离的环境中使用，避免不可恢复的操作。

6.5 配置默认模式

你可以在配置文件中设置默认操作模式，避免每次都手动指定：

\# 编辑配置文件：~/.codex/config.toml

\[defaults\]

approval\_mode = "auto-edit" # suggest | auto-edit | full-auto

第七章 配置文件详解

7.1 config.toml 全局配置

Codex CLI 的全局配置文件位于 ~/.codex/config.toml。如果不存在，可以手动创建：

mkdir -p ~/.codex

nano ~/.codex/config.toml

常用配置项示例：

\# 默认模型（可通过 /model 命令临时切换）

model = "o4-mini"

\# 模型推理强度：low | medium | high

model\_reasoning\_effort = "medium"

\# 默认操作模式

approval\_mode = "auto-edit"

\# 启用 MCP 服务器（见第九章）

\[mcp\_servers\]

github = { command = "npx", args = \["-y", "@modelcontextprotocol/server-github"\] }

7.2 可用模型列表

在对话中输入 /models 可以查看当前可用的所有模型。常见模型包括：

•o4-mini：速度快，成本低，适合日常编码任务（默认）

•o4-mini-high：更强的推理能力，适合复杂问题

•gpt-5 / gpt-5-codex：最强能力，适合高难度任务

💡 对于日常代码生成和简单重构，o4-mini 已经足够好，且成本更低。只有在遇到复杂架构问题时才考虑切换到更强的模型。

7.3 自定义 API 提供商

除了 OpenAI 官方 API，Codex CLI 也支持配置兼容 OpenAI 接口的第三方 API（如 OpenRouter、Azure、本地 Ollama）：

\[model\_providers.openrouter\]

name = "Open Router"

base\_url = "https://openrouter.ai/api/v1"

env\_key = "OPENROUTER\_API\_KEY"

wire\_api = "chat"

\[model\_providers.ollama\]

name = "Ollama (本地模型)"

base\_url = "http://localhost:11434/v1"

配置完成后启动时指定提供商：

export OPENROUTER\_API\_KEY="your-key"

codex -m openai/gpt-5

第八章 AGENTS.md：项目上下文配置

8.1 什么是 AGENTS.md

AGENTS.md 是 Codex 专属的项目上下文配置文件，类似于 Claude Code 的 CLAUDE.md。你可以在这个文件中告诉 Codex：

•这个项目使用什么技术栈

•代码风格规范（如 ESLint 配置、命名习惯）

•架构约定（如目录结构、模块划分原则）

•哪些文件或目录不应该被修改

•常用命令（如何运行测试、如何构建）

8.2 AGENTS.md 的查找规则

Codex 会在多个位置寻找并合并 AGENTS.md 文件：

•~/.codex/AGENTS.md：全局配置，对所有项目生效

•项目根目录的 AGENTS.md：当前项目的配置

•当前工作目录的 AGENTS.md：细粒度控制

多个文件同时存在时，内容会被合并，项目级配置优先级更高。

8.3 AGENTS.md 示例

以下是一个前端 React 项目的 AGENTS.md 示例：

\# 项目概述

这是一个基于 React 18 + TypeScript + Vite 的前端项目。

\# 技术栈

\- 框架：React 18，使用函数组件 + Hooks

\- 语言：TypeScript（strict 模式）

\- 样式：Tailwind CSS

\- 状态管理：Zustand

\# 代码规范

\- 使用 2 空格缩进

\- 组件文件使用 PascalCase 命名

\- 工具函数文件使用 camelCase 命名

\- 所有组件必须有 TypeScript 类型声明

\# 常用命令

\- 启动开发服务器：npm run dev

\- 运行测试：npm run test

\- 构建：npm run build

\# 注意事项

\- 不要修改 src/api/generated/ 目录（自动生成文件）

\- 新增组件请放在 src/components/ 目录下

✅ 每个项目都应该配置一个 AGENTS.md。这是提升 Codex 输出质量最有效的方式之一，相当于给 AI 一份"项目说明书"。

8.4 使用 Codex 自动生成 AGENTS.md

你可以让 Codex 帮你分析项目并自动生成 AGENTS.md：

codex "分析当前项目结构，为我生成一个详细的 AGENTS.md 配置文件"

第九章 MCP 服务器：扩展 Codex 的能力边界

9.1 什么是 MCP

MCP（Model Context Protocol，模型上下文协议）是 Anthropic 提出的开放标准，允许 AI 工具连接到外部数据源和服务。Codex CLI 完整支持 MCP，通过配置 MCP 服务器，你可以让 Codex 直接操作：

•GitHub：读取 Issues、创建 PR、管理仓库

•数据库：查询 PostgreSQL、MySQL、SQLite

•文件系统：访问项目外的文件

•Slack、Notion、Linear 等第三方工具

9.2 配置 MCP 服务器

在 ~/.codex/config.toml 中添加 \[mcp\_servers\] 配置：

\[mcp\_servers\]

\# GitHub 集成

github = { command = "npx", args = \["-y", "@modelcontextprotocol/server-github"\] }

\# PostgreSQL 数据库

postgres = { command = "npx", args = \["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"\] }

\# 文件系统访问

filesystem = { command = "npx", args = \["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"\] }

需要环境变量的 MCP 服务器配置示例（GitHub Token）：

\[mcp\_servers.github\]

command = "npx"

args = \["-y", "@modelcontextprotocol/server-github"\]

env = { GITHUB\_PERSONAL\_ACCESS\_TOKEN = "ghp\_你的token" }

9.3 使用 MCP 功能示例

配置好 GitHub MCP 后，你可以：

codex "查看我的 GitHub 仓库最近 5 个未关闭的 Issue，并给每个 Issue 打上优先级标签"

codex "读取数据库 users 表的结构，帮我生成对应的 TypeScript 类型定义"

💡 MCP 服务器是可选的。如果你只是做普通的代码生成和文件操作，不配置任何 MCP 也完全够用。

第十章 VS Code 插件与 Codex Cloud

10.1 VS Code 插件安装

如果你更习惯在 VS Code 中工作，Codex 也提供了官方插件：

13.打开 VS Code

14.进入扩展市场（Ctrl+Shift+X 或 Cmd+Shift+X）

15.搜索"Codex"或"OpenAI Codex"

16.点击安装

首次使用插件时，需要登录 ChatGPT 账户（同 CLI 的认证方式）。对于 Plus/Pro 订阅用户，体验非常流畅。

10.2 Codex VS Code 插件的特色功能

•内联代码建议：在编辑器中直接获得 AI 代码补全

•代码解释：选中代码，右键"用 Codex 解释"

•一键重构：选中代码块，快速重构或改进

•测试生成：自动为函数生成单元测试

10.3 Codex Cloud（云端 Agent）

Codex Cloud 是 Codex 生态中的云端版本，可以在 chatgpt.com/codex 访问。与 CLI 版本的主要区别：

•运行在云端沙盒环境，不需要本地环境配置

•支持并行处理多个任务

•每项任务在独立的云端容器中运行，互不干扰

•适合长时间运行的后台任务（如大型重构、自动化测试生成）

通过 CLI 也可以启动 Codex Cloud 任务：

\# 在云端执行任务，不占用本地资源

codex cloud "为整个项目生成完整的单元测试套件"

💡 Codex Cloud 目前仍在持续完善中，适合尝鲜。常规开发任务推荐优先使用本地 CLI 版本，响应更快、更直观。

第十一章 Codex 桌面端 App 完全指南

11.1 桌面端 App 是什么

2026 年 2 月，OpenAI 正式推出了 Codex 桌面端 App（Codex Desktop App）。它不只是 CLI 的图形化包装，而是一个全新的"AI Agent 指挥中心"，专为并行管理多个 Agent 任务而设计，内置 Git 工作树、自动化调度、内置浏览器、计算机控制等一系列 CLI 中没有的强大功能。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

与 CLI 的核心区别可以简单概括如下：

| 对比维度 | CLI 终端版 | 桌面端 App |
| --- | --- | --- |
| 界面 | 纯文字终端 | 图形化 GUI |
| 多任务 | 单线程对话 | 多线程并行 Thread |
| Git 集成 | 手动操作 | 内置 diff/commit/PR |
| 浏览器 | 不支持 | 内置浏览器 |
| 计算机控制 | 不支持 | 支持（macOS） |
| 图像生成 | 不支持 | 支持（gpt-image-1.5） |
| 自动化调度 | 不支持 | 支持定时/长期任务 |
| 适合场景 | 脚本/CI/CD | 日常开发主力工具 |

11.2 下载与安装

桌面端 App 支持 macOS 和 Windows（2026 年 3 月起），Linux 暂不支持。

macOS 安装

方法一：通过 CLI 一键启动桌面端（需已安装 CLI）：

codex app

方法二：直接下载安装包：

•Apple Silicon（M1/M2/M3/M4）：下载 macOS Apple Silicon 版

•Intel Mac：下载 macOS Intel 版

•下载页面：https://developers.openai.com/codex/app

下载后双击.dmg 文件，将 Codex 拖入 Applications 文件夹，然后打开即可。

Windows 安装

从官方下载页下载 Windows 安装包（.exe），双击安装即可。Windows 版无需 WSL2，Codex 可直接在 PowerShell 原生环境中运行，使用 Windows 原生沙盒。

💡 Windows 用户注意：桌面端 App 的 Windows 版比 CLI 的 Windows 支持更完善，如果你主要使用 Windows，优先选择安装桌面端而非 CLI。

15.3 首次启动与登录

打开 Codex App 后，首次使用需要登录：

17.选择登录方式：ChatGPT 账户（推荐）或 OpenAI API Key

18.ChatGPT 登录：会弹出浏览器跳转到 OpenAI 登录页，完成后自动返回 App

19.API Key 登录：在输入框中粘贴你的 sk- 开头的 Key，注意部分功能（如云端 Thread）在 API Key 模式下不可用

⚠️ 使用 OpenAI API Key 登录时，云端 Thread 功能不可用，只能使用本地（Local）模式。建议有 ChatGPT 订阅的用户优先使用账户登录。

14.4 核心界面：Thread（任务线程）

Codex App 的核心工作单元是 Thread（任务线程），每个 Thread 对应一个独立的 Agent 会话。

创建第一个 Thread

20.打开 App，点击左侧"+ New Thread"

21.选择项目文件夹（即你要让 Codex 操作的代码目录）

22.选择模式：Local（本地，直接操作项目文件）或 Worktree（独立 Git 工作树，隔离变更）

23.在对话框中输入任务描述，按 Enter 发送

Local 模式 vs Worktree 模式

•Local 模式：Codex 直接在你的项目目录中工作，修改会立即体现在文件系统里

•Worktree 模式：Codex 在一个独立的 Git 工作树分支上工作，主项目文件不受影响，适合探索性修改或并行任务

✅ 日常开发建议使用 Worktree 模式，完成后通过 App 内置的 Git 功能合并变更。这样你的主工作区始终保持干净。

14.5 并行多任务：同时运行多个 Thread

桌面端 App 最大的优势之一是支持同时运行多个 Thread，实现真正的并行 AI 开发。例如：

•Thread 1：修复生产环境的 Bug

•Thread 2：为新功能编写单元测试

•Thread 3：重构旧模块的代码风格

三个任务同时在后台运行，你可以随时切换查看进度，或者去做别的事，等 Codex 完成后再回来 Review。

在 App 左侧的 Thread 列表中可以看到所有任务的实时状态：

•运行中（蓝色旋转图标）

•等待确认（黄色图标）

•已完成（绿色图标）

•出错（红色图标）

12.6 内置 Git 功能

Codex App 将 Git 操作深度集成到了界面中，无需离开 App 就能完成完整的 Git 工作流。

Diff 查看与审核

每个 Thread 完成后，右侧会展示 Git Diff 面板，显示 Codex 做了哪些文件修改。你可以：

•逐行查看代码变更

•对特定代码行添加内联注释，让 Codex 进一步修改

•选择性暂存（Stage）部分修改，拒绝其他部分

•一键回滚（Revert）整个 Thread 的所有修改

提交与推送

审核通过后，直接在 App 内：

24.填写 Commit Message（也可以让 Codex 自动生成）

25.点击 Commit 提交

26.点击 Push 推送到远程仓库

27.可选：一键创建 Pull Request

💡 Codex 可以帮你自动生成符合规范的 Commit Message，只需在提交前输入"帮我生成这次修改的 commit message"。

11.7 内置浏览器

Codex App 内置了一个浏览器，主要用于前端开发调试。使用场景：

•实时预览你让 Codex 开发的网页应用（localhost）

•在页面上直接点击或框选，添加注释告诉 Codex "这里的样式不对，帮我修改"

•截图给 Codex 参考，让它根据视觉效果调整代码

使用方法：在 Thread 中发送本地服务器地址，Codex 会自动在内置浏览器打开：

帮我查看 http://localhost:3000，检查首页的布局是否正确，如有问题请修复

⚠️ 内置浏览器目前主要支持 localhost 本地页面，公网页面的完整控制功能仍在扩展中。

11.8 计算机控制（Computer Use）

这是桌面端 App 独有的杀手级功能：Codex 可以像人一样操控你电脑上的 GUI 应用程序——通过截图理解屏幕内容，自动点击、输入文字、切换窗口。

典型使用场景

•测试你正在开发的 macOS 原生 App，让 Codex 自动完成点击测试流程

•在 iOS 模拟器中运行 App 并截图，让 Codex 检查 UI 布局

•操作没有 API 接口的第三方软件（如修改某些 App 的设置）

•复现只在图形界面出现的 Bug

•在多个 App 间完成跨应用的自动化工作流

开启 Computer Use 功能

28.打开 Codex App 的 Settings（设置）

29.进入 Computer Use 选项卡

30.点击 Install 安装 Computer Use 插件

31.系统会弹出权限请求，授予以下两项权限：

• 屏幕录制（Screen Recording）：允许 Codex 看到屏幕内容

• 辅助功能（Accessibility）：允许 Codex 点击和输入

使用 Computer Use

在对话中通过 @ 符号指定要操作的应用：

帮我打开 Safari，访问 http://localhost:3000，截图给我看看首页渲染效果

@Simulator 在 iPhone 15 模拟器中运行 App，点击登录按钮，检查是否有崩溃

⚠️ Computer Use 功能目前仅在 macOS 上可用，EU/UK 地区暂未开放。请确保只对可信任的操作授权，Codex 操作桌面应用可能影响系统状态。

11.9 图像生成

桌面端 App 集成了 GPT-image-1.5 模型，支持在开发流程中直接生成和编辑图像。实用场景：

•为正在开发的游戏生成美术素材（图标、背景、角色）

•快速生成 UI 设计稿给 Codex 参考，让它按照设计实现界面

•生成产品原型图、功能示意图

直接在对话中描述需求即可：

帮我为这个待办 App 生成一个 512x512 的应用图标，风格简洁现代，主色调蓝色

11.10 自动化任务（Automations）

这是桌面端 App 的另一个核心特色：你可以设置定时或触发式的自动化任务，让 Codex 在后台持续工作，甚至跨天跨周执行长期任务。

设置自动化任务

32.在左侧菜单点击 Automations

33.点击 New Automation

34.选择触发方式：定时（如每天早上 9 点）或手动触发

35.输入任务描述

36.选择关联的项目和执行模式

常见自动化场景：

•每天上班前自动检查 GitHub Issues，整理优先级并生成今日工作计划

•每周一自动从 git log 生成本周代码变更摘要

•监控生产告警（接入 Slack 插件），自动分析错误日志并提交修复 PR

•定期对代码库进行安全扫描，发现潜在风险自动报告

✅ 自动化功能最适合"重复但重要"的维护类任务。把这些工作交给 Codex 后，你就能专注在真正需要创造力的功能开发上。

11.11 插件（Plugins）与 Skills

桌面端 App 支持安装插件来扩展 Codex 的能力。目前已有超过 90 个插件，覆盖主流开发工具：

•项目管理：GitHub、JIRA（Atlassian Rovo）、Linear、GitLab Issues

•CI/CD：CircleCI、Render、Vercel

•代码质量：CodeRabbit（AI Code Review）

•通讯：Slack、Gmail、Notion

•数据库：Neon by Databricks、PostgreSQL

•其他：Microsoft Suite、Remotion（视频生成）、Superpowers

Skills 是可复用的任务模板，你可以自定义 Skill 封装常用工作流。例如创建一个"前端 UI 开发"Skill，里面包含你的 UI 框架规范、设计系统文档和常用组件列表，每次开发 UI 时一键激活。

💡 在 App 侧边栏的 Skills 入口可以查看和管理所有 Skill，包括你的团队成员共享的 Skill。

11.12 桌面端 App 使用最佳实践

•新建项目时优先选 Worktree 模式，保持主分支干净

•善用并行 Thread，把大任务拆成多个独立子任务同时执行

•配置好 AGENTS.md 再开始工作，App 同样会读取此文件

•利用内置 Diff 面板逐行 Review，不要无脑接受所有修改

•Computer Use 保持最小权限原则，只授权必要的 App

•自动化任务先手动测试一遍，确认行为符合预期后再设置定时执行

第十二章 实战案例：从零构建 Todo 应用

15.1 案例目标

通过这个实战案例，你将体验 Codex CLI 的完整工作流：从初始化项目、生成代码、运行应用，到添加功能和 Debug。

15.2 初始化项目

mkdir codex-todo && cd codex-todo

git init

codex

15.3 生成基础 Todo 应用

在 Codex 对话框中输入：

帮我创建一个 Node.js 的命令行 Todo 应用，功能包括：

1\. 添加待办事项

2\. 列出所有待办事项

3\. 标记完成

4\. 数据用 JSON 文件持久化存储

Codex 会分析需求，然后展示操作计划，确认后自动创建以下文件：

•index.js：主入口文件

•package.json：项目配置

•README.md：使用说明

14.4 运行和测试

让 Codex 帮你运行项目：

现在帮我运行这个应用，添加 3 个待办事项并列出它们

如果有报错，直接把错误信息粘贴给 Codex：

运行时报错了：\[错误信息\] 帮我修复

14.5 添加新功能

项目运行后，继续对话添加功能：

帮我添加一个删除功能，根据序号删除待办事项

帮我给这个项目添加颜色高亮，用绿色显示已完成项，红色显示未完成项

12.6 生成测试

帮我用 Jest 为所有函数生成单元测试，并运行测试确保全部通过

✅ 在整个过程中，保持使用 Suggest 模式，查看每一步 Codex 做了什么修改。这是最快理解 AI 编程助手工作原理的方式。

第十三章 进阶技巧与工作流优化

15.1 Exec 命令：自动化重复任务

对于可重复执行的任务，可以使用 exec 命令配合脚本，非常适合 CI/CD 集成：

\# 非交互式执行，适合脚本调用

codex exec --full-auto "更新 CHANGELOG，包含所有未记录的提交"

\# 在 GitHub Actions 中使用

\- name: Update changelog

run: |

export OPENAI\_API\_KEY="${{ secrets.OPENAI\_KEY }}"

codex exec --full-auto "generate release notes from git log"

15.2 代码审查工作流

在提交代码前，用 Codex 进行自动化代码审查：

\# 审查最近的改动

codex "审查 git diff HEAD 中的所有改动，重点检查：安全漏洞、性能问题、代码规范"

\# 在 pre-commit hook 中配置

codex "检查暂存区的代码变更，如有明显问题请指出"

15.3 多智能体并行工作流

对于大型任务，可以使用多个子 Agent 并行处理不同模块：

codex "把前端重构任务拆分成 5 个子任务，分别：

1\. 重构组件库

2\. 优化路由配置

3\. 重写状态管理

4\. 更新测试用例

5\. 更新文档"

💡 多智能体模式仍处于实验阶段，建议在非关键项目上先尝试，熟悉其行为后再应用到生产环境。

14.4 Web 搜索集成

Codex 支持在对话中搜索最新信息，非常适合需要查阅文档的场景：

帮我搜索 React 19 的最新 API 变化，并将我的项目升级到兼容的写法

14.5 与其他工具结合

•与 GitHub Actions 结合：自动化代码审查、文档生成、版本管理

•与 Docker 结合：在容器中运行 full-auto 模式，隔离风险

•与 Makefile 结合：将常用 Codex 命令封装为 make 目标

第十四章 常见问题与故障排查

15.1 安装问题

命令找不到：codex: command not found

原因：npm 全局安装目录不在系统 PATH 中。

\# 查看 npm 全局安装目录

npm config get prefix

\# 将 {prefix}/bin 添加到 PATH（添加到 ~/.zshrc 或 ~/.bashrc）

export PATH="$(npm config get prefix)/bin:$PATH"

source ~/.zshrc

Node.js 版本太低

\# 使用 nvm 升级

nvm install 22 && nvm use 22 && nvm alias default 22

15.2 认证问题

API Key 无效或额度不足

\# 验证 API Key 是否设置正确

echo $OPENAI\_API\_KEY

如果输出为空，说明环境变量没有正确设置，重新配置并重新打开终端。

ChatGPT 账户登录后仍提示未授权

可能原因：ChatGPT 订阅已过期，或当前套餐不包含 Codex 权限。请登录 chat.openai.com 确认订阅状态。

15.3 网络问题（国内用户常见）

Codex CLI 需要访问 OpenAI API（api.openai.com）。如果连接超时，请检查：

•确认代理软件正常运行

•将 OpenAI 相关域名加入代理规则

•尝试使用国内 npm 镜像安装：npm i -g @openai/codex --registry=https://registry.npmmirror.com

14.4 运行时问题

Codex 修改了不该改的文件

立即执行 git checkout. 回滚所有未暂存的修改，然后检查你的指令是否足够精确，并考虑切换到 Suggest 模式。

生成的代码有语法错误

直接在对话中告知 Codex：

生成的代码有语法错误：\[错误信息\] 请修复

14.5 性能优化建议

•在项目目录下运行，避免在根目录使用（Codex 会扫描当前目录）

•配置.codexignore 文件排除不需要的目录（如 node\_modules、dist）

•为复杂项目配置详细的 AGENTS.md，减少 AI 的猜测成本

•使用 -q 安静模式减少无关输出：codex -q "你的任务"

✅ 遇到任何问题，第一步是检查 GitHub 仓库的 Issues 页面（github.com/openai/codex/issues），通常能找到类似问题的解决方案。

第十五章 总结与学习路线

15.1 核心要点回顾

恭喜你读完了这份指南！让我们回顾一下最重要的几个知识点：

37.Codex CLI 是 OpenAI 开源的本地 AI 编程助手，用自然语言操控代码

38.安装需要 Node.js 22+，一行 npm 命令即可完成

39.新手推荐使用 Suggest 模式，养成查看 AI 操作的习惯

40.配置 AGENTS.md 是提升 Codex 输出质量最有效的方式

41.MCP 服务器可以让 Codex 接入 GitHub、数据库等外部工具

42.结合 Git 使用，任何时候都能安全回滚

15.2 推荐学习路线

按以下路线循序渐进，效果最好：

第一周：安装 + 认证 + 熟悉基本对话，在小项目上练习

第二周：配置 AGENTS.md，体验它对输出质量的提升

第三周：尝试 MCP 集成（GitHub 或数据库），扩大使用场景

第四周：在真实工作项目中引入 Codex，优化个人工作流

15.3 持续关注

Codex CLI 迭代非常快，建议关注以下资源保持同步：

•GitHub 仓库：https://github.com/openai/codex（Star + Watch）

•官方文档：https://developers.openai.com/codex

•CHANGELOG.md：每次更新的详细记录

•程序员AI破局指南公众号：第一时间推送 Codex 中文实操教程

✅ AI 编程工具的核心价值不在于替代你，而在于把你从重复、机械的编码工作中解放出来，让你能专注在真正需要创造力和判断力的部分。Codex CLI 是一个很好的起点。

关注我，获取更多教程

感谢阅读这份指南！如果对你有帮助，欢迎关注我的公众号和视频号，获取更多实用技术教程、AI 工具测评和行业干货 🎉

| 📱 公众号  ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  程序员AI破局指南  扫码关注，获取图文教程 | 📹 视频号  ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  程序员康健  扫码关注，获取视频教程 |
| --- | --- |

💬 有问题？欢迎在公众号后台留言，我会及时回复！

---

📚 相关阅读

- [Ollama 完全新手指南：一行命令实现 token 自由](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487669&idx=1&sn=2da25b6d78e33972dff158ccd0e5a73d&scene=21#wechat_redirect)
- [ReactFlow完全入门指南：从零构建 AI 工作流编辑器](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487646&idx=1&sn=6abf022e43a3251ebbb45a8249ec5433&scene=21#wechat_redirect)
- [微信小程序开发完全新手指南：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487627&idx=1&sn=27307061cf0a25f88ed02b8f902e93bc&scene=21#wechat_redirect)
- [Superpowers 完全指南：用它少返工80%](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487617&idx=1&sn=49fee04bf4d412a7c444d0ea4f750fe4&scene=21#wechat_redirect)
- [OpenSpec 完全新手指南：5分钟上手规范驱动开发](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487610&idx=1&sn=d609ea6bc83f3832886b6062eb6c2b19&scene=21#wechat_redirect)
- [【2026 应届生必备】2万字前端面试题库（附详解）](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487603&idx=1&sn=3d714904d4a83af12906b009d876b35a&scene=21#wechat_redirect)
- [Skills 完全新手指南(2026版)：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487596&idx=1&sn=cc25377c79e2e19c230894be6793973c&scene=21#wechat_redirect)
- [群晖完全新手指南—家里装一台 NAS，从此告别百度网盘和移动硬盘](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487555&idx=1&sn=ab09a5b43c73161f1bb82ff3660e3a4b&scene=21#wechat_redirect)
- [GitHub Copilot 完全指南：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487536&idx=1&sn=24042c775a66b237577e23cc57ebe001&scene=21#wechat_redirect)
- [Cursor深度使用指南：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487483&idx=1&sn=d6ab0a602c4bf67a7aebd331e8b8a7eb&scene=21#wechat_redirect)
- [Claude Code 完全新手指南（2026 版）：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487467&idx=1&sn=816295fe691f3622449d2ed3966f7f85&scene=21#wechat_redirect)
- [全网最详细的OpenClaw完全新手指南(中文保姆级教程)](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487459&idx=1&sn=ad1d429cddc9f9f0ff206246b65f22d5&scene=21#wechat_redirect)
- [一天烧掉一个亿 Token？程序员的 AI 账单，正在惩罚「偷懒的人」](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487442&idx=1&sn=523bf616b7f8b154481f3c819b22485b&scene=21#wechat_redirect)

AI 实战完全指南 · 目录

继续滑动看下一个

程序员AI破局指南

向上滑动看下一个

搜索范围

全网

文库

学术

所有文献

所有文献

中文库

英文库

---

PubMed

北大核心

中科院分区

全部

---

中科院1区

中科院1-2区

中科院1-3区

JCR

全部

---

JCR：Q1

JCR：Q1-Q2

JCR：Q1-Q3

SCIE

EI

图片

视频

播客

我的

全部

我的

海管家\_货代系统\_货代软件\_跨境物流系统\_国际货代操作系统

强度

深入

简洁

深入

深度研究

先想后搜

先搜后扩

新建自定义技能