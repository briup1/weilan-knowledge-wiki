---
type: concept
created: 2026-04-20
updated: 2026-04-20
sources: [fastapi-users-concepts, fastapi-users-auth-transport-strategy-1, fastapi-users-auth-transport-strategy-2]
tags: [jwt, authentication, security, fastapi, oauth2]
---

# JWT 认证

JWT（JSON Web Token）是一种开放标准（RFC 7519），用于在各方之间安全地传输信息作为 JSON 对象。在 Web 认证场景中，JWT 常被用作无状态的令牌格式，服务端通过验证令牌签名确认用户身份，无需维护会话状态。

## 定义

JWT 是一种自包含的令牌，将用户身份和声明信息编码为 JSON 后经过 Base64Url 编码和数字签名，形成可在网络中安全传输的字符串。服务端收到 JWT 后，只需验证签名有效性即可信任其中携带的信息，无需查询数据库或会话存储。

## 核心原理

JWT 由三部分组成，以点号（`.`）分隔：

- **Header（头部）**：包含令牌类型（`typ: JWT`）和签名算法（`alg: HS256` 或 `RS256`）。
- **Payload（载荷）**：包含声明（claims），如用户 ID（`sub`）、签发时间（`iat`）、过期时间（`exp`）、受众（`aud`）等。Payload 仅做 Base64Url 编码，**不加密**，因此不应存放敏感信息。
- **Signature（签名）**：使用 Header 中指定的算法和密钥对 "Header.Payload" 进行签名，确保令牌未被篡改。

验证流程：客户端在请求头中携带 `Authorization: Bearer <token>`，服务端分离出 Header 和 Payload，用密钥重新计算签名并与令牌中的签名比对；同时检查 `exp` 是否过期。

## 与其他概念的对比

| 维度 | JWT | Session |
|------|-----|---------|
| 状态管理 | 无状态，服务端不存储令牌 | 有状态，服务端需维护会话存储 |
| 扩展性 | 易于横向扩展，任意节点均可验证 | 需要共享会话存储（如 Redis）或粘性会话 |
| 令牌撤销 | 签发后无法服务端撤销，只能等待过期 | 可立即删除会话，实现即时登出 |
| 性能 | 验证仅需计算签名，无需数据库查询 | 每次请求需查询会话存储 |
| 适用场景 | API/移动应用、微服务间调用 | 传统 Web 应用、需要即时失效的场景 |

## 适用场景

- **RESTful API 认证**：前后端分离架构中，JWT 是 API 请求身份验证的标准方案。
- **微服务间调用**：服务间通过 JWT 传递用户身份，避免每个服务都维护会话状态。
- **单点登录（SSO）**：用户登录一次后，JWT 可在多个子系统间传递身份。
- **移动端应用**：移动应用不适合使用 Cookie 会话，Bearer JWT 是更自然的选择。

## 注意事项

- **密钥安全**：HS256 使用单一共享密钥，泄露意味着可伪造任意令牌；RS256 使用公私钥对，私钥仅保存在签发服务端，安全性更高。
- **过期时间**：应设置合理的 `exp`，通常 15 分钟到数小时；结合 Refresh Token 机制可在安全与用户体验间取得平衡。
- **敏感信息**：Payload 可被 Base64 解码读取，不要存放密码、密钥等敏感数据。

## 相关来源

- [[fastapi-users-concepts]] —— FastAPI-Users 核心概念与快速上手
- [[fastapi-users-auth-transport-strategy-1]] —— 传输方式与 JWT 策略详解
- [[fastapi-users-auth-transport-strategy-2]] —— Database 与 Redis 策略详解
