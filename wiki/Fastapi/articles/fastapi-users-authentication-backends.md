---
title: "FastAPI-Users 保姆级教程（三）：认证后端详解——传输方式与策略"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/tutorial", "type/concept", "FastAPI-Users", "认证", "JWT", "Cookie", "Redis"]
status: "archived"
references:
  - "Archive/20250828_FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy)上.md"
  - "Archive/20250829_FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy)下.md"
---

# FastAPI-Users 保姆级教程（三）：认证后端详解——传输方式与策略

FastAPI-Users 支持多认证后端并行工作。本章深入解析认证后端的两大核心组成部分：**传输方式（Transport）**和**策略（Strategy）**。

核心公式：

> **传输方式 (Transport) + 策略 (Strategy) = 认证后端 (Authentication Backend)**

FastAPI-Users 官方提供了 **2 种传输方式**和 **3 种策略**，可以自由组合出 6 种认证后端。

---

## 传输方式 (Transport)：令牌的信使

### 1. Bearer 传输

令牌通过 `Authorization: Bearer <token>` 请求头发送。

- ✅ 优点：易于在每个请求中阅读和设置。
- ❌ 缺点：需要在客户端手动存储（如 `localStorage`）。
- ➡️ 建议场景：移动应用或纯 REST API。

```python
from fastapi_users.authentication import BearerTransport

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
```

参数 `tokenUrl` 指定登录端点路径，让 Swagger UI 自动发现 "Authorize" 按钮。

### 2. Cookie 传输

令牌通过 HTTP Cookie 发送。

- ✅ 优点：由浏览器自动、安全地存储和发送。
- ❌ 缺点：需要配合 CSRF 保护；在浏览器环境外工作困难。
- ➡️ 建议场景：Web 前端应用。

```python
from fastapi_users.authentication import CookieTransport

cookie_transport = CookieTransport(cookie_max_age=3600)
```

**CookieTransport 配置参数**：

- `cookie_name` (默认: "fastapiusersauth")：Cookie 名称。
- `cookie_max_age` (默认: `None`)：生命周期（秒）。`None` 表示会话 Cookie，浏览器关闭后失效。
- `cookie_path` (默认: "/")：有效路径。
- `cookie_domain` (默认: `None`)：有效域名。
- `cookie_secure` (默认: `True`)：是否仅通过 HTTPS 发送。
- `cookie_httponly` (默认: `True`)：阻止 JavaScript 访问，防止 XSS。
- `cookie_samesite` (默认: "lax")：CSRF 防御策略。

---

## 策略 (Strategy)：令牌的大脑

### 1. JWT 策略

JSON Web Token (JWT) 是目前应用最广泛的令牌策略，优点是**简单、无状态、易于横向扩展**。缺点是令牌一旦签发，在有效期内无法从服务端强制使其失效。

```python
from fastapi_users.authentication import JWTStrategy

SECRET = "YOUR_SUPER_SECRET_KEY"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)
```

**JWTStrategy 参数**：

- `secret` (str)：编码令牌的密钥。
- `lifetime_seconds` (int)：令牌生命周期（秒）。
- `token_audience` (List[str], 默认: `["fastapi-users:auth"]`)。
- `algorithm` (str, 默认: `"HS256"`)。
- `public_key` (str)：如果使用 RS256 等需要密钥对的算法，提供公钥。

**策略为什么要放在函数里？**

> 为了允许策略能够与其他依赖项动态实例化，它们必须作为可调用对象（callable）提供给认证后端。

**RS256 算法示例**：

```python
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----"""

PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"""

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=PRIVATE_KEY,
        lifetime_seconds=3600,
        algorithm="RS256",
        public_key=PUBLIC_KEY,
    )
```

### 2. 数据库策略 (Database Strategy)

将令牌存储在应用数据库中，是最"自然"的方式。

- ✅ 优点：无需额外服务；登出时可直接删除令牌使其立即失效。
- ❌ 缺点：配置稍繁琐；高并发下对数据库有一定压力。

#### SQLAlchemy 配置

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,
)

class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass

async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
```

默认 `user_id` 外键为 UUID。若使用整数 ID：

```python
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable

class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
```

#### Beanie (MongoDB) 配置

```python
from beanie import Document
from fastapi_users_db_beanie.access_token import (
    BeanieAccessTokenDatabase,
    BeanieBaseAccessToken,
)

class AccessToken(BeanieBaseAccessToken, Document):
    pass

async def get_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)
```

**提示**：自定义配置需继承 `BeanieBaseAccessToken.Settings`，并将 `AccessToken` 模型加入 `init_beanie` 的 `document_models` 数组。

#### 定义数据库策略

```python
from fastapi import Depends
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)
```

登出时，此策略会自动删除数据库中对应的令牌。

### 3. Redis 策略 (Redis Strategy)

Redis 是基于内存的高性能键值存储，是令牌管理的理想选择。

```bash
pip install "fastapi-users[redis]"
```

```python
import redis.asyncio
from fastapi_users.authentication import RedisStrategy

redis_client = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)

def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis_client, lifetime_seconds=3600)
```

**RedisStrategy 参数**：

- `redis` (`redis.asyncio.Redis`)：**务必将 `decode_responses` 设置为 `True`**。
- `lifetime_seconds` (Optional[int])：令牌生命周期，默认 `None`（永不过期）。
- `key_prefix` (str, 默认: `"fastapi_users_token:"`)。

---

## 创建认证后端 (AuthenticationBackend)

将传输方式和策略组合起来：

```python
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

SECRET = "SECRET"

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
```

**AuthenticationBackend 参数**：

- `name` (str)：后端名称，**必须唯一**。
- `transport` (Transport)：传输类实例。
- `get_strategy` (Callable[..., Strategy])：返回策略实例的可调用对象。

你可以同时拥有任意数量的认证后端，然后将它们传递给 `FastAPIUsers` 实例：

```python
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
```

### 实战：Cookie 传输 + JWT 策略

```python
cookie_transport = CookieTransport(cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt_cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
```

登录成功后会返回 `StatusCode: 204` 和 `Set-Cookie` 头：

```http
Set-Cookie: fastapiusersauth=eyJ...; HttpOnly; Max-Age=3600; Path=/; SameSite=lax; Secure
```

> 完整代码请移步 GitHub 项目：https://github.com/acelee0621/fastapi-users-turtorial

---

## 来源与归档

- 原始素材：
  - [Archive/20250828_FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy)上.md](../../../Archive/20250828_FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy)上.md)
  - [Archive/20250829_FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy)下.md](../../../Archive/20250829_FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy)下.md)
