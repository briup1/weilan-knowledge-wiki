---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system]
tags: [session, context, projection, messages, model-input]
---

# Session Context Projection（会话上下文投影）

## 定义

Session Context Projection 是从完整会话存储中，依据当前 `leafId` 计算本次模型可见 `messages` 的过程。它明确区分：**Entry 是持久化事实，Message 是面向模型的视图。**

## 输入与输出

```text
输入：entries + byId + leafId
          │
          ▼
定位 leaf
          │
          ▼
沿 parentId 回溯：leaf → root
          │
          ▼
反转为时间正序：root → leaf
          │
          ▼
解释路径上的状态节点与 compaction
          │
          ▼
输出：messages + model + thinkingLevel
```

## Python 极简实现

```python
def build_session_context(by_id: dict, leaf_id: str | None) -> list[dict]:
    path = []
    current = by_id.get(leaf_id) if leaf_id else None

    while current:
        path.append(current)
        current = by_id.get(current.parent_id)

    path.reverse()
    return [entry.payload["message"] for entry in path
            if entry.type == "message"]
```

真实实现还需要解释 `model_change`、`thinking_level_change`、`branch_summary`、`custom_message` 和 `compaction` 等节点。

## 两种树视图

| 目标 | 遍历方向 | 结果 |
|---|---|---|
| 给模型构造当前历史 | leaf → root | 单条祖先链 |
| 展示全部分支 | root → leaves | 临时构造的 children 树 |

投影只需要一条祖先链，因此无需 BFS/DFS；展示整棵树时，才需要扫描所有 Entry 并按 `parentId` 建 `children`。

## 路径局部性

模型切换、思考等级和压缩状态都从**当前路径**提取，而不是从整个 Session 的最后一条同类事件提取。切换 leaf 后，同一棵物理树可以得到不同消息历史与运行设置。

## 设计意义

该模式将“存了什么”和“现在发什么”解耦：

- [[session-entry-tree]] 可以保留全部历史与分支。
- [[session-branching-and-forking]] 只需改变 leaf。
- [[context-compaction-checkpoint]] 只需改变路径解释规则。
- [[append-only-session-persistence]] 无需为每个模型视图维护副本。

## 交互式演示

- [打开 Session Message Flow 动画](../../docs/demos/session-message-flow-demo.html)：逐步观察 `Entry Tree → parentId 回溯 → Message[] → agent.state.messages`。

## 来源

- [[pi-session-system]]
