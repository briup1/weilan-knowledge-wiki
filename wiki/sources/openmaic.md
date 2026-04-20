---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/THU-MAICOpenMAIC Open Multi-Agent Interactive Classroom — Get an immersive, multi-agent learning experience in just one click.md
tags: [multi-agent, education, ai-classroom, open-source, langgraph]
---

# OpenMAIC：开源多智能体互动课堂平台

## 摘要

OpenMAIC（Open Multi-Agent Interactive Classroom）是由清华大学 THU-MAIC 团队开发的开源 AI 互动课堂平台，基于 Next.js 和 LangGraph 构建。它能够将任意主题或文档转化为丰富的互动学习体验，通过多智能体协作引擎自动生成演示幻灯片、测验、交互式模拟实验和项目制学习（PBL）活动。AI 教师和 AI 同学可进行语音讲解、白板绘图，并与学习者实时讨论。平台支持 OpenClaw 集成，可在飞书、Slack、Telegram 等 20+ 聊天应用中直接生成课堂。项目基于 AGPL-3.0 协议开源，已有相关论文发表于 Journal of Computer Science and Technology。

## 核心要点

- **两阶段课堂生成流水线**：大纲生成（AI 分析输入生成结构化大纲）→ 场景生成（每个大纲条目生成为幻灯片、测验、交互模块或 PBL 活动）
- **四种课堂组件**：幻灯片（AI 语音讲解配合聚光灯/激光笔）、测验（单选/多选/简答，AI 实时判分）、交互式模拟（HTML 可视化实验）、项目制学习（PBL，角色协作完成结构化项目）
- **多智能体互动**：课堂讨论（智能体主动发起话题）、圆桌辩论（多个人设智能体讨论）、自由问答、白板实时绘图（SVG -based，支持公式推导和流程图）
- **技术架构**：Next.js App Router + TypeScript；LangGraph 多智能体编排（导演图状态机）；28+ 种动作类型的动作执行引擎（语音、白板、特效）；Zustand 状态管理
- **多 LLM 支持**：OpenAI、Anthropic、Google Gemini、DeepSeek、MiniMax、Grok、豆包、Ollama（本地）及任何兼容 OpenAI API 的服务；推荐 Gemini 3 Flash（效果与速度平衡）
- **导出能力**：可编辑的 PowerPoint (.pptx)、交互式 HTML 网页、课堂 ZIP（完整导出含媒体文件）
- **OpenClaw 集成**：通过 `clawhub install openmaic` 在 20+ 聊天应用中生成课堂，支持托管模式（访问码）和本地部署模式
- **部署方式**：本地开发（pnpm）、Vercel、Docker，可选 ACCESS_CODE 站点级密码保护

## 原始文件

- [原始文件](../../raw/archive/THU-MAICOpenMAIC Open Multi-Agent Interactive Classroom — Get an immersive, multi-agent learning experience in just one click.md)
