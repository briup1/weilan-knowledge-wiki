---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, tool-system, mcp, tool-registry]
---

# Agent Tool System（工具系统）

## 定义

工具系统是 Agent 与外部世界交互的「双手」：负责工具的**发现、注册、schema 编排、过滤和调度分发**。它把 LLM 生成的工具调用意图转化为实际可执行动作，并把结果回传给 LLM。

## 为什么需要

- LLM 本身不能读文件、查数据库、调用 API；需要工具扩展能力边界。
- 工具数量多时，必须解决发现、分组、动态启用/禁用、命名空间冲突等问题。
- 不同 provider 对 tool schema 的容忍度不同，需要统一出口做兼容处理。
- MCP 等动态工具协议要求运行时可增删工具，需要可变的注册表。

## 核心组成

| 组件 | 作用 |
|---|---|
| 工具注册表 | 统一存储 name → schema/handler/check_fn |
| 发现机制 | 自动发现内置工具、插件、MCP server |
| Schema 编排 | 按启用 toolset 过滤、做 provider 兼容转换 |
| 调度分发 | 把 LLM 调用的 name/args 路由到对应 handler |
| 参数校验/修复 | 把模型输出的松散参数转换成 handler 期望类型 |

## 设计模式

| 模式 | 说明 | 优缺点 |
|---|---|---|
| 自注册 | 每个工具模块顶层调用 `registry.register(...)` | 新增工具只改一处；依赖图清晰；需显式 import |
| 装饰器扫描 | 用装饰器标记函数，启动时扫描 | 集中注册；但装饰器顺序/导入顺序可能引入魔法 |
| 中心化清单 | 手工维护 name → handler 映射表 | 简单直接；但 schema/handler 容易不同步 |
| MCP 动态 | 从 MCP server 拉 tool list，运行时刷新 | 支持外部工具生态；需要失效和缓存策略 |

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 注册方式 | 模块顶层 `registry.register(...)` 自注册 + AST 扫描兜底 | `Tool` ABC + 手动 `ToolRegistry` 字典注册 | 多层策略管道 + 沙箱隔离 | 统一 DSL 定义 + 注册中心 |
| Schema 处理 | `sanitize_tool_schemas` + `coerce_tool_args` 兼容多 provider | `parameters` property 与 `to_schema()` 共用同一份 dict；手写轻量校验 | `anyOf`/`oneOf` 扁平化；参数别名兼容 | zod 参数校验；模型级工具过滤 |
| 错误处理 | 错误降级为字符串，不中断循环 | 错误字符串 + `_HINT` 后缀 | 循环检测 + 策略阻断 | `experimental_repairToolCall` 修复/降级 |
| 动态工具 | MCP 动态刷新 + `_generation` 计数器 + TTL | MCP 懒加载，MCPToolWrapper 也继承 `Tool` | 6 层策略管道控制 | 注册中心运行时组装 |
| 沙箱/权限 | 环境后端 ABC | `restrict_to_workspace` 注入 allowed_dir | Docker 沙箱 + `SandboxFsBridge` | `PermissionNext` 规则引擎 |
| 独特设计 | 工具集分组 + `check_fn` TTL 缓存 | 先 cast 再 validate 的"类型防火墙" | 多层策略管道 + 循环检测 | DSL 定义 + zod 一体 |

## 与相关概念的关系

- 工具系统在 [[orchestration-loop]] 内被反复调用。
- 工具执行结果需要 [[output-parsing]] 规范化后回灌上下文。
- 危险工具需要 [[agent-security]] 和 [[validation-loop]] 审批。
- MCP 工具是工具系统与 [[mcp]] 协议的交汇点。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `ToolRegistry` 实现：自注册、AST 扫描兜底、`_generation` 计数器 + TTL 缓存、并发安全。其他框架待补充。
