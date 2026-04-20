---
title: "heygen-com/hyperframes: Write HTML. Render video. Built for agents."
source: "https://github.com/heygen-com/hyperframes"
author:
published:
created: 2026-04-18
description: "Write HTML. Render video. Built for agents. Contribute to heygen-com/hyperframes development by creating an account on GitHub."
tags:
  - "clippings"
---
![HyperFrames](https://github.com/heygen-com/hyperframes/raw/main/docs/logo/light.svg)

**Write HTML. Render video. Built for agents.  
写 HTML。渲染视频。为经纪人打造。**

[![HyperFrames demo — HTML code on the left transforms into a rendered video on the right](https://camo.githubusercontent.com/5f0ea07fbd400bb7d7086410fbff25b62404440c7926e71125fd36b39bfef247/68747470733a2f2f7374617469632e68657967656e2e61692f68797065726672616d65732d6f73732f646f63732f696d616765732f726561646d652d64656d6f2e676966)](https://camo.githubusercontent.com/5f0ea07fbd400bb7d7086410fbff25b62404440c7926e71125fd36b39bfef247/68747470733a2f2f7374617469632e68657967656e2e61692f68797065726672616d65732d6f73732f646f63732f696d616765732f726561646d652d64656d6f2e676966)

Hyperframes is an open-source video rendering framework that lets you create, preview, and render HTML-based video compositions — with first-class support for AI agents.  
Hyperframes 是一个开源视频渲染框架，允许你创建、预览和渲染基于 HTML 的视频作品——并支持一流的 AI 代理。

## Quick Start 快速入门

Install the HyperFrames skills, then describe the video you want:  
安装 HyperFrames 技能，然后描述你想要的视频：

```
npx skills add heygen-com/hyperframes
```

This teaches your agent (Claude Code, Cursor, Gemini CLI, Codex) how to write correct compositions and GSAP animations. In Claude Code, the skills register as slash commands — invoke `/hyperframes` to author compositions, `/hyperframes-cli` for CLI commands, and `/gsap` for animation help.  
这会教你的代理（Claude Code、Cursor、Gemini CLI、Codex）如何编写正确的构图和 GSAP 动画。在 Claude Code 中，技能以斜杠命令注册——调用 `/hyperframes` 来创作合成，/ `hyperframes-cli` 用于 CLI 命令，/ `gsap` 用于动画帮助。

#### Try it: example prompts 试试看：示例提示

Copy any of these into your agent to get started. The `/hyperframes` prefix loads the skill context explicitly so you get correct output the first time.  
把这些内容复制到你的代理中即可开始。 `/hyperframes` 前缀会显式加载技能上下文，这样你第一次就能得到正确的输出。

**Cold start — describe what you want:  
冷启动——描述你想要什么：**

> Using `/hyperframes`, create a 10-second product intro with a fade-in title, a background video, and background music.  
> 利用 `/hyperframes` ，创建一个 10 秒的产品介绍，带有淡入标题、背景视频和背景音乐。

**Warm start — turn existing context into a video:  
热身开场——将现有语境转化为视频：**

> Take a look at this GitHub repo [https://github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) and explain its uses and architecture to me using `/hyperframes`.  
> 看看这个 GitHub 仓库 [https://github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) ，用 `/hyperframes` 向我解释它的用途和架构。

> Summarize the attached PDF into a 45-second pitch video using `/hyperframes`.  
> 用 `/hyperframes` 将附带的 PDF 总结成一个 45 秒的简短视频。

> Turn this CSV into an animated bar chart race using `/hyperframes`.  
> 用 `/hyperframes` 把这个 CSV 变成一个动画条形图竞速。

**Format-specific:格式特定：**

> Make a 9:16 TikTok-style hook video about \[topic\] using `/hyperframes`, with bouncy captions synced to a TTS narration.  
> 用 `/hyperframes` 制作一个 9：16 的 TikTok 风格 hook 视频，主题是关于\[topic\]，配上跳跃字幕与 TTS 旁白同步。

**Iterate — talk to the agent like a video editor:  
迭代——像视频剪辑师一样与代理交流：**

> Make the title 2x bigger, swap to dark mode, and add a fade-out at the end.  
> 把标题放大2倍，切换到暗黑模式，并在结尾加入渐淡。

> Add a lower third at 0:03 with my name and title.  
> 在0：03处加上我的名字和职称。

The agent handles scaffolding, animation, and rendering. See the [prompting guide](https://hyperframes.heygen.com/guides/prompting) for more patterns.  
代理负责脚手架、动画和渲染。更多模式请参见 [提示指南](https://hyperframes.heygen.com/guides/prompting) 。

### Option 2: Start a project manually选项二：手动启动项目

```
npx hyperframes init my-video
cd my-video
npx hyperframes preview      # preview in browser (live reload)
npx hyperframes render       # render to MP4
```

`hyperframes init` installs skills automatically, so you can hand off to your AI agent at any point.  
`Hyperframes 的初始化` 会自动安装技能，所以你可以随时交给你的 AI 代理。

**Requirements:** Node.js >= 22, FFmpeg  
**要求：** Node.js >= 22，FFmpeg

## Why Hyperframes? 为什么选择超帧？

- **HTML-native** — compositions are HTML files with data attributes. No React, no proprietary DSL.  
	HTML **原生** ——组合是带有数据属性的 HTML 文件。没有 React，没有专有 DSL。
- **AI-first** — agents already speak HTML. The CLI is non-interactive by default, designed for agent-driven workflows.  
	AI **优先** ——客服已经会说 HTML。CLI 默认是非交互式的，专为代理驱动的工作流程设计。
- **Deterministic rendering** — same input = identical output. Built for automated pipelines.  
	确定 **性渲染** ——相同输入=相同输出。为自动化流水线设计。
- **Frame Adapter pattern** — bring your own animation runtime (GSAP, Lottie, CSS, Three.js).  
	帧 **适配器模式** ——自带动画运行时（GSAP、Lottie、CSS Three.js）。

## How It Works 工作原理

Define your video as HTML with data attributes:  
将你的视频定义为带有数据属性的 HTML：

```
<div id="stage" data-composition-id="my-video" data-start="0" data-width="1920" data-height="1080">
  <video
    id="clip-1"
    data-start="0"
    data-duration="5"
    data-track-index="0"
    src="intro.mp4"
    muted
    playsinline
  ></video>
  <img
    id="overlay"
    class="clip"
    data-start="2"
    data-duration="3"
    data-track-index="1"
    src="logo.png"
  />
  <audio
    id="bg-music"
    data-start="0"
    data-duration="9"
    data-track-index="2"
    data-volume="0.5"
    src="music.wav"
  ></audio>
</div>
```

Preview instantly in the browser. Render to MP4 locally or in Docker.  
在浏览器中立即预览。本地或在 Docker 中渲染成 MP4。

## Catalog 目录

50+ ready-to-use blocks and components — social overlays, shader transitions, data visualizations, and cinematic effects:  
50+ 现成模块和组件——社交叠加层、着色器过渡、数据可视化和电影效果：

```
npx hyperframes add flash-through-white   # shader transition
npx hyperframes add instagram-follow      # social overlay
npx hyperframes add data-chart            # animated chart
```

Browse the full catalog at **[hyperframes.heygen.com/catalog](https://hyperframes.heygen.com/catalog/blocks/data-chart)**.  
完整目录请在 **[hyperframes.heygen.com/catalog](https://hyperframes.heygen.com/catalog/blocks/data-chart)** 浏览。

## Documentation 文献资料

Full documentation at **[hyperframes.heygen.com/introduction](https://hyperframes.heygen.com/introduction)** — [Quickstart](https://hyperframes.heygen.com/quickstart) | [Guides](https://hyperframes.heygen.com/guides/gsap-animation) | [API Reference](https://hyperframes.heygen.com/packages/core) | [Catalog](https://hyperframes.heygen.com/catalog/blocks/data-chart)  
完整文档见 **[hyperframes.heygen.com/introduction](https://hyperframes.heygen.com/introduction)** — [快速入门](https://hyperframes.heygen.com/quickstart) | [指南](https://hyperframes.heygen.com/guides/gsap-animation) | [API 参考](https://hyperframes.heygen.com/packages/core) | [目录](https://hyperframes.heygen.com/catalog/blocks/data-chart)

## Packages

| Package | Description |
| --- | --- |
| [`hyperframes`](https://github.com/heygen-com/hyperframes/blob/main/packages/cli) | CLI — create, preview, lint, and render compositions |
| [`@hyperframes/core`](https://github.com/heygen-com/hyperframes/blob/main/packages/core) | Types, parsers, generators, linter, runtime, frame adapters |
| [`@hyperframes/engine`](https://github.com/heygen-com/hyperframes/blob/main/packages/engine) | Seekable page-to-video capture engine (Puppeteer + FFmpeg) |
| [`@hyperframes/producer`](https://github.com/heygen-com/hyperframes/blob/main/packages/producer) | Full rendering pipeline (capture + encode + audio mix) |
| [`@hyperframes/studio`](https://github.com/heygen-com/hyperframes/blob/main/packages/studio) | Browser-based composition editor UI |
| [`@hyperframes/player`](https://github.com/heygen-com/hyperframes/blob/main/packages/player) | Embeddable `<hyperframes-player>` web component |
| [`@hyperframes/shader-transitions`](https://github.com/heygen-com/hyperframes/blob/main/packages/shader-transitions) | WebGL shader transitions for compositions |

## Skills

HyperFrames ships [skills](https://github.com/vercel-labs/skills) that teach AI agents framework-specific patterns that generic docs don't cover.

```
npx skills add heygen-com/hyperframes
```

| Skill | What it teaches |
| --- | --- |
| `hyperframes` | HTML composition authoring, captions, TTS, audio-reactive animation, transitions |
| `hyperframes-cli` | CLI commands: init, lint, preview, render, transcribe, tts, doctor |
| `hyperframes-registry` | Block and component installation via `hyperframes add` |
| `gsap` | GSAP animation API, timelines, easing, ScrollTrigger, plugins, React/Vue/Svelte, performance |