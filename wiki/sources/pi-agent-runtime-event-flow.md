---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-agent-runtime-event-flow.md
tags: [pi, agent-runtime, event-stream, tool-call, turn]
---

# Pi 系列 01：用最小例子看 Agent Runtime 的事件流

## 来源信息

- 标题：Pi 系列 01｜用最小例子看 agent runtime 的事件流
- 公众号：CodeAgent
- 发布时间：2026-05-31
- 原始链接：见归档原文

## 摘要

Pi 把一次 Agent 运行拆成可订阅的类型化事件。模型请求工具时，runtime 执行工具、把结果回填上下文并再次调用模型，直到不存在真实的工具调用或其他继续条件。事件流同时暴露 Agent、Runtime Turn、消息流和工具执行四个层次，是 UI 渲染、Trace、预算、中断和 checkpoint 的共同观测接口。

## 事件骨架

```text
agent_start
  ├─ turn_start
  │    ├─ message_start
  │    ├─ message_update
  │    │    ├─ text_delta
  │    │    ├─ thinking_delta
  │    │    └─ toolcall_delta
  │    ├─ message_end
  │    ├─ tool_execution_start
  │    ├─ tool_execution_update
  │    ├─ tool_execution_end
  │    └─ turn_end
  ├─ ...下一 Runtime Turn
  └─ agent_end
```

## 核心主张

1. **Agent loop 的最小骨架是“模型 → 工具 → 模型”。** 工具结果必须回填上下文，模型才能基于观察继续决策。
2. **事件是运行时契约，不只是调试日志。** UI、Trace、进度展示、中断和预算控制都可以订阅同一事件流。
3. **工具参数也会流式到达。** `toolcall_delta` 逐段累积 JSON 参数，不能假设工具调用在单个 chunk 中完整出现。
4. **`turn_end` 与 `agent_end` 边界不同。** 前者结束一次 assistant 行动机会，后者结束整个 run。
5. **继续执行以真实内容为准。** `stopReason` 可用于解释，但源码最终检查 assistant message 中是否存在 tool call，以及工具批次、steering、follow-up 和停止钩子的结果。

## 工程意义

- UI 可以按 Runtime Turn 分组渲染消息和工具状态。
- Trace 可以直接把 message/tool/turn 事件映射为 Event/Span。
- 预算和中断应挂在稳定的 `turn_end` 等边界，而不是散落在 provider chunk 解析中。
- Provider 差异应在事件进入 Agent loop 前归一化，参见 [[provider-protocol-normalization]]。

## 关联知识

- [[pi-coding-agent]]
- [[agent-runtime-event-stream]]
- [[agent-turn]]
- [[orchestration-loop]]
- [[agent-trace]]
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

- [完整原文](../../raw/archive/pi-agent-runtime-event-flow.md)
