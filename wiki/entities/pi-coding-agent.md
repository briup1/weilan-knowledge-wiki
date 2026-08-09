---
type: entity
created: 2026-08-05
updated: 2026-08-05
sources: [pi-agent-runtime-event-flow, pi-agent-loop-and-turn, pi-provider-unified-event-protocol, pi-tool-call-lifecycle, pi-tool-registration-and-extension, pi-custom-tools-and-extension, pi-session-system]
tags: [pi, coding-agent, agent-harness, typescript, open-source]
---

# Pi Coding Agent

Pi 是一个开源 LLM Agent Harness / Coding Agent 系统，将模型访问、编排循环、工具执行、事件、Session 持久化和 Extension 组织成相互解耦的层。

## 核心分层

```text
Application / SDK / CLI
  → Coding Agent：Session、内置工具、ResourceLoader、Extension
  → Agent Core：Loop、Runtime Turn、Tool execution、统一事件
  → AI / Provider：模型注册、wire protocol 适配、流式消息归一化
  → Model Provider
```

## 关键抽象

| 抽象 | 职责 |
|---|---|
| Agent loop | 驱动模型、工具、steering 和 follow-up |
| Runtime Turn | assistant 的一次行动机会及其工具结果 |
| Runtime event stream | 暴露 Agent、Turn、消息和工具生命周期 |
| Provider adapter | 将不同 wire protocol 转成统一消息事件 |
| ToolDefinition / Registry | 汇总并筛选模型可见工具 |
| Extension | 注册工具、命令、Provider 和生命周期 Hook |
| SessionEntry tree | append-only 保存完整、可分支的会话事实 |
| Context projection | 从当前 leaf 投影模型可见消息 |
| Compaction node | 用摘要 checkpoint 替代早期投影视图而不删除历史 |

## 工具系统

Coding Agent 提供 `read`、`bash`、`edit`、`write`、`grep`、`find`、`ls` 七个内置工具，也接受 Extension 和 SDK `customTools`。三种来源汇入同一个 Registry，再经过准入和 active tools 选择进入 `agent.state.tools`。

## 设计特征

- 核心机制与应用策略分离，例如 Core 提供 `beforeToolCall`，但默认权限策略由外层决定。
- Provider 差异在边界归一化，Agent loop 不直接处理厂商 SSE 细节。
- Session 存储与模型上下文分层，持久化 Entry 树可派生多个上下文视图。
- 事件流贯穿 UI、Trace、预算、中断和工具进度。
- Extension 和 SDK 工具复用同一 ToolDefinition，不形成两套执行系统。

## 关联知识

- [[pi-agent-runtime-architecture]]
- [[agent-runtime-event-stream]]
- [[agent-turn]]
- [[provider-protocol-normalization]]
- [[tool-call-lifecycle]]
- [[agent-extension-system]]
- [[agent-session-storage-and-context-views]]
