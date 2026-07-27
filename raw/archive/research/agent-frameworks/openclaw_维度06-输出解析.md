# 维度名：输出解析（Output Parsing）

## 1. 一句话定位

输出解析是 OpenClaw 中负责将 LLM 原始流式输出（含标签、指令、工具调用、推理块）转化为结构化、可消费、面向用户/下游系统的安全内容的中间层，核心解决"模型输出格式不可控"与"下游消费需要确定性"之间的矛盾。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有输出解析层，系统会在多个层面崩溃或劣化：

1. **推理内容泄漏到用户界面**：模型（尤其是 DeepSeek、GLM-5、Minimax 等）会在正文中输出 `<think>...</think>` 或 `<|assistant|>` 等内部标记。若不剥离，`handleMessageUpdate` 中 `ctx.emitAgentEvent({ stream: "assistant", data: { text: ... } })` 会直接将这些标记发给用户，导致体验劣化甚至暴露系统提示。

2. **重复/非单调输出导致 UI 闪烁**：部分 provider 在 `text_end` 时会重发完整内容（而非增量 delta）。`pi-embedded-subscribe.handlers.messages.ts:L155-162` 中的 monotonic 逻辑若不生效，`deltaBuffer` 会累积重复文本，前端看到文字回跳或重复追加。

3. **工具结果中的 base64 图片数据撑爆内存/传输**：`read_image` 等工具返回的 image content 包含原始 bytes。`sanitizeToolResult` 不截断的话，这些 bytes 会进入 session messages 和 WebSocket payload，造成内存和带宽灾难。

4. **MEDIA: 指令和回复标签（`[[reply:123]]`）直接暴露给用户**：LLM 输出中用于控制行为的机器指令会原样显示在聊天界面中，破坏产品体验。

5. **Markdown 代码块在分块渲染时断裂**：若 `EmbeddedBlockChunker` 不处理 fence split，一个代码块被切成两半时，前端 Markdown 渲染会错乱（ fence 未闭合导致后续所有内容被误解析为代码）。

### 2.2 OpenClaw 的具体触发条件

- **触发条件 1**：当 `AgentSession` 产生 `message_start` 事件时，`handleMessageStart` 被调用，重置 `deltaBuffer`、`blockState`、`replyDirectiveAccumulator` 等全部流式状态（`pi-embedded-subscribe.handlers.messages.ts:L59-76`）。
- **触发条件 2**：当 `message_update` 事件的 `evtType` 为 `text_delta` / `text_start` / `text_end` 时，`handleMessageUpdate` 进入输出解析主路径（`pi-embedded-subscribe.handlers.messages.ts:L78-253`）。
- **触发条件 3**：当 `tool_execution_end` 事件到达时，`handleToolExecutionEnd` 调用 `sanitizeToolResult` 和 `emitToolResultOutput`（`pi-embedded-subscribe.handlers.tools.ts:L422-577`）。
- **触发条件 4**：当 `blockReplyChunking` 配置存在且 `text_delta` 到达时，`ctx.blockChunker.append(chunk)` 触发分块缓冲（`pi-embedded-subscribe.ts:L168`）。

---

## 3. 核心设计思路

### 3.1 抽象模型

输出解析可以被抽象为一个**带状态的多级流式过滤器管道**：

```
原始 LLM 流事件
  → [事件分发器]          ← 按 type 路由到 message/tool/lifecycle/compaction 处理器
  → [增量归一化层]        ← 解决 delta vs full-content、重复、非单调问题
  → [标签剥离器]          ← 状态机处理 <think>, <final>, 代码 span 保护
  → [指令解析器]          ← 提取 MEDIA:, reply tags, silent tokens
  → [块分片器]            ← 按语义边界切分，保护 Markdown fence
  → [工具结果消毒器]      ← 截断长文本、移除 image bytes、提取 media paths
  → [Provider 适配层]     ← Anthropic/OpenAI payload 规范化
  → [结构化事件发射]      ← assistant/thinking/tool/compaction 事件
```

