---
type: concept
created: 2026-07-26
updated: 2026-08-08
sources: [hermes-agent-tool-system, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis, pi-tool-call-lifecycle, pi-tool-registration-and-extension, pi-custom-tools-and-extension, ai-agent-book-async-agent-experiment]
tags: [agent-architecture, tool-system, mcp, tool-registry, tool-contract, async-tool, rbac, abac, adapter]
---

# Agent Tool System（工具系统）

## 定义

工具系统是 Agent 与外部世界之间的执行层。它负责工具的**供给与发现、契约设计、可见性选择、调用调度、异步恢复和故障隔离**，把模型提出的调用意图转换为 Runtime 可控制、可观测、可恢复的动作。

核心边界是：**模型选择工具，Runtime 拥有执行权；工具声明能力，Agent 不应靠猜测决定同步、异步、权限或错误语义。**

## 能力主干

```text
工具来源
  → 发现与注册
  → 契约归一化
  → 可见性与选择
  → 调用生命周期
       ├─ 同步：执行后直接返回 ToolResult
       └─ 异步：返回 job_id，完成后用事件恢复
  → 故障隔离与恢复
```

| 能力 | 解决的问题 | 主要产物 |
|---|---|---|
| 工具供给与发现 | 工具从哪里来，何时加入或退出系统 | Tool Registry、版本快照 |
| 工具契约设计 | 模型和 Runtime 如何理解同一个工具 | ToolDefinition、执行语义 |
| 可见性与选择 | 哪些工具能被本次模型看到并执行 | Active Tools、授权决策 |
| 调用生命周期 | 调用如何校验、执行、观测和回填 | ToolResult、Tool Event |
| 异步执行与唤醒 | 长任务如何释放 Agent 并在完成时恢复 | Job Record、Completion Event |
| 故障隔离与恢复 | 单个工具失败如何不拖垮整个 Loop | Error ToolResult、JobEvent |
| 外部互操作 | 如何接入远程工具与协议生态 | Client Adapter、协议网关 |

## 工具供给与发现

工具定义可来自四类入口：

| 来源 | 典型方法 | 生命周期 |
|---|---|---|
| 内置工具 | 静态清单、自注册 | 随 Runtime 启动 |
| 应用工具 | SDK `customTools` | 随应用实例创建 |
| Extension | `registerTool`、ResourceLoader | 可加载、重载、卸载 |
| 远程工具 | 服务端能力发现 | 按连接、TTL 或版本刷新 |

所有入口应汇入同一 Registry，避免内置工具、插件工具和远程工具各走一条执行链。动态发现需要缓存失效、命名冲突、版本切换和失败回退；详见 [[agent-extension-system]]。

### 注册与发现模式

| 模式 | 说明 | 优缺点 |
|---|---|---|
| 自注册 | 每个工具模块调用 `registry.register(...)` | 新增工具只改一处；但仍需显式加载模块 |
| 装饰器扫描 | 用装饰器标记函数，启动时扫描 | 集中注册；需防导入顺序和隐式副作用 |
| 中心化清单 | 手工维护 name → handler 映射 | 简单直接；Schema 与 Handler 容易漂移 |
| 远程动态发现 | 从外部服务获取工具列表并刷新 | 支持外部生态；需要缓存、健康检查和回退 |

### 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 注册方式 | 自注册 + AST 扫描兜底 | `Tool` 抽象 + Registry 字典 | 多层策略管道 + 沙箱 | DSL 定义 + 注册中心 |
| Schema 处理 | Schema 清洗 + 参数强制 | 同一参数定义生成 Schema 和校验 | 组合 Schema 扁平化、参数别名 | zod 参数校验、模型级过滤 |
| 错误处理 | 错误降级为字符串 | 错误字符串 + 修复提示 | 循环检测 + 策略阻断 | ToolCall 修复与降级 |
| 动态工具 | MCP 刷新 + generation + TTL | MCP 懒加载 + Wrapper | 策略管道控制可见性 | 注册中心运行时组装 |
| 沙箱与权限 | 环境后端抽象 | 工作区路径限制 | Docker 沙箱 + FS Bridge | Permission 规则引擎 |

## 工具契约设计

一个完整 ToolDefinition 不只是参数 Schema，还要告诉 Runtime 该工具如何运行：

```json
{
  "name": "start_report_generation",
  "description": "启动报表生成",
  "input_schema": {},
  "output_schema": {},
  "execution_mode": "async",
  "cancellable": true,
  "progress_events": true,
  "timeout_seconds": 900,
  "idempotent": true
}
```

这是一种**通用契约形状**，不是 Codex、MCP 或某个框架的固定声明格式。具体字段可变，但以下语义必须明确：

