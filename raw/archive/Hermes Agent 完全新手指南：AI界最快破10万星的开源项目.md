---
title: "Hermes Agent 完全新手指南：AI界最快破10万星的开源项目"
source: "https://mp.weixin.qq.com/s/A_RzvL-u3XedXy6lAb11vQ"
author:
  - "[[程康健]]"
published:
created: 2026-05-14
description: "Hermes Agent 是 2026 年增速最猛的开源 AI Agent，不到 3 个月 GitHub 突破 10 万星。它能跨会话记忆、自动积累技能、越用越懂你，真正做到「用完不归零」。本文从安装到进阶全覆盖，12 章手把手带你上手，附 Word 完整版可下载，完全新手也能跑起来。"
tags:
  - "clippings"
---
程康健 *2026年4月21日 10:12*

最近有一个开源项目，两个月内在 GitHub 狂揽 4.7 万 Star，三个月破10万 star，连续多日霸榜全球开源热门榜第一。它叫 **Hermes Agent** 。

你可能已经听过它的名字，但大概率还没真正用起来——因为网上的资料要么太散，要么直接扔给你一堆英文文档，从来没有人认真告诉你： **一个完全不懂的新手，到底应该怎么一步步上手？**

这篇文章，就是专门为你写的。

先说说它凭什么火。

大多数 AI 工具有一个根本性的缺陷： **用完归零** 。你今天教会了它一套工作流，明天开一个新对话，它什么都不记得了。你花在「教 AI 认识你」上的时间，每次都在清空重来。

Hermes Agent 解决的，正是这个问题。

它的口号是「 **The agent that grows with you** 」——跟你一起成长的 Agent。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/f044ic7E07hfCbAKhdicyqBkvVkRV1WIHKZV0SUHF81oibqzuRianFPdJmLDpP6Mg6zCibsCU2icSB0GWbJcIaZMn4LFRfp4kthS01gjEgvISiagWk/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

这不是营销文案，是它的底层设计逻辑：

- 每次完成复杂任务，它会自动把成功经验提炼成「技能」，存进技能库，下次同类任务直接调用
- 它会主动记住你的偏好、工作习惯、常用路径，跨会话持续积累，越用越懂你
- 它可以住在你的服务器上，通过 Telegram 随时叫醒它，让它帮你干活——你睡觉，它在跑

从 2 月底开源首月破 2.2 万星，到后来单日新增 6400+ 星，Hermes Agent 在不到两个月里持续霸榜全球开源榜单第一。 36Kr社区里有人说：「这是我用过的第一个真正在变聪明的 AI 工具——不是因为模型升级，而是因为它记住了我。」

说回这份指南本身。

这份《Hermes Agent 完全新手指南》由我主导策划、AI 辅助生成，内容覆盖官方文档、GitHub 源码和社区反馈中的核心知识点。我负责确定结构、审核内容、把关准确性——AI 负责整理和写作。12 个章节，手把手带你走完整个上手路径。

**无论你之前有没有用过 AI Agent，看这一篇就够了。**

---

Hermes Agent

完全新手入门指南

The Agent That Grows With You

会学习、会记忆、会进化的 AI 智能体

程序员康健 出品

公众号：程序员AI破局指南

2026 年 4 月

目录

第一章 认识 Hermes Agent

1.1 什么是 Hermes Agent

1.2 Hermes Agent 的核心特性

1.3 Hermes Agent 与普通 AI 工具的对比

1.4 适合谁使用 Hermes Agent

第二章 安装与环境准备

2.1 系统要求

2.2 一键安装（推荐）

2.3 Android / Termux 安装

2.4 开发者手动安装

2.5 安装语音功能（可选）

2.6 更新与卸载

第三章 配置 LLM 提供商

3.1 选择并配置模型

3.2 支持的 LLM 提供商一览

3.3 配置 API Key（以 OpenRouter 为例）

3.4 随时切换模型

3.5 运行配置向导（推荐新手使用）

第四章 基础使用：开始你的第一次对话

4.1 启动 Hermes

4.2 基础交互操作

4.3 常用斜杠命令

4.4 让 Agent 操作终端

4.5 配置终端执行后端

第五章 技能系统（Skills）

5.1 什么是技能（Skill）

5.2 技能的三个加载级别

5.3 如何使用技能

5.4 技能目录结构

5.5 从 Skills Hub 安装技能

5.6 支持的技能来源

5.7 Agent 自动创建技能

第六章 持久化记忆

6.1 记忆系统概述

6.2 记忆文件说明

6.3 记忆的使用方式

6.4 FTS5 全文搜索

6.5 记忆最佳实践

第七章 消息平台网关

7.1 消息网关概述

