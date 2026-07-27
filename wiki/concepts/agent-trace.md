---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, openclaw-framework-analysis, opencode-framework-analysis]
tags: [observability, trace, span, agent, llm, monitoring, debugging, evaluation]
---

# Agent Trace

Agent Trace 是 Agent 一次执行过程的**结构化、可观测记录**，通常以树状结构（Trace → Span → Event）呈现。它让开发者可以追踪一次用户请求（通常对应一个 [[agent-turn]]）内部到底发生了什么：哪些 LLM 被调用了、哪些工具被执行了、每次调用的延迟和 Token 消耗是多少、错误在哪里发生。

## 定义

> **Trace** = 一次完整工作流的记录（通常对应一个 Turn）。
> **Span** = Trace 内的一个工作单元（一次 LLM 调用、一次工具调用、一次检索、一次推理）。
> **Event** = Span 内发生的离散事件（如工具参数被修正、错误被触发）。

## 一次典型 Agent Trace 的 Span 结构

```
Trace: user_turn_123
├── Span: context_assembly (50ms)
├── Span: llm_call #1 (2.4s)
│   ├── Event: prompt_tokens=2048, completion_tokens=512
│   └── Event: reasoning_content=...
├── Span: tool_call.read_file (120ms)
│   ├── Event: tool_name=read_file
│   └── Event: arguments={"path": "config.yaml"}
├── Span: llm_call #2 (1.8s)
│   └── Event: tool_calls=[...]
├── Span: tool_call.web_search (800ms)
├── Span: validation (20ms)
│   └── Event: schema_check=passed
└── Span: final_response (10ms)
    └── Event: output_tokens=...
```

## 与普通日志的区别

| 维度 | 日志（Log） | Trace |
|---|---|---|
| 结构 | 文本行，非结构化 | 树状 Span，有父子关系 |
| 聚合 | 按关键字 grep | 按 Trace/Span ID 关联 |
| 延迟分析 | 难 | 每个 Span 有 start/end 时间 |
| 成本分析 | 难 | 每个 LLM Span 可挂 Token/费用 |
| 可视化 | 文本 | 瀑布图、火焰图 |
| 标准 | 无统一标准 | OpenTelemetry / LangSmith / W&B 等 |

## Agent Trace 的特殊性

相比普通微服务 Trace，Agent Trace 有额外挑战：

1. **非确定性**：同一次输入可能因模型采样、工具返回不同而产生不同执行路径。
2. **长链路**：一个 Turn 可能包含 10+ 次 LLM 调用和 20+ 次工具调用。
3. **分支**：工具调用可能并行（Hermes 的 ThreadPool、OpenAI 的 parallel tool calls），形成分支 Span。
4. **子 Agent 嵌套**：子 Agent 的 Trace 应作为父 Trace 的子树，或独立 Trace 并通过 `parent_id` 关联。
5. **LLM 特有语义**：需要记录 prompt、completion、reasoning、tool_calls、function 输出等，而不是简单的 HTTP 请求/响应。

## 哪些信息应该被 Trace 记录

- **Span 级别**：name、start_time、end_time、parent_id、span_kind
- **LLM Span**：model、provider、prompt_tokens、completion_tokens、total_tokens、cost、latency、temperature、reasoning_content
- **Tool Span**：tool_name、arguments、output、exit_code（如果是 shell/bash）、error
- **Agent 事件**：loop_iteration、halt_decision、budget_exceeded、compaction_triggered、sub_agent_spawned
- **上下文事件**：memory_retrieved、context_truncated、prompt_cached

## 四框架中的 Trace/Observability 设计

| 框架 | 可观测性重点 | 特点 |
|---|---|---|
| **Hermes** | 以调试和安全性为中心 | `_api_call_count`、`_budget`、interrupt 传播、工具集版本号；未强调外部 Trace 导出 |
| **nanobot** | 轻量本地日志 | 以 `print`/日志事件为主；不内置复杂 Trace 系统 |
| **OpenClaw** | 生产级事件驱动 | `Run`/`Attempt`/`Stream` 天然可映射为 Span；draft stream 支持节流和 in-flight 监控 |
| **OpenCode** | 流式事件直接可观测 | AI SDK 的 `fullStream` + `text-delta` 事件可自然转化为 Trace；流式 UI 进度可见 |

## 设计建议

1. **一个 Turn 一个 Trace**：这样能把用户请求、成本、延迟完整关联起来。
2. **LLM 调用必须是一个独立 Span**：因为模型调用通常占 80%+ 延迟和费用。
3. **工具调用也要成 Span**：方便定位「是哪个工具慢了/错了」。
4. **保留原始输入输出**：用于调试、评估和后续微调训练数据生成。
5. **不要泄露敏感信息**：Trace 中的 prompt 可能包含密钥、用户隐私；要做好脱敏和访问控制。
6. **与 Eval 对齐**：Trace 数据可以导出为 golden dataset，用于回归测试。

## 相关概念

- [[agent-turn]] —— 一个 Turn 通常对应一个顶层 Trace
- [[orchestration-loop]] —— Trace 的 Span 结构映射循环内的每次迭代
- [[error-handling]] —— Trace 是定位错误现场的关键
- [[state-management]] —— Trace 记录状态转换，状态持久化保留最终状态
- [[sub-agent-orchestration]] —— 子 Agent 的 Trace 关联方式

## 相关来源

- [[hermes-agent]] —— Hermes 的 budget/interrupt 等可观测计数
- [[openclaw-framework-analysis]] —— 分层运行结构（Run/Attempt/Stream）
- [[opencode-framework-analysis]] —— AI SDK 流式事件
