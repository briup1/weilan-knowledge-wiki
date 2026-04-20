---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/FastAPI压力测试实战：Locust模拟真实用户并发及优化建议.md
tags: [fastapi, 压力测试, locust, 性能优化, gunicorn, 高并发]
---

# FastAPI 压力测试实战：Locust 模拟真实用户并发及优化建议

## 摘要

本文以通俗的比喻和实战经验，系统讲解了如何对 FastAPI 应用进行压力测试和性能优化。文章首先解释了压测的本质——在上线前模拟真实并发以发现系统瓶颈。随后对比了 ab、wrk、Locust 三种压测工具，推荐 Locust 作为 Python 开发者的首选，因为它能用纯 Python 编写压测脚本、模拟真实用户行为、自带 Web UI 实时图表，并支持分布式施压。文章提供了完整的 Locust 压测脚本示例和 FastAPI 测试接口代码，演示了从单进程到多进程的压测流程。最后总结了优化 FastAPI 性能的"三板斧"：多进程（Gunicorn + UvicornWorker）、数据库连接池、Redis 缓存热点数据，并分享了三个常见踩坑经验（不要在生产环境压测、调整系统文件句柄数、避免客户端自身成为瓶颈）。

## 核心要点

- **压测本质**：模拟真实用户并发，提前发现系统瓶颈（CPU、数据库连接、内存等），避免上线后崩溃
- **工具对比**：
  - `ab`（Apache Bench）：简单但**不支持 HTTP Keep-Alive**，对异步框架不友好，容易低估性能
  - `wrk`：性能强悍，支持 Lua 脚本，但对纯 Python 开发者有门槛
  - `Locust`：纯 Python 脚本、模拟真实用户行为、自带 Web UI、支持分布式施压，最适合 Python 开发者
- **Locust 脚本核心**：继承 `HttpUser`，设置 `wait_time = between(1, 3)` 模拟用户等待，用 `@task` 装饰器定义用户行为
- **单进程 vs 多进程压测**：uvicorn 单进程只能跑满一个 CPU 核心，是常见瓶颈；单进程 RPS 约 900，多进程（4 worker）可提升到 3000+
- **优化三板斧**：
  - **第一板斧：多进程 + Gunicorn**：`gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`，worker 数一般设为 CPU 核心数 × 2 + 1
  - **第二板斧：数据库连接池**：限制最大连接数并复用连接，避免每次请求新建连接导致数据库拒绝服务
  - **第三板斧：Redis 缓存热点数据**：对频繁访问的数据加缓存层，合理设置过期时间
- **优化效果**：同样 1000 用户，优化后 RPS 可稳定在 5000+，平均响应时间降至 200ms 以内
- **踩坑预警**：
  - 不要在生产环境直接压测
  - Linux 默认文件句柄数 1024，高并发下需修改 `/etc/security/limits.conf`
  - 单机压测时注意客户端自身是否成为瓶颈，可使用 Locust 分布式模式
- **压测是常态化工作**：每次大版本更新或架构调整都应重新压测

## 原始文件

- [原始文件](../../raw/archive/FastAPI压力测试实战：Locust模拟真实用户并发及优化建议.md)