7.2 支持的消息平台

7.3 配置 Telegram 网关

7.4 消息平台专用斜杠命令

第八章 定时任务与自动化

8.1 定时任务系统概述

8.2 用自然语言创建定时任务

8.3 管理定时任务

第九章 MCP 集成：接入外部工具与服务

9.1 什么是 MCP

9.2 配置 MCP Server

9.3 常用 MCP Server 推荐

第十章 进阶配置与最佳实践

10.1 配置文件结构

10.2 AGENTS.md：项目级配置

10.3 配置多个 Profile（多项目隔离）

10.4 常用 config 命令

10.5 ACP 编辑器集成

10.6 故障排除常用命令

第十一章 常见问题解答（FAQ）

第十二章 推荐学习路径与资源

12.1 新手三步走

12.2 官方资源

12.3 快速命令速查表

关注我，持续获取 AI 编程干货

第一章 认识 Hermes Agent

1.1 什么是 Hermes Agent

Hermes Agent 是由 NousResearch 开源的一款自进化 AI 智能体，口号是 "The agent that grows with you"（跟你一起成长的 Agent）。它不是普通的聊天机器人，而是一个具备持久记忆、技能积累和自主学习能力的终端 AI 助手。

截至 2026 年 4 月，该项目已在 GitHub 上获得超过 8,700 星标，拥有 142 名贡献者，是当前最受关注的开源 AI Agent 项目之一。

1.2 Hermes Agent 的核心特性

会学习：闭合学习循环

Hermes 最大的亮点在于其闭合学习循环（Closed Learning Loop）。每次完成复杂任务后，Agent 会自动将成功经验总结为「技能（Skill）」，下次遇到类似任务时直接调用，越用越聪明。

会记忆：持久化跨会话记忆

普通 AI 聊天工具每次对话都是全新开始，没有上下文记忆。Hermes 通过 MEMORY.md、USER.md 等机制将重要信息持久化存储，并借助 FTS5 全文搜索引擎让 Agent 在任意时刻召回历史对话。

多平台接入：不被绑定在笔记本上

Hermes 支持通过 Telegram、Discord、Slack、WhatsApp、Signal 等主流即时通讯工具与 Agent 交互，实现随时随地访问。同时支持 Docker、SSH、Daytona、Modal 等多种终端后端，真正做到云端部署、按需唤醒。

多模型支持：不锁定任何提供商

Hermes 支持超过 20 种 LLM 提供商，包括 OpenAI、Anthropic Claude、DeepSeek、Qwen、Gemini、GLM 等，通过一条命令 hermes model 随时切换，无需修改任何代码。

定时自动化：让 Agent 独立工作

Hermes 内置 cron 调度器，只需用自然语言描述任务，Agent 就会自动设置定时计划，无人值守地运行日报、备份、监控等自动化任务，并将结果推送到指定平台。

📌 一句话总结：Hermes Agent = 终端 AI 助手 + 自学习技能库 + 跨平台接入 + 多模型支持 + 定时自动化，是目前功能最完整的开源 AI Agent 之一。

1.3 Hermes Agent 与普通 AI 工具的对比

| 对比维度 | 普通 AI 聊天工具 | Hermes Agent |
| --- | --- | --- |
| 对话记忆 | 每次对话重新开始，无记忆 | 持久化跨会话记忆，越用越懂你 |
| 技能积累 | 无法积累，每次重新摸索 | 自动创建技能，知识可复用 |
| 执行能力 | 仅生成文字，无法直接执行 | 可操作终端、文件系统、网络等 |
| 平台接入 | 受限于特定 App 或网页 | Telegram/Discord/CLI 等多平台 |
| 模型选择 | 通常绑定单一模型 | 20+ 提供商随时切换 |
| 自动化任务 | 不支持定时任务 | 内置 cron，无人值守运行 |
| 部署方式 | 仅本地或云端 SaaS | 本地/Docker/VPS/Serverless 均可 |

1.4 适合谁使用 Hermes Agent

•程序员、开发者：希望拥有一个能操作本地环境、读写文件、运行命令的 AI 助手

•AI 工具玩家：想深度探索开源 Agent 生态，体验最前沿的自主 AI 系统

•内容创作者：希望用 AI 自动化日常工作流，定时生成报告、整理资料

•远程办公人群：需要随时通过手机或即时通讯工具与 AI 助手交互

•研究人员：对 AI 强化学习、轨迹生成、Agent 训练感兴趣

第二章 安装与环境准备

2.1 系统要求

