# 维度名：上下文管理（Context Management）

## 1. 一句话定位

上下文管理是 OpenClaw 在 LLM 硬性上下文窗口约束下的"资源调度器"——它负责计量、预算、压缩、截断和守卫每一条进入模型视野的消息，确保 Agent 在长会话中不会因为 token 溢出而崩溃，同时最大限度保留对当前任务有用的信息。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有上下文管理机制，系统会在多个层面出现故障：

- **API 层面直接报错**：当消息总 token 数超过模型上下文窗口时，Anthropic/OpenAI 等提供商会返回 `400 context_length_exceeded` 错误，导致当前 turn 完全失败（`src/agents/pi-embedded-runner/run.ts` 中的重试逻辑会捕获这类错误，但根本问题未解决）。
- **工具结果淹没对话**：`cat` 一个大文件或执行 `grep -r` 可能产生数万 token 的工具结果。如果不加限制，这些结果会挤占用户消息和系统提示的空间，导致模型"忘记"当前任务目标。
- **长会话上下文丢失**：随着对话轮数增加，历史消息线性增长。没有 compaction，旧消息会不断累积，最终必然触顶。
- **Bootstrap 文件膨胀**：工作区中的 `README.md`、`CLAUDE.md` 等 bootstrap 文件如果过大，会在每次请求时重复消耗 token，造成隐性的上下文浪费。

### 2.2 OpenClaw 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 上下文窗口溢出检测 | `src/agents/pi-embedded-runner/run.ts` | 当 `session.isOverflow()` 返回 true 时触发 compaction |
| 工具结果超限 | `src/agents/pi-embedded-runner/tool-result-context-guard.ts` | 单个工具结果超过上下文预算的 50% 时截断 |
| Bootstrap 文件超预算 | `src/agents/bootstrap-budget.ts` | 注入的 bootstrap 文件超过 `bootstrapMaxChars` 或 `bootstrapTotalMaxChars` 时截断 |
| 模型上下文窗口配置 | `src/agents/context.ts` | 根据模型 ID 查找对应的上下文窗口大小 |
| 上下文窗口守卫告警 | `src/agents/context-window-guard.ts` | 当配置的上下文窗口小于 32K 时发出警告，小于 16K 时阻断运行 |

---

## 3. 核心设计思路

### 3.1 抽象模型

上下文管理可以被抽象为一个**多级漏斗过滤管道**：

```
原始消息流 → [Bootstrap 预算控制] → [历史消息限制] → [工具结果守卫] 
            → [上下文剪枝] → [Compaction 压缩] → [LLM 输入]
```

每一层都在不同粒度上对上下文进行裁剪，且**每一层都有明确的预算上限和降级策略**。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 上下文预算分层 | 分为 Bootstrap 预算、历史消息预算、工具结果预算、Compaction 预算四层独立控制 | 单一全局 token 预算 | `bootstrap-budget.ts` 独立计算 per-file 和 total 限制，`tool-result-context-guard.ts` 独立限制单个工具结果，说明作者认为不同来源的上下文需要不同策略 |
| Compaction 策略 | 用专门的 compaction agent 生成结构化摘要，支持分阶段摘要（multi-stage）和 fallback | 直接截断旧消息 | `compaction.ts:L17-30` 的 `MERGE_SUMMARIES_INSTRUCTIONS` 明确要求保留"Active tasks/Batch progress/Decisions/TODOs"，简单截断会丢失任务连续性 |
| 工具结果截断 | 保留头部和尾部（head+tail），中间用占位符替代 | 直接截断到固定长度 | `context-pruning/pruner.ts` 实现了 `takeHeadFromJoinedText` 和 `takeTailFromJoinedText`，说明作者认为工具结果的"开头和结尾"往往包含最关键信息（命令和退出状态） |
| 上下文窗口发现 | 运行时动态发现模型上下文窗口（通过模型注册表 + 用户配置），取最小值作为 fail-safe | 硬编码各模型窗口 | `context.ts:L46` 注释明确说明："prefer the smaller window so token budgeting is fail-safe" |

### 3.3 数据流/控制流

