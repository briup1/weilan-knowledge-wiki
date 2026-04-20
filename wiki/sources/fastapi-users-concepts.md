---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/20250826_FastAPI-Users保姆级教程（一）：核心概念与快速上手.md
tags: [fastapi, fastapi-users, 用户认证, 快速入门, 教程]
---

# FastAPI-Users 保姆级教程（一）：核心概念与快速上手

## 摘要

本文是 FastAPI-Users 系列教程的开篇，旨在帮助开发者从零开始理解并上手 fastapi-users 这一 FastAPI 生态中成熟的用户认证库（当前版本 14.0.1）。文章首先概述了 fastapi-users 的核心特性：可扩展的用户模型、开箱即用的认证路由、OAuth2 社交登录、可插拔的密码验证、多种数据库后端支持（SQLAlchemy/MongoDB）以及多种可定制的认证后端。随后深入介绍了五大核心模块：用户模型及数据库适配器、认证后端（Transport + Strategy）、UserManager、Pydantic Schemas、以及 FastAPIUsers 和 Routers。最后通过一个仅含四个文件的最小化实现示例（db.py、schemas.py、users.py、main.py），手把手演示了如何搭建一个完整的用户认证系统，并在 Swagger UI 中验证各接口功能。

## 核心要点

- **FastAPI-Users 定位**：为 FastAPI 项目快速添加注册和认证系统，强调高度可定制（customizable）和适应性（adaptable）
- **五大核心模块**：
  - 用户模型及数据库适配器（User model and database adapters）：支持 SQLAlchemy（PostgreSQL/SQLite/MySQL）和 Beanie（MongoDB）
  - 认证后端（Authentication backends）：由传输方式（Transport）和策略（Strategy）组合而成
  - 用户管理器（UserManager）：承载注册、验证、密码重置等核心逻辑的枢纽
  - Pydantic 模型（Schemas）：定义用户读取、创建、更新时的数据结构
  - FastAPIUsers 和路由（Routers）：生成认证路由和 `current_user` 依赖工厂
- **最小化实现仅需四个文件**：`main.py`（应用入口与路由挂载）、`db.py`（数据库与模型）、`schemas.py`（Pydantic 模型）、`users.py`（UserManager 与认证后端配置）
- **默认用户模型字段**：`email`、`hashed_password`、`is_active`、`is_superuser`、`is_verified`，默认使用邮箱作为用户名
- **默认主键为 UUID**：`SQLAlchemyBaseUserTableUUID` 使用 UUID 作为主键，避免暴露自增 ID；也可使用 `SQLAlchemyBaseUserTable[int]` 切换为整数 ID
- **UserManager 事件钩子**：`on_after_register`、`on_after_forgot_password`、`on_after_request_verify` 等方法允许在用户生命周期关键节点插入自定义业务逻辑
- **认证后端组合公式**：Transport（Bearer/Cookie）+ Strategy（JWT/Database/Redis）= Authentication Backend
- **current_active_user 依赖**：通过 `fastapi_users.current_user(active=True)` 生成，用于保护需要登录的路由

## 原始文件

- [原始文件](../../raw/archive/20250826_FastAPI-Users保姆级教程（一）：核心概念与快速上手.md)
