# 维度名：错误处理（Error Handling）

## 1. 一句话定位

错误处理是 OpenClaw 在"不可靠的外部世界"（LLM API、网络、用户输入）与"必须持续运行的 Agent"之间的减震器——它通过分层重试、模型故障转移、循环检测和优雅降级，确保单次失败不会终止整个会话。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **API 瞬态错误导致会话崩溃**：LLM 提供商的 429/503 错误是常态而非异常。如果没有重试，用户会频繁看到"请求失败"，体验极差。
- **模型完全不可用时代理停摆**：如果配置的模型因额度用尽或区域故障不可用，没有 fallback 机制的话整个 Agent 就无法工作。
- **Agent 陷入无限工具循环**：LLM 可能反复调用相同工具（如不断 `cat` 同一文件或轮询同一进程），消耗 token 和 API 额度而不产生进展。
- **未捕获的 Promise rejection 杀死进程**：Node.js 默认会在未处理 rejection 时终止进程，一个边缘 bug 就能让整个 gateway 崩溃。

### 2.2 OpenClaw 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| LLM API 返回 429/500/503 | `src/infra/retry.ts` | 指数退避重试，最多 3 次 |
| 模型完全失败 | `src/agents/model-fallback.ts` | 按 fallback 链切换到备用模型 |
| 相同工具重复调用 | `src/agents/tool-loop-detection.ts` | 10 次警告，20 次阻断，30 次熔断 |
| Promise 未处理 rejection | `src/infra/unhandled-rejections.ts` | 根据错误类型决定退出或继续 |
| Compaction 超时 | `src/agents/pi-embedded-runner/run/compaction-timeout.ts` | 安全超时防止 compaction 卡住 |
| 上下文溢出 | `src/agents/pi-embedded-helpers/errors.ts` | 识别为 fail-over 错误还是终止错误 |

---

## 3. 核心设计思路

### 3.1 抽象模型

错误处理可以抽象为一个**决策树过滤器**：

```
错误发生
  ├── 瞬态网络错误？ → 重试（指数退避）
  ├── 模型不可用？ → Fallback 到下一个模型
  ├── 上下文溢出？ → 触发 compaction，不 fallback
  ├── 工具循环？ → 向 LLM 注入警告/阻断
  ├── 配置错误？ → 立即退出
  ├── 致命错误（OOM）？ → 立即退出
  └── 其他未知错误？ → 未处理 rejection 处理器决定
```

每一层都只处理自己层级的错误，不会越权。例如 `model-fallback.ts` 明确排除了上下文溢出错误（`isLikelyContextOverflowError`），因为切换模型无法解决上下文问题。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 重试策略 | 指数退避 + jitter + `Retry-After` 响应头支持 | 固定间隔重试 | `retry.ts:L115-123` 优先使用 provider 返回的 `retryAfterMs`，否则用指数退避，说明作者认为 provider 比通用策略更了解自身恢复时间 |
| Fallback 模型选择 | 基于配置链 + 运行时 provider cooldown 探测 | 随机选择或固定顺序 | `model-fallback.ts:L428-500` 的 cooldown 决策逻辑复杂，区分了 primary/fallback、rate_limit/auth/billing 等不同原因 |
| 工具循环检测 | 多种检测器并行（genericRepeat / knownPollNoProgress / pingPong） | 单一阈值计数 | `tool-loop-detection.ts` 区分了"轮询无进展"和"乒乓切换"两种不同模式，说明作者认为不同类型的循环需要不同的检测策略 |
| 未处理 rejection | 分类处理：fatal/config 退出、transient 继续、abort 静默 | 全部退出或全部忽略 | `unhandled-rejections.ts:L13-68` 定义了详细的错误码分类，说明作者认为"不是所有错误都致命" |

### 3.3 数据流/控制流

