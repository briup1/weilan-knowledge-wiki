---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/前沿重器85  Claude Code源码阅读：万字解析记忆系统.md
tags: [claude-code, memory-system, source-code-analysis, agent-memory, kairos, auto-dream]
---

# Claude Code 源码阅读：万字解析记忆系统

## 摘要

本文深度拆解了 Claude Code（TypeScript 版本）的本地文件式记忆系统。该系统完全落地在本地目录，不依赖云端数据库，支持个人/团队/项目三层隔离。记忆分为四大类型：user（用户画像）、feedback（工作指导）、project（项目背景）、reference（外部资源指针）。记忆以 Markdown 文件形式存储，通过 MEMORY.md 索引管理，采用「两步保存」流程（写文件 → 更新索引）。系统还包含 KAIROS 日志模式（append-only 的每日日志，通过 /dream 夜间蒸馏为结构化记忆）和会话记忆（session-memory.md，用于对话压缩）。核心流程涵盖启动时预加载、每次查询前动态注入、基于 Sonnet 的相关性检索（最多选 5 条）、以及 extractMemories（查询结束时触发）和 /dream（每日后台整理）两种提取机制。文章还分析了记忆维护的挑战（冲突处理、信息过时、重复冗余）及对应的解决策略。

## 核心要点

- **四类结构化记忆**：user（用户角色/偏好/知识）、feedback（用户纠正与确认）、project（谁在做什么/为什么/何时完成）、reference（外部系统资源指针）。
- **文件式存储结构**：`~/.claude/projects/<project>/memory/` 下存放记忆片段 Markdown 文件 + MEMORY.md 索引，团队记忆在 `team/` 子目录。
- **记忆文件格式**：YAML frontmatter（name、description、type）+ Markdown 内容；索引 MEMORY.md 每行一条 `- [Title](file.md) — one-line hook`，无 frontmatter，200 行/25KB 上限。
- **KAIROS 日志模式**：长生命周期会话的 append-only 每日日志（`logs/YYYY/MM/YYYY-MM-DD.md`），记录用户更正、偏好、项目背景、外部系统指引等；夜间通过 /dream 四阶段（Orient→Gather→Consolidate→Prune）蒸馏为结构化记忆。
- **会话记忆（Session Memory）**：`~/.claude/session-memory.md`，阈值触发（token 数 + 工具调用数），10 个章节（当前状态、任务说明、文件和函数、工作流程、错误和修正、代码库文档、经验总结、关键结果、工作记录），用于对话压缩（compaction）。
- **记忆加载机制**：启动时预加载到 readFileState 缓存；每次查询前通过 `getUserContext` 动态注入到系统提示。
- **记忆提取流程**：handleStopHooks → executeExtractMemories → 检查互斥/节流 → 扫描现有记忆 → 构建 Prompt → 执行分叉 agent（最多 5 轮）→ 写入文件 → 更新索引。
- **/dream 机制**：三重门控（时间≥24h、扫描节流、新会话数≥minSessions），四阶段整固（了解现状→收集信号→整合记忆→修剪索引），后台异步执行。
- **相关性检索**：`findRelevantMemories` 扫描最多 200 个记忆文件，通过 Sonnet 侧边查询选择最多 5 条相关记忆，注入到系统提示作为 attachments。
- **记忆维护策略**：冲突处理（最新胜出、特异性优先、合并去重）、新鲜度检测（>1 天添加 system-reminder 标签）、过时信息验证与更新。

## 原始文件

- [原始文件](../../raw/archive/前沿重器85%20%20Claude%20Code源码阅读：万字解析记忆系统.md)
