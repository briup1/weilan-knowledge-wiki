---
type: concept
created: 2026-04-20
updated: 2026-04-20
sources: [understand-anything-mcp, panniantong-agent]
tags: [mcp, model-context-protocol, tool-calling, agent, interoperability]
---

# MCP (Model Context Protocol)

一种开放协议标准，用于标准化 AI 模型与外部工具、数据源之间的通信方式，使 Agent 能够以统一接口调用任意第三方服务。

## 定义

MCP（Model Context Protocol）是由 Anthropic 提出的开放标准协议，定义了 AI 模型与外部工具、API、数据库和服务之间的通信规范。通过 MCP，AI Agent 可以像调用本地函数一样调用远程服务，无需为每个服务编写定制化的集成代码。

## 核心原理

### 客户端-服务器架构

MCP 采用类似 LSP（Language Server Protocol）的客户端-服务器模式：

- **MCP 客户端**：运行在 AI Agent 或 IDE 中，负责发现、连接和管理 MCP 服务器。
- **MCP 服务器**：为特定服务提供标准化接口的适配层，将服务的原生 API 转换为 MCP 协议格式。
- **工具暴露**：MCP 服务器将服务的功能暴露为「工具」（tools），每个工具包含名称、描述、参数 schema 和返回值 schema。

### 标准化工具调用流程

1. **发现**：Agent 通过 MCP 客户端扫描可用的 MCP 服务器和工具列表。
2. **选择**：根据用户请求，LLM 决定调用哪个工具，生成符合 schema 的参数。
3. **执行**：MCP 客户端将调用请求发送到对应的 MCP 服务器，服务器执行实际操作。
4. **返回**：服务器将执行结果按 MCP 格式返回，LLM 整合到回复中。

### 与 Function Calling 的对比

| 维度 | MCP | Function Calling |
|------|-----|-----------------|
| 标准化程度 | 协议级标准，跨平台通用 | 模型特定实现，各厂商不兼容 |
| 生态开放性 | 任何服务可写 MCP 服务器接入 | 依赖模型厂商支持 |
| 配置方式 | 安装 MCP 服务器即可使用 | 需在代码中逐个定义函数 schema |
| 适用场景 | 多 Agent、多工具、跨平台协作 | 单一应用内的工具调用 |
| 示例工具 | Slack、BigQuery、Sentry、GitHub | 应用内自定义函数 |

## 典型应用场景

- **企业工具链集成**：通过 MCP 连接 Slack（发送消息）、BigQuery（运行查询）、Sentry（获取错误日志）、Jira（创建工单），使 Agent 成为企业工作流的中枢。
- **互联网访问能力**：Agent-Reach 等项目通过 MCP 为 AI Agent 提供一键互联网阅读和搜索能力，覆盖 Twitter、Reddit、YouTube、B站、小红书等 15+ 平台。
- **代码库理解**：Understand-Anything 利用 MCP 将代码库分析能力暴露为 `/understand`、`/understand-dashboard` 等命令，实现跨平台的代码知识图谱生成。
- **数据库与存储**：通过 MCP 连接 PostgreSQL、MongoDB、Redis、向量数据库等，使 Agent 能够直接查询和操作数据。

## 优势与局限

**优势**：
- 一次编写 MCP 服务器，所有支持 MCP 的 Agent 均可使用。
- 降低工具集成成本，促进 Agent 生态的互操作性。
- 标准化安全模型，支持权限控制和审计日志。

**局限**：
- 生态仍在早期，MCP 服务器数量和成熟度有限。
- 性能开销：协议转换带来额外延迟。
- 错误处理：跨服务调用的错误传播和调试较复杂。

## 相关来源

- [[understand-anything-mcp]] —— Understand-Anything 项目及其 MCP 集成实践
- [[panniantong-agent]] —— Agent-Reach 通过 MCP 为 Agent 提供互联网访问能力
