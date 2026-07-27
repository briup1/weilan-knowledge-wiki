---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/opencode_维度01-编排循环.md
tags: [opencode, agent-framework, typescript, open-source, ide-agent]
---

# OpenCode 框架调研（12 维度综合）

## 摘要

OpenCode 是一个**IDE 集成型 TypeScript AI Agent**，与 Cursor/Windsurf 同赛道。它通过 Session 状态机、SQLite + Drizzle ORM、AI SDK 流式消费和 Doom Loop 检测，在代码编辑场景中提供低延迟、可恢复的 Agent 体验。

## 核心定位

- **项目类型**：开源 IDE Agent（TypeScript）
- **目标场景**：代码编辑器内嵌 Agent、代码生成与重构
- **设计哲学**：IDE 原生、流式优先、结构化输出、插件扩展

## 12 维度核心特点

| 维度 | 一句话特点 |
|---|---|
| 编排循环 | `while(true)` 主循环；单次 LLM 调用无法完成的任务拆解为多轮自治迭代 |
| 工具系统 | 统一 DSL 定义、注册中心、运行时组装；类型安全、权限受控、可观测 |
| 记忆系统 | SQLite + Drizzle ORM 三层表结构（Session/Message/Part）；Prune/Compaction/Overflow 三级压缩 |
| 上下文管理 | 按文件路径向上查找 AGENTS.md/CLAUDE.md；实时生成环境信息；指令去重 |
| Prompt 构建 | Agent prompt 优先覆盖 provider prompt；2-part system 结构优化 prompt caching |
| 输出解析 | AI SDK 流式消费；工具调用修复；Doom Loop 检测 |
| 状态管理 | Session 状态机（idle/busy/retry）；Instance Map 缓存；AbortSignal 取消协议；Bus 双模发布 |
| 错误处理 | 三级分类（overflow/compaction、可重试、不可重试）；指数退避；尊重服务端 `retry-after` |
| 安全防护 | `PermissionNext` 规则引擎；Bash AST 解析；模型级工具过滤 |
| 验证循环 | 结构化输出用工具模式；zod 参数校验；Doom Loop 运行时检测 |
| 子 Agent 编排 | `TaskTool` 创建独立 child session；权限继承但禁用 todo 工具；任务可恢复 |
| 初始化与环境 | 项目 ID 基于 git root commit；7 层配置合并；AsyncLocalStorage 上下文传递 |

## 与其他框架的关键差异

| 维度 | Hermes / OpenClaw / nanobot | OpenCode |
|---|---|---|
| 集成形态 | CLI / Gateway / 个人助手 | IDE 插件 |
| 数据库 | SQLite / JSONL | SQLite + Drizzle ORM |
| 流式 | Hermes/OpenClaw 也有流式 | AI SDK 原生流式消费 |
| 取消 | 线程级 / 全局中断 | `AbortSignal` Web 标准 |
| 配置 | YAML / JSON5 | 7 层配置合并 |

## 原始文件

本 source 页综合了 OpenCode 的 12 份维度调研笔记：

- [opencode_维度01-编排循环.md](../../raw/archive/research/agent-frameworks/opencode_维度01-编排循环.md)
- [opencode_维度02-工具系统.md](../../raw/archive/research/agent-frameworks/opencode_维度02-工具系统.md)
- [opencode_维度03-记忆系统.md](../../raw/archive/research/agent-frameworks/opencode_维度03-记忆系统.md)
- [opencode_维度04-上下文管理.md](../../raw/archive/research/agent-frameworks/opencode_维度04-上下文管理.md)
- [opencode_维度05-Prompt构建.md](../../raw/archive/research/agent-frameworks/opencode_维度05-Prompt构建.md)
- [opencode_维度06-输出解析.md](../../raw/archive/research/agent-frameworks/opencode_维度06-输出解析.md)
- [opencode_维度07-状态管理.md](../../raw/archive/research/agent-frameworks/opencode_维度07-状态管理.md)
- [opencode_维度08-错误处理.md](../../raw/archive/research/agent-frameworks/opencode_维度08-错误处理.md)
- [opencode_维度09-安全防护.md](../../raw/archive/research/agent-frameworks/opencode_维度09-安全防护.md)
- [opencode_维度10-验证循环.md](../../raw/archive/research/agent-frameworks/opencode_维度10-验证循环.md)
- [opencode_维度11-子Agent编排.md](../../raw/archive/research/agent-frameworks/opencode_维度11-子Agent编排.md)
- [opencode_维度12-初始化与环境.md](../../raw/archive/research/agent-frameworks/opencode_维度12-初始化与环境.md)
