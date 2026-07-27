# 维度名：记忆系统（Memory System）

## 1. 一句话定位

OpenClaw 的记忆系统是一套**以 Markdown 文件为唯一事实来源、SQLite 为索引载体、混合检索为召回手段**的长期记忆基础设施，它让 Agent 在跨会话场景中能够"记住"用户偏好、历史决策和项目上下文，同时在单次会话内通过上下文压缩与剪枝来适配 LLM 的有限上下文窗口。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有记忆系统，Agent 将面临三重失效：

1. **跨会话失忆**：每次新会话都是一张白纸。用户上周说"用 pnpm 而不是 npm"，本周 Agent 仍会默认用 npm，因为 `MEMORY.md` 不存在、也没有检索机制。代码中 `memory_search` 工具被设计为"Mandatory recall step"（`src/agents/tools/memory-tool.ts:L53`），正是因为没有它 Agent 无法知道"之前发生了什么"。

2. **上下文溢出导致循环崩溃**：当会话消息累积超过模型上下文窗口时，如果不做 compaction，LLM API 会直接返回 `context_length_exceeded` 错误。`compaction.ts` 中的 `pruneHistoryForContextShare`（`L398-460`）通过迭代丢弃旧消息块来避免这一点；如果没有它，超出窗口的消息会直接触发 API 报错，打断整个 Agent 循环。

3. **工具结果膨胀淹没有效信号**：Agent 调用 `cat` 读取大文件、`grep` 搜索代码库时，tool result 往往包含数万字符的冗余输出。如果不做上下文剪枝（context pruning），这些结果会快速占满上下文窗口，挤占 system prompt 和用户指令的空间。`pruner.ts` 的 `softTrim` 和 `hardClear` 两级机制（`L188-343`）专门解决这一问题。

### 2.2 OpenClaw 的具体触发条件

