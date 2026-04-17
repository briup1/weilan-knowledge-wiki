---
title: "FastAPI-Users 保姆级教程（四）：深入核心——揭秘 UserManager"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/tutorial", "type/concept", "FastAPI-Users", "UserManager", "认证"]
status: "archived"
references: "Archive/20250831_FastAPI-Users保姆级教程（五）：深入核心——揭秘UserManager.md"
---

# FastAPI-Users 保姆级教程（四）：深入核心——揭秘 UserManager

`UserManager` 是 FastAPI-Users 的真正核心与大脑，承载了几乎所有与用户相关的业务逻辑。

官方文档定义：

> `UserManager` 类是 FastAPI-Users 的核心逻辑所在。我们提供了 `BaseUserManager` 类，你应该继承它来设置一些参数和定义逻辑，例如，当一个用户刚刚注册或忘记密码时应该做什么。它的设计旨在轻松扩展和定制。

## UserManager 的泛型与 ID 解析 Mixin

```python
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

SECRET = "SECRET"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
```

- `BaseUserManager[User, uuid.UUID]`：泛型参数分别指定用户模型和主键 ID 类型。
- `UUIDIDMixin`：为 `UUID` 类型 ID 提供 `parse_id` 方法解析能力。

**官方提供的 ID 解析 Mixins**：

- `UUIDIDMixin`：用于 UUID 类型 ID。
- `IntegerIDMixin`：用于整数类型 ID。
- `ObjectIDIDMixin`（由 `fastapi-users-db-beanie` 提供）：用于 MongoDB 的 ObjectID。

**继承顺序很重要**：Mixin 应排在第一位（`UserManager(UUIDIDMixin, BaseUserManager)`），因为 Python 的 MRO 最左边的元素拥有优先权。

如果需要自定义 ID 类型，可直接重载 `parse_id` 方法：

```python
from fastapi_users import BaseUserManager, InvalidID

class UserManager(BaseUserManager[User, MyCustomID]):
    def parse_id(self, value: Any) -> MyCustomID:
        try:
            return MyCustomID(value)
        except ValueError as e:
            raise InvalidID() from e
```

## 自定义属性和方法：注入你的业务逻辑

`UserManager` 提供了一系列“事件钩子”方法，允许你在用户生命周期的关键节点执行自定义逻辑。

### 属性 (Attributes)

- `reset_password_token_secret`：重置密码令牌的编码密钥。
- `reset_password_token_lifetime_seconds`：重置密码令牌生命周期，默认 3600 秒。
- `reset_password_token_audience`：JWT 受众，默认 `"fastapi-users:reset"`。
- `verification_token_secret`：验证令牌的编码密钥。
- `verification_token_lifetime_seconds`：验证令牌生命周期，默认 3600 秒。
- `verification_token_audience`：JWT 受众，默认 `"fastapi-users:verify"`。

### 方法 (Methods)

#### `validate_password`

验证密码规则：

```python
async def validate_password(self, password: str, user: User) -> None:
    if len(password) < 8:
        raise InvalidPasswordException(reason="Password should be at least 8 characters")
    if user.email in password:
        raise InvalidPasswordException(reason="Password should not contain e-mail")
```

#### `on_after_register`

用户注册成功后执行（如发送欢迎邮件）：

```python
async def on_after_register(self, user: User, request: Optional[Request] = None):
    print(f"User {user.id} has registered.")
```

#### `on_after_update`

用户信息更新后执行：

```python
async def on_after_update(
    self,
    user: User,
    update_dict: Dict[str, Any],
    request: Optional[Request] = None,
):
    print(f"User {user.id} has been updated with {update_dict}.")
```

#### `on_after_login`

用户登录后执行（如记录登录日志）：

```python
async def on_after_login(
    self,
    user: User,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
):
    print(f"User {user.id} logged in.")
```

#### `on_after_request_verify`

用户请求验证后执行（通常用于发送验证邮件）：

```python
async def on_after_request_verify(
    self, user: User, token: str, request: Optional[Request] = None
):
    print(f"Verification requested for user {user.id}. Verification token: {token}")
```

#### `on_after_verify`

用户成功验证后执行：

```python
async def on_after_verify(self, user: User, request: Optional[Request] = None):
    print(f"User {user.id} has been verified")
```

#### `on_after_forgot_password`

用户请求忘记密码后执行（发送密码重置邮件）：

```python
async def on_after_forgot_password(
    self, user: User, token: str, request: Optional[Request] = None
):
    print(f"User {user.id} has forgot their password. Reset token: {token}")
```

#### `on_after_reset_password`

用户重置密码后执行：

```python
async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
    print(f"User {user.id} has reset their password.")
```

#### `on_before_delete`

用户被删除前执行（如清理关联资源）：

```python
async def on_before_delete(self, user: User, request: Optional[Request] = None):
    print(f"User {user.id} is going to be deleted")
```

#### `on_after_delete`

用户被删除后执行：

```python
async def on_after_delete(self, user: User, request: Optional[Request] = None):
    print(f"User {user.id} is successfully deleted")
```

## 提供 `get_user_manager` 依赖

```python
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
```

这个依赖将被用在最终的 `FastAPIUsers` 实例中：

```python
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
```

至此，FastAPI-Users 的核心配置已经基本完成！

> 完整代码请移步 GitHub 项目：https://github.com/acelee0621/fastapi-users-turtorial

---

## 来源与归档

- 原始素材：[Archive/20250831_FastAPI-Users保姆级教程（五）：深入核心——揭秘UserManager.md](../../../Archive/20250831_FastAPI-Users保姆级教程（五）：深入核心——揭秘UserManager.md)
