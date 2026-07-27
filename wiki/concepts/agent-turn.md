---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, hermes-agent-state-management, hermes-agent-validation-loop, hermes-agent-sub-agent-orchestration, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent, turn, conversation, orchestration-loop, state-management, budget]
---

# Agent Turn

Agent Turn 是 Agent 与用户（或另一个系统）之间**一次完整交互回合**的抽象单位。一次 Turn 通常以用户输入开始，以 Agent 最终响应结束，但中间可能包含多轮内部 ReAct 循环、多次 LLM API 调用、多个工具调用，甚至子 Agent 委派。

## 定义

> 一个 **Turn** = 一条用户输入 → Agent 内部推理/工具执行 → 最终返回给用户/下游系统的响应。

它不等同于一次 LLM 调用，也不等同于一次 HTTP 请求。一个 Turn 是**业务语义上的最小交互单元**。

## 一次 Turn 内部的生命周期

```
用户输入
   │
   ▼
上下文组装（system prompt + 历史 + 记忆 + 工具 schema）
   │
   ▼
ReAct 推理循环 ───→ LLM 调用 → tool calls → 工具执行 → 结果回注
   │                    ↑______________________________↓
   ▼
收尾/验证（halt decision、budget check、状态持久化）
   │
   ▼
最终响应（text / tool result / event stream）
```

## 与相关概念的区别

| 概念 | 含义 | 与 Turn 的关系 |
|---|---|---|
| **HTTP Request** | 网络层请求 | 一个 Turn 可能对应一次或多次 HTTP 请求 |
| **LLM Call** | 对模型 API 的一次调用 | 一个 Turn 内可能有多个 LLM Call |
| **ReAct Step** | 一次推理-行动循环 | 一个 Turn 由多个 Step 组成 |
| **Trace** | 一次执行的可观测记录 | 一个 Turn 通常对应一个顶层 Trace/Span |
| **Session** | 多次 Turn 的集合 | 一个 Session 包含多个 Turn |

## 为什么需要 Turn 这个抽象

1. **计费与限流**：限制的是「一次用户请求里最多调多少 token/多少次 API」，而不是每次 LLM 调用。
2. **用户体验**：用户以 Turn 为单位感知延迟。中间的工具调用和再推理用户不应直接看到。
3. **状态边界**：一个 Turn 结束时会做持久化、压缩、归档，让 Session 在下次启动时可恢复。
4. **预算管理**：Turn 级预算（iteration budget、token budget、tool budget）防止单次请求失控。

## 四框架中的 Turn 设计

| 框架 | Turn 的边界在哪里 | 特点 |
|---|---|---|
| **Hermes** | `run_conversation()` 的一次调用 | 有 `max_iterations`、`_api_call_count` 等 Turn 级预算；`_halt_decision` 负责收尾 |
| **nanobot** | `_save_turn()` 标记一次 Turn 结束 | 以 user 轮次为最小单元；会剥离 runtime context 后再持久化 |
| **OpenClaw** | `Run` 下的一次 `Attempt` 成功返回 payload | 分层：Gateway → Lane → Run → Attempt → Stream；Turn 的边界接近 Run/Attempt |
| **OpenCode** | `SessionPrompt.loop` 的一次完整迭代 | 流式循环内，一个 Turn 可能包含 compaction、subtask 等系统级任务 |

## 关键设计决策

- **Turn 内是否允许用户中途干预？** Hermes 有 `/steer`，nanobot 有 `/stop`，OpenClaw 有 steer/queue 双模式。这影响的是「长 Turn 中用户插话」的能力。
- **Turn 失败是否写入历史？** nanobot 选择 `finish_reason=="error"` 不写入历史，防止毒化后续 Turn。这是 Turn 级错误隔离的重要实践。
- **Turn 与压缩的关系**：当一次 Turn 导致上下文超过阈值时，是在 Turn 内做 compaction，还是 Turn 结束后压缩？各框架选择不同。

## 相关概念

- [[orchestration-loop]] —— Turn 内部由编排循环驱动
- [[agent-trace]] —— 一个 Turn 通常对应一个顶层 Trace
- [[state-management]] —— Turn 结束是状态持久化的关键边界
- [[validation-loop]] —— Turn 收尾前 often 经过验证/护栏检查
- [[context-management]] —— 每次 Turn 开始都需要重新组装上下文

## 相关来源

- [[hermes-agent-state-management]] —— Hermes 的 Turn 级计数与持久化
- [[hermes-agent-validation-loop]] —— Turn 收尾的 halt 决策
- [[nanobot-framework-analysis]] —— `_save_turn()` 的消毒与归档逻辑
- [[openclaw-framework-analysis]] —— Run/Attempt 的层级边界
- [[opencode-framework-analysis]] —— 流式 Turn 内的任务处理
