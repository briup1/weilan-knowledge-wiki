# 维度 08 — 错误处理（Error Handling）

> 源码基线：`agent/error_classifier.py`、`agent/retry_utils.py`、`run_agent.py`、`model_tools.py`、`agent/display.py`、`agent/nous_rate_guard.py`、`agent/rate_limit_tracker.py`、`agent/auxiliary_client.py`

---

## 1. 一句话定位

错误处理维度是 Hermes Agent **在多供应商、多协议、多瞬时故障的真实生产环境中保持「不崩溃、不空转、不放大故障」**的中枢：它把所有异常（HTTP 错误、传输层抖动、工具崩溃、模型协议级错误）归一到一个**结构化分类器**上，再由**主循环**根据分类结果选择「重试 / 退避 / 轮换凭证 / 切换 Provider / 压缩上下文 / 修补请求 / 中止」六类恢复动作。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

基于代码反推，缺失任何一层都会触发具体故障：

| 缺失层 | 触发的具体故障 |
|---|---|
| **结构化分类** | `run_agent.py:12404` 之前的版本只有散落 `if "rate limit" in str(e)` 检查，会把「OpenRouter 把 Anthropic 错误用 metadata.raw 嵌套包装」的内层 `context length exceeded` 误归为通用 5xx，触发无意义的指数退避 + fallback 而不是压缩上下文（`error_classifier.py:381-411` 的 metadata.raw 解析就是为这种 case 写的） |
| **402 歧义消解** | 把所有 402 当成「账单耗尽」直接轮换凭证，会让「Usage limit, try again in 5 minutes」这种**周期性配额**也被错误地当作硬性破产，轮换走刚刚被周期性限流的 key（`error_classifier.py:_classify_402` 698-724） |
| **断流 + 大会话 → 上下文溢出**推导 | API gateway 对超大请求**直接断 TCP**而不返回 413，没有这条规则 `RemoteProtocolError` 会一直被识别为 timeout 重试，每次重试都因为同样的大上下文再次断流（`error_classifier.py:541-561`） |
| **单工具失败不终止主循环** | 一个 `terminal` 工具 `RuntimeError` 会让整轮对话崩溃，session 失去后续 N 次 turn 的累计成果。`run_agent.py:9965-9967` 的捕获把异常**降级为 tool 消息内容**，模型可以基于 "Error executing tool ..." 自行规划下一步 |
| **退避抖动** | 多个 session 同时被 429，没有 jitter 的指数退避会让所有 session 在同一秒重试，造成 thundering herd（`retry_utils.py:38-57`） |
| **跨进程 Nous 限流广播** | 一个 429 触发 9 次 SDK+Hermes 重试，每次都消耗 RPH，5 个 session 并发会把 RPH 池打爆。`agent/nous_rate_guard.py` 用文件级共享状态阻断（`run_agent.py:12810-12850`） |
| **assistant.tool_calls 缺 tool 应答** | 外层 except 不补齐 tool 消息，下次 API 调用会因 OpenAI / Anthropic 协议要求"每个 tool_call_id 必须有对应 role=tool 消息"被强制 400，整个 session 卡死（`run_agent.py:14163-14188`） |

### 2.2 具体触发条件（代码中的判断逻辑）

**异常入口 → 分类器入口**（`run_agent.py:12404`）：
```python
classified = classify_api_error(
    api_error,
    provider=getattr(self, "provider", "") or "",
    model=getattr(self, "model", "") or "",
    approx_tokens=approx_tokens,
    context_length=_ctx_len,
    num_messages=len(api_messages) if api_messages else 0,
)
```
分类器是**纯函数**，不修改状态，所有恢复动作由调用方依据 `ClassifiedError` 字段决定。

