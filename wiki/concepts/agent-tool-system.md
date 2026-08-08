---
type: concept
created: 2026-07-26
updated: 2026-08-05
sources: [hermes-agent-tool-system, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis, pi-tool-call-lifecycle, pi-tool-registration-and-extension, pi-custom-tools-and-extension]
tags: [agent-architecture, tool-system, mcp, tool-registry, rbac, abac, adapter]
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

## 工具可用性的三阶段管道

Pi 的实现补充了工具系统中三个容易混淆的决策点：

```text
Definition Registry
  → 准入：allowedToolNames
  → 暴露：Active Tools → agent.state.tools → Provider tools
  → 执行授权：beforeToolCall
```

- **准入**决定工具能否进入候选定义集合。
- **暴露**决定模型本次请求能看到哪些工具。
- **执行授权**决定模型已经请求后是否允许真正运行。

内置工具、Extension 工具和 SDK `customTools` 应汇入同一 Registry；System Prompt 的工具描述不是调用能力来源，Provider 的结构化 `tools` 字段才是。工具执行统一经过 [[tool-call-lifecycle]]，插件化供给与 Hook 参见 [[agent-extension-system]]。

## 工具类型学（五类工具）

参考 Agent 工具调用方向与作用对象，可把工具分为五类：

| 类型 | 调用方向 | 作用对象 | 设计重点 |
|---|---|---|---|
| 感知工具 | Agent 主动调用 | 获取信息 | 返回结构化候选、分页/offset、显式截断、可缓存可并行 |
| 执行工具 | Agent 主动调用 | 改变世界 | 安全优先：输入校验、权限、沙箱、自动验证、幂等 |
| 协作工具 | Agent 主动调用 | 驱动其他 Agent 或人类 | 上下文传递策略、任务边界、HITL、通知机制 |
| 事件触发工具 | Agent 注册、外部触发 | 驱动 Agent 开始执行 | 触发条件过滤、事件载荷设计、异步队列 |
| 用户沟通工具 | Agent 主动调用 | 向用户传递信息 | 异步消息、多渠道、召回机制、虚拟身份 |

## Adapter 归一化模式

当同一类工具可能对接多个外部服务（如搜索可用 DuckDuckGo / SerpAPI / Bing，天气可用 Open-Meteo / OpenWeatherMap）时，建议在工具层与外部 API 之间加一层 **Adapter**：

- 把不同 API 的入参/出参映射为统一内部 schema。
- 处理认证、重试、限流、分页、错误包装。
- 工具层只依赖统一接口，换源时不改工具逻辑。

典型接口：

```python
class BaseSearchAdapter:
    async def search(self, query: str, cursor: str | None = None) -> SearchPage: ...
```

## 执行-验证-反馈闭环

执行工具（尤其是写文件、运行代码）应在工具内部集成自动验证：

- 写代码文件后自动调用 linter（如 `py_compile`、`eslint`）。
- 执行命令后检查返回码，长输出做截断持久化。
- 验证结果作为工具返回值的一部分回传给 Agent，使其能在下一轮自修正。

这与 [[validation-loop]] 的“调用后护栏”是同一理念在不同层级的落地。

## 与相关概念的关系

- 工具系统在 [[orchestration-loop]] 内被反复调用。
- 工具执行结果需要 [[output-parsing]] 规范化后回灌上下文。
- 危险工具需要 [[agent-security]] 和 [[validation-loop]] 审批。
- MCP 工具是工具系统与 [[mcp]] 协议的交汇点。
- 权限钩子与动态工具可见性可参考 [[mcp-permission-middleware]]。

## 当前证据

当前证据来自四个 Agent 框架调研，以及 Pi 对 ToolDefinition Registry、active tools、Extension、`customTools` 与 `beforeToolCall` 的完整链路分析。
