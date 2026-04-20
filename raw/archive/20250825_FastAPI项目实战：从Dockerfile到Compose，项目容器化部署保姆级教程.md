# FastAPI 项目实战：从 Dockerfile 到 Compose，项目容器化部署保姆级教程

# **FastAPI 项目实战：从 Dockerfile 到 Compose，项目容器化部署保姆级教程**

大家好，欢迎再次回到我们的 FastAPI 项目实战系列！🚀

由于是第一次写合集教程，仓库代码也没按照文章组织好，都混在一起了，现在也不好改了，等下一个系列再进行优化。那么到今天，这个新手系列其实已经基本差不多了，基础的内容都有讲到。这个系列就算暂时告一段落了，在这个收官篇章，我们将探讨一个现代Web开发中不可或缺的技能：  **容器化**  。掌握了它，再加上之前学到的基础知识，你就更有能力根据自己的需求来进行后续的项目，边写边学了。

> **系列回顾**  ：在上一篇文章《FastAPI 项目实战：抽取通用仓库基类，拥抱工作单元模式下的事务管理》中，我们对代码进行了重构，实现了更优雅、更安全的事务管理。同时，代码仓库中也新增了  `get_service`  工厂函数和“英雄收藏集”模块，大家可以自行探索。虽然代码的迭代没能和文章完全同步，有些遗憾，但非常感谢大家一路的陪伴和反馈！

有读者提议出一期  `fastapi-users`  的教程，这个建议非常好！  `fastapi-users`  是一个功能强大的用户认证库，我计划在后续开启一个全新的系列，带领大家从零开始，结合官方文档，彻底吃透它。

那么，作为新手系列的最后一讲，我们将聚焦于如何将项目  **Docker 化**  。

## **为什么要使用 Docker？**

在现代开发中，Docker 几乎是必备技能。简单来说，它解决了“在我的电脑上可以跑，怎么到你那就不行了？”这个经典难题。

对于新手而言，它的核心优点包括：

1. 1.
   **环境一致性**
   ：Docker 将你的应用及其所有依赖（Python解释器、库、甚至操作系统底层文件）打包到一个隔离的“容器”中。这个容器无论是在你的Windows电脑、同事的Mac，还是在云服务器上，运行表现都完全一致。
2. 2.
   **简化部署**
   ：告别在服务器上手动安装Python、PostgreSQL、Redis并逐个配置的繁琐流程。使用 Docker Compose，只需一条命令 (
   `docker compose up`
   ) 就能启动整个应用所需的所有服务。
3. 3.
   **隔离与安全**
   ：每个容器都运行在自己的沙箱环境中，不会与主机系统或其他容器互相干扰，使应用更稳定、更安全。
4. 4.
   **轻量与高效**
   ：相比传统的虚拟机，Docker容器更轻量，启动更快，资源占用更少。

话不多说，我们马上进入实战环节！

## **第一步：编写 Dockerfile，为应用打包**

要将项目容器化，我们首先需要创建一个“镜像”（Image），它相当于一个应用的静态模板，包含了运行所需的一切。而  `Dockerfile`  就是一份告诉 Docker 如何构建这个镜像的“配方说明书”。

同时，我们还需要一个  `.dockerignore`  文件，用来告诉 Docker 在打包时忽略哪些文件。

### **1. `.dockerignore` ：为镜像瘦身**

在项目根目录新建  `.dockerignore`  文件。它的作用类似于  `.gitignore`  ，可以防止将本地开发环境的临时文件、缓存、虚拟环境等无关内容打包进镜像，从而有效减小镜像体积。

```

# 忽略 Python 运行时产生的缓存文件  

__pycache__/  
*.pyc  
*.pyo  
  

# 忽略本地日志文件  

*.log  
  

# 忽略 Python 虚拟环境  

.venv/  
  

# 忽略测试目录（通常不在生产镜像中包含）  

tests/  
  

# 忽略 git 相关文件和项目文档  

.git  
.gitignore  
.coverage  
README.md  
LICENSE  
.python-version
```

#### **文件内容释义** ：

