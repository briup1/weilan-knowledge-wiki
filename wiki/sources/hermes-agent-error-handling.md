---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度08-错误处理.md
tags: [hermes-agent, error-handling, retry, failover, rate-limit]
---

# Hermes Agent：错误处理

## 摘要

Hermes 的错误处理是在多供应商、多协议、多瞬时故障的真实生产环境中保持「不崩溃、不空转、不放大故障」的中枢。它把所有异常归一到结构化分类器 `ClassifiedError`，主循环根据分类结果选择「重试 / 退避 / 轮换凭证 / 切换 Provider / 压缩上下文 / 修补请求 / 中止」六类恢复动作。关键源码位于 `agent/error_classifier.py`、`agent/retry_utils.py`、`run_agent.py:12404` 附近。

## 核心主张

1. **结构化分类先于恢复**：`classify_api_error()` 是纯函数，输出 `retryable`、`should_compress`、`should_rotate_credential`、`should_fallback` 等布尔字段，调用方据此决策。
2. **metadata.raw 嵌套解析**：OpenRouter 会把 Anthropic 错误包装在 `metadata.raw` 中，分类器能内层解析，避免 context-length 被误归为 5xx 退避。
3. **402 歧义消解**：区分「账单耗尽」与「周期性配额」，避免把刚被周期性限流的 key 错误轮换走。
4. **断流 + 大会话 → 上下文溢出**：API gateway 对超大请求直接断 TCP 而不返回 413，分类器根据 `RemoteProtocolError` + `approx_tokens > context_length * 0.6` 推断为 context overflow。
5. **单工具失败不终止主循环**：`RuntimeError` 被降级为 tool 消息内容 `{"error": "..."}`，模型可基于错误自行规划下一步。
6. **退避抖动与跨进程限流广播**：指数退避加 jitter 避免 thundering herd；`nous_rate_guard.py` 用文件级共享状态阻断多进程同时反复重试。
7. **Orphan tool 补齐**：外层 except 中补齐缺失的 tool 消息，防止下轮请求因协议要求而 400 卡死。

## 恢复动作优先级

1. 凭证轮换（credential rotate）
2. 图片缩小（image too large）
3. OAuth 1M beta 禁用重建
4. Token 刷新（codex/nous/anthropic 401）
5. 上下文压缩
6. Provider fallback
7. 中止

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度08-错误处理.md)
