---
type: concept
created: 2026-08-05
updated: 2026-08-08
sources: [pi-tool-call-lifecycle, pi-tool-registration-and-extension, pi-custom-tools-and-extension, pi-agent-loop-and-turn, hermes-agent-tool-system, hermes-agent-validation-loop, ai-agent-book-async-agent-experiment]
tags: [agent, tool-call, lifecycle, validation, error-recovery]
---

# ToolCall Lifecycle

ToolCall Lifecycle 描述模型产生工具调用意图后，Agent Harness 如何完成查找、校验、授权、执行、观测、错误转换和上下文回填。核心边界是：**模型提出意图，Runtime 拥有执行权。**

## 标准流程

```text
AssistantMessage.toolCall
  → 调度：串行 / 并行
  → 准备
       ├─ lookup：工具是否存在
       ├─ repair/coerce：参数修正
       ├─ validate：Schema 校验
       └─ authorize：beforeToolCall
  → execute(args, onUpdate)
       ├─ 同步完成 → afterToolCall → ToolResultMessage
       └─ 异步接受 → JobAccepted(job_id) → 后台执行
                                      → CompletionEvent
                                      → ToolResult / 恢复事件
  → context
  → 下一 Runtime Turn
```

## 同步与异步分叉

同步或异步不应由 Agent 根据工具名称猜测，而应由 ToolDefinition 声明执行能力，再由 Runtime 根据等待预算和部署策略作最终选择：

- **同步工具**：当前 Runtime Turn 持有执行权，完成后直接产生 ToolResult。
- **异步工具**：当前调用只产生 `JobAccepted`；Runtime 保存 `tool_call_id`、`job_id` 和父任务关系后释放执行槽。
- **完成恢复**：后台任务终态事件进入统一 inbox，按恢复策略触发新 Turn 或父任务汇合。

异步启动结果不能伪装成最终 ToolResult。它表达的是“任务已接受”，真实业务结果必须通过同一 `job_id` 的终态事件补齐。详细协议见 [[async-tool-execution-and-wakeup]]。

## 结果模型

以下情况都应产生与原 ToolCall id 配对的 ToolResult，而不是让可恢复错误逃逸出 loop：

- 成功执行。
- 工具不存在。
- 参数解析或 Schema 校验失败。
- 权限策略阻止执行。
- Handler 抛出异常或返回失败。

这样模型能基于失败原因修改参数、选择其他工具或解释限制。

## 关键设计决策

- **工具作者与 Loop 分工**：工具内部可正常抛异常，Loop 统一捕获、脱敏并转为 ToolResult。
- **机制与策略分离**：Core 提供 hook，应用层决定权限规则、人工审批和审计策略。
- **流式进度与最终结果分离**：执行 update 服务实时 UI，ToolResult 服务推理和持久化。
- **配对不可破坏**：上下文裁剪和压缩必须保持 ToolCall 与 ToolResult 成对，避免孤儿消息。
- **并行执行受语义约束**：只读、互不依赖的调用可并行；有副作用或顺序依赖的调用应串行。

## 关联概念

- [[agent-tool-system]]
- [[validation-loop]]
- [[error-handling]]
- [[agent-runtime-event-stream]]
- [[orchestration-loop]]
- [[context-management]]
- [[async-tool-execution-and-wakeup]]
