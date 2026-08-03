---
type: entity
created: 2026-05-08
updated: 2026-05-08
sources: [agent-harness-anatomy]
tags: [openai, agents-sdk, codex, agent-framework, code-first]
---

# OpenAI Agents SDK

OpenAI 推出的 Agent 开发框架，采用"代码优先"设计——工作流逻辑用原生 Python 表达而非图 DSL，是 [[agent-harness|Harness]] 的三大主流实现之一。

## 一句话定义

代码优先的 Agent Harness 框架，通过 `Runner` 类实现编排循环，支持 Codex 三层架构和多 Agent 编排。

## 核心架构

### Runner 类

`Runner` 类是 Harness 的执行引擎，支持三种运行模式：异步、同步和流式。

### Codex 三层架构

```
Codex Core（Agent 代码 + 运行时）
    ↕ 双向 JSON-RPC API
App Server（应用服务器）
    ↕ 多客户端支持
客户端界面（CLI / VS Code / Web App）
```

所有界面共享同一个 Harness，这解释了为什么"Codex 模型在 Codex 界面上的表现优于通用聊天窗口"。

### 工具体系

- **函数工具**：`@function_tool` 装饰器将 Python 函数暴露为工具
- **托管工具**：平台内置能力（WebSearch、CodeInterpreter、FileSearch）
- **MCP 服务器工具**：通过 [[mcp]] 连接的远程工具

### 优先级栈

系统提示的严格优先级排序：
1. 服务器控制的系统消息（最高优先级，防提示注入）
2. 工具定义
3. 开发者指令
4. 用户指令（级联的 `AGENTS.md` 文件，32 KiB 限制）
5. 对话历史

### 状态管理

四种互斥的持久化策略：
1. 应用内存（最简单，无法跨进程恢复）
2. SDK Sessions（SDK 自动管理）
3. 服务端 Conversations API（OpenAI 服务端存储）
4. `previous_response_id` 链式调用（轻量级状态传递）

## 多 Agent 编排

### Handoffs（交接模式）

分流 Agent 识别用户需求，将对话完全转移给专业 Agent。专业 Agent 成为活跃 Agent，直接响应用户。

### Agents-as-Tools（工具模式）

管理 Agent 保持对话控制权，将专业 Agent 作为工具调用处理有边界的子任务，结果返回管理 Agent。

两种模式可组合使用。

## 生产案例：Symphony

OpenAI Frontier 团队的百万行代码实验：3 名工程师、5 个月、零行人工代码。核心教训：
- **构建时间至关重要**：1 分钟是内循环上限，超过则 Agent 生产力急剧下降
- **环境定义比模型能力更关键**：早期进展慢不是因为模型不足，而是环境定义不充分
- Ryan Lopopolo："当 Agent 失败时，问'缺少什么具体能力/上下文/结构'，而非'换提示'"

## 与其他框架的对比

| 维度 | OpenAI Agents SDK | Claude Code | LangGraph |
|------|-------------------|-------------|-----------|
| 哲学 | 代码优先 | 薄 Harness（dumb loop） | 厚 Harness（显式控制） |
| DSL | 原生 Python | 配置 + 文件 | 图 DSL |
| 安全 | Guardrails 三层 + Tripwire | OS 级沙箱 + 40 工具权限门控 | 显式控制流 |
| 状态 | 四种互斥策略 | Git 提交 | Super-step 检查点 |

## 相关概念

- [[agent-harness]] —— Agent Harness 核心概念
- [[multi-agent-collaboration]] —— 多 Agent 协作

## 来源

- [[agent-harness-anatomy]] —— Agent Harness 十二大模块深度解析
