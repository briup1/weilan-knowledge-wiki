---
type: source
created: 2026-05-14
updated: 2026-05-18
raw: raw/archive/Hermes Agent 完全新手指南：AI界最快破10万星的开源项目.md
tags: [hermes-agent, open-source, agent-memory, skills, mcp, nous-research]
---

# Hermes Agent 完全新手指南：AI界最快破10万星的开源项目

**来源**：微信公众号 / 程康健
**链接**：https://mp.weixin.qq.com/s/A_RzvL-u3XedXy6lAb11vQ

## 摘要

Hermes Agent 是 NousResearch 于 2026 年 2 月开源的 AI 智能体框架，口号为「The agent that grows with you」（跟你一起成长的 Agent）。不到 3 个月 GitHub 突破 10 万星，核心差异化在于：闭合学习循环（自动提炼 Skill）、三层持久记忆、多平台网关和 20+ 模型自由切换。本文是 12 章完整新手教程的摘要。

## 核心主张

1. **闭合学习循环（Closed Learning Loop）**：每次完成复杂任务后，Agent 自动将成功经验总结为「Skill」（SKILL.md），存入技能库。下次同类任务直接调用，越用越聪明。触发条件：5 步以上工具调用、碰到错误找到解决路径、被纠正操作方式、发现非显而易见的工作流程。
2. **三层持久记忆**：
   - `MEMORY.md`：通用记忆（任务笔记、技术偏好、常用路径、重要发现）
   - `USER.md`：用户画像（背景、习惯、偏好、工作方式）
   - `SOUL.md`：Agent 人格（角色、语气、行为风格）
   配合 SQLite + FTS5 全文搜索引擎，Agent 可在任意时刻召回历史对话。
3. **多平台网关**：支持 Telegram、Discord、Slack、WhatsApp、Signal 等 15+ 即时通讯平台，以及 Email、Home Assistant。一个 Gateway 进程可同时监听多个平台，实现「你睡觉，它在跑」。
4. **20+ LLM 提供商自由切换**：OpenAI、Anthropic Claude、DeepSeek、Qwen、Gemini、GLM、Kimi 等，通过 `hermes model` 一键切换，无需改代码。
5. **Skills Hub 技能市场**：内置完整的技能搜索、预览、安装机制，支持 official、skills-sh、well-known、GitHub、clawhub、lobehub 等多种来源。

## 关键洞察

- **Skill 的三级加载机制**：Level 0（技能列表，~3000 tokens）→ Level 1（技能完整内容）→ Level 2（技能参考文件），只在需要时加载，有效控制 token 消耗。这遵循渐进式披露（Progressive Disclosure）模式。
- **终端执行后端多样化**：local（本机）/ docker（隔离）/ ssh（远程）/ daytona（Serverless 持久化）/ modal（按需唤醒），满足不同安全需求场景。
- **AGENTS.md 项目级配置**：在任意项目目录下创建 AGENTS.md，可为该项目提供专属上下文和指令，每次在该目录启动 Hermes 时自动加载。
- **定时自动化**：内置 cron 调度器，用自然语言描述即可创建定时计划（如「每天早上 9 点查看 Hacker News AI 新闻，整理成中文摘要发到 Telegram」）。
- **与 Claude Code 不是竞争，是互补**：Claude Code 是专业编码工具（深度代码理解），Hermes 是持久化自主 Agent（长期记忆、跨平台、定时任务）。最佳组合：Hermes 做大脑和调度，Claude Code 做执行引擎。

## 与现有知识的关联

- 是 [[hermes-agent]] entity 的核心信息来源
- 三层记忆系统（MEMORY/USER/SOUL）与 [[agent-memory-system]] 的四类记忆（user/feedback/project/reference）形成对照
- Skills 机制与 [[claude-code-skills]] 的 SKILL.md 设计哲学一致
- 与 [[agent-harness]] 的方法论有明确的产品化对应关系
- MCP 集成与 [[mcp]] 概念直接关联

## 原始文件

- [原始文件](../../raw/archive/Hermes%20Agent%20%E5%AE%8C%E5%85%A8%E6%96%B0%E6%89%8B%E6%8C%87%E5%8D%97%EF%BC%9AAI%E7%95%8C%E6%9C%80%E5%BF%AB%E7%A0%B410%E4%B8%87%E6%98%9F%E7%9A%84%E5%BC%80%E6%BA%90%E9%A1%B9%E7%9B%AE.md)