- •  `__pycache__/`  ,  `*.pyc`  ,  `*.pyo`  : Python 解释器生成的字节码缓存，镜像中会重新生成，无需包含。
- •  `.venv/`  : 这是我们本地的虚拟环境，体积庞大且包含与主机系统相关的路径，绝不能打包进镜像。镜像内部会创建自己的、干净的虚拟环境。
- •  `tests/`  : 测试代码通常只在开发和CI/CD流程中需要，生产镜像中可以不包含。
- •  `.git`  ,  `.gitignore`  等：这些是版本控制和项目元数据文件，与应用运行无关。

### **2. `Dockerfile` ：定义镜像构建流程**

在项目根目录新建  `Dockerfile`  文件。我们将采用  **两阶段构建（Multi-stage build）**  策略，这是一个非常重要的最佳实践。

**为什么要用两阶段构建？**   
 想象一下，我们建房子需要用到脚手架、水泥搅拌机等各种工具（构建依赖），但房子建好后，我们只需要房子本身，而不需要把这些工具留在里面（最终镜像）。两阶段构建就是这个原理：

- •
  **构建阶段 (Builder Stage)**
  ：在一个包含完整构建工具的环境中，安装所有依赖、编译代码。
- •
  **运行阶段 (Runner Stage)**
  ：另起一个干净、轻量的基础镜像，只从构建阶段拷贝最终产物（代码和已安装的依赖库）。

这样做的好处是  **最终镜像体积会小得多**  ，并且  **更安全**  ，因为它不包含任何不必要的编译工具和开发库。

```

# ===================================================  

# -------------- 构建阶段 (Builder Stage) --------------  

# ===================================================  

# 使用一个轻量的 Python 官方镜像作为基础  

FROM python:3.13.5-slim-bookworm AS builder  
  

# 将 uv (一个超快的 Python 打包工具) 从其官方镜像复制到我们的构建环境中  

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/  
  

# 设置工作目录，后续所有命令都在此目录下执行  

WORKDIR /app  
  

# 仅复制依赖定义文件。这是为了利用 Docker 的层缓存机制。  

# 只有当这些文件变化时，下面的依赖安装步骤才会重新运行，从而加快构建速度。  

COPY pyproject.toml uv.lock ./  
  

# 使用 uv 创建虚拟环境并安装所有依赖  

# --frozen: 确保精确按照 lock 文件安装  

# --no-cache: 构建时禁用缓存，减小这一层的体积  

RUN uv venv && uv sync --frozen --no-cache  
  

# 复制项目的全部代码到工作目录  

COPY . .  
  

# 清理构建过程中产生的无用文件，进一步减小体积  

RUN find /app -type d -name '__pycache__' -exec rm -rf {} + \  
    && find /app -type f -name '*.pyc' -delete  
  

# ===================================================  

# -------------- 运行阶段 (Runner Stage) --------------  

# ===================================================  

# 再次使用同一个轻量的 Python 镜像作为最终镜像的基础  

FROM python:3.13.5-slim-bookworm  
  

# 设置工作目录  

WORKDIR /app  
  

# --- 安全最佳实践：使用非 root 用户运行应用 ---  

# 创建一个专门用于运行应用的普通用户  

RUN useradd --create-home appuser  

# 将工作目录的所有权交给这个新用户  

RUN chown -R appuser:appuser /app  
  

# 从 builder 阶段，将已经包含代码和虚拟环境的整个 /app 目录完整地复制过来  

# --chown=appuser:appuser 确保复制过来的文件属于我们创建的 appuser  

COPY --from=builder --chown=appuser:appuser /app /app  
  

# 如果项目有上传文件等持久化需求，可以在这里创建并授权目录  

# 例如: RUN mkdir -p /app/uploads && chown -R appuser:appuser /app/uploads  

  

# 切换到我们创建的非特权用户来运行后续命令  

USER appuser  
  

# 将镜像内虚拟环境的 bin 目录添加到 PATH 环境变量中  

# 这样就可以直接运行 uvicorn 等命令，而无需写完整路径  

ENV PATH="/app/.venv/bin:$PATH"  
  

# 声明容器将对外暴露 8000 端口  

EXPOSE 8000  
  

# 容器启动时默认执行的命令  

# 虽然在 docker-compose 中通常会被覆盖，但这是一个好习惯，让镜像可以独立运行  

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **3. 构建镜像**

现在，打开终端，确保 Docker Desktop 正在运行。在项目根目录下，执行以下命令：

```
docker build -t fastapi-demo-project:latest .
```

**命令解释**  ：

- •
  `docker build`
  ：构建镜像的命令。
- •
  `-t fastapi-demo-project:latest`
  ：
  `-t`
  表示 "tag"，为镜像指定一个名称和标签。格式是
  `镜像名称:标签`
  。
  `latest`
  是一个常用的默认标签。
- •
  `.`
  ：表示 Dockerfile 的上下文路径，这里是当前目录。

构建过程会逐行执行 Dockerfile 中的指令，你需要耐心等待它下载基础镜像、安装依赖。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2gGhydUiaS87ddxnVPcF7wX01rfRfibsXPH9x2Iiaxu8o8fdIspDqZByLelkd8UHputvDEKyy7rmiaxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

构建成功后，我们可以验证一下。

**通过命令行查看**  ：

```
docker images fastapi-demo-project
```

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2gGhydUiaS87ddxnVPcF7wX3c6DkI6BibhrYro6wWmTicTNp0o7JCZysufQROxkGuRmXGo4mKRHibB8w/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

**通过 Docker Desktop 查看**  ：   
 打开 Docker Desktop 应用，在 "Images" 标签页下，你应该能找到刚刚创建的  `fastapi-demo-project`  镜像。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2gGhydUiaS87ddxnVPcF7wXFCMq5cJVwXLib9P8rqRyT2TXIGBgVCLAicfwscjqMZmdpjw12MkwTNQw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

## **第二步：单容器运行与外部服务连接**

现在我们有了镜像，但还不能直接运行。因为我们的项目依赖 PostgreSQL 和 Redis。如果这两个服务是运行在你的电脑（宿主机）上，而不是在容器里，我们需要告诉容器内的 FastAPI 应用如何找到它们。

容器有自己的网络空间，它的  `localhost`  指向的是容器内部，而不是你的电脑。为了解决这个问题，Docker 提供了一个特殊的 DNS 名称：  `host.docker.internal`  ，它会解析为你宿主机的IP地址。

修改你的  `.env.dev`  配置文件：

```

