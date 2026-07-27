---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, context-management, context-compression, prompt-cache]
---

# Context Management（上下文管理）

## 定义

上下文管理是把「塞进 LLM 一次请求里的所有 token」当作受限资源来主动经营的能力：决定**什么进、什么出、以什么形态出、以什么时机出**，使 Agent 能在固定上下文窗口下持续运行而不丢失任务、不破坏 prompt cache、不撞 4xx。

## 为什么需要

- LLM 上下文窗口有限；长会话必然溢出。
- 上下文溢出会导致后端返回 4xx，处理不当会报废整个 session。
- 上下文中的工具调用/结果配对若被截断，会产生 orphan tool message，导致后续请求持续 400。
- Prompt cache（如 Anthropic）要求 system prompt 稳定；频繁修改会显著增加成本。

## 核心策略

| 策略 | 说明 |
|---|---|
| Preflight 压缩 | 在发送请求前主动估算 token，超过阈值先压缩 |
| 响应后压缩 | 根据后端返回的真实 prompt_tokens 触发压缩 |
| 错误恢复压缩 | 收到 context-length 4xx 后把压缩作为恢复动作 |
| 保护首尾 | 头部 N 条和尾部 M 条消息保留，中间压缩 |
| 锁定最后 user 消息 | 防止压缩后丢失用户当前请求 |
| Tool-call 配对修复 | 压缩后自动修复 orphan tool_call/tool 消息 |
| System prompt 隔离 | 动态内容注入 user 消息，不修改 system prompt |

## 三段式视图

```
System Prompt（缓存层 / 一个 session 只 build 一次）
  ↓
Conversation Messages（持久化 / 可压缩）
  ├─ head: 受保护 N 条
  ├─ middle: 可压缩区 → LLM 摘要
  └─ tail: token-budget 锁定区（含最后 user 消息）
  ↓
Tool Schemas（动态 / 与 messages 解耦）
```

## 设计权衡

| 权衡 | 选项 A | 选项 B |
|---|---|---|
| 压缩时机 | 发送前主动压 | 出错后被动压 |
| 摘要模型 | 用同一模型自总结 | 用轻量模型外挂 |
| 保留策略 | 保留最近 K 轮 | 保留关键轮次 |
| 缓存优先级 | 保护 system prompt | 动态调整 system prompt |

生产级系统通常同时采用「主动 + 被动」双轨压缩，并以保护 system prompt 缓存为优先。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 压缩触发 | preflight + 响应后 + 错误恢复三种入口 | token 超限触发 `consolidate()`；`/new` 强制归档 | 四层独立预算 + 动态窗口发现 | Prune → Compaction → Overflow 三级 |
| 压缩策略 | LLM 生成 12-section 结构化摘要；auxiliary 压缩模型 fallback | LLM 驱动 `save_memory` 生成语义摘要；按用户轮次边界 | 专门 compaction agent；multi-stage 摘要 | Compaction agent 五部分摘要 |
| 缓存保护 | system prompt 稳定，动态内容注入 user message | RuntimeContext 合并到 user message | ephemeral injection 不写入 SQLite；2-part system | 2-part system header + rest；header 不变缓存 |
| 工具结果处理 | 纳入 preflight token 预算 | 超过 16K 截断头部 | head+tail 保留，中间占位 | 流式处理 |
| 持久化策略 | SQLite 持久化完整 messages | JSONL 持久化；剥离 RuntimeContext | 文件级写锁 + 内存锁队列 | SQLite + Drizzle ORM |
| 独特设计 | 保护首尾 + 锁定最后 user 消息 | 以 user 轮次为最小固化单元 | 工具结果 head+tail 截断 | 指令文件向上查找 + 去重 |

## 与相关概念的关系

- 上下文管理在 [[orchestration-loop]] 的每轮迭代前执行。
- 压缩需要 [[prompt-building-for-agents]] 中稳定的 system prompt 配合。
- 压缩后的消息序列需要 [[output-parsing]] 的配对修复支持。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `context_compressor` 实现。其他框架待补充。
