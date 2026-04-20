---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Agent-Reach AI agent internet search tool.md
tags: [agent-reach, internet-access, twitter, reddit, youtube, bilibili, xiaohongshu, mcp, cli]
---

# Agent-Reach：给 AI Agent 一键装上互联网能力

## 摘要

Agent-Reach 是一个开源脚手架项目，旨在让 AI Agent（Claude Code、OpenClaw、Cursor、Windsurf 等）一键获得互联网阅读和搜索能力，完全免费、零 API 费用。它整合了 15+ 平台的访问能力，包括网页（Jina Reader）、YouTube（yt-dlp）、Twitter/X（twitter-cli）、Reddit（rdt-cli）、B站（bili-cli）、小红书（xhs-cli）、GitHub（gh CLI）、微信公众号（Exa + Camoufox）、微博、V2EX、雪球、LinkedIn、抖音、RSS、全网搜索（Exa via mcporter）等。Agent-Reach 的设计理念是「脚手架而非框架」——安装完成后，Agent 直接调用上游工具，不经过包装层；每个渠道都是可插拔的，不满意可替换。安装只需一句话：`帮我安装 Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md`。安全方面，Cookie 只存在本地（`~/.agent-reach/config.yaml`，权限 600），支持安全模式（`--safe`）和 Dry Run（`--dry-run`）。

## 核心要点

- **一句话安装**：复制安装指令给 AI Agent，Agent 自动完成 CLI 工具安装、系统依赖检测、搜索引擎配置、环境判断、SKILL.md 注册等全部步骤。
- **15+ 平台支持**：网页阅读、YouTube 字幕提取、Twitter/X 读推文和搜索、Reddit 搜索和读帖、B站字幕和搜索、小红书阅读和搜索、GitHub 仓库浏览、微信公众号搜索和阅读、微博热搜和搜索、V2EX、雪球、LinkedIn、抖音视频解析、RSS 订阅、全网语义搜索。
- **零 API 费用**：所有后端均为开源工具（twitter-cli、rdt-cli、xhs-cli、yt-dlp、Jina Reader、Exa 等），无需付费 API Key；唯一可选成本是服务器代理（约 $1/月，本地不需要）。
- **脚手架设计理念**：安装完成后 Agent 直接调用上游工具，不经过 Agent Reach 包装层；每个渠道是可插拔的独立文件（`channels/` 目录），可替换为其他实现。
- **安全设计**：Cookie 本地存储不上传（权限 600）、安全模式不自动修改系统、完全开源可审查、Dry Run 预览操作、可插拔架构（不信任某组件可直接替换）。
- **诊断工具**：`agent-reach doctor` 一条命令检测所有渠道状态，告知哪个通、哪个不通、怎么修。
- **兼容所有 Agent**：Claude Code、OpenClaw、Cursor、Windsurf、Codex 等任何能跑命令行的 Agent 都能使用。
- **Cookie 配置流程**：浏览器登录 → Cookie-Editor 插件导出 → 发给 Agent 配置，比扫码更简单可靠；建议用专用小号避免封号风险。
- **当前选型**：Jina Reader（网页）、twitter-cli（Twitter）、rdt-cli（Reddit）、yt-dlp（YouTube+B站）、xhs-cli（小红书）、gh CLI（GitHub）、Exa via mcporter（全网搜索）等。

## 原始文件

- [原始文件](../../raw/archive/Agent-Reach AI agent internet search tool.md)