# /.env.dev  

  

# ... 其他配置 ...  

  

# 数据库配置 (从 localhost 修改为 host.docker.internal)  

DEMO_DB_HOST=host.docker.internal   
DEMO_DB_PORT=5432  
DEMO_DB_USER=postgres  
DEMO_DB_PASSWORD=postgres  
DEMO_DB_DB=tutorial  
  

# Redis 配置 (从 localhost 修改为 host.docker.internal)  

DEMO_REDIS_HOST=host.docker.internal:6379 
```

然后，使用以下命令来启动我们的容器：

```
docker run -d --name fastapi-demo-app -p 8000:8000 --env-file .env.dev fastapi-demo-project:latest
```

**命令解释**  ：

- •
  `docker run`
  ：创建并运行一个新容器。
- •
  `-d`
  ：(detached) 后台运行容器。
- •
  `--name fastapi-demo-app`
  ：为容器指定一个名字，方便管理。
- •
  `-p 8000:8000`
  ：(publish) 端口映射，格式为
  `宿主机端口:容器端口`
  。它将你电脑的8000端口的流量转发到容器的8000端口。
- •
  `--env-file .env.dev`
  ：将
  `.env.dev`
  文件中的所有变量作为环境变量加载到容器中。
- •
  `fastapi-demo-project:latest`
  ：指定使用哪个镜像来创建容器。

启动后，访问  `http://localhost:8000`  ，如果能看到我们之前为应用设置的健康的输出信息，说明我们的应用容器已经成功运行并连接到了宿主机上的数据库和Redis！

## **第三步：使用 Docker Compose 编排多服务应用**