**触发分类的几个真实条件**：
- `api_error.status_code == 429` 且 message 含 "extra usage" + "long context" → `long_context_tier`（Anthropic 1M 阶梯门票）
- `status_code == 400` 且 message 含 "exceeds the max_model_len" → `context_overflow`（vLLM）
- 无 status_code 且异常类型是 `ReadTimeout/ConnectError/SSLError/...` → `timeout`
- 无 status_code 且 message 含 "server disconnected" 且 `approx_tokens > context_length * 0.6` → `context_overflow`（API gateway 对超大包的 silent drop）
- message 含 `"signature"` 且 `"thinking"` → `thinking_signature`（Anthropic thinking block 签名失效）

---

## 3. 核心设计思路

### 3.1 抽象模型

```text
classify_api_error(error, provider, model, approx_tokens, context_length, num_messages)
    ─→ ClassifiedError {
          reason:                   FailoverReason  # 分类标签
          status_code:              int | None
          retryable:                bool             # 是否值得直接重试
          should_compress:          bool             # 是否需要压缩上下文
          should_rotate_credential: bool             # 是否需要轮换凭证
          should_fallback:          bool             # 是否需要切换 Provider
          message:                  str              # 给用户看的清洗后字符串
       }

main_retry_loop():
    while retry_count < max_retries:
        try:
            response = api_call()
        except Exception as api_error:
            classified = classify_api_error(api_error, ...)

            # 优先级降级阶梯（同一个错误最多走一条）
            if pool_can_recover(classified): rotate_credential();   continue
            if image_too_large:              shrink_images();       continue
            if oauth_1m_beta_forbidden:      disable_beta_rebuild();continue
            if codex/nous/anthropic 401:     refresh_token();       continue
            if thinking_signature:           strip_reasoning();     continue
            if llama_cpp_grammar:            strip_pattern();       continue
            if long_context_tier:            reduce_ctx + compress();continue
            if rate_limited and chain_has_fallback: switch_provider();continue
            if payload_too_large:            compress();            continue
            if context_overflow:             compress();            continue
            if not retryable:                try_fallback() or abort
            wait(jittered_backoff(retry_count)); retry_count += 1
```

关键抽象：**分类器只做"这是什么错"的判断，不做"该怎么修"的决策**。恢复策略全部留给调用方根据上下文（已经 retry 几次、是否 fallback 已激活、credential pool 状态）综合判断。

### 3.2 关键设计决策

| 决策 | 选了什么 | 放弃了什么 | 代码位置 |
|---|---|---|---|
| **分类器结构** | 单一纯函数 + 优先级流水线（provider-specific → status_code → error_code → message → transport heuristic → unknown） | 没有用「每 provider 一个 plugin」式可扩展架构 | `error_classifier.py:331-570` |
| **retryable 字段语义** | `retryable=False` 表示"不要直接重试，但可能可以恢复"（凭证轮换 / fallback 仍然要试），不是"立即死" | 没有把 retryable / abort / recoverable 拆成三态枚举 | `error_classifier.py:596-601`（401 是 retryable=False 但 should_rotate=True） |
| **错误归并阈值用比例而非常数** | `approx_tokens > context_length * 0.4`，让 1M 与 32K 模型共用一套判断 | 放弃绝对阈值，但在 `context_length <= 256000` 时回退到绝对阈值（80k/200msg）作 OR 兜底 | `error_classifier.py:551-554, 803-805` |
| **单工具失败 → 降级为 tool 消息字符串** | 把 `_invoke_tool` / `handle_function_call` 抛出的异常**就地转成 `"Error executing tool '{name}': {e}"`** 写回 `result`，让模型继续推进 | 放弃了"工具失败立即终止 turn"的强一致语义；放弃了用户中断信号能立即冒泡 | `run_agent.py:9965-9967, 10448-10450, 10467-10469` |
| **退避用 jittered backoff 而非 fixed** | `min(base * 2^(n-1), max) + uniform(0, 0.5*delay)` | 放弃了"可预测重试时间"，换来「多 session 并发不会同步重试」 | `retry_utils.py:19-57` |
| **assistant.tool_calls 没人应答时合成 error tool 消息** | 外层 except 反向扫描 messages，给每个未被应答的 `tool_call_id` 注入合成 tool 消息 | 放弃了"严格协议层失败立刻可见"，换来下次 API 调用不会因协议违反被 400 | `run_agent.py:14166-14188` |
| **跨进程限流通过文件协调** | Nous 429 写入 `~/.hermes/rate_limits/nous.json`，所有 session 启动前读 | 放弃了"内存锁的低延迟"，换来 cron / gateway / CLI 多进程能共识 | `agent/nous_rate_guard.py` 全文件 |

