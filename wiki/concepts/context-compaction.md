---
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [pi-session-system, hermes-agent-context-management, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, context-management, context-compaction, summarization, token-budget]
---

# Context Compaction（上下文压缩）

## 定义

上下文压缩是在模型上下文窗口受限时，将较早、低价值或高冗余内容转换为更短表示，同时保留继续完成任务所需状态的机制。一个完整方案必须回答五个问题：**何时压、压缩要保住什么、从哪里切、怎样压、下一次怎样更新。**

```text
上下文压缩
  ├─ 1. 压缩时机：什么时候触发？
  ├─ 2. 压缩目标：必须保住什么？
  ├─ 3. findCutPoint：旧历史与近期原文在哪里分界？
  ├─ 4. 压缩方法：如何降低 token？
  └─ 5. 更新压缩：多次压缩如何继承已有 checkpoint？
```

## 1. 压缩时机

| 方案 | 触发依据 | 优点 | 定位 |
|---|---|---|---|
| Preflight 主动压缩 | 请求前估算 `contextTokens > contextWindow - reserveTokens` | 在请求失败前释放空间 | 主路径 |
| 响应后校准 | Provider 返回真实 `prompt_tokens` 后判断 | 用真实用量修正估算偏差 | 校准路径 |
| Overflow 错误恢复 | 捕获 context-length 错误后压缩并重试 | 覆盖估算失败和模型窗口变化 | 兜底路径 |
| 手动压缩 | 用户执行 `/compact [focus]` | 可指定保留重点或主动建立 checkpoint | 控制入口 |
| 任务阶段压缩 | 完成阶段性目标或准备切换子任务时 | 摘要边界语义完整 | 可选优化 |

### 推荐组合

```text
Preflight 主动压缩
        ├─ 响应后真实 token 校准阈值
        ├─ Overflow 错误压缩兜底
        └─ 手动 focus 压缩作为控制面
```

不要只依赖错误后压缩；也不要只依赖字符估算。较稳妥的方案是“主动预防 + 真实用量校准 + 错误兜底”。

## 2. 压缩目标

压缩目标不是“生成一段更短的聊天摘要”，而是：**以更少 token 保留继续工作的最小充分状态。**

### 必须保留

- 当前 Goal 与验收条件。
- 用户约束、偏好和禁止事项。
- Done / In Progress / Blocked 状态。
- 已做出的关键决策及原因。
- 下一步动作和未解决问题。
- 精确文件路径、函数名、命令、错误信息和关键数据。
- 最近一段原始消息，尤其是最后一条 user 消息。
- 完整的 tool call / tool result 配对。

### 优先压缩

- 已完成且细节不再影响后续工作的过程记录。
- 重复解释、重复工具输出和低价值观察。
- 可以由文件、数据库或工具重新读取的大段内容。
- 已被稳定结论覆盖的探索过程。

### 不应混入

稳定 system prompt 和 tool schemas 应有独立预算及缓存策略，不宜和普通会话历史一起反复摘要。长期记忆也应进入 [[agent-memory-system]]，而不是无限堆积在 Session checkpoint 中。

## 3. `findCutPoint`：切点选择

切点同时决定摘要覆盖范围和近期原文保留范围。`reserveTokens` 决定**何时压**，`keepRecentTokens` 决定**从哪里切**，二者应分开配置。

### 基础算法

```python
def find_cut_point(messages, keep_recent_tokens, estimate_tokens):
    kept = 0
    cut = len(messages)

    for i in range(len(messages) - 1, -1, -1):
        cost = estimate_tokens(messages[i])
        if kept + cost > keep_recent_tokens:
            break
        kept += cost
        cut = i

    return move_to_safe_boundary(messages, cut)
```

### 安全边界规则

1. **优先切在完整 turn 边界**，不要把同一轮用户意图和助手执行拆开。
2. **不可拆开工具对**，`tool_call` 与对应 `tool_result` 必须同留或同压。
3. **保护最后 user 消息**，避免压缩后忘记当前问题。
4. **中间切分时补前缀摘要**，保留下来的 turn 后半段必须能独立理解。
5. **为估算误差留余量**，不能把保留区刚好塞满窗口。
6. **允许重要性提升**，关键决策或用户约束即使较旧，也应进入 checkpoint，而不是机械丢弃。

### 推荐策略

