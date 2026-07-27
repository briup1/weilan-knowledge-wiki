---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度01-编排循环.md
tags: [hermes-agent, orchestration-loop, agent-architecture]
---

# Hermes Agent：编排循环

## 摘要

Hermes Agent 的编排循环是一个**带预算控制、可中断、支持并发工具执行的 ReAct 风格主循环**。核心职责是在 LLM 推理与工具执行之间反复迭代，直到任务完成、预算耗尽或用户主动中断。关键源码位于 `run_agent.py:11158` 附近。

## 核心主张

1. **双保险预算控制**：`max_iterations` + `IterationBudget` 防止无限循环，预算耗尽后还有 `_budget_grace_call` 允许一次无工具的体面总结。
2. **线程级可中断**：通过 `_set_interrupt(tid)` + `_interrupt_requested` 标志位，把中断精确到单个 Agent 会话，不影响网关下的其他会话。
3. **并发工具执行**：对独立工具调用使用 `ThreadPoolExecutor(max_workers=8)` 并行执行，由静态白名单 `_should_parallelize_tool_batch()` 决策。
4. **Steer 机制**：用户 `/steer` 指令不中断循环，而是把文本注入最后一个 tool 结果，保持 role alternation 合法。
5. **API 调用隔离**：每次请求新建 worker-local client，中断时只关闭该次请求的 client，避免污染共享连接。

## 关键设计

- `IterationBudget` 线程安全、可退款（`refund()`），父子 Agent 各自独立预算。
- `_interruptible_api_call()` 在独立后台线程中执行 API 调用，主循环通过 `join(timeout=0.3)` 轮询检测中断。
- 每次 API 调用前复制 `api_messages` 并做 sanitize：修复孤儿 tool_call、合并相邻 user 消息，保持持久化历史与 API 请求解耦。

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度01-编排循环.md)
