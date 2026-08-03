---
type: concept
created: 2026-04-20
updated: 2026-08-03
sources: [understand-anything-mcp, panniantong-agent, mcp-permission-middleware]
tags: [mcp, model-context-protocol, tool-calling, agent, interoperability, oauth, authorization]
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

## 授权与权限控制

远程 MCP 服务器（HTTP transport）推荐基于 **OAuth 2.1 + PKCE** 的标准授权流程：

1. 客户端首次请求收到 `401 Unauthorized` + `WWW-Authenticate: Bearer` + `resource_metadata` 地址。
2. 客户端拉取 **Protected Resource Metadata (PRM)**，获得授权服务器地址和 `scopes_supported`。
3. 做 OIDC/OAuth discovery，拿到 authorize/token endpoint。
4. 用户授权后，客户端获得 access token。
5. 后续 MCP 请求在 `Authorization: Bearer <token>` 中携带 token。

服务端拿到 token 后必须校验：

- **有效性**：introspection endpoint 或 JWT 签名验证。
- **Audience (`aud`)**：确认 token 是发给本 MCP 服务器的，防止 token passthrough。
- **Scope**：检查 token 是否包含当前工具所需的 scope。
- **主体身份**：从 `sub` / `client_id` 取出身份，用于后续 RBAC/ABAC。

### 权限模式分层

| 模式 | 粒度 | 说明 |
|---|---|---|
| **Scope** | 粗 | OAuth scope，如 `mcp:tools:read` / `mcp:tools:write` / `mcp:tools:admin` |
| **RBAC** | 中 | 按角色决定可见/可调用的工具 |
| **ABAC** | 细 | 按属性判断，如部门、金额、时间 |
| **CBAC** | 上下文 | 身份 + 上下文 + 资源同时评估，如未信任输入禁止高风险工具 |

安全最佳实践反对 wildcard scope（`files:*`、`admin:*`），主张 **scope minimization** 和按需 step-up 授权。

## MCP 安全威胁

| 风险 | 要点 |
|---|---|
| **Confused Deputy** | MCP proxy 用静态 client_id 代理多客户端，攻击者利用 consent cookie 跳过授权，把 code 转发到恶意 redirect_uri |
| **Token Passthrough** | 服务端不校验 audience，把客户端 token 原样透传给下游 API |
| **SSRF** | 恶意 MCP 服务器在 OAuth metadata 里填内网/云元数据地址，诱导客户端发起内网请求 |
| **Local MCP Server Compromise** | 一键安装的本地 MCP server 可能是恶意二进制，执行任意命令 |
| **State Handle Hijacking** | 工具返回的 state handle 未绑定用户身份，可被猜测或冒用 |
| **Scope 过度授权** | 一次性请求全部 scope，stolen token 影响面大 |

参考实现与 demo 见 [[mcp-permission-middleware]]。

## 相关来源

- [[understand-anything-mcp]] —— Understand-Anything 项目及其 MCP 集成实践
- [[panniantong-agent]] —— Agent-Reach 通过 MCP 为 Agent 提供互联网访问能力
- [[mcp-permission-middleware]] —— MCP 授权与 RBAC/ABAC/CBAC 中间件示例
