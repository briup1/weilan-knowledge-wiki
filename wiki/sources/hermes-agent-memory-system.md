---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度03-记忆系统.md
tags: [hermes-agent, agent-memory-system, memory-provider, honcho, mem0]
---

# Hermes Agent：记忆系统

## 摘要

Hermes 的记忆系统是**「内置 MemoryStore + 外部 MemoryProvider 插件」的双层架构**。内置 MEMORY.md/USER.md 以「载入时冻结快照、写入时落盘但不刷新 prompt」的方式保护 prefix cache；外部 provider 通过统一 ABC 接口以「prefetch → 注入用户消息 → sync_turn」的节奏接入。关键源码位于 `tools/memory_tool.py`、`agent/memory_manager.py`、`agent/memory_provider.py`。

## 核心主张

1. **内置记忆 frozen snapshot**：`load_from_disk()` 一次性把 MEMORY/USER 块渲染到 `_system_prompt_snapshot`，本会话内只读，新写入落盘但下次会话才生效，保护 prefix cache。
2. **外部 recall 注入 user 消息**：`run_agent.py:11311-11322` 把 prefetch 结果通过 `<memory-context>` fence 拼到当前 user 消息末尾，不修改原 messages，不污染会话持久化。
3. **MemoryProvider ABC 插件化**：`agent/memory_provider.py:42` 定义统一接口，新后端只需实现几个生命周期方法，不改 `run_agent.py` 主流程。
4. **单 external provider 约束**：第二个非 builtin provider 会被拒绝，避免工具名冲突、schema 膨胀和并发 RPC 开销。
5. **失败不阻塞主流程**：所有 manager 方法都用 try/except + logger 包裹，外部记忆后端离线不影响用户看到回复。

## 关键生命周期

- 启动：`MemoryStore.load_from_disk()` + `load_memory_provider(name)`
- 每轮：`on_turn_start()` → `prefetch_all()` → 注入 user 消息 → 工具调用 → `sync_all()` + `queue_prefetch_all()`
- 边界：`on_pre_compress()`、`on_session_switch()`、`on_session_end()`

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度03-记忆系统.md)
