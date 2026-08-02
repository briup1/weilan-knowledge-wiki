---
type: concept
created: 2026-07-26
updated: 2026-08-03
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, orchestration-loop, agent-control-flow]
---

# Orchestration Loop（编排循环）

## 定义

编排循环是 Agent 在 **LLM 推理 → 工具执行 → 观察结果 → 再次推理** 之间反复迭代的主控制流，也是 [[react-pattern|ReAct]] 等模式运行的基础设施。它是 Agent 从「单次问答」进化到「自主任务执行」的最小必要结构。

## 为什么需要

- 没有循环，模型只能做一次性生成，无法根据工具反馈调整策略。
- 长任务需要多轮迭代；循环提供了持续推进任务的机制。
- 循环内必须嵌入预算、中断、错误恢复等控制机制，否则会出现无限调用、费用爆炸、用户体验断裂。

## 核心组成

一个生产级编排循环至少包含：

| 组件 | 作用 | 相关概念 |
|---|---|---|
| 迭代计数/预算 | 防止无限循环 | [[orchestration-loop]] |
| 中断机制 | 允许用户或系统优雅停止 | [[orchestration-loop]] |
| 工具调用解析 | 把 LLM 输出转成可执行动作 | [[output-parsing]] |
| 工具执行 | 同步或异步调用外部能力 | [[agent-tool-system]] |
| 结果回灌 | 把工具结果重新放入上下文 | [[context-management]] |
| 终止判断 | 任务完成、预算耗尽、用户中断 | [[error-handling]] |

## 设计权衡

| 权衡 | 选项 A | 选项 B | 适用场景 |
|---|---|---|---|
| 并发 | 独立工具并行执行 | 全部串行 | 网络/文件 IO 多时并行；有依赖时串行 |
| 中断粒度 | 线程/进程级精确中断 | 全局事件 | 多会话网关选精确中断；单用户 CLI 可选全局 |
| 预算 | 迭代次数 + token 双保险 | 单一计数器 | 生产环境推荐双保险 |
| Steer/干预 | 注入工具结果 | 插入新 user 消息 | 保持 role alternation 合法时选工具结果 |

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 并发模型 | ThreadPool 并发工具，线程级精确中断 | 全局 `asyncio.Lock` 串行处理 | Session Lane + Global Lane 双层队列 | `while(true)` 主循环，流式优先 |
| 中断机制 | `_set_interrupt(tid)` 标志位 + 关闭 worker-local client | `/stop` 走同一 inbound 队列，1s 超时轮询 | in-process 重启 + restartResolver | `AbortSignal` Web 标准 |
| 终止条件 | `max_iterations` + `IterationBudget` + `_budget_grace_call` | 默认 40 轮，`has_tool_calls` 为假终止 | Compaction 超时快照回退 + 模型降级 | 三级分类终止 |
| 错误隔离 | 单工具失败降级为字符串 | `finish_reason=="error"` 不写入历史 | 多种检测器 + 运行时阻断 | Doom Loop 检测 |
| 独特设计 | grace call 体面总结 | 派发异步、执行串行，保证 `/stop` 可插队 | macOS TCC 权限保留的 in-process 重启 | 流式事件路由 |

## 与相关概念的关系

- 编排循环内部会调用 [[agent-tool-system]] 执行工具。
- 最常见的编排模式是 [[react-pattern|ReAct]]：每轮迭代让模型输出 Thought → Action → Observation。
- 与 ReAct 平级的另一种模式是 Plan-and-Execute（先规划再执行），后续补充。
- 每轮迭代前可能触发 [[context-management]] 做上下文压缩。
- 预算耗尽时可能调用 [[error-handling]] 的收尾策略。
- 复杂任务可拆分到 [[sub-agent-orchestration]]。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的实现：带预算控制、可中断、支持并发工具执行的 ReAct 风格主循环。其他框架（nanobot、OpenClaw、OpenCode）的实现待补充。
