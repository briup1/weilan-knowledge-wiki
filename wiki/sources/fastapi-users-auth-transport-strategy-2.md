---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250829_FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy)下.md
tags: [fastapi, fastapi-users, 认证后端, database-strategy, redis-strategy, 令牌存储]
---

# FastAPI-Users 保姆级教程（四）：认证后端揭秘——传输方式（Transport）与策略（Strategy）下

## 摘要

本文继续解析 FastAPI-Users 官方文档中 "Authentication backends" 章节的下半部分，重点讲解 Database 策略和 Redis 策略两种令牌存储方案。Database 策略将令牌存储在应用数据库中，优点是无需额外服务、支持服务端令牌失效（登出即删除），缺点是配置稍繁琐且高并发下对数据库有压力。Redis 策略利用内存键值存储的高性能读写来管理令牌，适合高并发场景，但需要额外维护 Redis 服务。文章分别展示了 SQLAlchemy 和 Beanie（MongoDB）两种数据库适配器下 AccessToken 模型的配置方式，以及 RedisStrategy 的简单配置。最后总结了 AuthenticationBackend 的创建方式，强调每个后端名称必须唯一，并演示了 Bearer + Redis 的实战组合。

## 核心要点

- **Database 策略**：将令牌存储在应用数据库中，建立包含 `token`、`user_id`、`created_at` 字段的表/集合
  - 优点：无需额外服务，支持服务端令牌失效（登出自动删除）
  - 缺点：配置稍繁琐，高并发下数据库压力大
- **AccessToken 模型（SQLAlchemy）**：继承 `SQLAlchemyBaseAccessTokenTableUUID`，结构与 User 模型配置几乎相同
  - `user_id` 外键默认使用 UUID，与用户模型主键保持一致
  - 使用 `SQLAlchemyBaseAccessTokenTable[int]` 可切换为整数 ID
- **AccessToken 模型（Beanie/MongoDB）**：继承 `BeanieBaseAccessToken` 和 `Document`
  - 自定义配置需在内部创建 `Settings` 类并继承 `BeanieBaseAccessToken.Settings`
  - 必须将 `AccessToken` 模型添加到 `init_beanie` 的 `document_models` 数组中
- **DatabaseStrategy 配置**：接收 `access_token_db`（适配器实例）和 `lifetime_seconds`（令牌生命周期）
- **Redis 策略**：使用 Redis 内存存储令牌，高性能读写，适合高并发场景
  - 安装：`pip install "fastapi-users[redis]"`
  - 配置：`RedisStrategy(redis_client, lifetime_seconds=3600)`
  - `decode_responses=True` 是必须的
  - `key_prefix` 默认值为 `fastapi_users_token:`
- **AuthenticationBackend 创建**：`AuthenticationBackend(name=..., transport=..., get_strategy=...)`
  - `name` 必须唯一，支持同时激活多个认证后端
  - `get_strategy` 是返回 Strategy 实例的可调用对象（callable）
- **Bearer + Redis 实战组合**：令牌通过 Bearer 头传输，存储在 Redis 中，兼具 API 友好性和服务端可控性

## 原始文件

- [原始文件](../../raw/archive/20250829_FastAPI-Users保姆级教程（四）：认证后端揭秘——传输方式(Transport)与策略(Strategy)下.md)
