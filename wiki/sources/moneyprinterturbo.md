---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/harry0703MoneyPrinterTurbo 利用AI大模型，一键生成高清短视频 Generate short videos with one click using AI LLM.md
tags: [ai-video, short-video, automated-video, moneyprinterturbo, tts]
---

# MoneyPrinterTurbo: 利用 AI 大模型一键生成高清短视频

## 摘要

MoneyPrinterTurbo 是一款开源的 AI 全自动短视频生成工具，在中文生态中具有较高知名度。用户只需提供视频主题或关键词，即可全自动生成视频文案、视频素材、字幕和背景音乐，合成高清短视频。项目采用完整的 MVC 架构，同时提供 Web 界面（Streamlit）和 API 接口。支持多种高清视频尺寸、批量生成、中英文文案、多种语音合成（含 Azure 真实语音）、字幕生成与样式调整、背景音乐配置等功能。视频素材来源为高清无版权素材（Pexels），也支持本地素材。支持接入 OpenAI、Moonshot、Azure、DeepSeek、通义千问、Google Gemini、Ollama 等十余种大模型。

## 核心要点

- **一键生成**：输入主题/关键词 → AI 生成文案 → 自动获取素材 → 合成字幕 → 添加 BGM → 输出高清视频
- **双界面支持**：Web UI（Streamlit）+ REST API，满足不同使用场景
- **批量生成**：一次生成多个视频，选择最满意的，提升产出效率
- **多模型接入**：OpenAI、Moonshot、Azure、DeepSeek、通义千问、Google Gemini、Ollama、MiniMax 等
- **字幕生成**：支持 edge（速度快）和 whisper（质量可靠）两种模式，可调整字体、位置、颜色、大小、描边
- **语音合成**：多种语音可选，支持实时试听；v1.1.2 新增 9 种 Azure 真实语音
- **素材来源**：Pexels 高清无版权视频 + 本地自定义素材
- **部署方式**：Windows 一键启动包、Docker、手动部署（uv/pip）
- **衍生服务**：录咖（reccloud.cn/com）基于该项目提供免费的在线 AI 视频生成器

## 原始文件

- [原始文件](../../raw/archive/harry0703MoneyPrinterTurbo 利用AI大模型，一键生成高清短视频 Generate short videos with one click using AI LLM.md)
