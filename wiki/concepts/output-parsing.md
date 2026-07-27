---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, output-parsing, tool-calls, reasoning-content, transport]
---

# Output Parsing（输出解析）

## 定义

输出解析是将 LLM 返回的原始响应（结构化 JSON、SSE chunk、XML 标签、原生 SDK 对象）转化为 Agent 内部统一消费的标准化消息，并从中提取 content、tool_calls、reasoning、finish_reason、usage 等语义单元的过程。它决定下一步是执行工具还是向用户交付最终回复。

## 为什么需要

- 不同 provider 对 tool call、reasoning、usage 的封装截然不同。
- 流式响应中 delta 边界可能破坏标签状态（如 `<thinking>` 被拆成两个 delta）。
- 本地模型可能输出非法 JSON、trailing comma、Python `None` 等，需要容错解析。
- reasoning content 若泄漏到用户可见回复或污染上下文，会导致体验问题和成本膨胀。

## 核心组成

| 组件 | 作用 |
|---|---|
| Transport 归一化 | 把 provider 原始响应转成统一 `NormalizedResponse` |
| Tool call 提取 | 从不同 schema 中提取 name/arguments/call_id |
| Reasoning 提取 | 识别并隔离 reasoning/thinking 内容 |
| JSON 修复 | 对非法 tool-call 参数做容错修复 |
| 消息序列修复 | 修复 orphan tool_call/tool 消息配对 |
| 流式状态机 | 跨 delta 维护状态，避免 per-delta 正则破坏边界 |

## Provider 差异示例

| Provider | Tool call | Reasoning |
|---|---|---|
| OpenAI | `message.tool_calls[].function` | `reasoning_content` |
| Anthropic | `content_blocks` 中 `tool_use` | `thinking` block / `reasoning_details` |
| Gemini | `parts[].functionCall` | 自定义字段 |
| DeepSeek | 类 OpenAI | `reasoning_content`（tool-call 轮次必须回传） |

## 设计模式

- **Transport 层抽象**：每个 provider 一个 Transport 类，核心循环只依赖 `NormalizedResponse`。
- **双轨 reasoning**：内部统一用 `reasoning` 字段；API 回传时按 provider 要求转换。
- **流式 scrubber**：维护跨 delta 状态机处理 `<thinking>` 等标签。
- **防御性修复**：多重 fallback，最终用空对象/空参数避免会话崩溃。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 抽象层 | `Transport` 类归一化为 `NormalizedResponse` | Provider 子类直接返回标准结构 | 流式状态机处理 delta | AI SDK 流式消费 |
| Reasoning 处理 | 双轨存储：内部 `reasoning` + 按 provider 回传 | Think 块剥离下沉为全局工具 | 状态机跨 chunk 跟踪 ` ici` 标签 | AI SDK 原生事件路由 |
| 工具参数修复 | 5 层修复策略，最终回退 `"{}"` | 先 cast 再 validate | Schema 扁平化 + 参数别名兼容 | `experimental_repairToolCall` 修复/降级 |
| 流式 delta 处理 | `StreamingThinkScrubber` 跨 delta 状态机 | 工具结果截断到 16K | `deltaBuffer` 前缀比较保证单调输出 | `for await...of stream.fullStream` |
| 消息序列修复 | 三重防护修复 orphan tool | error 响应不进入历史 | 流式状态重置 + 代码块保护 | 工具修复 + Doom Loop 检测 |
| 独特设计 | 多 provider reasoning 五层回传 | Think 剥离在 loop 层统一处理 | 代码块保护防止误删标签 | Doom Loop 运行时检测 |

## 与相关概念的关系

- 输出解析的上游是 [[orchestration-loop]] 中的 LLM 调用。
- 解析出的 tool_calls 交给 [[agent-tool-system]] 执行。
- reasoning 内容的处理与 [[prompt-building-for-agents]] 的模型家族特化有关。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `agent/transports/` 和 `think_scrubber` 实现。其他框架待补充。
