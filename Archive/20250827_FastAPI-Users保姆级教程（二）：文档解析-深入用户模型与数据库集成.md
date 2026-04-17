# FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成

# **FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成**

大家好，欢迎回到 FastAPI Users 保姆级教程合集！🚀

> 在上一期文章  [《FastAPI-Users保姆级教程（一）：核心概念与快速入门》](https://mp.weixin.qq.com/s?__biz=Mzk2NDk1MzgwOQ==&mid=2247484313&idx=1&sn=1007e9674c5327033520fb6a30f25ea2&token=1920395761&lang=zh_CN&scene=21#wechat_redirect)  中，我们对 FastAPI Users 的核心功能模块做了简单的介绍，并使用官方文档的示例代码搭建起了一个 Demo，对这个库的作用有了初步的了解。

从本节开始，我将带领大家逐个章节地深入剖析 FastAPI Users 的官方文档。这样，你可以更透彻地理解各个模块的配置和功能，在未来的实战中更加得心应手。

今天，我们的主题是官方文档中的  **User model and databases**  章节。这一部分主要分为两大块：  **SQLAlchemy**  和  **Beanie**  ，它们分别代表了 FastAPI Users 对关系型数据库和对 MongoDB 这类 NoSQL 数据库的强大支持。

准备好了吗？让我们开始吧！

## 第一站：SQLAlchemy 与关系型数据库

官方文档开篇明义：

> FastAPI Users provides the necessary tools to work with SQL databases thanks to SQLAlchemy ORM with asyncio.

简单来说，FastAPI Users 借助 SQLAlchemy 的异步 ORM 功能，为我们提供了操作 SQL 数据库所需的一切工具。

### 1. 安装异步驱动

要让 SQLAlchemy 连接到你的数据库，首先需要安装对应的异步驱动。

文档中虽然只提到了 PostgreSQL 和 SQLite，但实际上，只要是 SQLAlchemy 支持异步的数据库，FastAPI Users 同样也支持，比如  **MySQL**  。可能是因为前两者更为流行，所以文档优先列出。

我在这里为大家补充一下各个数据库的安装命令和连接字符串（DB_URL）示例：

- •
  **PostgreSQL**
  :

* • 安装驱动:
  `pip install asyncpg`
  或 `uv add asyncpg``
* • 连接示例:
  `postgresql+asyncpg://user:password@host:port/name`

- •
  **SQLite**
  :

* • 安装驱动:
  `pip install aiosqlite`
  或
  `uv add aiosqlite`
* • 连接示例:
  `sqlite+aiosqlite:///name.sqlite3`

- •
  **MySQL**
  :

* • 安装驱动:
  `pip install asyncmy`
  或
  `uv add aiosqlite`
* • 连接示例:
  `mysql+asyncmy://user:password@host:port/db?charset=utf8mb4`

**一个小建议**  ：注意到我将 SQLite 的数据库文件扩展名从  `.db`  改为了  `.sqlite3`  吗？虽然功能上完全一样，但  `.sqlite3`  是 SQLite 官方推荐的扩展名，它能更清晰地表明这是一个 SQLite3 数据库文件，便于开发者和工具识别。

### 2. 重要提醒： `expire_on_commit`

官方文档在这里给出了一个与 SQLAlchemy 异步编程相关的关键警告：

> ⚠️  **在使用 SQLAlchemy 的异步会话 (  `AsyncSession`  ) 时，必须将  `expire_on_commit`  设置为  `False`  。**

这是 SQLAlchemy 官方在异步环境下的硬性要求，目的是为了避免在事务提交后，对象因为自动过期刷新（auto-expire）而引发潜在的 I/O 操作，从而导致死锁、连接错误等问题。

### 3. 创建用户模型 (User Model)

接下来，我们定义用户数据在数据库中如何存储。

```

# db.py  

# ...其他引入  

from fastapi_users.db import SQLAlchemyBaseUserTableUUID  
  
class User(SQLAlchemyBaseUserTableUUID, Base):  
    """  
    用户数据库模型，增加了一个自定义的 full_name 字段  
    """  
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
```

这段代码和我们上一期快速上手中的几乎一模一样。唯一的区别是，我在这里额外增加了一个  `full_name`  字段。这意味着，我们可以在用户注册或更新信息时，保存用户的全名，方便在前端页面进行展示。你可以根据自己的业务需求，在这里添加任意自定义字段。

**一个核心知识点**  ：注意我们的  `User`  类继承了  `SQLAlchemyBaseUserTableUUID`  。

> By default, we use UUID as a primary key ID for your user.

这个基类决定了用户表的主键  `id`  将使用  **UUID**  类型。这是一个非常好的实践，特别是在生产环境中，可以避免通过自增 ID 暴露数据库的内部细节（例如用户总量）。

当然，如果你仍然偏爱传统的自增整数 ID，官方也为你提供了选择：

> If you want to use another type, like an auto-incremented integer, you can use  `SQLAlchemyBaseUserTable`  as base class and define your own  `id`  column.

你可以这样做：

```
from sqlalchemy import Integer  
from fastapi_users.db import SQLAlchemyBaseUserTable  
  
class User(SQLAlchemyBaseUserTable[int], Base):  
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
```

只需将基类换成  `SQLAlchemyBaseUserTable[int]`  ，并手动定义  `id`  字段即可。

### 4. 创建数据库适配器 (Database Adapter)

为了让 FastAPI Users 知道如何与我们的数据库和  `User`  模型进行交互，我们需要创建一个数据库适配器。这通过一个特殊的依赖项函数来实现。

```

# db.py  

from typing import AsyncGenerator  
from sqlalchemy.ext.asyncio import AsyncSession  
from fastapi import Depends  
from fastapi_users.db import SQLAlchemyUserDatabase  
  
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:  
    async with async_session_maker() as session:  
        yield session  
  
async def get_user_db(session: AsyncSession = Depends(get_async_session)):  
    yield SQLAlchemyUserDatabase(session, User)
```

这里的依赖链条非常清晰：

1. 1. 当一个路由需要用户信息时，它会依赖
   `get_user_db`
   。
2. 2. FastAPI 调用
   `get_user_db`
   ，发现它又依赖
   `get_async_session`
   。
3. 3. FastAPI 首先执行
   `get_async_session`
   ，获取一个数据库会话
   `session`
   。
4. 4. 然后将
   `session`
   和我们的
   `User`
   模型传入
   `SQLAlchemyUserDatabase`
   ，创建一个“用户数据库适配器”实例并
   `yield`
   出来。

这个适配器就是 FastAPI Users 用来执行所有用户相关数据库操作（如创建、查询、更新用户）的中间层。

最后，关于数据库表的创建，就是我们熟悉的  `create_db_and_tables()`  函数，在应用启动时执行即可。官方强烈建议在生产环境中使用 Alembic 等数据库迁移工具来管理表结构变更。

---

## 第二站：Beanie 与 MongoDB

讲完了关系型数据库，我们再来看看如何与文档数据库 MongoDB 协作。FastAPI Users 通过  **Beanie**  这个库实现了对 MongoDB 的无缝支持。

由于 SQLAlchemy 的完整示例代码和第一期的快速上手篇基本一致，大家可以直接参考仓库中的代码。因此，今天仓库里我会提供  **MongoDB**  版本的完整示例代码。

### 1. 安装与连接

首先，你需要安装带有 Beanie 支持的 FastAPI Users：

```
uv add "fastapi-users[beanie]"
```

这会自动安装 Beanie 及其依赖  `motor`  (MongoDB 的异步驱动)。

接下来是连接数据库和定义模型：

```

# db.py  

import motor.motor_asyncio  
from beanie import Document  
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase  
  
DATABASE_URL = "mongodb://localhost:27017"  
client = motor.motor_asyncio.AsyncIOMotorClient(  
    DATABASE_URL, uuidRepresentation="standard"  
)  
db = client["my_app_db"]  # 你可以任意指定自己的数据库名称  

  
class User(BeanieBaseUser, Document):  
    # 这里可以添加你自己的字段，例如：  

    # full_name: Optional[str] = None  

      
    class Settings:  
        # 自定义集合（表）的名称  

        name = "accounts"
```

这里的  `User`  模型同时继承了 FastAPI Users 提供的  `BeanieBaseUser`  和 Beanie 提供的  `Document`  基类。

#### **官方文档的两个重要提示** ：

1. 1.
   **自定义配置**
   ：如果你想修改默认配置（比如集合的名称），
   **必须在模型内部创建一个
   `Settings`
   类**
   。如代码所示，我将默认的集合名 "user" 修改为了 "accounts"。
2. 2.
   **自动索引**
   ：
   `BeanieBaseUser`
   会自动在
   `id`
   和
   `email`
   字段上创建唯一索引。这意味着你无需手动配置，就能保证邮箱的唯一性，并获得高效的查询性能。

### 2. 创建数据库适配器

与 SQLAlchemy 相比，Beanie 的数据库适配器创建过程要简洁得多，它没有复杂的依赖链。

```

# db.py  

# (接上文)  

  
async def get_user_db():  
    yield BeanieUserDatabase(User)
```

就是这么简单！  `BeanieUserDatabase`  接收  `User`  模型作为参数，就完成了适配器的配置。FastAPI Users 在内部已经处理好了不同数据库类型的差异。

### 3. 初始化 Beanie

最后一步，也是必不可少的一步，是在 FastAPI 应用的生命周期事件中初始化 Beanie。这与关系型数据库中“建表”的角色类似。

```

# main.py  

from contextlib import asynccontextmanager  
from fastapi import FastAPI  
from beanie import init_beanie  
from .db import db, User # 导入 db 连接实例和 User 模型  

  
@asynccontextmanager  
async def lifespan(app: FastAPI):  
    await init_beanie(  
        database=db,          # db 就是 client["my_app_db"]  

        document_models=[  
            User,             # 注册你的用户模型  

        ],  
    )  
    yield  
  
app = FastAPI(lifespan=lifespan)
```

在  `lifespan`  启动事件中，我们调用  `init_beanie`  ，将数据库连接实例和所有需要管理的 Beanie 模型列表传给它，Beanie 就会处理好后续的一切。

### 实战演练与总结

要将项目切换到 MongoDB，你只需要：

1. 1. 将
   `db.py`
   替换为使用 Beanie 的版本。
2. 2. 在
   `schemas.py`
   和
   `usermanager.py`
   中，将用户 ID 的类型提示从
   `UUID`
   修改为 MongoDB 的
   `ObjectId`
   （通常从
   `beanie`
   或
   `bson`
   中导入）。

我已将完整的 MongoDB 示例代码上传到仓库，有兴趣的朋友可以自行尝试。当然，这需要你本地安装了 MongoDB，或者使用云服务。我个人非常推荐  **MongoDB Atlas**  ，它的免费套餐提供 500MB 空间，非常适合学习和小型项目。

> **MongoDB Atlas 官网**  : https://cloud.mongodb.com/

当我使用 Atlas 完成注册和数据插入后，在网页端就可以清晰地看到用户信息了：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1fADStNKPzZRT7yrJSWTUJ9KhG6V0fcNwa1nO10xhZ1DkDvh5CXY2Vj5U2rJ6VXicJsjiawtPrxTNw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

好了，关于 FastAPI Users 官方文档中数据库与模型适配的部分就讲解到这里了。你会发现，  **最大的区别就在于  `db.py`  这个文件的配置**  。一旦数据库层设置完毕，后续无论你使用哪种数据库，上层的业务逻辑代码几乎是完全相同的。

希望这篇教程能帮助你扫清在数据库集成上的障碍！下一期，我们将继续深入其他模块，敬请期待！

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-users-turtorial

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)