### 3.3 数据流 / 控制流

**入口**：`run_agent.py:12404` `classify_api_error(api_error, ...)`
**输出**：`ClassifiedError` 上的 6 个字段
**消费者链**（按调用顺序，每条命中即 `continue` 跳过后续）：

```
1. _recover_with_credential_pool()    ← classified.reason   run_agent.py:12419
2. image_too_large 分支               ← classified.reason   run_agent.py:12434
3. oauth_long_context_beta_forbidden  ← classified.reason   run_agent.py:12461
4. provider-specific 401 refresh      ← status_code         run_agent.py:12482-12557
5. thinking_signature 分支            ← classified.reason   run_agent.py:12566
6. llama_cpp_grammar 分支             ← classified.reason   run_agent.py:12595
7. long_context_tier 压缩 + 降 ctx    ← classified.reason   run_agent.py:12713
8. is_rate_limited 立即 fallback      ← classified.reason   run_agent.py:12772
9. nous 429 跨 session 广播           ← classified.reason   run_agent.py:12810
10. payload_too_large 压缩            ← classified.reason   run_agent.py:12855
11. context_overflow 压缩 + 降 ctx    ← classified.reason   run_agent.py:12911
12. is_client_error → fallback or abort ← classified.retryable  run_agent.py:13091
13. retry_count >= max_retries →
       primary 传输重建 → fallback     ← _try_recover_primary_transport  run_agent.py:13171
14. wait jittered_backoff(retry_count)  ← retry_utils       run_agent.py:13260
```

**事件广播**：每条恢复路径都会通过 `self._emit_status` / `self._vprint` 把"⚠️ 怎么了 / 怎么救"输出给用户，错误对用户始终**可见且带恢复说明**，不是静默重试。

---

## 4. 关键机制拆解（含源码）

### 4.1 分类器主入口：优先级流水线

**为什么值得看**：教科书式的"先窄后宽"分类策略——provider-specific 误差最严重的特殊 case 排第一，然后是确定性最强的 status code，最后才是模糊的 message 模式。每一层都有"这条不命中就 fall through"的明确语义，避免分类规则之间相互掩盖。

`agent/error_classifier.py:341-570`：
```python
def classify_api_error(error, *, provider="", model="",
                      approx_tokens=0, context_length=200000,
                      num_messages=0) -> ClassifiedError:
    status_code = _extract_status_code(error)
    error_type = type(error).__name__
    if status_code is None and error_type == "RateLimitError":
        status_code = 429                         # 强制纠正 SDK bug
    body = _extract_error_body(error)
    error_code = _extract_error_code(body)
    error_msg = _build_combined_msg(error, body)  # str(error)+body+metadata.raw

    # ── 1. Provider-specific（thinking sig / 1M tier / llama.cpp grammar） ──
    # ── 2. HTTP status_code 分类 ──
    # ── 3. error_code 分类 ──
    # ── 4. message 模式分类 ──
    # ── 5. SSL 瞬时 → timeout（必须早于 disconnect 检查） ──
    # ── 6. server disconnect + 大会话 → context_overflow ──
    # ── 7. 传输错误类型名启发式 ──
    # ── 8. 兜底 unknown（retryable=True） ──
```

