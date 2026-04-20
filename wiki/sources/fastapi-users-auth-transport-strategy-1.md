---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250828_FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy)上.md
tags: [fastapi, fastapi-users, 认证后端, transport, jwt, cookie, bearer]
---

# FastAPI-Users 保姆级教程（三）：认证后端揭秘——传输方式（Transport）与策略（Strategy）上

## 摘要

本文深入解析 FastAPI-Users 官方文档中 "Authentication backends" 章节的上半部分，揭示了认证后端设计的核心公式：Transport + Strategy = Authentication Backend。文章详细讲解了两种传输方式（Bearer 和 Cookie）的优缺点与适用场景，以及 JWT 策略的配置与工作原理。对于 CookieTransport，文章逐一解释了各配置参数的安全含义（`cookie_secure`、`cookie_httponly`、`cookie_samesite` 等）。对于 JWTStrategy，文章介绍了其无状态、易于横向扩展的优点，以及令牌签发后无法服务端撤销的缺点，并展示了 HS256 和 RS256 两种算法的配置方式。最后通过实战演练，演示了 Cookie 传输 + JWT 策略的组合配置，并使用 PowerShell 验证登录后 `Set-Cookie` 响应头的各属性。

## 核心要点

- **认证后端核心公式**：Transport（传输方式）+ Strategy（策略）= Authentication Backend
- **两种传输方式**：Bearer（Authorization 头，适合 API/移动应用）和 Cookie（HTTP Cookie，适合 Web 前端应用）
- **两种策略（本文）**：JWT（JSON Web Token，无状态、自包含）、Database 和 Redis（下篇讲解）
- **理论组合数**：2 种 Transport × 3 种 Strategy = 6 种认证后端，可按需自由组合
- **CookieTransport 配置参数**：
  - `cookie_name`：Cookie 名称（默认 `fastapiusersauth`）
  - `cookie_max_age`：生命周期（秒），默认 None 表示会话 Cookie
  - `cookie_secure`：仅 HTTPS 发送（默认 True）
  - `cookie_httponly`：阻止 JavaScript 访问，防 XSS（默认 True）
  - `cookie_samesite`：CSRF 防御策略（默认 `lax`）
- **Cookie 登录/登出行为**：返回 `204 No Content`，登录时通过 `Set-Cookie` 头设置 Cookie
- **BearerTransport 配置**：仅需 `tokenUrl` 参数，指定登录端点路径，使 Swagger UI 自动显示 "Authorize" 按钮
- **Bearer 登录行为**：返回 `200 OK` + JSON 响应体 `{"access_token": "...", "token_type": "bearer"}`
- **JWTStrategy 参数**：`secret`（密钥）、`lifetime_seconds`（有效期）、`token_audience`（受众）、`algorithm`（默认 HS256）、`public_key`（用于 RS256 等非对称算法）
- **JWT 登出特性**：登出时不执行任何操作，JWT 在过期前始终有效，无法服务端撤销
- **策略实例化使用函数**：`get_strategy` 必须作为可调用对象（callable）提供给认证后端，以支持与其他依赖项动态实例化

## 原始文件

- [原始文件](../../raw/archive/20250828_FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy)上.md)