```
[配置加载] → context.ts 构建 MODEL_CACHE
                ↓
[Run 启动] → compact.ts 读取 sessionFile
                ↓
[Bootstrap 加载] → bootstrap-files.ts 加载工作区文件
                ↓
[Bootstrap 预算分析] → bootstrap-budget.ts 计算截断
                ↓
[工具结果守卫安装] → tool-result-context-guard.ts 拦截 transformContext
                ↓
[Agent Turn] → 消息进入 pi-coding-agent
                ↓
[溢出检测] → isOverflow() ? → compaction.ts 压缩历史
                ↓
[上下文剪枝] → context-pruning 清理过期工具结果
                ↓
[最终发送] → 构建 LLM 请求
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：自适应 Compaction（多阶段摘要）

**作用**：当历史消息超过上下文预算时，将其压缩为结构化摘要，而非简单丢弃。

**设计意图**：LLM 的上下文窗口是硬性上限，但旧消息中往往包含当前任务的关键状态（进行中的任务、已做出的决策、待办事项）。直接截断会导致 Agent"失忆"。OpenClaw 选择用**另一个 LLM 调用**来生成摘要，这样摘要本身可以利用 LLM 的理解能力，保留语义重要性高的信息。

**关键源码**（`src/agents/compaction.ts:L54-70`）：

```typescript
export function buildCompactionSummarizationInstructions(
  customInstructions?: string,
  instructions?: CompactionSummarizationInstructions,
): string | undefined {
  const custom = customInstructions?.trim();
  const identifierPreservation = resolveIdentifierPreservationInstructions(instructions);
  if (!identifierPreservation && !custom) {
    return undefined;
  }
  if (!custom) {
    return identifierPreservation;
  }
  if (!identifierPreservation) {
    return `Additional focus:\n${custom}`;
  }
  return `${identifierPreservation}\n\nAdditional focus:\n${custom}`;
}
```

这段代码体现了 compaction 的设计哲学：**保留标识符**（UUID、文件名、API key 等）是首要任务，因为这些东西无法从上下文中推断；其次是用户自定义的聚焦点。`IDENTIFIER_PRESERVATION_INSTRUCTIONS`（`L31-33`）明确要求"Preserve all opaque identifiers exactly as written"，因为摘要一旦丢失这些标识符，后续 Agent 就无法引用它们。

**关键源码**（`src/agents/compaction.ts:L264-331`）—— Progressive Fallback：

```typescript
export async function summarizeWithFallback(params: {
  // ...
}): Promise<string> {
  // Try full summarization first
  try {
    return await summarizeChunks(params);
  } catch (fullError) {
    log.warn(`Full summarization failed, trying partial: ...`);
  }

  // Fallback 1: Summarize only small messages, note oversized ones
  const smallMessages: AgentMessage[] = [];
  const oversizedNotes: string[] = [];

  for (const msg of messages) {
    if (isOversizedForSummary(msg, contextWindow)) {
      oversizedNotes.push(`[Large ${role} (~${Math.round(tokens / 1000)}K tokens) omitted from summary]`);
    } else {
      smallMessages.push(msg);
    }
  }
  // ... try partial summarization

  // Final fallback: Just note what was there
  return `Context contained ${messages.length} messages (${oversizedNotes.length} oversized). Summary unavailable due to size limits.`;
}
```

这段 fallback 链展示了作者对**失败 graceful degradation**的重视：全量摘要失败 → 跳过超大消息做部分摘要 → 最后连部分摘要也失败时，至少留下一条说明，让后续 Agent 知道"这里曾经有内容但被省略了"。这比静默丢失上下文要安全得多。

---

### 机制 B：工具结果上下文守卫

**作用**：在消息发往 LLM 之前，截断超长的工具结果，防止单次工具调用消耗过多上下文。

**设计意图**：工具结果（尤其是 `cat`/`grep`/`ls -R` 的输出）往往是上下文中的"大头"。与其等整个上下文溢出后再处理，不如在工具结果进入消息流时就进行 preemptive 截断。

**关键源码**（`src/agents/pi-embedded-runner/tool-result-context-guard.ts:L154-182`）：

```typescript
function enforceToolResultContextBudgetInPlace(params: {
  messages: AgentMessage[];
  contextBudgetChars: number;
  maxSingleToolResultChars: number;
}): void {
  const { messages, contextBudgetChars, maxSingleToolResultChars } = params;
  const estimateCache = createMessageCharEstimateCache();

  // Ensure each tool result has an upper bound before considering total context usage.
  for (const message of messages) {
    if (!isToolResultMessage(message)) {
      continue;
    }
    const truncated = truncateToolResultToChars(message, maxSingleToolResultChars, estimateCache);
    applyMessageMutationInPlace(message, truncated, estimateCache);
  }

  let currentChars = estimateContextChars(messages, estimateCache);
  if (currentChars <= contextBudgetChars) {
    return;
  }

  // Compact oldest tool outputs first until the context is back under budget.
  compactExistingToolResultsInPlace({
    messages,
    charsNeeded: currentChars - contextBudgetChars,
    cache: estimateCache,
  });
}
```

这里有两个层级：
1. **单结果上限**（`maxSingleToolResultChars`）：每个工具结果不超过上下文窗口的 50%（`L16: SINGLE_TOOL_RESULT_CONTEXT_SHARE = 0.5`）
2. **总量上限**（`contextBudgetChars`）：所有消息加起来不超过 75% 的上下文窗口（`L15: CONTEXT_INPUT_HEADROOM_RATIO = 0.75`），留出 25% 给系统提示词和用户输入

超过总量时，**从最旧的工具结果开始 compact**（替换为占位符），这是一种 LRU-like 的淘汰策略。

---

### 机制 C：Bootstrap 预算控制

**作用**：控制注入到系统提示词中的工作区文件（bootstrap files）的大小，防止它们占用过多上下文。

**设计意图**：`CLAUDE.md`、`README.md` 等文件可能很大（数千行）。如果不加限制，这些文件会在每次请求时重复消耗 token。Bootstrap 预算控制让这些文件的注入变得"可预测"。

**关键源码**（`src/agents/bootstrap-budget.ts:L164-221`）：

```typescript
export function analyzeBootstrapBudget(params: {
  files: BootstrapInjectionStat[];
  bootstrapMaxChars: number;
  bootstrapTotalMaxChars: number;
  nearLimitRatio?: number;
}): BootstrapBudgetAnalysis {
  const nearLimitRatio = /* ... default 0.85 */;
  const nonMissing = params.files.filter((file) => !file.missing);
  const rawChars = nonMissing.reduce((sum, file) => sum + file.rawChars, 0);
  const injectedChars = nonMissing.reduce((sum, file) => sum + file.injectedChars, 0);
  const totalNearLimit = injectedChars >= Math.ceil(bootstrapTotalMaxChars * nearLimitRatio);
  const totalOverLimit = injectedChars >= bootstrapTotalMaxChars;

  const files = params.files.map((file) => {
    // ... per-file limit check + total limit check
    const causes: BootstrapTruncationCause[] = [];
    if (file.truncated) {
      if (perFileOverLimit) causes.push("per-file-limit");
      if (totalOverLimit) causes.push("total-limit");
    }
    return { ...file, nearLimit, causes };
  });
  // ...
}
```

这里有两个限制维度：
- **per-file limit**（`bootstrapMaxChars`）：单个文件不超过此值
- **total limit**（`bootstrapTotalMaxChars`）：所有文件加起来不超过此值

截断原因被精确分类（`per-file-limit` vs `total-limit`），并生成可重复的签名（`buildBootstrapTruncationSignature`），用于去重警告——避免每次请求都重复提示用户相同的信息。

---

### 机制 D：上下文窗口守卫

**作用**：在配置层面阻止使用过小上下文窗口的模型运行，防止系统性失败。

**设计意图**：如果用户错误配置了一个上下文窗口只有 4K 的模型， compaction 和截断机制会频繁触发，导致体验极差且容易失败。守卫机制在启动时就拒绝这种配置。

**关键源码**（`src/agents/context-window-guard.ts:L57-74`）：

```typescript
export function evaluateContextWindowGuard(params: {
  info: ContextWindowInfo;
  warnBelowTokens?: number;
  hardMinTokens?: number;
}): ContextWindowGuardResult {
  const warnBelow = Math.max(1, Math.floor(params.warnBelowTokens ?? CONTEXT_WINDOW_WARN_BELOW_TOKENS));
  const hardMin = Math.max(1, Math.floor(params.hardMinTokens ?? CONTEXT_WINDOW_HARD_MIN_TOKENS));
  const tokens = Math.max(0, Math.floor(params.info.tokens));
  return {
    ...params.info,
    tokens,
    shouldWarn: tokens > 0 && tokens < warnBelow,
    shouldBlock: tokens > 0 && tokens < hardMin,
  };
}
```

阈值设定：
- **警告阈值**：32K（`CONTEXT_WINDOW_WARN_BELOW_TOKENS`）——低于此值会警告但允许运行
- **硬阻断阈值**：16K（`CONTEXT_WINDOW_HARD_MIN_TOKENS`）——低于此值直接阻断

这两个阈值的存在说明作者认为：**16K 是 OpenClaw 正常运行的绝对下限**，低于此值系统行为不可预测。

---

## 5. 与其他维度的交互

```
[上下文管理] --(提供上下文预算)--> [编排循环]
[上下文管理] --(Compaction 触发)--> [记忆系统]
[上下文管理] --(工具结果截断)--> [工具系统]
[上下文管理] --(Bootstrap 文件加载)--> [Prompt 构建]
[上下文管理] <--(会话历史)-- [状态管理]
[上下文管理] <--(模型配置)-- [初始化与环境]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环 | 通过 `isOverflow()` 触发 compaction，决定是否需要重试 turn | `pi-embedded-runner/run.ts` |
| 输出到 | 记忆系统 | Compaction 生成的摘要存储到 session，成为"长期记忆"的一部分 | `compact.ts` 的 `result.summary` |
| 输出到 | 工具系统 | 工具结果被截断后进入 LLM，影响模型对工具输出的理解 | `tool-result-context-guard.ts` |
| 输出到 | Prompt 构建 | Bootstrap 文件内容注入到 system prompt | `bootstrap-files.ts` + `system-prompt.ts` |
| 依赖 | 状态管理 | 从 session file 读取历史消息，compact 后写回 | `compact.ts` 的 `SessionManager.open` |
| 依赖 | 初始化与环境 | 模型上下文窗口从配置和模型注册表动态解析 | `context.ts` 的 `lookupContextTokens` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"工具结果是可以牺牲的"**：`tool-result-context-guard.ts` 将工具结果视为最容易截断的目标，因为工具结果通常可以从重新执行工具恢复。而用户消息和系统提示更难恢复。
2. **"Compaction 的质量足够高"**：系统假设用一个 LLM 调用生成的摘要，其信息密度高于原始消息。如果 compaction 质量差，Agent 会"失忆"导致任务失败。
3. **"标识符比自然语言描述更重要"**：`IDENTIFIER_PRESERVATION_INSTRUCTIONS` 的优先级高于其他指令，说明作者认为 UUID/文件名等机器标识符是后续操作的关键引用点。

