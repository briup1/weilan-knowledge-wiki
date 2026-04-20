---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250902_FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers.md
tags: [fastapi, fastapi-users, pydantic, schemas, routers, 路由]
---

# FastAPI-Users 保姆级教程（六）：最后的拼图——Schemas 与 Routers

## 摘要

本文是 FastAPI-Users 系列教程的理论收官篇，讲解最后两块核心拼图：数据模型（Schemas）和路由（Routers）。Schemas 基于 Pydantic 模型，定义了 API 请求和响应的数据结构与验证规则，fastapi-users 提供了 `BaseUser`（读取）、`BaseUserCreate`（注册）、`BaseUserUpdate`（更新）三个基础模型供继承。文章展示了如何添加自定义字段，并强调 Schema 中的字段必须与数据库模型保持一致。Routers 部分介绍了 `FastAPIUsers` 主类的实例化方式，以及五种可用的路由生成器：Auth router（登录/登出）、Register router（注册）、Reset password router（密码重置）、Verify router（邮箱验证）、Users router（用户管理）。文章展示了如何在 `main.py` 中注册这些路由，并介绍了 `requires_verification=True` 参数用于要求用户必须先验证邮箱才能访问特定接口。

## 核心要点

- **Schemas 的作用**：定义 API 的数据契约，负责请求验证和响应序列化，与数据库 ORM 模型职责分离
- **三个基础 Schema 模型**：
  - `BaseUser[ID]`：用于读取用户信息，需要泛型指定 ID 类型
  - `BaseUserCreate`：用于用户注册，包含 `email` 和 `password`
  - `BaseUserUpdate`：用于更新用户资料
- **添加自定义字段**：在继承的 Schema 类中直接添加字段，同时确保数据库 User 模型中也定义了相同字段
- **FastAPIUsers 实例化**：`FastAPIUsers[User, ID](get_user_manager, [auth_backend, ...])`
  - 需要泛型指定用户模型和 ID 类型
  - 可传入多个认证后端
- **五种路由生成器**：
  - `get_auth_router(auth_backend)`：登录 `/login` 和登出 `/logout`
  - `get_register_router(UserRead, UserCreate)`：注册 `/register`
  - `get_reset_password_router()`：忘记密码 `/forgot-password` 和重置密码 `/reset-password`
  - `get_verify_router(UserRead)`：请求验证令牌 `/request-verify-token` 和验证 `/verify`
  - `get_users_router(UserRead, UserUpdate)`：用户管理（获取/更新自身信息、管理员操作）
- **requires_verification 参数**：在 `get_auth_router` 和 `get_users_router` 中传入 `requires_verification=True`，要求用户必须通过邮箱验证才能访问
- **高级主题**：OAuth2 第三方登录（Google、Facebook 等）、密码哈希算法自定义（默认 Argon2）

## 原始文件

- [原始文件](../../raw/archive/20250902_FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers.md)
