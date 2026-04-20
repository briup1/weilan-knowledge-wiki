---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250825_FastAPI项目实战：从Dockerfile到Compose，项目容器化部署保姆级教程.md
tags: [fastapi, docker, docker-compose, 容器化部署, 生产实践]
---

# FastAPI 项目实战：从 Dockerfile 到 Compose，项目容器化部署保姆级教程

## 摘要

本文是 FastAPI 新手系列的收官篇章，聚焦于如何将 FastAPI 项目及其依赖服务（PostgreSQL、Redis）进行完整的 Docker 容器化部署。文章从 Docker 的核心优势（环境一致性、简化部署、隔离安全、轻量高效）出发，逐步讲解了：编写 `.dockerignore` 为镜像瘦身、采用多阶段构建（Multi-stage build）策略编写 `Dockerfile`、单容器运行与外部服务连接（使用 `host.docker.internal`）、以及使用 Docker Compose 编排多服务应用的完整流程。文章提供了可直接复用的 `Dockerfile` 和 `compose.yaml` 配置，涵盖非 root 用户运行、层缓存优化、健康检查、服务依赖控制等生产级最佳实践。

## 核心要点

- **多阶段构建（Multi-stage build）**：将构建阶段和运行阶段分离，最终镜像只包含运行所需的代码和依赖，显著减小体积并提升安全性
- **`.dockerignore` 文件**：类似于 `.gitignore`，排除 `__pycache__`、`.venv`、`tests/` 等无关文件，减小镜像体积
- **非 root 用户运行**：在 Dockerfile 中创建 `appuser` 用户并以该用户运行应用，是容器安全的关键最佳实践
- **`host.docker.internal`**：容器访问宿主机上服务（如 PostgreSQL、Redis）时使用的特殊 DNS 名称，解决容器 `localhost` 指向容器内部而非宿主机的问题
- **Docker Compose 服务发现**：当所有服务由 Compose 管理时，可直接使用服务名（如 `postgresql`、`redis`）作为主机名进行通信，Compose 内置 DNS 会自动解析
- **健康检查与依赖控制**：在 `compose.yaml` 中为数据库和 Redis 配置 `healthcheck`，并在 `app` 服务中使用 `depends_on.condition: service_healthy` 确保应用只在依赖服务就绪后才启动
- **数据持久化**：使用具名卷（named volumes）如 `postgresql_data` 和 `redis_data`，确保容器删除后数据依然保留
- **自动创建数据库表**：在 `lifespan` 事件处理器中调用 `create_db_and_tables()`，生产环境建议使用 Alembic 等迁移工具

## 原始文件

- [原始文件](../../raw/archive/20250825_FastAPI项目实战：从Dockerfile到Compose，项目容器化部署保姆级教程.md)