整个管道是**增量式（incremental）**的：每个 `text_delta` 只携带增量文本，但所有过滤器都维护内部状态（`deltaBuffer`、`blockState`、`replyDirectiveAccumulator` 等），从而支持跨 chunk 的语义解析（如 `<think>` 标签可能跨两个 chunk 到达）。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **状态重置时机** | 在 `message_start` 时重置所有流式状态 | 在 `message_end` 或 `text_end` 时重置 | `handleMessageStart` 注释明确说明：`text_end` 不可靠（late/duplicate end events），`message_start` 是唯一可靠边界（`pi-embedded-subscribe.handlers.messages.ts:L68-72`） |
| **推理块处理** | 用状态机跨 chunk 跟踪 `<think>` 标签，并区分 `blockState`（用于 block reply）和 `partialBlockState`（用于流式 assistant 事件） | 简单正则一次性替换 | 标签可能跨 chunk 到达，且 block reply 和 streaming assistant 需要不同粒度的可见性；代码中明确维护了两个独立状态对象（`pi-embedded-subscribe.ts:L52-53`） |
| **单调输出保证** | 用 `deltaBuffer` 累积全文，通过前缀比较（`startsWith`）提取真正的新增内容 | 完全信任 provider 的 delta 字段 | 代码注释说明："Some providers resend full content on `text_end`"（`pi-embedded-subscribe.handlers.messages.ts:L153`），因此必须有防御性逻辑 |
| **代码块保护** | 在剥离标签前先构建 `codeSpanIndex`，所有标签扫描跳过代码 span 内部 | 全局正则替换 | `stripBlockTags` 中明确调用 `buildCodeSpanIndex` 并检查 `codeSpans.isInside(idx)`（`pi-embedded-subscribe.ts:L377-386`），防止模型在代码示例中写的 `<think>` 被误删 |
| **工具结果截断** | 硬截断到 8000 字符并标注 `…(truncated)…` | 流式分页或完全不截断 | `TOOL_RESULT_MAX_CHARS = 8000`（`pi-embedded-subscribe.tools.ts:L9`），这是为了防止 LLM 上下文被单个工具结果占满；代价是可能丢失尾部信息 |
| **Messaging 工具去重** | 只检查已提交（成功执行）的 messaging 文本，pending 状态不用于去重 | 所有 pending 也参与去重 | 注释说明："checking pending texts is risky because if the tool fails after suppression, the user gets no response"（`pi-embedded-subscribe.ts:L492-493`） |

### 3.3 数据流/控制流

```
LLM Provider Stream
  │
  ▼
AgentSession 产生事件（message_start / message_update / message_end /
│                    tool_execution_start / tool_execution_end / auto_compaction_start...）
│
▼
createEmbeddedPiSessionEventHandler (pi-embedded-subscribe.handlers.ts:L22-66)
  │── message_start ──→ handleMessageStart ──→ resetAssistantMessageState()
  │── message_update ──→ handleMessageUpdate
  │                      ├── thinking_delta ──→ emitReasoningStream()
  │                      └── text_delta ──→ deltaBuffer ──→ blockChunker.append()
  │                                          ├── stripBlockTags() ──→ 标签剥离
  │                                          ├── parseReplyDirectives() ──→ 指令解析
  │                                          └── emitAgentEvent({stream:"assistant"})
  │── message_end ──→ handleMessageEnd
  │                      ├── promoteThinkingTagsToBlocks() ──→ 结构化转换
  │                      ├── resolveSilentReplyFallbackText() ──→ 静默回复回退
  │                      ├── finalizeAssistantTexts() ──→ 文本归档
  │                      └── blockChunker.drain() / emitBlockChunk()
  │── tool_execution_start ──→ handleToolExecutionStart ──→ flushBlockReplyBuffer()
  │── tool_execution_end ──→ handleToolExecutionEnd
  │                      ├── sanitizeToolResult() ──→ 截断/清理
  │                      ├── emitToolResultOutput() ──→ 结果分发
  │                      └── after_tool_call hook
  └── auto_compaction_start/end ──→ handleAutoCompactionStart/End
                              └── resetForCompactionRetry() / waitForCompactionRetry()
```

