---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, sub-agent, multi-agent, delegation]
---

# Sub-Agent Orchestration（子 Agent 编排）

## 定义

子 Agent 编排是把复杂任务拆分成一个或多个受限的子 Agent 实例执行，并把子 Agent 的最终摘要回传给父 Agent 的能力。子 Agent 拥有独立的上下文、工具集、预算和生命周期，父 Agent 只看到结果，不暴露中间推理和工具调用细节。

## 为什么需要

- 复杂子任务会迅速膨胀父 Agent 的上下文窗口，触发频繁压缩并丢失早期决策。
- 子任务可能调用有副作用的工具（如 `memory.add`、`send_message`），需要与父 Agent 的能力隔离。
- 多个子任务可以并行执行，减少总体等待时间。
- 用户中断需要级联到所有嵌套子任务，否则会出现「父已停、子还在跑」的失控。

## 核心组成

| 组件 | 作用 |
|---|---|
| 委派入口 | 父 Agent 触发子 Agent 的 mechanism（如 `delegate_task` 工具） |
| 子 Agent 工厂 | 创建受限的临时 AIAgent 实例 |
| 工具集裁剪 | 子 Agent 只能访问父 Agent 允许的工具子集 |
| 副作用隔离 | 切断可能污染父/跨会话状态的工具 |
| 并发执行 | ThreadPool/ProcessPool 并行运行多个子任务 |
| 中断级联 | 父 Agent 中断时递归取消所有子 Agent |
| 结果汇总 | 把子 Agent 的 summary/cost/tokens 返回给父循环 |

## 设计权衡

| 权衡 | 选项 A | 选项 B |
|---|---|---|
| 子 Agent 形态 | 同框架临时实例 | 独立进程/服务 |
| 上下文策略 | 完全隔离，只回 summary | 共享部分历史 |
| 并发粒度 | 任务级并行 | 轮次级并行 |
| 深度限制 | 硬限制 max depth | 无限制 |
| 工具继承 | 交集裁剪 | 完全继承 |

生产级系统通常采用「同框架临时实例 + 完全隔离 + 任务级并行 + 硬深度限制 + 交集裁剪」的组合，兼顾实现简单性和可控性。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 触发方式 | LLM 主动调用 `delegate_task` 工具 | LLM 主动调用子 Agent 工具 | LLM 主动调用子 Agent 工具 | `TaskTool` 创建 child session |
| Agent 形态 | 同框架临时 `AIAgent` 实例 | 独立沙箱推理线程（无 message/spawn） | 独立 session | 独立 child session |
| 上下文策略 | 完全隔离，只回 summary | 完全隔离，system 消息注入结果 | 独立 session，push 交付 | 独立 session，内联执行 subtask |
| 并发 | ThreadPoolExecutor 并发子 Agent | 后台运行不阻塞用户 | 事件驱动 push | 主循环直接执行 |
| 工具继承 | 父工具集交集 + 黑名单剥离 5 个 | 只注册 filesystem/shell/web | 独立 session | 继承但禁用 todo 工具 |
| 中断/深度 | 深度限制 + 中断级联 | 15 轮限制 | 基于 `spawnedBy` 链的深度限制 | task_id 可恢复 |
| 结果交付 | 同步阻塞，父循环等 summary | MessageBus system 消息注入 | 事件驱动 announce | 内联 subtask part 执行 |
| 适用场景 | 单任务内子任务外包 | 耗时任务后台运行 | 复杂任务分解 | 代码探索/重构子任务 |

## 与相关概念的关系

- 子 Agent 编排是 [[multi-agent-collaboration]] 的一种实现形态。
- 子 Agent 内部仍然运行自己的 [[orchestration-loop]]。
- 父 Agent 通过 [[agent-tool-system]] 暴露 `delegate_task` 等委派工具。
- 中断级联依赖 [[error-handling]] 和 [[orchestration-loop]] 的中断机制。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `delegate_task` 实现。其他框架待补充。
