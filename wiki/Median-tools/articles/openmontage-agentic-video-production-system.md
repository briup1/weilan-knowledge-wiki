---
title: "OpenMontage：开源 Agentic 视频生产系统"
source: "https://github.com/calesthio/OpenMontage"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "AICoding", "type/tool", "type/hands-on", "OpenMontage", "Video-Production", "Remotion", "Agent", "Open-Source"]
status: "archived"
references: "Archive/OpenMontage.agentsskillselevenlabs at main.md"
---

> OpenMontage 是全球首个开源的 agentic 视频生产系统。12 条流水线、52 个工具、500+ agent 技能——将你的 AI 编程助手变成完整的视频制作工作室。

## 核心定位

与大多数"将静态图片拼接成视频"的工具不同，OpenMontage 支持两种真正的视频制作路径：

- **Image-based video**：AI 生成图像 + Remotion 动画引擎合成
- **Real-footage video**：从免费开源素材库（Archive.org、NASA、Wikimedia Commons）检索真实动态 footage，智能剪辑成时间线

**关键区别**：OpenMontage 能制作真正的"视频视频"，而不仅仅是"把静态图动起来"。

## 12 条生产流水线

| 流水线 | 产出类型 | 最佳适用 |
| --- | --- | --- |
| **Animated Explainer** | AI 生成讲解视频 | 教育内容、教程、主题拆解 |
| **Animation** | 动态图形、运动排版 | 社交媒体、产品演示 |
| **Avatar Spokesperson** | 虚拟人讲解视频 | 企业沟通、培训 |
| **Cinematic** | 预告片、氛围驱动剪辑 | 品牌影片、宣传内容 |
| **Clip Factory** | 批量短视频片段 | 长内容 repurposing |
| **Documentary Montage** | 主题蒙太奇（真实 footage） | 视频散文、纪实内容 |
| **Hybrid** | 源 footage + AI 辅助视觉 | 增强现有 footage |
| **Localization & Dub** | 字幕、配音、翻译 | 多语言分发 |
| **Podcast Repurpose** | 播客高光转视频 | 播客营销 |
| **Screen Demo** | 软件录屏演示 | 产品演示、文档 |
| **Talking Head** | 主讲人视频 | 演讲、vlog、访谈 |

每条流水线遵循统一结构：

```
research → proposal → script → scene_plan → assets → edit → compose
```

## 零 API Key 也能制作视频

Out of the box，`make setup` 即提供以下免费能力：

| 能力 | 免费工具 | 说明 |
| --- | --- | --- |
| 旁白 | Piper TTS | 离线文本转语音，真人感 narration |
| 开放素材 | Archive.org + NASA + Wikimedia | 免费/开源档案 footage |
| 额外素材 | Pexels + Unsplash + Pixabay | 免费 stock footage（开发者 key 免费申请） |
| 合成 | Remotion | React 程序化视频：弹簧动画、转场、字幕 |
| 后期 | FFmpeg | 编码、字幕烧录、音频混音、调色 |
| 字幕 | 内置 | 自动生成字级时间轴字幕 |

## 支持的 Provider（可选扩展）

**视频生成（14 个）**：Kling、Runway Gen-4、Google Veo 3、Grok Imagine Video、Higgsfield、MiniMax、HeyGen、WAN 2.1（本地）、Hunyuan（本地）、CogVideo（本地）、LTX-Video（本地）、Pexels、Pixabay、Wikimedia Commons

**图像生成（10 个）**：FLUX、Google Imagen、Grok Imagine、DALL-E 3、Recraft、Local Diffusion、Pexels、Pixabay、Unsplash、ManimCE

**语音（4 个）**：ElevenLabs、Google TTS（700+ 声音）、OpenAI TTS、Piper（本地免费）

**音乐**：Suno AI、ElevenLabs Music、ElevenLabs SFX

## 快速开始

### 前置要求

- Python 3.10+
- FFmpeg
- Node.js 18+
- AI 编程助手（Claude Code、Cursor、Copilot、Windsurf、Codex）

### 安装

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
```

### 制作视频

打开项目，告诉 AI 助手你想要什么：

```
"Make a 60-second animated explainer about how neural networks learn"
```

或真实 footage 路径：

```
"Make a 75-second documentary montage about city life in the rain. Use real footage only, no narration, elegiac tone, with music."
```

## Agent-First 架构

OpenMontage 采用** agent 优先架构**——没有代码编排器，AI 编程助手本身就是编排器。

```
用户请求
  → Agent 读取流水线 manifest（YAML）
  → Agent 读取阶段导演 skill（Markdown）
  → Agent 调用 Python 工具（7 维度评分选择 provider）
  → Agent 自审（schema 验证、质量检查）
  → Agent checkpoint 状态（JSON，可恢复）
  → 用户确认
  → 预合成验证门（交付承诺检查）
  → 渲染（Remotion 或 FFmpeg）
  → 渲染后自审（ffprobe + 帧提取 + 音频分析）
  → 最终视频输出
```

## 质量治理

- **预合成验证**：阻止违反交付承诺的渲染（如"motion-led"视频含 80% 静态图）
- **PPT 风险评分**：6 维度分析防止"动画 PowerPoint"输出
- **Provider 评分选择**：7 维度评分（任务适配 30%、输出质量 20%、控制性 15%、可靠性 15%、成本效率 10%、延迟 5%、连续性 5%）
- **决策审计追踪**：每个创意和技术选择都记录备选方案、置信度、推理过程
- **预算管控**：执行前估算、预算预留、事后核对；支持 `observe` / `warn` / `cap` 三种模式

## 平台适配

| 平台 | 配置文件 |
| --- | --- |
| Claude Code | `CLAUDE.md` |
| Cursor | `CURSOR.md` + `.cursor/rules/` |
| GitHub Copilot | `COPILOT.md` + `.github/copilot-instructions.md` |
| Codex | `CODEX.md` |
| Windsurf | `.windsurfrules` |

---

## 来源与归档

- 原始素材：[Archive/OpenMontage.agentsskillselevenlabs at main.md](../../../Archive/OpenMontage.agentsskillselevenlabs%20at%20main.md)