在安装 Hermes Agent 之前，请确认你的系统满足以下基本要求：

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Linux、macOS、WSL2（Windows 原生不支持）、Android Termux |
| Python | 3.11 及以上（安装脚本自动处理） |
| Node.js | 16+ （安装脚本自动处理） |
| 磁盘空间 | 建议预留至少 1GB 可用空间 |
| 网络 | 安装时需要联网，运行时取决于所选 LLM 提供商 |
| 模型上下文窗口 | 最低 64,000 tokens（大多数主流模型均满足） |

⚠️ Windows 用户须知：Hermes Agent 不支持 Windows 原生环境。请先安装 WSL2（Windows Subsystem for Linux），然后在 WSL2 终端内执行安装命令。WSL2 安装教程：https://learn.microsoft.com/zh-cn/windows/wsl/install

2.2 一键安装（推荐）

Hermes 提供了一键安装脚本，自动处理 Python、Node.js、依赖库以及 hermes 命令行工具的全部配置，无需提前安装任何前置依赖（仅需 git）。

在终端中运行以下命令：

curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

安装完成后，重新加载 Shell 配置：

\# Bash 用户

source ~/.bashrc

\# Zsh 用户

source ~/.zshrc

✅ 验证安装是否成功，运行以下命令，看到版本信息即表示安装成功： hermes --version

2.3 Android / Termux 安装

Hermes 也支持在 Android 手机上通过 Termux 运行，适合移动端体验。请参考官方文档的 Termux 专属指南，按照手动安装步骤操作，注意 Android 存在一些平台限制（部分工具集无法使用）。

2.4 开发者手动安装

如果你希望参与开发或需要自定义安装，可以使用以下手动方式：

\# 克隆仓库

git clone https://github.com/NousResearch/hermes-agent.git

cd hermes-agent

\# 初始化子模块（必须执行）

git submodule update --init mini-swe-agent

\# 安装 uv 包管理器

curl -LsSf https://astral.sh/uv/install.sh | sh

\# 创建虚拟环境并安装依赖

uv venv.venv --python 3.11

source.venv/bin/activate

uv pip install -e ".\[all,dev\]"

uv pip install -e "./mini-swe-agent"

\# 可选：安装 RL 训练相关组件

git submodule update --init tinker-atropos

uv pip install -e "./tinker-atropos"

2.5 安装语音功能（可选）

如果希望使用语音输入（麦克风）或语音播报功能，可以额外安装语音依赖：

pip install "hermes-agent\[voice\]"

\# 包含 faster-whisper，支持免费本地语音转文字

启动 Hermes 后，在对话中输入以下命令开启语音：

/voice on # 开启语音输入（Ctrl+B 开始录音）

/voice tts # 开启文字转语音播报

2.6 更新与卸载

hermes update # 更新到最新版本

hermes doctor # 诊断并修复常见问题

💡 如果你之前使用过 OpenClaw，可以使用 hermes claw migrate 命令自动迁移所有配置、记忆、技能和 API 密钥。

第三章 配置 LLM 提供商

3.1 选择并配置模型

安装完成后，首先需要配置 LLM（大语言模型）提供商。Hermes 支持 20+ 个提供商，你可以根据自己的情况选择最适合的一个。

运行以下命令进入交互式模型配置向导：

hermes model

3.2 支持的 LLM 提供商一览

| 提供商 | 说明 | 配置方式 |
| --- | --- | --- |
| Nous Portal | 订阅制，零配置，官方推荐 | hermes model 内 OAuth 登录 |
| Anthropic Claude | Claude Pro/Max 或 API Key | hermes model 授权或填入 API Key |
| OpenAI / Codex | GPT 系列模型 | 设备码授权或 API Key |
| OpenRouter | 200+ 模型统一接入 | 设置 OPENROUTER\_API\_KEY |
| DeepSeek | DeepSeek 直接 API | 设置 DEEPSEEK\_API\_KEY |
| Z.AI (GLM) | 智谱 GLM 模型 | 设置 GLM\_API\_KEY / ZAI\_API\_KEY |
| Kimi / Moonshot | 月之暗面系列模型 | 设置 KIMI\_API\_KEY |
| 阿里云 DashScope | Qwen 通义千问系列 | 设置 DASHSCOPE\_API\_KEY |
| Google Gemini | Gemini 系列（免费层可用） | hermes model 内 OAuth 授权 |
| xAI (Grok) | Grok 4 系列模型 | 设置 XAI\_API\_KEY |
| GitHub Copilot | GPT/Claude/Gemini 统一入口 | hermes model 内 OAuth 授权 |
| AWS Bedrock | Claude、Nova、DeepSeek 等 | 标准 boto3 授权 |
| Ollama / 本地模型 | 完全本地运行，无费用 | 自定义 Endpoint 配置 |