**值得看的点**：
- 第 5 层 **SSL 瞬时检查必须放在第 6 层之前**，否则一个 `[SSL: BAD_RECORD_MAC]` 在大会话里会被错判为 context_overflow 触发昂贵的压缩（`error_classifier.py:530-539` 的注释明确写了为什么）
- `_extract_status_code` 走 5 层 `__cause__` 链查找，因为 SDK 包装异常时常见把 `httpx.HTTPStatusError` 链到 `__cause__`（`error_classifier.py:971-987`）
- 把 `_raw_msg`、`_body_msg`、`metadata.raw` 三处都拼起来匹配，专门为 OpenRouter 把 Anthropic 错误内嵌为 JSON 字符串的"双层包装"设计（`error_classifier.py:381-411`）

### 4.2 402 歧义消解：周期配额 vs 真破产

**为什么值得看**：OpenClaw 那张帐——"Usage limit, try again in 5 minutes"是个周期性 quota 不是账单破产。这条规则只用 6 行表达完，但避免了"凭证池被周期性 quota 全部错杀"的灾难。

`agent/error_classifier.py:698-724`：
```python
def _classify_402(error_msg: str, result_fn) -> ClassifiedError:
    has_usage_limit  = any(p in error_msg for p in _USAGE_LIMIT_PATTERNS)
    has_transient    = any(p in error_msg for p in _USAGE_LIMIT_TRANSIENT_SIGNALS)
    if has_usage_limit and has_transient:
        return result_fn(FailoverReason.rate_limit, retryable=True,
                         should_rotate_credential=True, should_fallback=True)
    return result_fn(FailoverReason.billing, retryable=False,
                     should_rotate_credential=True, should_fallback=True)
```
`_USAGE_LIMIT_TRANSIENT_SIGNALS = ["try again", "retry", "resets at", "reset in", "wait", ...]`（`error_classifier.py:135-144`）。

### 4.3 断流 + 大会话 → 推导出 context overflow

**为什么值得看**：很多 API gateway（特别是 Cloudflare 前置的 Anthropic）面对超大 payload 不返 413，而是直接 RST TCP。如果只看异常类型，所有 RemoteProtocolError 都会被当 timeout 重试，永远卡死。这条规则是**用上下文规模反推协议层"沉默拒绝"的真实意图**。

`agent/error_classifier.py:541-561`：
```python
is_disconnect = any(p in error_msg for p in _SERVER_DISCONNECT_PATTERNS)
if is_disconnect and not status_code:
    is_large = approx_tokens > context_length * 0.6 or (
        context_length <= 256000 and (approx_tokens > 120000 or num_messages > 200)
    )
    if is_large:
        return _result(FailoverReason.context_overflow,
                       retryable=True, should_compress=True)
    return _result(FailoverReason.timeout, retryable=True)
```
注意阈值 `context_length * 0.6` 比正常的 context_overflow 触发线 (0.4) 高，因为是**推导**而非确认。

### 4.4 jittered backoff：去相关化的退避

**为什么值得看**：这是整个错误处理唯一一个"严肃考虑了多 session 并发场景"的地方。`time_ns ^ counter * 0x9E3779B9`（黄金分割数）保证即使 100 个 session 在同一毫秒同时进入退避，每个的 jitter 都不同。

`agent/retry_utils.py:19-57`：
```python
def jittered_backoff(attempt, *, base_delay=5.0, max_delay=120.0, jitter_ratio=0.5):
    global _jitter_counter
    with _jitter_lock:
        _jitter_counter += 1
        tick = _jitter_counter
    exponent = max(0, attempt - 1)
    if exponent >= 63 or base_delay <= 0:
        delay = max_delay
    else:
        delay = min(base_delay * (2 ** exponent), max_delay)
    seed = (time.time_ns() ^ (tick * 0x9E3779B9)) & 0xFFFFFFFF
    rng = random.Random(seed)
    jitter = rng.uniform(0, jitter_ratio * delay)
    return delay + jitter
```

### 4.5 单工具失败的"局部异常 → 数据降级"

**为什么值得看**：这是 Hermes 抗故障设计的**精神核心**——把异常变成数据，让模型作为"上层错误处理器"。每个工具执行点都有完全相同的捕获模式：异常 → 字符串 → 写入 `result` → 继续 turn。