```text
反向 token 累计
    ↓
得到候选 cut point
    ↓
向前调整到 turn / tool-pair 安全边界
    ↓
抽取候选区中的关键约束与决策进入摘要
    ↓
生成 firstKeptEntryId
```

## 4. 压缩方法

| 方法 | 做法 | 适用场景 | 风险 |
|---|---|---|---|
| 结构化 checkpoint | 用固定字段总结旧历史，保留近期原文 | 长期编码、研究任务 | 摘要遗漏关键事实 |
| Append-only compaction | 新增压缩节点，由投影替代旧消息 | 需要审计、分支和恢复的 Session | 存储持续增长 |
| 工具结果裁剪 | 保留 head + tail，中间用占位或摘要替代 | 超长日志、搜索结果、文件内容 | 丢失中间关键行 |
| 抽取式保留 | 原样保留约束、决策、错误和路径 | 精确信息不可改写时 | 压缩率有限 |
| 分层/多阶段摘要 | 先分段总结，再合并为全局 checkpoint | 超长会话或多子任务 | 成本与延迟较高 |
| 破坏性截断 | 直接删除最旧消息 | 无持久化要求的极简场景 | 不可恢复，不推荐作主方案 |

### 推荐主方案

```text
旧历史 ──结构化摘要──────────────┐
关键事实 ──抽取式原样保留────────┼─▶ checkpoint
超长工具结果 ──head/tail 裁剪────┘
近期消息 ─────────────────────────▶ recent raw messages

模型输入 = checkpoint + recent raw messages
```

在需要完整审计和分支能力时，优先使用 [[context-compaction-checkpoint]]：压缩结果作为新 Entry 写入，旧消息仍保留在事实存储中，由 [[session-context-projection]] 决定本次模型看到的视图。

## 5. 更新压缩

多次压缩不能每次从零总结全部历史，否则成本会随会话长度持续增长，并容易丢失旧 checkpoint 中的关键事实。

### 增量更新

```text
上一版 checkpoint
        +
上次压缩后的新增对话
        ↓
更新状态迁移
  ├─ In Progress → Done / Blocked
  ├─ 合并新的 Key Decisions
  ├─ 刷新 Next Steps
  ├─ 保留仍有效的 Constraints
  └─ 删除已失效或被明确推翻的状态
        ↓
新 checkpoint
```

### 好方案应包含

- **版本化而非覆盖事实**：append-only 系统追加新 compaction 节点，保留旧版本以便审计。
- **增量合并**：输入“旧 checkpoint + 新增区间”，而不是重新处理全量历史。
- **状态迁移**：显式更新 Done、In Progress、Blocked 和 Next Steps。
- **冲突处理**：新决策覆盖旧决策时，记录变化原因，避免两个版本同时生效。
- **Anti-thrashing**：压缩收益过低时停止连续压缩，可设置最小节省比例或冷却轮数。
- **质量校验**：确认最后 user 请求、工具配对、关键路径和错误信息仍存在。
- **分支局部性**：只继承当前 leaf 路径上的最新 checkpoint，不混入其他分支状态。

## 推荐参考架构

```text
每次模型请求前
    │
    ├─ 计算/估算当前 token
    │
    ├─ 未超阈值 ──────────────────────────────▶ 直接投影
    │
    └─ 超阈值
         │
         ├─ findCutPoint：反向累计 + 安全边界修正
         ├─ 构造：旧 checkpoint + 新增待压缩历史
         ├─ 生成：结构化新 checkpoint
         ├─ 校验：当前问题、工具对、路径、约束
         ├─ 持久化：追加 compaction Entry
         └─ 投影：checkpoint + recent messages
```

## 与相关概念的关系

- [[context-management]]：上位概念，除压缩外还包括缓存保护、工具配对和预算管理。
- [[context-compaction-checkpoint]]：append-only、可追溯的具体压缩方法。
- [[session-context-projection]]：将 checkpoint 与近期原文组装为模型消息。
- [[append-only-session-persistence]]：保存完整历史和历次压缩事件。
- [[agent-memory-system]]：承接跨 Session、长期稳定的知识，不与上下文压缩混用。

## 来源

- [[pi-session-system]]
- [[hermes-agent-context-management]]
- [[nanobot-framework-analysis]]
- [[openclaw-framework-analysis]]
- [[opencode-framework-analysis]]
