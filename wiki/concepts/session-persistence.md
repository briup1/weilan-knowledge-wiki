---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [hermes-agent-state-management, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis, pi-session-system]
tags: [agent, session, persistence, transactional-storage, event-log, recovery]
---

# Session persistence（会话持久化）

## 定义

会话持久化是将消息、状态变更、工具结果、分支关系与压缩检查点保存为**跨进程存续的会话事实**，并在重启后恢复可继续运行状态的能力。它负责“可靠地存了什么”，但不直接决定“本轮发给模型什么”；后者属于 [[session-context-projection]]。

## 核心边界

```text
运行时状态
  │  append / transaction
  ▼
持久化事实 ── load / replay ──> 内存索引与当前 leaf
  │                                │
  │                                └─ 继续写入
  └─ context projection ─────────> 模型可见 messages
```

- **存储层**保存完整事实、顺序、标识和父子关系。
- **恢复层**重建索引、游标及必要的运行状态。
- **投影层**只选择当前路径所需内容，不等同于读取全部历史。
- **压缩层**可以追加摘要检查点改变投影结果，而不删除旧事实。

## 主要持久化方案

### 事务型数据库存储

把 Session、Message、Part 或状态元数据保存为表和行，通过事务保证多记录更新的一致性。

| 设计点 | 常见实现 | 适用价值 |
|---|---|---|
| 事务与约束 | SQLite / 关系模型 | 原子更新、结构化查询、关联约束 |
| 读写并发 | WAL、锁、重试退避 | 降低读写互斥与写竞争 |
| 检索索引 | FTS5 或独立索引 | 历史全文搜索与定位 |
| Schema 演进 | reconciliation、版本门控迁移 | 随功能演进补列、回填和升级 |

该方案适合查询维度多、需要事务更新或多个会话共享数据库的系统，但必须明确迁移、锁竞争和崩溃恢复策略。

### Append-only 事件日志

每次变化写成不可变 Entry，只追加、不原地改写旧记录。JSONL 的 Entry-per-line 是一种极简落地：顺序写盘后，可通过逐行加载和 Replay 重建内存状态。

```text
header
entry A
entry B(parent=A)
entry C(parent=B)
compaction(parent=C)
```

[[append-only-session-persistence]]、[[session-entry-tree]] 和 `leafId` 组合后，可同时支持审计、恢复、分支与非破坏性压缩。代价是日志持续增长，复杂查询通常还需要内存索引、快照或外部数据库。

### Snapshot + Replay

周期性保存状态快照，并从快照之后回放增量记录：

```text
完整历史 Replay      → 恢复简单，历史越长启动越慢
Snapshot + tail Replay → 恢复更快，需要保证快照与日志边界一致
```

纯 JSONL 会话可以只做 Replay；长生命周期或高频事件系统通常需要快照、检查点或分段日志控制恢复成本。

## Schema 演进

不同存储模型需要不同的兼容策略：

- **关系型存储**：声明式 Schema reconciliation、版本门控迁移、幂等回填。
- **事件日志**：Entry 类型版本、可选字段、向后兼容读取器和未知类型容错。
- **投影逻辑**：新旧 Entry 必须能被同一恢复流程解释，不能只升级写入端。

Schema 演进的目标不是追求统一格式，而是确保旧会话在新版本中仍可加载、恢复和投影。

## 并发与崩溃恢复

| 风险 | 设计原则 |
|---|---|
| 多写者覆盖 | 单写者、文件锁、数据库事务或乐观版本控制 |
| 进程中断留下坏尾部 | 原子提交，或允许读取器跳过不完整尾记录 |
| 内存与磁盘游标不一致 | 持久化成功后再发布可见状态，恢复时重新推导 leaf |
| 日志无限增长 | Snapshot、分段、归档；不要以破坏历史换取模型窗口压缩 |
| 新版本无法读取旧数据 | 版本化 Entry 与幂等迁移 |

## 推荐决策顺序

```text
是否需要复杂查询和多记录原子更新？
  ├─ 是 → 事务型数据库存储
  └─ 否 → 是否强调审计、分支和可回放？
           ├─ 是 → Append-only 事件日志
           └─ 否 → 简单 Snapshot

历史或启动成本持续增长？
  └─ 增加 Snapshot + tail Replay，而不是删除仍有审计价值的事实
```

实际系统也可以混合使用：数据库保存可查询实体，事件日志保存完整变更事实，Snapshot 加速恢复。

## 与相关概念的关系

- [[state-management]] 覆盖运行时状态与持久化状态的整体生命周期；本概念聚焦会话事实的落盘、恢复与演进。
- [[append-only-session-persistence]] 是会话持久化的一种通用方法。
- [[session-entry-tree]] 是支持分支历史的持久化数据模型。
- [[session-branching-and-forking]] 消费持久化的父子关系与 leaf 游标。
- [[session-context-projection]] 将持久化事实转换成当前模型视图。
- [[context-compaction-checkpoint]] 通过新增检查点改变投影，而不是删除历史。

## 来源

- [[hermes-agent-state-management]]
- [[nanobot-framework-analysis]]
- [[openclaw-framework-analysis]]
- [[opencode-framework-analysis]]
- [[pi-session-system]]
