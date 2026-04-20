# FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers

# **FastAPI-Users保姆级教程（六）：最后的拼图——Schemas与Routers**

大家好，欢迎回到 FastAPI-Users 保姆级教程系列！🚀

> 在上一篇文章  [《FastAPI-Users保姆级教程（五）：深入核心——揭秘 UserManager》](https://mp.weixin.qq.com/s?__biz=Mzk2NDk1MzgwOQ==&mid=2247484343&idx=1&sn=33189a742fe63ebc794acc5433140749&token=627626012&lang=zh_CN&scene=21#wechat_redirect)  中，我们已经配置好了  `FastAPI-Users`  最核心的大脑  `UserManager`  。

至此，我们的用户认证系统已经万事俱备，只欠东风。今天，我们就来完成最后的两块拼图：  **数据模型 (  `Schemas`  )**  和  **路由 (  `Routers`  )**  ，将我们所有的后端逻辑最终暴露为可供客户端调用的  `API`  接口。

---

## 数据模型 (Schemas)：API 的数据契约

`Schemas`  在  `FastAPI`  (以及  `FastAPI-Users`  ) 中扮演着至关重要的角色。它们基于  `Pydantic`  模型，定义了  `API`  请求和响应的数据结构、类型和验证规则。你可以将它们理解为你的  `API`  与外界沟通时必须遵守的“数据契约”。

官方文档是这样介绍  `Schemas`  的：

> **`Pydantic`  模型 (  `Schemas`  )**
>
> `FastAPI`  大量使用  `Pydantic`  模型来验证请求体和序列化响应。  `FastAPI-Users`  也不例外，它期望你提供代表用户在读取、创建和更新时状态的  `Pydantic`  模型。
>
> 这与你的数据库用户模型 (  `User model`  ) 不同，后者是实际与数据库交互的对象。而  `Schemas`  则用于在  `API`  层面验证数据并正确地将其序列化。

简单来说，  `Schemas`  负责定义接口的输入和输出，而数据库模型 (  `ORM model`  ) 负责与数据库交互。

`FastAPI-Users`  已经为我们内置了覆盖基本需求的基础  `Schema`  ，它包含以下字段：

- •
  `id`
  (
  `ID`
  )：用户的唯一标识符。
- •
  `email`
  (
  `str`
  )：用户的邮箱。
- •
  `is_active`
  (
  `bool`
  )：用户是否已激活。如果为
  `False`
  ，登录和忘记密码请求将被拒绝。
- •
  `is_verified`
  (
  `bool`
  )：用户是否已验证。与验证路由逻辑配合使用。
- •
  `is_superuser`
  (
  `bool`
  )：用户是否为超级用户。用于实现管理后台逻辑。

### 定义你自己的 Schemas

`FastAPI-Users`  提供了三个基础模型供我们继承：

- •
  `BaseUser`
  ：用于
  **读取**
  用户的基本模型。
- •
  `BaseUserCreate`
  ：专用于用户
  **注册**
  ，包含
  `email`
  和
  `password`
  字段。
- •
  `BaseUserUpdate`
  ：专用于用户资料
  **更新**
  。

我们应该根据这三个基类定义出自己应用所需的  `Schema`  ：

```
import uuid  
from fastapi_users import schemas  
  
class UserRead(schemas.BaseUser[uuid.UUID]):  
    # BaseUser 需要一个泛型来指定 ID 的类型  

    pass  
  
class UserCreate(schemas.BaseUserCreate):  
    pass  
  
class UserUpdate(schemas.BaseUserUpdate):  
    pass
```

在最简单的情况下，如果官方提供的默认字段已经满足你的需求，你只需像上面这样继承并使用  `pass`  即可。

> **类型提示：需要 ID 泛型类型**
>
> 你可以看到，在继承  `BaseUser`  类时我们定义了一个泛型类型。它应该与你在模型中使用的  `ID`  类型相对应。这里我们选择了  `UUID`  ，但它可以是任何类型，比如整数或 MongoDB 的  `ObjectID`  。

### 添加自定义字段

当然，你完全可以根据业务需求添加自定义字段。

```
import datetime  
import uuid  
from typing import Optional  
from fastapi_users import schemas  
  
class UserRead(schemas.BaseUser[uuid.UUID]):  
    # 读取用户时，返回 first_name 和 birthdate 字段  

    first_name: str  
    birthdate: Optional[datetime.date]  
  
class UserCreate(schemas.BaseUserCreate):  
    # 创建用户时，需要提供 first_name 和 birthdate 字段  

    first_name: str  
    birthdate: Optional[datetime.date]  
  
class UserUpdate(schemas.BaseUserUpdate):  
    # 更新用户时，可以修改 first_name 和 birthdate 字段  

    first_name: Optional[str]  
    birthdate: Optional[datetime.date]
```

对于熟悉  `FastAPI`  和  `Pydantic`  的开发者来说，这部分操作非常直观。

> **请确保在你的数据库模型中镜像这些字段**
>
> 你之前为特定数据库定义的  `User`  模型是实际存储数据的中心对象。因此，你需要确保在其中定义了相同的字段，以便数据能够被真正存储。

---

## 路由 (Routers)：连接世界的桥梁

我们距离成功仅一步之遥！最后一步是配置  `FastAPIUsers`  对象，它将把  `UserManager`  和认证后端连接起来，并让我们能够生成最终的  `API`  路由。

### 统一管理 `FastAPIUsers` 实例

首先，我们需要将之前配置的所有组件整合到一个  `FastAPIUsers`  实例中。

```
import uuid  
from fastapi_users import FastAPIUsers  
from app.db import User  
from app.users import auth_backend, get_user_manager  
  
fastapi_users = FastAPIUsers[User, uuid.UUID](  
    get_user_manager,  # 注入我们的 UserManager 依赖  

    [auth_backend],    # 传入一个包含所有认证后端的列表  

)
```

> **类型提示：需要用户模型 (  `User`  ) 和 ID 泛型**
>
> 与  `UserManager`  和  `Schema`  类似，  `FastAPIUsers`  实例也需要通过泛型指定你的用户模型及其  `ID`  类型，以获得良好的类型检查和自动补全。

### 可用的路由生成器

这个  `fastapi_users`  实例提供了一系列便捷的路由生成器，你可以按需选用：

- •
  **Auth router**
  : 提供
  `/login`
  和
  `/logout`
  路由。
- •
  **Register router**
  : 提供
  `/register`
  路由。
- •
  **Reset password router**
  : 提供
  `/forgot-password`
  和
  `/reset-password`
  路由。
- •
  **Verify router**
  : 提供
  `/request-verify-token`
  和
  `/verify`
  路由，用于邮箱验证。
- •
  **Users router**
  : 提供管理用户的路由，如读取、更新个人信息。

下面我们来看如何在主应用文件（  `main.py`  ）中注册这些路由。

#### 认证路由 (Auth router)

```

# main.py  

app.include_router(  
    fastapi_users.get_auth_router(auth_backend),  
    prefix="/auth/jwt",  
    tags=["auth"],  
)
```

你还可以要求用户必须先通过邮箱验证才能登录：

```

# 要求用户必须验证后才能登录  

fastapi_users.get_auth_router(auth_backend, requires_verification=True)
```

#### 注册路由 (Register router)

```
from app.schemas import UserRead, UserCreate  
  
app.include_router(  
    fastapi_users.get_register_router(UserRead, UserCreate),  
    prefix="/auth",  
    tags=["auth"],  
)
```

#### 验证路由 (Verify router)

```
app.include_router(  
    fastapi_users.get_verify_router(UserRead),  
    prefix="/auth",  
    tags=["auth"],  
)
```

#### 密码重置路由 (Reset password router)

```
app.include_router(  
    fastapi_users.get_reset_password_router(),  
    prefix="/auth",  
    tags=["auth"],  
)
```

#### 用户管理路由 (Users router)

```
from app.schemas import UserUpdate  
  
app.include_router(  
    fastapi_users.get_users_router(UserRead, UserUpdate),  
    prefix="/users",  
    tags=["users"],  
)
```

同样，你也可以要求用户必须验证后才能访问这些管理接口：

```

# 要求用户验证后才能访问 /users/me 等接口  

fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True)
```

---

## 结语

到这里，  `FastAPI-Users`  的主要配置部分就全部讲解完毕了。我们从数据库模型出发，一路配置了认证后端、  `UserManager`  、  `Schemas`  ，并最终通过  `Routers`  将功能暴露为  `API`  。

官方文档还提供了一些高级主题，例如：

- •
  **OAuth2**
  : 支持通过 Google、Facebook 等第三方账号登录。
- •
  **密码哈希 (Password hash)**
  :
  `FastAPI-Users`
  默认使用
  `Argon2`
  算法，你也可以自定义哈希算法。

不过，对于大多数应用而言，我们已经掌握的内容足以构建一个强大而安全的用户系统。

下一期，我们将正式进入  **实战阶段**  ！我们会一步步构建一个完整的用户管理应用。当这个应用完成后，你既可以将其作为微服务架构中的用户中心，也可以作为你未来任何  `FastAPI`  项目的用户认证模块模板。敬请期待！

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-users-turtorial

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)