单容器运行只是第一步。在真实场景中，我们希望将 PostgreSQL、Redis 和我们的 FastAPI 应用  **作为一个整体**  来管理和部署。这时，  `Docker Compose`  就该登场了！

Compose 是一个用于定义和运行多容器 Docker 应用程序的工具。我们只需一个  `compose.yaml`  文件，就能配置好整个应用服务栈。

### **1. 编写 `compose.yaml`**

在项目根目录新建  `compose.yaml`  文件：

```

# compose.yaml  

  

# 定义我们整个应用栈的名称  

name: 'fastapi-demo-project'  
  
services:  
  # 1. PostgreSQL 数据库服务  

  postgresql:  
    image: bitnami/postgresql:latest  # 使用 bitnami 维护的可靠镜像  

    environment:  
      - POSTGRESQL_USERNAME=postgres  
      - POSTGRESQL_PASSWORD=postgres  
      - POSTGRESQL_DATABASE=tutorial  
    volumes:  
      - postgresql_data:/bitnami/postgresql # 将数据持久化到具名卷中  

    healthcheck: # 健康检查，确保数据库真正可用后再启动依赖它的服务  

      test: ["CMD", "pg_isready", "-U", "postgres"]  
      interval: 10s  
      timeout: 10s  
      retries: 5  
  
  # 2. Redis 服务  

  redis:  
    image: bitnami/redis:latest  
    environment:  
      - ALLOW_EMPTY_PASSWORD=yes # 允许无密码访问（仅限开发环境）  

    volumes:  
      - redis_data:/bitnami/redis/data # 持久化 redis 数据  

    healthcheck:  
      test: ["CMD", "redis-cli", "ping"]  
      interval: 10s  
      timeout: 5s  
      retries: 5  
  
  # 3. FastAPI 后端应用服务  

  app:  
    build: # 不再拉取镜像，而是直接在这里构建  

      context: . # 指定上下文为当前目录  

      dockerfile: Dockerfile # 指定 Dockerfile 文件名  

    image: fastapi-demo-project:latest # 为构建出的镜像命名  

    ports:  
      - "8000:8000" # 依然需要端口映射以从外部访问  

    env_file:  
      - .env.dev # 挂载 env 文件  

    depends_on: # 声明服务依赖关系  

      postgresql:  
        condition: service_healthy # 等待 postgresql 健康检查通过  

      redis:  
        condition: service_healthy # 等待 redis 健康检查通过  

  

# 定义具名卷，用于持久化存储数据  

# 即使容器被删除，数据也会保留在这些卷中  

volumes:  
  postgresql_data:  
    driver: local  
  redis_data:  
    driver: local
```

### **2. `compose.yaml` 解释**

- •  `name`  : 定义整个应用栈的名称，在 Docker Desktop 中会显示这个名字。
- •  `services`  : 包含我们应用所有组件的列表，如  `postgresql`  ,  `redis`  ,  `app`  。
- •  `postgresql`  /  `redis`  :

* •  `image`  : 指定要使用的镜像。这里我们直接用了 Bitnami 提供的预配置镜像，非常方便。
* •  `environment`  : 设置容器内的环境变量，用于配置数据库和Redis。
* •  `volumes`  : 这是  **数据持久化**  的关键。  `postgresql_data:/bitnami/postgresql`  意思是将一个名为  `postgresql_data`  的数据卷挂载到容器内 Postgres 存储数据的路径。这样即使容器被删除重建，数据依然存在。
* •  `healthcheck`  : Docker 会根据  `test`  命令来判断服务是否真的准备好了，这对于控制启动顺序至关重要。

- •  `app`  :

* •  `build`  : 告诉 Compose 不需要去 Docker Hub 拉取镜像，而是根据指定的  `context`  和  `dockerfile`  在本地构建。
* •  `ports`  : 和  `docker run`  中的  `-p`  作用一样。
* •  `env_file`  : 加载环境变量配置文件。
* •  `depends_on`  : Compose 最强大的功能之一。它确保  `app`  服务在  `postgresql`  和  `redis`  的  `healthcheck`  变为 "healthy" 状态之后才会启动，完美解决了应用启动时数据库还没准备好的问题。

