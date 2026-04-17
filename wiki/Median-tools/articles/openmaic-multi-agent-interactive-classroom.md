---
title: "OpenMAIC：开源多智能体互动课堂平台"
source: "https://github.com/THU-MAIC/OpenMAIC"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "AICoding", "type/tool", "OpenMAIC", "Multi-Agent", "LangGraph", "Education", "Next.js", "Open-Source"]
status: "archived"
references: "Archive/THU-MAICOpenMAIC OpenMAIC Open Multi-Agent Interactive Classroom — Get an immersive, multi-agent learning experience in just one click.md"
---

> OpenMAIC（Open Multi-Agent Interactive Classroom）是清华大学 MAIC 团队开源的 AI 互动课堂平台，能够将任何主题或文档转化为丰富的互动学习体验。

## 核心亮点

- **一键生成课堂**：描述主题或附上学习材料，AI 几分钟内构建完整课堂
- **多智能体课堂**：AI 老师和智能体同学实时授课、讨论、互动
- **丰富的场景类型**：幻灯片、测验、交互式模拟实验、项目制学习（PBL）
- **白板 & 语音**：智能体实时绘制图表、书写公式、语音讲解
- **灵活导出**：可编辑的 `.pptx` 幻灯片或交互式 `.html` 网页
- **OpenClaw 集成**：通过 AI 助手在飞书、Slack、Telegram 等 20+ 聊天应用中直接生成课堂

## 课堂组件

| 组件 | 说明 |
| --- | --- |
| **幻灯片（Slides）** | AI 老师配合聚光灯和激光笔动作进行语音讲解——如同真实课堂 |
| **测验（Quiz）** | 交互式测验（单选/多选/简答），AI 实时判分和反馈 |
| **交互式模拟（Interactive）** | 基于 HTML 的交互实验：物理模拟器、流程图等 |
| **项目制学习（PBL）** | 选择角色，与 AI 智能体协作完成结构化项目 |

## 多智能体互动

- **课堂讨论**：智能体主动发起话题，可随时加入或被点名互动
- **圆桌辩论**：多个不同人设智能体围绕话题展开讨论
- **自由问答**：随时提问，AI 老师通过幻灯片、图表或白板解答
- **白板**：AI 在共享白板上实时绘图——推导方程、绘制流程图

## 快速开始

### 环境要求

- Node.js >= 20
- pnpm >= 10

### 安装与启动

```bash
git clone https://github.com/THU-MAIC/OpenMAIC.git
cd OpenMAIC
pnpm install
cp .env.example .env.local
# 填入至少一个 LLM API Key
pnpm dev
```

打开 [http://localhost:3000](http://localhost:3000) 开始学习。

### 生产部署

```bash
# Vercel
# Fork 仓库 → 导入 Vercel → 配置环境变量 → 部署

# Docker
cp .env.example .env.local
# 编辑 .env.local 填入 API Key
docker compose up --build
```

### 支持的服务商

OpenAI、Anthropic、Google Gemini、DeepSeek、MiniMax、Grok (xAI)、豆包、Ollama（本地），以及任何兼容 OpenAI API 的服务。

**推荐模型**：Gemini 3 Flash（效果与速度最佳平衡）。

## 两阶段生成流水线

| 阶段 | 说明 |
| --- | --- |
| **大纲生成** | AI 分析输入，生成结构化课堂大纲 |
| **场景生成** | 每个大纲条目生成为丰富场景——幻灯片、测验、交互模块或 PBL 活动 |

## 核心架构

```
OpenMAIC/
├── app/                        # Next.js App Router
│   ├── api/                    # 服务端 API 路由（约 18 个端点）
│   │   ├── generate/           # 场景生成流水线
│   │   ├── generate-classroom/ # 异步课堂生成提交与轮询
│   │   ├── chat/               # 多智能体讨论（SSE 流式传输）
│   │   └── ...
│   ├── classroom/[id]/         # 课堂回放页面
│   └── page.tsx                # 首页
├── lib/
│   ├── generation/             # 两阶段课堂生成流水线
│   ├── orchestration/          # LangGraph 多智能体编排（导演图）
│   ├── playback/               # 回放状态机（idle → playing → live）
│   ├── action/                 # 动作执行引擎（28+ 种动作类型）
│   ├── ai/                     # LLM 服务商抽象层
│   ├── audio/                  # TTS & ASR 服务商
│   ├── media/                  # 图片 & 视频生成服务商
│   └── export/                 # PPTX & HTML 导出
├── components/                 # React UI 组件
│   ├── slide-renderer/         # 基于 Canvas 的幻灯片编辑器
│   ├── scene-renderers/        # 测验、交互、PBL 场景渲染器
│   ├── chat/                   # 聊天区域和会话管理
│   ├── whiteboard/             # 基于 SVG 的白板绘图
│   └── agent/                  # 智能体头像、配置、信息栏
├── packages/
│   ├── pptxgenjs/              # 定制化 PowerPoint 生成
│   └── mathml2omml/            # MathML → Office Math 转换
└── skills/openmaic/            # OpenClaw / ClawHub Skill
```

### 核心模块

- **生成流水线** (`lib/generation/`)：两阶段——大纲生成 → 场景内容生成
- **多智能体编排** (`lib/orchestration/`)：基于 LangGraph 的状态机，管理智能体轮次和讨论
- **回放引擎** (`lib/playback/`)：驱动课堂回放和实时互动的状态机
- **动作引擎** (`lib/action/`)：执行 28+ 种动作类型（语音、白板绘图/文字/形状/图表、聚光灯、激光笔等）

## OpenClaw 集成

通过 OpenClaw，可在飞书、Slack、Discord、Telegram 等 20+ 聊天应用中直接生成课堂。

```bash
clawhub install openmaic
```

支持两种模式：
- **托管模式**：在 [open.maic.chat](https://open.maic.chat/) 获取访问码，无需本地部署
- **本地部署模式**：Skill 引导完成 clone、配置和启动

## 导出格式

| 格式 | 说明 |
| --- | --- |
| **PowerPoint (.pptx)** | 可编辑幻灯片，含图片、图表和 LaTeX 公式 |
| **交互式 HTML** | 自包含网页，含交互式模拟实验 |
| **课堂 ZIP** | 完整课堂导出（课程结构 + 媒体文件），可备份或分享 |

---

## 来源与归档

- 原始素材：[Archive/THU-MAICOpenMAIC OpenMAIC Open Multi-Agent Interactive Classroom — Get an immersive, multi-agent learning experience in just one click.md](../../../Archive/THU-MAICOpenMAIC%20OpenMAIC%20Open%20Multi-Agent%20Interactive%20Classroom%20%E2%80%94%20Get%20an%20immersive%2C%20multi-agent%20learning%20experience%20in%20just%20one%20click.md)
