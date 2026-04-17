# FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板

# **FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板**

大家好，欢迎回到 FastAPI-Users 保姆级教程系列！🚀

> 在之前的文章里，我们对官方文档做了全面解析，基本了解了  `FastAPI-Users`  的运作原理。理论已经完备，是时候付诸实践了！

今天，我们将进入激动人心的  **实战环节**  。我将带领大家从零开始，构建一个生产级、可复用的用户认证模板项目。

### 为什么说它是“终极模板”？

这个项目完成后，它将是你未来开发的得力助手：

1. 1.
   **高度可复用**
   ：任何新项目需要用户认证，都可以直接以此为模板，在其上添砖加瓦。
2. 2.
   **微服务架构核心**
   ：你可以将此项目作为一个独立的用户认证
   **微服务**
   。其他服务通过
   `HTTP`
   客户端（如
   `httpx`
   ）与它通信，实现整个系统的统一认证。

话不多说，我们直接开始！为了照顾所有朋友，我将从一个全新的项目开始，带大家从头完整地走一遍流程。

## 第一步：项目初始化与环境配置

首先，建立项目文件夹，然后执行以下命令初始化环境并安装依赖：

```
uv init  
uv venv  

# 激活虚拟环境  

source .venv/bin/activate  

# 安装所有必需的包  

uv add "fastapi[standard]" 'fastapi-users[sqlalchemy]' aiosqlite asyncpg pydantic-settings
```

接着，创建我们的应用目录结构：

```
app/  
  core/          # 核心逻辑 (配置, 数据库, 用户管理器)  

  models/        # SQLAlchemy 模型  

  schemas/       # Pydantic 模型  

  lifespan.py    # 应用生命周期管理  

  main.py        # FastAPI 应用入口

```

确保在  `core`  ,  `models`  ,  `schemas`  文件夹内都新建一个  `__init__.py`  文件。

---

## 第二步：智能化的应用配置 ( `config.py` )

这次实战的第一个亮点，就是我们高度灵活的配置文件。它使用  `pydantic-settings`  设计，可以轻松通过环境变量在  **PostgreSQL**  和  **SQLite**  之间一键切换。

这是我们的配置文件代码：

```

# /app/core/config.py  

from functools import lru_cache  
from typing import Literal  
  
from pydantic import computed_field  
from pydantic_settings import BaseSettings, SettingsConfigDict  

class Settings(BaseSettings):  
    """应用配置（支持 PostgreSQL 和 SQLite，含连接池设置）"""  
  
    APP_NAME: str = "FastAPI Users Template"  
    DEBUG: bool = False  
  
    # 数据库类型  

    DB_TYPE: Literal["postgres", "sqlite"] = "postgres"  
  
    # PostgreSQL 配置  

    DB_HOST: str = "localhost"  
    DB_PORT: int = 5432  
    DB_USER: str = "postgres"  
    DB_PASSWORD: str = "postgres"  
    DB_NAME: str = "fastapi_users"  
  
    # 连接池配置（仅 Postgres 有效）  

    POOL_SIZE: int = 20  
    MAX_OVERFLOW: int = 10  
    POOL_TIMEOUT: int = 30  
    POOL_RECYCLE: int = 3600  
    ECHO: bool = False  
  
    # SQLite 配置  

    SQLITE_PATH: str = "./db.sqlite3"  
  
    @computed_field  
    @property  
    def DATABASE_URL(self) -> str:  
        if self.DB_TYPE == "postgres":  
            return (  
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"  
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  
            )  
        elif self.DB_TYPE == "sqlite":  
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"  
        else:  
            raise ValueError(f"Unsupported DB_TYPE: {self.DB_TYPE}")  
  
    @computed_field  
    @property  
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict:  
        """统一封装 engine options，供 create_async_engine 使用"""  
        if self.DB_TYPE == "postgres":  
            return {  
                "pool_size": self.POOL_SIZE,  
                "max_overflow": self.MAX_OVERFLOW,  
                "pool_timeout": self.POOL_TIMEOUT,  
                "pool_recycle": self.POOL_RECYCLE,  
                "echo": self.ECHO,  
            }  
        # SQLite 不支持 pool 设置，返回最小参数  

        return {"echo": self.ECHO}  
  
    # JWT 配置  

    JWT_SECRET: str = "CHANGE_ME"  
  
    model_config = SettingsConfigDict(  
        env_file=".env",  
        env_file_encoding="utf-8",  
        case_sensitive=False,  
    )  

@lru_cache  
def get_settings() -> Settings:  
    return Settings()  

settings = get_settings()
```

#### **✨ 代码解析：**

