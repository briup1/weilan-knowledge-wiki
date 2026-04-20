---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [fastapi-users-concepts, fastapi-users-user-model, fastapi-users-auth-transport-strategy-1, fastapi-users-auth-transport-strategy-2, fastapi-users-usermanager, fastapi-users-schemas-routers, fastapi-users-project-template]
tags: [fastapi, fastapi-users, authentication, oauth2, jwt]
---

# FastAPI-Users

FastAPI-Users 是 FastAPI 生态中成熟的用户认证库（当前版本 14.0.1），提供可扩展的用户模型、开箱即用的认证路由、OAuth2 社交登录和可插拔的密码验证，帮助开发者在几分钟内为项目添加完整的注册与认证系统。

## 核心组件与特性

- **用户模型与数据库适配器**：支持 SQLAlchemy（PostgreSQL/SQLite/MySQL）和 Beanie（MongoDB）。默认使用 UUID 主键，也可切换为整数 ID；详见 [[fastapi-users-user-model]]。
- **认证后端（Transport + Strategy）**：核心设计公式为 Transport + Strategy = Authentication Backend。
  - Transport：Bearer（Authorization 头，适合 API/移动应用）或 Cookie（适合 Web 前端）。
  - Strategy：JWT（无状态、易扩展）、Database（服务端可控令牌失效）、Redis（高并发内存存储）。
  - 详见 [[fastapi-users-auth-transport-strategy-1]] 和 [[fastapi-users-auth-transport-strategy-2]]。
- **UserManager**：承载注册、验证、密码重置等核心逻辑的枢纽，提供丰富的事件钩子（如 `on_after_register`、`on_after_forgot_password`）供插入自定义业务；详见 [[fastapi-users-usermanager]]。
- **Pydantic Schemas**：定义用户读取、创建、更新的数据契约，与数据库 ORM 模型职责分离；详见 [[fastapi-users-schemas-routers]]。
- **路由生成器**：自动生成 Auth、Register、Reset password、Verify、Users 五条路由，通过 `current_user` 依赖工厂保护受控接口。
- **OAuth2 支持**：内置 Google、Facebook 等第三方社交登录扩展。

## 使用指南与最佳实践

- **最小化实现仅需四个文件**：`main.py`（应用入口）、`db.py`（数据库与模型）、`schemas.py`（Pydantic 模型）、`users.py`（UserManager 与认证后端配置）。
- **生产策略推荐**：Bearer + DatabaseStrategy 的组合比纯 JWT 更安全，因为支持服务端令牌失效（登出/改密码后立即失效）；详见 [[fastapi-users-project-template]]。
- **密码验证**：在 UserManager 中重载 `validate_password`，强制长度、复杂度规则。
- **权限分级**：利用 `fastapi_users.current_user(active=True, verified=True, superuser=True)` 按需生成不同级别的依赖。

## 相关来源

- [[fastapi-users-concepts]] —— 核心概念与快速上手
- [[fastapi-users-user-model]] —— 用户模型与数据库集成
- [[fastapi-users-auth-transport-strategy-1]] —— 传输方式与 JWT 策略
- [[fastapi-users-auth-transport-strategy-2]] —— Database 与 Redis 策略
- [[fastapi-users-usermanager]] —— UserManager 深入解析
- [[fastapi-users-schemas-routers]] —— Schemas 与 Routers
- [[fastapi-users-project-template]] —— 生产级项目模板实战
