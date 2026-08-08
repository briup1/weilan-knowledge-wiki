---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-tool-call-lifecycle.md
tags: [pi, tool-call, validation, hooks, tool-result]
---

# Pi 系列 04：一个 ToolCall 的一生

## 来源信息

- 标题：Pi 系列 04｜Tool 系统（上）：一个 toolCall 的一生
- 公众号：CodeAgent
- 发布时间：2026-06-11
- 原始链接：见归档原文

## 摘要

模型不会直接执行工具，只会生成结构化 ToolCall 意图。Pi 的 harness 识别这些意图后进行调度、工具查找、参数修正、Schema 校验、执行前权限钩子、`execute()`、执行后钩子，再把结果统一转换成 `ToolResultMessage` 回填上下文。可恢复错误也被转换为模型可读结果，让模型在下一 Runtime Turn 自我修正。

## 生命周期

```text
模型生成 ToolCall 意图
  → Harness 从 AssistantMessage 提取 toolCall
  → 选择串行 / 并行调度
  → prepareToolCall
       ├─ 查找工具是否存在
       ├─ 修正参数
       ├─ Schema 校验
       └─ beforeToolCall：权限与策略钩子
  → tool.execute(args, onUpdate)
       └─ tool_execution_update
  → afterToolCall
  → ToolResultMessage
  → 回填 context
  → 下一 Runtime Turn
```

## 核心主张

1. **意图与执行必须分层。** 模型只能请求工具，runtime 才拥有查找、授权、执行和记录结果的责任。
2. **所有执行路径都应产出 ToolResult。** 成功、工具不存在、参数非法、权限拦截和执行异常都应转成模型能理解的结果。
3. **工具作者可以正常抛异常。** Agent loop 在统一边界捕获并转换，避免每个工具重复实现错误包装。
4. **可恢复错误不应直接杀死 loop。** 把失败原因回填给模型，模型可以改参数、换工具或向用户说明。
5. **机制与策略分离。** Core 提供 `beforeToolCall` 拦截点；是否审批、如何授权由应用或 Extension 决定。
6. **执行事件与消息结果职责不同。** `tool_execution_update` 服务实时进度，最终 `ToolResultMessage` 服务后续推理和持久化。

## 关联知识

- [[pi-coding-agent]]
- [[tool-call-lifecycle]]
- [[agent-tool-system]]
- [[validation-loop]]
- [[error-handling]]
- [[orchestration-loop]]
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

- [完整原文](../../raw/archive/pi-tool-call-lifecycle.md)