- •  **`DB_TYPE: Literal[...]`**  ：这是整个配置的“总开关”。你只需在  `.env`  文件中将  `DB_TYPE`  设置为  `postgres`  或  `sqlite`  ，后续所有配置都会自动适配，非常优雅。
- •  **`@computed_field`**  ：这是  `Pydantic v2`  的一大亮点。  `DATABASE_URL`  和  `SQLALCHEMY_ENGINE_OPTIONS`  不再是静态配置项，而是根据  `DB_TYPE`  **动态计算**  出来的属性。这种设计让配置更智能，避免了在代码其他地方写  `if/else`  来判断数据库类型。
- •  **精细化连接池配置**  ：我们为 PostgreSQL 提供了详尽的连接池参数（  `POOL_SIZE`  ,  `MAX_OVERFLOW`  等），这对于生产环境下的性能调优至关重要。同时，当  `DB_TYPE`  为  `sqlite`  时，  `SQLALCHEMY_ENGINE_OPTIONS`  会自动剔除这些不支持的参数，表现出极佳的健壮性。
- •  **`@lru_cache`**  ：通过缓存  `get_settings()`  的结果，确保  `Settings`  类在应用生命周期内只被实例化一次，实现了高效的单例模式。

---

## 第三步：健壮的数据库连接层 ( `database.py` )

接下来，我们定义数据库连接、会话管理以及  `FastAPI-Users`  所需的依赖。那么之前的文章里写过更加健全的数据库连接设置，这里使用简化版的，这个项目可以去我仓库里看完整代码：

```

# app/core/database.py  

from typing import AsyncGenerator  
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession  
from fastapi import Depends  
from fastapi_users.db import SQLAlchemyUserDatabase  
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase  
  
from app.core.config import settings  
from app.models.base import Base  # 确保所有模型都继承自这个 Base  

from app.models.user import User, AccessToken  
  

# 创建异步引擎和会话工厂  

engine = create_async_engine(settings.DATABASE_URL, **settings.SQLALCHEMY_ENGINE_OPTIONS)  
SessionFactory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)  
  
async def create_db_and_tables():  
    """在应用启动时创建数据库表（如果不存在）"""  
    async with engine.begin() as conn:  
        await conn.run_sync(Base.metadata.create_all)  
  
async def get_db() -> AsyncGenerator[AsyncSession, None]:  
    """为每个请求提供一个数据库会话的依赖"""  
    async with SessionFactory() as session:  
        yield session  
  

# --- FastAPI Users 专用依赖 ---  

async def get_user_db(session: AsyncSession = Depends(get_db)):  
    yield SQLAlchemyUserDatabase(session, User)  
  
async def get_access_token_db(session: AsyncSession = Depends(get_db)):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
```

### **✨ 代码评析：**

- •  **全局实例**  ：我们将  `engine`  和  `SessionFactory`  作为模块级别的全局实例。这种模式简洁明了，并通过  `lifespan`  事件确保它们在应用启动时被正确初始化。
- •  **依赖解耦**  ：  `get_user_db`  和  `get_access_token_db`  依赖于通用的  `get_db`  。这意味着  `FastAPI-Users`  的数据库逻辑与我们应用自身的数据库会话管理完全统一，便于维护。

---

## 第四步：集中的用户认证核心 ( `user_manager.py` )

这是  `FastAPI-Users`  的大脑所在，我们将所有认证相关的配置都集中于此。

```

# app/core/user_manager.py  

import uuid  
from typing import Optional  
from fastapi import Depends, Request  
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin  
from fastapi_users.authentication import AuthenticationBackend, BearerTransport  
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy  
  
from app.core.config import settings  
from app.core.database import get_user_db, get_access_token_db  
from app.models.user import User, AccessToken  
  
SECRET = settings.JWT_SECRET  
  
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):  
    reset_password_token_secret = SECRET  
    verification_token_secret = SECRET  
  
    async def on_after_register(self, user: User, request: Optional[Request] = None):  
        print(f"用户 {user.id} 已注册。")  
    # ... 其他 on_after_... 事件钩子  

  
async def get_user_manager(user_db=Depends(get_user_db)):  
    yield UserManager(user_db)  
  
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")  
  
def get_database_strategy(access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db)) -> DatabaseStrategy:  
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)  
  
auth_backend = AuthenticationBackend(  
    name="jwt",  
    transport=bearer_transport,  
    get_strategy=get_database_strategy,  
)  
  
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])  
  

# --- 导出一个易于使用的依赖 ---  

current_active_user = fastapi_users.current_user(active=True)
```

### **✨ 代码解析：**

