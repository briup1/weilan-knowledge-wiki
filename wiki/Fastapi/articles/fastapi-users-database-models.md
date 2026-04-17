---
title: "FastAPI-Users 保姆级教程（二）：深入用户模型与数据库集成"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/tutorial", "type/concept", "FastAPI-Users", "SQLAlchemy", "MongoDB", "Beanie"]
status: "archived"
references: "Archive/20250827_FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成.md"
---

# FastAPI-Users 保姆级教程（二）：深入用户模型与数据库集成

本文深入解析 FastAPI-Users 官方文档中的 **User model and databases** 章节，涵盖 SQLAlchemy（关系型数据库）和 Beanie（MongoDB）两大数据库适配方案。

## 第一站：SQLAlchemy 与关系型数据库

FastAPI Users 借助 SQLAlchemy 的异步 ORM 功能，提供了操作 SQL 数据库所需的一切工具。

### 1. 安装异步驱动

- **PostgreSQL**：`uv add asyncpg`，连接字符串：`postgresql+asyncpg://user:password@host:port/name`
- **SQLite**：`uv add aiosqlite`，连接字符串：`sqlite+aiosqlite:///name.sqlite3`
- **MySQL**：`uv add asyncmy`，连接字符串：`mysql+asyncmy://user:password@host:port/db?charset=utf8mb4`

### 2. 重要提醒：`expire_on_commit`

在使用 SQLAlchemy 的异步会话 (`AsyncSession`) 时，必须将 `expire_on_commit` 设置为 `False`，以避免事务提交后因自动过期刷新引发死锁或连接错误。

```python
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
```

### 3. 创建用户模型 (User Model)

```python
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

class User(SQLAlchemyBaseUserTableUUID, Base):
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
```

`SQLAlchemyBaseUserTableUUID` 默认使用 **UUID** 作为主键 ID。如果你偏爱自增整数 ID，可以这样做：

```python
from sqlalchemy import Integer
from fastapi_users.db import SQLAlchemyBaseUserTable

class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
```

### 4. 创建数据库适配器 (Database Adapter)

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
```

依赖链条：`路由` → `get_user_db` → `get_async_session` → `SQLAlchemyUserDatabase` 适配器实例。

## 第二站：Beanie 与 MongoDB

### 1. 安装与连接

```bash
uv add "fastapi-users[beanie]"
```

```python
import motor.motor_asyncio
from beanie import Document
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["my_app_db"]

class User(BeanieBaseUser, Document):
    class Settings:
        name = "accounts"  # 自定义集合名称
```

**官方提示**：
- 自定义配置必须在模型内部创建 `Settings` 类。
- `BeanieBaseUser` 会自动在 `id` 和 `email` 字段上创建唯一索引。

### 2. 创建数据库适配器

```python
async def get_user_db():
    yield BeanieUserDatabase(User)
```

### 3. 初始化 Beanie

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from beanie import init_beanie
from .db import db, User

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[User],
    )
    yield

app = FastAPI(lifespan=lifespan)
```

### 实战演练与总结

将项目切换到 MongoDB 只需两步：
1. 将 `db.py` 替换为使用 Beanie 的版本。
2. 在 `schemas.py` 和 `user_manager.py` 中，将用户 ID 类型提示从 `UUID` 修改为 MongoDB 的 `ObjectId`。

一旦数据库层设置完毕，后续上层的业务逻辑代码几乎是完全相同的。

> 完整代码请移步 GitHub 项目：https://github.com/acelee0621/fastapi-users-turtorial

---

## 来源与归档

- 原始素材：[Archive/20250827_FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成.md](../../../Archive/20250827_FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成.md)
