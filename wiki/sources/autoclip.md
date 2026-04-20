---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/zhouxiaokaautoclip AutoClip  AI-powered video clipping and highlight generation · 一款智能高光提取与剪辑的二创工具.md
tags: [video-clipping, highlight-detection, ai-analysis, youtube, bilibili]
---

# AutoClip: AI-Powered Video Clipping and Highlight Generation

## 摘要

AutoClip 是一款基于 AI 的智能视频切片处理系统，能够自动从 YouTube、B 站等平台下载视频，通过 AI 分析提取精彩片段，并智能生成合集。系统采用前后端分离架构，后端基于 FastAPI + Celery + Redis + SQLite，前端基于 React 18 + TypeScript + Ant Design。核心功能包括多平台视频下载（YouTube/B 站/本地文件）、基于通义千问的 AI 内容分析、智能切片与精彩度评分、自动生成标题、智能合集推荐、实时进度推送（WebSocket）。提供一键启动脚本和 Docker 部署支持，并计划开发 B 站自动上传、字幕编辑、移动端支持等功能。

## 核心要点

- **多平台支持**：YouTube（yt-dlp）、B 站视频一键下载，支持本地文件上传
- **AI 智能分析**：基于通义千问大语言模型，自动提取视频大纲、识别话题时间点、对片段进行精彩度评分
- **自动切片流程**：素材准备 → 内容分析 → 时间线提取 → 精彩评分 → 标题生成 → 合集推荐 → 视频生成
- **实时处理**：异步任务队列（Celery），WebSocket 实时进度推送，支持错误处理和重试
- **技术栈**：后端 FastAPI + Celery + Redis + SQLite + yt-dlp + 通义千问；前端 React 18 + TypeScript + Ant Design + Vite + Zustand
- **部署方式**：Docker 一键启动（推荐）、本地一键启动脚本（start_autoclip.sh）、手动安装
- **开发中功能**：B 站上传（多账号管理）、字幕编辑（可视化编辑器）、移动端支持、多语言支持
- **性能优化建议**：生产环境使用 PostgreSQL 替代 SQLite、Redis 持久化、Celery 并发调优

## 原始文件

- [原始文件](../../raw/archive/zhouxiaokaautoclip AutoClip  AI-powered video clipping and highlight generation · 一款智能高光提取与剪辑的二创工具.md)
