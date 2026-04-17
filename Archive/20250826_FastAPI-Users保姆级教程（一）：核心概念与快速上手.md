# FastAPI-Users保姆级教程（一）：核心概念与快速上手

# **FastAPI-Users保姆级教程（一）：核心概念与快速上手**

大家好，欢迎来到我们的 FastAPI 项目实战新的合集系列 —— FastAPI Users 教程合集！🚀

在现代 Web 应用开发中，用户认证（User Authentication）是不可或缺的一环。本系列教程将聚焦于 FastAPI 生态中一个久负盛名的用户认证库：  `FastAPI-Users`  。我们的目标是理论与实践相结合，通过深入解读其官方文档的精髓，并配合实际项目代码教学，手把手教会你如何利用  `FastAPI-Users`  为你的 FastAPI 应用构建一套强大且灵活的用户认证模块。通过本系列，你不仅能掌握如何快速上手，更能理解其内部模块的功能与用法，从而能够根据自身项目的具体需求，自由选择并组合出最贴合业务场景的用户认证方案。

你可能会好奇，市面上教程那么多，为什么还要写  `FastAPI-Users`  呢？  `FastAPI-Users`  作为一款老牌开源用户认证库，当前版本已迭代至  `14.0.1`  ，其功能之完善、结构之稳健可见一斑。然而，它也存在一些令初学者望而却步的痛点：最主要的是  **缺乏官方中文文档**  ，其次部分概念较为抽象，阅读体验不够友好，甚至在 Reddit 上也有不少用户抱怨其文档理解门槛较高。我在初学使用时，也曾遇到过类似困境：网上找到的教程往往不够细致，知其然而不知其所以然，代码能跑起来却不理解其工作原理，导致想要根据实际需求进行修改时，因缺乏底层理解而无从下手。

因此，本教程系列旨在从整体到细节，带领大家基于官方文档，逐步理解  `FastAPI-Users`  的工作模式。一旦你掌握了它的运作机制，无论是日常使用还是按需定制，都将变得游刃有余。

事不宜迟，首先呈上  `FastAPI-Users`  项目的官方文档与 GitHub 地址，感兴趣的小伙伴也可自行研读原文：

- •
  **官方文档 (
  `Documentation`
  )**
  : https://fastapi-users.github.io/fastapi-users/
- •
  **源代码 (
  `Source Code`
  )**
  : https://github.com/fastapi-users/fastapi-users

---

## FastAPI-Users：核心概念概览

那么，  `FastAPI-Users`  究竟是什么？它能为我们实现哪些功能呢？

根据其官方文档的介绍：

> 为你的 FastAPI 项目快速添加注册和认证系统。  **FastAPI Users**  旨在尽可能地实现可定制（  `customizable`  ）和适应性（  `adaptable`  ）。

简而言之，它提供了一套完整的用户注册与认证解决方案，并且强调高度的灵活性和可扩展性。

它具体包含了哪些功能呢？让我们看看官方文档中对其核心特性（  `Features`  ） 的描述：

- •
  **可扩展的基础用户模型 (
  `Extensible base user model`
  )**
  ：允许开发者根据需求自由扩展用户字段。
- •
  **开箱即用的路由 (
  `Ready-to-use routes`
  )**
  ：提供注册（
  `register`
  ）、登录（
  `login`
  ）、重置密码（
  `reset password`
  ）和验证邮箱（
  `verify e-mail`
  ）等常用认证路由。
- •
  **开箱即用的社交 OAuth2 登录流程 (
  `Ready-to-use social OAuth2 login flow`
  )**
  ：支持集成通过 OAuth2 进行的社交登录。
- •
  **依赖注入可调用对象 (
  `Dependency callables`
  )**
  ：能够将当前用户（
  `current user`
  ）注入到你的路由中。
- •
  **可插拔的密码验证 (
  `Pluggable password validation`
  )**
  ：允许自定义密码验证规则。
- •
  **可定制的数据库后端 (
  `Customizable database backend`
  )**
  ：

* • 内置支持
  **SQLAlchemy ORM 异步模式 (
  `async`
  )**
  ，兼容 PostgreSQL、SQLite、MySQL 等关系型数据库。
