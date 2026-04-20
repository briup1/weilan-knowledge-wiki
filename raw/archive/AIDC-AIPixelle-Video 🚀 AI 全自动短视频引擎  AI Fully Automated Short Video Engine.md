---
title: "AIDC-AI/Pixelle-Video: 🚀 AI 全自动短视频引擎 | AI Fully Automated Short Video Engine"
source: "https://github.com/AIDC-AI/Pixelle-Video"
author:
published:
created: 2026-04-18
description: "🚀 AI 全自动短视频引擎 | AI Fully Automated Short Video Engine - AIDC-AI/Pixelle-Video"
tags:
  - "clippings"
---
## 🎬 Pixelle-Video —— AI 全自动短视频引擎

[English](https://github.com/AIDC-AI/Pixelle-Video/blob/main/README_EN.md) | **中文**

Pixelle\_video.mp4<video src="https://private-user-images.githubusercontent.com/177295860/518523041-a42e7457-fcc8-40da-83fc-784c45a8b95d.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNzcyOTU4NjAvNTE4NTIzMDQxLWE0MmU3NDU3LWZjYzgtNDBkYS04M2ZjLTc4NGM0NWE4Yjk1ZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lM2VkYzBjMmFhOWI0NmYxYjUwNmM4MzI1MjZjNWRkYmU4Yzg5YjA0ZTZlZjc4MWRhMWMzMmFlY2M2M2IxN2YzJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.cYE0ARJ4ArrIJDIgGcApGEIdP2052MlyBmmDgOt8mZ4" controls="controls"></video>

只需输入一个 **主题** ，Pixelle-Video 就能自动完成：

- ✍️ 撰写视频文案
- 🎨 生成 AI 配图/视频
- 🗣️ 合成语音解说
- 🎵 添加背景音乐
- 🎬 一键合成视频

**零门槛，零剪辑经验** ，让视频创作成为一句话的事！

## 🖥️ Web 界面预览

[![Web UI界面](https://github.com/AIDC-AI/Pixelle-Video/raw/main/resources/webui.png)](https://github.com/AIDC-AI/Pixelle-Video/blob/main/resources/webui.png)

## 📋 最近更新

- ✅ **2026-01-26**: 新增「动作迁移」模块，上传参考视频和图片进行动作迁移
- ✅ **2026-01-14**: 新增「数字人口播」和「图生视频」流水线，新增多语言 TTS 音色支持
- ✅ **2026-01-06**: 新增 RunningHub 48G 显存机器调用支持
- ✅ **2025-12-28**: 支持 RunningHub 并发限制可配置，优化 LLM 返回结构化数据的逻辑
- ✅ **2025-12-17**: 支持 ComfyUI API Key 配置，支持 Nano Banana 模型调用，API 接口支持模板自定义参数
- ✅ **2025-12-10**: 侧边栏内置 FAQ，锁定 edge-tts 版本修复 TTS 服务不稳定问题
- ✅ **2025-12-08**: 支持固定脚本多种分割方式(段落/行/句子)，优化模板选择交互逻辑支持直接预览选择
- ✅ **2025-12-06**: 修复视频生成 API 返回 URL 路径处理，支持跨平台兼容
- ✅ **2025-12-05**: 新增 Windows 整合包下载，优化图片与视频反推工作流
- ✅ **2025-12-04**: 新增「自定义素材」功能，支持用户上传自己的照片和视频，AI 智能分析生成脚本
- ✅ **2025-11-18**: 优化 RunningHub 服务调用支持并行处理，新增历史记录页面，支持批量创建视频任务

## ✨ 功能亮点

- ✅ **全自动生成** - 输入主题，自动生成完整视频
- ✅ **AI 智能文案** - 根据主题智能创作解说词，无需自己写脚本
- ✅ **AI 生成配图** - 每句话都配上精美的 AI 插图
- ✅ **AI 生成视频** - 支持使用 AI 视频生成模型（如 WAN 2.1）创建动态视频内容
- ✅ **AI 生成语音** - 支持 Edge-TTS、Index-TTS 等众多主流 TTS 方案
- ✅ **背景音乐** - 支持添加 BGM，让视频更有氛围
- ✅ **视觉风格** - 多种模板可选，打造独特视频风格
- ✅ **灵活尺寸** - 支持竖屏、横屏等多种视频尺寸
- ✅ **多种 AI 模型** - 支持 GPT、通义千问、DeepSeek、Ollama 等
- ✅ **原子能力灵活组合** - 基于 ComfyUI 架构，可使用预置工作流，也可自定义任意能力（如替换生图模型为 FLUX、替换 TTS 为 ChatTTS 等）

## 📊 视频生成流程

Pixelle-Video 采用模块化设计，整个视频生成流程清晰简洁：

[![视频生成流程图](https://github.com/AIDC-AI/Pixelle-Video/raw/main/resources/flow.png)](https://github.com/AIDC-AI/Pixelle-Video/blob/main/resources/flow.png)

从输入文本到最终视频输出，整个流程简洁清晰： **文案生成 → 配图规划 → 逐帧处理 → 视频合成**

每个环节都支持灵活定制，可选择不同的 AI 模型、音频引擎、视觉风格等，满足个性化创作需求。

## 🎬 视频示例

以下是使用 Pixelle-Video 生成的实际案例，展示了不同主题和风格的视频效果：

### 📱 扩展模块视频展示

| ### 👤 数字人口播  video1.mp4<video src="https://private-user-images.githubusercontent.com/150135158/540442067-7c122563-c2e0-4dcd-a73c-25ba1d4fa2dd.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNTAxMzUxNTgvNTQwNDQyMDY3LTdjMTIyNTYzLWMyZTAtNGRjZC1hNzNjLTI1YmExZDRmYTJkZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yNDdhZThjZDY5NzNhZTYyMTQwYmE3MDJiMzMxYTU1NWU2OTQwMTE2YmMzMTE0OGU0ZGFhYjVjMmFmZjQ4NWNjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.PRL1ZbixhJfHeKM27QzCcnmi_HubKa2cHJ1JLLgKv6g" controls="controls"></video>  **韩语数字人口播** | ### 🖼️ 图生视频  video2.mp4<video src="https://private-user-images.githubusercontent.com/150135158/540459888-5b4eef17-07d0-4bde-9748-2ed68cc9888e.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNTAxMzUxNTgvNTQwNDU5ODg4LTViNGVlZjE3LTA3ZDAtNGJkZS05NzQ4LTJlZDY4Y2M5ODg4ZS5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0wNjM5Zjc0ZGFhNjljNWRmNjhhNGY1YzMwNzRhMjY5ZTQyYjViZTQ2ODQ2NmQ0ZjhmYzBjMWIyMTk3OTAzY2EwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.8UoSUp2nOxNfPfDyEmiszFl9-GmKHqw5IAfu7sEugTQ" controls="controls"></video>  **卡通视频** | ### 💃 动作迁移  video3.mp4<video src="https://private-user-images.githubusercontent.com/150135158/540441683-7b1240bc-e965-434c-b343-118ec4793d4f.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNTAxMzUxNTgvNTQwNDQxNjgzLTdiMTI0MGJjLWU5NjUtNDM0Yy1iMzQzLTExOGVjNDc5M2Q0Zi5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04Mzc1MjE5ODliYjYwMTU3MjM5MTc3ZTUzMmU3ZDFmNzkxZTZhY2Y4Njc2YmViZGExYWU4OTQwMmVmOTQ4MjI4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.D4WIpJ90SVqFpqmTV9MWGjbXY7Tn2azRWzBz4yEi3pQ" controls="controls"></video>  **跳舞小猫** |
| --- | --- | --- |

### 📱 竖屏视频展示

| ### 🌄 人文纪实类 - 视频默认模版  default1.mp4<video src="https://private-user-images.githubusercontent.com/177295860/520042501-e6716c1d-78de-453d-84c2-10873c8c595f.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNzcyOTU4NjAvNTIwMDQyNTAxLWU2NzE2YzFkLTc4ZGUtNDUzZC04NGMyLTEwODczYzhjNTk1Zi5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lM2RhZjQ3ODg0NmQ2YzdkODQ1YWM5NjRhNjA2MWJhNGY1YzllNTU4ODE5NzY0OTBmNmI5N2EzODQxNDMwYzNmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.UUlrZCKg17E_aIqJL-M8ivwKzPHrdzuaG8Xu6zsCax8" controls="controls"></video>  **旅行路上的风景让人流连忘返** | ### 🔍 文化解构类 - 视频默认模版  default2.mp4<video src="https://private-user-images.githubusercontent.com/177295860/520043080-f5de75f6-135a-4ab4-9f5f-079f649764d5.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNzcyOTU4NjAvNTIwMDQzMDgwLWY1ZGU3NWY2LTEzNWEtNGFiNC05ZjVmLTA3OWY2NDk3NjRkNS5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05Y2Q5N2NmMmIyMmU1ZmI2M2UxYjgyZDkzZDA3MmQxZDc5MDg4MDUxMTk3NGFmMTdhYjFjOGFjZGEzOWE1N2RjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.DAPfVLsW1MwVRXSWYthbCwXyOEPuPV0E1fIOq9QIZL0" controls="controls"></video>  **Santa ID** | ### 🔭 科学思辨类 - 视频默认模版  default3.mp4<video src="https://private-user-images.githubusercontent.com/177295860/520043399-ceb8b0df-8331-4e1f-88e7-db5b295a1c1d.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii8xNzcyOTU4NjAvNTIwMDQzMzk5LWNlYjhiMGRmLTgzMzEtNGUxZi04OGU3LWRiNWIyOTVhMWMxZC5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNDE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDQxOFQwMTUwNTBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zNGRmMjNkYzA5NjU3YzY4YmYwYTE4NDRkMTQyYWNlODg3YjRkZTY4N2FkMTJlZjc5NzQ0ZTExNDA4NzUwOTQyJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZtcDQifQ.agulfoDN5cw4NXBK72nSsXymuz_Pc6QPNaDxmfsx5ps" controls="controls"></video>  **为什么我们还没有找到外星文明？** |
| --- | --- | --- |
| ### 🌱 个人成长类 - 克隆音色  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511308153-1bad9a49-df83-4905-9cc8-9a7640e9c7d8.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMwODE1My0xYmFkOWE0OS1kZjgzLTQ5MDUtOWNjOC05YTc2NDBlOWM3ZDgubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NmM2Mzg4MGU2MTdjYjI4MGI5YWVkYTZlN2NjNzMwMzg2NzkwY2JkODVjMjE3Y2VmYmVhMDNjY2RiODg0YmE5YyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.4Nv-HiyPTGBc9D9xck1vAdQ7EycYRckXY4X4Ir_pWhA" controls="controls"></video>  **如何提升自己** | ### 🧠 深度思考类 - 默认模板  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511308151-663b705a-2aea-44bc-b266-4bb27aa255a8.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMwODE1MS02NjNiNzA1YS0yYWVhLTQ0YmMtYjI2Ni00YmIyN2FhMjU1YTgubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9YzQwOGZmODg0ZDVhMmViNGU0NzU1MzU4NTc1YTEyOWNjNzRjNGI5ZjBjNzFmYTU0MzcyYzZmMWMxZDAyZGY5YiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.1C8crsLOoTwSi1OTQAoxqh5_YWhwJFNGO14MurR0Xu4" controls="controls"></video>  **如何理解反脆弱** | ### 🏯 历史文化类 - 固定画面  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511308155-56e0a018-fa99-47eb-a97f-fc2fa8915724.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMwODE1NS01NmUwYTAxOC1mYTk5LTQ3ZWItYTk3Zi1mYzJmYTg5MTU3MjQubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MzdjOWE1MTc5NzNkYmQwYzUxM2M0YWQ2MWMyMjc0ODQwMmQ3ZWI0ZTg1ZjM2Njg1MGYxYzNmOWQzNjYyZWViZCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.j5KdkYSY-IYm8APNjnPzCJLVhk1CRRlXCwytq7FMYmE" controls="controls"></video>  **资治通鉴** |
| ### ☀️ 情感类 - 克隆音色  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511308150-4687df95-dd21-4a7b-b01e-f33a7b646644.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMwODE1MC00Njg3ZGY5NS1kZDIxLTRhN2ItYjAxZS1mMzNhN2I2NDY2NDQubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NmFhMzU3ODBmZWI4YTZjMjYxYzJkZmUwZmMwZDRhYmMzZWM1ZDAxZGRiN2RlYzk5MmMzODk1YTYwMmY2ZGY1MSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.qoJ3g9dfciaQ1BEAXEfJW7W05vVwMl2x_EAjHhpfVto" controls="controls"></video>  **冬日暖阳** | ### 📜 小说解说类 - 自创脚本  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511308149-d354465e-3fa8-40b4-93e9-61ad75ef0697.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMwODE0OS1kMzU0NDY1ZS0zZmE4LTQwYjQtOTNlOS02MWFkNzVlZjA2OTcubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9OGY4NmUyYTYyMjI2Zjk1MDFiMWJhMWEyMjkwNDRmOThlMzEzMmI3ZTU1NTcyYjMxMTg4MDliZGY5NDIwZjBmOSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.bV_3Ynlh3hcfSWiJ20aS94784F3cxGD-_3lMBHcI114" controls="controls"></video>  **斗破苍穹** | ### 🧬 知识科普类 - Qwen生图  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511308154-8ac21768-41ce-4d41-acdd-e3dd3eb9725a.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMwODE1NC04YWMyMTc2OC00MWNlLTRkNDEtYWNkZC1lM2RkM2ViOTcyNWEubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZDQzZGU2N2U1Njc2Y2NhM2ExMjBhMGMyYmIyZmNjYjYyOGFjNTgwZjJhNGFmOTM3ZTMyNTg2NmRhODhkMDkxNSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.LVKHA2anIzBIpE7M_M7KbTWWtwpBaL6W4nYgU7mQpbk" controls="controls"></video>  **养生知识** |

### 🖥️ 横屏视频展示

| ### 💰 副业赚钱 - 电影模板  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511320949-c9209d4e-73a6-4b82-aaad-cf102248c9e2.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMyMDk0OS1jOTIwOWQ0ZS03M2E2LTRiODItYWFhZC1jZjEwMjI0OGM5ZTIubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MzBkMDVlZGRmZmExMjVjNzE2MDk3NTgyYTNkODM3ZWFiMDBmNDM0ZDA0YTQ4OTU5OWI3NjQzYTFlMDQyNDAxOSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.pEprHVThaGNrfzCbwFwTtbzbeyflFGvOvFaYYaGH61U" controls="controls"></video>  **副业赚钱** | ### 🏛️ 历史解说 - 自定义模板  default.mp4<video src="https://private-user-images.githubusercontent.com/9640444/511320948-a767c452-d5f1-4cff-bb34-b80fff0d4c3e.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzY0NzczNTAsIm5iZiI6MTc3NjQ3NzA1MCwicGF0aCI6Ii85NjQwNDQ0LzUxMTMyMDk0OC1hNzY3YzQ1Mi1kNWYxLTRjZmYtYmIzNC1iODBmZmYwZDRjM2UubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDQxOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA0MThUMDE1MDUwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NDk3MTQ1ODRlNTRlYjE4ODFlNDFjNDAxNzAxMmVmNDRhN2U5MmRlNjNkZGZkNjBiODg4YmQ1MzRhMzk2MTM3YyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.moW8A0kco-mTNCz7wLB1EoZClW2b9SLpicTCqLjrTDA" controls="controls"></video>  **资治通鉴启示录** |
| --- | --- |

> 💡 **提示**: 这些视频都是通过输入一个主题关键词，由 AI 全自动生成的，无需任何视频剪辑经验！

## 🚀 快速开始

### 🪟 Windows 一键整合包（推荐 Windows 用户使用）

**无需安装 Python、uv 或 ffmpeg，一键开箱即用！**

👉 **[下载 Windows 一键整合包](https://github.com/AIDC-AI/Pixelle-Video/releases/latest)**

1. 下载最新的 Windows 一键整合包并解压
2. 双击运行 `start.bat` 启动 Web 界面
3. 浏览器会自动打开 [http://localhost:8501](http://localhost:8501/)
4. 在「⚙️ 系统配置」中配置 LLM API 和图像生成服务
5. 开始生成视频！

> 💡 **提示**: 整合包已包含所有依赖，无需手动安装任何环境。首次使用只需配置 API 密钥即可。

### 从源码安装（适合 macOS / Linux 用户或需要自定义的用户）

#### 前置环境依赖

在开始之前，需要先安装 Python 包管理器 `uv` 和视频处理工具 `ffmpeg` ：

##### 安装 uv

请访问 uv 官方文档查看适合你系统的安装方法：  
👉 **[uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)**

安装完成后，在终端中运行 `uv --version` 验证安装成功。

##### 安装 ffmpeg

**macOS**

```
brew install ffmpeg
```

**Ubuntu / Debian**

```
sudo apt update
sudo apt install ffmpeg
```

**Windows**

- 下载地址： [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- 下载后解压，将 `bin` 目录添加到系统环境变量 PATH 中

安装完成后，在终端中运行 `ffmpeg -version` 验证安装成功。

#### 第一步：下载项目

```
git clone https://github.com/AIDC-AI/Pixelle-Video.git
cd Pixelle-Video
```

#### 第二步：启动 Web 界面

```
# 使用 uv 运行（推荐，会自动安装依赖）
uv run streamlit run web/app.py
```

浏览器会自动打开 [http://localhost:8501](http://localhost:8501/)

#### 第三步：在 Web 界面配置

首次使用时，展开「⚙️ 系统配置」面板，填写：

- **LLM 配置**: 选择 AI 模型（如通义千问、GPT 等）并填入 API Key
- **图像配置**: 如需生成图片，配置 ComfyUI 地址或 RunningHub API Key

配置好后点击「保存配置」，就可以开始生成视频了！

## 💻 使用方法

打开 Web 界面后，你会看到三栏布局，下面详细讲解每个部分：

### ⚙️ 系统配置（首次必填）

首次使用时需要配置，点击展开「⚙️ 系统配置」面板：

#### 1\. LLM 配置（大语言模型）

用于生成视频文案的 AI。

**快速选择预设**

- 通过下拉菜单选择预设模型（通义千问、GPT-4o、DeepSeek 等）
- 选择后会自动填充 base\_url 和 model
- 点击「🔑 获取 API Key」链接去注册并获取密钥

**手动配置**

- API Key: 填入你的密钥
- Base URL: API 地址
- Model: 模型名称

#### 2\. 图像配置

用于生成视频配图的 AI。

**本地部署（推荐）**

- ComfyUI URL: 本地 ComfyUI 服务地址（默认 [http://127.0.0.1:8188）](http://127.0.0.1:8188%EF%BC%89)
- 点击「测试连接」确认服务可用

**云端部署**

- RunningHub API Key: 云端图像生成服务的密钥

配置完成后点击「保存配置」。

### 📝 内容输入（左侧栏）

#### 生成模式

- **AI 生成内容**: 输入主题，AI 自动创作文案
	- 适合：想快速生成视频，让 AI 写稿
		- 例如：「为什么要养成阅读习惯」
- **固定文案内容**: 直接输入完整文案，跳过 AI 创作
	- 适合：已有现成文案，直接生成视频

#### 背景音乐（BGM）

- **无 BGM**: 纯人声解说
- **内置音乐**: 选择预置的背景音乐（如 default.mp3）
- **自定义音乐**: 将你的音乐文件（MP3/WAV 等）放到 `bgm/` 文件夹
- 点击「试听 BGM」可以预览音乐

### 🎤 语音设置（中间栏）

#### TTS 工作流

- 从下拉菜单选择 TTS 工作流（支持 Edge-TTS、Index-TTS 等）
- 系统会自动扫描 `workflows/` 文件夹中的 TTS 工作流
- 如果懂 ComfyUI，可以自定义 TTS 工作流

#### 参考音频（可选）

- 上传参考音频文件用于声音克隆（支持 MP3/WAV/FLAC 等格式）
- 适用于支持声音克隆的 TTS 工作流（如 Index-TTS）
- 上传后可以直接试听

#### 预览功能

- 输入测试文本，点击「预览语音」即可试听效果
- 支持使用参考音频进行预览

### 🎨 视觉设置（中间栏）

#### 图像生成

决定 AI 生成什么风格的配图。

**ComfyUI 工作流**

- 从下拉菜单选择图像生成工作流
- 支持本地部署（selfhost）和云端（RunningHub）工作流
- 默认使用 `image_flux.json`
- 如果懂 ComfyUI，可以放自己的工作流到 `workflows/` 文件夹

**图像尺寸**

- 设置生成图像的宽度和高度（单位：像素）
- 默认 1024x1024，可根据需要调整
- 注意：不同的模型对尺寸有不同的限制

**提示词前缀（Prompt Prefix）**

- 控制图像的整体风格（语言需要是英文的）
- 例如：Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style
- 点击「预览风格」可以测试效果

#### 视频模板

决定视频画面的布局和设计。

**模板命名规范**

- `static_*.html`: 静态模板（无需AI生成媒体，纯文字样式）
- `image_*.html`: 图片模板（使用AI生成的图片作为背景）
- `video_*.html`: 视频模板（使用AI生成的视频作为背景）

**使用方法**

- 从下拉菜单选择模板，按尺寸分组显示（竖屏/横屏/方形）
- 点击「预览模板」可以自定义参数测试效果
- 如果懂 HTML，可以在 `templates/` 文件夹创建自己的模板
- 🔗 [查看所有模板效果图](https://aidc-ai.github.io/Pixelle-Video/zh/user-guide/templates/#_3)

### 🎬 生成视频（右侧栏）

#### 生成按钮

- 配置好所有参数后，点击「🎬 生成视频」
- 会显示实时进度（生成文案 → 生成配图 → 合成语音 → 合成视频）
- 生成完成后自动显示视频预览

#### 进度显示

- 实时显示当前步骤
- 例如：「分镜 3/5 - 生成插图」

#### 视频预览

- 生成完成后自动播放
- 显示视频时长、文件大小、分镜数等信息
- 视频文件保存在 `output/` 文件夹

### ❓ 常见问题

**Q: 第一次使用需要多久？**  
A: 生成时长取决于视频分镜数量、网络状况和 AI 推理速度，通常几分钟内即可完成。

**Q: 视频效果不满意怎么办？**  
A: 可以尝试：

1. 更换 LLM 模型（不同模型文案风格不同）
2. 调整图像尺寸和提示词前缀（改变配图风格）
3. 更换 TTS 工作流或上传参考音频（改变语音效果）
4. 尝试不同的视频模板和尺寸

**Q: 费用大概多少？**  
A: **本项目完全支持免费运行！**

- **完全免费方案**: LLM 使用 Ollama（本地运行）+ ComfyUI 本地部署 = 0 元
- **推荐方案**: LLM 使用通义千问（成本极低，性价比高）+ ComfyUI 本地部署
- **云端方案**: LLM 使用 OpenAI + 图像使用 RunningHub（费用较高但无需本地环境）

**选择建议** ：本地有显卡建议完全免费方案，否则推荐使用通义千问（性价比高）

## 🤝 参考项目

Pixelle-Video 的设计受到以下优秀开源项目的启发：

- [Pixelle-MCP](https://github.com/AIDC-AI/Pixelle-MCP) - ComfyUI MCP 服务器，让 AI 助手直接调用 ComfyUI
- [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) - 优秀的视频生成工具
- [NarratoAI](https://github.com/linyqh/NarratoAI) - 影视解说自动化工具
- [MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus) - 视频创作平台
- [ComfyKit](https://github.com/puke3615/ComfyKit) - ComfyUI 工作流封装库

感谢这些项目的开源精神！🙏

## 💬 社区交流

扫描下方二维码加入我们的社区，获取最新动态和技术支持：

| 微信群 | Discord 社区 |
| --- | --- |
| [![微信交流群](https://github.com/AIDC-AI/Pixelle-Video/raw/main/resources/wechat.png)](https://github.com/AIDC-AI/Pixelle-Video/blob/main/resources/wechat.png) | [![Discord 社区](https://github.com/AIDC-AI/Pixelle-Video/raw/main/resources/discord.png)](https://github.com/AIDC-AI/Pixelle-Video/blob/main/resources/discord.png) |

## 📢 反馈与支持

- 🐛 **遇到问题**: 提交 [Issue](https://github.com/AIDC-AI/Pixelle-Video/issues)
- 💡 **功能建议**: 提交 [Feature Request](https://github.com/AIDC-AI/Pixelle-Video/issues)
- ⭐ **给个 Star**: 如果这个项目对你有帮助，欢迎给个 Star 支持一下！

## 📝 许可证

本项目采用 Apache 2.0 许可证，详情请查看 [LICENSE](https://github.com/AIDC-AI/Pixelle-Video/blob/main/LICENSE) 文件。

[![Star History Chart](https://camo.githubusercontent.com/9341c4599c9669a3bb3a92d91a1b4fd7b10a3b5d65796d28a016c7e2374e70f3/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f7376673f7265706f733d414944432d41492f506978656c6c652d566964656f26747970653d44617465)](https://star-history.com/#AIDC-AI/Pixelle-Video&Date)