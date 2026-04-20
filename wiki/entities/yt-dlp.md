---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [panniantong-agent, auto-video-slicing]
tags: [video-download, subtitle-extraction, cli, open-source, youtube, bilibili]
---

# yt-dlp

yt-dlp 是一款功能强大的开源命令行视频下载工具，是 youtube-dl 的活跃分支，支持从 YouTube、Bilibili 等 1800+ 站点下载视频并提取字幕，完全免费且无需 API 费用。

## 核心组件与特性

- **多平台支持**：覆盖 YouTube、Bilibili、Twitter/X、Reddit、TikTok、Instagram 等 1800+ 视频网站，是 Agent-Reach 等 AI Agent 脚手架的核心视频渠道工具。
- **字幕提取**：可自动下载视频的内嵌字幕、自动生成字幕（auto-subtitles）或提取独立字幕文件，支持多语言选择。
- **格式灵活**：支持下载不同分辨率、编码格式和音轨，可按需选择仅音频、仅视频或完整合并。
- **无 API 费用**：纯开源 CLI 工具，所有功能本地执行，无需向任何平台支付 API 费用。
- **活跃维护**：作为 youtube-dl 的分支，更新频率高，对新站点和反爬机制的适配更及时。

## 使用指南与最佳实践

- **基础下载**：`yt-dlp "<URL>"` 即可下载最高质量视频；配合 `-f` 参数可精确选择格式。
- **字幕提取**：`yt-dlp --write-subs --sub-langs zh-CN,en --skip-download "<URL>"` 仅下载指定语言字幕，不下载视频本身。
- **集成到自动化工作流**：在 AutoClip 等 AI 视频切片工具中，yt-dlp 作为后端素材获取环节，负责从 YouTube/B 站拉取原始视频。
- **Agent 集成**：在 Agent-Reach 脚手架中，AI Agent 可直接调用 yt-dlp 命令获取视频内容和字幕，为后续 AI 分析提供输入。
- **Cookie 配置**：对于需要登录的站点，可通过 `--cookies-from-browser` 参数直接使用浏览器的登录状态，无需手动管理 Cookie 文件。

## 相关来源

- [[panniantong-agent]]
- [[auto-video-slicing]]