* • 内置支持
  **MongoDB 及 Beanie ODM (
  `Beanie ODM`
  )**
  ，用于非关系型数据库。
* • 目前暂不支持其他 ORM 工具。

- •
  **多种可定制的认证后端 (
  `Multiple customizable authentication backends`
  )**
  ：

* •
  **传输方式 (
  `Transports`
  )**
  ：支持
  `Authorization`
  头（
  `header`
  ）、
  `Cookie`
  等方式传递认证信息。
* •
  **策略 (
  `Strategies`
  )**
  ：支持
  `JWT`
  (JSON Web Token)、数据库（
  `Database`
  ）、Redis 等多种令牌（
  `token`
  ）生成和管理策略。

- •
  **完整的 OpenAPI 模式支持 (
  `Full OpenAPI schema support`
  )**
  ：即使使用多个认证后端也能良好支持。

---

## `FastAPI-Users` 的五大核心模块

`FastAPI-Users`  的功能是基于以下五个主要模块构建的：

1. 1.
   **用户模型及数据库适配器 (
   `User model and database adapters`
   )**
     
   这个模块负责处理用户数据的存储。目前，
   `FastAPI-Users`
   通过整合
   `SQLAlchemy`
   来支持 PostgreSQL、SQLite、MySQL 等多种关系型数据库，并支持异步操作。此外，它也通过
   `Beanie`
   库来支持
   `MongoDB`
   这类非关系型数据库。值得注意的是，当前版本对于其他的 ORM 工具（如 ORM
   `Peewee`
   、
   `PonyORM`
   等）尚未提供直接支持。
2. 2.
   **认证后端 (
   `Authentication backends`
   )**
     
   认证后端定义了应用中用户会话（
   `session`
   ）的管理方式，例如通过访问令牌（
   `access tokens`
   ）或
   `cookies`
   。
     
   官方文档对它的工作方式是这样描述的：
   > 认证后端定义了您的应用程序中用户会话 (  `users sessions`  ) 的管理方式，例如访问令牌 (  `access tokens`  ) 或  `cookies`  。   
   >  它们由两部分组成：  `传输方式`  （  `transport`  ），即令牌 (  `token`  ) 如何通过请求携带（例如  `cookies`  、请求头  `headers`  ...），以及  `策略`  （  `strategy`  ），即令牌如何生成和保护（例如  `JWT`  、数据库中的令牌...）。

   简单来说，  `传输方式`  决定了令牌怎样在客户端和服务端之间传递，而  `策略`  则决定了令牌自身的生命周期管理与安全性。
3. 3.
   **用户管理器 (
   `UserManager`
   )**
     
   用户管理器是
   `FastAPI-Users`
   库的核心配置中心，它承载了
   `FastAPI-Users`
   的大部分业务逻辑，也是将各个模块连接起来的“枢纽”。
     
   官方文档对此的介绍是：
   > `UserManager`  对象承载了  `FastAPI Users`  的大部分逻辑：注册 (  `registration`  )、验证 (  `verification`  )、密码重置 (  `password reset`  )... 我们提供了一个带有这些通用逻辑的  `BaseUserManager`  ；您应该继承并重载 (  `overload`  ) 它来定义如何验证密码或处理事件 (  `handle events`  )。   
   >  这个  `UserManager`  对象应该通过 FastAPI 依赖（  `FastAPI dependency`  ），即  `get_user_manager`  来提供。

   `UserManager`  包含了例如用户注册、密码验证、重置密码、邮箱验证等核心功能。我们将通过继承  `BaseUserManager`  来定制化这些逻辑，例如添加用户注册后的欢迎邮件发送、密码重置流程中的安全校验等。
4. 4.
   **Pydantic 模型 (
   `Schemas`
   )**
     
   对于 FastAPI 开发者而言，
   `Pydantic`
   模型无疑是处理请求负载（
   `request payloads`
   ）验证和响应序列化（
   `serialize responses`
   ）的得力工具。
   `FastAPI-Users`
   也不例外，它要求你提供
   `Pydantic schemas`
   来表示用户在被读取（
   `read`
   ）、创建（
   `created`
   ）和更新（
   `updated`
   ）时的不同数据结构。这与我们日常使用 FastAPI 的习惯完全一致。
