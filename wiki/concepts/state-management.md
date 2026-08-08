---
type: concept
created: 2026-07-26
updated: 2026-08-05
sources: [hermes-agent-state-management, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis, pi-session-system]
tags: [agent-architecture, state-management, session-db, persistence]
---

# State Management（状态管理）

## 定义

状态管理是 Agent 系统中负责维护**运行时状态**与**持久化状态**的能力。运行时状态支持低延迟读写和实时诊断；持久化状态支持跨进程共享、崩溃恢复、历史检索和审计。

## 为什么需要

- 长会话需要保存消息历史、元数据、用户偏好，防止进程崩溃后丢失。
- 多进程/多实例并发读写时需要避免脏写和数据损坏。
- 运维调试需要实时获取 Agent 的运行时活动快照。
- 功能迭代要求数据库 schema 持续演进，但迁移脚本维护成本高。

## 双轨架构

```
┌─────────────────────────────────────────┐
│  运行时状态（AIAgent 实例内存）          │
│  ─ 迭代预算、中断标志、API 计数         │
│  ─ 最近活动时间、当前任务 ID             │
│  ─ 低延迟、会话级、随进程消失           │
└─────────────────────────────────────────┘
                    ↕ 同步/回写
┌─────────────────────────────────────────┐
│  持久化状态（SQLite / 其他存储）         │
│  ─ 会话元数据、消息历史                  │
│  ─ 全文索引、配置、审批记录              │
│  ─ 跨进程共享、崩溃可恢复                │
└─────────────────────────────────────────┘
```

## 关键设计点

| 设计点 | 说明 |
|---|---|
| WAL 模式 | 多 reader + 单 writer 并发，避免读写互斥 |
| 应用级随机抖动退避 | 降低多进程同时重试的碰撞概率 |
| 声明式 schema 调和 | 以代码内 `SCHEMA_SQL` 为唯一来源，自动补齐缺失列 |
| 版本门控迁移 | `state_meta` 表记录版本，确保幂等回填 |
| 全文检索 | FTS5 支持 unicode61/trigram，兼顾英文和 CJK |
| 原子性消息替换 | `/retry`、`/undo`、`/compress` 在单事务内完成 |

## Entry Tree 状态模型

[[pi-session-system]] 展示了数据库双轨之外的事件日志方案：

```text
fileEntries: 顺序事件日志
byId:        id → Entry 内存索引
leafId:      当前分支游标
parentId:    持久化的父引用
```

[[session-persistence]] 定义会话事实的落盘、恢复与 Schema 演进边界；其中 [[session-entry-tree]] 保存完整事实，[[session-context-projection]] 负责构造当前模型视图，[[append-only-session-persistence]] 则用 JSONL 提供增量写入和崩溃恢复。该模型说明“持久化状态”与“当前可见消息”可以拥有不同数据结构和生命周期。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 运行时状态 | `AIAgent` 内存态：budget、interrupt、API 计数 | 内存 `Session.messages` + `SessionManager._cache` | 内存 Map + Gateway 聊天缓冲 | `SessionStatus` + Bus 订阅 |
| 持久化 | SQLite + WAL + FTS5 双索引 | JSONL 每会话一个文件 | 文件级写锁 + 内存锁队列 | SQLite + Drizzle ORM（Session/Message/Part） |
| 并发控制 | WAL + 应用级随机抖动退避 | 全局单锁 `_processing_lock` | 文件级写锁 + 内存锁队列 | Instance Map 缓存 + Bus 双模发布 |
| Schema 演进 | 声明式 schema 调和，自动 ALTER TABLE ADD COLUMN | 无 schema（JSONL） | 文件级写锁 | Drizzle ORM + Zod |
| 会话恢复 | `parent_session_id` 压缩链 | `last_consolidated` 切片 | 压缩快照回退 | task_id 恢复子任务 |
| 独特设计 | FTS5 unicode61 + trigram 双索引 | 零 schema 迁移成本 | 跨进程文件锁 | Part 级存储 + 级联删除 |

## 与相关概念的关系

- 运行时状态在 [[orchestration-loop]] 内被频繁读写。
- [[session-persistence]] 负责会话事实的落盘、恢复、并发边界与 Schema 演进。
- 持久化状态为 [[context-management]] 的压缩和会话切换提供数据基础。
- 状态数据库可支撑 [[agent-memory-system]] 的长期记忆。

## 当前证据

当前证据来自 [[hermes-agent-state-management]]、[[nanobot-framework-analysis]]、[[openclaw-framework-analysis]]、[[opencode-framework-analysis]] 与 [[pi-session-system]]。
