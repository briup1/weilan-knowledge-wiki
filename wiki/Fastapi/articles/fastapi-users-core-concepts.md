---
title: "FastAPI-Users 保姆级教程（一）：核心概念与快速上手"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/tutorial", "type/concept", "FastAPI-Users", "认证", "用户管理"]
status: "archived"
references: "Archive/20250826_FastAPI-Users保姆级教程（一）：核心概念与快速上手.md"
---

# FastAPI-Users 保姆级教程（一）：核心概念与快速上手

`FastAPI-Users` 是 FastAPI 生态中一个久负盛名的用户认证库，当前版本已迭代至 `14.0.1`。本文将带你快速理解其核心概念，并通过最小化示例搭建一个基本用户认证系统。

## 官方资源

- **官方文档**：https://fastapi-users.github.io/fastapi-users/
- **源代码**：https://github.com/fastapi-users/fastapi-users

## FastAPI-Users：核心概念概览

根据官方文档，`FastAPI-Users` 旨在尽可能地实现可定制（customizable）和适应性（adaptable）。它提供了一套完整的用户注册与认证解决方案。

### 核心特性

- **可扩展的基础用户模型**：允许开发者根据需求自由扩展用户字段。
- **开箱即用的路由**：提供注册（register）、登录（login）、重置密码（reset password）和验证邮箱（verify e-mail）等常用认证路由。
- **开箱即用的社交 OAuth2 登录流程**：支持集成通过 OAuth2 进行的社交登录。
- **依赖注入可调用对象**：能够将当前用户（current user）注入到你的路由中。
- **可插拔的密码验证**：允许自定义密码验证规则。
- **可定制的数据库后端**：
  - 内置支持 **SQLAlchemy ORM 异步模式**，兼容 PostgreSQL、SQLite、MySQL 等关系型数据库。
  - 内置支持 **MongoDB 及 Beanie ODM**。
- **多种可定制的认证后端**：
  - **传输方式（Transports）**：支持 Authorization 头（header）、Cookie 等方式传递认证信息。
  - **策略（Strategies）**：支持 JWT、数据库（Database）、Redis 等多种令牌生成和管理策略。
- **完整的 OpenAPI 模式支持**：即使使用多个认证后端也能良好支持。

## 五大核心模块

1. **用户模型及数据库适配器（User model and database adapters）**
   负责处理用户数据的存储，通过 SQLAlchemy 支持关系型数据库，通过 Beanie 支持 MongoDB。

2. **认证后端（Authentication backends）**
   定义应用中用户会话的管理方式，由**传输方式**（token 如何通过请求携带）和**策略**（token 如何生成和保护）两部分组成。

3. **用户管理器（UserManager）**
   承载了 FastAPI-Users 的大部分业务逻辑，是连接各个模块的“枢纽”。包含注册、验证、密码重置等核心功能。

4. **Pydantic 模型（Schemas）**
   表示用户在读取（read）、创建（created）和更新（updated）时的不同数据结构，用于请求验证和响应序列化。

5. **FastAPIUsers 和路由（routers）**
   提供预定义的路由（注册、登录、验证账户、重置密码等）和 `current_user` 依赖工厂。

## 快速上手：最小化实现示例

### 1. 项目初始化

```bash
cd fastapi-users-tutorial
uv init
uv venv
uv add "fastapi[standard]" "fastapi-users[sqlalchemy]" aiosqlite
```

### 2. 构建项目文件

在项目根目录下创建 `app` 文件夹，并在其中创建以下四个文件：

#### `app/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
```

`main.py` 引入了五个核心路由生成器：

- `get_auth_router(auth_backend)`：处理用户认证（登录、登出）。
- `get_register_router(UserRead, UserCreate)`：用户注册。
- `get_reset_password_router()`：用户重置密码。
- `get_verify_router(UserRead)`：用户账户验证。
- `get_users_router(UserRead, UserUpdate)`：用户管理（获取/更新用户信息）。

#### `app/db.py`

```python
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
```

`SQLAlchemyBaseUserTableUUID` 预置了用户认证所需的核心字段：

```python
email: Mapped[str]
hashed_password: Mapped[str]
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

默认使用邮箱作为用户名格式。

#### `app/schemas.py`

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

- `UserRead`：读取用户信息时的结构。
- `UserCreate`：创建用户（注册）时的请求体结构。
- `UserUpdate`：更新用户资料时的请求体结构。

#### `app/users.py`

```python
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.db import User, get_user_db

SECRET = "SECRET"  # 生产环境请使用复杂密钥

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
```

核心组件解析：

- **`SECRET`**：用于生成和验证令牌的密钥，生产环境务必从环境变量加载。
- **`UserManager`**：继承 `UUIDIDMixin` 和 `BaseUserManager`，提供用户注册、验证、密码重置等逻辑。`on_after_register`、`on_after_forgot_password`、`on_after_request_verify` 等方法是事件钩子，可填充自定义业务逻辑。
- **`get_user_manager`**：FastAPI 依赖，实例化并提供 `UserManager`。
- **`bearer_transport`**：认证后端的传输方式，令牌通过 `Authorization: Bearer <token>` 传递。
- **`get_jwt_strategy`**：认证后端的策略，使用 JWT 作为令牌生成方式，有效期 1 小时。
- **`auth_backend`**：整合传输方式和策略的完整认证后端。
- **`fastapi_users`**：主类，整合 `get_user_manager` 和认证后端，用于生成路由和 `current_user` 依赖。
- **`current_active_user`**：检查请求中的令牌，验证用户身份并确保用户是活跃状态。

**注意**：在 `app` 文件夹下创建空的 `__init__.py` 文件，以便 Python 将其识别为一个包。

### 3. 运行项目与查看 Swagger UI

```bash
uv run fastapi dev
```

启动后访问 `http://localhost:8000/docs`，可以看到 `auth` 和 `users` 两个分组的路由。你可以尝试调用接口（注册 → 登录 → 访问受保护路由），初步体验 `FastAPI-Users` 的功能。

> 完整代码请移步 GitHub 项目：https://github.com/acelee0621/fastapi-users-turtorial

---

## 来源与归档

- 原始素材：[Archive/20250826_FastAPI-Users保姆级教程（一）：核心概念与快速上手.md](../../../Archive/20250826_FastAPI-Users保姆级教程（一）：核心概念与快速上手.md)
