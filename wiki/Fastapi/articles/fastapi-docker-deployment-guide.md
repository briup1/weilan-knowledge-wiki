---
title: "FastAPI 项目实战：从 Dockerfile 到 Compose，项目容器化部署保姆级教程"
created: 2026-04-17
category: "Fastapi"
tags: ["Fastapi", "type/hands-on", "type/tutorial", "Docker", "部署"]
status: "archived"
references: "Archive/20250825_FastAPI项目实战：从Dockerfile到Compose，项目容器化部署保姆级教程.md"
---

# FastAPI 项目实战：从 Dockerfile 到 Compose，项目容器化部署保姆级教程

本文是 FastAPI 新手系列的收官篇，聚焦于如何将 FastAPI 项目及其依赖服务进行 Docker 容器化部署。

## 为什么要使用 Docker？

在现代开发中，Docker 几乎是必备技能。它解决了“在我的电脑上可以跑，怎么到你那就不行了？”这个经典难题。

- **环境一致性**：将应用及其所有依赖打包到一个隔离的容器中，无论在 Windows、Mac 还是云服务器上，运行表现都完全一致。
- **简化部署**：使用 Docker Compose，只需一条命令就能启动整个应用所需的所有服务。
- **隔离与安全**：每个容器都运行在自己的沙箱环境中，不会与主机系统或其他容器互相干扰。
- **轻量与高效**：相比传统的虚拟机，Docker 容器更轻量，启动更快，资源占用更少。

## 第一步：编写 Dockerfile，为应用打包

### 1. `.dockerignore`：为镜像瘦身

在项目根目录新建 `.dockerignore` 文件，防止将本地开发环境的临时文件、缓存、虚拟环境等无关内容打包进镜像：

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

### 2. `Dockerfile`：定义镜像构建流程

采用**两阶段构建（Multi-stage build）**策略，最终镜像体积更小、更安全：

```dockerfile
# ===================================================
# -------------- 构建阶段 (Builder Stage) --------------
# ===================================================
FROM python:3.13.5-slim-bookworm AS builder

# 将 uv 从其官方镜像复制到构建环境中
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# 设置工作目录
WORKDIR /app

# 仅复制依赖定义文件，利用 Docker 的层缓存机制
COPY pyproject.toml uv.lock ./

# 使用 uv 创建虚拟环境并安装所有依赖
RUN uv venv && uv sync --frozen --no-cache

# 复制项目的全部代码到工作目录
COPY . .

# 清理构建过程中产生的无用文件
RUN find /app -type d -name '__pycache__' -exec rm -rf {} + \
    && find /app -type f -name '*.pyc' -delete

# ===================================================
# -------------- 运行阶段 (Runner Stage) --------------
# ===================================================
FROM python:3.13.5-slim-bookworm

WORKDIR /app

# 安全最佳实践：使用非 root 用户运行应用
RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app

# 从 builder 阶段复制已包含代码和虚拟环境的整个 /app 目录
COPY --from=builder --chown=appuser:appuser /app /app

# 切换到我们创建的非特权用户
USER appuser

# 将镜像内虚拟环境的 bin 目录添加到 PATH 环境变量中
ENV PATH="/app/.venv/bin:$PATH"

# 声明容器将对外暴露 8000 端口
EXPOSE 8000

# 容器启动时默认执行的命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. 构建镜像

```bash
docker build -t fastapi-demo-project:latest .
```

构建成功后，可以通过以下命令查看：

```bash
docker images fastapi-demo-project
```

## 第二步：单容器运行与外部服务连接

如果 PostgreSQL 和 Redis 运行在宿主机上，容器需要知道如何找到它们。Docker 提供了一个特殊的 DNS 名称 `host.docker.internal`，它会解析为宿主机的 IP 地址。

修改 `.env.dev` 配置文件：

```env
# 数据库配置 (从 localhost 修改为 host.docker.internal)
DEMO_DB_HOST=host.docker.internal
DEMO_DB_PORT=5432
DEMO_DB_USER=postgres
DEMO_DB_PASSWORD=postgres
DEMO_DB_DB=tutorial

# Redis 配置 (从 localhost 修改为 host.docker.internal)
DEMO_REDIS_HOST=host.docker.internal:6379
```

启动容器：

```bash
docker run -d --name fastapi-demo-app -p 8000:8000 --env-file .env.dev fastapi-demo-project:latest
```

## 第三步：使用 Docker Compose 编排多服务应用

### 1. 编写 `compose.yaml`

```yaml
name: 'fastapi-demo-project'

services:
  # 1. PostgreSQL 数据库服务
  postgresql:
    image: bitnami/postgresql:latest
    environment:
      - POSTGRESQL_USERNAME=postgres
      - POSTGRESQL_PASSWORD=postgres
      - POSTGRESQL_DATABASE=tutorial
    volumes:
      - postgresql_data:/bitnami/postgresql
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 10s
      retries: 5

  # 2. Redis 服务
  redis:
    image: bitnami/redis:latest
    environment:
      - ALLOW_EMPTY_PASSWORD=yes # 仅限开发环境
    volumes:
      - redis_data:/bitnami/redis/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 3. FastAPI 后端应用服务
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: fastapi-demo-project:latest
    ports:
      - "8000:8000"
    env_file:
      - .env.dev
    depends_on:
      postgresql:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgresql_data:
    driver: local
  redis_data:
    driver: local
```

### 2. 修改配置以适应 Compose 网络

当所有服务都由 Docker Compose 管理时，它们会被放入同一个虚拟网络中，**可以直接使用服务名作为主机名**进行通信。

修改 `.env.dev`：

```env
# 数据库配置 (使用 Compose 中的服务名)
DEMO_DB_HOST=postgresql
DEMO_DB_PORT=5432

# Redis 配置 (使用 Compose 中的服务名)
DEMO_REDIS_HOST=redis:6379
```

### 3. 启动整个应用栈

```bash
docker compose up -d
```

Compose 会按照 `depends_on` 的顺序，在 `postgresql` 和 `redis` 的健康检查通过后再启动 `app` 服务。

### 4. 关闭并清理

```bash
docker compose down
```

## 总结

本文介绍了如何使用 Docker 和 Docker Compose 将 FastAPI 项目及其依赖服务（PostgreSQL、Redis）进行容器化部署。掌握这些技能后，你可以将项目镜像发布到 Docker Hub 等镜像仓库，方便在任何地方快速部署。

---

## 来源与归档

- 原始素材：[Archive/20250825_FastAPI项目实战：从Dockerfile到Compose，项目容器化部署保姆级教程.md](../../../Archive/20250825_FastAPI项目实战：从Dockerfile到Compose，项目容器化部署保姆级教程.md)
