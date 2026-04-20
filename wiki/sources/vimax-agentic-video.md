---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/HKUDSViMax ViMax Agentic Video Generation (Director, Screenwriter, Producer, and Video Generator All-in-One).md
tags: [agentic-video, ai-video, multi-agent, video-generation, vimax]
---

# ViMax: Agentic Video Generation (Director, Screenwriter, Producer, and Video Generator All-in-One)

## 摘要

ViMax 是由香港大学（HKUDS）开发的多智能体视频生成框架，将导演、编剧、制片人和视频生成器融为一体。它旨在解决当前 AI 视频生成的三大局限：仅能生成长度有限的短视频、角色和场景一致性差、缺乏脚本/音频/叙事结构。ViMax 通过多智能体协作，实现从原始创意到完整视频的端到端自动化生产，支持 Idea2Video（创意转视频）、Novel2Video（小说转视频）、Script2Video（剧本转视频）和 AutoCameo（照片生成客串视频）四种核心模式。系统采用 RAG 驱动的长脚本设计引擎、镜头级故事板设计、多机位拍摄模拟、智能参考图选择和一致性校验等关键技术。

## 核心要点

- **四大核心模式**：Idea2Video（创意→视频）、Novel2Video（完整小说→分集视频）、Script2Video（任意剧本→视频）、AutoCameo（上传照片→客串视频）
- **多智能体视频生成流水线**：输入层 → 中央编排（Agent 调度/资源管理） → 脚本理解 + 场景/镜头规划 → 视觉资产规划 → 资产索引 + 一致性/连续性校验 → 视觉合成与组装 → 输出层
- **关键技术能力**：RAG 长脚本生成引擎、镜头级故事板设计、多机位拍摄模拟、智能参考图选择、自动化图像生成、MLLM/VLM 一致性校验、高效并行镜头生成
- **音视频绑定**：同步整合角色语音和音效，创造沉浸式体验
- **支持模型**：Google Gemini、MiniMax（M2.7 1M 上下文/M2.5 204K 上下文）、图像/视频生成模型可配置
- **部署方式**：基于 uv 环境管理，支持 Linux 和 Windows
- **解决的核心痛点**：参考图获取与对齐、一致性校验、脚本生成、故事板设计、镜头设计、长视频跨场景连续性

## 原始文件

- [原始文件](../../raw/archive/HKUDSViMax ViMax Agentic Video Generation (Director, Screenwriter, Producer, and Video Generator All-in-One).md)
