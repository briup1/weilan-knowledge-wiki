---
title: "FastAPI-Users 保姆级教程（五）：最后的拼图——Schemas 与 Routers"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/tutorial", "type/concept", "FastAPI-Users", "Pydantic", "路由"]
status: "archived"
references: "Archive/20250902_FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers.md"
---

# FastAPI-Users 保姆级教程（五）：最后的拼图——Schemas 与 Routers

本文完成 FastAPI-Users 配置的最后两块拼图：**数据模型 (Schemas)** 和 **路由 (Routers)**，将后端逻辑最终暴露为可供客户端调用的 API 接口。

## 数据模型 (Schemas)：API 的数据契约

`Schemas` 基于 `Pydantic` 模型，定义了 API 请求和响应的数据结构、类型和验证规则。

官方文档说明：

> FastAPI 大量使用 Pydantic 模型来验证请求体和序列化响应。FastAPI-Users 期望你提供代表用户在读取、创建和更新时状态的 Pydantic 模型。这与你的数据库用户模型不同，后者是实际与数据库交互的对象。

FastAPI-Users 内置的基础 Schema 包含以下字段：

- `id` (ID)：用户唯一标识符。
- `email` (str)：用户邮箱。
- `is_active` (bool)：是否已激活。
- `is_verified` (bool)：是否已验证。
- `is_superuser` (bool)：是否为超级用户。

### 定义你自己的 Schemas

FastAPI-Users 提供了三个基础模型：

- `BaseUser`：用于**读取**用户的基本模型。
- `BaseUserCreate`：专用于用户**注册**，包含 `email` 和 `password`。
- `BaseUserUpdate`：专用于用户资料**更新**。

```python
import uuid
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass
```

`BaseUser` 需要泛型来指定 ID 类型（如 `uuid.UUID`、整数或 MongoDB 的 `ObjectID`）。

### 添加自定义字段

```python
import datetime
import uuid
from typing import Optional
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    birthdate: Optional[datetime.date]

class UserCreate(schemas.BaseUserCreate):
    first_name: str
    birthdate: Optional[datetime.date]

class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str]
    birthdate: Optional[datetime.date]
```

**请确保在你的数据库模型中镜像这些字段**，否则数据无法被真正存储。

## 路由 (Routers)：连接世界的桥梁

### 统一管理 `FastAPIUsers` 实例

```python
import uuid
from fastapi_users import FastAPIUsers
from app.db import User
from app.users import auth_backend, get_user_manager

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,  # 注入 UserManager 依赖
    [auth_backend],    # 传入所有认证后端列表
)
```

### 可用的路由生成器

- **Auth router**：提供 `/login` 和 `/logout`。
- **Register router**：提供 `/register`。
- **Reset password router**：提供 `/forgot-password` 和 `/reset-password`。
- **Verify router**：提供 `/request-verify-token` 和 `/verify`，用于邮箱验证。
- **Users router**：提供管理用户的路由，如读取、更新个人信息。

#### 认证路由 (Auth router)

```python
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
```

要求用户必须通过邮箱验证才能登录：

```python
fastapi_users.get_auth_router(auth_backend, requires_verification=True)
```

#### 注册路由 (Register router)

```python
from app.schemas import UserRead, UserCreate

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
```

#### 验证路由 (Verify router)

```python
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
```

#### 密码重置路由 (Reset password router)

```python
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
```

#### 用户管理路由 (Users router)

```python
from app.schemas import UserUpdate

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
```

要求用户验证后才能访问管理接口：

```python
fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True)
```

## 结语

FastAPI-Users 的主要配置部分就全部讲解完毕了。从数据库模型出发，一路配置了认证后端、`UserManager`、`Schemas`，并最终通过 `Routers` 将功能暴露为 API。

官方文档还提供了 OAuth2 社交登录、密码哈希自定义等高级主题，但已掌握的内容足以构建一个强大而安全的用户系统。

> 完整代码请移步 GitHub 项目：https://github.com/acelee0621/fastapi-users-turtorial

---

## 来源与归档

- 原始素材：[Archive/20250902_FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers.md](../../../Archive/20250902_FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers.md)
