---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [moneyprinterturbo]
tags: [ai-video, short-video, automated-video, tts, open-source]
---

# MoneyPrinterTurbo

MoneyPrinterTurbo 是一款开源的 AI 全自动短视频生成工具，用户只需提供视频主题或关键词，即可一键生成包含文案、素材、字幕和背景音乐的高清短视频。

## 核心组件与特性

- **LLM 驱动文案生成**：接入 OpenAI、Moonshot、Azure、DeepSeek、通义千问、Google Gemini、Ollama 等十余种大模型，根据主题自动生成视频文案。
- **自动素材获取**：从 Pexels 自动获取高清无版权视频素材，同时支持本地自定义素材上传。
- **语音合成（TTS）**：多种语音可选并支持实时试听，v1.1.2 版本新增 9 种 Azure 真实语音，让解说更自然。
- **字幕生成与样式调整**：支持 edge（速度快）和 whisper（质量可靠）两种字幕模式，可调整字体、位置、颜色、大小和描边。
- **视频合成**：自动将文案、素材、语音和背景音乐合成为完整高清视频，支持多种视频尺寸。
- **批量生成**：一次可生成多个视频版本，供用户挑选最满意的结果，显著提升产出效率。

## 使用指南与最佳实践

- **双界面使用**：项目同时提供 Web UI（Streamlit）和 REST API，既适合非技术用户通过浏览器操作，也方便开发者集成到自动化工作流中。
- **部署方式灵活**：支持 Windows 一键启动包（开箱即用）、Docker 容器化部署、以及手动部署（uv/pip）。
- **模型选择建议**：追求效果优先可选 Azure/OpenAI；追求成本优先可选 Ollama 本地运行；中文场景可选 DeepSeek 或通义千问。
- **素材补充策略**：Pexels 素材库覆盖通用场景，对于垂直领域内容建议提前准备本地素材库。

## 相关来源

- [[moneyprinterturbo]]
