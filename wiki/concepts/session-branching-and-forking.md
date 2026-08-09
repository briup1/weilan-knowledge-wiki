---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system]
tags: [session, branching, fork, leaf-pointer, conversation-history]
---

# Session Branching and Forking（会话分支与派生）

## 定义

会话分支是在同一棵 [[session-entry-tree]] 中移动 `leafId`，再从历史节点追加新 Entry；会话派生（fork）则复制一条祖先路径，创建拥有独立 id、header 和存储文件的新 Session。

## 分支过程

```text
原路径：A → B → C → D [leaf]
                  │
branch(C)         │  仅 leafId = C
                  ▼
append(E)
                  │
结果：  A → B → C ─┬→ D
                    └→ E [leaf]
```

当前投影从 E 回溯得到 `A → B → C → E`；D 仍在树和磁盘中，只是不属于当前 leaf 的祖先链。

## 三种操作的边界

| 操作 | 是否新建 Session | 是否复制历史 | 核心动作 |
|---|---:|---:|---|
| `/tree` | 否 | 否 | 在同一文件内移动 leaf，切换已有分支 |
| `branch` | 否 | 否 | leaf 回到历史节点，后续 append 形成新子节点 |
| `/fork` | 是 | 是，仅根到目标节点的一条路径 | 创建新 sessionId、header、JSONL |

`branchWithSummary` 是分支的增强形式：切换后追加 `branch_summary`，把旧分支中未直接继承的关键信息作为模型消息带入新路径。

## 适用场景

- 从历史方案重新探索，同时保留原方案。
- 对同一上下文尝试不同模型、提示或工具策略。
- 将某条已验证路径独立为新任务或新会话。
- 提供可审计、可回退但不破坏历史的交互体验。

## 约束

分支本身只改变可见路径，不自动解决跨分支的信息合并。需要共享旧分支结论时，应显式追加摘要节点，而不是让投影同时读取多条分支。

## 交互式演示

- [打开 Session Message Flow 动画](../../docs/demos/session-message-flow-demo.html)：选择“分支与 leaf 切换”，观察旧分支保留而模型可见路径发生变化。

## 来源

- [[pi-session-system]]
