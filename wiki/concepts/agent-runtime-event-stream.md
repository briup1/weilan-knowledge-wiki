---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-agent-runtime-event-flow, pi-agent-loop-and-turn, pi-provider-unified-event-protocol, pi-tool-call-lifecycle]
tags: [agent, runtime, event-stream, observability, streaming]
---

# Agent Runtime Event Stream

Agent Runtime Event Stream 是 Agent Harness 对执行过程提供的**类型化、流式生命周期协议**。它把一次 run 中的 Agent 边界、Runtime Turn、模型消息和工具执行统一暴露给 UI、Trace、预算、中断和插件系统。

## 分层事件

```text
Agent：agent_start ───────────────────────────── agent_end
  Turn：turn_start ───────────────────────────── turn_end
    Message：message_start → message_update* → message_end
      Delta：text_delta / thinking_delta / toolcall_delta
    Tool：tool_execution_start → update* → end
```

## 设计原则

1. **事件必须有明确层级和成对边界。** 否则 UI 无法稳定分组，Trace 也无法构建父子 Span。
2. **增量与累积状态同时可用。** delta 用于低延迟渲染，partial 用于消费者随时读取完整当前消息。
3. **事件不能替代持久化事实。** Runtime Event 适合在线观察；长期恢复仍应保存消息、Session Entry 或 Trace。
4. **Provider 事件先归一化再进入 Runtime。** 上层不应依赖厂商专用 chunk 类型。
5. **控制流读取最终语义对象。** 是否继续 Agent loop 应检查完整 AssistantMessage 中的 ToolCall，而不是依据某个增量事件猜测。

## 典型用途

- UI：按 Runtime Turn 渲染文本、思考、工具参数和执行进度。
- Observability：映射为 Trace → Span → Event。
- Control：在 `turn_end` 执行预算检查、中断和 checkpoint。
- Extension：订阅 context、tool_call 或消息生命周期事件。

## 关联概念

- [[agent-turn]]
- [[agent-trace]]
- [[provider-protocol-normalization]]
- [[tool-call-lifecycle]]
- [[orchestration-loop]]
