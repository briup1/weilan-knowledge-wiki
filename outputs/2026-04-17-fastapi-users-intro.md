---
title: "FastAPI-Users 简介与应用场景"
created: 2026-04-17
query: "FastAPI-Users是什么？我能用它做什么？"
sources:
  - "wiki/Fastapi/articles/fastapi-users-core-concepts.md"
  - "wiki/Fastapi/articles/fastapi-users-project-template.md"
---

# FastAPI-Users 简介与应用场景

## FastAPI-Users 是什么？

**FastAPI-Users** 是 FastAPI 生态中一个成熟、专门用于用户认证与管理的库（当前版本 14.0.1）。它的设计目标是**高度可定制**和**易于适配**，为 FastAPI 应用提供一套完整的用户注册、登录、权限控制解决方案，让你不用从零手写认证系统。

---

## 核心特性

- **可扩展的用户模型**：在基础字段（email、密码、是否激活等）上自由扩展自定义字段
- **开箱即用的路由**：注册、登录、登出、重置密码、邮箱验证等 API 直接可用
- **社交 OAuth2 登录**：支持集成 Google、GitHub 等第三方登录
- **依赖注入支持**：通过 `Depends(current_active_user)` 轻松保护路由
- **可插拔密码验证**：可自定义密码强度规则
- **多数据库支持**：内置 SQLAlchemy 异步适配（PostgreSQL、SQLite、MySQL）和 MongoDB（Beanie ODM）
- **多认证策略**：支持 JWT、Database Token、Redis 等策略，以及 Bearer / Cookie 等传输方式
- **完整的 OpenAPI 支持**：Swagger UI 中自动生成认证入口

---

## 五大核心模块

| 模块                               | 职责                              |
| -------------------------------- | ------------------------------- |
| **用户模型 & 数据库适配器**                | 定义用户表结构，连接 SQLAlchemy / Beanie  |
| **认证后端（Authentication Backend）** | 组合「传输方式」+「策略」，决定 Token 怎么传、怎么验证 |
| **UserManager**                  | 核心逻辑枢纽，处理注册、验证、密码重置、事件钩子        |
| **Pydantic Schemas**             | 定义用户数据的读取、创建、更新时的校验规则           |
| **FastAPIUsers & 路由**            | 生成预定义路由和 `current_user` 依赖工厂    |

---

## 你能用它做什么？

### 1. 快速搭建带认证的后端服务
无需手写注册/登录逻辑，几行代码即可拥有一套 RESTful 认证 API：
- `POST /auth/register` — 用户注册
- `POST /auth/jwt/login` — 用户登录获取 Token
- `POST /auth/forgot-password` — 申请重置密码
- `GET /users/me` — 获取当前用户信息
- `PATCH /users/me` — 更新用户资料

### 2. 保护你的业务路由
通过 `Depends(current_active_user)` 将用户身份注入路由：
```python
@app.get("/dashboard")
async def dashboard(user: User = Depends(current_active_user)):
    return {"message": f"Hello, {user.email}"}
```

### 3. 实现分级权限控制
`fastapi_users.current_user()` 支持多种权限筛选：
- `active=True` — 仅活跃用户
- `verified=True` — 仅已验证邮箱的用户
- `superuser=True` — 仅超级管理员

### 4. 构建可复用的项目模板 / 微服务
FastAPI-Users 是构建「用户认证微服务」或「新项目脚手架」的理想起点，尤其适合：
- SaaS 产品的用户系统
- 内部工具的统一登录服务
- 需要快速验证 MVP 认证流程的场景

### 5. 灵活切换数据库和认证策略
开发时用 SQLite + JWT 快速迭代，生产环境无缝切换到 PostgreSQL + Database Strategy（支持服务端吊销 Token），完全不需要重写业务代码。

---

## 最小化上手路径

```bash
uv add "fastapi[standard]" "fastapi-users[sqlalchemy]" aiosqlite
```

然后只需配置 4 个文件（`db.py`、`schemas.py`、`users.py`、`main.py`），即可运行一个完整的认证系统。详细代码和项目模板可参考知识库中的 [FastAPI-Users 核心概念](wiki/Fastapi/articles/fastapi-users-core-concepts.md) 和 [实战项目模板](wiki/Fastapi/articles/fastapi-users-project-template.md) 文章。
