---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-provider-unified-event-protocol, pi-agent-runtime-event-flow, hermes-agent-output-parsing, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent, provider, protocol, normalization, streaming]
---

# Provider Protocol Normalization

Provider Protocol Normalization 是在模型厂商协议与 Agent Runtime 之间建立稳定内部协议：将不同请求格式、SSE/chunk、完成原因、思考内容和 ToolCall 表达，转换为统一消息与事件。

## 两个独立维度

| 维度 | 含义 | 示例 |
|---|---|---|
| Provider | 厂商身份、认证、端点和兼容配置 | Anthropic、OpenAI、兼容网关 |
| API protocol | 实际 wire format | anthropic-messages、openai-completions |

同一种 API protocol 可以被多个 Provider 复用，因此不应把“厂商”和“协议解析器”硬绑定。

## 双向归一化

```text
请求侧
内部 Message / Tool schema
  → Provider adapter
  → 厂商请求格式

响应侧
厂商 SSE / chunk
  → 协议解析与增量累积
  → 统一 AssistantMessageEvent
  → Agent Runtime
```

## 统一事件最小集合

- `start`：创建流式消息容器。
- `text_delta`：普通文本增量。
- `thinking_delta`：推理内容增量。
- `toolcall_delta`：工具调用名称、id 或参数增量。
- `done`：产出完整 AssistantMessage。
- `error`：以统一终止语义收尾运行期错误。

## 设计要点

1. 保留 delta 与累积 partial，避免消费者重复实现拼接器。
2. ToolCall 参数通常是增量 JSON，必须维护跨 chunk 状态。
3. Provider 的 `stopReason` 是解释信息，不应成为 Agent loop 唯一事实来源。
4. 请求/解析期错误进入统一流终态；初始化、注册等流创建前错误可直接抛出。
5. 原始 Provider 数据可在 Trace 中保留，但不能泄漏到核心控制流接口。

## 关联概念

- [[output-parsing]]
- [[agent-runtime-event-stream]]
- [[orchestration-loop]]
- [[error-handling]]
- [[agent-tool-system]]
