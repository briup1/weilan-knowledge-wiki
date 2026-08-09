---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-provider-unified-event-protocol.md
tags: [pi, provider, protocol-normalization, streaming, events]
---

# Pi 系列 03：Provider 抽象与统一事件协议

## 来源信息

- 标题：Pi 系列 03｜Provider 抽象与统一事件协议
- 公众号：CodeAgent
- 发布时间：2026-06-09
- 原始链接：见归档原文

## 摘要

Pi 将 Provider 的厂商身份与 API wire format 分开建模，再按 `model.api` 选择协议翻译器。Anthropic、OpenAI、Gemini 等不同 SSE/chunk 被累积并转换为统一的 `AssistantMessageEvent`，使上层 Agent loop 只依赖稳定事件语义，而不直接理解每家 Provider 的原始协议。

## 归一化链路

```text
Provider 原始 SSE / chunk
  → 根据 model.api 选择协议翻译器
  → 解析 text / thinking / tool-call 增量
  → 累积 partial AssistantMessage
  → 统一 AssistantMessageEvent
       start
       text_delta
       thinking_delta
       toolcall_delta
       done | error
  → Agent loop / UI / Trace
```

## 核心主张

1. **`api` 与 `provider` 是两个维度。** `api` 表示 wire format，`provider` 表示厂商、认证和兼容配置；多个 Provider 可以复用同一种 API 协议。
2. **统一事件隔离上层与厂商差异。** Agent loop 只消费 `start/delta/done/error`，新增兼容 Provider 通常不需要改编排逻辑。
3. **事件同时携带 delta 与 partial。** delta 便于流式渲染，partial 提供截至当前时刻的累积消息，降低每个消费者自行拼接的复杂度。
4. **工具参数需要增量拼接。** Provider 的 tool call 名称、id、参数片段可能分散在多个 chunk 中，翻译层必须维护状态。
5. **运行期错误也进入统一终止事件。** 请求或解析失败应通过 `error` 完成流的统一收尾；注册、模型查找等流创建前错误仍可直接抛出。

## 设计边界

- Provider adapter 负责协议解析与统一事件，不负责 Agent 是否继续运行。
- Agent loop 根据完成消息中的真实 tool call 做控制流判断。
- Tool schema 的 Provider 兼容转换属于请求侧归一化，与响应侧事件归一化互补。

## 关联知识

- [[pi-coding-agent]]
- [[provider-protocol-normalization]]
- [[agent-runtime-event-stream]]
- [[output-parsing]]
- [[error-handling]]
- [[pi-agent-runtime-architecture]]

## 本系列其他文章

- [[pi-agent-runtime-event-flow|01｜Runtime 事件流]]
- [[pi-agent-loop-and-turn|02｜Agent loop 与 turn]]
- [[pi-provider-unified-event-protocol|03｜Provider 与统一事件协议]]
- [[pi-tool-call-lifecycle|04｜ToolCall 的一生]]
- [[pi-tool-registration-and-extension|05｜工具供给、暴露与 Extension]]
- [[pi-custom-tools-and-extension|06｜customTools 与 Extension 实战]]
- [[pi-session-system|07｜Session 系统]]

## 原始文件

- [完整原文](../../raw/archive/pi-provider-unified-event-protocol.md)