5. 5.
   **`FastAPIUsers`
   和路由 (
   `routers`
   )**
     
   这个模块与 FastAPI 中的路由概念保持一致。
   `FastAPI-Users`
   提供了预定义的路由，例如用户注册、登录、验证账户、重置密码等常用功能。同时，它也提供了
   `current_user`
   依赖工厂（
   `dependency factory`
   ），以便你在自己的路由中轻松注入已认证的用户信息。

   官方文档的解释是：

   > 最后，  `FastAPIUsers`  对象是主类（  `main class`  ），你可以从中生成用于经典路由（如注册或登录）的路由器（  `routers`  ），还可以获取  `current_user`  依赖工厂（  `dependency factory`  ）以将已认证用户注入到你自己的路由中。

---

## 快速上手：最小化实现示例

了解了  `FastAPI-Users`  的核心概念和模块划分后，我们立刻进入实战环节。遵循“少说多练”的原则，我们将从官方文档提供的最小化实现示例入手，通过一个最简单的用例来感受  `FastAPI-Users`  的魅力。当然，你也可以从我的 GitHub 仓库拉取本教程的完整代码。

这个示例非常简洁，仅包含四个文件，却能搭建起一个基本的用户认证系统。

### 1. 项目初始化

首先，我们创建一个名为  `fastapi-users-tutorial`  的项目文件夹，然后使用  `uv`  工具初始化项目、设置虚拟环境并安装必要的依赖包：

```
cd fastapi-users-tutorial  
uv init  
uv venv  
uv add "fastapi[standard]" "fastapi-users[sqlalchemy]" aiosqlite
```

这些命令会为我们创建项目骨架，激活虚拟环境，并安装  `fastapi`  （包含标准依赖）、  `fastapi-users`  （并指定  `sqlalchemy`  适配器）以及  `aiosqlite`  （一个异步 SQLite 驱动）。

### 2. 构建项目文件

接着，在项目根目录下创建一个  `app`  文件夹，并在其中创建以下四个文件：

#### `app/main.py`

```
from contextlib import asynccontextmanager  
  
from fastapi import Depends, FastAPI  
  
from app.db import User, create_db_and_tables  
from app.schemas import UserCreate, UserRead, UserUpdate  
from app.users import auth_backend, current_active_user, fastapi_users  

@asynccontextmanager  
async def lifespan(app: FastAPI):  
    # Not needed if you setup a migration system like Alembic  

    await create_db_and_tables()  
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
async def authenticated_route(user: User = Depends(current_active_user)):  
    return {"message": f"Hello {user.email}!"}
```

我们的主文件  `main.py`  看起来非常简洁。它充分体现了 FastAPI 应用的模块化思想。   
 可以看到，这里引入了  `fastapi-users`  提供的五个核心路由生成器：

- •
  `fastapi_users.get_auth_router(auth_backend)`
  : 用于处理用户认证（
  `authentication`
  ），例如登录等。
- •
  `fastapi_users.get_register_router(UserRead, UserCreate)`
  : 用于用户注册（
  `registration`
  ）。
- •
  `fastapi_users.get_reset_password_router()`
  : 用于用户重置密码（
  `reset password`
  ）。
- •
  `fastapi_users.get_verify_router(UserRead)`
  : 用于用户账户验证（
  `verify account`
  ）。
- •
  `fastapi_users.get_users_router(UserRead, UserUpdate)`
  : 用于用户管理，包括获取当前用户信息以及更新用户资料。

这些路由器都被挂载在  `/auth`  或  `/users`  前缀下，并进行了  `tags`  分类，这在  `Swagger UI`  中会非常直观。

此外，代码中还包含了一个受保护的示例路由  `/authenticated-route`  ，它通过  `Depends(current_active_user)`  依赖声明，确保只有活跃（  `active`  ）用户才能访问。

