---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度04-上下文管理.md
tags: [hermes-agent, context-management, context-compression, prompt-cache]
---

# Hermes Agent：上下文管理

## 摘要

Hermes 的上下文管理把「塞进 LLM 一次请求里的所有 token」当作受限资源来主动经营，决定**什么进、什么出、以什么形态出、以什么时机出**。核心机制是三段式：稳定的 system prompt（缓存层）+ 可压缩的 conversation messages + 动态的 tool schemas。关键源码位于 `agent/context_compressor.py`、`run_agent.py:11011-11069`。

## 核心主张

1. **Preflight 压缩**：每次进入主循环前，若估算 token 超过 `threshold_tokens`，先主动压缩，避免后端返回 context-length 4xx。
2. **Tool-call/result 配对修复**：压缩会制造孤儿 tool_call/result，`context_compressor.py:1041-1099` 的 `_sanitize_tool_pairs` 自动修复，否则后续请求会持续 400。
3. **最近 user 消息锁定 tail**：`_ensure_last_user_message_in_tail` 硬保护最后一条 user 消息不被压入 summary 区，防止「压缩后忘记用户在问什么」。
4. **Prompt cache 保护**：动态内容（plugin context、recall）只注入 user 消息，不修改 system prompt，最大化 Anthropic prefix cache 命中。
5. **Anti-thrashing**：连续两次压缩节省 < 10% 时停手，避免无效循环。

## 压缩触发点

- 主循环 preflight：`estimate_request_tokens_rough() >= threshold_tokens`
- 响应后压缩：`last_prompt_tokens >= threshold_tokens`
- 错误恢复压缩：context-length 4xx 被 `error_classifier` 标记为 `should_compress`
- 手动 `/compress [focus]`：用户可带 focus topic 引导式压缩

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度04-上下文管理.md)
