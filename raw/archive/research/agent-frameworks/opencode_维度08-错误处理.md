# 维度：错误处理 (Error Handling)

## 1. 一句话定位

错误处理是 OpenCode 的"免疫系统"，通过三级分类（overflow→compaction、可重试→退避、不可重试→终止）和指数退避策略，将 LLM 调用中的各种故障转化为可控的状态转移。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **上下文溢出导致会话崩溃**：`ContextOverflowError` 如果不触发 compaction，会直接终止 loop，用户丢失整个会话上下文。
- **临时网络错误中断任务**：API 超限、连接重置等临时错误如果没有重试机制，会让用户从头开始。
- **错误信息混乱**：AI SDK 的异常类型多样（`APICallError`、`LoadAPIKeyError`、`DOMException`），如果没有统一转换，错误处理逻辑会遍布各处。
- **无限重试浪费资源**：如果没有区分可重试和不可重试错误，系统可能对配置错误等问题无限重试。

### 2.2 OpenCode 的具体触发条件

- **流式过程中出错**：`processor.ts:L353-385` 的 catch 块
- **API 调用失败**：`llm.ts:L172-177` 的 `onError` 回调
- **错误统一转换**：`message-v2.ts:L827-913` 的 `fromError`

---

## 3. 核心设计思路

### 3.1 抽象模型

```
错误分类决策树：

Error ──► ContextOverflowError?
    ├──► YES ──► needsCompaction = true ──► 触发 compaction ──► continue
    │
    └──► NO ──► retryable?
            ├──► YES ──► 计算退避时间 ──► sleep ──► continue
            │
            └──► NO ──► 写入 assistantMessage.error ──► 停止 loop
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **三级分类** | overflow/compaction、可重试、不可重试 | 统一重试或统一终止 | 精确分类最大化自动恢复能力，同时避免无意义重试 |
| **指数退避** | `RETRY_INITIAL_DELAY * Math.pow(2, attempt-1)` | 固定间隔 | 减少服务器压力，避免洪水请求 |
| **尊重服务端退避** | 优先使用 `retry-after` / `retry-after-ms` 头 | 只使用客户端计算 | `retry.ts:L28-58` 体现了对服务端意愿的尊重 |
| **统一错误转换** | `fromError` 将各种异常转为 NamedError | 各处单独处理 | 集中处理减少遗漏，统一错误格式便于日志和监控 |

### 3.3 数据流/控制流

```
[LLM.stream 或工具执行]
    │
    └──► 异常抛出
            │
            ▼
    [processor.ts catch 块]
            │
            ├──► [MessageV2.fromError] ──► 统一错误类型转换
            │       │
            │       └──► ContextOverflowError?
            │           ├──► YES ──► needsCompaction = true
            │           └──► NO ──► 继续判断
            │
            ├──► [SessionRetry.retryable] ──► 可重试?
            │       ├──► YES ──► [SessionRetry.delay] ──► sleep ──► continue
            │       └──► NO ──► 写入 error ──► break
            │
            └──► [Bus.publish(Session.Event.Error)] ──► 通知 UI
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：三级错误分类

**作用**：在 catch 块中将错误分为三类并分别处理。

**关键源码**（`packages/opencode/src/session/processor.ts:353-385`）：
```typescript
} catch (e: any) {
  const error = MessageV2.fromError(e, { providerID: input.model.providerID })
  if (MessageV2.ContextOverflowError.isInstance(error)) {
    needsCompaction = true
    Bus.publish(Session.Event.Error, { sessionID: input.sessionID, error })
  } else {
    const retry = SessionRetry.retryable(error)
    if (retry !== undefined) {
      attempt++
      const delay = SessionRetry.delay(attempt, error.name === "APIError" ? error : undefined)
      SessionStatus.set(input.sessionID, { type: "retry", attempt, message: retry, next: Date.now() + delay })
      await SessionRetry.sleep(delay, input.abort).catch(() => {})
      continue
    }
    input.assistantMessage.error = error
    Bus.publish(Session.Event.Error, { sessionID: input.assistantMessage.sessionID, error })
    SessionStatus.set(input.sessionID, { type: "idle" })
  }
}
```

**这段代码为什么值得看**：
- `ContextOverflowError` 直接设置 `needsCompaction = true`，外层 loop 会触发 compaction，而不是重试。
- `SessionRetry.delay` 支持从 HTTP 头解析退避时间，是生产级设计。
- 不可重试错误直接写入 `assistantMessage.error` 并停止，避免无限循环。

### 机制 B：指数退避重试