```
[LLM 调用] → 错误发生
                ↓
        [是否为 Abort？] ──是──→ 终止（用户主动取消）
                ↓ 否
        [是否为上下文溢出？] ──是──→ 触发 compaction
                ↓ 否
        [是否为可重试错误？] ──是──→ retryAsync（指数退避）
                ↓ 否/重试耗尽
        [模型 Fallback] → 遍历候选模型
                ↓
        [是否工具循环？] ──是──→ 注入警告到 LLM
                ↓
        [未处理 rejection 分类]
                ↓
        [致命/配置 → 退出] [瞬态 → 继续] [未知 → 退出]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：模型故障转移（Model Fallback）

**作用**：当主模型不可用时，自动切换到配置好的 fallback 模型链。

**设计意图**：LLM 提供商不可能 100% 可用。OpenClaw 面向的是"必须持续工作"的 Agent 场景，而不是"失败了就告诉用户"的 chatbot 场景。Fallback 让用户可以配置主模型（如 Claude Opus）+ 备用模型（如 GPT-4），在主模型不可用时无缝降级。

**关键源码**（`src/agents/model-fallback.ts:L502-503` 及 `L698-701`）：

```typescript
export async function runWithModelFallback<T>(params: {
  cfg: OpenClawConfig | undefined;
  provider: string;
  model: string;
  run: ModelFallbackRunFn<T>;
  // ...
}): Promise<ModelFallbackRunResult<T>> {
  const candidates = resolveFallbackCandidates({ /* ... */ });
  // ...
  for (let i = 0; i < candidates.length; i += 1) {
    // ...
    const errMessage = err instanceof Error ? err.message : String(err);
    if (isLikelyContextOverflowError(errMessage)) {
      throw err;  // 上下文溢出不走 fallback！
    }
    // ...继续尝试下一个候选
  }
}
```

这里最值得注意的是 **`isLikelyContextOverflowError` 被显式排除在 fallback 之外**。为什么？因为上下文溢出是一个"与模型无关"的问题——换一个模型（甚至换一个有更大窗口的模型）可能解决，但代码选择让上层的 compaction 逻辑来处理。这避免了 fallback 链被无意义的上下文溢出请求耗尽。

**关键源码**（`src/agents/model-fallback.ts:L428-500`）—— Cooldown 探测决策：

```typescript
function resolveCooldownDecision(params: {
  candidate: ModelCandidate;
  isPrimary: boolean;
  // ...
}): CooldownDecision {
  // 对于 auth 错误：永久跳过该 provider 的所有模型
  const isPersistentAuthIssue = inferredReason === "auth" || inferredReason === "auth_permanent";
  if (isPersistentAuthIssue) {
    return { type: "skip", reason: inferredReason, error: "..." };
  }

  // 对于 billing 错误：单 provider 设置探测，多 provider 跳过
  if (inferredReason === "billing") {
    const shouldProbeSingleProviderBilling =
      params.isPrimary && !params.hasFallbackCandidates && isProbeThrottleOpen(/* ... */);
    // ...
  }

  // 对于 rate_limit/overloaded：primary 探测，同 provider fallback 尝试
  const shouldAttemptDespiteCooldown =
    (params.isPrimary && (!params.requestedModel || shouldProbe)) ||
    (!params.isPrimary && (inferredReason === "rate_limit" || inferredReason === "overloaded"));
  // ...
}
```

这段决策逻辑体现了作者对**不同错误类型的恢复概率**的精细判断：
- **auth**：几乎不会自愈 → 永久跳过
- **billing**：用户可能充值 → 单 provider 时偶尔探测
- **rate_limit**：通常几分钟内恢复 → primary 探测、同 provider fallback 尝试
- **overloaded**：provider 端问题 → 同 provider 其他模型可能可用

### 机制 B：工具循环检测

**作用**：检测并阻断 Agent 在工具调用上的无限循环。

**设计意图**：LLM 不是完美的——它可能陷入"反复检查同一文件状态"或"在两个工具之间来回切换"的循环。这种循环消耗 API 额度但不做有用工作。

**关键源码**（`src/agents/tool-loop-detection.ts:L372-401`）：

```typescript
export function detectToolCallLoop(
  state: SessionState,
  toolName: string,
  params: unknown,
  config?: ToolLoopDetectionConfig,
): LoopDetectionResult {
  const currentHash = hashToolCall(toolName, params);
  const noProgress = getNoProgressStreak(history, toolName, currentHash);

  if (noProgressStreak >= resolvedConfig.globalCircuitBreakerThreshold) {
    return {
      stuck: true,
      level: "critical",
      detector: "global_circuit_breaker",
      message: `CRITICAL: ${toolName} has repeated identical no-progress outcomes ${noProgressStreak} times. Session execution blocked...`,
    };
  }
  // ...
}
```

检测的核心是 **`hashToolCall` + `hashToolOutcome`**（`L106-125`）：

```typescript
export function hashToolCall(toolName: string, params: unknown): string {
  return `${toolName}:${digestStable(params)}`;
}

