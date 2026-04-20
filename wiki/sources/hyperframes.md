---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/heygen-comhyperframes Write HTML. Render video. Built for agents.md
tags: [hyperframes, video-rendering, html-video, agentic, heygen]
---

# Hyperframes: Write HTML. Render video. Built for agents.

## 摘要

Hyperframes 是由 HeyGen 开源的视频渲染框架，核心理念是"写 HTML，渲染视频"。它允许开发者使用带有 data 属性的 HTML 文件来创建、预览和渲染视频作品，并为 AI Agent 提供一流支持。框架采用 HTML-native 设计（无需 React 或专有 DSL），CLI 默认非交互式，专为 Agent 驱动的工作流设计。支持确定性渲染（相同输入 = 相同输出），并采用 Frame Adapter 模式，可接入 GSAP、Lottie、CSS、Three.js 等任意动画运行时。Hyperframes 还提供 50+ 现成模块和组件（社交叠加层、着色器过渡、数据可视化、电影效果），以及配套的 skill 系统，可教 AI Agent（Claude Code、Cursor、Gemini CLI、Codex）如何编写正确的 composition 和 GSAP 动画。

## 核心要点

- **HTML-native 视频合成**：使用带 data 属性的 HTML 元素（video、img、audio 等）定义视频时间线，无需学习专有 DSL
- **AI-first 设计**：CLI 默认非交互式，专为 Agent 驱动工作流设计；提供 `/hyperframes`、`/hyperframes-cli`、`/gsap` 等 skill 命令
- **确定性渲染**：相同输入产生相同输出，适合自动化流水线
- **Frame Adapter 模式**：支持 GSAP、Lottie、CSS、Three.js 等动画运行时
- **50+ 现成组件**：通过 `npx hyperframes add <block>` 安装，涵盖社交叠加、着色器过渡、数据图表、电影效果
- **多包架构**：hyperframes（CLI）、@hyperframes/core（类型/解析器/运行时）、@hyperframes/engine（Puppeteer+FFmpeg 捕获引擎）、@hyperframes/producer（完整渲染管线）、@hyperframes/studio（浏览器编辑器）、@hyperframes/player（Web 组件）
- **Skill 系统**：通过 `npx skills add heygen-com/hyperframes` 安装，教 Agent 框架特定模式
- **使用方式**：Agent 对话生成（"帮我做一个 10 秒产品介绍视频"）或手动项目初始化（`npx hyperframes init`）

## 原始文件

- [原始文件](../../raw/archive/heygen-comhyperframes Write HTML. Render video. Built for agents.md)