**作用**：根据重试次数和服务端指示计算退避时间。

**关键源码**（`packages/opencode/src/session/retry.ts:28-59`）：
```typescript
export function delay(attempt: number, error?: MessageV2.APIError) {
  if (error) {
    const headers = error.data.responseHeaders
    if (headers) {
      const retryAfterMs = headers["retry-after-ms"]
      if (retryAfterMs) return Number.parseFloat(retryAfterMs)
      const retryAfter = headers["retry-after"]
      if (retryAfter) {
        const parsedSeconds = Number.parseFloat(retryAfter)
        if (!Number.isNaN(parsedSeconds)) return Math.ceil(parsedSeconds * 1000)
        const parsed = Date.parse(retryAfter) - Date.now()
        if (!Number.isNaN(parsed) && parsed > 0) return Math.ceil(parsed)
      }
    }
  }
  return Math.min(RETRY_INITIAL_DELAY * Math.pow(RETRY_BACKOFF_FACTOR, attempt - 1), RETRY_MAX_DELAY_NO_HEADERS)
}
```

**这段代码为什么值得看**：
- 优先使用服务端指示（`retry-after-ms`、`retry-after`），尊重服务端的流量控制意愿。
- 支持 `retry-after` 的秒数格式和 HTTP Date 格式。
- 指数退避有上限（`RETRY_MAX_DELAY_NO_HEADERS = 30s`），避免退避时间过长。

### 机制 C：错误统一转换

**作用**：将 AI SDK 和系统异常统一转换为内部 `NamedError`。

**关键源码**（`packages/opencode/src/session/message-v2.ts:827-913`）：
```typescript
export function fromError(e: unknown, ctx: { providerID: string }) {
  switch (true) {
    case e instanceof DOMException && e.name === "AbortError":
      return new MessageV2.AbortedError({ message: e.message }).toObject()
    case LoadAPIKeyError.isInstance(e):
      return new MessageV2.AuthError({ providerID: ctx.providerID, message: e.message }).toObject()
    case (e as SystemError)?.code === "ECONNRESET":
      return new MessageV2.APIError({ message: "Connection reset by server", isRetryable: true }).toObject()
    case APICallError.isInstance(e):
      const parsed = ProviderError.parseAPICallError({ providerID: ctx.providerID, error: e })
      if (parsed.type === "context_overflow")
        return new MessageV2.ContextOverflowError({ message: parsed.message }).toObject()
      return new MessageV2.APIError({...parsed}).toObject()
  }
}
```

**这段代码为什么值得看**：
- `switch(true)` 配合 `case` 条件，是一种简洁的多类型分发模式。
- 每种错误都保留原始错误作为 `cause`，便于调试。
- `ContextOverflowError` 被单独识别，触发 compaction 而非重试。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 输出到 | 编排循环 | 错误恢复后继续或终止 | `processor.ts catch` 块 |
| 输出到 | 记忆系统 | ContextOverflowError 触发 compaction | `compaction.ts` |
| 输出到 | 状态管理 | retry 状态更新 | `SessionStatus.set` |
| 输出到 | UI | 错误事件通知 | `Bus.publish(Session.Event.Error)` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **不是所有错误都值得重试**：ContextOverflowError 不需要重试，但需要 compaction；配置错误重试无意义。
2. **服务端知道最佳的退避时间**：优先使用 `retry-after` 头，假设服务端比客户端更了解自己的负载状况。
3. **错误需要统一格式**：便于日志、监控和 UI 展示。

### 6.2 这个设计的代价/风险

1. **错误分类可能不完整**：新增错误类型时需要同步更新 `fromError` 和 `retryable`，容易遗漏。
2. **退避时间上限固定**：`RETRY_MAX_DELAY_NO_HEADERS = 30s` 对某些场景可能太短。
3. **compaction 失败无兜底**：如果 compaction 本身也 overflow，系统会返回 "stop"。

### 6.3 如果要重新设计，可能会改变什么

1. **错误分类配置化**：将可重试错误类型和策略移到配置中。
2. **compaction 失败降级**：如果 compaction 失败，尝试更激进的截断策略。
3. **退避时间动态调整**：根据历史成功率动态调整退避参数。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：错误处理不是"try-catch"那么简单，而是一个**状态驱动的恢复系统**。OpenCode 的三级分类将错误从"致命故障"转化为"可控状态转移"：overflow 触发 compaction（自愈）、可重试错误触发退避（等待恢复）、不可重试错误终止并记录（优雅失败）。这种设计让系统在面对各种故障时都能保持可用性。