`run_agent.py:9956-9974`（并发分支）：
```python
start = time.time()
try:
    result = self._invoke_tool(function_name, function_args, ...)
except Exception as tool_error:
    result = f"Error executing tool '{function_name}': {tool_error}"
    logger.error("_invoke_tool raised for %s: %s", function_name, tool_error,
                 exc_info=True)                     # ← 完整堆栈到日志
duration = time.time() - start
is_error, _ = _detect_tool_failure(function_name, result)
if is_error:
    logger.info("tool %s failed (%.2fs): %s", function_name, duration, result[:200])
results[index] = (function_name, function_args, result, duration, is_error, False)
```
关键点：**`exc_info=True` 把完整堆栈写到日志，但传给模型的只是单行 message**——模型不需要 traceback，调试者需要。

### 4.6 外层 except：补齐协议级"应答缺口"

**为什么值得看**：这是**协议驱动的防御**——OpenAI/Anthropic 协议要求每个 `tool_call_id` 必须有对应的 `role=tool` 应答。如果中途异常导致 tool_calls 还在但应答没写，下一次 API 调用会被 provider 强制 400。这段代码反向扫描 messages，给每个未应答的 tool_call_id **合成 error tool 消息**，让协议保持自洽。

`run_agent.py:14154-14188`：
```python
except Exception as e:
    error_msg = f"Error during OpenAI-compatible API call #{api_call_count}: {str(e)}"
    try:
        print(f"❌ {error_msg}")
    except (OSError, ValueError):
        logger.error(error_msg)
    logger.debug("Outer loop error in API call #%d", api_call_count, exc_info=True)

    for idx in range(len(messages) - 1, -1, -1):
        msg = messages[idx]
        if not isinstance(msg, dict): break
        if msg.get("role") == "tool": continue
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            answered_ids = {m["tool_call_id"] for m in messages[idx + 1:]
                            if isinstance(m, dict) and m.get("role") == "tool"}
            for tc in msg["tool_calls"]:
                if not tc or not isinstance(tc, dict): continue
                if tc["id"] not in answered_ids:
                    messages.append({
                        "role": "tool",
                        "name": AIAgent._get_tool_call_name_static(tc),
                        "tool_call_id": tc["id"],
                        "content": f"Error executing tool: {error_msg}",
                    })
            break
```

### 4.7 凭证池 / Provider Fallback / 上下文压缩的解耦

**为什么值得看**：分类器抛出 `should_rotate_credential / should_fallback / should_compress` 三个并列的「修复建议」，主循环按"代价从小到大"的顺序处理：先尝试**便宜的轮换**，再尝试**中等开销的 fallback**，最后才是**昂贵的压缩**。每条路径之间用 `continue` 严格断开，不会在同一异常里既轮换又压缩。

`run_agent.py:12419-12426`（先轮换）：
```python
recovered_with_pool, has_retried_429 = self._recover_with_credential_pool(
    status_code=status_code,
    has_retried_429=has_retried_429,
    classified_reason=classified.reason,
    error_context=error_context,
)
if recovered_with_pool:
    continue
```
`run_agent.py:12772-12788`（再 fallback）：
```python
is_rate_limited = classified.reason in (FailoverReason.rate_limit, FailoverReason.billing)
if is_rate_limited and self._fallback_index < len(self._fallback_chain):
    pool_may_recover = _pool_may_recover_from_rate_limit(
        self._credential_pool, provider=self.provider,
        base_url=getattr(self, "base_url", None))
    if not pool_may_recover:
        if self._try_activate_fallback(reason=classified.reason):
            retry_count = 0; compression_attempts = 0
            primary_recovery_attempted = False
            continue
```
`run_agent.py:12915-12960`（最后才压缩）—— 仅当前两步都没救活才走 `_compress_context`。

### 4.8 model_tools 工具执行的"最后一道兜底"