- **输入输出**：参数类型、必填项、结果结构和截断规则。
- **执行模式**：同步、异步，或由 Runtime 根据策略选择。
- **副作用**：只读还是写操作，是否要求审批或串行化。
- **可靠性**：超时、幂等、重试条件、取消能力。
- **观测性**：是否产生进度事件、日志和审计记录。

同步或异步应优先由工具契约声明，Runtime 可根据超时预算、部署形态和用户策略收紧或覆盖；不应让 Agent 根据工具名称或自然语言描述临场猜测。

## 工具可用性的三阶段管道

```text
Definition Registry
  → 准入：allowedToolNames
  → 暴露：Active Tools → Provider tools
  → 执行授权：beforeToolCall
```

- **准入**决定工具能否进入候选定义集合。
- **暴露**决定模型本次请求能看到哪些工具。
- **执行授权**决定模型已经请求后是否允许真正运行。

工具过多时，应按任务、角色、权限和当前环境裁剪，而不是把整个仓库塞给模型。System Prompt 中的工具描述不是调用能力来源，Provider 的结构化 `tools` 字段才是。

## Schema 与 Adapter 归一化

不同 Provider 和外部服务对 Schema、认证、分页、错误格式的要求不同。工具层应通过 Adapter 收口：

- 将外部入参与结果映射为统一内部 Schema。
- 处理认证、重试、限流、分页和错误包装。
- 对 Provider 不支持的 Schema 关键字做兼容转换。
- 保持 ToolDefinition 与 Handler 使用同一份类型事实，避免两套定义漂移。

```python
class BaseSearchAdapter:
    async def search(self, query: str, cursor: str | None = None) -> SearchPage: ...
```

## 调用与执行边界

模型生成 ToolCall 后，统一经过 [[tool-call-lifecycle]]：

```text
lookup → repair → validate → authorize
       → execute → observe → normalize result
       → ToolResult 或 JobAccepted
```

- 同步工具在当前 Runtime Turn 内返回 ToolResult。
- 异步工具只完成“启动”，立即返回 `job_id` 和接受状态；真实结果由完成事件在后续恢复，详见 [[async-tool-execution-and-wakeup]]。
- 只读、互不依赖的调用可以并行；有副作用、共享资源或顺序依赖的调用必须串行或显式加锁。

## 工具类型学

| 类型 | 调用方向 | 作用对象 | 设计重点 |
|---|---|---|---|
| 感知工具 | Agent 主动调用 | 获取信息 | 结构化结果、分页、截断、缓存、可并行 |
| 执行工具 | Agent 主动调用 | 改变世界 | 校验、权限、沙箱、验证、幂等 |
| 协作工具 | Agent 主动调用 | 其他 Agent 或人类 | 上下文传递、任务边界、HITL |
| 事件触发工具 | 外部事件触发 | 启动或恢复 Agent | 事件过滤、载荷、去重和队列 |
| 用户沟通工具 | Agent 主动调用 | 用户或外部渠道 | 异步消息、送达状态、召回机制 |

## 执行—验证—反馈闭环

执行工具尤其是写文件、运行代码和修改外部状态时，应把自动验证纳入结果：

- 写代码后执行语法检查、linter 或测试。
- 执行命令后检查返回码，长输出截断并持久化原文位置。
- 验证结果作为工具结果的一部分回传，使 Agent 下一轮可以修正。

这与 [[validation-loop]] 的调用后护栏是同一原则在工具层的落地。

## 故障边界

工具不存在、参数非法、权限拒绝、Handler 异常等可恢复故障，应转成与原调用配对的 ToolResult。异步任务的超时、取消、迟到结果和重复完成，则应转成带 `job_id`、`event_id` 和终态的 JobEvent。详见 [[error-handling]]。

## 与相关概念的关系

- [[agent-extension-system]] 负责插件发现、动态加载与 Hook。
- [[tool-call-lifecycle]] 负责单次 ToolCall 的执行协议。
- [[async-tool-execution-and-wakeup]] 负责长耗时工具的任务状态和完成恢复。
- [[agent-runtime-event-stream]] 负责在线进度和生命周期观测。
- [[agent-security]] 与 [[validation-loop]] 负责危险工具审批和执行护栏。
- [[mcp]] 是外部工具互操作的一种具体协议，不等于整个工具系统。
- 工具系统在 [[orchestration-loop]] 中被反复调度，结果经 [[output-parsing]] 归一化后回灌上下文。
- 权限钩子与动态工具可见性可参考 [[mcp-permission-middleware]]。

## 当前证据

当前证据来自 Hermes、nanobot、OpenClaw、OpenCode、Pi 的工具与 Extension 实现，以及 AI Agent Book 异步 Agent 实验中的后台任务、`task_id` 和完成事件回注机制。
