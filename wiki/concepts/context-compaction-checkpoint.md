---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system, hermes-agent-context-management, openclaw-framework-analysis, opencode-framework-analysis]
tags: [context-management, compaction, checkpoint, summarization, append-only]
---

# Context Compaction Checkpoint（上下文压缩检查点）

## 定义

Context Compaction Checkpoint 是把较早对话总结为可继续工作的结构化摘要，同时保留近期原文的上下文压缩模式。在 append-only Session 中，压缩被记录为一个新事件节点，而不是删除或重写历史消息。

## 触发与保留是两个预算

```text
contextTokens > contextWindow - reserveTokens
                         │
                         ▼
                    触发压缩
                         │
从最新消息向前累计到 keepRecentTokens
                         │
                         ▼
确定 firstKeptEntryId
```

以 Pi 为例，`reserveTokens` 默认约 16K，负责给模型回复预留空间；`keepRecentTokens` 默认约 20K，负责决定压缩时保留多少近期原文。两者不可混为一个阈值。

## 节点与投影语义

```text
存储：m1 → m2 → m3 → m4 → [compaction] → m5 → m6
                               ├─ summary
                               └─ firstKeptEntryId = m3

投影：[summary] → m3 → m4 → m5 → m6
```

投影由三段组成：

1. 摘要替代 `firstKeptEntryId` 之前的旧消息。
2. 从 `firstKeptEntryId` 到 compaction 前保留原文。
3. compaction 后的消息全部保留。

物理历史 m1、m2 仍存在；“不可见”不等于“已删除”。

## Checkpoint 内容

面向 Agent 连续工作的摘要应至少保存：

- Goal
- Constraints & Preferences
- Progress：Done / In Progress / Blocked
- Key Decisions
- Next Steps
- Critical Context
- 精确文件路径、函数名、错误信息和改动文件

多次压缩时，新 checkpoint 应基于旧摘要增量更新，而不是每次从零生成。当前路径只使用最新 compaction 作为投影基准。

## 切点安全

- 不应切开不可独立解释的工具调用与结果。
- 若切点落在 turn 中间，应补充该 turn 前缀摘要。
- token 估算应留安全余量，避免近似计算造成窗口溢出。

## 在上下文压缩五维模型中的位置

[[context-compaction]] 是完整决策模型；本页面描述其中一种推荐实现：

- 压缩时机：使用 preflight 阈值，也支持手动触发。
- 压缩目标：生成可继续工作的结构化 checkpoint。
- 切点方法：以 `firstKeptEntryId` 标记近期原文起点。
- 压缩方法：追加 compaction Entry，不删除历史。
- 更新压缩：基于上一份摘要增量生成新 checkpoint。

## 与一般上下文管理的关系

[[context-management]] 关注窗口预算、压缩时机和消息完整性；本模式进一步把压缩结果变成可追溯的 Session 事件，使 [[append-only-session-persistence]] 与 [[session-context-projection]] 保持解耦。

## 交互式演示

- [打开 Session Message Flow 动画](../../docs/demos/session-message-flow-demo.html)：选择“压缩节点与投影”，观察原始 Entry 保留、摘要替换旧区间的双轨结构。

## 来源

- [[pi-session-system]]
- [[hermes-agent-context-management]]
- [[openclaw-framework-analysis]]
- [[opencode-framework-analysis]]
