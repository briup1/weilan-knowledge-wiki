# 维度名：编排循环（Orchestration Loop）

## 1. 一句话定位

编排循环是 OpenClaw 将外部事件（用户消息、心跳、cron、子代理完成）转化为有序、可恢复、可降级的 LLM Agent 执行序列的核心调度机制，负责在并发控制、故障恢复、资源约束之间维持系统稳态。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **没有 Agent 执行循环**：`runEmbeddedAttempt` 中 LLM 调用是单次请求，但 tool-use 循环需要多轮对话。如果没有外层 `runEmbeddedPiAgent` 的 `while(true)` 重试循环，任何一次 provider 超时、rate limit 或 context overflow 都会直接终止整个用户会话，导致用户消息丢失且无法自动恢复。
- **没有命令队列 lane 机制**：`command-queue.ts` 的 `drainLane` 若不存在，并发用户消息会直接竞争 session write lock，导致 "session file locked" 错误大量抛出；cron 任务和主会话也会相互穿插 stdout，造成输出混乱。
- **没有 Gateway 主循环**：`runGatewayLoop` 的 `while(true)` 若不存在，SIGUSR1 重启会杀死进程并丢失 macOS TCC 权限（#35862），且 in-flight 的 agent turn 会被静默丢弃。
- **没有模型降级循环**：`model-fallback.ts` 若不存在，当主模型因 rate limit / billing / overloaded 失败时，用户会立即收到硬错误，系统丧失弹性。
- **没有子代理交付循环**：`subagent-announce.ts` 若不存在，子代理完成后结果无法回传父会话，spawn 操作变成" fire-and-forget "黑洞。
- **没有 cron 调度循环**：`timer.ts` 的 `onTimer` 若不存在，cron job 在进程重启后会丢失 missed runs，且长任务会阻塞整个调度器（#12025）。
- **没有心跳调度**：`heartbeat-runner.ts` 若不存在，agent 失去周期性自主检查能力，HEARTBEAT.md 的监控逻辑完全失效。
- **没有草稿流循环**：`draft-stream-loop.ts` 若不存在，流式输出会在高频 token 到达时触发大量网络请求，导致消息平台 rate limit。

### 2.2 OpenClaw 的具体触发条件

| 触发条件 | 代码位置 |
|---------|---------|
| 用户发送消息触发 Agent turn | `runEmbeddedPiAgent` 被 `enqueueCommandInLane` 调用（`run.ts:274`） |
| 心跳定时器到期 | `startHeartbeatRunner` 中 `setTimeout` 触发 `requestHeartbeatNow`（`heartbeat-runner.ts:1064`） |
| Cron job 到达 `nextRunAtMs` | `armTimer` 计算 `nextWakeAtMs` 后触发 `onTimer`（`timer.ts:550`） |
| 子代理完成需要回传结果 | `runSubagentAnnounceFlow` 在子代理 run 结束后被调用（`subagent-announce.ts:1136`） |
| Gateway 收到 SIGUSR1/SIGTERM | `runGatewayLoop` 注册信号处理器（`run-loop.ts:199-201`） |
| LLM 返回错误需要模型降级 | `runWithModelFallback` 在 `promptError` 或 `assistantError` 时触发（`model-fallback.ts:502`） |
| 流式回复需要节流发送 | `createDraftStreamLoop` 在 `onPartialReply` 时被调用（`draft-stream-loop.ts:10`） |

---

## 3. 核心设计思路

### 3.1 抽象模型

OpenClaw 的编排循环是一个**分层状态机 + 管道**的混合模型：

```
[事件源] → [队列/Lane] → [外层重试循环] → [单次 Attempt] → [流式输出管道]
                ↓              ↓                    ↓
            [Gateway]    [模型降级]          [Compaction]
                ↓              ↓                    ↓
         [生命周期管理]  [Auth Profile 轮换]   [Context Engine]
```