- •  `volumes`  : 在文件末尾声明我们用到的具名卷  `postgresql_data`  和  `redis_data`  。

### **3. 修改配置以适应 Compose 网络**

当所有服务都由 Docker Compose 管理时，它们会被放入同一个虚拟网络中。在这个网络里，  **可以直接使用服务名作为主机名**  进行通信！

修改你的  `.env.dev`  文件，将  `host.docker.internal`  替换为服务名：

```

# /.env.dev  

  

# ...  

  

# 数据库配置 (使用 Compose 中的服务名)  

DEMO_DB_HOST=postgresql   
DEMO_DB_PORT=5432  

# ...  

  

# Redis 配置 (使用 Compose 中的服务名)  

DEMO_REDIS_HOST=redis:6379 
```

**为什么？**   
 因为 Docker Compose 内置了 DNS 服务。对于  `app`  容器来说，访问  `postgresql`  这个域名，会被 Docker 自动解析到  `postgresql`  容器的内部IP地址。

### **4. 启动整个应用栈**

现在，万事俱备，只需在项目根目录运行一条命令：

```
docker compose up -d
```

**命令解释**  ：

- •
  `docker compose up`
  : 启动
  `compose.yaml`
  文件中定义的所有服务。
- •
  `-d`
  : (detached) 同样表示在后台运行。

Compose 会首先检查  `compose.yaml`  ，然后并行拉取或构建所有服务的镜像，并按照  `depends_on`  的顺序依次启动它们。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2gGhydUiaS87ddxnVPcF7wXFCMq5cJVwXLib9P8rqRyT2TXIGBgVCLAicfwscjqMZmdpjw12MkwTNQw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

此时再打开 Docker Desktop，你会看到一个名为  `fastapi-demo-project`  的应用栈（Stack），里面包含了我们定义的三个正在运行的容器。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs2gGhydUiaS87ddxnVPcF7wXic5iajibJicu244SPAjQZfOuVKRibPBCm4tHLoV6LDaSh0VDh3Qekb3ibg0Q/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

### **5. 自动创建数据库表**

当使用 Compose 启动一个全新的数据库容器时，里面的数据库是空的。我们需要让 FastAPI 应用在启动时自动创建表。这可以通过在  `lifespan`  事件处理器中调用  `create_db_and_tables()`  来实现。

对于更复杂的生产场景，通常会使用 Alembic 等数据库迁移工具，并在启动脚本中运行迁移命令。但对于新手系列，  `create_db_and_tables()`  已经足够简单好用。

### **6. 关闭并清理**

当你不再需要这个应用栈时，可以使用以下命令来关闭并移除所有相关的容器、网络和（可选的）数据卷：

```
docker compose down
```

### **结语**

恭喜你！到这里，你已经掌握了如何使用 Docker 和 Docker Compose 将一个 FastAPI 项目及其依赖服务进行容器化，这是从开发走向部署的关键一步。你可以将项目镜像发布到 Docker Hub 等镜像仓库，方便在任何地方快速部署。

FastAPI 新手系列到此就告一段落了。希望这个系列能为你打下坚实的基础。编程之路，学无止境，真正的成长始于你根据自己的需求，不断实践和创造。期待在下一个系列中与大家再会！

接下来，我就是着手编写 fastapi-users 的教程，由于这个库没有中文文档，我将对照英文文档，尽量写的详细点。

后续这个系列有时间的话会补充一下关于测试的文章，测试也是很重要的一个环节。

> 前文及本文详细代码请移步我的 GitHub 项目：   
>  https://github.com/acelee0621/fastapi-demo-project

> FastAPI 新手系列合集：   
>  [FastAPI 项目实战：给新手从零到一的异步之旅](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzk2NDk1MzgwOQ==&action=getalbum&album_id=4084843978460463116#wechat_redirect)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/icqSakibXlSs1ulvHwbTy18BWAlFoneMEDBKcat04USUFU1VjU5mFUayrE6SE4nHmGbInDv8rTic0Z98EF0MCZGxA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)