### 6.2 这个设计的代价/风险

1. **Compaction 的延迟成本**：每次 compaction 都是一次额外的 LLM API 调用，在慢速 provider 上可能导致明显的卡顿。代码中 `EMBEDDED_COMPACTION_TIMEOUT_MS` 和 `compaction-safety-timeout.ts` 的存在说明作者已经意识到这个问题并加了超时保护。
2. **估算误差**：token 估算使用 `chars/4` 的启发式（`CHARS_PER_TOKEN_ESTIMATE = 4`），对中文、代码、特殊字符会系统性低估。`SAFETY_MARGIN = 1.2`（20% buffer）是对这种误差的补偿，但仍有越界风险。
3. **复杂的多层交互**：Bootstrap 预算、工具结果守卫、上下文剪枝、Compaction 四层机制各自独立运作，可能在某些边界条件下产生意想不到的交互（例如工具结果守卫截断了 compaction 需要的内容）。

### 6.3 如果要重新设计，可能会改变什么

1. **统一 token 估算**：目前有多套估算逻辑（`compaction.ts` 的 `estimateTokens`、`tool-result-context-guard.ts` 的 `estimateContextChars`、`bootstrap-budget.ts` 的字符计数），如果能接入统一的 tokenizer（如 tiktoken），预算控制会更精确。
2. **Compaction 的增量策略**：当前 compaction 是对整个历史做摘要，如果改为"增量摘要"（只对新消息做摘要然后合并），可以减少重复计算。
3. **工具结果的 lazy loading**：与其在每次请求时携带完整的工具结果，不如只在模型需要引用时才加载，类似虚拟内存的按需分页。

### 6.4 对我自己设计 Agent 系统的启示

> **上下文管理不是"截断策略"，而是"信息优先级分层策略"**。OpenClaw 的设计启示是：不要把所有消息一视同仁，而是明确不同来源的信息有不同的恢复成本和保留价值——用户消息最珍贵（不可恢复），工具结果次之（可重新执行），系统提示可以重复注入。在这个优先级框架下做预算分配，比简单的"截旧留新"要可靠得多。
