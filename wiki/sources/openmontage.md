---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/OpenMontage.agentsskillselevenlabs at main.md
tags: [agentic-video, open-source, video-production, remotion, multi-pipeline]
---

# OpenMontage: The First Open-Source Agentic Video Production System

## 摘要

OpenMontage 是全球首个开源的 Agentic 视频制作系统，包含 12 条生产流水线、52 个生产工具和 400+ Agent 技能。它将 AI 编程助手转变为完整的视频制作工作室——用户用自然语言描述需求，Agent 自动完成研究、脚本、素材生成、编辑和最终合成。OpenMontage 的独特之处在于：不仅能做基于图片的视频，还能通过免费/开源工作流制作真正的"视频视频"——Agent 从免费素材库和开放档案中构建语料库，检索实际运动片段，剪辑成时间线并渲染成品。系统采用 Agent-first 架构，AI 编程助手本身就是编排器，通过 YAML 流水线清单和 Markdown 技能文件来指导生产流程。支持 14 个视频生成提供商、10 个图像生成工具、4 个 TTS 提供商，以及完整的后期制作工具链。

## 核心要点

- **12 条生产流水线**：Animated Explainer、Animation、Avatar Spokesperson、Cinematic、Clip Factory、Documentary Montage、Hybrid、Localization & Dub、Podcast Repurpose、Screen Demo、Talking Head
- **52 个生产工具**：涵盖视频生成、图像创建、TTS、音乐、音频混合、字幕、增强和分析
- **400+ Agent 技能**：生产技能、流水线导演、创意技巧、质量检查清单、深度技术知识包
- **Agent-first 架构**：AI 编程助手（Claude Code、Cursor、Copilot 等）是编排器，无代码编排层
- **三层知识架构**：Layer 1（tools + pipeline_defs，"有什么"）、Layer 2（skills，"怎么用"）、Layer 3（.agents/skills，"原理是什么"）
- **参考视频驱动**：粘贴喜欢的视频，Agent 分析其节奏、结构、风格，生成差异化制作方案
- **真实素材纪录片模式**：从 Archive.org、NASA、Wikimedia Commons 等免费来源构建 CLIP 可搜索语料库，剪辑真实运动 footage
- **零 API Key 可用**：Piper TTS（离线 narration）、Archive.org/NASA/Wikimedia（免费素材）、Remotion（动画合成）、FFmpeg（后期）
- **生产治理**：预合成验证、渲染后自审（ffprobe + 帧提取 + 音频分析）、幻灯片风险评分、7 维度提供商选择评分、决策审计追踪、预算控制
- **多平台输出配置**：YouTube、Shorts、Reels、TikTok、LinkedIn、Cinematic 等预设分辨率和比例
- **许可证**：GNU AGPLv3

## 原始文件

- [原始文件](../../raw/archive/OpenMontage.agentsskillselevenlabs at main.md)
