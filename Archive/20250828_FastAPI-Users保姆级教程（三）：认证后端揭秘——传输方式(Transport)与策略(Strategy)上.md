# FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy) 上

# **FastAPI-Users保姆级教程（三）：认证后端揭秘——传输方式(Transport)与策略(Strategy) 上**

大家好，欢迎回到 FastAPI-Users 保姆级教程系列！🚀

> 在上一篇文章  [《FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成》](https://mp.weixin.qq.com/s?__biz=Mzk2NDk1MzgwOQ==&mid=2247484319&idx=1&sn=d8aaa49d6dcbbfb39d560298bf6edff2&token=1920395761&lang=zh_CN&scene=21#wechat_redirect)  中，我们对 FastAPI-Users 官方文档的  **用户模型与数据库 (  `User model and databases`  )**  章节进行了深入解析。

本章，我们将继续探索下一个核心概念：  **认证后端 (  `Authentication backends`  )**  。让我们看看官方文档是如何阐述的：

> FastAPI-Users 允许你接入多种认证方法。
>
> **它是如何工作的？**
>
> 你可以拥有多种认证方法，例如，为基于浏览器的查询提供  `cookie`  认证，为纯  `API`  查询提供  `JWT`  令牌 (  `token`  ) 认证。
>
> 在检查认证时，每种方法会依次运行。第一个成功解析出用户的方法将胜出。如果没有任何方法能成功解析出用户，则会抛出  `HTTPException`  异常。
>
> 对于每个后端，你都可以为其添加一个带有相应  `/login`  和  `/logout`  路由的路由器。更多相关信息请参阅路由器 (  `routers`  ) 文档。

这段介绍的核心思想是  **`FastAPI-Users`**  支持  **多认证后端并行工作**  ，并且为我们揭示了一个关键的公式：

### 传输方式 (Transport) + 策略 (Strategy) = 认证后端 (Authentication Backend)

这个公式是  `FastAPI-Users`  认证系统设计的精髓。  **传输方式 (  `Transport`  )**  决定了认证令牌（  `token`  ）如何通过  `HTTP`  请求在客户端与服务端之间传递；而  **策略 (  `Strategy`  )**  则定义了令牌本身的生成、验证和管理逻辑。

官方为我们提供了  **2 种传输方式**  和  **3 种策略**  ，这意味着我们可以像搭积木一样，自由组合出理论上的 6 种认证后端，以满足不同场景下的需求。这种高度模块化的设计正是  `FastAPI-Users`  灵活性的体现。

通常，认证后端的配置与  `UserManager`  类的定义都位于同一个文件中，共同构成了  `fastapi-users`  的核心配置。在我们之前的快速上手示例中，这个文件就是  `app/users.py`  。

---

## 传输方式 (Transport)：令牌的信使

传输方式管理着令牌在请求中的携带方式。目前官方提供了两种方法：  **`Bearer`**  和  **`Cookie`**  。

### 1. Bearer 传输

令牌将通过  `Authorization: Bearer <token>`  请求头 (  `header`  ) 发送。

**优缺点 (  `Pros and cons`  )**

- • ✅
  **优点**
  ：易于在每个请求中阅读和设置。
- • ❌
  **缺点**
  ：需要在客户端手动存储（例如，在
  `localStorage`
  或
  `sessionStorage`
  中）。
- • ➡️
  **建议场景**
  ：如果你正在开发移动应用 (
  `mobile application`
  ) 或纯
  `REST API`
  ，请使用它。

### 2. Cookie 传输

令牌将通过  `HTTP cookie`  发送。

**优缺点 (  `Pros and cons`  )**

- • ✅
  **优点**
  ：由 Web 浏览器在每个请求中自动、安全地存储和发送。
- • ✅
  **优点**
  ：由 Web 浏览器在过期时自动移除。
- • ❌
  **缺点**
  ：为实现最高安全性，需要配合
  `CSRF`
  (跨站请求伪造) 保护。
- • ❌
  **缺点**
  ：在浏览器环境之外（如移动应用或服务器间调用）工作起来比较困难。
- • ➡️
  **建议场景**
  ：如果你正在开发一个 Web 前端应用，请使用它。

在这里，我个人认为，对于大多数 FastAPI 应用来说，选择  **`Bearer`**  方式更为合适。它不仅方便跨平台（Web、iOS、Android），也更符合 FastAPI 主要作为  `REST API`  后端的定位。在当前的 Web 开发实践中，如果需要与浏览器深度集成，通常会采用现代前端框架（如 Vue, React）来构建全栈应用，而  `Bearer`  令牌是这类架构的标配。

---

### 深入解析两种传输方式

#### CookieTransport

> `Cookies`  是在用户浏览器中存储有状态信息的一种简单方式。因此，它更适用于基于浏览器的导航（例如，前端应用发起  `API`  请求），而非纯粹的  `API`  交互。

**配置 (  `Configuration`  )**

```
from fastapi_users.authentication import CookieTransport  
  
cookie_transport = CookieTransport(cookie_max_age=3600) # 设置 cookie 有效期为 1 小时

```

`CookieTransport`  的实例化非常简单，它接受以下参数：

- •
  `cookie_name`
  (默认: "fastapiusersauth"):
  `Cookie`
  的名称。
- •
  `cookie_max_age`
  (默认:
  `None`
  ):
  `Cookie`
  的生命周期，单位为秒。默认为
  `None`
  ，表示它是一个会话 (
  `session`
  )
  `cookie`
  ，浏览器关闭后即失效。
- •
  `cookie_path`
  (默认: "/"):
  `Cookie`
  的有效路径。
- •
  `cookie_domain`
  (默认:
  `None`
  ):
  `Cookie`
  的有效域名。
- •
  `cookie_secure`
  (默认:
  `True`
  ): 是否仅通过
  `SSL`
  请求（即
  `HTTPS`
  ）发送
  `cookie`
  。
- •
  `cookie_httponly`
  (默认:
  `True`
  ): 是否阻止
  `JavaScript`
  通过
  `document.cookie`
  访问此
  `cookie`
  ，这是防止
  `XSS`
  攻击的关键安全措施。
- •
  `cookie_samesite`
  (默认: "lax"): 指定
  `cookie`
  的
  `samesite`
  策略，有效值为
  `"lax"`
  ,
  `"strict"`
  和
  `"none"`
  。

**登录/登出行为**

- •
  **登录 (
  `Login`
  )**
  : 成功登录后，此方法将返回一个带有有效的
  `set-cookie`
  头的响应，状态码为
  **`204 No Content`**
  （无内容）。
- •
  **登出 (
  `Logout`
  )**
  : 此方法将移除认证
  `cookie`
  ，同样返回
  **`204 No Content`**
  。
- •
  **认证 (
  `Authentication`
  )**
  : 此方法期望你在请求头中提供一个有效的
  `cookie`
  。

#### BearerTransport

> 使用这种传输方式时，令牌应位于  `HTTP`  请求的  `Authorization`  头中，并采用  `Bearer`  方案。它特别适用于纯  `API`  交互或移动应用。

**配置 (  `Configuration`  )**

```
from fastapi_users.authentication import BearerTransport  
  
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
```

`BearerTransport`  的配置非常简洁，它只接受一个参数：

- •
  `tokenUrl`
  (str): 你的登录端点的确切路径。这个设置能让交互式文档（如
  `Swagger UI`
  ）自动发现并提供一个可用的 "Authorize" 按钮。在大多数情况下，你应该使用相对路径而非绝对路径。

**登录/登出行为**

- •
  **登录 (
  `Login`
  )**
  : 成功登录后，此方法将返回
  **`200 OK`**
  ，并附带
  `JSON`
  响应体：

  ```
  {  
      "access_token": "eyJ...",  
      "token_type": "bearer"  
  }
  ```
- •  **登出 (  `Logout`  )**  : 返回  **`204 No Content`**  。
- •  **认证 (  `Authentication`  )**  : 此方法期望你提供一个带有有效令牌的  `Bearer`  认证头，如下例所示：

  ```
  curl http://localhost:8000/protected-route \  
    -H 'Authorization: Bearer eyJ...'
  ```

---

## 策略 (Strategy)：令牌的大脑

介绍完两种传输方式，我们再来看策略。策略决定了令牌如何生成、包含哪些信息以及如何被验证。

### 1. JWT 策略

> **`JSON Web Token (JWT)`**  是一种用于基于  `JSON`  创建访问令牌的互联网标准。它们无需存储在数据库中：数据是自包含于令牌内部并通过加密签名的。

`JWT`  是目前应用最广泛的令牌策略，FastAPI 官方教程中演示的基础认证就是基于它。  `JWT`  的优点是  **简单、无状态、易于横向扩展**  。相应的缺点也很明显：令牌一旦签发，在有效期内就无法从服务端强制使其失效，除非密钥泄露，否则它将一直有效，这可能带来一定的安全隐患。

**配置 (  `Configuration`  )**

```
from fastapi_users.authentication import JWTStrategy  
  
SECRET = "YOUR_SUPER_SECRET_KEY" # 生产环境请使用强密码并从环境变量加载  

  
def get_jwt_strategy() -> JWTStrategy:  
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)
```

`JWTStrategy`  的实例化同样很简单，它接受以下参数：

- •
  `secret`
  (str): 用于编码令牌的常量密钥。请使用一个强大的密码短语并确保其安全！
- •
  `lifetime_seconds`
  (int): 令牌的生命周期，单位为秒。可以设置为
  `None`
  ，但这样令牌将永久有效，可能引发严重的安全问题。
- •
  `token_audience`
  (List[str], 默认:
  `["fastapi-users:auth"]`
  ):
  `JWT`
  令牌的有效受众列表。
- •
  `algorithm`
  (str, 默认:
  `"HS256"`
  ):
  `JWT`
  的加密算法，详见
  `RFC 7519`
  。
- •
  `public_key`
  (str): 如果
  `JWT`
  加密算法需要密钥对（如
  `RS256`
  ），则在此处提供用于解密的公钥。
  `secret`
  参数将始终用于加密。

**为什么要将策略实例化放在函数里？**

> 为了允许策略能够与其他依赖项动态实例化，它们必须作为可调用对象（  `callable`  ）提供给认证后端。对于  `JWTStrategy`  ，因为它不依赖其他项，所以可以像上面的函数一样简单。

这意味着如果你的  `SECRET`  或其他配置需要从另一个依赖（比如配置管理对象）中获取，这种函数式的提供方式将变得非常有用。

**RS256 算法示例**   
 如果需要使用非对称加密算法如  `RS256`  ，可以这样配置：

```
from fastapi_users.authentication import JWTStrategy  
  
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----  

# 你的 RSA 公钥 (PEM 格式)  

-----END PUBLIC KEY-----"""  
  
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----  

# 你的 RSA 私钥 (PEM 格式)  

-----END RSA PRIVATE KEY-----"""  
  
def get_jwt_strategy() -> JWTStrategy:  
    return JWTStrategy(  
        secret=PRIVATE_KEY,   
        lifetime_seconds=3600,  
        algorithm="RS256",  
        public_key=PUBLIC_KEY,  
    )
```

**登出行为**

> 登出时，此策略不会执行任何操作。实际上，  `JWT`  无法在服务器端被撤销：它在过期之前始终有效。

---

## 实战演练： `Cookie` 传输 + `JWT` 策略

由于篇幅关系，今天我们就先介绍到这里。下一篇文章我们将继续解读策略中的数据库 (  `Database`  ) 和  `Redis`  方案。

鉴于我们的快速上手示例代码使用的是  `Bearer`  +  `JWT`  的组合，今天我们就来动手实践一下  `Cookie`  +  `JWT`  的组合，并使用  `SQLAlchemy`  配合  `SQLite`  数据库。我已将完整代码更新至我们的代码仓库。

简要来说，我主要修改了  `app/users.py`  文件中的配置：

```

# app/users.py 的核心改动  

  

# 使用 CookieTransport，并设置 cookie 过期时间为 1 小时  

cookie_transport = CookieTransport(cookie_max_age=3600)   
  
def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:  
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)  
  
auth_backend = AuthenticationBackend(  
    name="jwt_cookie", # 可以为后端起一个描述性的名字  

    transport=cookie_transport,  # 在认证后端中，使用我们定义的 CookieTransport  

    get_strategy=get_jwt_strategy,  
)
```

修改配置后，我们启动应用，并注册一个测试用户。然后，我们可以使用  `PowerShell`  (Windows) 或  `curl`  (Linux/Mac) 来模拟登录请求：

```

# 使用 PowerShell 的 Invoke-WebRequest  

Invoke-WebRequest -Method POST -Uri "http://localhost:8000/auth/jwt/login" -Headers @{"Content-Type"="application/x-www-form-urlencoded"} -Body "username=test@test.com&password=test"
```

注意，我们访问的登录地址是  `http://localhost:8000/auth/jwt_cookie/login`  ，用户名为  `test@test.com`  ，密码是  `test`  。

执行后，你会得到类似这样的输出：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2rFtl8ViaQWPibBacPTWib48Ag01JfE3YDMLDD1Zl3JWW6Xsuic3telhNg0t8Kt48nZz5yEBCeqbQEtQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

让我们来分析一下这个输出的关键信息：

1. 1.
   **成功的标志
   `StatusCode: 204`**
   :
     
   HTTP
   `204 (No Content)`
   是一个标准的成功响应状态码，表明服务器已成功处理请求，但无需返回任何内容。这完全符合我们前面提到的
   `CookieTransport`
   的登录行为。
2. 2.
   **成功的证据
   `Set-Cookie`
   头**
   :
     
   这部分是证明
   `CookieTransport`
   正常工作的最有力证据！在响应头中，你会找到一个
   `Set-Cookie`
   字段：

   ```
   Set-Cookie: fastapiusersauth=eyJ...[此处为JWT令牌]...; HttpOnly; Max-Age=3600; Path=/; SameSite=lax; Secure
   ```

   让我们逐一拆解这个  `cookie`  的属性：

- •
  `fastapiusersauth=...`
  : 这就是我们的
  `JWT`
  令牌，它被存放在了名为
  `fastapiusersauth`
  的
  `Cookie`
  中。
- •
  `HttpOnly`
  : 这是一个重要的安全设置，防止客户端
  `JavaScript`
  读取此
  `Cookie`
  ，有效抵御
  `XSS`
  攻击。
- •
  `Max-Age=3600`
  : 这正是我们在
  `CookieTransport`
  中设置的
  `cookie_max_age=3600`
  ，表示
  `Cookie`
  将在 1 小时后过期。
- •
  `Path=/`
  : 表示此
  `Cookie`
  对整个网站（根路径下所有页面）都有效。
- •
  `SameSite=lax`
  : 一种
  `CSRF`
  攻击的防御策略。
- •
  `Secure`
  : 表示此
  `Cookie`
  仅在
  `HTTPS`
  连接下发送。如果在本地
  `HTTP`
  环境开发，你可以在
  `CookieTransport`
  中暂时设置
  `cookie_secure=False`
  。

至此，我们成功地演示了如何将  `Cookie`  传输方式与  `JWT`  策略结合使用。

那么这期的文章就到这里，下一期我们将深入解读官方文档中关于  **数据库 (  `Database`  )**  和  **`Redis`**  的令牌存储策略，敬请期待！

> 本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-users-turtorial

> FastAPI User 教程系列合集：   
>  [FastAPI-Users 中文实战教程](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4137507202221441040#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)