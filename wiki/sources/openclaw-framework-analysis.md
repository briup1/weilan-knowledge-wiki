---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/openclaw_维度01-编排循环.md
tags: [openclaw, agent-framework, typescript, open-source]
---

# OpenClaw 框架调研（12 维度综合）

## 摘要

OpenClaw 是一个面向**生产环境的 TypeScript AI Agent** 框架，强调双层队列并发、in-process 重启、上下文压缩、多层策略管道和 Docker 沙箱隔离。它在错误处理、模型故障转移、安全沙箱和配置可扩展性上投入了大量工程。

## 核心定位

- **项目类型**：开源 Agent 框架（TypeScript）
- **目标场景**：生产级 Gateway/CLI 部署、多会话、高可用
- **设计哲学**：纵深防御、可配置策略、进程内恢复

## 12 维度核心特点

| 维度 | 一句话特点 |
|---|---|
| 编排循环 | 双层队列（Session Lane + Global Lane）；in-process 重启保留 macOS TCC 权限 |
| 工具系统 | 6 层策略管道（profile/provider/global/agent/group/sandbox/subagent）；Docker 沙箱文件系统；循环检测 |
| 记忆系统 | Markdown 文件为唯一事实来源，SQLite 仅作索引；hybrid 向量 + BM25 检索 |
| 上下文管理 | 四层独立预算（Bootstrap/历史/工具结果/Compaction）；专门 compaction agent |
| Prompt 构建 | PromptMode 三级（full/minimal/none）；工具硬编码排序；技能路径压缩 |
| 输出解析 | 流式状态机；`message_start` 重置状态；单调输出保证；代码块保护 |
| 状态管理 | 文件级写锁 + 内存锁队列；ACP 运行时 Map 缓存；Gateway 聊天状态纯内存 |
| 错误处理 | 指数退避 + jitter + Retry-After；模型故障转移；工具循环检测 |
| 安全防护 | Docker 沙箱默认；三级执行审批；DNS 解析前/后双重 SSRF 防护；SecretRef 密钥引用 |
| 验证循环 | 工具循环检测向 LLM 注入警告；配置验证懒加载；Skill 静态扫描 |
| 子 Agent 编排 | 独立 session；事件驱动 push 交付；基于 `spawnedBy` 链的深度限制 |
| 初始化与环境 | JSON5 + `$include` + `${ENV}`；Jiti 运行时 TS 插件加载；单一入口 + respawn |

## 与 Hermes 的关键差异

| 维度 | Hermes | OpenClaw |
|---|---|---|
| 语言 | Python | TypeScript |
| 并发 | ThreadPool 线程级中断 | 双层队列（session + global） |
| 沙箱 | 环境后端 ABC（local/docker/modal/ssh） | Docker 容器默认 + `SandboxFsBridge` |
| 记忆索引 | FTS5 / 外部 provider | 向量 + BM25 hybrid |
| 配置 | YAML 三路合并 | JSON5 + `$include` |
| 重启 | 进程内 `restartResolver` | 外部 systemd 等 |

## 原始文件

本 source 页综合了 OpenClaw 的 12 份维度调研笔记：

- [openclaw_维度01-编排循环.md](../../raw/archive/research/agent-frameworks/openclaw_维度01-编排循环.md)
- [openclaw_维度02-工具系统.md](../../raw/archive/research/agent-frameworks/openclaw_维度02-工具系统.md)
- [openclaw_维度03-记忆系统.md](../../raw/archive/research/agent-frameworks/openclaw_维度03-记忆系统.md)
- [openclaw_维度04-上下文管理.md](../../raw/archive/research/agent-frameworks/openclaw_维度04-上下文管理.md)
- [openclaw_维度05-Prompt构建.md](../../raw/archive/research/agent-frameworks/openclaw_维度05-Prompt构建.md)
- [openclaw_维度06-输出解析.md](../../raw/archive/research/agent-frameworks/openclaw_维度06-输出解析.md)
- [openclaw_维度07-状态管理.md](../../raw/archive/research/agent-frameworks/openclaw_维度07-状态管理.md)
- [openclaw_维度08-错误处理.md](../../raw/archive/research/agent-frameworks/openclaw_维度08-错误处理.md)
- [openclaw_维度09-安全防护.md](../../raw/archive/research/agent-frameworks/openclaw_维度09-安全防护.md)
- [openclaw_维度10-验证循环.md](../../raw/archive/research/agent-frameworks/openclaw_维度10-验证循环.md)
- [openclaw_维度11-子Agent编排.md](../../raw/archive/research/agent-frameworks/openclaw_维度11-子Agent编排.md)
- [openclaw_维度12-初始化与环境.md](../../raw/archive/research/agent-frameworks/openclaw_维度12-初始化与环境.md)
