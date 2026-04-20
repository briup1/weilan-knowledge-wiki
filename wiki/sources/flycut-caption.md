---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/x007xyzflycut-caption A complete video subtitle editing React component with AI-powered speech recognition and visual editing capabilities.md
tags: [subtitle-editing, react-component, whisper, asr, video-editing]
---

# FlyCut Caption: AI-Powered Video Subtitle Editing React Component

## 摘要

FlyCut Caption 是一个功能完整的 AI 驱动视频字幕编辑 React 组件，专注于智能字幕生成、编辑和视频剪辑。它基于 Whisper 模型实现高精度语音识别（支持多语言），提供直观的字幕分段选择和删除界面，视频播放器与字幕实时同步，支持区间播放。组件采用 React 19 + TypeScript + Vite + Tailwind CSS 技术栈，使用 Hugging Face Transformers.js 在浏览器本地运行 AI 模型，ASR 处理通过 Web Workers 在后台线程运行不阻塞主界面。支持 SRT/JSON 字幕格式导出和视频文件导出（含字幕烧录），并提供组件化国际化设计，支持中文、英文和自定义语言包。

## 核心要点

- **本地 AI 语音识别**：基于 Whisper 模型，使用 Hugging Face Transformers.js 在浏览器本地运行，无需后端
- **可视化字幕编辑**：直观的字幕分段选择、批量删除、撤销/重做、实时视频同步预览
- **Web Workers 处理**：ASR 运行在后台线程，不阻塞主界面交互
- **字幕样式自定义**：字体、颜色、位置、背景、透明度、边框等 WYSIWYG 调整
- **视频处理**：基于 WebAV 的本地视频处理，支持区间剪辑合并、字幕烧录、多格式/质量输出
- **组件化国际化**：支持内置语言包（zhCN、enUS）和自定义语言包，组件内外语言状态同步
- **技术栈**：React 19、TypeScript 5.8、Vite 7.1、Tailwind CSS 4.1、Shadcn/ui、Zustand、WebAV
- **组件化设计**：可作为 npm 包（`@flycut/caption-react`）嵌入第三方应用，提供丰富的配置选项和事件回调
- **浏览器支持**：Chrome 88+、Firefox 78+、Safari 14+、Edge 88+

## 原始文件

- [原始文件](../../raw/archive/x007xyzflycut-caption A complete video subtitle editing React component with AI-powered speech recognition and visual editing capabilities.md)
