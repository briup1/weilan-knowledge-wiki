---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/AIComicBuilder AI-powered animated comic generator.md
tags: [ai-comic, animated-comic, storyboard, video-generation, nextjs]
---

# AIComicBuilder: AI-Powered Animated Comic Generator

## 摘要

AIComicBuilder 是一款 AI 驱动的漫剧/动画生成器，实现从剧本到动画视频的全自动流水线。用户可上传 TXT/DOCX/PDF 剧本文件，AI 自动解析文本、提取角色、智能分集，然后依次完成角色四视图生成、智能分镜、首尾帧生成、视频提示词生成、视频生成和视频合成。项目基于 Next.js 16 + React 19 构建，使用 SQLite + Drizzle ORM 作为数据库，支持 OpenAI、Gemini、Kling、Seedance、Veo 等多家 AI 供应商。提供分镜编辑抽屉、角色内联面板、看板视图三种协作视图，支持单张分镜精细编辑和版本管理。支持多语言（中/英/日/韩）和多种视频比例（16:9/9:16/1:1）。

## 核心要点

- **完整生成流水线**：剧本输入 → 剧本解析 → 角色提取 → 角色四视图 → 智能分镜 → 首尾帧生成 → 视频提示词 → 视频生成 → 视频合成 + 字幕
- **角色一致性保障**：为每个角色生成四视图参考图（正面/四分之三/侧面/背面），确保后续帧画面一致性
- **智能分镜**：AI 将剧本拆解为专业镜头列表，含构图、灯光、运镜指令
- **首尾帧生成**：为每个镜头生成起始帧和结束帧，支持首尾帧插值生成动画
- **多模型支持**：AI 文本（OpenAI/Gemini）、AI 图像（DALL-E/Gemini Imagen/Kling）、AI 视频（Seedance/Kling/Veo）
- **技术栈**：Next.js 16 (App Router)、React 19、Tailwind CSS 4、Zustand、SQLite + Drizzle ORM、FFmpeg
- **协作视图**：分镜编辑抽屉、角色内联面板、看板视图（按生成进度自动分列）
- **风格自适应**：自动识别剧本风格（动漫/写实等），角色四视图与首尾帧匹配对应风格
- **部署方式**：Docker 一键部署、手动构建（pnpm）

## 原始文件

- [原始文件](../../raw/archive/AIComicBuilder AI-powered animated comic generator.md)
