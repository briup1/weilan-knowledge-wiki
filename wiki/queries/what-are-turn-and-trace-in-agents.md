---
type: query
created: 2026-07-26
updated: 2026-07-26
sources: [agent-turn, agent-trace, hermes-agent, hermes-agent-state-management, hermes-agent-validation-loop, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent, turn, trace, observability, faq]
---

# Agent 中的 Turn 和 Trace 是什么？

## 问题

我想了解 agent 中的 turn 和 trace 的概念。

## 答案

### 1. Turn 是什么？

**Turn** 是 Agent 与用户（或下游系统）之间**一次完整交互回合**的业务语义单位。

- 以用户输入开始，以 Agent 最终响应结束。
- 中间可能包含**多次 LLM 调用、多次工具调用、多轮 ReAct 循环**。
- 一个 Turn 不等同于一次 HTTP 请求，也不等同于一次 LLM 调用。

Turn 是 Agent 系统中最重要的「预算边界」和「状态边界」：
- 限流、计费、token 预算通常按 Turn 控制。
- 用户感知到的延迟是 Turn 级别的延迟。
- Turn 结束时通常会做状态持久化、上下文压缩、记忆归档。

详见概念页：[[agent-turn]]

### 2. Trace 是什么？

**Trace** 是一次 Agent 执行的**结构化、可观测记录**，通常表示为树状的 Span 结构：
- **Trace** = 一次完整工作流（通常对应一个 Turn）。
- **Span** = 一个工作单元（一次 LLM 调用、一次工具调用、一次检索）。
- **Event** = Span 内发生的离散事件（如参数修正、错误触发）。

Trace 与普通日志的区别：
- 树状结构，有父子关系。
- 每个 Span 有明确的起止时间、延迟、Token 消耗。
- 可以可视化为瀑布图或火焰图。
- 适合与 OpenTelemetry、LangSmith、W&B 等可观测平台集成。

详见概念页：[[agent-trace]]

### 3. Turn 和 Trace 的关系

```
一个 Session 包含多个 Turn
一个 Turn 对应一个顶层 Trace
一个 Trace 包含多个 Span（LLM Call、Tool Call、Retrieval、Validation）
```

简单来说：
- **Turn 是业务交互单位**（用户视角）。
- **Trace 是技术执行记录**（开发者视角）。
- 两者通常一一对应，但一个复杂 Turn 可能产生多个相关 Trace（例如子 Agent 委派）。

### 4. 四框架中的体现

| 框架 | Turn 边界 | Trace/可观测性 |
|---|---|---|
| **Hermes** | `run_conversation()` 一次调用；有 `_api_call_count` 和 `_halt_decision` | 以预算、中断计数、工具集版本为主 |
| **nanobot** | `_save_turn()` 标记结束；以 user 轮次为最小单元 | 轻量日志事件 |
| **OpenClaw** | `Run` 下的一次 `Attempt` 成功返回 payload | 分层结构天然可映射为 Span |
| **OpenCode** | `SessionPrompt.loop` 一次完整迭代 | AI SDK 流式事件可直接转化为 Trace |

## 相关概念

- [[agent-turn]] —— Turn 的完整定义、生命周期和框架实现
- [[agent-trace]] —— Trace 的 Span 结构、Agent 特殊性、设计建议
- [[orchestration-loop]] —— Turn 内部由编排循环驱动
- [[state-management]] —— Turn 结束是状态持久化的边界
- [[error-handling]] —— Trace 是定位错误现场的关键
