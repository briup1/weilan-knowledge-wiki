---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250827_FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成.md
tags: [fastapi, fastapi-users, sqlalchemy, beanie, mongodb, 数据库模型]
---

# FastAPI-Users 保姆级教程（二）：文档解析——深入用户模型与数据库集成

## 摘要

本文深入解析 FastAPI-Users 官方文档中 "User model and databases" 章节，详细讲解了如何为 FastAPI-Users 配置关系型数据库（通过 SQLAlchemy）和文档数据库（通过 Beanie + MongoDB）。对于 SQLAlchemy，文章介绍了各数据库（PostgreSQL、SQLite、MySQL）的异步驱动安装与连接字符串，强调了 `expire_on_commit=False` 的硬性要求，展示了如何继承 `SQLAlchemyBaseUserTableUUID` 创建用户模型并添加自定义字段，以及如何创建 `SQLAlchemyUserDatabase` 适配器。对于 MongoDB，文章介绍了通过 Beanie 实现的无缝支持，包括 `BeanieBaseUser` 模型的定义、自动索引、数据库适配器的创建，以及在 FastAPI `lifespan` 中初始化 Beanie 的步骤。文章的核心结论是：数据库层的配置差异主要集中在 `db.py` 文件，一旦配置完成，上层业务逻辑几乎完全相同。

## 核心要点

- **SQLAlchemy 异步驱动**：
  - PostgreSQL：`asyncpg`，连接字符串 `postgresql+asyncpg://...`
  - SQLite：`aiosqlite`，连接字符串 `sqlite+aiosqlite:///...`
  - MySQL：`asyncmy`，连接字符串 `mysql+asyncmy://...`
- **`expire_on_commit=False` 硬性要求**：使用 SQLAlchemy `AsyncSession` 时必须设置，避免事务提交后对象自动过期刷新引发 I/O 死锁
- **用户模型继承**：继承 `SQLAlchemyBaseUserTableUUID` 默认使用 UUID 主键；使用 `SQLAlchemyBaseUserTable[int]` 可切换为自增整数 ID
- **数据库适配器依赖链**：路由 → `get_user_db` → `SQLAlchemyUserDatabase(session, User)` → `get_async_session` → `AsyncSession`
- **Beanie + MongoDB 支持**：安装 `fastapi-users[beanie]`，同时获得 Beanie 和 `motor`（MongoDB 异步驱动）
- **Beanie 模型配置**：继承 `BeanieBaseUser` 和 `Document`，在内部 `Settings` 类中自定义集合名称；`BeanieBaseUser` 自动在 `id` 和 `email` 上创建唯一索引
- **Beanie 初始化**：在 `lifespan` 启动事件中调用 `init_beanie(database=db, document_models=[User])`
- **切换数据库只需修改**：`db.py` 文件、用户 ID 类型提示（UUID → ObjectId）
- **生产环境建议**：使用 Alembic 等数据库迁移工具管理表结构变更

## 原始文件

- [原始文件](../../raw/archive/20250827_FastAPI-Users保姆级教程（二）：文档解析-深入用户模型与数据库集成.md)
