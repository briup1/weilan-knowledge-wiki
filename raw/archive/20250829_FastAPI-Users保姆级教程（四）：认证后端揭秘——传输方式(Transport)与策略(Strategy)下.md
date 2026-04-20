# FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy) 下

# **FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy) 下**

大家好，欢迎回到 FastAPI-Users 保姆级教程系列！🚀

> 在上一篇文章  [《FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy) 上》](https://mp.weixin.qq.com/s?__biz=Mzk2NDk1MzgwOQ==&mid=2247484324&idx=1&sn=4d49652bdb42774717aae66c83f55a12&token=1920395761&lang=zh_CN&scene=21#wechat_redirect)  中，我们对 FastAPI-Users 官方文档的  **认证后端 (  `Authentication backends`  )**  章节中的传输方式，以及策略中的  `JWT`  部分进行了深入解析。

本章，我们将继续探索  **策略 (  `Strategy`  )**  的另外两种实现方式：  **数据库 (  `Database`  )**  和  **`Redis`**  。最后，我们会学习如何将传输方式和策略完美组合，正式创建一个认证后端。

---

## 数据库策略 (Database Strategy)：最“自然”的选择

官方文档首先介绍，将令牌存储在数据库中是“最自然”的方式：

> **数据库 (Database)**
>
> 存储令牌最自然的方式，当然是使用与你应用程序相同的数据库。在这种策略中，我们建立一个表（或集合）来存储这些令牌及关联的用户 ID。在每个请求中，我们尝试从数据库中检索此令牌，以获取相应的用户 ID。

这段话的核心意思是，直接复用现有的应用数据库来管理令牌。

- •
  **优点**
  ：

* •
  **无需额外服务**
  ：不需要引入和维护
  `Redis`
  等外部依赖。
* •
  **完全掌控**
  ：你可以更灵活地控制令牌。例如，当用户登出时，可以直接从数据库中删除令牌，使其立即失效，哪怕它还未到过期时间。

- •
  **缺点**
  ：

* •
  **配置稍繁琐**
  ：相比
  `JWT`
  ，需要额外定义一个
  `AccessToken`
  模型和数据库适配器。
* •
  **数据库压力**
  ：在高并发场景下，频繁的登录、登出和验证操作可能会对数据库造成一定压力。

尽管官方文档提到配置稍显繁琐，但我个人认为，如果你已经熟悉了用户模型的配置，这部分的配置几乎是完全相同的，非常直观。

### 数据库适配器 (Database Adapters)

> **数据库适配器 (Database adapters)**
>
> 一个访问令牌 (  `access token`  ) 在你的数据库中将具有如下结构：
>
> - •
>   `token`
>   (str) – 令牌的唯一标识符。由策略在登录时自动生成。
> - •
>   `user_id`
>   (ID) – 与此令牌关联的用户的 ID。
> - •
>   `created_at`
>   (datetime) – 令牌的创建日期和时间。用于判断令牌是否已过期。
>
> 我们为支持的每种数据库都提供了一个包含这些字段的基础模型。

接下来，我们分别看看  `SQLAlchemy`  和  `Beanie`  的配置方式。

#### SQLAlchemy 配置

```
from sqlalchemy.ext.asyncio import AsyncSession  
from fastapi import Depends  
from app.db import Base, get_async_session  
  

# 注意这个引入来源，它来自 fastapi_users_db_sqlalchemy  

from fastapi_users_db_sqlalchemy.access_token import (  
    SQLAlchemyAccessTokenDatabase,  
    SQLAlchemyBaseAccessTokenTableUUID,  
)  
  
class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass  
  
async def get_access_token_db(  
    session: AsyncSession = Depends(get_async_session),  
):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
```

仔细观察这段代码，你会发现它与用户模型的配置结构几乎一模一样：定义一个继承自官方基础模型的  `AccessToken`  表，再创建一个用于数据库操作的依赖项  `get_access_token_db`  。默认情况下，  `user_id`  字段使用  `UUID`  类型，这与用户模型的主键类型保持了一致。

官方文档也特别提示了  `user_id`  外键的类型问题：

> **`user_id`  外键默认为  `UUID`**
>
> 默认情况下，我们使用  `UUID`  作为用户的主键  `ID`  ，因此我们遵循相同的约定来定义指向用户的外键。
>
> 如果你想使用其他类型，比如自增整数，你可以使用  `SQLAlchemyBaseAccessTokenTable`  作为基类，并自定义你的  `user_id`  列。
>
> ```
> class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):  
>     @declared_attr  
>     def user_id(cls) -> Mapped[int]:  
>         return mapped_column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
> ```
>
> 注意，  `SQLAlchemyBaseAccessTokenTable`  期望一个泛型类型来定义你实际使用的  `ID`  类型。

**核心建议**  ：为了避免不必要的麻烦，最好将  `AccessToken`  模型与  `User`  模型的主键类型保持一致。在生产环境中，强烈推荐使用  `UUID`  。

#### Beanie (MongoDB) 配置

对于  `MongoDB`  用户，配置同样简洁明了：

```
from beanie import Document  
from fastapi_users_db_beanie.access_token import (  
    BeanieAccessTokenDatabase,  
    BeanieBaseAccessToken,  
)  
  
class AccessToken(BeanieBaseAccessToken, Document):  
    pass  
  
async def get_access_token_db():  
    yield BeanieAccessTokenDatabase(AccessToken)
```

与用户模型一样，如果你需要自定义配置（例如集合名称），  **必须在模型内部创建一个  `Settings`  类**  ，并继承官方的  `Settings`  基类。

> **提示**
>
> 如果你想为你的  `AccessToken`  文档模型添加自定义设置（比如更改集合名称），不要忘记让你的内部  `Settings`  类继承自  `BeanieBaseAccessToken`  预定义的设置，像这样：  `class Settings(BeanieBaseAccessToken.Settings): ...`  ！
>
> **非常重要**  ：切记将你的  `AccessToken`  ODM 模型添加到初始化  `Beanie`  的  `document_models`  数组中，就像你对  `User`  模型所做的那样！

### 定义数据库策略

配置好模型和适配器后，定义策略就水到渠成了：

```
from fastapi import Depends  
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy  
  

# 注意上面的引入来源  

from .db import AccessToken, User, get_access_token_db  
  
def get_database_strategy(  
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),  
) -> DatabaseStrategy:  
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)
```

`DatabaseStrategy`  接受两个参数：

- •
  `database`
  (
  `AccessTokenDatabase`
  ): 我们上面定义的
  `AccessToken`
  数据库适配器实例。
- •
  `lifetime_seconds`
  (int): 令牌的生命周期，单位为秒。

当用户登出时，此策略会自动将存储在数据库中的对应令牌删除。

---

## Redis 策略 (Redis Strategy)：性能之选

> **Redis**
>
> Redis 是一个超高速的键值存储数据库。因此，它是令牌管理的理想选择。在此策略中，会生成一个令牌并将其与用户  `ID`  关联存储在数据库中。在每个请求中，我们尝试从  `Redis`  中检索此令牌以获取相应的用户 ID。

使用  `Redis`  作为令牌存储，核心优势在于其基于内存的高性能读写，可以有效减轻主数据库的压力。缺点是你需要额外部署和维护一个  `Redis`  服务。

在用户登出时，  `Redis`  策略的行为与数据库策略相同：从  `Redis`  中删除对应的令牌。

**安装依赖**   
 你需要安装带有  `redis`  可选依赖的  `fastapi-users`  ：

```
pip install "fastapi-users[redis]"
```

**配置**   
 `Redis`  策略的配置非常简单，你甚至不需要像常规用法那样，在应用的生命周期事件中处理  `Redis`  的连接。

```
import redis.asyncio  
from fastapi_users.authentication import RedisStrategy  
  

# 注意：decode_responses=True 是必须的  

redis_client = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)  
  
def get_redis_strategy() -> RedisStrategy:  
    return RedisStrategy(redis_client, lifetime_seconds=3600)
```

`RedisStrategy`  接受以下参数：

- •
  `redis`
  (
  `redis.asyncio.Redis`
  ): 一个
  `redis.asyncio.Redis`
  的实例。
  **请务必将
  `decode_responses`
  标志设置为
  `True`**
  。
- •
  `lifetime_seconds`
  (
  `Optional[int]`
  ): 令牌的生命周期，单位为秒。默认为
  `None`
  ，意味着令牌永不过期。
- •
  `key_prefix`
  (str): 在
  `Redis`
  中存储键时使用的前缀。默认为
  `fastapi_users_token:`
  。

---

## 创建认证后端 (AuthenticationBackend)

现在，我们已经掌握了各种传输方式和策略，是时候将它们组合起来，创建最终的认证后端了。

> **创建一个后端**
>
> 正如我们所说，一个后端是  **传输方式**  和  **策略**  的组合。通过这种方式，你可以创建一个完全满足你需求的完整策略。
>
> 为此，你需要使用  `AuthenticationBackend`  类。

下面是一个以  `Bearer`  传输方式和  `JWT`  策略为例的组合：

```
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy  
  
SECRET = "SECRET"  
  
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")  
  
def get_jwt_strategy() -> JWTStrategy:  
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)  
  
auth_backend = AuthenticationBackend(  
    name="jwt",  
    transport=bearer_transport,  
    get_strategy=get_jwt_strategy,  
)
```

`AuthenticationBackend`  的实例化非常直观，它接受以下参数：

- •
  `name`
  (str): 后端的名称。
  **每个后端的名称必须是唯一的**
  。
- •
  `transport`
  (
  `Transport`
  ): 一个传输类 (
  `Transport`
  ) 的实例。
- •
  `get_strategy`
  (
  `Callable[..., Strategy]`
  ): 一个返回策略类 (
  `Strategy`
  ) 实例的依赖可调用对象。

如果你想使用其他的组合，比如  `Cookie`  +  `Database`  ，只需替换  `transport`  和  `get_strategy`  参数即可。名称可以随意命名，但保持唯一性很重要，因为  `FastAPI-Users`  支持同时激活多个认证后端，每个后端都需要关联到不同的认证路由。

> **下一步**
>
> 你可以拥有任意数量的认证后端。然后，你需要将这些后端传递给你的  `FastAPIUsers`  实例，并为它们中的每一个生成一个认证路由。

今天的示例代码，我将以  **`Bearer`  传输方式**  加上  **`Redis`  策略**  来展示其用法。在配置好最小示例并运行后，我们注册一个用户，然后登录。此时打开  `Tiny RDM`  或其他  `Redis`  客户端，可以看到，我们的令牌已经被成功缓存到  `Redis`  服务器中了。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2soIDOvia3YlD2RApPX6Q7icYWcLy6kmFzmKfibTvdLQG2KmxH1QFQY3ibA8777eZOXx3FVeAx80dTmw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

到这里，关于认证后端的解析就全部结束了！下一个章节，我们将深入  `FastAPI-Users`  的真正核心——  `UserManager`  ，敬请期待！

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-users-turtorial

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)