⚠️ 重要提示：所有模型必须支持至少 64,000 tokens 的上下文窗口，否则 Hermes 在启动时会拒绝使用该模型。绝大多数主流商用模型均满足此要求。如果使用本地模型（如 Ollama），请确保启动时指定：ollama run qwen2.5-coder:32b --ctx-size 65536

3.3 配置 API Key（以 OpenRouter 为例）

以下是通过环境变量配置 API Key 的标准流程：

\# 方式一：临时设置（当前终端会话有效）

export OPENROUTER\_API\_KEY="your\_api\_key\_here"

\# 方式二：写入 Hermes 配置文件（推荐，永久有效）

echo 'OPENROUTER\_API\_KEY=your\_api\_key\_here' >> ~/.hermes/.env

\# 然后运行模型选择

hermes model

3.4 随时切换模型

Hermes 的模型切换完全无缝，不需要重启，不需要修改任何代码：

\# 命令行方式

hermes model

\# 在对话中切换

/model openai:gpt-4o

/model anthropic:claude-opus-4-5

/model openrouter:deepseek/deepseek-r1

3.5 运行配置向导（推荐新手使用）

如果你希望一次性完成所有配置（模型、工具、网关等），可以运行全套配置向导：

hermes setup # 交互式配置向导，覆盖所有配置项

第四章 基础使用：开始你的第一次对话

4.1 启动 Hermes

配置好模型提供商之后，就可以启动 Hermes 开始对话了：

hermes # 经典 CLI 界面

hermes --tui # 现代 TUI 界面（推荐，支持鼠标、模态窗口）

启动后你会看到欢迎界面，其中显示当前使用的模型、可用工具和已加载的技能。直接输入内容按回车即可开始对话。

4.2 基础交互操作

多行输入

在输入框中按 Alt+Enter 或 Ctrl+J 可以换行，非常适合粘贴代码或输入复杂的多行提示词。

中断 Agent

如果 Agent 正在执行某个耗时任务，你可以随时发送新消息打断当前任务，Agent 会切换去处理你的新指令。也可以按 Ctrl+C 强制中断。

恢复上次会话

hermes --continue # 恢复最近一次会话

hermes -c # 简写形式

4.3 常用斜杠命令

在对话窗口中输入 / 会弹出命令自动补全菜单。以下是最常用的斜杠命令：

| 命令 | 功能说明 |
| --- | --- |
| /help | 显示所有可用命令列表 |
| /tools | 列出所有可用工具及状态 |
| /model | 交互式切换 LLM 提供商和模型 |
| /skills | 查看、搜索、安装技能 |
| /new 或 /reset | 开始新的对话（清空当前上下文） |
| /save | 保存当前对话内容 |
| /personality \[name\] | 切换 Agent 人格（如 pirate、assistant 等） |
| /compress | 压缩对话上下文，节省 token 用量 |
| /usage | 查看当前 token 使用量 |
| /retry | 重新执行上一轮对话 |
| /undo | 撤销上一轮对话 |
| /voice on | 开启语音输入功能 |
| /stop | 停止当前正在运行的任务（消息平台使用） |

4.4 让 Agent 操作终端

Hermes 不只是聊天工具，它可以直接执行系统操作。以下是一些典型示例：

\# 示例：查看磁盘使用情况

\> 查一下我的磁盘使用情况，列出最大的 5 个目录

\# 示例：文件操作

\> 在当前目录创建一个 README.md 文件，写上项目介绍

\# 示例：代码任务

\> 帮我写一个 Python 脚本，每天早上 9 点爬取 Hacker News 头条并发邮件给我

🔒 安全提示：Hermes 执行命令前会根据安全策略请求你的确认。建议在 Docker 容器或远程服务器等隔离环境中运行，可通过 hermes config set terminal.backend docker 切换到 Docker 模式。

4.5 配置终端执行后端

Hermes 支持多种终端执行后端，适合不同安全需求场景：

| 后端类型 | 特点 | 配置命令 |
| --- | --- | --- |
| local | 直接在本机执行（默认） | hermes config set terminal.backend local |
| docker | 在 Docker 容器内隔离执行（推荐） | hermes config set terminal.backend docker |
| ssh | 连接到远程服务器执行 | hermes config set terminal.backend ssh |
| daytona | Serverless 持久化环境，空闲时休眠 | hermes config set terminal.backend daytona |
| modal | 按需唤醒，几乎零成本 | hermes config set terminal.backend modal |

第五章 技能系统（Skills）：Agent 的程序性记忆

5.1 什么是技能（Skill）

