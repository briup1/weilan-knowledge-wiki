---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/FastAPI + Celery 实战：异步任务里调用 Redis 和数据库的全解析，及生产级组织方案.md
tags: [fastapi, celery, redis, 异步任务, sqlalchemy, 生产实践]
---

# FastAPI + Celery 实战：异步任务里调用 Redis 和数据库的全解析，及生产级组织方案

## 摘要

本文从一个真实踩坑案例切入，深入剖析了在 FastAPI 项目中使用 Celery 执行异步任务时，如何正确管理数据库会话和 Redis 连接的核心问题。文章指出，Celery 任务在独立的工作进程（worker）中执行，与 FastAPI 请求进程分离，因此绝不能将主进程中的数据库会话或 Redis 连接直接传给任务。正确的做法是在 Celery 任务函数内部重新创建所需的资源，并在任务执行完毕后确保资源被正确关闭或归还。文章展示了一套生产级的代码组织方案，包括目录结构、Celery 应用配置、基于上下文管理器的资源管理（`get_db_session` 和 `get_redis_conn`）、具体的 Celery 任务编写，以及在 FastAPI 路由中调用任务的方式。最后给出了错误重试配置和任务幂等性设计的进阶建议。

## 核心要点

- **核心原则：职责分离**：Celery worker 与 FastAPI 请求进程分离，必须在任务内部重新创建数据库 Session 和 Redis 连接，不能直接传递主进程的资源
- **为什么不能传递会话**：数据库会话通常不可序列化；即使序列化成功，worker 端的底层连接可能已关闭或不存在
- **目录结构**：`app/api/`（路由）、`app/core/`（数据库、Redis、Celery 配置）、`app/models/`（模型）、`app/schemas/`（Pydantic）、`app/tasks/`（Celery 任务）
- **Celery 应用配置**：使用 Redis 作为 broker 和 backend，配置序列化、时区、任务超时等参数，`include` 指定自动发现任务模块
- **资源管理上下文管理器（重点）**：
  - `get_db_session()`：每个任务独立创建 SQLAlchemy Session，自动 commit/rollback/close
  - `get_redis_conn()`：每个任务从连接池独立获取 Redis 连接，用完归还（`conn.close()` 只是归还连接池）
- **Celery 任务编写**：使用 `@celery_app.task` 装饰器，在任务内部通过 `with` 语句使用上下文管理器获取资源
- **FastAPI 路由调用**：只传递必要的业务数据（如 `user_id`、`image_path`），调用 `.delay()` 异步触发任务，返回 `task_id`
- **错误重试**：配置 `autoretry_for=(Exception,)`、`retry_backoff=True`、`max_retries=3`，处理数据库暂时性连接问题
- **任务幂等性**：设计任务时保证幂等，使用条件更新（如 `UPDATE ... WHERE status = 'processing'`）避免重试导致重复执行

## 原始文件

- [原始文件](../../raw/archive/FastAPI + Celery 实战：异步任务里调用 Redis 和数据库的全解析，及生产级组织方案.md)
