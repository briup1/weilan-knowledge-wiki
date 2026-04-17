---
title: FastAPI + Celery 实战：异步任务里调用 Redis 和数据库的全解析，及生产级组织方案
source: https://mp.weixin.qq.com/s/7o5uRgEPFgm_W3g0-x6_og
created: 2026-04-16
category: Fastapi
tags:
  - Fastapi
  - type/hands-on
  - type/tutorial
  - Celery
  - Redis
  - SQLAlchemy
  - Async
status: archived
references: Archive/FastAPI + Celery 实战：异步任务里调用 Redis 和数据库的全解析，及生产级组织方案.md
---

> 核心原则：**Celery 任务必须在内部独立创建和关闭资源（数据库 Session、Redis 连接）**，不能依赖 FastAPI 请求进程注入的资源。

## 问题背景

Celery 的任务在独立的工作进程（worker）中执行，和 FastAPI 的请求进程是分离的。如果你在 API 路由里通过依赖项注入创建了一个数据库会话，然后把这个会话对象传给 Celery 任务，会发生什么？

- **数据库会话不可序列化**：SQLAlchemy 的 `Session` 通常不是可序列化的，根本传不到 worker 那边。
- **连接生命周期错乱**：就算通过技巧序列化了，worker 拿到的底层数据库连接可能早已在原始进程中关闭，导致各种稀奇古怪的报错。
- **Redis 连接同理**：如果把连接池里"借"出来的连接直接传给 Celery 任务，序列化后在 worker 端完全无法使用。

**解决方案**：在 Celery 任务函数内部，**重新创建所需的资源**，并在任务执行完毕后，**确保这些资源被正确关闭或归还**。

## 生产级组织方案

### 1. 目录结构

```
project/
├── app/
│   ├── api/              # 路由层
│   ├── core/             # 核心配置
│   │   ├── database.py   # 数据库引擎、SessionLocal 工厂
│   │   ├── redis_client.py # Redis 连接池
│   │   └── celery_app.py   # Celery 应用实例
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic 模型
│   └── tasks/            # Celery 任务模块
│       ├── __init__.py
│       └── user_tasks.py
└── ...
```

### 2. Celery 应用配置

在 `core/celery_app.py` 中创建 Celery 实例，并配置 broker 和 backend（通常用 Redis）。

```python
# core/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["app.tasks.user_tasks"]  # 自动发现任务模块
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 任务超时时间 30 分钟
)
```

### 3. 资源管理上下文管理器（重点）

在 `core/database.py` 和 `core/redis_client.py` 中定义好工厂和上下文管理器，供 Celery 任务独立使用。

```python
# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

engine = create_engine(
    "mysql+pymysql://user:pass@localhost/db",
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 超出 pool_size 最大连接数
    pool_pre_ping=True,     # 自动重连检测
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session() -> Session:
    """每个 Celery 任务独立创建一个数据库会话，用完即关"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

```python
# core/redis_client.py
import redis
from contextlib import contextmanager

redis_pool = redis.ConnectionPool(
    host="localhost",
    port=6379,
    db=0,
    max_connections=20,
    decode_responses=True,
)

@contextmanager
def get_redis_conn():
    """每个 Celery 任务独立获取一个 Redis 连接，用完归还"""
    conn = redis.Redis(connection_pool=redis_pool)
    try:
        yield conn
    finally:
        # 如果使用了连接池，关闭连接只是归还给池子
        conn.close()
```

**关键点**：`get_db_session` 和 `get_redis_conn` 确保了每一个独立的 Celery 任务都拥有一个属于自己的、生命周期完整的资源。

### 4. 编写具体的 Celery 任务

在 `tasks/user_tasks.py` 里编写具体的业务逻辑，使用 `@celery_app.task` 装饰器定义任务。

```python
# tasks/user_tasks.py
from app.core.celery_app import celery_app
from app.core.database import get_db_session
from app.core.redis_client import get_redis_conn
from app.models.user import User
import time

@celery_app.task(name="process_avatar")
def process_avatar(user_id: int, image_path: str):
    """处理用户头像的异步任务"""
    # 1. 更新数据库状态：processing
    with get_db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        user.avatar_status = "processing"
        db.commit()

    # 2. 模拟耗时的图片处理（可替换为实际图片处理库）
    time.sleep(3)

    # 假设处理成功，生成缩略图路径
    thumbnail_path = f"/thumbnails/{user_id}.jpg"

    # 3. 更新 Redis 状态
    with get_redis_conn() as redis:
        redis.set(f"user:{user_id}:avatar:status", "completed")
        redis.set(f"user:{user_id}:avatar:thumbnail", thumbnail_path)

    # 4. 再次更新数据库最终状态
    with get_db_session() as db:
        user.avatar_status = "completed"
        user.avatar_thumbnail = thumbnail_path
        db.commit()

    return {"status": "success", "user_id": user_id, "thumbnail": thumbnail_path}
```

### 5. 在 FastAPI 路由中调用 Celery 任务

```python
# api/user.py
from fastapi import APIRouter, UploadFile, File
from app.tasks.user_tasks import process_avatar
import uuid

router = APIRouter()

@router.post("/upload_avatar")
async def upload_avatar(user_id: int, file: UploadFile = File(...)):
    # 保存文件到临时目录（省略）
    temp_path = f"/tmp/{uuid.uuid4()}.jpg"
    # 将文件写入磁盘...

    # 调用 Celery 任务，只传递必要的业务数据
    task = process_avatar.delay(user_id, temp_path)
    return {"task_id": task.id, "status": "queued"}
```

## 进阶思考与踩坑预警

### 错误重试

Celery 自带重试机制。可以配置：

```python
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
```

让任务在遇到异常时自动重试，这对处理数据库暂时性连接问题很有帮助。

### 任务幂等性

设计任务时尽量保证幂等，因为重试可能导致同一个任务被执行多次。比如更新数据库状态时，可以用 `UPDATE ... WHERE status = 'processing'` 这样的条件来避免重复执行。

## 核心原则总结

Celery 任务里的资源管理，核心就是一个"**职责分离**"的原则：

- FastAPI 路由只负责接收请求和触发任务；
- Celery Worker 只负责执行业务逻辑，并在任务内部独立管理自己的资源；
- 不要跨进程传递数据库会话或 Redis 连接等不可序列化的对象。

---

## 来源与归档

- 原始素材：[Archive/FastAPI + Celery 实战：异步任务里调用 Redis 和数据库的全解析，及生产级组织方案.md](../../../Archive/FastAPI%20+%20Celery%20实战：异步任务里调用%20Redis%20和数据库的全解析，及生产级组织方案.md)