- •  **`BearerTransport`  +  `DatabaseStrategy`**  ：我们选用了最经典的组合——通过  `Bearer Token`  进行传输，并将  `Token`  存储在数据库中。这比纯  `JWT`  更安全，因为它支持服务端  `Token`  失效（例如，用户登出或修改密码后）。
- •  **`current_active_user`**  ：在之前的文章中，我们遗漏了这一点。  `fastapi_users.current_user()`  是一个强大的依赖项生成器。我们可以通过设置参数（如  `active=True`  ,  `verified=True`  ,  `superuser=True`  ）来创建不同权限级别的用户依赖。这里我们导出一个最常用的  `current_active_user`  ，可以直接在需要登录的路由中使用。

* •  **应用场景**  ：比如，一个公开的API可能只需要用户登录 (  `current_active_user`  )；但修改个人资料、发表评论等敏感操作，则可能要求用户必须通过邮箱验证 (  `current_active_verified_user`  )；而访问管理后台，则必须是超级管理员 (  `current_superuser`  )。我们预置的这些依赖，在定义路由时可以像菜单一样按需选用，极大地提升了开发效率和代码清晰度。

---

## 第五步：应用生命周期管理 ( `lifespan.py` )

最后，我们用  `lifespan`  串联起数据库的初始化与关闭，并在  `main.py`  中组装应用。

```

# app/lifespan.py  

from contextlib import asynccontextmanager  
from fastapi import FastAPI  
from app.core.database import create_db_and_tables, engine  
  
@asynccontextmanager  
async def lifespan(app: FastAPI):  
    # -------- 启动 --------  

    print("🚀 应用启动，开始创建数据库表...")  
    await create_db_and_tables()  
    print("✅ 数据库表创建完成。")  
    
    yield  
    
    # -------- 关闭 --------  

    print("应用关闭，释放数据库连接池...")  
    await engine.dispose()  
    print("✅ 资源已释放。")
```

## 第六步：主应用与路由 ( `main.py` )

```

# app/main.py  

from fastapi import Depends, FastAPI  
from app.core.config import settings  
from app.core.user_manager import auth_backend, fastapi_users, current_active_user  
from app.lifespan import lifespan  
from app.models.user import User  
from app.schemas.user import UserRead, UserCreate, UserUpdate  
  
app = FastAPI(  
    title=settings.APP_NAME,  
    description="一个功能齐全的 FastAPI Users 模板",  
    lifespan=lifespan,  
)  
  

# --- 引入 FastAPI-Users 路由 ---  

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])  
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])  
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])  
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])  
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])  
  

# --- 其他自定义路由 ---  

@app.get("/health")  
def health_check():  
    return {"status": "ok 👍"}  
  
@app.get("/authenticated-route")  
async def authenticated_route(user: User = Depends(current_active_user)):  
    return {"message": f"你好, {user.email}! 欢迎来到认证后的世界。"}
```

**关于  `models`  和  `schemas`**   
 我没有详细写  `models`  和  `schemas`  的代码，这是因为它们基本是标准实现。大家只要按照官方文档或者我们之前文章里的最小实现来写入就可以了。

---

## 总结

恭喜你！我们已经成功构建了一个结构清晰、功能完备且高度可扩展的  `FastAPI`  用户认证模板。它不仅仅是一个教程示例，更是一个可以直接用于生产环境的坚实起点。

这个模板的价值在于：

- •
  **开箱即用**
  ：克隆仓库，配置
  `.env`
  ，一行命令即可启动一个完整的认证服务。
- •
  **双库支持**
  ：无论是开发阶段的轻量级
  `SQLite`
  ，还是生产环境的高性能
  `PostgreSQL`
  ，都能无缝切换。
- •
  **最佳实践**
  ：集成了异步数据库、依赖注入、分层架构等
  `FastAPI`
  社区的公认最佳实践。

接下来，你可以基于这个模板：

- •
  **集成 Alembic**
  进行数据库迁移管理。
- •
  **编写
  `on_after_...`
  钩子**
  ，实现注册后发送欢迎邮件等业务逻辑。
- •
  **添加 OAuth2**
  ，支持Google、GitHub 等第三方登录。
- • 将其
  **容器化 (Dockerize)**
  ，为部署到云端做好准备。

希望这个实战教程能真正成为你开发工具箱中的一部分。  `FastAPI-Users`  的探索之旅告一段落，将来我可能基于这个模板，进一步探讨如何将其作为微服务使用，或者如何在其上扩展更复杂的业务功能。

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/users-template

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDGJIhz9llqDVbum2Q0tdmO19XzDjAAGrPQlFlLZUAatWA3eJvbmxupA/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)