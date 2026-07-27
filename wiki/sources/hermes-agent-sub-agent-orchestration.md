---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度11-子Agent编排.md
tags: [hermes-agent, sub-agent-orchestration, multi-agent, delegation]
---

# Hermes Agent：子 Agent 编排

## 摘要

Hermes 通过 `delegate_task` 把「目标 + 受限工具集 + 隔离终端会话」打包成一个**临时的、同步阻塞的子 AIAgent 实例**，让父代理在不污染自身上下文的前提下并行/串行地把「会消耗大量中间状态的子任务」外包出去；父代理拿到的只是子代理写回的最终摘要。关键源码位于 `tools/delegate_tool.py`、`run_agent.py:10358` 附近。

## 核心主张

1. **上下文隔离**：子任务的中件 tool calls/reasoning 不会进入父上下文，避免子任务导致父上下文窗口爆炸。
2. **工具能力切断**：`DELEGATE_BLOCKED_TOOLS` 明确切断 `memory`、`send_message`、`clarify`、`execute_code` 等可能产生跨会话副作用的能力。
3. **并发执行**：通过 `ThreadPoolExecutor` 并发运行多个子 Agent，父循环可统一监控并响应中断。
4. **中断级联**：`child.interrupt(message)` 递归打断嵌套子 Agent，用户 Ctrl+C 可穿透整个子任务树。
5. **深度限制**：`depth >= max_spawn` 时直接返回错误，防止无限递归派生。
6. **角色降级**：`orchestrator` 角色在深度或配置不满足时静默退化为 `leaf`，保证系统不崩溃。

## 子 Agent 生命周期

```
delegate_task(goal | tasks)
  ├─ 准入控制（depth/spawn_paused）
  ├─ 解析凭证、保存父工具名
  ├─ 为每个 task 构建受限 child AIAgent
  ├─ ThreadPoolExecutor 并发执行
  │   └─ 监控 parent._interrupt_requested，取消未完成子任务
  └─ 汇总 summary/cost/tokens/tool_trace 返回父循环
```

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度11-子Agent编排.md)