---

## 4. 关键机制拆解（含源码）

> 原则：每个子机制只放一段最核心的代码（5-15 行），其余用文字解释。
> 所有源码必须标注文件路径和行号。

### 机制 A：流式事件分发与生命周期管理

**作用**：将底层 `AgentSession` 产生的异构事件路由到对应的处理器，并在关键生命周期点（compaction、agent end）执行状态清理。

**设计意图**：将事件处理逻辑按类型拆分到独立文件（`handlers.messages.ts`、`handlers.tools.ts`、`handlers.compaction.ts`），避免一个巨型 switch-case；同时通过 `EmbeddedPiSubscribeContext` 统一共享状态和回调。

**关键源码**（`src/agents/pi-embedded-subscribe.handlers.ts:L22-66`）：
```typescript
export function createEmbeddedPiSessionEventHandler(ctx: EmbeddedPiSubscribeContext) {
  return (evt: EmbeddedPiSubscribeEvent) => {
    switch (evt.type) {
      case "message_start":
        handleMessageStart(ctx, evt as never);
        return;
      case "message_update":
        handleMessageUpdate(ctx, evt as never);
        return;
      case "message_end":
        handleMessageEnd(ctx, evt as never);
        return;
      case "tool_execution_start":
        handleToolExecutionStart(ctx, evt as never).catch((err) => {
          ctx.log.debug(`tool_execution_start handler failed: ${String(err)}`);
        });
        return;
      // ... 其他事件
    }
  };
}
```

**为什么值得看**：`tool_execution_start` 和 `tool_execution_end` 被标记为 async 但用 `.catch()` 包裹，说明这些回调是**best-effort、非阻塞**的——设计意图是不让工具元数据的发送延迟阻塞核心 LLM 流。

---

### 机制 B：单调增量累积与重复抑制

**作用**：解决 provider 在 `text_end` 时重发完整内容、或 delta 与 content 不一致的问题，保证输出严格单调递增。

**设计意图**：不盲目信任 provider 的事件格式，而是用本地 `deltaBuffer` 作为 ground truth，通过字符串前缀比较计算真正的新增内容。

**关键源码**（`src/agents/pi-embedded-subscribe.handlers.messages.ts:L146-162`）：
```typescript
  let chunk = "";
  if (evtType === "text_delta") {
    chunk = delta;
  } else if (evtType === "text_start" || evtType === "text_end") {
    if (delta) {
      chunk = delta;
    } else if (content) {
      // KNOWN: Some providers resend full content on `text_end`.
      // We only append a suffix (or nothing) to keep output monotonic.
      if (content.startsWith(ctx.state.deltaBuffer)) {
        chunk = content.slice(ctx.state.deltaBuffer.length);
      } else if (ctx.state.deltaBuffer.startsWith(content)) {
        chunk = "";
      } else if (!ctx.state.deltaBuffer.includes(content)) {
        chunk = content;
      }
    }
  }
```

**为什么值得看**：三个分支覆盖了所有 provider 怪异行为：① 正常前缀扩展（取 diff）；② provider 回退到更早内容（忽略）；③ 完全不相关的新内容（全量追加）。这是防御式编程的典范。

---

### 机制 C：状态化标签剥离（`<think>` / `<final>`）与代码 Span 保护

**作用**：跨 chunk 跟踪 `<think>`、`<final>` 等标签，剥离推理内容或提取最终答案；同时保护代码块内出现的同名标记不被误删。

**设计意图**：标签可能跨 chunk 到达（如 `<thin` 在 chunk 1，`k>text</think>` 在 chunk 2），必须用状态机维护 `inThinking` / `inFinal`；代码示例中的 `<think>` 是合法内容，不能剥离。