各层职责：
- **Gateway 层**：进程级生命周期（启动、drain、重启、退出）
- **Lane 层**：会话级并发控制（serialize per-session, parallel per-lane）
- **Run 层**：Turn 级重试与降级（profile 轮换 → model fallback → thinking fallback）
- **Attempt 层**：单次 LLM 调用（prompt → stream → tool loop → compaction）
- **Stream 层**：输出节流与交付（draft stream → block reply pipeline）

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **双层队列（Global + Session Lane）** | `enqueueSession(() => enqueueGlobal(async () => { ... }))`（`run.ts:274-275`） | 单层全局队列 | 外层 session lane 保证同一会话串行，内层 global lane 控制全局并发；若只有单层，要么牺牲同会话顺序性，要么牺牲全局吞吐量 |
| **In-process 重启而非进程退出** | `while(true)` + `restartResolver` 协调（`run-loop.ts:218-246`） | `process.exit` + 外部 supervisor 重启 | 代码注释 #35862 明确指出：macOS TCC 权限在进程重启后丢失，in-process 重启保留权限 |
| **Compaction 超时快照回退** | `selectCompactionTimeoutSnapshot` 在 `timedOutDuringCompaction` 时回退到 `preCompactionSnapshot`（`compaction-timeout.ts:30-54`） | 直接使用当前（可能损坏的）session 状态 | `attempt.ts:1866-1883` 显示 compaction 期间 session 结构可能不一致，回退避免将损坏状态带入下一轮 |
| **模型降级与 Auth Profile 轮换分离** | `run.ts` 内层处理 profile 轮换，`model-fallback.ts` 外层处理跨模型降级 | 合并为统一重试层 | 代码中 profile 轮换基于 `authStore` cooldown 状态（`run.ts:633-658`），而 model fallback 基于配置链（`model-fallback.ts:252-327`）；合并会导致 cooldown 状态污染模型选择逻辑 |
| **Cron 调度器自包含 timer 循环** | `armTimer` + `onTimer` + `armRunningRecheckTimer` 三级定时器（`timer.ts:507-590`） | 依赖外部调度框架 | 代码注释 #12025 指出：长任务会阻塞 `onTimer`，必须用 `armRunningRecheckTimer` 保持调度器心跳，否则调度器静默死亡 |

### 3.3 数据流/控制流

```
用户消息 / 心跳 / Cron / 子代理完成
    ↓
[enqueueCommandInLane] —— 按 sessionKey 路由到对应 lane
    ↓
[runEmbeddedPiAgent] —— 外层 while(true) 重试循环
    ├── 模型解析（hook 覆盖 → resolveModel）
    ├── Auth Profile 选择（cooldown 检测 → applyApiKeyInfo）
    └── while(true) {  // 内层重试
            runEmbeddedAttempt()  // 单次 LLM turn
            ├── 错误分类（context overflow / prompt error / assistant error）
            ├── 恢复策略（compaction / tool result truncation / profile rotation）
            └── 成功 → break
        }
    ↓
[runEmbeddedAttempt] —— 单次 attempt
    ├── session 加载 + sanitize history
    ├── context engine assemble
    ├── prompt(effectivePrompt)  // LLM 调用
    ├── waitForCompactionRetry   // compaction 等待
    ├── snapshot selection       // 超时回退
    └── payload build + return
    ↓
[流式输出] —— draft-stream-loop / block-reply-pipeline
    ↓
[交付] —— 按 channel 发送给用户
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：双层 Lane 队列（并发控制）

**作用**：将并发请求按 session 序列化，同时允许不同 lane（main/cron/subagent）并行。

**设计意图**：为什么不用简单的 `Promise.all` 或单队列？因为同一会话的多个消息必须按顺序处理（否则 session file 会竞争写锁），但 cron 和 subagent 不应阻塞主消息流。

**关键源码**（`src/process/command-queue.ts:34-78,161-187`）：

```typescript
// ① lane 是动态创建的，每个 session 一个 lane，默认 "main"
const lanes = new Map<string, LaneState>();

// ② generation 机制：SIGUSR1 重启后旧任务的 finally 可能不执行，
//    通过 generation 让旧任务的 completeTask 被忽略
function completeTask(state: LaneState, taskId: number, taskGeneration: number): boolean {
  if (taskGeneration !== state.generation) {
    return false;  // ← 旧生命周期的任务，直接丢弃
  }
  state.activeTaskIds.delete(taskId);
  return true;
}

