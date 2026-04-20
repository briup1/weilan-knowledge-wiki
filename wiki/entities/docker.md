---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [fastapi-docker-compose-deploy]
tags: [docker, container, devops, deployment, microservices]
---

# Docker

Docker 是一个开源的容器化平台，允许开发者将应用及其依赖打包到轻量级、可移植的容器中，从而在任何环境中实现一致的运行体验。

## 核心组件与特性

- **镜像（Image）**：只读模板，包含运行应用所需的代码、运行时、库和配置。镜像分层存储，便于复用和缓存。
- **容器（Container）**：镜像的运行实例，相互隔离且独立于宿主机环境。启动速度快，资源占用低。
- **Dockerfile**：定义镜像构建步骤的文本文件，支持多阶段构建（Multi-stage build）以显著减小最终镜像体积。
- **Docker Compose**：通过声明式的 `compose.yaml` 编排多服务应用，自动处理服务发现、网络配置和依赖启动顺序。
- **轻量高效**：与传统虚拟机相比，容器共享宿主机内核，无需完整的操作系统，启动时间以秒计，资源利用率更高。
- **环境一致性**：开发、测试、生产环境使用同一镜像，彻底消除"在我机器上能跑"的问题。

## 使用指南与最佳实践

- **多阶段构建**：将构建阶段和运行阶段分离，最终镜像只包含运行所需的代码和依赖，显著减小体积并提升安全性。
- **`.dockerignore`**：排除 `__pycache__`、`.venv`、`tests/` 等无关文件，减小镜像体积并加速构建。
- **非 root 用户运行**：在 Dockerfile 中创建专用用户（如 `appuser`）并以该用户运行应用，是容器安全的关键最佳实践。
- **健康检查与依赖控制**：在 `compose.yaml` 中为数据库等服务配置 `healthcheck`，并在应用服务中使用 `depends_on.condition: service_healthy`，确保依赖就绪后才启动应用。
- **数据持久化**：使用具名卷（named volumes）保存数据库和缓存数据，确保容器删除后数据依然保留。
- **服务发现**：Compose 管理的容器可直接使用服务名（如 `postgresql`、`redis`）作为主机名通信，内置 DNS 自动解析。

## 相关来源

- [[fastapi-docker-compose-deploy]] —— FastAPI 项目 Docker 容器化部署完整教程