**关键源码**（`src/agents/pi-embedded-subscribe.ts:L368-399`）：
```typescript
  const stripBlockTags = (
    text: string,
    state: { thinking: boolean; final: boolean; inlineCode?: InlineCodeState },
  ): string => {
    // ...
    const codeSpans = buildCodeSpanIndex(text, inlineStateStart);
    let processed = "";
    THINKING_TAG_SCAN_RE.lastIndex = 0;
    let lastIndex = 0;
    let inThinking = state.thinking;
    for (const match of text.matchAll(THINKING_TAG_SCAN_RE)) {
      const idx = match.index ?? 0;
      if (codeSpans.isInside(idx)) {
        continue;  // ① 代码 span 内跳过
      }
      if (!inThinking) {
        processed += text.slice(lastIndex, idx);
      }
      const isClose = match[1] === "/";
      inThinking = !isClose;  // ② 状态机翻转
      lastIndex = idx + match[0].length;
    }
    if (!inThinking) {
      processed += text.slice(lastIndex);
    }
    state.thinking = inThinking;  // ③ 状态写回，供下一 chunk 使用
    // ...
```

**为什么值得看**：`codeSpans.isInside(idx)` 是核心保护逻辑——先构建代码 span 索引，再判断标签位置是否在代码块内。`state.thinking` 在函数结束时写回，使状态能跨 chunk 累积。这是"流式状态机"的典型实现。

---

### 机制 D：Reply 指令解析（MEDIA: / reply tags / silent tokens）

**作用**：从 LLM 输出中提取机器指令（媒体附件、回复目标、静默标记），将机器控制流与用户可见文本分离。

**设计意图**：LLM 被训练在输出中嵌入 `MEDIA:/path/to/img.png` 或 `[[reply:123]]` 等标记来控制行为。这些标记必须在到达用户前被剥离，同时提取的指令要驱动下游的媒体上传和消息路由。

**关键源码**（`src/agents/auto-reply/reply/streaming-directives.ts:L75-133`）：
```typescript
export function createStreamingDirectiveAccumulator() {
  let pendingTail = "";
  let pendingReply: PendingReplyState = { sawCurrent: false, hasTag: false };
  let activeReply: PendingReplyState = { sawCurrent: false, hasTag: false };

  const consume = (raw: string, options: ConsumeOptions = {}): ReplyDirectiveParseResult | null => {
    let combined = `${pendingTail}${raw ?? ""}`;
    pendingTail = "";

    if (!options.final) {
      const split = splitTrailingDirective(combined);
      combined = split.text;
      pendingTail = split.tail;  // ① 保留未闭合的 [[... 到下一 chunk
    }
    // ...
    // Keep reply context sticky for the full assistant message
    activeReply = { explicitId, sawCurrent, hasTag };
    pendingReply = { sawCurrent: false, hasTag: false };
    return combinedResult;
  };
```

**为什么值得看**：`splitTrailingDirective` 处理指令标签跨 chunk 的问题（如 `[[rep` 和 `ly:123]]` 分两次到达）。`activeReply` 的 sticky 设计保证一旦检测到 reply tag，后续所有 chunk 都继承同一回复目标，直到 `reset()`。

---

### 机制 E：Block 分片与 Markdown Fence 保护

**作用**：将长文本按语义边界（段落、句子、换行）切分为适合 UI 渲染的块，同时保证不切断 Markdown 代码块（fenced code block）。

**设计意图**：前端需要增量渲染，但如果在一个代码块中间切断，Markdown 解析会错乱。因此必须在 fence 边界处安全切断，必要时主动关闭并重新打开 fence。