技能是 Hermes 最核心的差异化特性之一。它本质上是一份结构化的知识文档（SKILL.md），告诉 Agent「在遇到某类任务时应该怎么做」。技能遵循渐进式披露（Progressive Disclosure）模式，只有在真正需要时才加载完整内容，有效控制 token 消耗。

所有技能存储在 ~/.hermes/skills/ 目录下，Agent 可以在完成复杂任务后自动创建新技能，也可以对已有技能进行自我改进。

5.2 技能的三个加载级别

| 级别 | 内容 | Token 消耗 |
| --- | --- | --- |
| Level 0 | skills\_list() — 技能列表 | 约 3,000 tokens（名称+描述） |
| Level 1 | skill\_view(name) — 技能完整内容 | 按技能大小而定 |
| Level 2 | skill\_view(name, path) — 技能参考文件 | 按文件大小而定 |

5.3 如何使用技能

每个已安装的技能都会自动注册为一个斜杠命令，使用非常简单：

\# 直接调用技能名

/gif-search 一只在玩耍的猫

/axolotl 帮我在自定义数据集上微调 Llama 3

/plan 设计一个用户认证系统的实现方案

\# 只输入技能名，让 Agent 询问你需要什么

/excalidraw

\# 查看所有可用技能

/skills

5.4 技能目录结构

~/.hermes/skills/ # 技能根目录（读写）

├── mlops/ # 分类目录

│ ├── axolotl/

│ │ ├── SKILL.md # 主技能文件（必须）

│ │ ├── references/ # 参考文档

│ │ ├── templates/ # 输出模板

│ │ └── scripts/ # 辅助脚本

│ └── vllm/

├── devops/

│ └── deploy-k8s/ # Agent 自动创建的技能

│ └── SKILL.md

└──.hub/ # Skills Hub 状态

5.5 从 Skills Hub 安装技能

Hermes 内置了完整的技能市场（Skills Hub），你可以搜索、预览、安装来自全球开发者贡献的技能：

\# 浏览所有技能

hermes skills browse

\# 搜索特定技能

hermes skills search kubernetes

hermes skills search react --source skills-sh

\# 预览技能内容（安装前检查）

hermes skills inspect openai/skills/k8s

\# 安装技能

hermes skills install openai/skills/k8s

hermes skills install official/security/1password

\# 更新已安装的技能

hermes skills check # 检查是否有更新

hermes skills update # 更新所有技能

5.6 支持的技能来源

| 来源 | 说明 | 示例 |
| --- | --- | --- |
| official | Hermes 官方维护的可选技能 | official/security/1password |
| skills-sh | Vercel 的公开技能目录 | skills-sh/vercel-labs/json-render |
| well-known | 网站发布的标准化技能端点 | well-known:https://mintlify.com/docs |
| github | 直接从 GitHub 仓库安装 | openai/skills/k8s |
| clawhub | 第三方社区技能市场 | clawhub.ai 上发布的技能 |
| lobehub | LobeHub 智能体目录 | https://lobehub.com/ |

5.7 Agent 自动创建技能

Hermes 会在以下情况下自动为你创建新技能，无需手动干预：

•完成了需要 5 步以上工具调用的复杂任务之后

•碰到错误并找到了可行的解决路径

•你纠正了 Agent 的操作方式，Agent 学到了更好的方法

•发现了一个非显而易见的工作流程

💡 这就是 Hermes 的核心价值：用的次数越多，它积累的专属技能越丰富，处理同类任务的效率越高。这是真正意义上的「越用越聪明」。

第六章 持久化记忆：让 Agent 真正认识你

6.1 记忆系统概述

Hermes 的记忆系统让 Agent 能够跨会话积累对你的了解。不同于每次都从零开始的普通 AI 对话，Hermes 会主动记录和整理重要信息，形成越来越完整的用户画像。

6.2 记忆文件说明

| 文件 | 用途 |
| --- | --- |
| MEMORY.md | 通用记忆：任务笔记、技术偏好、常用路径、重要发现等 |
| USER.md | 用户画像：你的背景、习惯、偏好、工作方式等 |
| SOUL.md | Agent 人格：定义 Agent 的角色、语气和行为风格 |

6.3 记忆的使用方式

记忆系统完全自动运行。以下是主要的交互场景：

\# 查看当前记忆内容

\> 你记住了哪些关于我的信息？

\# 主动要求记住某件事

\> 记住我更喜欢用 TypeScript 而不是 JavaScript

\# 查看跨会话的对话历史

\> 搜索我们上周讨论过的 Docker 部署问题

\# 清除记忆（谨慎使用）

\> 请清除你关于我工作项目的所有记忆

6.4 FTS5 全文搜索

Hermes 内置了基于 SQLite FTS5 的全文搜索引擎，可以对所有历史对话进行关键词搜索，并通过 LLM 进行语义摘要。