// ③ drainLane 是同步启动的异步泵：while 循环一次性启动 maxConcurrent 个任务
const pump = () => {
  while (state.activeTaskIds.size < state.maxConcurrent && state.queue.length > 0) {
    const entry = state.queue.shift() as QueueEntry;
    // ... 启动任务，完成后递归调用 pump()
  }
};
```

**为什么这样实现**：`drainLane` 用同步 `while` 启动任务但内部是 `void (async () => { ... })()`，这样不会阻塞事件循环，同时保证 lane 内 maxConcurrent 个任务并行、其余排队。

---

### 机制 B：Agent Turn 外层重试循环（故障恢复）

**作用**：在单次 attempt 失败后，根据错误类型选择恢复策略（compaction、profile 轮换、model fallback、thinking fallback）。

**设计意图**：为什么不在 attempt 内部处理所有重试？因为不同恢复策略需要改变外部状态（如切换 API key、切换模型、截断 session），这些操作需要重新构建 attempt 的输入参数。

**关键源码**（`src/agents/pi-embedded-runner/run.ts:807-1285`）：

```typescript
// ① 硬上限：防止无限重试（基于 profile 数量动态计算）
const MAX_RUN_LOOP_ITERATIONS = resolveMaxRunRetryIterations(profileCandidates.length);
while (true) {
  if (runLoopIterations >= MAX_RUN_LOOP_ITERATIONS) {
    return { payloads: [{ text: "Request failed after repeated internal retries...", isError: true }], ... };
  }
  runLoopIterations += 1;

  // ② 单次 attempt
  const attempt = await runEmbeddedAttempt({ ... });

  // ③ Context Overflow 恢复链（优先级严格有序）
  if (contextOverflowError) {
    // 3a: 如果 attempt 内部已 compaction 过，直接重试
    if (!isCompactionFailure && hadAttemptLevelCompaction && overflowCompactionAttempts < MAX) {
      overflowCompactionAttempts++;
      continue;  // ← 不额外 compaction，直接重试
    }
    // 3b: 尝试显式 compaction
    if (!hadAttemptLevelCompaction && overflowCompactionAttempts < MAX) {
      const compactResult = await contextEngine.compact({ ... });
      if (compactResult.compacted) { continue; }
    }
    // 3c: 尝试截断 oversized tool results
    if (!toolResultTruncationAttempted) {
      const truncResult = await truncateOversizedToolResultsInSession({ ... });
      if (truncResult.truncated) { continue; }
    }
    // 3d: 放弃，返回用户友好错误
    return { payloads: [{ text: "Context overflow: prompt too large...", isError: true }], ... };
  }

  // ④ Prompt 错误：Copilot token 刷新 → profile 轮换 → thinking fallback → model fallback
  if (promptError && !aborted) {
    if (await maybeRefreshCopilotForAuthError(errorText, copilotAuthRetry)) { continue; }
    if (await advanceAuthProfile()) { continue; }  // ← 轮换到下一个 API key
    const fallbackThinking = pickFallbackThinkingLevel({ message: errorText, attempted: attemptedThinking });
    if (fallbackThinking) { thinkLevel = fallbackThinking; continue; }
    if (fallbackConfigured && promptFailoverFailure) {
      throw new FailoverError(errorText, { reason: promptFailoverReason, ... });  // ← 抛给外层 model-fallback
    }
    throw promptError;  // ← 不可恢复，直接抛出
  }

  // ⑤ Assistant 错误（LLM 返回 error stopReason）：类似处理链
  // ... authFailure / rateLimitFailure / billingFailure / failoverFailure
}
```

**为什么这样实现**：恢复策略按 "低成本 → 高成本" 排序：compaction（纯计算）> tool truncation（局部修改）> profile 轮换（切换 key）> thinking fallback（降低模型能力）> model fallback（切换模型）。这种排序最小化用户感知延迟和系统资源消耗。

---

### 机制 C：Compaction 超时快照回退

**作用**：当 attempt 在 compaction 阶段超时，避免使用可能结构不一致的 session 状态。

**设计意图**：为什么 compaction 期间的状态不一致？因为 pi-coding-agent 的 compaction 会重写 session transcript，可能将多轮对话合并为摘要，如果中断，session 可能处于 "摘要已写入但原始消息未完全删除" 的中间状态。

**关键源码**（`src/agents/pi-embedded-runner/run/attempt.ts:1797-1883` 及 `compaction-timeout.ts:30-54`）：

```typescript
// attempt.ts:1797-1801
// ① 在 compaction 等待前捕获快照
const wasCompactingBefore = activeSession.isCompacting;
const snapshot = activeSession.messages.slice();
const wasCompactingAfter = activeSession.isCompacting;
// 只有 compaction 前后都没在运行，才信任快照
const preCompactionSnapshot = wasCompactingBefore || wasCompactingAfter ? null : snapshot;

// attempt.ts:1814-1828
// ② 等待 compaction 完成，带 aggregate timeout
const compactionRetryWait = await waitForCompactionRetryWithAggregateTimeout({
  waitForCompactionRetry,
  abortable,
  aggregateTimeoutMs: COMPACTION_RETRY_AGGREGATE_TIMEOUT_MS,  // 60s
  isCompactionStillInFlight: isCompactionInFlight,
});
if (compactionRetryWait.timedOut) { timedOutDuringCompaction = true; }

