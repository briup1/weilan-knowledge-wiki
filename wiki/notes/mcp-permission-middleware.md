---
type: note
created: 2026-08-02
updated: 2026-08-02
tags: [mcp, authorization, rbac, abac, cbac, security, agent-tool-system]
sources:
  - modelcontextprotocol.io authorization docs
  - cerbos-mcp-authorization-blog
  - aembit-context-based-access-control
  - medium-rbac-in-mcp-servers
---

# MCP 权限控制：RBAC + ABAC + CBAC 中间件示例

本笔记整理 MCP 生态中的权限控制调研结论，并提供一个最小可运行的 FastAPI 中间件示例，演示如何把 **认证 → Scope 校验 → RBAC 动态工具可见性 → ABAC 上下文判断** 串成一条链路。

## 关联概念

- [[mcp]] —— Model Context Protocol 协议本身
- [[agent-tool-system]] —— 工具注册、发现、调度
- [[agent-security]] —— 纵深防御与 fail-closed 默认
- [[validation-loop]] —— 工具调用前的多层验证

## 调研结论

### 1. MCP 官方授权机制

远程 MCP 服务器（HTTP transport）推荐基于 **OAuth 2.1 + PKCE** 的标准流程：

1. 客户端首次请求收到 `401 Unauthorized` + `WWW-Authenticate: Bearer` + `resource_metadata` 地址。
2. 拉取 Protected Resource Metadata (PRM)，获得授权服务器地址与 `scopes_supported`。
3. OIDC/OAuth discovery 拿到 authorize/token endpoint。
4. 用户授权后客户端获得 access token。
5. 后续请求带 `Authorization: Bearer <token>`，服务端必须校验：
   - token 有效性（introspection 或 JWT 签名）
   - audience (`aud`) 是否匹配本 MCP 服务器
   - scope 是否包含当前工具所需权限
   - subject / client_id 用于后续 RBAC/ABAC

### 2. 权限控制模式分层

| 模式 | 粒度 | 说明 |
|---|---|---|
| **Scope** | 粗 | OAuth scope，如 `mcp:tools:read` / `mcp:tools:write` / `mcp:tools:admin` |
| **RBAC** | 中 | 按角色决定能看到/调用哪些工具 |
| **ABAC** | 细 | 按属性判断，如部门、金额、环境 |
| **CBAC** | 上下文 | 把身份 + 上下文 + 资源一起评估，如未信任输入禁止高风险工具 |

官方安全文档明确反对 wildcard scope（`files:*`、`admin:*`），主张 **scope minimization** 和按需 step-up 授权。

### 3. MCP 协议层特有风险

| 风险 | 要点 |
|---|---|
| **Confused Deputy** | MCP proxy 用静态 client_id 代理多客户端，攻击者利用 consent cookie 跳过授权 |
| **Token Passthrough** | 服务端不校验 audience，把客户端 token 透传给下游 API |
| **SSRF** | 恶意 MCP 服务器在 OAuth metadata 里填内网/云元数据地址 |
| **Local MCP Server Compromise** | 一键安装的本地 MCP server 可能是恶意二进制 |
| **State Handle Hijacking** | 工具返回的 state handle 未绑定用户身份，可被冒充 |

## 代码示例

完整可运行代码见同目录下的 [`mcp_permission_demo.py`](./mcp_permission_demo.py)。

核心架构：

```text
认证 (Bearer token)
    ↓
Scope 校验
    ↓
RBAC 动态工具可见性
    ↓
ABAC 上下文条件判断
    ↓
工具执行
```

### 测试命令

```bash
# 1. 普通用户只能看到 read_file
curl -H "Authorization: Bearer role_user_env_prod" http://localhost:8000/tools

# 2. 管理员能看到所有工具
curl -H "Authorization: Bearer role_admin_env_prod" http://localhost:8000/tools

# 3. 管理员调用 shell_exec 成功
curl -X POST -H "Authorization: Bearer role_admin_env_prod" \
  -H "Content-Type: application/json" \
  -d '{"tool":"shell_exec","arguments":{"command":"ls"}}' \
  http://localhost:8000/invoke

# 4. 带未信任输入时，manager 调用 shell_exec 会被 ABAC 拒绝
curl -X POST -H "Authorization: Bearer role_manager_env_prod" \
  -H "X-Untrusted-Input: true" \
  -H "Content-Type: application/json" \
  -d '{"tool":"shell_exec","arguments":{"command":"ls"}}' \
  http://localhost:8000/invoke
```

## 生产环境替换清单

| Demo 中 | 生产环境 |
|---|---|
| `mock_verify_token` | JWT 签名验证 或 OAuth introspection endpoint |
| 硬编码 `RBAC_POLICY` | 外置策略引擎（Cerbos / OpenFGA / OPAL） |
| 请求头 `X-Untrusted-Input` | 输入消毒模块或 LLM 检测自动注入的上下文标记 |
| 内存 `ToolRegistry` | 与 MCP SDK 的 `Server.register_tool` 集成 |
| HTTP 接口 | MCP stdio / StreamableHTTP 传输层 |

## 参考资料

- [MCP Authorization — modelcontextprotocol.io](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization)
- [MCP Security Best Practices — modelcontextprotocol.io](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [MCP authorization: Securing Model Context Protocol servers with fine-grained access control — Cerbos](https://www.cerbos.dev/blog/mcp-authorization)
- [Context-Based Access Control for MCP Servers: Why Static Rules Fail — Aembit](https://aembit.io/blog/context-based-access-control-mcp-servers/)
- [Role-Based Access Control in MCP Servers — Medium](https://medium.com/@binayakdutta/role-based-access-control-in-mcp-servers-a-security-first-approach-for-ai-systems-e35aff8efa76)
