# 维度名：状态管理（State Management）

## 1. 一句话定位

OpenClaw 的状态管理维度负责在**进程内运行时状态**、**磁盘持久化会话元数据**和**ACP 后端运行时句柄**三个层级之间维护一致性，确保 Agent 在多轮对话、并发请求和进程重启后仍能正确恢复上下文。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有这些分层状态管理机制，系统会出现以下具体故障：

1. **会话数据丢失**：`sessions.json` 直接存储在磁盘上，但如果没有 `SessionStore` 的写锁队列（`LOCK_QUEUES`）和原子写入（`writeTextAtomic`），并发写入会导致文件损坏或数据覆盖。代码中 `saveSessionStoreUnlocked` 在 Windows 下实现了最多 5 次重试（`src/config/sessions/store.ts:L466-484`），正是因为文件系统级别的并发冲突。

2. **ACP 运行时泄漏**：`AcpSessionManager` 维护的 `runtimeCache` 如果不做空闲驱逐（`evictIdleRuntimeHandles`），当 `maxConcurrentSessions` 达到上限后，新会话初始化会直接抛出 `ACP_SESSION_INIT_FAILED` 错误（`src/acp/control-plane/manager.core.ts:L1072-1077`），导致服务不可用。

3. **Gateway 聊天状态混乱**：`chatRunState` 中的 `buffers` 和 `deltaSentAt` 如果不做 150ms 节流和去重，同一轮对话的增量文本会高频广播到所有 WebSocket 客户端，造成网络拥塞和 UI 闪烁。

4. **重复执行/重复响应**：`dedupe` Map 和 `agentRunSeq` 如果不维护，同一个 `runId` 的事件可能因网络重传被处理两次，导致客户端收到重复的 assistant 消息。

### 2.2 OpenClaw 的具体触发条件

- **会话存储加载**：`loadSessionStore` 在每次 `updateSessionStore` 时触发（`src/config/sessions/store.ts:L528`），优先读取内存缓存（TTL 默认 45s），缓存失效才读磁盘。
- **ACP 运行时缓存驱逐**：`evictIdleRuntimeHandles` 在每次 `runTurn`/`getSessionStatus`/`initializeSession` 前调用（`src/acp/control-plane/manager.core.ts:L221,L329,L598`），当 `idleMs >= idleTtlMs` 时关闭后端句柄。
- **Gateway 维护定时器**：`startGatewayMaintenanceTimers` 每 60s 执行一次（`src/gateway/server-maintenance.ts:L78-133`），清理过期 dedupe 条目、超时聊天运行和已中止运行残留状态。
- **Run 状态机心跳**：`createRunStateMachine` 在 `activeRuns > 0` 时启动 60s 心跳（`src/channels/run-state-machine.ts:L44-56`），向外部状态接收器报告活跃度。

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────────────────────────────────────────────────┐
│                    Gateway 进程运行时层                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ chatRunState │  │ agentRunSeq │  │ chatAbortControllers│  │
│  │ (Map-based)  │  │ (dedupe)    │  │ (timeout + abort)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    ACP 控制平面层                              │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │ AcpSessionManager│  │ RuntimeCache (LRU + idle TTL)   │   │
│  │ (singleton)      │  │ (Map<string, CachedRuntimeState)│   │
│  └─────────────────┘  └─────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    磁盘持久化层                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ sessions.json (per-agent)                             │  │
│  │  - SessionEntry (deliveryContext, acp meta, tokens)   │  │
│  │  - atomic write + write-lock + TTL cache              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 会话存储并发控制 | 文件级写锁（`session-write-lock.ts`）+ 内存锁队列（`LOCK_QUEUES`） | 数据库事务 / 纯内存存储 | `store.ts:L554-727` 显式实现了基于 `fs.open(wx)` 的跨进程锁，并处理了 PID 回收、孤儿锁清理等边界；放弃数据库是为了零外部依赖，放弃纯内存是为了进程重启不丢数据 |
| ACP 运行时缓存策略 | 进程内 Map 缓存 + 空闲 TTL 驱逐 | 每次操作重新创建运行时连接 | `manager.core.ts:L1097-1139` 的 `evictIdleRuntimeHandles` 在 `runTurn` 前主动驱逐，避免连接泄漏；缓存命中时直接复用句柄，减少后端初始化开销 |
| Gateway 聊天状态 | 纯内存 Map（无持久化） | 将聊天缓冲写入磁盘 | `server-chat.ts:L209-232` 的 `createChatRunState` 完全基于内存 Map；聊天缓冲是临时流式数据，丢失后可由客户端重连恢复，无需持久化 |
| 会话存储维护模式 | 双模式（"warn" / 默认执行） | 统一自动清理 | `store-maintenance.ts:L15-16` 默认模式为 `"warn"`，`store.ts:L350-454` 在 `shouldWarnOnly` 时只记录日志不删除，避免误删活跃会话 |