// attempt.ts:1868-1883
// ③ 超时后选择快照
const snapshotSelection = selectCompactionTimeoutSnapshot({
  timedOutDuringCompaction,
  preCompactionSnapshot,
  preCompactionSessionId,
  currentSnapshot: activeSession.messages.slice(),
  currentSessionId: activeSession.sessionId,
});
messagesSnapshot = snapshotSelection.messagesSnapshot;
sessionIdUsed = snapshotSelection.sessionIdUsed;
```

**为什么这样实现**：`preCompactionSnapshot` 的捕获时机非常关键——放在 `waitForCompactionRetry` 之前，但检查 `isCompacting` 状态。如果 compaction 已经在运行，快照不可信（`null`），此时回退到当前状态是更安全的策略。

---

### 机制 D：Gateway 进程级生命周期循环

**作用**：处理 SIGTERM/SIGINT 优雅退出、SIGUSR1 热重启，保证 in-flight 工作 drain 完成。

**设计意图**：为什么 SIGUSR1 要做 in-process 重启而不是 spawn 新进程？因为 macOS TCC（隐私权限）绑定到 PID，进程重启后权限丢失。

**关键源码**（`src/cli/gateway-cli/run-loop.ts:98-176,218-246`）：

```typescript
const DRAIN_TIMEOUT_MS = 90_000;
const SHUTDOWN_TIMEOUT_MS = 5_000;

const request = (action: GatewayRunSignalAction, signal: string) => {
  shuttingDown = true;
  const isRestart = action === "restart";
  // ① restart 时给更多时间（drain + shutdown）
  const forceExitMs = isRestart ? DRAIN_TIMEOUT_MS + SHUTDOWN_TIMEOUT_MS : SHUTDOWN_TIMEOUT_MS;
  const forceExitTimer = setTimeout(() => {
    // restart 超时返回非零码，让 systemd/launchd 视为失败并做 clean restart
    exitProcess(isRestart ? 1 : 0);
  }, forceExitMs);

  void (async () => {
    if (isRestart) {
      // ② 拒绝新入队，让客户端收到明确错误而非静默丢失
      markGatewayDraining();
      // ③ 先 abort compacting runs（它们持有 session write lock）
      if (activeRuns > 0) { abortEmbeddedPiRun(undefined, { mode: "compacting" }); }
      // ④ 等待 tasks 和 runs drain
      const [tasksDrain, runsDrain] = await Promise.all([
        activeTasks > 0 ? waitForActiveTasks(DRAIN_TIMEOUT_MS) : Promise.resolve({ drained: true }),
        activeRuns > 0 ? waitForActiveEmbeddedRuns(DRAIN_TIMEOUT_MS) : Promise.resolve({ drained: true }),
      ]);
      if (!tasksDrain.drained || !runsDrain.drained) {
        abortEmbeddedPiRun(undefined, { mode: "all" });  // 最终强制 abort
      }
    }
    await server?.close({ reason: isRestart ? "gateway restarting" : "gateway stopping" });
    // ⑤ 释放 lock 后再 spawn，避免子进程抢锁失败
    if (isRestart) { await handleRestartAfterServerClose(); }
  })();
};

