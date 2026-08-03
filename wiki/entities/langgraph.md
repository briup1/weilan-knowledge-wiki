---
type: entity
created: 2026-05-08
updated: 2026-05-08
sources: [agent-harness-anatomy]
tags: [langgraph, langchain, agent-framework, state-graph, orchestration]
---

# LangGraph

LangChain 旗下的 Agent 编排框架，将 [[agent-harness|Harness]] 建模为**显式状态图**（Explicit State Graph），是"厚 Harness"哲学的代表实现。

## 一句话定义

LangGraph 是一个将 Agent 工作流建模为图节点的状态机框架，通过显式控制流确保可靠性和可审计性。

## 核心架构

### 图节点状态机

- **状态（State）**：TypedDict 定义 workflow 中所有可能的状态字段
- **Reducers**：函数，定义如何合并状态更新（追加消息 vs 替换消息）
- **条件边**：两个核心节点（`llm_call` + `tool_node`）通过条件边连接——存在工具调用则路由到 `tool_node`，否则路由到 `END`
- **Super-step 边界**：检查点发生在一轮完整的 LLM 调用 + 工具执行之后

### 时间旅行调试

每个 super-step 的检查点都被保存，支持：
- **查询线程历史**：精确看到任意步骤之前的状态
- **分叉历史**：从某个历史检查点重新开始，用不同输入或修改后的状态测试"如果……会怎样"
- **中断后恢复**：Agent 在第 N 步因网络中断停止，下次从第 N 步检查点恢复

### 与 LangChain AgentExecutor 的关系

LangGraph 从 LangChain 的 AgentExecutor（v0.2 中弃用）演进而来。AgentExecutor 难以扩展且缺乏多 Agent 支持。LangChain 的 Deep Agents 明确使用"Agent Harness"术语：内置工具、规划（`write_todos`）、文件系统、子 Agent 生成、持久化记忆。

## Harness 定位

LangGraph 的设计哲学是"厚 Harness"——通过显式控制来确保可靠性和可审计性，与 [[claude-code]] 的"薄 Harness"形成鲜明对比。

LangChain TerminalBench 2.0 优化案例：使用同一模型 gpt-5.2-codex，通过构建自验证机制、环境上下文注入、循环失败检测打断、推理三明治策略，将通过率从 52.8% 提升到 66.5%。

## 与其他框架的对比

| 维度 | LangGraph | Claude Code | OpenAI Agents SDK |
|------|-----------|-------------|-------------------|
| 哲学 | 厚 Harness（显式控制） | 薄 Harness（dumb loop） | 代码优先 |
| 状态管理 | 图节点状态机 | Git 提交即检查点 | previous_response_id |
| 调试 | 时间旅行 + 历史分叉 | Git diff/log | Runner 类 |
| 记忆 | 命名空间 JSON Store | 三层文件式记忆 | Sessions |

## 相关概念

- [[agent-harness]] —— Agent Harness 核心概念
- [[multi-agent-collaboration]] —— 多 Agent 协作

## 来源

- [[agent-harness-anatomy]] —— Agent Harness 十二大模块深度解析
