---
type: synthesis
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system, hermes-agent-context-management, hermes-agent-state-management, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, session, state-management, context-management, projection]
---

# Agent Session Storage and Context Views（会话存储与上下文视图）

## 核心结论

Agent 会话不应只有一个 `messages` 数组。更稳定的架构至少分为三层：**事实存储、当前 Session 视图、模型请求上下文**。Pi 的 Entry Tree 把这三层分得最直观，也解释了分支、压缩和恢复为何可以共用一套机制。

## 三层模型

```text
┌──────────────────────────────────────────────┐
│ 1. 事实存储                                  │
│ Entry / JSONL / SQLite：完整历史、事件、分支 │
└──────────────────────┬───────────────────────┘
                       │ 索引、路径选择
                       ▼
┌──────────────────────────────────────────────┐
│ 2. Session 视图                              │
│ 当前 leaf 的祖先链 + 当前路径上的状态节点    │
└──────────────────────┬───────────────────────┘
                       │ 压缩、裁剪、消息转换
                       ▼
┌──────────────────────────────────────────────┐
│ 3. 模型请求上下文                            │
│ system prompt + messages + tool schemas      │
└──────────────────────────────────────────────┘
```

[[pi-session-system]] 的关键贡献是说明：同一份事实存储可以在不修改历史的前提下投影出多条 Session 视图，而同一条 Session 视图又可因压缩预算投影成不同的模型上下文。

## 三类机制的统一解释

| 能力 | 事实存储变化 | 视图变化 |
|---|---|---|
| 分支 | 追加新子节点，旧分支保留 | 移动 leaf，选择另一条祖先链 |
| 压缩 | 追加 compaction/checkpoint | 用摘要替代一段旧消息 |
| 恢复 | 重新读取事件并建索引 | 从最后 leaf 重新计算路径 |
| fork | 复制选中路径到新存储 | 新 Session 独立投影 |

这比“修改 messages 数组”更容易审计，因为每次变化都能追溯到原始 Entry。

## 与其他 Agent 框架知识的关系

- [[hermes-agent-state-management]] 展示了内存运行态与 SQLite 持久态的双轨分层。
- [[hermes-agent-context-management]] 展示了 preflight、响应后和错误恢复三类压缩入口，以及工具消息配对保护。
- [[nanobot-framework-analysis]] 使用 JSONL 体现低运维成本的个人 Agent 取舍。
- [[openclaw-framework-analysis]] 将上下文预算、压缩恢复和会话并发提升到生产级控制面。
- [[opencode-framework-analysis]] 以 SQLite Session 状态机服务 IDE 场景的低延迟和可恢复交互。

这些实现的存储介质不同，但共同指向一个原则：**持久化历史、运行时状态和模型上下文不是同一种数据结构，也不应共享同一生命周期。**

## 架构设计检查表

```text
[ ] 是否区分持久化 Entry 与 Provider Message？
[ ] 当前分支是否由显式游标/leaf 决定？
[ ] 模型、思考等级、压缩状态是否具有路径作用域？
[ ] 压缩是否保留可继续工作的 checkpoint？
[ ] 工具调用与结果是否在裁剪后仍配对？
[ ] Session 是否可以从持久化数据确定性重建？
[ ] 分支和 fork 是否有清晰的文件/事务边界？
[ ] append-only 文件增长与并发写入是否受控？
```

## 进一步推论

1. **Session Tree 本质上是事件日志。** `leafId` 类似某个分支的 HEAD，`parentId` 提供历史拓扑。
2. **Compaction 本质上是物化视图检查点。** 它加速后续上下文构造，但不替代原始事实。
3. **Context Projection 是策略边界。** Provider 适配、token 预算、摘要和权限过滤都可以在这里组合，而无需污染持久化结构。
4. **恢复能力来自可重放性。** 只要事件完整、父引用有效，运行时索引和当前视图就可以重建。

## 关联概念

- [[session-entry-tree]]
- [[session-context-projection]]
- [[session-branching-and-forking]]
- [[context-compaction-checkpoint]]
- [[append-only-session-persistence]]
- [[state-management]]
- [[context-management]]