// ⑥ 主循环：SIGUSR1 只 resolve restartResolver，不退出进程
while (true) {
  onIteration();  // 重置 lane 状态（处理 SIGUSR1 后遗留的 active count）
  server = await params.start();
  await new Promise<void>((resolve) => { restartResolver = resolve; });
}
```

**为什么这样实现**：`releaseLockIfHeld` 在 `handleRestartAfterServerClose` 中先于 `restartGatewayProcessWithFreshPid()` 执行，这是为了避免父进程持有 lock 时子进程无法获取（#35862 的连锁修复）。

---

### 机制 E：模型降级循环（Model Fallback）

**作用**：当主模型完全不可用时，按配置链尝试备用模型，同时处理 auth profile cooldown 的探测逻辑。

**设计意图**：为什么 fallback 要独立于内层 run 循环？因为 fallback 需要重新选择模型、重新解析模型配置、重新初始化 streamFn，这些操作在 `runEmbeddedAttempt` 内部做会导致函数签名爆炸。

**关键源码**（`src/agents/model-fallback.ts:502-763`）：

```typescript
export async function runWithModelFallback<T>(params: { ... }): Promise<ModelFallbackRunResult<T>> {
  const candidates = resolveFallbackCandidates({ cfg, provider, model });
  const attempts: FallbackAttempt[] = [];

  for (let i = 0; i < candidates.length; i++) {
    const candidate = candidates[i];
    const isPrimary = i === 0;

    // ① Cooldown 探测：主模型在 cooldown 边缘时，允许一次探测性调用
    if (authStore && profileIds.length > 0 && !isAnyProfileAvailable) {
      const decision = resolveCooldownDecision({
        candidate, isPrimary, hasFallbackCandidates,
        now, probeThrottleKey, authStore, profileIds,
      });
      if (decision.type === "skip") {
        attempts.push({ provider: candidate.provider, model: candidate.model, error: decision.error, ... });
        continue;  // ← 跳过此候选
      }
      if (decision.markProbe) { markProbeAttempt(now, probeThrottleKey); }
      runOptions = { allowTransientCooldownProbe: true };
    }

    // ② 执行候选
    const attemptRun = await runFallbackAttempt({ run: params.run, ...candidate, attempts, options: runOptions });
    if ("success" in attemptRun) {
      // ③ 成功：如果有失败记录，打 warning log
      return attemptRun.success;
    }

    // ④ 失败：context overflow 不降级（备用模型可能窗口更小）
    const errMessage = err instanceof Error ? err.message : String(err);
    if (isLikelyContextOverflowError(errMessage)) { throw err; }

    // ⑤ 记录失败，继续下一个候选
    attempts.push({ provider: candidate.provider, model: candidate.model, error: described.message, reason: described.reason });
  }

  throwFallbackFailureSummary({ attempts, candidates, lastError, label: "models", ... });
}
```

**为什么这样实现**：`resolveCooldownDecision` 区分了 `rate_limit`/`overloaded`（可探测）和 `auth`/`billing`（半持久化）——前者允许在 cooldown 边缘探测一次，后者直接跳过。这避免了在 billing 欠费时浪费 fallback 尝试。

---

### 机制 F：Cron 调度循环

**作用**：维护一个自包含的定时器循环，执行 cron job，处理 missed runs、错误退避、并发控制。

**设计意图**：为什么不用 `node-cron` 等库？因为需要精细控制：startup catchup、错误退避、长任务不阻塞调度器、session reaper  piggyback。

**关键源码**（`src/cron/service/timer.ts:507-730`）：

```typescript
export function armTimer(state: CronServiceState) {
  const nextAt = nextWakeAtMs(state);
  const delay = Math.max(nextAt - now, 0);
  // ① 防热循环：delay=0 时强制最小间隔 2s（#17821）
  const flooredDelay = delay === 0 ? MIN_REFIRE_GAP_MS : delay;
  // ② 防漂移：最多 60s 必须唤醒一次
  const clampedDelay = Math.min(flooredDelay, MAX_TIMER_DELAY_MS);
  state.timer = setTimeout(() => { void onTimer(state); }, clampedDelay);
}