**为什么值得看**：和 run_agent.py 里的 except 是**双重兜底**——单个工具的异常先在 `handle_function_call` 内被捕获并打成 JSON 字符串，再被 run_agent 的 except 二次捕获。两层都失败模型才会看到生硬的字符串错误。

`model_tools.py:815-818`：
```python
except Exception as e:
    error_msg = f"Error executing {function_name}: {str(e)}"
    logger.exception(error_msg)
    return json.dumps({"error": error_msg}, ensure_ascii=False)
```

### 4.9 跨进程限流文件锁（Nous 案例）

**为什么值得看**：这是**唯一一处把单进程错误处理升级为跨进程协调**的地方。Nous 的 RPH（每小时请求数）一旦被打爆，再多重试只会延长封禁时间。文件级共享状态让 cron 任务、gateway worker、CLI session **联合冷却**。

`run_agent.py:12810-12850`（消费方）：
```python
if (is_rate_limited and self.provider == "nous"
    and classified.reason == FailoverReason.rate_limit
    and not recovered_with_pool):
    _genuine_nous_rate_limit = False
    try:
        from agent.nous_rate_guard import is_genuine_nous_rate_limit, record_nous_rate_limit
        _err_resp = getattr(api_error, "response", None)
        _err_hdrs = getattr(_err_resp, "headers", None) if _err_resp else None
        _genuine_nous_rate_limit = is_genuine_nous_rate_limit(
            headers=_err_hdrs, last_known_state=self._rate_limit_state)
        if _genuine_nous_rate_limit:
            record_nous_rate_limit(headers=_err_hdrs, error_context=error_context)
    except Exception:
        pass
    if _genuine_nous_rate_limit:
        retry_count = max_retries          # 跳过所有重试，让顶层 fallback 接管
        continue
```
关键点是 `is_genuine_nous_rate_limit` 用 `x-ratelimit-*` 头**区分"账户级 RPH 耗尽"与"上游 provider 瞬时容量"**，避免上游瞬时 429 触发跨 session 全局冷却。

---

## 5. 与其他维度的交互