在应用生命周期管理（  `lifespan`  ）函数中，我们调用了  `create_db_and_tables()`  函数，这顾名思义是用于创建数据库表的。与其他导入类似，  `User`  模型、  `schemas`  以及  `auth_backend`  、  `current_active_user`  、  `fastapi_users`  等核心组件都从项目内部的其他文件导入。对于熟悉 FastAPI 的开发者来说，  `main.py`  的结构应该不难理解。

#### `app/db.py`

```
from collections.abc import AsyncGenerator  
  
from fastapi import Depends  
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase  
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  
from sqlalchemy.orm import DeclarativeBase  
  
DATABASE_URL = "sqlite+aiosqlite:///./test.db"  

class Base(DeclarativeBase):  
    pass  

class User(SQLAlchemyBaseUserTableUUID, Base):  
    pass  

engine = create_async_engine(DATABASE_URL)  
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)  

async def create_db_and_tables():  
    async with engine.begin() as conn:  
        await conn.run_sync(Base.metadata.create_all)  

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:  
    async with async_session_maker() as session:  
        yield session  

async def get_user_db(session: AsyncSession = Depends(get_async_session)):  
    yield SQLAlchemyUserDatabase(session, User)
```

`db.py`  文件主要负责数据库相关的配置和操作。

- • 它定义了
  `DATABASE_URL`
  ，这里为了简单起见，我们使用了异步 SQLite 数据库 (
  `sqlite+aiosqlite:///./test.db`
  )。
- •
  `Base`
  类继承自
  `SQLAlchemy`
  的
  `DeclarativeBase`
  ，是所有 ORM 模型的基类。
- •
  `User`
  模型继承自
  `SQLAlchemyBaseUserTableUUID`
  和
  `Base`
  。
  `SQLAlchemyBaseUserTableUUID`
  是
  `fastapi-users`
  提供的一个基础用户表模型，它预置了用户认证所需的核心字段，并且使用
  `UUID`
  作为用户 ID 类型。
- •
  `engine`
  和
  `async_session_maker`
  用于创建异步数据库连接和会话。
- •
  `create_db_and_tables()`
  函数负责创建数据库表。
- •
  `get_async_session()`
  是一个 FastAPI 依赖函数，它提供了异步数据库会话，作用类似于我们常用的
  `get_db()`
  函数。
- •
  `get_user_db()`
  是
  `fastapi-users`
  专有的一个依赖函数，它依赖于
  `get_async_session()`
  来获取数据库会话，并返回一个
  `SQLAlchemyUserDatabase`
  实例，这是
  `fastapi-users`
  用来与
  `SQLAlchemy`
  用户模型进行交互的关键适配器。

值得注意的是，这里的  `User`  模型内部直接  `pass`  了，这意味着我们没有添加任何自定义字段。  `fastapi-users`  库的默认用户模型已经包含了以下核心字段，这是他的源代码中对于默认用户字段的定义：

```
email: Mapped[str] = mapped_column(  
        String(length=320), unique=True, index=True, nullable=False  
    )  
hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)  
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  
is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  
is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

这里需要提醒大家，  `fastapi-users`  默认使用邮箱作为用户名格式，这非常符合现代  `Web`  应用的设计理念，因为邮箱可以方便地用于用户验证、通知、密码重置和账户激活等多种业务逻辑。如果你需要为用户添加额外的字段（如昵称、头像等），可以在  `User`  类中进行扩展。

#### `app/schemas.py`

```
import uuid  
  
from fastapi_users import schemas  
  
class UserRead(schemas.BaseUser[uuid.UUID]):  
    pass  
  
class UserCreate(schemas.BaseUserCreate):  
    pass  
  
class UserUpdate(schemas.BaseUserUpdate):  
    pass
