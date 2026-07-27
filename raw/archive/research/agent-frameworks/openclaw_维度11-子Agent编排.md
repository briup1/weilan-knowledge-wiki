# 维度名：子 Agent 编排（Sub-Agent Orchestration）

## 1. 一句话定位

子 Agent 编排是 OpenClaw 的"任务委派系统"——它允许一个 Agent 将复杂任务分解为子任务，派生独立的子 Agent 执行，并通过事件驱动的交付机制将结果回传，同时通过深度限制和生命周期管理防止子 Agent 无限膨胀。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **复杂任务无法分解**：用户要求"分析整个代码库并生成文档"时，没有子 Agent，主 Agent 需要在单一会话中完成所有工作，上下文会迅速溢出。
- **长任务阻塞交互**：一个耗时 30 分钟的任务会占用主 Agent 的全部注意力，期间用户无法发送新消息。
- **子任务失败影响全局**：如果某个子任务（如"分析第 3 个模块"）失败，没有隔离机制的话会导致整个会话失败。
- **资源无限递归**：Agent 可能递归生成子 Agent（A 生成 B，B 生成 C...），最终耗尽系统资源。

### 2.2 OpenClaw 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 用户或 Agent 调用 spawn 工具 | `src/agents/tools/subagents-tool.ts` | Agent 主动请求生成子 Agent |
| 子 Agent 完成任务 | `src/agents/subagent-announce.ts` | 子 Agent 生命周期结束时触发结果交付 |
| 深度超过限制 | `src/agents/subagent-depth.ts` | 嵌套深度超过配置阈值时拒绝生成 |
| 父 Agent 发送 steer 消息 | `src/agents/subagent-control.ts` | 向运行中的子 Agent 发送指令 |
| Cron 任务触发 | `src/cron/isolated-agent/` | 隔离 Agent 执行定时任务 |

---

## 3. 核心设计思路

### 3.1 抽象模型

子 Agent 编排可以抽象为一个**树形任务分解模型**：

```
[父 Agent] ──spawn──→ [子 Agent A] ──spawn──→ [子 Agent A-1]
              │                              │
              └──spawn──→ [子 Agent B]      └──spawn──→ [子 Agent A-2]
```

每个子 Agent 有：
- 独立的 session（隔离上下文）
- 独立的 workspace 继承策略
- 生命周期事件（start/end/error）
- 结果回传机制（announce）

同时有一个**深度守卫**防止树无限增长。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 子 Agent 上下文隔离 | 每个子 Agent 有独立 session | 共享父 Agent 的上下文 | `subagent-spawn.ts` 生成新的 `sessionKey`，说明作者认为上下文隔离是防止复杂任务相互干扰的关键 |
| 结果交付模式 | 事件驱动的 push 模式（announce） | 父 Agent 轮询查询 | `subagent-announce.ts:L82` 的注释 "Auto-announce is push-based...do NOT call sessions_list...or any polling tool" 明确禁止轮询 |
| 深度限制策略 | 基于 session store 中记录的 `spawnDepth` 递归计算 | 简单的 session key 前缀计数 | `subagent-depth.ts:L124-176` 递归遍历 `spawnedBy` 链，说明作者认为深度需要从根节点精确计算 |
| 子 Agent 控制 | steer（发送消息）+ abort（强制终止） | 直接操作子进程 | `subagent-control.ts` 通过 gateway 调用发送消息，说明作者选择了一种"消息传递"而非"进程控制"的模型 |

### 3.3 数据流/控制流