**关键源码**（`src/agents/pi-embedded-block-chunker.ts:L125-218`）：
```typescript
  drain(params: { force: boolean; emit: (chunk: string) => void }) {
    // KNOWN: We cannot split inside fenced code blocks (Markdown breaks + UI glitches).
    // When forced (maxChars), we close + reopen the fence to keep Markdown valid.
    const { force, emit } = params;
    // ...
    const fenceSpans = parseFenceSpans(source);
    let start = 0;
    let reopenFence: FenceSpan | undefined;

    while (start < source.length) {
      const reopenPrefix = reopenFence ? `${reopenFence.openLine}\n` : "";
      // ...
      const breakResult = /* 寻找安全切断点 */;
      // ...
      const fenceSplit = breakResult.fenceSplit;
      if (fenceSplit) {
        const closeFence = rawChunk.endsWith("\n")
          ? `${fenceSplit.closeFenceLine}\n`
          : `\n${fenceSplit.closeFenceLine}\n`;
        rawChunk = `${rawChunk}${closeFence}`;  // ① 主动关闭 fence
      }
      emit(rawChunk);
      if (fenceSplit) {
        return { start: absoluteBreakIdx, reopenFence: fenceSplit.fence };  // ② 记录 reopen
      }
    }
    this.#buffer = reopenFence
      ? `${reopenFence.openLine}\n${source.slice(start)}`  // ③ 残余内容带上 reopen 前缀
      : stripLeadingNewlines(source.slice(start));
  }
```

**为什么值得看**：当强制切断点落在 fence 内部时，不是简单切断，而是**主动插入 close fence + 在下一 chunk 前缀插入 open fence**，从而保证任意 chunk 都是合法 Markdown。这是流式渲染中非常精细的边界处理。

---

### 机制 F：工具结果消毒（Sanitization）与媒体提取

**作用**：截断过长的工具输出文本、移除 image content 的原始 bytes、从工具结果中提取 MEDIA: 路径，并区分 trusted/untrusted 工具的媒体权限。

**设计意图**：工具结果直接来自外部系统（shell 命令、文件读取、网页抓取），可能包含任意大的输出。必须消毒后才能：① 进入 LLM 上下文（避免占满 token 预算）；② 展示给用户（避免 UI 卡顿）；③ 防止 untrusted 插件通过本地文件路径读取敏感文件。

**关键源码**（`src/agents/pi-embedded-subscribe.tools.ts:L86-114`）：
```typescript
export function sanitizeToolResult(result: unknown): unknown {
  if (!result || typeof result !== "object") {
    return result;
  }
  const record = result as Record<string, unknown>;
  const content = Array.isArray(record.content) ? record.content : null;
  if (!content) {
    return record;
  }
  const sanitized = content.map((item) => {
    // ...
    if (type === "text" && typeof entry.text === "string") {
      return { ...entry, text: truncateToolText(entry.text) };  // ① 截断长文本
    }
    if (type === "image") {
      const cleaned = { ...entry };
      delete cleaned.data;  // ② 删除原始 image bytes
      return { ...cleaned, bytes: data?.length, omitted: true };
    }
    return item;
  });
  return { ...record, content: sanitized };
}
```

**为什么值得看**：`delete cleaned.data` 是核心安全操作——原始 base64 图片数据在消毒后被彻底移除，只保留 `bytes` 长度和 `omitted: true` 标记。这防止了巨大的二进制数据在系统内无节制传播。

---

### 机制 G：Provider 特定 Payload 规范化

**作用**：针对不同 provider（Anthropic、OpenAI、OpenRouter 等）的工具格式、context management、thinking signatures 进行适配。

**设计意图**：底层 LLM SDK（pi-ai）抽象了通用接口，但各 provider 对 tool schema、tool choice、context storage 的支持存在差异。OpenClaw 在 stream wrapper 层做最后一英里适配，而非污染通用逻辑。

**关键源码**（`src/agents/pi-embedded-runner/anthropic-stream-wrappers.ts:L272-305`）：
```typescript
export function createAnthropicToolPayloadCompatibilityWrapper(
  baseStreamFn: StreamFn | undefined,
): StreamFn {
  const underlying = baseStreamFn ?? streamSimple;
  return (model, context, options) => {
    const originalOnPayload = options?.onPayload;
    return underlying(model, context, {
      ...options,
      onPayload: (payload) => {
        if (
          payload &&
          typeof payload === "object" &&
          requiresAnthropicToolPayloadCompatibilityForModel(model)
        ) {
          const payloadObj = payload as Record<string, unknown>;
          if (
            Array.isArray(payloadObj.tools) &&
            usesOpenAiFunctionAnthropicToolSchemaForModel(model)
          ) {
            payloadObj.tools = payloadObj.tools
              .map((tool) => normalizeOpenAiFunctionAnthropicToolDefinition(tool))
              .filter((tool): tool is Record<string, unknown> => !!tool);
          }
          if (usesOpenAiStringModeAnthropicToolChoiceForModel(model)) {
            payloadObj.tool_choice = normalizeOpenAiStringModeAnthropicToolChoice(
              payloadObj.tool_choice,
            );
          }
        }
        return originalOnPayload?.(payload, model);
      },
    });
  };
}
```