| 机制 | 触发条件 | 代码位置 |
|------|---------|---------|
| 记忆索引同步 | 文件 watcher 检测到 `MEMORY.md` 或 `memory/*.md` 变更（debounce 1500ms） | `manager-sync-ops.ts:L403-409` |
| 记忆索引同步 | 会话启动时 `warmSession` 触发首次 sync | `manager.ts:L240-254` |
| 记忆索引同步 | 搜索时若 `dirty === true` 则触发 sync | `manager.ts:L265-269` |
| 会话转录索引 | 会话转录文件增量超过 `deltaBytes`（默认 100KB）或 `deltaMessages`（默认 50 条） | `manager-sync-ops.ts:L441-477` |
| 上下文压缩（compaction） | 当 `estimateMessagesTokens(messages) > contextWindow * maxHistoryShare` 时 | `compaction.ts:L422` |
| 上下文剪枝（pruning） | 当 `totalChars / charWindow >= softTrimRatio`（默认 0.3）时先软裁剪；若仍 `>= hardClearRatio`（默认 0.5）则硬清空 | `pruner.ts:L262-303` |
| 自动记忆 flush | 当会话接近 compaction 阈值时触发 silent agentic turn，提醒模型写 durable memory | `docs/concepts/memory.md:L52-58` |

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────────────────────────────────────────────────┐
│                    记忆系统三层架构                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 事实层（Source of Truth）                           │
│    - MEMORY.md, memory/*.md, memory/YYYY-MM-DD.md            │
│    - 纯文本 Markdown，人可读、可版本控制、可手动编辑            │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 索引层（Index）                                     │
│    - per-agent SQLite: ~/.openclaw/memory/<agentId>.sqlite   │
│    - chunks 表: 文本块 + 序列化 embedding                     │
│    - chunks_vec 虚拟表: sqlite-vec 加速向量检索               │
│    - chunks_fts 虚拟表: FTS5 全文检索                         │
│    - embedding_cache 表: 按 hash 去重缓存                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 召回层（Retrieval）                                 │
│    - Hybrid: vectorScore * 0.7 + textScore * 0.3             │
│    - Optional MMR 多样性重排                                  │
│    - Optional Temporal Decay 时间衰减                         │
│    - FTS-only 降级模式（无 embedding provider 时）            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **存储格式** | Markdown 文件作为唯一事实来源，SQLite 仅作索引 | 直接用数据库存储记忆内容 | `docs/concepts/memory.md:L11` 明确说"The files are the source of truth; the model only 'remembers' what gets written to disk." 这样保证了可移植性、可版本控制和人工干预能力 |
| **索引策略** | 混合搜索（向量相似度 + BM25 关键词），可降级为 FTS-only | 纯向量搜索 或 纯关键词搜索 | `manager.ts:L282-364` 的搜索逻辑显示：无 provider 时自动降级到 FTS；有 provider 时默认 hybrid（`DEFAULT_HYBRID_ENABLED = true`）。这是因为向量对语义匹配强但对精确 ID/符号弱，BM25 互补 |
| **Embedding 降级** | 当 API key 缺失或 provider 失败时，自动降级到 FTS-only 或 fallback provider，而不是抛错终止 | 硬失败，要求用户必须配置 embedding provider | `embeddings.ts:L230-238`：auto 模式下所有 remote provider 都因 missing API key 失败时，返回 `provider: null` 并进入 FTS-only。`search-manager.ts:L53-75` 的 `FallbackMemoryManager` 进一步在 QMD 失败时回退到 builtin |
| **同步原子性** | 全量重索引时先写到 temp DB，再原子 swap，失败可回滚 | 直接在当前 DB 上 DELETE + INSERT | `manager-sync-ops.ts:L1017-1124` 的 `runSafeReindex` 实现了完整的 temp-db + backup + swap 流程，避免索引过程中搜索拿到半完成状态 |
| **上下文压缩** | 用专门的 summarization agent 生成结构化摘要，而非简单截断 | 直接丢弃旧消息 | `compaction.ts:L211-258` 的 `summarizeChunks` 调用 `generateSummary`，且 `MERGE_SUMMARIES_INSTRUCTIONS`（`L17-30`）明确要求保留任务状态、决策理由、TODO 等结构化信息，简单截断会丢失这些 |

### 3.3 数据流/控制流

```
用户对话 → 产生消息 → 会话转录写入 JSONL
                ↓
        [上下文剪枝] ←── 若 tool result 过长
                ↓
        [上下文压缩] ←── 若总 token 超过预算
                ↓
        LLM 推理 → 可能调用 memory_search / memory_get
                ↓
        若接近 compaction 阈值 → [自动 memory flush]
                ↓
        Agent 可能写入 memory/YYYY-MM-DD.md
                ↓
        文件 watcher 标记 dirty → 后台 sync 重建索引
                ↓
        下次 memory_search 使用新索引
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：混合搜索（Hybrid Search）

**作用**：结合向量语义相似度和 BM25 关键词匹配，兼顾"同义不同词"和"精确符号匹配"两类查询。

**设计意图**：为什么不是单一检索方式？因为代码中明确注释了——向量搜索对 "Mac Studio gateway host" vs "the machine running the gateway" 很强，但对 IDs (`a828e60`)、代码符号 (`memorySearch.query.hybrid`)、错误字符串很弱（`docs/concepts/memory.md:L410-421`）。BM25 正好相反。

**关键源码**（`src/memory/manager.ts:282-364`）：
```typescript
// ① 无 provider 时降级到 FTS-only（提取关键词增强匹配）
if (!this.provider) {
  const keywords = extractKeywords(cleaned);  // "that thing about API" → ["discussed", "API"]
  const resultSets = await Promise.all(
    searchTerms.map((term) => this.searchKeyword(term, candidates).catch(() => []))
  );
  // merge & dedupe by highest score
}

// ② 有 provider 时并行执行 vector + keyword
const keywordResults = hybrid.enabled && this.fts.available
  ? await this.searchKeyword(cleaned, candidates).catch(() => [])
  : [];
const queryVec = await this.embedQueryWithTimeout(cleaned);
const vectorResults = hasVector
  ? await this.searchVector(queryVec, candidates).catch(() => [])
  : [];

// ③ 合并后若 strict filter 无结果，relax minScore 保留纯 keyword hit
const strict = merged.filter((entry) => entry.score >= minScore);
if (strict.length > 0 || keywordResults.length === 0) {
  return strict.slice(0, maxResults);
}
const relaxedMinScore = Math.min(minScore, hybrid.textWeight);
return merged.filter(...keyword match...).slice(0, maxResults);
```

这里第三个分支（`L343-363`）是一个精妙的边界处理：当 `minScore=0.35` 而 `textWeight=0.3` 时，纯 keyword 匹配的最高分就是 0.3，会被过滤掉。代码检测到这种情况后主动降低阈值，确保纯文本命中不被误杀。

---

### 机制 B：MMR 多样性重排

**作用**：在混合搜索后，用 Maximal Marginal Relevance 平衡相关性与多样性，避免返回 5 个几乎相同的 daily note 片段。

**设计意图**：为什么用 Jaccard 而不是余弦相似度？因为 MMR 只需要一个快速的"内容是否重复"的度量，Jaccard 在 token 集合上计算，不需要重新调用 embedding 模型，成本极低。且 snippet 长度有限（~700 chars），Jaccard 足够有效。

**关键源码**（`src/memory/mmr.ts:116-183`）：
```typescript
export function mmrRerank<T extends MMRItem>(items: T[], config: Partial<MMRConfig> = {}): T[] {
  // ① 预 tokenize 所有 item，避免重复计算
  const tokenCache = new Map<string, Set<string>>();
  for (const item of items) {
    tokenCache.set(item.id, tokenize(item.content));
  }
  // ② 分数归一化到 [0,1]，保证与 similarity 同量纲
  const normalizeScore = (score: number): number => {
    if (scoreRange === 0) return 1;
    return (score - minScore) / scoreRange;
  };
  // ③ 贪心迭代：每次选 MMR 分最高的
  while (remaining.size > 0) {
    for (const candidate of remaining) {
      const normalizedRelevance = normalizeScore(candidate.score);
      const maxSim = maxSimilarityToSelected(candidate, selected, tokenCache);
      const mmrScore = computeMMRScore(normalizedRelevance, maxSim, clampedLambda);
      // lambda=0.7: 70% relevance + 30% diversity penalty
    }
    selected.push(bestItem);
    remaining.delete(bestItem);
  }
}
```

---

### 机制 C：时间衰减（Temporal Decay）

**作用**：让 dated daily notes 随时间自然降权，避免半年前的笔记因语义匹配度高而压过昨天的更新。

**设计意图**：为什么只对 dated file 生效？因为 `MEMORY.md` 和 `memory/projects.md` 这类 evergreen 知识是" durable reference information that should always rank normally"（`docs/concepts/memory.md:L542`）。代码通过正则 `DATED_MEMORY_PATH_RE = /(?:^|\/)memory\/(\d{4})-(\d{2})-(\d{2})\.md$/` 识别日期文件，其他文件返回 `null` timestamp 从而跳过衰减。

**关键源码**（`src/memory/temporal-decay.ts:121-167`）：
```typescript
export async function applyTemporalDecayToHybridResults<T extends { path: string; score: number; source: string }>(
  params: { results: T[]; temporalDecay?: Partial<TemporalDecayConfig>; workspaceDir?: string; nowMs?: number }
): Promise<T[]> {
  const timestampPromiseCache = new Map<string, Promise<Date | null>>();
  return Promise.all(
    params.results.map(async (entry) => {
      const cacheKey = `${entry.source}:${entry.path}`;
      let timestampPromise = timestampPromiseCache.get(cacheKey);
      if (!timestampPromise) {
        timestampPromise = extractTimestamp({ filePath: entry.path, source: entry.source, workspaceDir: params.workspaceDir });
        timestampPromiseCache.set(cacheKey, timestampPromise);
      }
      const timestamp = await timestampPromise;
      if (!timestamp) {
        return entry; // evergreen: no decay
      }
      const decayedScore = applyTemporalDecayToScore({
        score: entry.score,
        ageInDays: ageInDaysFromTimestamp(timestamp, nowMs),
        halfLifeDays: config.halfLifeDays,
      });
      return { ...entry, score: decayedScore };
    })
  );
}
```

注意 `timestampPromiseCache` 的设计：同一个文件的多条 chunk 结果只计算一次 timestamp，避免重复 IO。

---

### 机制 D：会话压缩（Compaction）

**作用**：当历史消息 token 数超过预算时，将旧消息压缩成结构化摘要，释放上下文窗口。

**设计意图**：为什么不用简单截断？因为截断会丢失 tool_use/tool_result 配对（导致 Anthropic API 报错），且会丢失关键上下文。代码中 `repairToolUseResultPairing`（`compaction.ts:L434`）专门修复被截断后的孤儿 tool_result。此外，用 agent 生成摘要可以保留"Active tasks / Decisions / TODOs"等结构化信息（`L17-30`）。

**关键源码**（`src/agents/compaction.ts:333-396`）：
```typescript
export async function summarizeInStages(params: { ... }): Promise<string> {
  const { messages } = params;
  const parts = normalizeParts(params.parts ?? DEFAULT_PARTS, messages.length);
  const totalTokens = estimateMessagesTokens(messages);
  // ① 消息不够多或总 token 没超预算，直接单阶段摘要
  if (parts <= 1 || messages.length < minMessagesForSplit || totalTokens <= params.maxChunkTokens) {
    return summarizeWithFallback(params);
  }
  // ② 分块并行摘要
  const splits = splitMessagesByTokenShare(messages, parts).filter((chunk) => chunk.length > 0);
  const partialSummaries: string[] = [];
  for (const chunk of splits) {
    partialSummaries.push(await summarizeWithFallback({ ...params, messages: chunk, previousSummary: undefined }));
  }
  // ③ 用专门的 merge instructions 合并多份摘要
  const summaryMessages: AgentMessage[] = partialSummaries.map((summary) => ({
    role: "user", content: summary, timestamp: Date.now(),
  }));
  return summarizeWithFallback({ ...params, messages: summaryMessages, customInstructions: mergeInstructions });
}
```

---

### 机制 E：上下文剪枝（Context Pruning）

**作用**：在不丢弃完整消息的前提下，缩短 tool result 的文本长度，为 system prompt 和用户指令腾出空间。

**设计意图**：为什么是 tool result 而不是 assistant message？因为 tool result 往往是"冗长的外部数据"（如 `cat` 大文件、`ls -R` 输出），而 assistant message 包含推理过程和决策，更不可丢弃。代码通过 `isToolPrunable`（`tools.ts:L10-26`）按 glob 规则控制哪些工具的 result 可裁剪。

**关键源码**（`src/agents/pi-extensions/context-pruning/pruner.ts:188-221`）：
```typescript
function softTrimToolResultMessage(params: { msg: ToolResultMessage; settings: EffectiveContextPruningSettings }): ToolResultMessage | null {
  // ① 跳过含图片的 tool result（难安全裁剪）
  if (hasImageBlocks(msg.content)) {
    return null;
  }
  const parts = collectTextSegments(msg.content);
  const rawLen = estimateJoinedTextLength(parts);
  // ② 不够长就不裁剪
  if (rawLen <= settings.softTrim.maxChars) {
    return null;
  }
  // ③ 保留 head + tail，中间用 "..." 替换
  const head = takeHeadFromJoinedText(parts, headChars);
  const tail = takeTailFromJoinedText(parts, tailChars);
  const trimmed = `${head}\n...\n${tail}`;
  const note = `\n\n[Tool result trimmed: kept first ${headChars} chars and last ${tailChars} chars of ${rawLen} chars.]`;
  return { ...msg, content: [asText(trimmed + note)] };
}
```

保留 head + tail 的设计很巧妙：大多数文件的前几行是 import/声明，后几行是结论/错误信息，中间往往是重复内容。

---

### 机制 F：Embedding Provider 的弹性架构

**作用**：支持 6 种 embedding provider（openai/gemini/voyage/mistral/ollama/local），具备 auto-select、fallback、FTS-only 降级三重弹性。

**设计意图**：为什么 Ollama 被排除在 auto-select 之外？因为 `REMOTE_EMBEDDING_PROVIDER_IDS`（`embeddings.ts:L47`）明确排除了 ollama——"auto mode does not implicitly assume a local Ollama instance is available"。这避免了用户未启动 Ollama 服务时产生 confusing 的错误。

**关键源码**（`src/memory/embeddings.ts:166-286`）：
```typescript
export async function createEmbeddingProvider(options: EmbeddingProviderOptions): Promise<EmbeddingProviderResult> {
  if (requestedProvider === "auto") {
    // ① 优先 local（如果 modelPath 存在且是本地文件）
    if (canAutoSelectLocal(options)) {
      try { return { ...await createProvider("local"), requestedProvider }; }
      catch (err) { localError = formatLocalSetupError(err); }
    }
    // ② 按顺序尝试 remote providers
    for (const provider of REMOTE_EMBEDDING_PROVIDER_IDS) {
      try { return { ...await createProvider(provider), requestedProvider }; }
      catch (err) {
        if (isMissingApiKeyError(err)) { missingKeyErrors.push(message); continue; }
        throw wrapped; // 非认证错误直接抛，不静默吞掉
      }
    }
    // ③ 全部因缺 API key 失败 → 返回 null provider，进入 FTS-only
    return { provider: null, requestedProvider, providerUnavailableReason: reason };
  }
  // ④ 指定 provider 失败时尝试 fallback
  try { ... }
  catch (primaryErr) {
    if (fallback && fallback !== "none") {
      try { return { ...fallbackResult, fallbackFrom: requestedProvider, fallbackReason: reason }; }
      catch (fallbackErr) { ... }
    }
  }
}
```

---

### 机制 G：QMD 后端与 FallbackMemoryManager

**作用**：支持将内置 SQLite 索引替换为外部 QMD（Query My Data）sidecar，提供更强大的 BM25+向量+rerank 能力；当 QMD 失败时自动回退到内置索引。

**设计意图**：为什么用 wrapper 模式而不是直接替换？因为 QMD 是一个外部进程（Bun + sqlite），可能因二进制缺失、模型下载失败、平台不兼容等原因不可用。`FallbackMemoryManager`（`search-manager.ts:L104-246`）在第一次调用失败后就标记 `primaryFailed = true`，后续所有操作走 fallback，同时 evict cache 让下次请求有机会重试 QMD。

**关键源码**（`src/memory/search-manager.ts:118-139`）：
```typescript
async search(query: string, opts?: { maxResults?: number; minScore?: number; sessionKey?: string }) {
  if (!this.primaryFailed) {
    try {
      return await this.deps.primary.search(query, opts);
    } catch (err) {
      this.primaryFailed = true;
      this.lastError = err instanceof Error ? err.message : String(err);
      log.warn(`qmd memory failed; switching to builtin index: ${this.lastError}`);
      await this.deps.primary.close?.().catch(() => {});
      this.evictCacheEntry(); // 让下次有机会重试 QMD
    }
  }
  const fallback = await this.ensureFallback();
  if (fallback) {
    return await fallback.search(query, opts);
  }
  throw new Error(this.lastError ?? "memory search unavailable");
}
```

---

## 5. 与其他维度的交互

```
[记忆系统] --(memory_search / memory_get 结果)--> [工具系统]
[记忆系统] --(索引后的 session transcripts)--> [会话系统]
[记忆系统] <--(会话转录更新事件)-- [会话系统]
[记忆系统] <--(agent 写入 memory/*.md)-- [Agent 执行循环]
[记忆系统] <--(compaction 前的 memory flush 提醒)-- [上下文管理]
[上下文剪枝] --(裁剪后的 messages)--> [LLM 调用]
[上下文压缩] --(结构化摘要)--> [LLM 调用]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 工具系统 | `memory_search` 返回 snippet + path + line range；`memory_get` 返回精确文本 | `src/agents/tools/memory-tool.ts:L55-97` |
| 输出到 | Agent 循环 | 自动 memory flush 在 compaction 前提醒 Agent 写 durable memory | `docs/concepts/memory.md:L52-58` |
| 依赖 | 会话系统 | 监听 `onSessionTranscriptUpdate` 事件，增量索引会话历史 | `manager-sync-ops.ts:L412-426` |
| 依赖 | 配置系统 | `resolveMemorySearchConfig` 解析 per-agent 的 memorySearch 配置 | `src/agents/memory-search.ts:L355-366` |
| 依赖 | Embedding 服务 | `createEmbeddingProvider` 创建可降级、可 fallback 的 provider | `src/memory/embeddings.ts:L166` |
| 交互 | 上下文管理 | `pruneContextMessages` 在发送给 LLM 前裁剪 tool result | `src/agents/pi-extensions/context-pruning/pruner.ts:L223-344` |
| 交互 | 上下文管理 | `summarizeInStages` 在上下文溢出时生成摘要替代旧消息 | `src/agents/compaction.ts:L333-396` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **Markdown 是足够好的记忆格式**：作者假设用户（和 Agent）都能以 Markdown 形式有效组织记忆，不需要结构化 schema 或数据库。这牺牲了强类型查询能力，换来了极大的灵活性和可移植性。

2. **Embedding 质量足够高，但 API 不可靠**：整个 provider 架构（auto-select、fallback、FTS-only、batch failure lock）都建立在"embedding 服务可能随时不可用"的假设上。代码中甚至为 readonly DB error 做了专门恢复（`manager.ts:L468-551`）。

3. **用户查询往往是 conversational，不是 keyword-perfect**：`query-expansion.ts` 中花了大量代码处理多语言 stop words（英/西/葡/阿/韩/日/中），并提取关键词做 FTS 增强。这说明作者假设用户不会输入精确的关键词查询。

### 6.2 这个设计的代价/风险

1. **SQLite 单点瓶颈**：per-agent 的 SQLite 文件在并发访问时可能成为瓶颈。`openDatabaseAtPath` 中设置了 `PRAGMA busy_timeout = 5000`（`manager-sync-ops.ts:L265`），但如果 gateway 是多进程架构，这个 timeout 可能不够。

2. **Embedding cache 的无限增长**：虽然可以配置 `maxEntries`，但默认未设置上限。且 cache key 包含 `provider_key`（含 endpoint fingerprint），换 endpoint 会导致 cache 失效但旧记录不会自动清理。

3. **FTS-only 模式下的召回质量**：`extractKeywords` 对中文只做字级和双字级切分（`query-expansion.ts:L696-705`），没有真正的分词，对长词组合可能效果不佳。

4. **Context pruning 的 image 盲区**：`softTrimToolResultMessage` 直接跳过含图片的 tool result（`pruner.ts:L194`），这意味着图片密集型会话（如视觉分析）的上下文膨胀问题未被解决。

### 6.3 如果要重新设计，可能会改变什么

1. **将 FTS-only 的 query expansion 升级为轻量 LLM 扩展**：代码中已预留了 `LlmQueryExpander` 接口（`query-expansion.ts:L786-810`），但实际未在 memory search 中接入。如果本地有小模型，可以用它做 query understanding，提升 FTS-only 召回率。

2. **引入分层记忆**：当前所有记忆在一个平面索引中。可以借鉴 `memory-lancedb` 插件的 `category`（preference/decision/entity/fact）概念，在 builtin 索引中也加入标签，让 Agent 按需检索特定类型记忆。

3. **Context pruning 的 image 处理**：当前直接跳过。可以考虑对图片做 base64 长度截断，或者将图片转换为更紧凑的描述文本。

4. **Compaction 的摘要持久化**：当前摘要只存在于内存中的 messages 数组。如果 compaction 后进程崩溃，摘要丢失。可以考虑将摘要也写入 `memory/YYYY-MM-DD.md` 或 session 转录中。

### 6.4 对我自己设计 Agent 系统的启示

最核心的启示是：**记忆系统必须设计为"优雅降级"的弹性架构**。OpenClaw 没有假设 embedding API 永远可用，而是构建了从 "hybrid search → vector-only → FTS-only → 完全不可用" 的多级降级链条，每一级都能给出合理结果而非直接抛错。这种"防御性设计"比追求单一最优方案更适合生产环境。

其次是**"文件即事实来源"的哲学**：用 Markdown 而非数据库作为唯一事实来源，虽然损失了查询灵活性，但获得了版本控制、人工编辑、跨工具互操作三大优势。对于需要长期维护的 Agent 系统，这种"对人友好"的设计往往比"对机器最优"的设计更有生命力。