export async function onTimer(state: CronServiceState) {
  if (state.running) {
    // ③ 长任务期间保持调度器心跳（#12025）
    armRunningRecheckTimer(state);
    return;
  }
  state.running = true;
  armRunningRecheckTimer(state);  // watchdog

  try {
    const dueJobs = await locked(state, async () => {
      await ensureLoaded(state, { forceReload: true, skipRecompute: true });
      const due = collectRunnableJobs(state, dueCheckNow);
      if (due.length === 0) {
        // ④ maintenance recompute：避免 past-due 的 nextRunAtMs 被静默跳过（#13992）
        recomputeNextRunsForMaintenance(state, { recomputeExpired: true });
        return [];
      }
      // 标记 runningAtMs，持久化
      for (const job of due) { job.state.runningAtMs = now; }
      await persist(state);
      return due;
    });

    // ⑤ 并发 worker 池
    const concurrency = Math.min(resolveRunConcurrency(state), dueJobs.length);
    const workers = Array.from({ length: concurrency }, async () => {
      for (;;) {
        const index = cursor++;
        if (index >= dueJobs.length) return;
        results[index] = await runDueJob(dueJobs[index]);
      }
    });
    await Promise.all(workers);

    // ⑥ 应用结果 + 错误退避
    await locked(state, async () => {
      for (const result of completedResults) {
        applyOutcomeToStoredJob(state, result);  // 更新 nextRunAtMs、consecutiveErrors
      }
      recomputeNextRunsForMaintenance(state);
      await persist(state);
    });
  } finally {
    // ⑦ piggyback session reaper（自限流 5min）
    await sweepCronRunSessions({ ... });
    state.running = false;
    armTimer(state);
  }
}
```

**为什么这样实现**：`armRunningRecheckTimer` 是核心防御机制——当 `onTimer` 因长任务还在执行时，下一个 timer tick 到达后发现 `state.running === true`，如果没有这个重设 timer 的逻辑，调度器会静默死亡直到下次外部事件触发。

---

### 机制 G：子代理交付循环（Subagent Announce）

**作用**：子代理完成后，将结果以 "steer message" 或 "queued announce" 形式回传父会话，支持嵌套子代理和 wake-on-descendant。

**设计意图**：为什么需要 "steer" 和 "queue" 两种模式？因为父会话可能正在运行（steer 直接注入）或空闲（queue 等待下次运行时处理）。

**关键源码**（`src/agents/subagent-announce.ts:662-728,1136-1485`）：

```typescript
async function maybeQueueSubagentAnnounce(params: { ... }): Promise<"steered" | "queued" | "none"> {
  const queueSettings = resolveQueueSettings({ cfg, channel, sessionEntry: entry });
  const isActive = isEmbeddedPiRunActive(sessionId);

  // ① steer 模式：父会话正在运行，直接注入消息
  if (queueSettings.mode === "steer" || queueSettings.mode === "steer-backlog") {
    const steered = queueEmbeddedPiMessage(sessionId, params.steerMessage);
    if (steered) return "steered";
  }

  // ② queue 模式：父会话空闲，入队等待下次处理
  if (isActive && (shouldFollowup || queueSettings.mode === "steer")) {
    enqueueAnnounce({ key, item: { ... }, settings: queueSettings, send: sendAnnounce });
    return "queued";
  }
  return "none";
}

// ③ wake-on-descendant：子代理的子代理全部完成后，唤醒父代理继续
if (params.wakeOnDescendantSettle && childCompletionFindings?.trim() && !childRunAlreadyWoken) {
  const woke = await wakeSubagentRunAfterDescendants({
    runId: params.childRunId, childSessionKey: params.childSessionKey,
    findings: childCompletionFindings, announceId: wakeAnnounceId,
  });
  if (woke) { shouldDeleteChildSession = false; return true; }
}