**为什么值得看**：wrapper 通过拦截 `onPayload` 在请求发出前动态修改 tool schema 和 tool_choice，而不是在业务逻辑中分支。这使得 provider 适配逻辑可组合（多个 wrapper 可以链式叠加），且不影响核心订阅逻辑。

---

### 机制 H：Compaction 重试状态管理

**作用**：在自动 compaction（上下文压缩）触发后，管理重试状态，保证 compaction 完成前后续逻辑正确等待。

**设计意图**：compaction 是异步的，可能在 agent run 中途触发。如果 compaction 后立即重试 LLM 请求，必须等 compaction 真正完成并清理状态，否则会出现消息重复或上下文不一致。

**关键源码**（`src/agents/pi-embedded-subscribe.ts:L231-271`）：
```typescript
  const ensureCompactionPromise = () => {
    if (!state.compactionRetryPromise) {
      state.compactionRetryPromise = new Promise((resolve, reject) => {
        state.compactionRetryResolve = resolve;
        state.compactionRetryReject = reject;
      });
      state.compactionRetryPromise.catch((err) => {
        log.debug(`compaction promise rejected (no waiter): ${String(err)}`);
      });
    }
  };

  const resolveCompactionRetry = () => {
    if (state.pendingCompactionRetry <= 0) {
      return;
    }
    state.pendingCompactionRetry -= 1;
    if (state.pendingCompactionRetry === 0 && !state.compactionInFlight) {
      state.compactionRetryResolve?.();
      state.compactionRetryResolve = undefined;
      state.compactionRetryReject = undefined;
      state.compactionRetryPromise = null;
    }
  };
```

**为什么值得看**：使用 `pendingCompactionRetry` 计数器而非简单 boolean，是为了支持**嵌套或连续多次 compaction**。`ensureCompactionPromise` 中显式 `.catch()` 防止 unhandled rejection，这是 Node.js 中 Promise 反模式的防御性处理。

---

## 5. 与其他维度的交互

