---
type: concept
created: 2026-08-05
updated: 2026-08-08
sources: [pi-tool-registration-and-extension, pi-custom-tools-and-extension, pi-tool-call-lifecycle]
tags: [agent, extension, plugin, hooks, tool-registry]
---

# Agent Extension System

Agent Extension System 是 Agent Harness 的插件边界：允许外部模块注册工具、命令、Provider，并订阅或拦截上下文、消息和工具调用生命周期。它既是**能力供给机制**，也是**运行时 Hook 机制**。

## 两个职责

```text
Extension
  ├─ 注册：Tool / Command / Provider / Resource
  └─ Hook：context / tool_call / message / lifecycle events
```

## 与直接 SDK 注入的关系

| 方式 | 适用场景 | 特点 |
|---|---|---|
| SDK `customTools` | 应用内固定工具 | 最直接、随应用编译 |
| Extension `registerTool` | 可插拔、可分发工具 | 可 reload，可同时注册 Hook/命令/Provider |

两者应复用同一 ToolDefinition 与 Registry。Extension 不应创造独立于 Core 的第二套工具执行链路。

## 生命周期

```text
发现 / 配置 / inline factory
  → ResourceLoader.reload()
  → Extension 注册资源和 Hook
  → 构建 Tool Registry / Active Tools
  → Agent Runtime 触发生命周期事件
  → Extension 观察、修改或阻止
```

## 动态加载与原子刷新

动态加载不是“扫描到文件就立刻改 Registry”。它需要一条可回滚的发布管道：

```text
发现候选资源
  → 读取与校验定义
  → 解析依赖和权限
  → 在临时 Registry 构建新版本
  → 冲突检查
  → 原子切换 Active Tools 快照
  → 旧版本排空或卸载
```

关键状态包括：

| 状态 | 作用 |
|---|---|
| `generation` / `version` | 标识某次完整工具快照 |
| `loaded_at` / `expires_at` | 控制 TTL 和刷新时机 |
| `source` | 追踪内置、Extension、配置或远程服务来源 |
| `health` | 防止失效工具继续暴露给模型 |
| `in_flight_count` | 决定旧版本何时可以安全卸载 |

刷新失败时保留最后一个健康快照，不能把半套工具暴露给模型。正在执行的 ToolCall 绑定启动时的版本；新调用使用新版本，避免运行中 Handler 被替换。名称冲突应由命名空间、显式优先级或 fail-closed 策略处理，不能依赖加载顺序碰运气。

关闭目录扫描、远程发现和 inline factory 应分别控制。所谓“动态卸载”还要说明：只是不再向模型暴露，还是连同 Handler、连接池和后台任务一起终止。

## 设计原则

1. **注册与执行解耦。** Extension 负责供给定义，Core 负责统一执行。
2. **Hook 返回值要有明确合并规则。** 多个 Extension 同时修改 context 或阻止 ToolCall 时，顺序和冲突策略必须可预测。
3. **默认策略要显式。** 只有拦截点而没有权限 Extension 时，是默认放行还是拒绝必须写清楚。
4. **自定义 Loader 的加载责任明确。** 调用方传入 ResourceLoader 时通常应显式 `reload()`。
5. **关闭发现不等于关闭内联 Extension。** 默认目录扫描、配置发现和 inline factory 应分别控制。
6. **Extension 需要隔离与信任模型。** Hook 能修改上下文或阻止/放行工具，应纳入权限、来源和审计治理。

## 关联概念

- [[agent-tool-system]]
- [[tool-call-lifecycle]]
- [[agent-security]]
- [[agent-runtime-event-stream]]
- [[provider-protocol-normalization]]
- [[async-tool-execution-and-wakeup]]