\> 搜索我们讨论过的 Kubernetes 相关内容

\> 找到上次我遇到的 Python 依赖冲突问题的解决方案

6.5 记忆最佳实践

1.在每次重要对话开始时，询问 Agent 记住了什么（确认上下文）

2.对于重要的技术决策，主动告诉 Agent 记住（避免重复说明）

3.定期审查 MEMORY.md，删除过时的信息

4.善用 /compress 命令压缩超长对话，节省 token 消耗

📌 记忆文件位于 ~/.hermes/MEMORY.md 和 ~/.hermes/USER.md，你可以直接用文本编辑器查看和编辑这些文件，对 Agent 的记忆进行精细化管理。

第七章 消息平台网关：随时随地访问你的 Agent

7.1 消息网关概述

Hermes 的消息网关（Gateway）让你可以通过 Telegram、Discord、Slack、WhatsApp、Signal 等日常使用的即时通讯软件与 Agent 交互，实现真正意义上的随时随地访问。一个 Gateway 进程可以同时监听多个平台。

7.2 支持的消息平台

| 平台 | 适用场景 | 配置难度 |
| --- | --- | --- |
| Telegram | 最推荐，功能完整，支持语音消息 | ⭐ 简单 |
| Discord | 适合开发者社区，支持语音频道 | ⭐ 简单 |
| Slack | 企业团队协作场景 | ⭐⭐ 中等 |
| WhatsApp | 日常通讯场景 | ⭐⭐ 中等 |
| Signal | 注重隐私保护 | ⭐⭐ 中等 |
| Email | 邮件定时报告场景 | ⭐⭐⭐ 较复杂 |
| Home Assistant | 智能家居自动化场景 | ⭐⭐⭐ 较复杂 |

7.3 配置 Telegram 网关（以 Telegram 为例）

Telegram 是最推荐的消息平台，以下是配置步骤：

5.在 Telegram 中搜索并启动 @BotFather

6.发送 /newbot 命令，按提示创建一个新机器人

7.记下 BotFather 给你的 Bot Token（格式类似：123456789:AABBcc...）

8.将 Token 保存到 Hermes 配置中：

echo 'TELEGRAM\_BOT\_TOKEN=你的token' >> ~/.hermes/.env

9.启动网关配置向导：

hermes gateway setup # 交互式配置向导

hermes gateway start # 启动消息网关

10.在 Telegram 中找到你的机器人，发送 /start 即可开始使用

7.4 消息平台专用斜杠命令

| 命令 | 功能 |
| --- | --- |
| /new 或 /reset | 开始新的对话 |
| /stop | 停止 Agent 当前正在执行的任务 |
| /model | 切换 LLM 模型 |
| /status | 查看当前 Agent 状态 |
| /sethome | 将当前平台设为默认通知接收平台 |
| /compress | 压缩上下文 |
| /usage | 查看 token 使用量 |

📱 实际应用场景举例：早上起床前用 Telegram 给 Agent 发消息「帮我检查一下服务器日志，有没有异常」，Agent 在你的云服务器上执行命令并把结果发回给你。这才是 AI Agent 的正确打开方式。

第八章 定时任务与自动化

8.1 定时任务系统概述

Hermes 内置了完整的 cron 调度器，你只需用自然语言描述任务，Agent 会自动创建定时计划并在指定时间无人值守地执行，结果推送到你指定的平台。

8.2 用自然语言创建定时任务

\# 示例 1：每日新闻摘要

\> 每天早上 9 点，查看 Hacker News 的 AI 相关新闻，

整理成中文摘要发到我的 Telegram

\# 示例 2：服务器监控

\> 每小时检查一次 /var/log/nginx/error.log，

如果有 500 错误就立即通知我

\# 示例 3：周报生成

\> 每周五下午 6 点，统计本周的 Git 提交记录，

生成工作周报并发邮件给我

\# 示例 4：数据备份

\> 每天凌晨 2 点，把 ~/projects 目录备份到 S3

8.3 管理定时任务

hermes cron list # 查看所有定时任务

hermes cron stop # 停止定时任务

hermes cron start # 启动定时任务

\# 也可以在对话中管理

\> 显示我所有的定时任务

\> 停止那个每小时检查日志的任务

⚡ 要让定时任务在你不在线时也能运行，建议在 VPS 或云服务器上部署 Hermes，并使用 nohup hermes gateway start & 让网关在后台持续运行。

第九章 MCP 集成：接入外部工具与服务

9.1 什么是 MCP