```
[输出解析] --(结构化事件: assistant/thinking/tool/compaction)--> [事件总线 / WebSocket]
[输出解析] --(消毒后的 tool result)--> [LLM 上下文 / Session Messages]
[输出解析] --(block reply payload)--> [频道适配层 / Telegram/Discord/Slack]
[输出解析] --(mediaUrls / audioAsVoice)--> [媒体上传系统]
[输出解析] <--(原始流事件: message_update/tool_execution_end)-- [LLM Provider / pi-ai SDK]
[输出解析] <--(工具定义 / provider capabilities)-- [Provider 配置系统]
[输出解析] <--(compaction 触发信号)-- [Session / 上下文管理]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | 事件总线 | `assistant`、`thinking`、`tool`、`compaction`、`lifecycle` 事件 | `emitAgentEvent({ runId, stream, data })` |
| 输出到 | 频道适配层 | Block reply 文本、mediaUrls、replyToId、audioAsVoice | `params.onBlockReply(payload)` |
| 输出到 | 媒体系统 | 从 tool result 和 reply directive 提取的媒体路径 | `extractToolResultMediaPaths()`、`splitMediaFromOutput()` |
| 依赖 | LLM Provider | 原始流事件（delta、content、thinking block） | `session.subscribe(handler)` |
| 依赖 | Provider 配置 | providerFamily、toolSchemaMode、thinking signature 策略 | `resolveProviderCapabilities()`、`provider-capabilities.ts` |
| 依赖 | Session / 上下文 | compaction 触发、消息历史、sessionFile | `handleAutoCompactionStart/End`、`ctx.params.session.messages` |
| 依赖 | 插件系统 | before_compaction、after_tool_call hooks | `getGlobalHookRunner()` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **假设 provider 是不可靠的**：代码中大量防御性逻辑（monotonic delta、late text_end 处理、duplicate suppression）都基于一个假设——LLM provider 的流式输出不保证顺序、不保证格式一致性、可能重发内容。

2. **假设模型的标签输出是结构化的但不可靠**：`<think>` 和 `<final>` 被当作结构化标记处理，但代码同时做了代码 span 保护，说明作者假设模型可能在代码示例中"误用"这些标签。

3. **假设工具结果可能极大且包含敏感数据**：`sanitizeToolResult` 的截断和 image bytes 删除，说明作者假设外部工具返回的数据不可信且可能失控。

4. **假设 messaging 工具的成功执行优先于 assistant 文本**：去重逻辑只检查已提交的 messaging 文本，说明作者假设"工具已发送的消息"是 ground truth，assistant 的确认文本是冗余的。

### 6.2 这个设计的代价/风险

1. **状态复杂度极高**：`EmbeddedPiSubscribeState` 包含 30+ 个字段，跨 `message_start/update/end` 和 `tool_execution_start/end` 维护一致性非常困难。任何一个状态字段在错误时机未重置，都会导致泄漏或重复。

2. **deltaBuffer 的内存风险**：`deltaBuffer` 累积整个 assistant message 的全文，对于极长输出（如 100K+ token）会占用大量内存。代码中没有显式的长度限制或截断逻辑。

3. **标签正则的脆弱性**：`THINKING_TAG_SCAN_RE` 使用 `/gi` 全局忽略大小写匹配，如果模型输出 `<Thinking>` 或 `<THINK>` 变体都能匹配，但也可能误匹配用户输入中的合法内容（尽管有代码 span 保护，但行内代码仍可能受影响）。

4. **Provider wrapper 的叠加顺序敏感**：多个 stream wrapper（Anthropic tool compat、OpenAI responses context、service tier 等）是链式调用的，顺序可能影响最终 payload。代码中没有显式验证 wrapper 组合的正确性。

### 6.3 如果要重新设计，可能会改变什么

1. **将流式状态机改为基于字符的 parser**：当前用正则 + 状态机处理跨 chunk 标签，对于更复杂的嵌套标签（如 `<think><final>...</final></think>`）难以正确处理。可以考虑用类似 SAX 的流式 parser。

2. **引入输出长度硬限制**：`deltaBuffer` 和 `blockBuffer` 应该有一个绝对上限（如 1MB），超过后强制 flush 或报错，防止恶意/异常输出导致 OOM。

3. **统一 tag stripping 和 reply directive parsing**：当前 `<think>`、`<final>`、MEDIA:、reply tags 是独立处理的，但它们本质都是"从 LLM 输出中提取结构化控制信息"。可以统一为一个声明式的 tag/指令解析框架。

4. **将 provider wrapper 改为编译时/配置时组合**：运行时链式 wrapper 虽然灵活，但增加了调试难度和性能开销（每次请求都经过多层函数包装）。可以考虑在启动时根据 provider 预编译一个专用的 stream function。

### 6.4 对我自己设计 Agent 系统的启示

> **不要信任 LLM provider 的流式输出格式，要在本地维护 ground truth 状态，并通过前缀比较、状态机、防御性重置等手段保证输出的单调性和一致性。**

> **工具结果是系统中最不可控的输入源之一，必须在进入核心循环前做严格的消毒（截断、脱敏、类型检查），否则一个异常大的工具返回就能拖垮整个 session。**

---

## 自检清单

- [x] 一个没看过代码的人，能否通过这篇报告理解"这个功能为什么存在"？
- [x] 源码片段是否都加了说明"这段代码为什么值得看"？
- [x] 是否有明确的"与其他维度的交互"图/表？
- [x] 最后是否有一句"对我自己设计 Agent 系统的启示"？
