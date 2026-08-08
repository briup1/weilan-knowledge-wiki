---
type: concept
created: 2026-08-05
updated: 2026-08-05
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
