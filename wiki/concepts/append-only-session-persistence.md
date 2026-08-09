---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system, nanobot-framework-analysis]
tags: [session, persistence, append-only, jsonl, crash-recovery]
---

# Append-only Session Persistence（只追加会话持久化）

## 定义

Append-only Session Persistence 是将每次会话变化作为不可变事件追加到文件或日志中，再通过索引与投影恢复当前状态的持久化模式。JSONL 与该模式天然匹配：每个事件一行，新增事件无需重写旧数据。

## 写入结构

```jsonl
{"type":"session","id":"s1"}
{"type":"message","id":"e1","parentId":null}
{"type":"message","id":"e2","parentId":"e1"}
{"type":"compaction","id":"e3","parentId":"e2","firstKeptEntryId":"e1"}
```

文件是平的，树关系编码在 `parentId` 中。内存通常维护：

```text
fileEntries: Entry[]       顺序扫描与追加
byId: Map<id, Entry>       O(1) 父节点查找
leafId: id | null          当前分支游标
```

## 写入时机

Pi 的实现会在第一条 assistant 消息前暂缓持久化：

```text
尚无 assistant 消息 → 只留内存，flushed = false
第一条 assistant 出现 → 一次性写入此前 entries
此后                 → 每个新 entry 追加一行
```

这避免模型尚未回复就中断时，留下只有用户提问的半截 Session。

## 恢复过程

```text
JSONL 逐行解析
    │  跳过损坏行
    ▼
fileEntries 平数组
    │
    ├─ byId[id] = entry
    └─ leafId = 最后一个非 header entry.id
    │
    ├─ 向上：[[session-context-projection]] 构造当前路径
    └─ 向下：两趟扫描临时构造 children 树
```

因此崩溃恢复不需要单独快照流程：打开文件、重建索引即可继续。JSONL 的坏尾行通常也不会破坏此前完整记录。

## 优势与代价

| 优势 | 代价 |
|---|---|
| 历史可审计、分支不丢失 | 文件会持续增长 |
| 追加写简单，崩溃影响局部 | 复杂查询依赖内存索引或外部数据库 |
| 压缩无需破坏原文 | 需要明确存储与模型视图的边界 |
| 容易回放和重建状态 | 并发写入仍需锁或单写者约束 |

## 与会话持久化的关系

[[session-persistence]] 是上位能力，Append-only 事件日志是其中一种实现方法。它优先保证顺序写入、可回放与历史可审计；若系统需要复杂查询、跨记录事务或快速启动，可与事务型数据库、索引和 Snapshot 组合。

## 来源

- [[pi-session-system]]
- [[nanobot-framework-analysis]]
