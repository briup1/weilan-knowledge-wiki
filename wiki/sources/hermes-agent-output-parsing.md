---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度06-输出解析.md
tags: [hermes-agent, output-parsing, reasoning-content, tool-calls, transport]
---

# Hermes Agent：输出解析

## 摘要

Hermes 的输出解析负责将 LLM 返回的原始字节流（结构化 JSON、SSE chunk、XML 标签、原生 SDK 对象）转化为 Agent 内部统一消费的标准化消息，并提取 tool_calls、reasoning content、finish_reason 等语义单元，决定下一步是执行工具还是向用户交付最终回复。关键源码位于 `agent/transports/`、`agent/think_scrubber.py`、`run_agent.py:13332` 附近。

## 核心主张

1. **Transport 归一化层**：每个 `api_mode` 有独立 Transport 类，统一输出 `NormalizedResponse`，`run_agent.py` 核心循环无 provider 感知代码。
2. **Reasoning 双轨存储**：内部用 `reasoning` 字段存纯文本；API 回传时按 provider 要求转换成 `reasoning_content` / `reasoning_details` / 空格占位等形态。
3. **流式状态机 scrubber**：`StreamingThinkScrubber` 维护跨 delta 状态，避免 per-delta 正则破坏 `<thinking>` 标签边界。
4. **Tool-call 参数修复**：`_repair_tool_call_arguments()` 用 5 层策略修复非法 JSON，最终回退到 `"{}"`，避免会话崩溃。
5. **消息序列防御性修复**：`_sanitize_api_messages()` + `_repair_message_sequence()` + `_drop_trailing_empty_response_scaffolding()` 三重防护，防止 orphan tool result 导致空回复死循环。

## Provider 响应差异处理

| Provider | Tool call | Reasoning | 特殊处理 |
|---|---|---|---|
| OpenAI | `message.tool_calls[].function` | `reasoning_content` | — |
| Anthropic | `content_blocks` 中 `tool_use` | `thinking` block | `reasoning_details` |
| Gemini | `parts[].functionCall` | 自定义字段 | — |
| DeepSeek | 类 OpenAI | `reasoning_content` | tool-call 轮次必须回传 |
| 本地模型 | 类 OpenAI | 可能混入 content | JSON 修复、非法 JSON 回退 |

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度06-输出解析.md)