| 方向 | 维度 | 交互内容 | 代码中的交互点 |
|---|---|---|---|
| **被调用** | 编排循环（维度1） | 主循环每次 API 调用都走分类器 → 决策树 → 重试/fallback | `run_agent.py:12404`（分类入口）、`12772`（fallback 入口）、`13166`（max_retries 兜底） |
| **被调用** | 工具系统（维度2） | 工具执行抛异常 → 降级为 tool 消息字符串，模型据此规划下一步 | `run_agent.py:9965, 10396, 10420, 10448, 10467`；`model_tools.py:815` |
| **被调用** | 子 Agent 编排（维度11） | 子 agent 异常通过同一套 except 兜底；外层把"子 agent 失败"作为 result 返回给 dispatcher | `run_agent.py:14154` 的 outer except 同时覆盖子 agent 调用 |
| **触发** | 上下文管理（维度4） | `should_compress=True` → 调用 `self._compress_context(messages, ...)`；`context_overflow` 时还会 `compressor.update_model(context_length=new_ctx)` 降低 ctx 探针 | `run_agent.py:12878, 13035`；`error_classifier.py:_classify_400, _classify_by_message` 中的所有 `should_compress=True` |
| **触发** | 状态管理（维度7） | 任何"放弃"分支都先 `_persist_session(messages, conversation_history)` 持久化；大会话 + 400 时**主动跳过持久化**避免增长循环 | `run_agent.py:13149-13156`、`12865, 12896, 13022, 13055, 13156, 13229` |
| **触发** | 凭证池（属于初始化/状态维度） | `should_rotate_credential` → `_credential_pool.mark_exhausted_and_rotate()` → `_swap_credential()` | `run_agent.py:6531-6613` `_recover_with_credential_pool` |
| **触发** | Provider 路由 | `should_fallback` → `_try_activate_fallback(reason)` → `resolve_provider_client()` 切换客户端 | `run_agent.py:7834-7929` |
| **读取** | 上下文管理 | 分类器需要 `approx_tokens` + `context_length` + `num_messages` 来推断"断流是不是因为太大" | `error_classifier.py:339-411` 入参 |
| **写入** | 跨进程状态 | Nous 真正限流时写入 `~/.hermes/rate_limits/nous.json`；所有 session 启动前读 | `agent/nous_rate_guard.py`；`run_agent.py:12832` 调用 `record_nous_rate_limit` |
| **协同** | 中断系统 | 退避循环每 200ms 检查一次 `_interrupt_requested`，避免长 sleep 阻塞中断 | `run_agent.py:13277-13297` |
| **协同** | gateway 心跳 | 退避期间每 30s 调用 `_touch_activity()` 防止 gateway inactivity monitor 杀掉 worker | `run_agent.py:13290-13297` |
| **被旁路** | UI 显示 | `_summarize_api_error` 处理 Cloudflare HTML、JSON body、Ray ID 提取，把丑陋的 raw error 变成给用户看的一行 | `run_agent.py:4282-4319` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **provider 错误格式是漂移的**：同一种错误（context overflow）在不同 provider 用不同 status code、不同 message 表达，分类器靠**模式 union** 而不是结构化 schema 兜底。
2. **错误类别远大于 HTTP 状态码维度**：402 这一个码下面就有 billing / rate_limit 两种语义，500 / 530 / 524 / 502 都需要单独区分（Cloudflare-specific），所以分类器不能简单 `dispatch_by_status_code()`。
3. **多次失败往往是关联的**：连续 429 → 同一 key 没救；连续 400 + 大会话 → 上下文真的爆了；连续 RemoteProtocolError → 不是网络抖动是 sweep。这就是为什么有 `compression_attempts` / `has_retried_429` 等"有状态"重试计数器。
4. **模型有能力自主修复部分错误**：单工具失败被降级为字符串 result，假设模型读到 `"Error executing tool 'terminal': ..."` 后会**主动选择不同工具或重新规划**。这个假设在大模型上成立但在小模型上可能崩。
5. **可观测性 > 性能**：所有错误路径都 `_vprint(..., force=True)`，即使 quiet_mode 也强制输出，因为静默的失败比慢一点的失败更糟糕。

### 6.2 代价 / 风险

- **分类规则爆炸**：`error_classifier.py` 有 17 种 `FailoverReason`、9 张模式表（_BILLING / _RATE_LIMIT / _USAGE_LIMIT / _CONTEXT_OVERFLOW / ...），每加一个新 provider 就要增补，已经接近人类可读的极限。
- **隐式优先级耦合**：第 5 层 SSL 检查必须早于第 6 层 disconnect 检查，第 6 层必须早于第 7 层传输错误检查——文件里靠注释说明，没有形式化的优先级表，重构容易破坏不变式。
- **assistant.tool_calls 合成 error 应答可能掩盖真错误**：模型可能会基于"工具失败"做出错误推理，因为它看到的不是"系统崩溃"而是"工具有 bug"。
- **跨进程文件锁的竞态**：`record_nous_rate_limit` + `is_genuine_nous_rate_limit` 之间没有原子保证，两个 session 同时被 429 时可能写到不同状态。
- **凭证池 + fallback 的优先级是硬编码的**：当前总是"先轮换再 fallback"。如果用户付费的 fallback provider 比免费 pool 更便宜，这个顺序就反了。
- **重试上限 3 次的合理性来自经验**（`api_max_retries=3`），但对 Cloudflare 524 这种 30 秒才知结果的 case，3 次可能都在累计延迟上不可接受。

### 6.3 如果要重新设计可能改变什么