```

`schemas.py`  文件定义了  `Pydantic`  模型，用于数据验证和序列化。对于熟悉 FastAPI 的开发者来说，这部分内容想必再熟悉不过了。

- •
  `UserRead`
  继承自
  `schemas.BaseUser[uuid.UUID]`
  ，用于表示读取（返回）用户信息时的结构。
- •
  `UserCreate`
  继承自
  `schemas.BaseUserCreate`
  ，用于表示创建用户（注册）时的请求体结构。
- •
  `UserUpdate`
  继承自
  `schemas.BaseUserUpdate`
  ，用于表示更新用户资料时的请求体结构。

同样地，这里每个  `Schema`  内部也直接  `pass`  了。这是因为它们通过继承  `fastapi-users`  提供的基类，已经自动包含了默认的用户字段。如果你在  `app/db.py`  中的  `User`  模型添加了自定义字段，需要在这里对应的  `Schema`  中将  `pass`  替换为你的自定义字段定义。

#### `app/users.py`

```
import uuid  
from typing import Optional  
  
from fastapi import Depends, Request  
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models  
from fastapi_users.authentication import (  
    AuthenticationBackend,  
    BearerTransport,  
    JWTStrategy,  
)  
from fastapi_users.db import SQLAlchemyUserDatabase  
  
from app.db import User, get_user_db  
  
SECRET = "SECRET"  # 强烈建议在实际生产环境中使用复杂的、从环境变量加载的密钥！  

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):  
    reset_password_token_secret = SECRET  
    verification_token_secret = SECRET  
  
    async def on_after_register(self, user: User, request: Optional[Request] = None):  
        print(f"User {user.id} has registered.")  
  
    async def on_after_forgot_password(  
        self, user: User, token: str, request: Optional[Request] = None  
    ):  
        print(f"User {user.id} has forgot their password. Reset token: {token}")  
  
    async def on_after_request_verify(  
        self, user: User, token: str, request: Optional[Request] = None  
    ):  
        print(f"Verification requested for user {user.id}. Verification token: {token}")  

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):  
    yield UserManager(user_db)  

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")  

def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:  
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)  

auth_backend = AuthenticationBackend(  
    name="jwt",  
    transport=bearer_transport,  
    get_strategy=get_jwt_strategy,  
)  
  
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])  
  
current_active_user = fastapi_users.current_user(active=True)
```

前三个文件中的内容，无论是数据库连接、  `ORM`  模型还是  `Pydantic`  `Schemas`  ，都是我们在普通 FastAPI 项目中经常会用到的概念。真正体现  `fastapi-users`  精华和定制能力的核心，就在于  `app/users.py`  文件，尤其是其中的  `UserManager`  。

在这个文件中，我们从  `fastapi-users`  库中引入了大量核心组件：

- •
  **`SECRET`**
  : 一个用于生成和验证令牌的密钥。
  **请注意，在实际生产环境中，务必使用一个复杂的随机字符串，并从环境变量等安全方式加载，切勿硬编码！**
- •
  **`UserManager`
  类**
  : 这是
  `fastapi-users`
  的核心管理类。它继承自
  `UUIDIDMixin`
  和
  `BaseUserManager[User, uuid.UUID]`
  。

* •
  `UUIDIDMixin`
  为用户ID提供了
  `UUID`
  类型支持。
* •
  `BaseUserManager`
  提供了用户注册、验证、密码重置等大部分通用逻辑。
* •
  `reset_password_token_secret`
  和
  `verification_token_secret`
  用于生成重置密码和验证邮箱的令牌。
* •
  `on_after_register`
  ,
  `on_after_forgot_password`
  ,
  `on_after_request_verify`
  等方法是
  **事件钩子（
  `event hooks`
  ）**
  。目前它们只包含了
  `print`
  语句。这些方法正是你可以填充自定义业务逻辑的地方！例如：

+ •
  `on_after_register`
  : 用户注册成功后，可以发送欢迎邮件。
+ •
  `on_after_forgot_password`
  : 用户忘记密码后，可以发送包含重置链接的邮件。
+ •
  `on_after_request_verify`
  : 用户请求验证账户后，可以发送包含验证链接的邮件。
    
  这些函数让你能够轻松地在用户生命周期的关键节点插入定制化的逻辑。

- •
  **`get_user_manager`
  函数**
  : 这是一个 FastAPI 依赖，职责是实例化并提供
  `UserManager`
  对象。它依赖于我们之前在
  `db.py`
  中定义的
  `get_user_db`
  来获取数据库适配器。
- •
  **`bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")`**
  : 这是认证后端（
  `Authentication Backend`
  ）的
  `传输方式`
  。
  `BearerTransport`
  意味着令牌将通过 HTTP
  `Authorization`
  头（
  `header`
  ）中的
  `Bearer`
  方案传递。
  `tokenUrl`
  参数指定了获取令牌的登录路由。
