---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [fastapi-celery-redis]
tags: [celery, python, distributed-tasks, async, message-queue]
---

# Celery

Celery 是一个简单、灵活且可靠的 Python 分布式任务队列，用于处理大量消息，同时提供维护此类系统所需的工具。它专注于实时操作，同时也支持任务调度。

## 核心组件与特性

- **异步任务执行**：将耗时操作（发送邮件、图片处理、数据清洗）从请求主线程剥离到独立 Worker 进程执行，避免阻塞用户响应。
- **任务调度（Beat）**：支持定时任务和周期性任务，可替代 Linux crontab 进行集中化管理。
- **Worker**：独立进程负责从消息队列中拉取任务并执行，支持横向扩展以提升吞吐量。
- **Broker**：任务消息的中间人，常用 Redis 或 RabbitMQ。Redis 因配置简单、性能高，在中小规模场景中尤为常见。
- **Backend**：存储任务执行结果，便于后续查询。Redis 同样可作为结果后端。
- **自动重试机制**：配置 `autoretry_for`、`retry_backoff` 和 `max_retries`，可优雅处理数据库暂时性连接失败等异常。
- **任务幂等性**：设计任务时保证幂等，使用条件更新避免重试导致重复执行。

## 使用指南与最佳实践

- **资源隔离原则**：Celery Worker 与 FastAPI 请求进程分离，绝不可将主进程中的数据库会话或 Redis 连接直接传给任务；必须在任务函数内部重新创建资源并在执行完毕后正确关闭。
- **上下文管理器**：为数据库 Session 和 Redis 连接封装 `with` 语句风格的上下文管理器，确保每个任务独立获取和归还资源。
- **目录组织**：建议将任务模块放在 `app/tasks/`，与路由（`app/api/`）和配置（`app/core/`）分离，保持职责清晰。
- **调用方式**：在 FastAPI 路由中只传递必要的业务数据（如 `user_id`、`image_path`），调用 `.delay()` 异步触发任务并返回 `task_id`。
- **错误处理**：配置合理的超时和重试策略，避免无限堆积失败任务。

## 相关来源

- [[fastapi-celery-redis]] —— FastAPI + Celery + Redis 实战与生产级组织方案
