---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-tool-registration-and-extension.md
tags: [pi, tool-registry, tool-visibility, extension, permissions]
---

# Pi 系列 05：工具供给、暴露与 Extension

## 来源信息

- 标题：Pi 系列 05｜Tool 系统（下）：工具从哪来、怎么暴露，以及 extension 的角色
- 公众号：CodeAgent
- 发布时间：2026-06-11
- 原始链接：见归档原文

## 摘要

Pi 的 Core 只消费 `agent.state.tools`，不决定工具从哪里来。Coding Agent 将内置工具、Extension 工具和 SDK `customTools` 汇入定义 Registry，经过 `allowedToolNames` 准入与 active tools 选择后，完整通过 Provider 的结构化 `tools` 字段暴露给模型。Extension 同时提供注册机制和生命周期 Hook，但默认不附带权限拦截策略。

## 工具可见性管道

```text
内置工具 / Extension / SDK customTools
                 │
                 ▼
          Tool Definition Registry
                 │
          allowedToolNames 准入
                 │
                 ▼
             Active Tools
                 │
                 ▼
          agent.state.tools
                 │
                 ▼
Provider 请求中的结构化 tools 字段
                 │
                 ▼
             模型可见工具集
                 │
                 ▼
beforeToolCall：执行时授权与拦截
```

## 核心主张

1. **工具供给与 Core 解耦。** Core 只认最终的 `agent.state.tools`，内置、Extension 和 SDK 工具只是不同来源。
2. **工具能力来自结构化 `tools` 字段。** System prompt 中的工具简介只帮助模型理解，不是工具调用能力的真实来源。
3. **准入、暴露和执行授权是三个阶段。** Registry 白名单、active set、`beforeToolCall` 不能混为同一个权限概念。
4. **Pi 不自动做工具 Top-N 或按需加载。** Active tools 会完整暴露给模型；工具过多时的 token 策略留给应用层。
5. **Extension = 注册机制 + 生命周期 Hook。** 可注册工具、命令、Provider，也可处理 context、tool_call 等事件。
6. **默认不拦截工具。** Core 只提供 `beforeToolCall` 机制，Coding Agent 转发给 Extension；没有策略 Extension 时默认放行。
7. **Coding Agent 的内置工具集固定。** 文中分析的 7 个内置工具为 `read`、`bash`、`edit`、`write`、`grep`、`find`、`ls`。

## 关联知识

- [[pi-coding-agent]]
- [[agent-tool-system]]
- [[agent-extension-system]]
- [[tool-call-lifecycle]]
- [[agent-security]]
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

- [完整原文](../../raw/archive/pi-tool-registration-and-extension.md)
