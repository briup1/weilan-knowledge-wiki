---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/last30days-skill-cn chinese internet research agent.md
tags: [ai-agent, skill, web-crawler, research, chinese-platforms]
---

# last30days-skill-cn：中国平台深度研究引擎

## 摘要

last30days-cn 是一个面向 AI Agent 的 Skill，能够自动搜索中国互联网 8 大主流平台（微博、小红书、B站、知乎、抖音、微信、百度、头条）最近 30 天的内容，综合分析后生成有据可查的研究报告。该项目是 mvanhorn/last30days-skill 的中文本土化 fork，v2.0 版本集成 MediaCrawler 爬虫引擎思路，通过 Playwright 浏览器自动化实现 7/8 平台零 API Key 可用。支持三级自动降级策略（API 优先 → 爬虫模式 → 公开接口），并配备基于相关性（45%）、时效性（25%）和互动度（30%）的智能评分系统。兼容 Cursor、Claude Code、OpenClaw、Gemini CLI 等多种 Agent 平台。

## 核心要点

- **8 大平台覆盖**：微博、小红书、B站、知乎、抖音、微信、百度、今日头条，涵盖社交媒体、视频、问答、搜索等主流中文内容生态
- **三级降级策略**：API 模式 → 爬虫模式（Playwright）→ 公开接口，确保最大可用性；安装 Playwright 后 7/8 平台无需 API Key
- **v2.0 核心升级**：集成 MediaCrawler 爬虫引擎，7/8 平台零配置可用；智能降级；Cookie 持久化缓存；修复 marketplace.json 缺少 owner 字段的 bug
- **评分系统**：每条结果综合评分（0-100）基于相关性 45%、时效性 25%、互动度 30%，各平台互动指标不同（如微博看转发/评论/点赞，B站看播放/弹幕/投币/收藏）
- **多 Agent 兼容**：支持 Cursor（推荐）、Claude Code（`claude install`）、OpenClaw/ClawHub、Gemini CLI 及任何支持 Bash/Read/Write 工具的通用 Agent
- **输出格式**：支持 compact、json、md、context、path 等多种输出模式，支持 `--quick` 快速搜索和 `--deep` 深度搜索
- **法律合规**：项目明确声明仅供学习研究，严禁商业用途，需遵守各平台 ToS 和 robots.txt

## 原始文件

- [原始文件](../../raw/archive/last30days-skill-cn chinese internet research agent.md)