// ④ 构建内部事件并交付
const internalEvents: AgentInternalEvent[] = [{
  type: "task_completion", source: "subagent",
  childSessionKey: params.childSessionKey, taskLabel, status: outcome.status,
  result: findings, statsLine, replyInstruction,
}];
const triggerMessage = buildAnnounceSteerMessage(internalEvents);
await deliverSubagentAnnouncement({ requesterSessionKey, triggerMessage, steerMessage: triggerMessage, ... });
```

**为什么这样实现**：`wakeOnDescendantSettle` 解决了嵌套子代理的"最后一公里"问题——父代理 spawn 子代理后可能处于等待状态，当子代理的子代理全部完成时，需要主动唤醒父代理（通过 `callGateway` 发送 steer message），而不是让父代理无限期 poll。

---

### 机制 H：心跳调度循环

**作用**：按配置间隔触发 agent 自主检查（HEARTBEAT.md），处理 exec/cron 事件，支持 quiet hours 和 dedupe。

**设计意图**：为什么心跳要检查 `getQueueSize(CommandLane.Main) > 0` 时 skip？因为心跳是低优先级后台任务，不应抢占用户消息的处理资源。

**关键源码**（`src/infra/heartbeat-runner.ts:1010-1246`）：

```typescript
export function startHeartbeatRunner(opts: { ... }): HeartbeatRunner {
  const state = { cfg, agents: new Map<string, HeartbeatAgentState>(), timer: null, stopped: false };

  const scheduleNext = () => {
    let nextDue = Number.POSITIVE_INFINITY;
    for (const agent of state.agents.values()) {
      if (agent.nextDueMs < nextDue) nextDue = agent.nextDueMs;
    }
    const delay = Math.max(0, nextDue - now);
    state.timer = setTimeout(() => { requestHeartbeatNow({ reason: "interval", coalesceMs: 0 }); }, delay);
    state.timer.unref?.();  // 不阻止进程退出
  };

  const run: HeartbeatWakeHandler = async (params) => {
    for (const agent of state.agents.values()) {
      if (isInterval && now < agent.nextDueMs) continue;
      const res = await runOnce({ cfg: state.cfg, agentId: agent.agentId, heartbeat: agent.heartbeat, reason });
      if (res.status === "skipped" && res.reason === "requests-in-flight") {
        // 不 advance schedule，让 wake 层 1s 后重试
        return res;
      }
      if (res.status !== "skipped" || res.reason !== "disabled") {
        advanceAgentSchedule(agent, now);  // 只有实际跑了才推进时间表
      }
    }
    scheduleNext();
  };
}
```

**为什么这样实现**：`requests-in-flight` 时不推进 `nextDueMs` 是关键设计——如果推进了，下次心跳会被推迟一个完整间隔（可能几分钟），导致用户消息和心跳之间的竞争使心跳永远被饿死。

---

### 机制 I：草稿流循环（Draft Stream Loop）

**作用**：对流式 LLM 输出做节流，避免高频 token 导致消息平台 rate limit。

**设计意图**：为什么不用简单的 `throttle` 函数？因为需要处理 "flush"（用户等待最终输出）和 "in-flight"（前一个网络请求未完成时不能发下一个）。

**关键源码**（`src/channels/draft-stream-loop.ts:10-104`）：

```typescript
export function createDraftStreamLoop(params: { throttleMs, isStopped, sendOrEditStreamMessage }): DraftStreamLoop {
  let lastSentAt = 0;
  let pendingText = "";
  let inFlightPromise: Promise<void | boolean> | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;

  const flush = async () => {
    while (!params.isStopped()) {
      if (inFlightPromise) { await inFlightPromise; continue; }  // ① 等待前一个请求完成
      const text = pendingText;
      if (!text.trim()) { pendingText = ""; return; }
      pendingText = "";
      const current = params.sendOrEditStreamMessage(text).finally(() => {
        if (inFlightPromise === current) inFlightPromise = undefined;
      });
      inFlightPromise = current;
      const sent = await current;
      if (sent === false) { pendingText = text; return; }  // ② 发送失败，保留 pending
      lastSentAt = Date.now();
      if (!pendingText) return;  // ③ 没有新内容，结束
    }
  };

  return {
    update: (text: string) => {
      if (params.isStopped()) return;
      pendingText = text;
      if (inFlightPromise) { schedule(); return; }  // ④ 有 in-flight，只更新 pending 并 schedule
      if (!timer && Date.now() - lastSentAt >= params.throttleMs) {
        void flush();  // ⑤ 超过 throttle 窗口，立即 flush
        return;
      }
      schedule();  // ⑥ 否则 schedule 延迟 flush
    },
    // ...
  };
}
```

**为什么这样实现**：`inFlightPromise` 的存在保证了消息顺序——如果前一个 `sendOrEditStreamMessage` 还没完成，新的 update 只会更新 `pendingText` 并等待，不会并发发送导致消息乱序。

---

## 5. 与其他维度的交互

```
[编排循环] --(输出什么)--> [目标维度]
[编排循环] <--(依赖什么)-- [来源维度]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | **工具系统** | 本轮需要暴露给 LLM 的工具列表 | `createOpenClawCodingTools()` → `tools` → `createAgentSession({ tools, customTools })`（`attempt.ts:846-893`） |
| 输出到 | **记忆系统** | 历史消息作为上下文输入 | `sessionManager.buildSessionContext()` → `activeSession.agent.replaceMessages()`（`attempt.ts:1087-1113`） |
| 输出到 | **上下文引擎** | token budget、session 状态，接收 compaction 结果 | `contextEngine.assemble()` / `contextEngine.compact()` / `contextEngine.afterTurn()`（`attempt.ts:1422-1447, 1901-1948`） |
| 输出到 | **交付系统** | 构建好的 ReplyPayload 数组 | `buildEmbeddedRunPayloads()` → `payloads`（`run.ts:1446-1462`） |
| 输出到 | **子代理系统** | 子代理完成后通过 steer/queue 回传 | `maybeQueueSubagentAnnounce()` / `deliverSubagentAnnouncement()`（`subagent-announce.ts`） |
| 依赖 | **配置系统** | 模型选择、timeout、lane 配置 | `resolveModel()` / `resolveContextWindowInfo()`（`run.ts:363-408`） |
| 依赖 | **认证系统** | API key、auth profile cooldown 状态 | `ensureAuthProfileStore()` / `getApiKeyForModel()` / `isProfileInCooldown()`（`run.ts:410-436`） |
| 依赖 | **插件系统** | before_prompt_build、before_agent_start、agent_end hooks | `getGlobalHookRunner()` → `runBeforePromptBuild()` / `runAgentEnd()`（`attempt.ts:1644-1684, 1964-1984`） |
| 依赖 | **会话存储** | session file、transcript、store | `SessionManager.open()` / `sessionManager.appendCustomEntry()`（`attempt.ts:1087, 1887`） |
| 依赖 | **进程队列** | lane 调度、drain 控制 | `enqueueCommandInLane()` / `markGatewayDraining()`（`run.ts:274` / `command-queue.ts:150`） |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"LLM 调用是不可靠的，但故障是可分类的"**：代码中花了大量篇幅对错误分类（`classifyFailoverReason`、`isLikelyContextOverflowError`、`isRateLimitAssistantError` 等），假设不同错误类型需要不同恢复策略。
2. **"Compaction 是昂贵的，但 context overflow 是致命的"**：`MAX_OVERFLOW_COMPACTION_ATTEMPTS = 3` 和 `COMPACTION_RETRY_AGGREGATE_TIMEOUT_MS = 60_000` 体现了对 compaction 成本的认知——愿意花 60 秒等待，但最多试 3 次。
3. **"macOS TCC 权限比进程干净性更重要"**：`runGatewayLoop` 的 in-process 重启逻辑（`#35862`）假设保留权限的优先级高于消除内存泄漏风险。
4. **"子代理是嵌套的，但交付是线性的"**：`subagent-announce.ts` 的 `wakeOnDescendantSettle` 假设嵌套子代理最终会收敛到线性交付链。

