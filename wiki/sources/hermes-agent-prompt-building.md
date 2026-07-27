---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度05-Prompt构建.md
tags: [hermes-agent, prompt-building-for-agents, system-prompt, prompt-cache]
---

# Hermes Agent：Prompt 构建

## 摘要

Hermes 的 Prompt 构建负责将 Agent 的「身份、能力、记忆、环境、技能索引」等多源信息按严格优先级组装成稳定的系统提示，并在 API 调用前叠加瞬态指令与缓存控制标记，以最大化多轮对话的 prefix cache 命中率并降低 token 成本。关键源码位于 `agent/prompt_builder.py`、`run_agent.py:5114-5226`。

## 核心主张

1. **洋葱式 system prompt 组装**：从身份（SOUL.md）→ 工具感知行为 → 模型家族特化 → 用户系统消息 → 持久记忆 → 外部记忆 → 技能索引 → 项目上下文文件 → 时间戳 → 平台格式提示。
2. **会话级缓存 + SQLite 持久化**：`_cached_system_prompt` 在一个会话内只构建一次，压缩事件后才失效，避免每轮重建破坏 prefix cache。
3. **技能索引双层缓存**：进程内 LRU（8 条目）+ 磁盘 snapshot（`.skills_prompt_snapshot.json`），按 mtime/size 校验，兼顾冷启动与运行时效率。
4. **上下文文件优先级严格互斥**：`.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`，只加载第一个，避免多项目上下文冲突。
5. **瞬态提示分离**：`ephemeral_system_prompt` 和 `prefill_messages` 只在 API 调用时才叠加，不进入缓存/存储。
6. **Prompt injection 扫描**：`_scan_context_content()` 在加载上下文文件时检测 9 类威胁模式。

## System Prompt 层次

| 层级 | 内容 | 稳定性 |
|---|---|---|
| 1 | SOUL.md / DEFAULT_AGENT_IDENTITY | 最稳定 |
| 2 | 产品自指引导 | 稳定 |
| 3 | 工具感知行为引导（memory/skills/kanban 等） | 条件注入 |
| 4 | 模型家族特化引导（tool use enforcement 等） | 按模型 |
| 5 | 用户/网关传入的系统消息 | 稳定 |
| 6-7 | 持久记忆 + 外部记忆 | 快照稳定 |
| 8 | 技能索引 | 缓存稳定 |
| 9 | 项目上下文文件 | 文件级稳定 |
| 10-11 | 时间戳、平台格式提示 | 每轮变化但不入缓存 |

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度05-Prompt构建.md)