1. **把分类规则从代码改成 YAML/JSON 配置**：`(provider, status_code, message_pattern, body_path) → (reason, recovery_actions)` 的规则表，新增 provider 不用改代码。
2. **引入"恢复成本"权重**：让主循环按 `min(成本) × P(成功)` 而不是固定优先级选择恢复路径——比如用户的 fallback 更便宜时跳过 pool rotation。
3. **结构化错误事件流**：每次错误产出 `ErrorEvent { provider, reason, attempted_recoveries[], outcome }`，给观测/限流/熔断系统消费，而不是只有日志。
4. **跨进程限流泛化**：现在只有 Nous 特化，其他 provider（OpenRouter、Cloudflare 前置的 Anthropic）都应该有同样的跨 session breaker。把 `nous_rate_guard.py` 抽象成 `provider_rate_guard.py(provider_name)`。
5. **分类器单测覆盖**：当前 `tests/test_retry_utils.py` 只测了退避，分类器没有专门的真错误样本回放测试，规则爆炸的同时回归保护几乎为零。
6. **拆分 `retryable` 的语义模糊性**：用 `retry_strategy: enum {direct, rotate, fallback, compress, abort}` 替代当前 4 个 bool 字段的 cartesian product。

### 6.4 对自己设计 Agent 系统的启示

1. **永远把分类（"这是什么"）和决策（"该怎么办"）分开**。前者纯函数、后者有状态——这让分类器可单测、决策树可调整、两者互不污染。
2. **优先级流水线 > 大 if/elif 树**。每条规则只关心"我命中或不命中"，命中即返回，不管下游怎么决策。否则规则间相互掩盖的 bug 几乎不可能复现。
3. **传输层断流 + 上下文规模 = 高置信度的协议层故意拒绝**。不要只看异常类型，同时看协议外的 contextual signal。
4. **退避必须 jittered**。任何被多 session 共享的下游一旦没 jitter，第一次 429 就会在 t+5s 触发雪崩同步重试。
5. **工具失败应该是数据，不是异常**。让模型读到 `"Error: ..."` 字符串，比 try/except 把整个 turn 杀掉更鲁棒——前提是模型够强能把错误当作输入推理。
6. **协议级不变式（如 tool_call_id 必须有应答）需要 except 路径里反向修复**。指望主流程不抛异常是不现实的，但保证"即使抛了异常，下次调用也能合法"是可达的。
7. **"放弃"分支必须 persist**。任何 abort 之前都先 `_persist_session()`，让用户能 `/resume` 接着上次失败的点。但要识别"会触发增长循环"的失败（大会话 + 400），跳过持久化避免越救越大。
8. **多进程协调用文件 + 原子写**。比 Redis / 共享内存简单，对 cron + CLI + gateway 多进程场景足够。但要识别"真鉴权失败"vs"上游瞬时容量"，避免错误的全局冷却。
9. **把"没有 fix 但需要 user action"的错误（OpenRouter 隐私设置、Codex token 被旋走）做成专门的 `FailoverReason` + 用户友好的 actionable hint**，比让用户翻 traceback 找原因强 100 倍（`run_agent.py:13129-13140` 的 actionable hint）。

---

**核心源码索引**：
- `/home/weilan/workdir/excellent_project/hermes-agent/agent/error_classifier.py:1-1036`（分类器全文件）
- `/home/weilan/workdir/excellent_project/hermes-agent/agent/retry_utils.py:1-57`（jittered backoff）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:12398-13297`（主循环错误恢复决策树）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:14154-14199`（外层 except + 协议补齐）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:9956-9974, 10380-10470`（工具失败降级）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:6531-6613`（凭证池恢复）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:7834-7929`（fallback 切换）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:8117-8195`（primary 传输重建）
- `/home/weilan/workdir/excellent_project/hermes-agent/run_agent.py:4282-4380`（错误信息清洗 / 上下文提取）
- `/home/weilan/workdir/excellent_project/hermes-agent/agent/display.py:804-834`（工具失败启发式检测）
- `/home/weilan/workdir/excellent_project/hermes-agent/model_tools.py:815-818`（工具兜底）
- `/home/weilan/workdir/excellent_project/hermes-agent/agent/nous_rate_guard.py:1-100`（跨进程限流共享状态）
