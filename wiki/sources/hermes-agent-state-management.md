---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度07-状态管理.md
tags: [hermes-agent, state-management, session-db, sqlite, fts5]
---

# Hermes Agent：状态管理

## 摘要

Hermes 的状态管理采用**「运行时内存状态 + SQLite 持久化状态」双轨架构**。`AIAgent` 实例持有运行期可变状态（迭代预算、中断信号、API 计数等），`SessionDB` 通过启用 WAL 的 SQLite 提供事务化持久化，并辅以声明式 schema 调和、FTS5 全文检索、版本门控迁移与随机抖动写竞争重试。关键源码位于 `agent/session_db.py`、`run_agent.py:1020-1280`。

## 核心主张

1. **运行时与持久化分离**：运行时需要低延迟读写和实时诊断；持久化需要跨进程共享与崩溃恢复。
2. **SQLite WAL + 应用级随机抖动**：WAL 允许多 reader 与单 writer 共存；随机抖动退避（20–150 ms）降低多进程同时重试的碰撞概率。
3. **声明式 schema 调和**：`SCHEMA_SQL` 是唯一来源，启动时与现有表结构做列级对比，自动 `ALTER TABLE ADD COLUMN`，无需手写迁移脚本。
4. **FTS5 双索引**：默认 `unicode61` 处理英文，CJK 文本 fallback 到 `trigram`，搜索无果再降级 `LIKE`。
5. **原子性消息替换**：`/retry`、`/undo`、`/compress` 等命令在单个事务内删除旧消息并插入新消息。
6. **压缩延续链**：压缩后的会话通过 `parent_session_id` 建立递归关联，可展示压缩链历史。

## 关键运行时状态

- `iteration_budget`：防止无限循环
- `_interrupt_requested`：用户/系统中断信号
- `_api_call_count`：当前 turn 的 API 调用计数
- `_last_activity_ts` / `_last_activity_desc`：实时诊断快照
- `session_id`：`{timestamp}_{short_uuid}`，兼顾可读性与唯一性

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度07-状态管理.md)