function stableStringify(value: unknown): string {
  // 确定性 JSON：排序键、递归处理
  const keys = Object.keys(obj).toSorted();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(obj[k])}`).join(",")}}`;
}
```

使用**确定性序列化 + SHA256** 而非引用比较，确保即使对象创建时间不同，相同参数也会得到相同哈希。这是检测的基础。

三种检测器：
1. **generic_repeat**：同一工具+参数重复调用（非轮询工具）
2. **known_poll_no_progress**：`command_status`/`process poll` 等已知轮询工具，结果无变化
3. **ping_pong**：两个工具交替调用，各自结果稳定不变

阈值分层（`L28-30`）：
- 警告：10 次
- 阻断：20 次
- 熔断：30 次

### 机制 C：全局未处理 Rejection 处理器

**作用**：捕获所有未被 `try/catch` 处理的 Promise rejection，根据错误类型决定进程命运。

**设计意图**：Node.js 进程是 gateway 的生命线——一个未处理的 rejection 不应该轻易杀死它。但配置错误或 OOM 又确实应该退出。

**关键源码**（`src/infra/unhandled-rejections.ts:L219-254`）：

```typescript
export function installUnhandledRejectionHandler(): void {
  process.on("unhandledRejection", (reason, _promise) => {
    if (isUnhandledRejectionHandled(reason)) return;

    if (isAbortError(reason)) {
      console.warn("[openclaw] Suppressed AbortError:", formatUncaughtError(reason));
      return;  // 用户取消，静默处理
    }

    if (isFatalError(reason)) {
      console.error("[openclaw] FATAL unhandled rejection:", formatUncaughtError(reason));
      process.exit(1);  // OOM 等致命错误必须退出
      return;
    }

    if (isConfigError(reason)) {
      console.error("[openclaw] CONFIGURATION ERROR:", formatUncaughtError(reason));
      process.exit(1);  // 配置错误需要修复后重启
      return;
    }

    if (isTransientNetworkError(reason)) {
      console.warn("[openclaw] Non-fatal unhandled rejection (continuing):", formatUncaughtError(reason));
      return;  // 网络抖动，继续运行
    }

    // 未知错误：保守策略，退出
    console.error("[openclaw] Unhandled promise rejection:", formatUncaughtError(reason));
    process.exit(1);
  });
}
```

这里的分类体现了**"已知危险 → 退出，已知安全 → 继续，未知 → 保守退出"**的策略。特别值得注意的是 `TRANSIENT_NETWORK_CODES`（`L24-44`）定义了 18 种网络错误码，这些都是"会自愈的"。

---

## 5. 与其他维度的交互

```
[错误处理] --(重试 Compaction)--> [上下文管理]
[错误处理] --(Fallback 模型选择)--> [编排循环]
[错误处理] --(循环检测阻断)--> [工具系统]
[错误处理] --(模型失败日志)--> [状态管理]
[错误处理] <--(工具调用历史)-- [工具系统]
[错误处理] <--(会话状态)-- [状态管理]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 上下文管理 | compaction 失败后的重试逻辑 | `compaction.ts` 的 `retryAsync` |
| 输出到 | 编排循环 | 模型 fallback 的结果返回给主循环 | `model-fallback.ts` 的 `runWithModelFallback` |
| 输出到 | 工具系统 | 检测到循环后向 LLM 注入警告消息 | `tool-loop-detection.ts` 返回的 `message` |
| 依赖 | 工具系统 | 获取工具调用历史用于循环检测 | `recordToolCall` / `recordToolCallOutcome` |
| 依赖 | 状态管理 | 读取/更新 session 的 cooldown 状态 | `auth-profiles.ts` 的 cooldown 机制 |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"瞬态错误比永久错误多得多"**：重试机制是默认配置（3 次），fallback 只在重试耗尽后才触发。这说明作者假设大多数错误是暂时的。
2. **"LLM 会听从循环警告"**：`tool-loop-detection.ts` 检测到循环后，选择向 LLM 发送警告消息而非强制终止会话。这假设 LLM 在收到警告后会改变行为。
3. **"网络错误可以安全忽略"**：`isTransientNetworkError` 将 18 种网络错误码归类为"非致命"，这意味着 gateway 可能在网络分区期间继续运行，只是暂时无法调用 LLM。

### 6.2 这个设计的代价/风险

1. **重试放大了 provider 的压力**：如果 provider 已经过载（503），指数退避重试仍会持续发送请求。虽然有 jitter 和 `Retry-After` 支持，但在大规模部署时可能成为"善意 DDoS"。
2. **Fallback 链的复杂度**：`resolveCooldownDecision` 的逻辑非常复杂，区分了 primary/fallback、单 provider/多 provider、不同错误原因——这使得行为难以预测，调试困难。
3. **循环检测的误报**：`generic_repeat` 检测器只基于参数哈希，可能误判"合法重复调用"（如用户明确要求的批量处理）。

### 6.3 如果要重新设计，可能会改变什么

1. **统一的错误分类体系**：目前错误分类散落在 `failover-error.ts`、`unhandled-rejections.ts`、`model-fallback.ts` 等多个文件中，各自有自己的分类逻辑。统一为一个错误分类注册表会更清晰。
2. **Fallback 的 circuit breaker**：当前 fallback 是"全部尝试一遍"，如果整个 fallback 链都失败，会快速耗尽。可以考虑为 fallback 链本身添加 circuit breaker。
3. **循环检测的自适应阈值**：固定阈值（10/20/30）对所有任务一视同仁。对于简单任务可能太宽松，对于复杂任务可能太严格。

### 6.4 对我自己设计 Agent 系统的启示

> **错误处理不是"兜底 catch"，而是"分层策略"**。OpenClaw 的设计启示是：不同层级的错误需要不同的处理策略——瞬态错误重试、模型错误 fallback、逻辑错误检测、进程错误分类退出。把"所有错误都 catch 然后重试"是危险的，因为某些错误（如上下文溢出）重试只会加剧问题。