```
[父 Agent] → spawn 工具调用
                ↓
        [深度检查] → subagent-depth.ts
                ↓
        [生成 session] → subagent-spawn.ts
                ↓
        [注册到 registry] → subagent-registry.ts
                ↓
        [子 Agent 执行] → 独立运行
                ↓
        [生命周期事件] → start / end / error
                ↓
        [结果 announce] → subagent-announce.ts
                ↓
        [交付到父 Agent] → 作为用户消息注入
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：子 Agent 生成与深度控制

**作用**：创建独立的子 Agent 会话，并限制嵌套深度防止无限递归。

**设计意图**：子 Agent 的生成必须受控。没有深度限制，Agent 可能陷入"为每个子任务都生成子 Agent"的递归，最终耗尽资源。

**关键源码**（`src/agents/subagent-depth.ts:L124-176`）—— 递归深度计算：

```typescript
export function getSubagentDepthFromSessionStore(
  sessionKey: string | undefined | null,
  opts?: { cfg?: OpenClawConfig; store?: Record<string, SessionDepthEntry> },
): number {
  const depthFromStore = (key: string): number | undefined => {
    const normalizedKey = normalizeSessionKey(key);
    if (!normalizedKey) return undefined;
    if (visited.has(normalizedKey)) return undefined;  // 防循环

    visited.add(normalizedKey);
    const entry = resolveEntryForSessionKey({ sessionKey: normalizedKey, cfg: opts?.cfg, store: opts?.store, cache });

    const storedDepth = normalizeSpawnDepth(entry?.spawnDepth);
    if (storedDepth !== undefined) return storedDepth;

    const spawnedBy = normalizeSessionKey(entry?.spawnedBy);
    if (!spawnedBy) return undefined;

    const parentDepth = depthFromStore(spawnedBy);
    if (parentDepth !== undefined) return parentDepth + 1;
    return getSubagentDepth(spawnedBy) + 1;
  };

  return depthFromStore(raw) ?? fallbackDepth;
}
```

这段代码展示了深度计算的复杂性：
1. **优先读取显式存储的 `spawnDepth`**（如果 session store 中有记录）
2. **递归遍历 `spawnedBy` 链**计算深度
3. **防循环检测**（`visited` Set）——防止损坏的数据导致无限递归
4. **Fallback 到 session key 编码的深度**（`getSubagentDepth`）

为什么如此复杂？因为子 Agent 可能在不同时间点生成，session store 可能在不同进程中被访问，需要多种方式确定深度以确保安全。

### 机制 B：事件驱动的结果交付（Announce）

**作用**：子 Agent 完成后，将结果通过事件推送给父 Agent。

**设计意图**：子 Agent 的执行是异步的——父 Agent 发出 spawn 请求后继续自己的工作（或等待）。结果不能依赖父 Agent 主动查询，因为父 Agent 可能处于等待状态或正在处理其他任务。

**关键源码**（`src/agents/subagent-spawn.ts:L82-85`）—— Push 模式声明：

```typescript
export const SUBAGENT_SPAWN_ACCEPTED_NOTE =
  "Auto-announce is push-based. After spawning children, do NOT call sessions_list, sessions_history, exec sleep, or any polling tool. " +
  "Wait for completion events to arrive as user messages, track expected child session keys, and only send your final answer after ALL expected completions arrive.";
```

这段注释非常明确地禁止了**轮询模式**。为什么？因为轮询会：
1. 浪费 API 调用（反复查询状态）
2. 增加复杂性（需要实现查询逻辑）
3. 延迟结果接收（轮询间隔导致延迟）

Push 模式让子 Agent 在完成时主动通知父 Agent，更高效且简单。

**关键源码**（`src/agents/subagent-announce.ts:L103-120`）—— 交付错误分类：

```typescript
const TRANSIENT_ANNOUNCE_DELIVERY_ERROR_PATTERNS: readonly RegExp[] = [
  /\berrorcode=unavailable\b/i,
  /\bstatus\s*[:=]\s*"?unavailable\b/i,
  /no active .* listener/i,
  /gateway not connected/i,
  /gateway timeout/i,
  /\b(econnreset|econnrefused|etimedout|enotfound|ehostunreach|network error)\b/i,
];

const PERMANENT_ANNOUNCE_DELIVERY_ERROR_PATTERNS: readonly RegExp[] = [
  /unsupported channel/i,
  /unknown channel/i,
  /chat not found/i,
  /bot was blocked by the user/i,
];
```

交付错误被分为**瞬态**（可重试）和**永久**（不应重试）。这种分类确保了 announce 的可靠性——瞬态网络问题会自动重试，而永久错误（如用户已删除聊天）不会浪费资源。

### 机制 C：子 Agent 注册表

**作用**：跟踪所有子 Agent 的运行状态，支持查询、控制和生命周期管理。

**设计意图**：子 Agent 是异步运行的，需要一个中央注册表来跟踪它们的状态。父 Agent 可能需要"列出所有运行中的子 Agent"或"终止某个子 Agent"。

**关键源码**（`src/agents/subagent-registry.ts:L65-99`）—— 内存注册表 + 持久化：

```typescript
const subagentRuns = new Map<string, SubagentRunRecord>();
let sweeper: NodeJS.Timeout | null = null;
let listenerStarted = false;
let listenerStop: (() => void) | null = null;
var restoreAttempted = false;
const SUBAGENT_ANNOUNCE_TIMEOUT_MS = 120_000;
const MAX_ANNOUNCE_RETRY_COUNT = 3;
const ANNOUNCE_EXPIRY_MS = 5 * 60_000;
const ANNOUNCE_COMPLETION_HARD_EXPIRY_MS = 30 * 60_000;
```

注册表设计的关键参数：
- **Announce 超时**：120 秒——子 Agent 结果必须在 2 分钟内交付
- **最大重试**：3 次——防止无限重试
- **Announce 过期**：5 分钟——非完成 announce 的过期时间
- **完成硬过期**：30 分钟——等待子代完成的最长时间

这些参数体现了作者对**异步系统可靠性的精细控制**——既要保证结果交付，又要防止无限等待。

### 机制 D：子 Agent 控制（Steer）

**作用**：向运行中的子 Agent 发送指令（如"停止当前任务，转而做 X"）。

**设计意图**：子 Agent 一旦启动就是自主运行的，但父 Agent 可能需要干预。Steer 机制提供了一种"软控制"方式——不强制终止，而是发送消息让子 Agent 自行调整。

**关键源码**（`src/agents/subagent-control.ts:L45-52`）—— 速率限制：

```typescript
export const MAX_STEER_MESSAGE_CHARS = 4_000;
export const STEER_RATE_LIMIT_MS = 2_000;