### 6.2 这个设计的代价/风险

1. **状态碎片化**：`run.ts` 中 `overflowCompactionAttempts`、`toolResultTruncationAttempted`、`didTransientCooldownProbe`、`authRetryPending` 等状态变量散落在函数各处，增加了理解成本。任何新增恢复策略都需要修改这个已经很长的 `while(true)` 块。
2. **Lane generation 的隐式契约**：`command-queue.ts` 的 `generation` 机制假设 "SIGUSR1 后旧任务的 finally 不执行"，但这个假设在 JavaScript 中并不绝对（如果任务在 `await` 前已完成同步部分，finally 可能已执行）。代码中通过 `completeTask` 的 generation 检查来防御，但这是一种 "事后补救" 而非 "事前预防"。
3. **Draft stream 的 `pendingText` 覆盖**：`draft-stream-loop.ts` 的 `update` 直接赋值 `pendingText = text`，这意味着如果两次 update 间隔小于 throttle，第一次的文本会被完全覆盖。这在 LLM 流式输出中通常没问题（因为每次 update 都是完整前缀），但如果用于其他场景可能导致数据丢失。
4. **Heartbeat 与主队列的竞争**：`heartbeat-runner.ts` 在 `requests-in-flight` 时 skip 并返回，但 `runOnce` 内部仍然执行了 `getQueueSize` 检查。这种双重检查（runner 层 + runOnce 层）增加了维护负担。

### 6.3 如果要重新设计，可能会改变什么

1. **将恢复策略提取为策略模式**：`run.ts` 的 `while(true)` 中混杂了 5+ 种恢复策略，可以提取为 `RecoveryStrategy` 接口，按错误类型注册策略链，使主循环只负责 "尝试 → 失败 → 找下一个策略"。
2. **统一超时语义**：目前 `attempt.ts` 有 `timeoutMs`（attempt 级）、`COMPACTION_RETRY_AGGREGATE_TIMEOUT_MS`（compaction 级）、`abortWarnTimer`（abort 后 10s 警告），三层超时容易相互干扰。可以设计为层级化的 `TimeoutBudget`，每层分配时间片。
3. **Cron 调度器抽离为独立进程/Worker**：当前 `onTimer` 的 `locked` 块和 worker 池都在主线程，长任务会占用事件循环。虽然 `armRunningRecheckTimer` 做了防御，但更好的方案是将 job 执行放入 Worker 或子进程。
4. **Subagent announce 的可靠性增强**：当前 `sendAnnounce` 使用 `callGateway` 的 HTTP 调用，如果 gateway 重启，in-flight 的 announce 会丢失。可以考虑将 announce 持久化到队列（类似 cron store），保证 at-least-once 交付。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：编排循环的设计不是 "让 LLM 一直跑"，而是 "在 LLM 不可靠的前提下，定义清晰的故障边界和恢复契约"。OpenClaw 的 `run.ts` 虽然代码量大，但其本质是一个**错误分类器 + 恢复策略调度器**——它将 LLM 的混沌输出（超时、rate limit、context overflow、auth failure）转化为确定性的系统行为（compaction、profile rotation、model fallback、用户友好错误）。这种 "防御式编排" 比 "乐观式编排" 更适合生产环境。