MCP（Model Context Protocol，模型上下文协议）是 Anthropic 主导的开放标准，允许 AI 助手通过标准化接口连接外部工具和数据源。Hermes 原生支持 MCP，通过简单的配置即可将 GitHub、数据库、云服务等外部工具接入 Agent。

9.2 配置 MCP Server

在 ~/.hermes/config.yaml 文件中添加 mcp\_servers 配置：

\# ~/.hermes/config.yaml

mcp\_servers:

github:

command: npx

args: \["-y", "@modelcontextprotocol/server-github"\]

env:

GITHUB\_PERSONAL\_ACCESS\_TOKEN: "ghp\_xxx"

filesystem:

command: npx

args: \["-y", "@modelcontextprotocol/server-filesystem", "/home/user"\]

postgres:

command: npx

args: \["-y", "@modelcontextprotocol/server-postgres"\]

env:

POSTGRES\_CONNECTION\_STRING: "postgresql://user:pass@localhost/db"

9.3 常用 MCP Server 推荐

| MCP Server | 功能 | 适用场景 |
| --- | --- | --- |
| server-github | 操作 GitHub 仓库、Issue、PR | 代码管理 |
| server-filesystem | 访问本地文件系统 | 文件操作 |
| server-postgres | 连接 PostgreSQL 数据库 | 数据分析 |
| server-brave-search | Brave 隐私搜索引擎 | 网络搜索 |
| server-slack | 读写 Slack 消息和频道 | 团队协作 |
| server-google-maps | 地图、位置、路线查询 | 地理信息 |

🔗 完整的 MCP Server 列表可以在 https://github.com/modelcontextprotocol/servers 查找，社区已贡献了数百个官方和第三方 MCP Server。

第十章 进阶配置与最佳实践

10.1 配置文件结构

Hermes 的所有配置都存储在 ~/.hermes/ 目录下：

~/.hermes/

├── config.yaml # 主配置文件（模型、工具、MCP 等）

├──.env # API Keys 和敏感配置

├── MEMORY.md # Agent 通用记忆

├── USER.md # 用户个人画像

├── SOUL.md # Agent 人格定义

├── AGENTS.md # 工作区指令（项目级配置）

├── skills/ # 技能库目录

├── sessions/ # 历史会话记录

└── logs/ # 运行日志

10.2 AGENTS.md：项目级配置

在任意项目目录下创建 AGENTS.md 文件，可以为该项目提供专属的上下文和指令。每次在该目录启动 Hermes 时，文件内容会自动加载到 Agent 的上下文中。

\# 示例：在 ~/my-project/AGENTS.md 中写入

\# 项目说明

这是一个 React + TypeScript 项目，后端使用 FastAPI。

数据库：PostgreSQL，连接字符串在.env 文件中。

\# 约定

\- 所有新功能都要写单元测试

\- 使用 ESLint + Prettier 格式化代码

\- Git commit 信息遵循 Conventional Commits 规范

10.3 配置多个 Profile（多项目隔离）

Hermes 支持多个独立的配置 Profile，适合需要在不同项目之间切换不同 Agent 配置的场景：

hermes -p work # 使用 "work" profile 启动

hermes -p personal # 使用 "personal" profile 启动

\# 不同 profile 拥有独立的：

\# - config.yaml（模型配置、工具配置）

\# - MEMORY.md（记忆文件）

\# - skills/（技能库）

10.4 常用 config 命令

hermes config show # 查看当前所有配置

hermes config set terminal.backend docker # 修改单项配置

hermes config migrate # 迁移旧版配置格式

\# 在对话中查看配置

/insights # 查看 7 天使用统计

/insights --days 30 # 查看 30 天使用统计

10.5 ACP 编辑器集成

Hermes 可以作为 ACP（Agent Communication Protocol）服务器运行，与 VS Code、Zed、JetBrains 等编辑器深度集成，实现在 IDE 内直接使用 Agent 的工作流：

\# 安装 ACP 支持

pip install -e '.\[acp\]'

\# 启动 ACP 服务器

hermes acp

10.6 故障排除常用命令

hermes doctor # 自动诊断并输出问题报告

hermes update # 更新到最新版本

hermes --version # 查看当前版本号

\# 查看运行日志

tail -f ~/.hermes/logs/hermes.log

📌 如果遇到无法解决的问题，可以前往 GitHub Issues 提交 Bug 报告（https://github.com/NousResearch/hermes-agent/issues），或者在 Discord 社区寻求帮助（https://discord.gg/NousResearch）。

第十一章 常见问题解答（FAQ）

Q1：安装脚本运行失败怎么办？

首先运行 hermes doctor 诊断问题。常见原因包括：网络访问 GitHub 受限（可使用代理）、Python 版本过低（需 3.11+）、git 命令不存在（需先安装 git）。

