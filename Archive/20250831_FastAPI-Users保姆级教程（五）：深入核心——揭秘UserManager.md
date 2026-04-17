# FastAPI-Users保姆级教程（五）：深入核心——揭秘 UserManager

# **FastAPI-Users保姆级教程（五）：深入核心——揭秘 UserManager**

大家好，欢迎回到 FastAPI-Users 保姆级教程系列！🚀

> 在之前的系列文章中，我们对 FastAPI-Users 官方文档的  **认证后端 (  `Authentication backends`  )**  章节做了比较全面的解析。

今天，我们将深入  `FastAPI-Users`  的真正核心与大脑——  **`UserManager`**  。

官方文档是这样介绍它的：

> `UserManager`  类是  `FastAPI-Users`  的核心逻辑所在。我们提供了  `BaseUserManager`  类，你应该继承它来设置一些参数和定义逻辑，例如，当一个用户刚刚注册或忘记密码时应该做什么。
>
> 它的设计旨在轻松扩展和定制，以便你可以集成自己的专属逻辑。

简单来说，  `UserManager`  是你处理所有与用户相关的业务逻辑的地方。

首先，我们需要创建自己的  `UserManager`  类。我建议将这个类的定义与传输方式、策略的配置放在同一个文件中，并给它一个清晰的文件名，比如  `user_manager.py`  。在我们的最小示例中，它仍然位于  `app/users.py`  。

> 你应该定义自己的  `UserManager`  类来设置各种参数。

下面是官方提供的一个标准  `UserManager`  范例：

```
import uuid  
from typing import Optional  
  
from fastapi import Depends, Request  
from fastapi_users import BaseUserManager, UUIDIDMixin  
  
from .db import User, get_user_db  
  
SECRET = "SECRET"  
  
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

async def get_user_manager(user_db=Depends(get_user_db)):  
    yield UserManager(user_db)
```

> 正如你所见，你必须在这里定义各种属性和方法。你可以在下面找到它们的完整列表。

---

### UserManager 的泛型与 `ID` 解析 `Mixin`

你可能注意到了  `UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID])`  这段定义有些特别。让我们来拆解一下。

> **类型提示：需要用户模型 (  `User`  ) 和 ID 类型的泛型**
>
> 你可以看到，在继承基类时我们定义了两个泛型类型：
>
> 1. 1.
>    `User`
>    ：这是我们在数据库部分定义的用户模型。
> 2. 2.
>    `ID`
>    ：这应该与你在模型中使用的
>    `ID`
>    类型相对应。这里我们选择了
>    `UUID`
>    ，但它可以是任何类型，比如整数或 MongoDB 的
>    `ObjectID`
>    。
>
> 这将帮助你在实现自定义方法时获得良好的类型检查和自动补全。

简单来说，  `BaseUserManager[User, uuid.UUID]`  是为了告诉  `UserManager`  你的用户长什么样 (  `User`  模型)，以及用户的主键是什么类型 (  `uuid.UUID`  )。

那么，  `UUIDIDMixin`  是做什么的呢？

> **ID 解析器  `Mixin`**
>
> 由于用户  `ID`  是完全泛型的，我们需要一种方法在它来自  `API`  请求时（通常作为  `URL`  路径参数）可靠地解析它。
>
> 这就是我们在上面例子中添加  `UUIDIDMixin`  的原因。它实现了  `parse_id`  方法，确保  `UUID`  是有效的并被正确解析。
>
> 当然，重要的是这个逻辑要与你的  `ID`  类型相匹配。为了帮助你，我们为最常见的情况提供了  `mixins`  ：
>
> - •
>   `UUIDIDMixin`
>   ：用于
>   `UUID`
>   类型的
>   `ID`
>   。
> - •
>   `IntegerIDMixin`
>   ：用于整数类型的
>   `ID`
>   。
> - •
>   `ObjectIDIDMixin`
>   (由
>   `fastapi-users-db-beanie`
>   提供)：用于
>   `MongoDB`
>   的
>   `ObjectID`
>   。

可以把  `Mixin`  理解为一个“插件”或者“增强包”，它给你的  `UserManager`  增加了“识别并解析特定类型 ID”的能力。

> **继承顺序很重要**
>
> 注意，在我们的例子中，  `mixin`  在  `UserManager`  继承中排在第一位。由于 Python 的方法解析顺序 (MRO)，最左边的元素拥有优先权。

如果你需要一个自定义的  `ID`  类型，你可以直接重载  `parse_id`  方法：

```
from fastapi_users import BaseUserManager, InvalidID  
  
class UserManager(BaseUserManager[User, MyCustomID]):  
    def parse_id(self, value: Any) -> MyCustomID:  
        try:  
            return MyCustomID(value)  
        except ValueError as e:  
            raise InvalidID() from e
```

> 如果  `ID`  无法被解析成期望的类型，你需要抛出  `InvalidID`  异常。

在绝大多数生产环境中，我们遵循官方推荐，直接使用  `UUIDIDMixin`  即可。

---

### 自定义属性和方法：注入你的业务逻辑

`UserManager`  的真正强大之处在于它提供了一系列“事件钩子”方法，允许你在用户生命周期的关键节点执行自定义逻辑。

在上面的示例代码中，我们看到了三个方法：  `on_after_register`  (注册后)、  `on_after_forgot_password`  (忘记密码后) 和  `on_after_request_verify`  (请求验证后)。