- •
  **`get_jwt_strategy`
  函数**
  : 这是认证后端的
  `策略`
  。
  `JWTStrategy`
  指定了使用
  `JWT`
  作为令牌生成和管理的方式。
  `secret`
  参数用于
  `JWT`
  的签名和验证，
  `lifetime_seconds`
  定义了
  `JWT`
  的有效期（这里是 3600 秒，即 1 小时）。
- •
  **`auth_backend`
  实例**
  : 整合了
  `传输方式`
  (
  `BearerTransport`
  ) 和
  `策略`
  (
  `JWTStrategy`
  )，创建了一个完整的
  `认证后端`
  。我们为其命名为
  `"jwt"`
  。
- •
  **`fastapi_users`
  实例**
  : 这是
  `FastAPI-Users`
  库的“总司令”。它将
  `get_user_manager`
  依赖和一系列
  `认证后端`
  (这里只有
  `auth_backend`
  ) 整合起来。通过这个实例，我们可以在
  `main.py`
  中生成各种用户相关的路由，并获取
  `current_user`
  依赖。
- •
  **`current_active_user`
  依赖**
  : 这是一个非常实用的 FastAPI 依赖，它会检查请求中的令牌，验证用户身份，并确保用户是活跃状态（
  `is_active=True`
  ）。如果验证成功，它会将当前
  `User`
  对象注入到路由函数中。

现在，你可能对  `UserManager`  和认证后端的复杂性感到有些压力。暂且不必深究每个细节，最好的方式是先将代码跑起来，实际操作一下用户注册和登录，感受一下流程。我们将在后续的文章中，通过更详细的官方文档解读和更多实战代码，带领大家逐一深入探讨各个模块的功能和定制方法。

**最后，确保在  `app`  文件夹下创建一个空的  `__init__.py`  文件，以便 Python 将其识别为一个包。**

```
fastapi-users-tutorial/  
├── app/  
│   ├── __init__.py  # 新建一个空文件  

│   ├── main.py  
│   ├── db.py  
│   ├── schemas.py  
│   └── users.py  
└── # 其他uv生成的文件

```

### 3. 运行项目与查看 Swagger UI

一切就绪后，打开终端，在项目根目录下使用  `uv`  命令运行 FastAPI 应用：

```
uv run app.main --reload
```

或者使用你的 Fastapi 开发命令：

```
uv run fastapi dev
```

成功启动后，打开浏览器访问  `http://localhost:8000/docs`  ，你将看到由  `FastAPI`  (  `Swagger UI`  ) 自动生成的接口文档：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs3kU9fZV4MUT1DSic0LqMFcZ96OoicxHNcoq8ByetqqicuTQt1o9pYgycqWjZhdBzsFtocoT0m38nT8g/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

从  `Swagger UI`  中，你可以清晰地看到接口被分成了两个主要的组：  `auth`  和  `users`  。

- •
  `auth`
  分组包含了 7 条与用户认证相关的路由，例如注册、登录、密码重置、邮箱验证等。
- •
  `users`
  分组则包含了用户管理相关的路由。其中，带有
  `me`
  字样的路由（如
  `/users/me`
  ）是供用户获取和修改自身信息的接口，而带有用户
  `ID`
  参数的路由（如
  `/users/{id}`
  ）通常是管理员才能使用的功能，允许其查询或修改其他用户的数据。

你可以尝试调用这些接口（例如先注册一个用户，然后登录获取令牌，再用令牌访问受保护路由），初步体验  `FastAPI-Users`  的功能。在接下来的系列文章中，我们将结合官方文档的详细解读和丰富的实战代码，一步步带领大家深入掌握这个强大的库！

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-users-turtorial

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)