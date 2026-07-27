---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/nanobot_维度01-编排循环.md
tags: [nanobot, agent-framework, python, open-source]
---

# nanobot 框架调研（12 维度综合）

## 摘要

nanobot 是一个面向**个人用户的轻量级 Python AI Agent** 框架，强调小而美的设计：单进程 asyncio、全局锁串行处理、JSONL 持久化、双层文件记忆（MEMORY.md + HISTORY.md）。它在并发控制、工具抽象、安全防护和子 Agent 编排上都做了与 Hermes/OpenClaw/OpenCode 不同的取舍。

## 核心定位

- **项目类型**：开源 Agent 框架（Python，asyncio）
- **目标场景**：个人助手、单用户、轻量部署
- **设计哲学**：小而美、零外部依赖、显式组装

## 12 维度核心特点

| 维度 | 一句话特点 |
|---|---|
| 编排循环 | Actor 风格消息泵 + 全局 `asyncio.Lock` 串行处理，`/stop` 走同一 inbound 队列 |
| 工具系统 | `Tool` ABC + `ToolRegistry` 字典调度；先 `cast_params` 再 `validate_params`；错误以字符串返回 |
| 记忆系统 | MEMORY.md（长期事实）+ HISTORY.md（可检索日志）；LLM 驱动的 `save_memory` 固化 |
| 上下文管理 | RuntimeContext 合并到 user message；持久化前剥离；丢弃非 user 开头的历史 |
| Prompt 构建 | Bootstrap 文件（AGENTS.md/SOUL.md/USER.md/TOOLS.md）+ 技能摘要索引 |
| 输出解析 | Think 块剥离下沉为全局工具；error 响应不进入历史 |
| 状态管理 | JSONL 持久化 + 进程内 dict 缓存 + 全局单锁 |
| 错误处理 | 分层降级（Provider/Registry/Loop/Memory），工具错误注入 `_HINT` |
| 安全防护 | SSRF 独立模块 + `restrict_to_workspace` + `allowFrom` 默认拒绝 |
| 验证循环 | 先 cast 再 validate 的"类型防火墙"；手写轻量 JSON Schema 校验 |
| 子 Agent 编排 | 子 Agent 无 message/spawn 工具；结果通过 MessageBus 以 system 消息注入 |
| 初始化与环境 | 显式 CLI 命令 `onboard`/`gateway`/`agent`；Provider 关键词启发式匹配 |

## 与 Hermes 的关键差异

| 维度 | Hermes | nanobot |
|---|---|---|
| 并发模型 | ThreadPool 并发工具 + 线程级精确中断 | 全局 asyncio.Lock 串行 |
| 持久化 | SQLite + WAL + FTS5 | JSONL |
| 记忆 | 内置 MemoryStore + 外部 MemoryProvider 插件 | MEMORY.md + HISTORY.md 双层文件 |
| 错误处理 | 结构化分类器 + 六类恢复动作 | 分层降级 + `_HINT` |
| 部署目标 | 网关/多会话生产环境 | 个人助手 |

## 原始文件

本 source 页综合了 nanobot 的 12 份维度调研笔记：

- [nanobot_维度01-编排循环.md](../../raw/archive/research/agent-frameworks/nanobot_维度01-编排循环.md)
- [nanobot_维度02-工具系统.md](../../raw/archive/research/agent-frameworks/nanobot_维度02-工具系统.md)
- [nanobot_维度03-记忆系统.md](../../raw/archive/research/agent-frameworks/nanobot_维度03-记忆系统.md)
- [nanobot_维度04-上下文管理.md](../../raw/archive/research/agent-frameworks/nanobot_维度04-上下文管理.md)
- [nanobot_维度05-Prompt构建.md](../../raw/archive/research/agent-frameworks/nanobot_维度05-Prompt构建.md)
- [nanobot_维度06-输出解析.md](../../raw/archive/research/agent-frameworks/nanobot_维度06-输出解析.md)
- [nanobot_维度07-状态管理.md](../../raw/archive/research/agent-frameworks/nanobot_维度07-状态管理.md)
- [nanobot_维度08-错误处理.md](../../raw/archive/research/agent-frameworks/nanobot_维度08-错误处理.md)
- [nanobot_维度09-安全防护.md](../../raw/archive/research/agent-frameworks/nanobot_维度09-安全防护.md)
- [nanobot_维度10-验证循环.md](../../raw/archive/research/agent-frameworks/nanobot_维度10-验证循环.md)
- [nanobot_维度11-子Agent编排.md](../../raw/archive/research/agent-frameworks/nanobot_维度11-子Agent编排.md)
- [nanobot_维度12-初始化与环境.md](../../raw/archive/research/agent-frameworks/nanobot_维度12-初始化与环境.md)