Q2：模型不满足 64K context 要求怎么办？

如果使用 Ollama 本地模型，请在启动时指定上下文大小：ollama run qwen2.5-coder:32b --ctx-size 65536。商用 API 模型（GPT-4、Claude、DeepSeek 等）均默认满足此要求。

Q3：Agent 执行命令需要我确认太麻烦了，能关掉吗？

可以将常用的无害命令加入自动允许白名单：hermes config set approval.auto\_approve "ls,cat,git status"。建议谨慎操作，或在 Docker 隔离环境中运行后关闭确认。

Q4：技能系统和普通提示词有什么区别？

普通提示词每次都需要重新输入，且会占用大量上下文 token。技能（Skill）是结构化的知识文档，只在需要时加载，且可以被 Agent 自动创建和改进，是真正可复用的知识资产。

Q5：如何在多台设备之间同步配置和技能？

建议将 ~/.hermes/ 目录（排除.env 等敏感文件）同步到 Git 仓库或云存储，在不同设备上 clone 后即可恢复完整配置。注意不要将.env 和 sessions/ 目录提交到公开仓库。

Q6：Hermes 会把我的对话数据发送给 NousResearch 吗？

不会。Hermes 是完全开源的本地软件，你的对话数据只会发送到你配置的 LLM 提供商（如 OpenAI、Anthropic 等），NousResearch 不会收集任何对话数据。

Q7：我可以在服务器上无头（Headless）模式运行 Hermes 吗？

完全可以。在服务器上启动消息网关 hermes gateway start 后，通过 Telegram 等消息平台与 Agent 交互，即是无头运行模式，非常适合 VPS 部署。

Q8：如何从 OpenClaw 迁移到 Hermes？

运行 hermes claw migrate 命令，可以自动迁移 SOUL.md 人格文件、记忆文件、自定义技能、命令白名单、消息平台配置和 API Keys 等所有数据。

第十二章 推荐学习路径与资源

12.1 新手三步走

| 阶段 | 目标 | 具体行动 |
| --- | --- | --- |
| 第一步 （第1天） | 跑起来，能对话 | 安装 Hermes → 配置模型 → 运行 hermes 开始对话 |
| 第二步 （第2-3天） | 用起来，感受能力 | 让 Agent 操作文件/终端 → 试用斜杠命令 → 安装几个技能 |
| 第三步 （第1周） | 深用，建立自己的工作流 | 配置消息平台 → 创建定时任务 → 接入 MCP → 定制 SOUL.md |

12.2 官方资源

•官方文档：https://hermes-agent.nousresearch.com/docs/

•GitHub 仓库：https://github.com/NousResearch/hermes-agent

•Discord 社区：https://discord.gg/NousResearch

•Skills Hub：https://agentskills.io

•GitHub Issues（提交 Bug）：https://github.com/NousResearch/hermes-agent/issues

12.3 快速命令速查表

| 命令 | 用途 |
| --- | --- |
| hermes | 启动交互式对话 |
| hermes --tui | 启动现代 TUI 界面 |
| hermes model | 配置 LLM 提供商和模型 |
| hermes tools | 配置工具集 |
| hermes setup | 全套配置向导 |
| hermes skills browse | 浏览技能市场 |
| hermes skills install | 安装技能 |
| hermes gateway setup | 配置消息平台 |
| hermes gateway start | 启动消息网关 |
| hermes cron list | 查看定时任务列表 |
| hermes update | 更新到最新版本 |
| hermes doctor | 诊断问题 |
| hermes --continue | 恢复上次会话 |
| hermes -p | 使用指定 Profile 启动 |
| hermes claw migrate | 从 OpenClaw 迁移配置 |

关注我，持续获取 AI 编程干货

程序员康健 | 程序员AI破局指南

专注 AI 编程工具 · 实战教程 · 职场破局

| 📱 微信公众号  程序员AI破局指南  ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  ✦ AI 编程工具深度评测  ✦ Claude Code / Cursor 实战教程  ✦ 程序员 AI 转型路线图 | 🎬 微信视频号  程序员康健  ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  ✦ AI 工具视频上手教程  ✦ 真实项目 AI 编程演示  ✦ 每周最新 AI 工具速览 |
| --- | --- |

如果本教程对你有帮助，欢迎转发给有需要的朋友 🙌

持续输出 AI 教程指南内容，陪你用 AI 走得更远

📚 相关阅读

- [OpenAI Codex 完全新手指南：Codex 凭什么和 Claude Code 抢饭碗？](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487684&idx=1&sn=8526ad23259fcccde5483bcd41677ebc&scene=21#wechat_redirect)
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