### 3.3 数据流/控制流

```
[用户消息] → Gateway WS Handler
                │
                ▼
        ┌───────────────┐
        │ chatRunState  │ ──注册 runId → buffers[clientRunId] = ""
        │ (内存注册)     │
        └───────────────┘
                │
                ▼
        [Agent 执行] → AgentEventPayload 流
                │
                ▼
        ┌───────────────┐
        │ createAgentEventHandler │
        │  - emitChatDelta (150ms 节流)  │
        │  - flushBufferedChatDeltaIfNeeded │
        │  - emitChatFinal (生命周期结束)   │
        └───────────────┘
                │
                ▼
        [ACP 需要状态] → AcpSessionManager
                │
                ▼
        ┌─────────────────────────────┐
        │ resolveSession → ensureRuntimeHandle │
        │  - runtimeCache.get (命中则复用)      │
        │  - runtime.ensureSession (未命中新建) │
        │  - reconcileRuntimeSessionIdentifiers │
        └─────────────────────────────┘
                │
                ▼
        [元数据变更] → updateSessionStore
                │
                ▼
        ┌─────────────────────────────┐
        │ withSessionStoreLock        │
        │  - loadSessionStore (磁盘/缓存) │
        │  - mutator 回调修改              │
        │  - saveSessionStoreUnlocked      │
        │    (prune → cap → rotate → atomic write)
        └─────────────────────────────┘
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：会话存储的并发安全写锁

**作用**：保证多进程/多线程环境下对 `sessions.json` 的互斥写操作。

**设计意图**：不使用外部数据库，而是用文件系统锁实现跨进程互斥。代码中处理了 PID 回收、进程崩溃后的孤儿锁、Windows 非原子 rename 等边界情况。

**关键源码**（`src/agents/session-write-lock.ts:444-553`）：
```typescript
export async function acquireSessionWriteLock(params: {
  sessionFile: string;
  timeoutMs?: number;
  staleMs?: number;
  maxHoldMs?: number;
  allowReentrant?: boolean;
}): Promise<{ release: () => Promise<void> }> {
  // ...
  const allowReentrant = params.allowReentrant ?? true;
  const held = HELD_LOCKS.get(normalizedSessionFile);
  if (allowReentrant && held) {
    held.count += 1;
    return { release: async () => { await releaseHeldLock(normalizedSessionFile, held); } };
  }

  const startedAt = Date.now();
  let attempt = 0;
  while (Date.now() - startedAt < timeoutMs) {
    attempt += 1;
    let handle: fs.FileHandle | null = null;
    try {
      handle = await fs.open(lockPath, "wx");  // ① 独占创建锁文件
      const lockPayload: LockFilePayload = { pid: process.pid, createdAt: new Date().toISOString() };
      // ... 写入 PID + starttime 用于检测 PID 回收
      await handle.writeFile(JSON.stringify(lockPayload, null, 2), "utf8");
      // ... 注册到 HELD_LOCKS，返回 release 句柄
    } catch (err) {
      // ② 锁已存在：检查是否 stale（PID 死亡 / 超时 / PID 回收）
      const payload = await readLockPayload(lockPath);
      const inspected = inspectLockPayload(payload, staleMs, nowMs);
      if (await shouldReclaimContendedLockFile(lockPath, reclaimDetails, staleMs, nowMs)) {
        await fs.rm(lockPath, { force: true });
        continue;  // ③ 回收后重试
      }
      const delay = Math.min(1000, 50 * attempt);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
  throw new Error(`session file locked (timeout ${timeoutMs}ms): ${owner} ${lockPath}`);
}
```

这段代码值得看的原因是：它用 `fs.open(wx)` 实现了一个**跨进程可感知的互斥锁**，并且通过记录 `starttime` 解决了 Linux 上 PID 回收导致的误判问题（`L308-315`）。这比简单的文件存在性检查健壮得多。

---

### 机制 B：会话存储的 TTL 内存缓存

**作用**：减少高频读取 `sessions.json` 的磁盘 I/O，同时通过 mtime/size 校验避免缓存脏读。

**设计意图**：在单进程内，同一会话可能被多次读取（如 Gateway 健康检查、心跳、消息路由）。缓存 45s 可以显著降低 I/O，但用 `mtimeMs` 和 `sizeBytes` 做失效校验，确保外部修改能被感知。

**关键源码**（`src/config/sessions/store-cache.ts:41-61`）：
```typescript
export function readSessionStoreCache(params: {
  storePath: string;
  ttlMs: number;
  mtimeMs?: number;
  sizeBytes?: number;
}): Record<string, SessionEntry> | null {
  const cached = SESSION_STORE_CACHE.get(params.storePath);
  if (!cached) {
    return null;
  }
  const now = Date.now();
  if (now - cached.loadedAt > params.ttlMs) {
    invalidateSessionStoreCache(params.storePath);
    return null;
  }
  // ① 用 mtime + size 检测外部修改，比文件内容哈希更轻量
  if (params.mtimeMs !== cached.mtimeMs || params.sizeBytes !== cached.sizeBytes) {
    invalidateSessionStoreCache(params.storePath);
    return null;
  }
  return structuredClone(cached.store);  // ② 返回深拷贝，防止外部修改污染缓存
}
```

放弃内容哈希而采用 `mtime+size` 组合校验，是因为在大量会话条目场景下，哈希计算成本不可接受。`structuredClone` 的深拷贝则防止了调用方修改缓存对象导致的隐式污染。

---

### 机制 C：ACP 运行时缓存与空闲驱逐

**作用**：在进程内缓存 ACP 后端运行时句柄，避免每次 turn 都重新初始化；同时通过空闲 TTL 防止句柄泄漏。

**设计意图**：ACP 后端（如 Claude Code 实例）初始化成本高，缓存可以显著降低延迟。但句柄占用系统资源，需要自动回收。

**关键源码**（`src/acp/control-plane/manager.core.ts:L893-1012`）：
```typescript
private async ensureRuntimeHandle(params: {
  cfg: OpenClawConfig;
  sessionKey: string;
  meta: SessionAcpMeta;
}): Promise<{ runtime: AcpRuntime; handle: AcpRuntimeHandle; meta: SessionAcpMeta }> {
  // ① 尝试从缓存命中
  const cached = this.getCachedRuntimeState(params.sessionKey);
  if (cached) {
    const backendMatches = !configuredBackend || cached.backend === configuredBackend;
    const agentMatches = cached.agent === agent;
    const modeMatches = cached.mode === mode;
    const cwdMatches = (cached.cwd ?? "") === (cwd ?? "");
    if (backendMatches && agentMatches && modeMatches && cwdMatches) {
      return { runtime: cached.runtime, handle: cached.handle, meta: params.meta };
    }
    this.clearCachedRuntimeState(params.sessionKey);  // ② 配置变化时失效缓存
  }

  this.enforceConcurrentSessionLimit({ cfg: params.cfg, sessionKey: params.sessionKey });

  // ③ 缓存未命中：重新 ensureSession
  const ensured = await runtime.ensureSession({ sessionKey, agent, mode, cwd });
  // ... 构建 nextIdentity，持久化到 sessions.json
  this.setCachedRuntimeState(params.sessionKey, {
    runtime, handle: nextHandle, backend, agent, mode, cwd,
    appliedControlSignature: undefined,
  });
  return { runtime, handle: nextHandle, meta: nextMeta };
}
```

这里的关键设计是**四维缓存键校验**（backend + agent + mode + cwd）。任何一个维度变化都会使缓存失效，这保证了运行时句柄始终与持久化元数据一致。`appliedControlSignature` 则用于避免重复应用运行时配置选项。

---

### 机制 D：ACP 运行时缓存的空闲驱逐

**作用**：当运行时句柄长时间未被使用时，主动关闭后端连接，释放资源。

**设计意图**：防止进程长期持有大量空闲句柄，导致后端资源耗尽或达到 `maxConcurrentSessions` 上限。

**关键源码**（`src/acp/control-plane/manager.core.ts:L1097-1139`）：
```typescript
private async evictIdleRuntimeHandles(params: { cfg: OpenClawConfig }): Promise<void> {
  const idleTtlMs = resolveRuntimeIdleTtlMs(params.cfg);
  if (idleTtlMs <= 0 || this.runtimeCache.size() === 0) {
    return;
  }
  const now = Date.now();
  const candidates = this.runtimeCache.collectIdleCandidates({ maxIdleMs: idleTtlMs, now });
  // ...
  for (const candidate of candidates) {
    await this.actorQueue.run(candidate.actorKey, async () => {
      if (this.activeTurnBySession.has(candidate.actorKey)) {
        return;  // ① 正在执行的会话不驱逐
      }
      const lastTouchedAt = this.runtimeCache.getLastTouchedAt(candidate.actorKey);
      if (lastTouchedAt == null || now - lastTouchedAt < idleTtlMs) {
        return;  // ② 双重检查：加入队列后可能已被 touch
      }
      this.runtimeCache.clear(candidate.actorKey);
      this.evictedRuntimeCount += 1;
      try {
        await cached.runtime.close({ handle: cached.handle, reason: "idle-evicted" });
      } catch (error) {
        logVerbose(`acp-manager: idle eviction close failed...`);
      }
    });
  }
}
```

双重检查（`collectIdleCandidates` 后再次验证 `lastTouchedAt`）是必要的，因为从收集候选到实际执行之间，该会话可能又收到了新请求。`actorQueue` 保证了同一会话的驱逐和操作不会并发执行。

---

### 机制 E：Gateway 聊天运行的增量广播节流

**作用**：在流式 LLM 响应场景下，控制向客户端广播 assistant 增量文本的频率，避免消息风暴。

**设计意图**：LLM 生成 token 的速度可能远高于 WebSocket 客户端的渲染能力，150ms 的节流在用户体验和网络负载之间取得平衡。

**关键源码**（`src/gateway/server-chat.ts:341-391`）：
```typescript
const emitChatDelta = (
  sessionKey: string,
  clientRunId: string,
  sourceRunId: string,
  seq: number,
  text: string,
  delta?: unknown,
) => {
  const previousText = chatRunState.buffers.get(clientRunId) ?? "";
  const mergedText = resolveMergedAssistantText({ previousText, nextText: cleanedText, nextDelta: cleanedDelta });
  if (!mergedText) {
    return;
  }
  chatRunState.buffers.set(clientRunId, mergedText);
  // ① 静默回复 / 心跳 ACK 直接过滤
  if (isSilentReplyText(mergedText, SILENT_REPLY_TOKEN)) return;
  if (shouldHideHeartbeatChatOutput(clientRunId, sourceRunId)) return;

  // ② 150ms 节流
  const now = Date.now();
  const last = chatRunState.deltaSentAt.get(clientRunId) ?? 0;
  if (now - last < 150) {
    return;
  }
  chatRunState.deltaSentAt.set(clientRunId, now);
  chatRunState.deltaLastBroadcastLen.set(clientRunId, mergedText.length);

  broadcast("chat", payload, { dropIfSlow: true });
  nodeSendToSession(sessionKey, "chat", payload);
};
```

`resolveMergedAssistantText` 处理了 LLM 输出中常见的**前缀重叠**问题（新 text 是旧 text 的超集时去重），这比简单追加 delta 更健壮。`dropIfSlow: true` 则允许在客户端缓冲区满时丢弃非关键更新。

---

### 机制 F：Run 状态机（Channel Worker 层）

**作用**：为 Discord/Telegram 等 channel worker 提供运行级别的忙闲状态跟踪和心跳。

**设计意图**：外部监控系统需要知道当前是否有正在处理的请求，以便做负载均衡或健康判断。心跳机制防止了"运行中但卡死"的状态误判。

**关键源码**（`src/channels/run-state-machine.ts:18-99`）：
```typescript
export function createRunStateMachine(params: RunStateMachineParams) {
  const heartbeatMs = params.heartbeatMs ?? DEFAULT_RUN_ACTIVITY_HEARTBEAT_MS;
  let activeRuns = 0;
  let runActivityHeartbeat: ReturnType<typeof setInterval> | null = null;
  let lifecycleActive = !params.abortSignal?.aborted;

  const publish = () => {
    if (!lifecycleActive) return;
    params.setStatus?.({ activeRuns, busy: activeRuns > 0, lastRunActivityAt: now() });
  };

  const ensureHeartbeat = () => {
    if (runActivityHeartbeat || activeRuns <= 0 || !lifecycleActive) return;
    runActivityHeartbeat = setInterval(() => {
      if (!lifecycleActive || activeRuns <= 0) {
        clearHeartbeat();
        return;
      }
      publish();  // ① 运行期间每 60s 心跳一次
    }, heartbeatMs);
    runActivityHeartbeat.unref?.();
  };

  return {
    isActive() { return lifecycleActive; },
    onRunStart() { activeRuns += 1; publish(); ensureHeartbeat(); },
    onRunEnd() {
      activeRuns = Math.max(0, activeRuns - 1);
      if (activeRuns <= 0) { clearHeartbeat(); }
      publish();
    },
    deactivate,
  };
}
```

`unref()` 的调用是关键细节：它防止了心跳定时器阻止 Node.js 进程正常退出。`AbortSignal` 的集成则允许上层在关闭 worker 时优雅地停止状态发布。

---

### 机制 G：会话存储的自动维护（修剪/上限/轮转）

**作用**：防止 `sessions.json` 无限增长，通过自动清理旧条目、限制总条目数和文件轮转控制磁盘占用。

**设计意图**：Agent 长期运行会产生大量历史会话，如果不做维护，单文件可能达到数百 MB，导致加载和序列化性能急剧下降。

**关键源码**（`src/config/sessions/store.ts:346-454`）：
```typescript
if (!opts?.skipMaintenance) {
  const maintenance = { ...resolveMaintenanceConfig(), ...opts?.maintenanceOverride };
  const shouldWarnOnly = maintenance.mode === "warn";

  if (shouldWarnOnly) {
    // ① warn 模式：只检查活跃会话是否会被误删，不执行清理
    const warning = getActiveSessionMaintenanceWarning({ store, activeSessionKey, ... });
    if (warning) { log.warn("session maintenance would evict active session; skipping enforcement"); }
  } else {
    // ② 执行清理：先 prune 旧条目，再 cap 总数
    const pruned = pruneStaleEntries(store, maintenance.pruneAfterMs, { onPruned });
    const capped = capEntryCount(store, maintenance.maxEntries, { onCapped });
    // ③ 归档被删除会话的 transcript，然后轮转文件
    await rotateSessionFile(storePath, maintenance.rotateBytes);
    // ④ 磁盘预算检查（高水位线清理）
    const diskBudget = await enforceSessionDiskBudget({ store, storePath, ... });
  }
}
```

`warn` 模式的默认选择（`store-maintenance.ts:L15`）体现了防御性设计：在不确定配置是否正确时，宁可只报警不删除，避免用户数据意外丢失。归档机制（`archiveRemovedSessionTranscripts`）则保证了删除的会话 transcript 在 `pruneAfterMs` 内仍可恢复。

---

## 5. 与其他维度的交互

```
[状态管理] --(会话元数据)--> [路由系统]
[状态管理] --(ACP runtime handle)--> [ACP 后端]
[状态管理] --(chat delta / final)--> [Gateway WS 广播]
[状态管理] --(session store)--> [记忆系统 / Transcript]
[状态管理] <--(AgentEventPayload)-- [Agent 执行]
[状态管理] <--(心跳/健康检查)-- [运维监控]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | Gateway 广播 | 聊天增量/最终消息、agent 事件流 | `createAgentEventHandler` → `broadcast("chat")` / `broadcast("agent")` |
| 输出到 | ACP 后端 | 运行时句柄（ensureSession / runTurn / close） | `AcpSessionManager.ensureRuntimeHandle` → `runtime.ensureSession` |
| 输出到 | 路由系统 | 会话 deliveryContext（channel、to、threadId） | `updateLastRoute` 更新 `SessionEntry.deliveryContext` |
| 依赖 | Agent 执行 | AgentEventPayload 流驱动聊天状态更新 | `onAgentEvent` 订阅 → `createAgentEventHandler` |
| 依赖 | 配置系统 | session.maintenance 配置决定清理策略 | `resolveMaintenanceConfig()` 读取 `loadConfig().session?.maintenance` |
| 依赖 | 记忆系统 | sessions.json 存储会话元数据，transcript 存储消息历史 | `loadSessionStore` / `saveSessionStore` 操作磁盘文件 |
| 依赖 | 运维监控 | RunStateMachine 发布 busy/activeRuns 状态 | `createRunStateMachine({ setStatus })` → Discord monitor status sink |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **磁盘 I/O 是主要瓶颈**：TTL 缓存、批量维护、原子写入都是为了减少磁盘操作。作者假设在典型使用场景下，会话读取频率远高于写入频率。
2. **ACP 后端初始化成本高**：`RuntimeCache` 的存在假设了 `ensureSession` 比一次网络往返更慢，值得用内存缓存换取性能。
3. **单进程是主要部署形态**：虽然写锁支持跨进程，但 TTL 缓存和 `RuntimeCache` 都是进程内 Map，多进程部署时会有缓存不一致问题。作者似乎假设大多数用户运行单 Gateway 进程。
4. **用户更在乎数据安全而非磁盘空间**：默认 `warn` 模式、归档机制、5 次 Windows 重试都体现了"宁可多用磁盘，不可丢数据"的偏好。

### 6.2 这个设计的代价/风险

1. **进程内缓存与多进程不兼容**：`SESSION_STORE_CACHE` 和 `RuntimeCache` 都是 `Map`，如果用户启动多个 Gateway 进程指向同一个 `sessions.json`，一个进程的缓存不会感知另一个进程的写入。代码中 `readSessionStoreCache` 用 `mtime+size` 做了部分防御，但 `RuntimeCache` 完全没有跨进程协调。

2. **ACP 运行时句柄的并发限制是进程级**：`enforceConcurrentSessionLimit` 检查的是 `this.runtimeCache.size()`（`manager.core.ts:L1071`），这在多进程部署下会失效——每个进程独立计数，总和可能超过配置上限。

3. **聊天状态无持久化，重启即丢失**：`chatRunState` 完全在内存中，Gateway 重启后所有进行中的聊天运行状态丢失，客户端会收到断连而非明确的错误状态。

4. **会话存储的锁队列可能堆积**：`LOCK_QUEUES` 是内存中的 FIFO 队列（`store.ts:L549-554`），如果某个持有锁的进程崩溃且锁文件未被清理，后续请求会阻塞直到 `timeoutMs`（默认 10s）。虽然 `staleMs`（默认 30min）和 PID 检测可以 eventually 回收，但期间队列中的请求会累积。

### 6.3 如果要重新设计，可能会改变什么

1. **引入可选的 SQLite 后端**：当前 JSON 文件存储在条目数超过 500、文件大小超过 10MB 后，序列化/反序列化开销显著。SQLite 可以提供增量更新、索引查询和真正的 ACID，代价是引入原生依赖。

2. **将 `RuntimeCache` 的并发限制改为后端感知**：与其在进程内计数，不如让 ACP 后端自己报告当前活跃会话数，或者引入一个轻量级的分布式计数器（如基于锁文件的计数）。

3. **聊天状态增加 graceful degradation**：在 Gateway 重启时，可以从 `sessions.json` 中读取 `state: "running"` 的 ACP 会话，向关联的 WebSocket 客户端发送 `error` 或 `aborted` 事件，而不是让客户端超时。

4. **统一状态管理层**：当前状态分散在 `src/config/sessions/`（磁盘）、`src/acp/control-plane/`（ACP 运行时）、`src/gateway/`（Gateway 运行时）三个目录，缺乏一个统一的状态管理抽象。可以考虑引入一个分层的 `StateManager` 接口，让各层实现不同的持久化策略。

### 6.4 对我自己设计 Agent 系统的启示

最核心的启示是：**Agent 系统的状态管理必须分层设计，且每一层的持久化策略应该与该层的数据生命周期匹配**。OpenClaw 的实践证明：磁盘持久化适合会话元数据（低频写、需恢复），内存缓存适合运行时句柄（高频读、可重建），纯内存 Map 适合临时流式状态（低价值、可丢失）。不要试图用同一种存储方案解决所有问题。
