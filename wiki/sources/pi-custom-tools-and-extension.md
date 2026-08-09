---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-custom-tools-and-extension.md
tags: [pi, custom-tools, extension, resource-loader, sdk]
---

# Pi 系列 06：用 customTools 与 Extension 添加工具

## 来源信息

- 标题：Pi 系列 06｜实战：给应用加一个 tool（customTools 与 extension 两种方式）
- 公众号：CodeAgent
- 发布时间：2026-06-15
- 原始链接：见归档原文

## 摘要

Pi 的 `customTools` 与 Extension `registerTool()` 复用同一个 `ToolDefinition`，最终进入同一个 Registry，因此工具对模型的可见形态和执行链路相同。区别只在供给与生命周期：固定编译进应用的工具适合 `customTools`；需要可插拔、分发、重载和附带 Hook 的能力适合 Extension。

## 两种入口

```text
方式一：SDK
ToolDefinition → createAgentSession({ customTools: [...] }) ┐
                                                            ├→ 同一 Registry → Active Tools → 模型
方式二：Extension                                           │
ToolDefinition → pi.registerTool() → extensionFactories ────┘
```

## 核心主张

1. **定义相同，入口不同。** 两种方式都使用同一个 `ToolDefinition`，进入系统后没有两套执行机制。
2. **`customTools` 适合应用内固定能力。** 直接传数组，配置最少，代码归应用所有。
3. **Extension 适合插件化能力。** 可独立分发、reload，并同时注册工具、命令、Provider 与生命周期 Hook。
4. **自定义 ResourceLoader 必须显式 reload。** 传入现成 loader 时，`createAgentSession` 不会代替调用方执行 `await loader.reload()`。
5. **`noExtensions: true` 只关闭默认发现。** 内联的 `extensionFactories` 仍会执行，因此其注册工具仍可进入 active set。
6. **工具实现不应感知注册入口。** 让定义与加载方式解耦，才能在 SDK 内嵌和插件分发之间迁移。

## 选择规则

| 场景 | 推荐入口 |
|---|---|
| 工具与应用一起编译、无需动态加载 | `customTools` |
| 工具需要独立分发或 reload | Extension |
| 同时需要 Hook、命令或 Provider 注册 | Extension |
| 只需最小代码快速注入工具 | `customTools` |

## 关联知识

- [[pi-coding-agent]]
- [[agent-extension-system]]
- [[agent-tool-system]]
- [[tool-call-lifecycle]]
- [[pi-agent-runtime-architecture]]

## 本系列其他文章

- [[pi-agent-runtime-event-flow|01｜Runtime 事件流]]
- [[pi-agent-loop-and-turn|02｜Agent loop 与 turn]]
- [[pi-provider-unified-event-protocol|03｜Provider 与统一事件协议]]
- [[pi-tool-call-lifecycle|04｜ToolCall 的一生]]
- [[pi-tool-registration-and-extension|05｜工具供给、暴露与 Extension]]
- [[pi-custom-tools-and-extension|06｜customTools 与 Extension 实战]]
- [[pi-session-system|07｜Session 系统]]

## 原始文件

- [完整原文](../../raw/archive/pi-custom-tools-and-extension.md)