const steerRateLimit = new Map<string, number>();
```

Steer 消息有字符限制（4K）和速率限制（2 秒间隔）。这是因为 steer 是一种"干预"机制——过于频繁的干预会破坏子 Agent 的自主性。

---

## 5. 与其他维度的交互

```
[子Agent编排] --(spawn 请求)--> [编排循环]
[子Agent编排] --(子 Agent 工具调用)--> [工具系统]
[子Agent编排] --(结果注入父会话)--> [上下文管理]
[子Agent编排] --(注册表状态)--> [状态管理]
[子Agent编排] --(深度限制检查)--> [验证循环]
[子Agent编排] <--(生命周期事件)-- [编排循环]
[子Agent编排] <--(session 存储)-- [状态管理]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环 | spawn 请求触发新的 Agent 执行循环 | `subagent-spawn.ts` 的 `spawnSubagent` |
| 输出到 | 工具系统 | 子 Agent 可以调用与父 Agent 相同的工具集 | `pi-tools.ts` 的 `createOpenClawCodingTools` |
| 输出到 | 上下文管理 | 子 Agent 结果作为消息注入父会话 | `subagent-announce.ts` 的交付逻辑 |
| 输出到 | 状态管理 | 子 Agent 运行状态存入注册表 | `subagent-registry.ts` |
| 依赖 | 编排循环 | 子 Agent 独立执行自己的 turn 循环 | `pi-embedded-runner/run.ts` |
| 依赖 | 状态管理 | session store 记录 spawn 深度和父子关系 | `subagent-depth.ts` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"子 Agent 应该和父 Agent 一样自主"**：子 Agent 有独立的 session、独立的上下文、独立的工具访问权限。这假设子 Agent 是"平等的协作者"而非"受控的奴隶"。
2. **"事件驱动优于轮询"**：Push-based announce 的设计假设异步事件通知是最可靠的交付方式。
3. **"深度限制比权限控制更重要"**：`subagent-depth.ts` 限制了嵌套层数，但没有限制子 Agent 能做什么（它可以使用和父 Agent 相同的工具）。这假设深度是主要的资源消耗来源。

### 6.2 这个设计的代价/风险

1. **结果交付的不可靠性**：Announce 机制依赖网络、gateway 连接和正确的 session 路由。任何一个环节失败，父 Agent 就永远收不到结果。虽然重试机制存在，但最终仍可能失败。
2. **子 Agent 的失控风险**：子 Agent 一旦启动就高度自主。虽然可以 steer 和 abort，但如果子 Agent 正在执行危险操作（如删除文件），干预可能有延迟。
3. **上下文分裂**：子 Agent 的上下文与父 Agent 完全隔离。这意味着子 Agent 无法直接访问父 Agent 的"记忆"，需要通过显式传递（attachments、system prompt）。

### 6.3 如果要重新设计，可能会改变什么

1. **结果交付的可靠性增强**：当前 announce 是一次性的 push。可以考虑结合 pull 模式作为 fallback——如果 push 失败，父 Agent 可以在适当时候查询结果。
2. **子 Agent 的能力继承**：当前子 Agent 要么继承全部工具，要么没有。可以考虑更细粒度的能力继承（如只允许子 Agent 使用某些工具）。
3. **父子上下文的选择性共享**：允许父 Agent 标记某些上下文（如当前任务目标）为"共享"，自动传递给所有子 Agent。

### 6.4 对我自己设计 Agent 系统的启示

> **子 Agent 编排的核心不是"生成子进程"，而是"定义清晰的委托契约"**。OpenClaw 的设计启示是：成功的子 Agent 系统需要三个要素——（1）明确的任务边界（通过独立 session 隔离），（2）可靠的结果回传（push-based announce），（3）防止无限递归的守卫（深度限制）。缺少任何一个，子 Agent 都会从"便利工具"变成"系统漏洞"。
