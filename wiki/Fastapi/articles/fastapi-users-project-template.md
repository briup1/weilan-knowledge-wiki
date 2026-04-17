---
title: "FastAPI-Users 保姆级教程（六）：实战篇——构建包含用户认证的项目模板"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/hands-on", "type/tutorial", "FastAPI-Users", "项目模板", "实战"]
status: "archived"
references: "Archive/20250904_FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板.md"
---

# FastAPI-Users 保姆级教程（六）：实战篇——构建包含用户认证的项目模板

本文将带领大家从零开始，构建一个生产级、可复用的 FastAPI 用户认证模板项目。完成后，它既可以作为新项目的起点，也可以作为微服务架构中的独立用户认证服务。

## 第一步：项目初始化与环境配置

```bash
uv init
uv venv
source .venv/bin/activate
uv add "fastapi[standard]" 'fastapi-users[sqlalchemy]' aiosqlite asyncpg pydantic-settings
```

应用目录结构：

```
app/
  core/          # 核心逻辑 (配置, 数据库, 用户管理器)
  models/        # SQLAlchemy 模型
  schemas/       # Pydantic 模型
  lifespan.py    # 应用生命周期管理
  main.py        # FastAPI 应用入口
```

确保在 `core`, `models`, `schemas` 文件夹内都新建 `__init__.py` 文件。

## 第二步：智能化的应用配置 (`config.py`)

使用 `pydantic-settings` 设计配置文件，支持通过环境变量在 **PostgreSQL** 和 **SQLite** 之间一键切换。

```python
from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置（支持 PostgreSQL 和 SQLite，含连接池设置）"""

    APP_NAME: str = "FastAPI Users Template"
    DEBUG: bool = False

    DB_TYPE: Literal["postgres", "sqlite"] = "postgres"

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "fastapi_users"

    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600
    ECHO: bool = False

    SQLITE_PATH: str = "./db.sqlite3"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        elif self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"
        else:
            raise ValueError(f"Unsupported DB_TYPE: {self.DB_TYPE}")

    @computed_field
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict:
        if self.DB_TYPE == "postgres":
            return {
                "pool_size": self.POOL_SIZE,
                "max_overflow": self.MAX_OVERFLOW,
                "pool_timeout": self.POOL_TIMEOUT,
                "pool_recycle": self.POOL_RECYCLE,
                "echo": self.ECHO,
            }
        return {"echo": self.ECHO}

    JWT_SECRET: str = "CHANGE_ME"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

**设计亮点**：

- `DB_TYPE` 是配置"总开关"，自动适配后续所有数据库配置。
- `@computed_field` 让 `DATABASE_URL` 和 `SQLALCHEMY_ENGINE_OPTIONS` 根据 `DB_TYPE` 动态计算。
- 为 PostgreSQL 提供详尽的连接池参数，生产环境下自动适配；SQLite 自动剔除不支持的参数。
- `@lru_cache` 实现高效的单例模式。

## 第三步：健壮的数据库连接层 (`database.py`)

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from app.core.config import settings
from app.models.base import Base
from app.models.user import User, AccessToken

engine = create_async_engine(settings.DATABASE_URL, **settings.SQLALCHEMY_ENGINE_OPTIONS)
SessionFactory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session

# --- FastAPI Users 专用依赖 ---
async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_access_token_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
```

- `engine` 和 `SessionFactory` 作为模块级全局实例。
- `get_user_db` 和 `get_access_token_db` 依赖于通用的 `get_db`，数据库逻辑完全统一。

## 第四步：集中的用户认证核心 (`user_manager.py`)

```python
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from app.core.config import settings
from app.core.database import get_user_db, get_access_token_db
from app.models.user import User, AccessToken

SECRET = settings.JWT_SECRET

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"用户 {user.id} 已注册。")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_database_strategy(access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db)) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
```

**设计亮点**：

- `BearerTransport` + `DatabaseStrategy`：比纯 JWT 更安全，支持服务端 Token 失效（登出或修改密码后）。
- `current_active_user` 是 `fastapi_users.current_user()` 的实例，可通过 `active=True`、`verified=True`、`superuser=True` 创建不同权限级别的依赖。

## 第五步：应用生命周期管理 (`lifespan.py`)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import create_db_and_tables, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用启动，开始创建数据库表...")
    await create_db_and_tables()
    print("数据库表创建完成。")

    yield

    print("应用关闭，释放数据库连接池...")
    await engine.dispose()
    print("资源已释放。")
```

## 第六步：主应用与路由 (`main.py`)

```python
from fastapi import Depends, FastAPI
from app.core.config import settings
from app.core.user_manager import auth_backend, fastapi_users, current_active_user
from app.lifespan import lifespan
from app.models.user import User
from app.schemas.user import UserRead, UserCreate, UserUpdate

app = FastAPI(
    title=settings.APP_NAME,
    description="一个功能齐全的 FastAPI Users 模板",
    lifespan=lifespan,
)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"你好, {user.email}! 欢迎来到认证后的世界。"}
```

## 总结

这个模板的价值在于：

- **开箱即用**：配置 `.env`，一行命令即可启动完整的认证服务。
- **双库支持**：开发阶段用 SQLite，生产环境切换 PostgreSQL，无缝切换。
- **最佳实践**：集成异步数据库、依赖注入、分层架构等 FastAPI 社区公认的最佳实践。

后续可基于此模板：
- 集成 Alembic 进行数据库迁移管理。
- 编写 `on_after_...` 钩子，实现注册后发送欢迎邮件等业务逻辑。
- 添加 OAuth2，支持 Google、GitHub 等第三方登录。
- 容器化 (Dockerize)，为部署到云端做好准备。

> 完整代码请移步 GitHub 项目：https://github.com/acelee0621/users-template

---

## 来源与归档

- 原始素材：[Archive/20250904_FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板.md](../../../Archive/20250904_FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板.md)