这就像预设好的触发器：

- •
  **用户注册后 (
  `on_after_register`
  )**
  ：你可以发送一封欢迎邮件，为新用户初始化一些基本数据，或者将其信息同步到营销系统。
- •
  **用户忘记密码后 (
  `on_after_forgot_password`
  )**
  ：你可以通过邮件或短信将包含重置令牌 (
  `token`
  ) 的链接发送给用户。我们在网上看到的那种非常长的重置密码链接就是这样生成的。
- •
  **用户请求验证后 (
  `on_after_request_verify`
  )**
  ：你可以向用户的注册邮箱发送一封包含验证链接的邮件。用户点击链接后，后端通过
  `token`
  验证其身份，并将数据库中的
  `is_verified`
  字段更新为
  `True`
  。

官方为我们准备了丰富的属性和方法，让我们逐一来看：

#### **属性 (Attributes)**

- •
  `reset_password_token_secret`
  : 用于编码重置密码令牌的密钥。
- •
  `reset_password_token_lifetime_seconds`
  : 重置密码令牌的生命周期（秒），默认为 3600。
- •
  `reset_password_token_audience`
  : 重置密码令牌的 JWT 受众，默认为
  `"fastapi-users:reset"`
  。
- •
  `verification_token_secret`
  : 用于编码验证令牌的密钥。
- •
  `verification_token_lifetime_seconds`
  : 验证令牌的生命周期（秒），默认为 3600。
- •
  `verification_token_audience`
  : 验证令牌的 JWT 受众，默认为
  `"fastapi-users:verify"`
  。

#### **方法 (Methods)**

##### `validate_password`

验证密码是否符合规则。

```
async def validate_password(self, password: str, user: User) -> None:  
    if len(password) < 8:  
        raise InvalidPasswordException(reason="Password should be at least 8 characters")  
    if user.email in password:  
        raise InvalidPasswordException(reason="Password should not contain e-mail")
```

##### `on_after_register`

在用户成功注册后执行。

```
async def on_after_register(self, user: User, request: Optional[Request] = None):  
    print(f"User {user.id} has registered.")
```

##### `on_after_update`

在用户信息成功更新后执行。

```
async def on_after_update(  
    self,  
    user: User,  
    update_dict: Dict[str, Any],  
    request: Optional[Request] = None,  
):  
    print(f"User {user.id} has been updated with {update_dict}.")
```

##### `on_after_login`

在用户成功登录后执行。例如可以用于发放每日登录奖励。

```
async def on_after_login(  
    self,  
    user: User,  
    request: Optional[Request] = None,  
    response: Optional[Response] = None,  
):  
    print(f"User {user.id} logged in.")
```

##### `on_after_request_verify`

在用户成功请求验证后执行。通常用于发送验证邮件。

```
async def on_after_request_verify(  
    self, user: User, token: str, request: Optional[Request] = None  
):  
    print(f"Verification requested for user {user.id}. Verification token: {token}")
```

##### `on_after_verify`

在用户成功验证后执行。

```
async def on_after_verify(self, user: User, request: Optional[Request] = None):  
    print(f"User {user.id} has been verified")
```

##### `on_after_forgot_password`

在用户成功请求忘记密码后执行。通常用于发送密码重置邮件。

```
async def on_after_forgot_password(  
    self, user: User, token: str, request: Optional[Request] = None  
):  
    print(f"User {user.id} has forgot their password. Reset token: {token}")
```

##### `on_after_reset_password`

在用户成功重置密码后执行。可以发送通知邮件提醒用户密码已被更改。

```
async def on_after_reset_password(self, user: User, request: Optional[Request] = None):  
    print(f"User {user.id} has reset their password.")
```

##### `on_before_delete`

在用户被删除前执行。可用于检查和处理与该用户相关的资源。

```
async def on_before_delete(self, user: User, request: Optional[Request] = None):  
    print(f"User {user.id} is going to be deleted")
```

##### `on_after_delete`

在用户被成功删除后执行。

```
async def on_after_delete(self, user: User, request: Optional[Request] = None):  
    print(f"User {user.id} is successfully deleted")
```

---

### 提供 `get_user_manager` 依赖

最后，我们需要创建一个 FastAPI 依赖项来在运行时获取  `UserManager`  的实例。

> `UserManager`  类将通过 FastAPI 依赖项在运行时注入。这样，你就可以在数据库会话中运行它，或在测试期间用模拟对象替换它。

```
async def get_user_manager(user_db=Depends(get_user_db)):  
    yield UserManager(user_db)
```

这里的  `get_user_db`  就是我们在数据库配置章节中定义好的依赖项。

这个  `get_user_manager`  将被用在最终的  `FastAPIUsers`  实例中，将所有组件串联起来：

```
fastapi_users = FastAPIUsers[User, uuid.UUID](  
    get_user_manager,  
    [auth_backend], # 这是一个包含所有认证后端的列表  

)
```

我们在这里将  `get_user_manager`  和之前定义的认证后端  `auth_backend`  一起传递给了  `FastAPIUsers`  。

至此，  `FastAPI-Users`  的核心配置已经基本完成！下一步只剩下定义  `schemas`  和  `router`  ，这两部分就非常简单了。我们下期再见！

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-users-turtorial

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)