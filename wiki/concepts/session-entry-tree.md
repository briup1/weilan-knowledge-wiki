---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system]
tags: [session, tree, append-only, leaf-pointer, agent-state]
---

# Session Entry Tree（会话条目树）

## 定义

Session Entry Tree 是用 **只追加节点 + `parentId` 单向父指针 + 当前 `leafId`** 保存 Agent 会话的模式。它把消息、模型切换、思考等级、压缩和扩展事件统一编码为树节点，以支持从历史位置重开而不覆盖旧后续。

## 最小结构

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

@dataclass(frozen=True)
class Entry:
    id: str
    parent_id: str | None
    type: str
    timestamp: str
    payload: dict


def append_entry(entries, by_id, leaf_id, entry_type, payload):
    entry_id = uuid4().hex       # 生成的是 entry.id
    entry = Entry(
        id=entry_id,
        parent_id=leaf_id,       # 新节点挂到当前 leaf 下
        type=entry_type,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
    )
    entries.append(entry)
    by_id[entry.id] = entry
    leaf_id = entry.id           # leafId 直接采用新 entry.id
    return entry, leaf_id
```

## 核心不变量

1. 每个非根 Entry 只有一个 `parentId`。
2. 新 Entry 默认以当前 leaf 为父节点。
3. Entry 一旦写入就不原地修改或删除。
4. `leafId` 是游标，不是独立业务实体，也不需要单独生成。
5. 一个父节点可以被多个后续 Entry 引用，因此自然形成分支。

## 为什么优于线性数组

```text
线性数组：A → B → C → D
从 C 重开：只能截断 D，或复制整个数组

Entry 树： A → B → C ─┬→ D
                       └→ E [leaf]
旧后续 D 保留，新问题 E 共享 A/B/C
```

数组足以处理保存和恢复；树的额外价值是**保留式分支**。该模式把 [[session-branching-and-forking]] 变成移动游标与追加节点，而不是删除或复制整段历史。

## 与模型上下文的边界

Entry Tree 是事实存储，不等于模型输入。模型可见历史由 [[session-context-projection]] 从当前 leaf 的祖先链计算；压缩则由 [[context-compaction-checkpoint]] 改变投影结果，而不改变旧节点。

## 来源

- [[pi-session-system]]
