---
type: synthesis
created: 2026-08-05
updated: 2026-08-05
sources: [pi-agent-runtime-event-flow, pi-agent-loop-and-turn, pi-provider-unified-event-protocol, pi-tool-call-lifecycle, pi-tool-registration-and-extension, pi-custom-tools-and-extension, pi-session-system]
tags: [pi, agent-runtime, provider, tools, session, architecture]
---

# Pi Agent Runtime 架构

Pi 系列 01–07 展示了一条完整 Agent Harness 主链：用户消息先写入可分支 Session Entry Tree，再投影为模型消息；Provider adapter 把模型流归一化为统一事件；Agent loop 按 Runtime Turn 驱动 ToolCall；Tool Registry 和 Extension 决定模型能看到与实际能执行的工具；最终消息和压缩 checkpoint 继续追加到 Session。

## 端到端主链

```text
用户输入 msg
  → SessionManager.appendMessage
       Entry(id, parentId=currentLeaf)
       → append-only JSONL
       → leafId = entry.id
  → buildSessionContext(current leaf)
       Entry path → Message[]
  → agent.state.messages
  → Agent loop / Runtime Turn
       → Provider request(messages, agent.state.tools)
       → Provider wire protocol
       → 统一 AssistantMessageEvent
       → AssistantMessage
       → 若包含 ToolCall：
            prepare → validate → authorize → execute
            → ToolResultMessage 回填 context
            → 下一 Runtime Turn
       → 若无 ToolCall/steering：结束内层循环
       → 若有 follow-up：开启下一轮
  → assistant/tool messages 继续追加为 Session Entry
  → 超预算时追加 compaction checkpoint
```

## 七篇文章对应的架构切面

| 系列 | 架构问题 | 核心答案 |
|---|---|---|
| 01 | 运行过程如何可观察 | 用类型化事件暴露 Agent、Turn、消息和工具生命周期 |
| 02 | 一次 prompt 为什么多次调模型 | Business Turn 内包含多个 Runtime Turn；内层工具/steering，外层 follow-up |
| 03 | 如何兼容不同模型厂商 | Provider 与 API protocol 分离，原始流转换为统一事件 |
| 04 | ToolCall 如何真正执行 | 意图经查找、校验、授权、执行和错误转换后成为 ToolResult |
| 05 | 工具从哪里来、如何暴露 | 多来源汇入 Registry，经 active set 进入 `agent.state.tools` |
| 06 | 应用如何增加工具 | `customTools` 与 Extension 复用同一 ToolDefinition 和执行链路 |
| 07 | 对话如何存储、分支和压缩 | append-only Entry Tree 保存事实，当前 leaf 投影模型视图 |

## 三组必须分开的数据结构

| 层 | 数据 | 作用 |
|---|---|---|
| 持久化事实 | SessionEntry + parentId + JSONL | 保存完整历史、分支、设置和压缩事件 |
| 模型上下文 | Message[] + ToolDefinition[] | 当前请求中模型可见的信息和能力 |
| 在线观测 | Runtime Event Stream / Trace | UI、进度、调试、成本、错误和审计 |

把三者混成一个数组会导致分支困难、Provider 污染存储、事件无法恢复或 UI 状态与事实耦合。

## 两条正交管道

### 消息管道

```text
Session Entry Tree
  → 当前 leaf 的路径
  → context projection
  → Message[]
  → Provider adapter
  → Model
```

### 工具管道

```text
Builtin / Extension / customTools
  → Definition Registry
  → allowed / active tools
  → agent.state.tools
  → Provider tools 字段
  → Model ToolCall
  → Runtime authorization + execution
```

工具“可被模型看到”与“执行时被允许”是不同决策点。

## Turn 语义

```text
Business/User Turn
  = 用户输入 → 最终面向用户的回答

Runtime/Model Turn
  = 一次模型响应 → 该响应触发的工具结果
```

因此一个 Business Turn 通常对应一个顶层 Trace，其中包含多个 Runtime Turn / LLM Span 和 Tool Span。

## 错误边界

| 错误位置 | 推荐处理 |
|---|---|
| Provider 流创建前配置错误 | 直接抛出，阻止启动 |
| Provider 请求/解析运行期错误 | 转为统一 `error` 终止事件 |
| Tool 不存在/参数非法/权限阻止/执行失败 | 转为配对 ToolResult，让模型可恢复 |
| Session 尾部不完整 | append-only 恢复时保留此前有效 Entry，并显式报告尾部问题 |

## 架构原则

1. **事实、视图、事件分层。** Session Entry 是事实，Message 是投影视图，Runtime Event 是在线观测。
2. **控制流依据结构化事实。** 是否继续 Loop 看真实 ToolCall，而不是 Provider 的单一声明字段。
3. **Core 提供机制，外层提供策略。** 例如工具 Hook、权限、工具选择和 token 策略。
4. **统一边界降低组合复杂度。** Provider 归一化、ToolResult 归一化、Context projection 都让核心 Loop 保持稳定。
5. **历史不可变，当前视图可变。** 移动 leaf 切换分支；追加 compaction 节点改变模型视图，但不删除原始历史。

## 架构检查表

```text
[ ] Business Turn 与 Runtime Turn 是否使用不同名称？
[ ] Provider 厂商身份与 wire protocol 是否解耦？
[ ] 所有工具调用是否经过统一查找、校验、授权和错误转换？
[ ] 模型可见工具与执行时权限是否是两个决策点？
[ ] Session 持久化事实是否独立于模型 Message？
[ ] 当前分支是否由显式 leaf/cursor 决定？
[ ] 压缩是否追加 checkpoint 而非破坏性删除历史？
[ ] Runtime 事件能否稳定驱动 UI、Trace、预算与中断？
```

## 关联知识

- [[pi-coding-agent]]
- [[agent-runtime-event-stream]]
- [[agent-turn]]
- [[orchestration-loop]]
- [[provider-protocol-normalization]]
- [[tool-call-lifecycle]]
- [[agent-tool-system]]
- [[agent-extension-system]]
- [[agent-session-storage-and-context-views]]
- [[context-compaction]]
