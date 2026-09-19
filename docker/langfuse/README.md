---
title: "本地 Langfuse"
created: 2026-09-16
updated: 2026-09-16
tags: [docker, langfuse, local-development]
---

# 本地 Langfuse

本项目的独立开发实例，不迁移老电脑的数据、用户或密钥。

老电脑 `192.168.7.248:3000` 的网页标识与健康接口确认其运行的是 **Langfuse 3.174.1**，不是 LangChain。SSH 密码认证未通过，因此尚未读取老电脑的 Docker 启动配置。

按用户要求使用当前最新稳定版 **Langfuse 4.37.0**，而非复刻旧版。官方发布于 2026-09-16，本次于同日核对 GitHub 的最新正式 Release，并确认镜像支持 ARM64。

本环境参考 `v4.37.0` 的官方 Compose，新拉取 ARM64 镜像，启动 Web、Worker、PostgreSQL、ClickHouse、Redis 和 MinIO。Langfuse Web 与 Worker 均固定为 `4.37.0`；ClickHouse 使用官方对应的 `25.12` 系列，媒体存储分别配置浏览器访问地址和容器内地址。不使用浮动的 Langfuse `latest` 标签，也不迁移旧版数据卷。

## 启动与停止

```bash
cd docker/langfuse
bash init.sh
docker compose pull
docker compose up -d --wait --wait-timeout 600
docker compose ps
```

Web 入口：`http://localhost:3000`。MinIO 对象访问端口：`http://localhost:9090`。两者均只监听本机；数据库、队列和 Worker 不发布宿主机端口。

登录账号：`weilan@local.test`。密码为 `.env` 中的 `LANGFUSE_INIT_USER_PASSWORD`。启动时会创建 `Weilan local` 组织及 `Knowledge Forest` 项目；项目 API 密钥也在 `.env` 中。

```bash
docker compose logs --tail 100 langfuse-web langfuse-worker
docker compose stop
docker compose start --wait --wait-timeout 600
docker compose down
```

`stop`、`start`、`down` 保留持久化卷。不要为了普通重启使用 `down -v`，它会删除此实例的数据。

## 镜像与密钥

- Docker Hub 镜像显式通过 `docker.m.daocloud.io` 拉取，以验证国内源的真实下载能力。
- MinIO 沿用 `v4.37.0` 官方 Compose 的 Chainguard 镜像，直接从 `cgr.dev` 新拉取。
- 如 DaoCloud 白名单或限流阻止下载，可在 `.env` 中添加 `DOCKER_REGISTRY=docker.io`，改用 Docker Hub；当前 Docker Engine 的镜像加速配置仍生效。
- 首次启动会从镜像仓库下载；重启复用本机镜像和持久化卷，不需要重复拉取。
- 基础设施使用固定主/次版本系列，MinIO 使用公开的 `latest` 标签；重新执行 `pull` 可能更新这些镜像。这是本地开发配置，不是生产部署。
- `init.sh` 只在 `.env` 不存在时生成随机密钥；已有文件不会被覆盖。不要删除 `.env` 后对已有数据卷重新生成密钥，尤其不要丢失 `ENCRYPTION_KEY`。
- `.env` 权限为 `0600` 且已被 Git 忽略；不要提交、转发或把它复制进 wiki。

## 验证

```bash
curl --fail http://localhost:3000/api/public/health
docker compose ps
```

健康接口与容器健康状态仅用于基础检查。完整验证还应使用本项目 API 密钥提交一条 Trace，并在 Worker 异步处理后通过查询接口读回，以覆盖数据库、对象存储、队列和 ClickHouse 链路。

2026-09-16 本次验收通过：Web 健康接口返回 `4.36.1`，网页 HTTP 200，六个 ARM64 容器均为 `healthy`；通过 OTLP 提交的 `docker-install-smoke-test` 已由 Worker 处理并写入 ClickHouse 的 `events_full` 表。非敏感验收证据保存在 `data/langfuse-install-check.json`。

随后发现同日发布的 `4.37.0`，已更新 Web 与 Worker 并再次验收通过：网页 HTTP 200，六个容器均为 `healthy`，新提交的 `docker-install-v4.37-smoke-test` 成功写入 `events_full`。验收证据已刷新为当前运行版本 `4.37.0`；原有账号、密钥和数据卷保持不变。

Langfuse v4 默认使用 `events_only` 写入模式。Trace 应通过兼容 v4 的 SDK 或 `/api/public/otel/v1/traces` 的 OTLP 接口提交；不要使用旧版 `/api/public/ingestion` 的 `trace-create` 事件，也不要仅为通过旧测试而启用临时迁移模式。

## 来源

- [Langfuse v4.37.0 正式发布](https://github.com/langfuse/langfuse/releases/tag/v4.37.0)
- [Langfuse v4.37.0 官方 Compose](https://github.com/langfuse/langfuse/blob/v4.37.0/docker-compose.yml)
- [官方 Docker Compose 部署文档](https://langfuse.com/self-hosting/deployment/docker-compose)
- [官方自动初始化文档](https://langfuse.com/self-hosting/administration/headless-initialization)
- [官方 OpenTelemetry 接入文档](https://langfuse.com/integrations/native/opentelemetry)
- [DaoCloud 公共镜像源](https://github.com/DaoCloud/public-image-mirror)
