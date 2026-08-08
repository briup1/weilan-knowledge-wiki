---
type: concept
created: 2026-07-26
updated: 2026-08-05
sources: [hermes-agent-orchestration-loop, hermes-agent-state-management, hermes-agent-validation-loop, hermes-agent-sub-agent-orchestration, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis, pi-agent-runtime-event-flow, pi-agent-loop-and-turn]
tags: [agent, turn, runtime-turn, business-turn, orchestration-loop, state-management, budget]
---

# Agent Turn

“Turn” 在不同 Agent 框架中存在两种常见粒度。设计和文档必须明确区分 **Business/User Turn** 与 **Runtime/Model Turn**，不能用一个未限定的 Turn 同时表达二者。

## 两种定义

### Business/User Turn

> 一条用户输入 → Agent 内部多次模型与工具迭代 → 最终面向用户或下游系统的响应。

这是产品、会话、计费、SLA 和顶层 Trace 常用的业务语义单位。

### Runtime/Model Turn

> assistant 的一次行动机会：一次模型响应，以及该响应直接触发的一批工具结果。

这是 Runtime 事件、模型调用次数、ToolCall 循环和中途 steering 常用的执行语义单位。Pi 使用的是这一粒度。

## 嵌套关系

```text
Business/User Turn
  ├─ Runtime Turn 1
  │    └─ LLM → ToolCall A → ToolResult A
  ├─ Runtime Turn 2
  │    └─ LLM → ToolCall B → ToolResult B
  └─ Runtime Turn 3
       └─ LLM → 最终文本
```

因此：

```text
1 Business Turn = 1..N Runtime Turns
1 Runtime Turn   = 1 LLM response + 0..N directly triggered ToolResults
```

## 一次 Business Turn 的生命周期

```text
用户输入
  → 上下文组装
  → Runtime Turn 循环
       LLM → ToolCalls → 工具执行 → 结果回填
       ↑___________________________________|
  → 收尾 / 验证 / 预算检查
  → 状态持久化或上下文压缩
  → 最终响应
```

## 与相关概念的区别

| 概念 | 含义 | 与 Turn 的关系 |
|---|---|---|
| HTTP Request | 网络层请求 | 一个 Business Turn 可能触发多个 Provider HTTP 请求 |
| LLM Call | 对模型 API 的一次调用 | 通常对应一个 Runtime Turn 的模型响应部分 |
| ReAct Step | 一次推理—行动—观察 | 常接近 Runtime Turn，但具体框架边界可能不同 |
| Trace | 一次执行的可观测记录 | 通常一个 Business Turn 对应顶层 Trace，Runtime Turn 对应子 Span |
| Session | 多回合历史与状态容器 | 一个 Session 包含多个 Business Turn |

## 为什么必须显式命名

1. **预算口径不同**：业务回合限制总 token/工具次数，Runtime Turn 统计每次模型行动。
2. **事件边界不同**：`turn_start/turn_end` 在 Pi 中每次模型行动都会触发，不等同于一次用户问答。
3. **UI 语义不同**：用户看到一条回答，但开发者可能需要展开其中多个 Runtime Turn。
4. **持久化边界不同**：Business Turn 常用于会话归档；Runtime Turn 常用于流式 checkpoint 和中断检查。
5. **Trace 层级不同**：混用会导致成本、延迟和错误聚合口径失真。

## Runtime Turn 的继续条件

Pi 的示例表明，是否进入下一 Runtime Turn 应以结构化事实判断：

```text
AssistantMessage 含 ToolCall？
  ├─ 是 → 执行并回填 ToolResult → 下一 Runtime Turn
  └─ 否 → 有 pending steering？
           ├─ 是 → 注入消息 → 下一 Runtime Turn
           └─ 否 → 结束当前内层循环
```

Provider 的 `stopReason` 可以记录和解释，但不应成为唯一控制流依据。

## steering 与 follow-up

- **steering**：用户在当前 Business Turn 尚未结束时补充或修正要求，应在下一 Runtime Turn 注入。
- **follow-up**：当前回答结束后排队的新任务，通常由外层循环开启新的业务处理阶段。

二者若共用一个队列，会丢失“改变当前任务”与“开始后续任务”的语义区别。

## 框架语义对照

| 框架 | Turn 粒度 | 特点 |
|---|---|---|
| Pi | Runtime/Model Turn | assistant 一次行动机会；一个 prompt 可有多个 Turn |
| Hermes | 接近 Business Turn | `run_conversation()` 内包含多次 API/工具迭代和 Turn 级预算 |
| nanobot | Business Turn | `_save_turn()` 以用户轮次做持久化边界 |
| OpenClaw | 需结合 Run/Attempt 解释 | Gateway → Run → Attempt → Stream 分层 |
| OpenCode | 依上下文而定 | `SessionPrompt.loop` 内可能包含模型、工具、压缩和 subtask |

## 命名建议

- 面向产品和会话：`user_turn`、`business_turn`。
- 面向 Runtime：`model_turn`、`runtime_turn`、`assistant_step`。
- API、事件和 Trace 字段中避免只写无限定的 `turn`。

## 相关概念

- [[orchestration-loop]]
- [[agent-runtime-event-stream]]
- [[agent-trace]]
- [[tool-call-lifecycle]]
- [[state-management]]
- [[context-management]]

## 相关来源

- [[pi-agent-loop-and-turn]] —— Pi 的 Runtime Turn、内外层循环、steering 与 follow-up
- [[pi-agent-runtime-event-flow]] —— `turn_start/turn_end` 事件边界
- [[hermes-agent-state-management]] —— Business Turn 级计数与持久化
- [[nanobot-framework-analysis]] —— `_save_turn()` 的用户回合语义
- [[openclaw-framework-analysis]] —— Run/Attempt/Stream 分层
- [[opencode-framework-analysis]] —— SessionPrompt 流式循环
