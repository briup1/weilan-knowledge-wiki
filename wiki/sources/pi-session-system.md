---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-session-system.md
tags: [pi, session, entry-tree, context-projection, compaction, jsonl]
---

# Pi 系列 07：Session 系统

## 来源信息

- 标题：Pi 系列 07｜Session 系统：对话怎么存、恢复、分支
- 公众号：CodeAgent
- 发布时间：2026-06-24
- 主要源码位置：`session-manager.ts`、`core/compaction/compaction.ts`

## 摘要

Pi 没有把会话持久化为线性的 `messages` 数组，而是保存为一棵 **append-only 的 `SessionEntry` 树**。每次追加时生成的是 `entry.id`，随后令 `leafId = entry.id`；模型真正收到的 `messages` 则由 `buildSessionContext(entries, leafId, byId)` 从当前 leaf 的祖先链实时投影得到。分支通过移动 leaf 实现，压缩通过追加 `compaction` 节点实现，历史节点始终保留。

## 一次提问的完整链路

```text
用户消息 msg
    │
    ▼
appendMessage(msg)
    │  生成 entry.id
    │  parentId = 当前 leafId
    ▼
_appendEntry(entry)
    ├─ fileEntries.push(entry)
    ├─ byId.set(entry.id, entry)
    ├─ leafId = entry.id
    └─ _persist(entry) → JSONL
    │
    ▼
buildSessionContext(entries, leafId, byId)
    ├─ leaf → parentId → root
    ├─ 还原为正序路径
    ├─ 应用最新模型/思考等级/压缩节点
    └─ Entry → Message[]
    │
    ▼
agent.state.messages → 模型输入
```

关键点：**`leafId` 不单独生成；生成的是新节点的 `entry.id`，然后 leaf 指针前移到该 id。**

## 数据模型

九种 `SessionEntry` 共享 `id`、`parentId`、`timestamp`：

| Entry 类型 | 作用 | 是否进入模型上下文 |
|---|---|---|
| `message` | 用户、助手或工具消息 | 是 |
| `thinking_level_change` | 记录思考等级变化 | 作为路径设置生效 |
| `model_change` | 记录模型切换 | 作为路径设置生效 |
| `compaction` | 摘要、`firstKeptEntryId`、压缩前 token 数 | 转换为摘要消息 |
| `branch_summary` | 切分支时携带旧分支摘要 | 是 |
| `custom` | Extension 自定义数据 | 否 |
| `custom_message` | Extension 自定义模型消息 | 是 |
| `label` | 为目标节点设置标签 | 否 |
| `session_info` | Session 名称等信息 | 否 |

磁盘只保存每个节点指向父节点的 `parentId`，不保存 `children`。树既可以从 leaf 沿 `parentId` 向上投影，也可以由 `getTree` 两趟扫描临时构造 `children`。

## 核心主张

1. **树的必要性来自分支，而非保存与恢复。** 数组能持久化线性历史，但无法从中间重开且保留旧后续。
2. **存储节点与模型消息是两层数据。** 写入的是完整 Entry，发送的是当前分支投影出的 Message。
3. **leaf 决定当前分支。** 移动 `leafId` 不修改历史；下一次追加会自然形成新的子节点。
4. **分支状态具有路径局部性。** 当前模型、思考等级和压缩状态只从当前 leaf 的祖先链提取。
5. **压缩是新增事件，不是破坏性改写。** `compaction` 节点用摘要替代早期上下文，但旧消息仍在树与 JSONL 中。
6. **压缩触发与保留预算分离。** `reserveTokens` 决定何时压，`keepRecentTokens` 决定保留多少近期原文。
7. **摘要是可继续工作的 checkpoint。** 固定保存目标、约束、进度、决策、下一步和关键上下文，多次压缩会增量更新摘要。
8. **JSONL 与 append-only 模型匹配。** 每个 Entry 独占一行，新增无需重写旧历史，坏尾行也不影响此前记录。
9. **首次回复前延迟落盘。** 第一条 assistant 消息出现后才批量 flush，此后逐 Entry 追加，避免留下无回复的半截会话。
10. **恢复就是读文件并重建索引。** JSONL → 平数组 → `byId`，leaf 落在最后一个非 header Entry；树结构按需现算。

## 分支与 fork

```text
/tree   → 同一 Session 内移动 leaf，切换已有分支
branch  → 移动 leaf 后继续 append，给历史节点新增子节点
/fork   → 复制根到目标节点的一条路径，创建新 sessionId 和新 JSONL
```

`/fork` 只复制选中的路径，不复制原树其他分支；新 header 用 `parentSession` 记录来源，但两个 Session 此后独立演化。

## 压缩投影

```text
物理树：m1 → m2 → m3 → m4 → [compaction] → m5 → m6
                                  │
                                  ├─ summary
                                  └─ firstKeptEntryId = m3

模型视图：[summary] → m3 → m4 → m5 → m6
```

投影分三段：摘要消息、`firstKeptEntryId` 到压缩点前的原文、压缩点后的所有消息。m1、m2 只是本次不可见，并未删除。

## 交互式演示

- [打开 Session Message Flow 动画](../../docs/demos/session-message-flow-demo.html)
- 演示覆盖：消息入树与投影、移动 `leafId` 形成分支、追加 `compaction` 节点并生成“摘要 + 近期原文”的模型视图。

## 关联页面

- [[session-entry-tree]]
- [[session-context-projection]]
- [[session-branching-and-forking]]
- [[context-compaction-checkpoint]]
- [[append-only-session-persistence]]
- [[agent-session-storage-and-context-views]]
- [[pi-coding-agent]]
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

- [原始文件](../../raw/archive/pi-session-system.md)
