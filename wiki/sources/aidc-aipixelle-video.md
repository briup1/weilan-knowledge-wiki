---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/AIDC-AIPixelle-Video 🚀 AI 全自动短视频引擎  AI Fully Automated Short Video Engine.md
tags: [ai-video, short-video, automated-video, tts, pixelle-video]
---

# AIDC-AI Pixelle-Video: AI 全自动短视频引擎

## 摘要

Pixelle-Video 是由 AIDC-AI 团队开发的开源 AI 全自动短视频生成引擎。用户只需输入一个主题，系统即可自动完成文案撰写、AI 配图/视频生成、语音解说合成、背景音乐添加和视频一键合成。项目基于 ComfyUI 架构，支持原子能力灵活组合，可替换生图模型（如 FLUX）、TTS 引擎（如 ChatTTS）等。提供 Web UI（Streamlit）和 Windows 一键整合包，零门槛使用。支持多种 AI 大模型（GPT、通义千问、DeepSeek、Ollama 等）和多种视频尺寸（竖屏/横屏），并扩展了数字人口播、图生视频、动作迁移等高级模块。

## 核心要点

- **全自动视频生成流程**：输入主题 → AI 文案生成 → 配图规划 → 逐帧处理 → 视频合成，全流程自动化
- **模块化 ComfyUI 架构**：基于 ComfyUI，原子能力可灵活组合，支持替换生图模型、TTS 工作流等
- **多模型支持**：LLM 支持 GPT、通义千问、DeepSeek、Ollama 等；图像生成支持 ComfyUI 本地部署和 RunningHub 云端
- **多种 TTS 方案**：Edge-TTS、Index-TTS 等，支持声音克隆（上传参考音频）
- **扩展模块**：数字人口播、图生视频（WAN 2.1）、动作迁移（上传参考视频+图片）
- **视觉模板系统**：支持 static（纯文字）、image（AI 图片背景）、video（AI 视频背景）三种模板类型
- **零成本运行方案**：LLM 使用 Ollama 本地运行 + ComfyUI 本地部署 = 完全免费
- **部署方式**：Windows 一键整合包（开箱即用）、源码安装（uv + ffmpeg）、Docker

## 原始文件

- [原始文件](../../raw/archive/AIDC-AIPixelle-Video 🚀 AI 全自动短视频引擎  AI Fully Automated Short Video Engine.md)
