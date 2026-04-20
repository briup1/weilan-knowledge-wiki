---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250904_FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板.md
tags: [fastapi, fastapi-users, 项目模板, 实战, pydantic-settings, 生产实践]
---

# FastAPI-Users 保姆级教程（七）：实战篇——构建包含用户认证的项目模板

## 摘要

本文是 FastAPI-Users 系列的实战收官篇，从零开始构建一个生产级、可复用的用户认证模板项目。项目采用分层架构（core/models/schemas），集成了多项生产最佳实践：使用 `pydantic-settings` 设计的智能配置系统支持 PostgreSQL 和 SQLite 一键切换；数据库连接层提供了完整的异步引擎和会话管理；用户认证核心采用 Bearer 传输 + Database 策略的组合，比纯 JWT 更安全（支持服务端令牌失效）；通过 `lifespan` 管理应用生命周期，确保资源正确释放。该模板可直接作为新项目起点，也可作为微服务架构中的独立用户认证服务。文章还展望了后续扩展方向：集成 Alembic 迁移、编写业务钩子、添加 OAuth2 第三方登录、容器化部署。

## 核心要点

- **项目结构**：`app/core/`（配置、数据库、用户管理器）、`app/models/`（SQLAlchemy 模型）、`app/schemas/`（Pydantic 模型）、`app/lifespan.py`（生命周期管理）、`app/main.py`（应用入口）
- **智能配置（pydantic-settings）**：
  - `DB_TYPE: Literal["postgres", "sqlite"]` 作为总开关，通过环境变量一键切换数据库
  - `@computed_field`（Pydantic v2）动态计算 `DATABASE_URL` 和 `SQLALCHEMY_ENGINE_OPTIONS`
  - PostgreSQL 连接池精细化配置（POOL_SIZE、MAX_OVERFLOW、POOL_TIMEOUT、POOL_RECYCLE）
  - `@lru_cache` 实现 Settings 单例模式
- **数据库连接层**：全局 `engine` 和 `SessionFactory` 实例，统一的 `get_db` 依赖，`get_user_db` 和 `get_access_token_db` 解耦封装
- **认证策略选择**：Bearer + DatabaseStrategy（而非 JWT），因为数据库策略支持服务端令牌失效（登出/改密码后令牌立即失效）
- **current_user 依赖工厂**：`fastapi_users.current_user(active=True)` 可生成不同权限级别的依赖（active、verified、superuser），按需选用
- **应用生命周期管理**：`lifespan` 中创建数据库表（启动）和释放连接池（关闭），`await engine.dispose()` 确保资源正确释放
- **模板价值**：开箱即用、双库支持（SQLite/PostgreSQL）、异步数据库、依赖注入、分层架构
- **后续扩展方向**：Alembic 数据库迁移、业务钩子（注册后发送邮件）、OAuth2 第三方登录、Docker 容器化

## 原始文件

- [原始文件](../../raw/archive/20250904_FastAPI-Users保姆级教程（七）：实战篇——构建包含用户认证的项目模板.md)
