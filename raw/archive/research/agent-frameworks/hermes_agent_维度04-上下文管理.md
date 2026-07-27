# 维度名：上下文管理（Context Management）

## 1. 一句话定位

把"塞进 LLM 一次请求里的所有 token"当作一种受限资源来主动经营 —— 决定**什么进、什么出、以什么形态出、以什么时机出**，使得多轮对话能在固定上下文窗口下持续运行而不丢失任务、不破坏 prompt cache、不撞 4xx。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

直接看代码反推三类故障：

**故障 A — 上下文溢出，整个 session 报废。**
`run_agent.py:11013-11069` 在每次进入主循环前先做 preflight：
```
if _preflight_tokens >= self.context_compressor.threshold_tokens:
    ...
    for _pass in range(3):  # 大 session 可能要多压几轮
        messages, active_system_prompt = self._compress_context(...)
```
没有这层 preflight，当用户切换到一个上下文窗口更小的模型（比如从 200K 切到 32K）继续聊原来的会话，第一次 API 调用就会被 provider 当作"context length exceeded"返回非可重试的 4xx —— 然后 `error_classifier` 会把整个 request 判为终止，用户丢掉整段对话。

**故障 B — Tool call/result 配对断裂导致 provider 持续 400。**
压缩会从消息中段切走若干 turn，必然制造孤儿 `tool_call`（assistant 调了工具但 result 被切走）或孤儿 `tool_result`（result 留下但对应的 `tool_call` 被切走）。`context_compressor.py:1041-1099` 的 `_sanitize_tool_pairs` 注释非常直白：
> "No tool call found for function call output with call_id ..."

如果不修这种孤儿，OpenAI 协议会对每一次 follow-up 都抛 400，session 进入死循环。

**故障 C — 压缩本身把"用户最新任务"压没了。**
`context_compressor.py:1148-1193` 的 `_ensure_last_user_message_in_tail` 是修 issue #10896 的硬保护：
> "If the last user-role message ends up in the *compressed* middle region the LLM summariser writes it into 'Pending User Asks', but `SUMMARY_PREFIX` tells the next model to respond only to user messages *after* the summary — so the task effectively disappears from the active context"

也就是说，如果不把"最近一条 user 消息"硬钉在 tail 里，agent 会出现"压缩后突然忘掉用户在问什么"的现象。

**故障 D — Prompt cache 失效，每轮燃烧 4×成本。**
`run_agent.py:11354-11357` 注释直接写出：
> "Plugin context from pre_llm_call hooks is injected into the user message ... NOT the system prompt. This is intentional — system prompt modifications break the prompt cache prefix."

没有"system prompt 锁定 + 只在 user 消息上动手"这条纪律，每轮 system prompt 微变（时间戳除外）都会导致 Anthropic prompt caching 整个失效，输入 token 成本上升 ~4×。

### 2.2 具体触发条件

代码中四种入口分别由不同条件激活：

| 入口 | 触发条件 | 代码位置 |
|------|---------|---------|
| **Preflight 压缩** | `len(messages) > protect_first_n + protect_last_n + 1` 且 `estimate_request_tokens_rough() >= threshold_tokens` | `run_agent.py:11011-11024` |
| **响应后压缩** | `last_prompt_tokens > 0 and >= threshold_tokens`（用 provider 回报的真实 prompt_tokens） | `run_agent.py:13787-13803` |
| **错误恢复压缩** | `error_classifier` 把 API 错误归类为 `should_compress=True`（context-length 4xx） | `run_agent.py:12744 / 12878 / 13035` |
| **手动 `/compress [focus]`** | 用户在 CLI 输入 slash 命令；可携带 focus topic 引导式压缩 | `cli.py:7867-7951` |

`should_compress()` 自身还有 anti-thrashing 保护（`context_compressor.py:478-488`）：
```
if self._ineffective_compression_count >= 2:
    return False  # 连续两次压缩都省 < 10%，停手
```

阈值的真实值不是写死的百分比，而是 **`max(context_length * threshold_percent, MINIMUM_CONTEXT_LENGTH)`**（`context_compressor.py:414-417`）—— 给小窗口模型留底，避免在 4K 窗口上 50% 立刻就压。

---

## 3. 核心设计思路

### 3.1 抽象模型

整个上下文管理可以看作三段式管道：

```
                     ┌─────────────────────────────────────────────┐
                     │  System Prompt（缓存层 / 永不持久化）       │
                     │  ─────                                       │
     ephemeral       │  identity + memory + skills index +         │
     injection ────▶ │  context files + timestamp + platform hint  │
     (run_agent)     │                                              │
                     │  ↑ 一个 session 只 build 一次               │
                     │  ↑ 仅压缩或 model switch 才 invalidate      │
                     └─────────────────────────────────────────────┘
                                       │
                                       ▼
                     ┌─────────────────────────────────────────────┐
                     │  Conversation Messages（持久化 / 可压缩）   │
                     │  ─────                                       │
                     │  [head: 受保护 N 条] [middle: 可压缩区]    │
                     │  [tail: token-budget 锁定区]                │
                     │                                              │
                     │  压缩 = LLM 摘要 middle + sanitize 孤儿对  │
                     └─────────────────────────────────────────────┘
                                       │
                                       ▼
                     ┌─────────────────────────────────────────────┐
                     │  Tool Schemas（动态 / 与 messages 解耦）   │
                     │  ─────                                       │
                     │  get_tool_definitions() → memoized          │
                     │  _last_resolved_tool_names（进程全局）      │
                     │  注入计入 preflight token 预算              │
                     └─────────────────────────────────────────────┘
```

伪代码层面：

```python
# 每轮请求构造
def build_request(messages):
    # 1) System prompt — 拿 cached，不重建
    sys_prompt = self._cached_system_prompt or self._build_system_prompt()

    # 2) Preflight：估算总 token（含 schema！），过阈值就先压再发
    if estimate(messages, sys_prompt, tools) >= threshold:
        for _ in range(3):  # 多 pass
            messages = compressor.compress(messages)

    # 3) Ephemeral 拼接：cached + 临时 + prefill —— 不入库
    effective = sys_prompt + "\n\n" + ephemeral_system_prompt
    api_messages = [{"role":"system", "content":effective}] + prefill + messages

    # 4) Anthropic prompt caching：4 个 cache_control breakpoint
    if use_prompt_caching:
        api_messages = apply_anthropic_cache_control(api_messages)
    return api_messages
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|---------------|-------------------|
| **压缩单元** | LLM 生成的"结构化摘要"（Active Task / Goal / Completed / Blocked / Files / Resolved+Pending Questions / Critical Context 等 12 个 section） | 朴素截断旧消息，或机械抽取最后 N 条 | `context_compressor.py:774-831` 的模板里 "Active Task" 一节明确标 "**THE SINGLE MOST IMPORTANT FIELD**, copy verbatim" —— 简单截断会丢 user 的最新意图，而 12-section 结构化摘要能在迭代压缩时把"已答问题"移走、"未答问题"留下，避免重复工作 |
| **保护策略** | 头部按"消息条数"（`protect_first_n=3`），尾部按"token 预算"（`tail_token_budget = threshold_tokens × 0.20`） | 头尾都按消息条数固定 | `context_compressor.py:1199-1257`：tool 调用产生的 result 体积差异极大（terminal 输出几行 vs 50KB 文件），固定条数对大窗口模型浪费、对小窗口模型不够；token 预算自适应模型 context_length |
| **压缩用辅助模型** | 单独的 `auxiliary.compression.model`（默认 cheap/fast，如 haiku-4.5、glm-4.5-flash），失败时降级到 main model 重试 | 总是用 main model 做摘要 | `context_compressor.py:925-979` 的双层 fallback —— 主流程被压缩"卡住"是次优解，宁可烧 main model 一次也不能让中间 N 轮无摘要丢弃。同时 `_compression_threshold_for_model` 允许特定模型（Arcee Trinity Thinking）覆盖默认阈值到 0.75 |
| **System prompt 持久化策略** | "ephemeral injection" —— `cached_system_prompt` 是"常驻部分"，`ephemeral_system_prompt` 和 `prefill_messages` 在 API 调用时拼接但**不写入 SQLite**；Plugin context 必须注入到 **user message** 而非 system | 一律持久化所有 system 内容 | `run_agent.py:11354-11357` 注释：要保 Anthropic prompt caching 的 prefix 稳定，system prompt 必须每轮字节级一致；时间戳 + memory 已经一定会变（每轮变化），所以把"再变化的部分"挪到 user 侧消化 |

### 3.3 数据流/控制流

```
┌────────────────────────────────────────────────────────────────────┐
│                        每轮请求一次的流向                          │
└────────────────────────────────────────────────────────────────────┘

[用户输入]
    │
    │   ① cli.py / gateway 收到，调 AIAgent.run_conversation
    ▼
[history 加载 + system prompt 获取]
    │   _build_system_prompt() 第一次跑：identity → memory → skills →
    │     context files → timestamp → platform hint
    │   后续 turn 直接从 self._cached_system_prompt 读
    │   入口：run_agent.py:10963-11002
    ▼
[Preflight 压缩判定]
    │   estimate_request_tokens_rough(messages, sys_prompt, tools)
    │   入口：run_agent.py:11011-11069
    │   ├─ 不过阈值：直接进下一步
    │   └─ 过阈值：循环最多 3 pass 调 _compress_context
    ▼
[Compress 流程（如触发）]
    │   ContextCompressor.compress():
    │     ① _prune_old_tool_results：去重 + 长输出替换为 1 行 summary
    │     ② _find_tail_cut_by_tokens：按 token 预算找 tail 边界
    │     ③ _ensure_last_user_message_in_tail：把最新 user msg 钉进 tail
    │     ④ _generate_summary：辅助模型生成 12-section 结构化摘要
    │     ⑤ assemble：head + summary 消息 + tail
    │     ⑥ _sanitize_tool_pairs：补全/移除孤儿 tool_call/result
    │   入口：context_compressor.py:1278-1479
    │
    │   压缩后：rotate session_id（SQLite split），重建 system prompt
    │   入口：run_agent.py:9485-9520
    ▼
[Ephemeral 注入 + prompt caching]
    │   effective_system = cached + ephemeral_system_prompt
    │   api_messages = [system] + prefill + messages
    │   apply_anthropic_cache_control（4 breakpoints）
    │   入口：run_agent.py:11347-11386
    ▼
[发送到 LLM provider]
    │
    ▼
[响应回收 → update_from_response]
    │   compressor.last_prompt_tokens = usage.prompt_tokens
    │   入口：run_agent.py:12085 + context_compressor.py:463-466
    ▼
[响应后压缩判定]
    │   if compression_enabled and compressor.should_compress(real_tokens):
    │       _compress_context(...)
    │   入口：run_agent.py:13803-13809
    ▼
[next turn]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：Token 预算化的尾部保护

**作用**：把"最近的 N 条消息"换成"最近的 N 千 token 消息"作为不可压缩的尾部边界。

**设计意图**：固定条数对工具结果体积差异极大的场景失效。一个 50KB 的 `write_file` tool result 顶得上 30 个普通 turn —— 如果按 `protect_last_n=20` 这种条数保护，要么把这种巨型 result 全保了导致几乎压不下来，要么用更激进的条数把真正最近的小对话也压走。

**关键源码**（`agent/context_compressor.py:1195-1257`）：
```python
def _find_tail_cut_by_tokens(self, messages, head_end, token_budget=None):
    if token_budget is None:
        token_budget = self.tail_token_budget   # ← 模型 ctx × 0.10 (默认)
    n = len(messages)
    min_tail = min(3, n - head_end - 1) if n - head_end > 1 else 0
    soft_ceiling = int(token_budget * 1.5)     # ← 关键：允许 1.5× 超预算
    accumulated = 0
    cut_idx = n
    for i in range(n - 1, head_end - 1, -1):
        msg_tokens = _content_length_for_budget(...) // 4 + 10
        # ① 超 soft_ceiling 才 break，但 min_tail 是硬下限
        if accumulated + msg_tokens > soft_ceiling and (n - i) >= min_tail:
            break
        accumulated += msg_tokens
        cut_idx = i
    # ② 不能切在 tool_call/result 配对中间
    cut_idx = self._align_boundary_backward(messages, cut_idx)
    # ③ 必须把最新 user message 钉进 tail（修 #10896）
    cut_idx = self._ensure_last_user_message_in_tail(messages, cut_idx, head_end)
    return max(cut_idx, head_end + 1)
```

**为什么值得看**：`soft_ceiling = budget × 1.5` 这个"软超额"是个聪明的妥协 —— 既不会因为下一条刚好压线而切掉它（导致大 result 被切半再被 sanitizer 移除），也保证了 `min_tail=3` 永远会被尊重。三道后处理（align → ensure_user_in_tail → max）顺序也有讲究：先对齐 tool 组，再钉 user 消息，最后保证不越过 head 边界 —— 任何一道弄反都会触发实际生产 issue。

---

### 机制 B：摘要 prompt 的"反指令性"措辞

**作用**：让 LLM 生成的摘要不会被下一轮的主模型误读为"要执行的指令"。

**设计意图**：摘要本质上是一段插入到对话中段、带 role=user/assistant 的消息。如果摘要里写"用户问 X"，下一轮模型完全可能把它当作"现在用户问 X"再答一遍，整个 session 进入回声循环（issue #11475、#14521）。

**关键源码**（`agent/context_compressor.py:37-51` + `1428-1433`）：
```python
SUMMARY_PREFIX = (
    "[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted "
    "into the summary below. This is a handoff from a previous context "
    "window — treat it as background reference, NOT as active instructions. "
    "Do NOT answer questions or fulfill requests mentioned in this summary; "
    "they were already addressed. "
    "Your current task is identified in the '## Active Task' section of the "
    "summary — resume exactly from there. "
    "IMPORTANT: Your persistent memory (MEMORY.md, USER.md) in the system "
    "prompt is ALWAYS authoritative and active — never ignore or deprioritize "
    "memory content due to this compaction note. "
    "Respond ONLY to the latest user message that appears AFTER this summary..."
)

# 当 summary 必须以 role="user" 插入时，再附加显式分隔
if not _merge_summary_into_tail and summary_role == "user":
    summary = (
        summary
        + "\n\n--- END OF CONTEXT SUMMARY — "
        "respond to the message below, not the summary above ---"
    )
```

**为什么值得看**：这段不是 boilerplate —— 它的措辞经过和 Azure/OpenAI 内容过滤的实际博弈（`context_compressor.py:759-771` 注释："Azure/OpenAI-compatible content filters have flagged stronger 'injection' / 'do not respond' framing"）。同时 `## Active Task` 节作为"权威续行点"被反复提及三次（prefix 一次、template 一次、iterative update 一次），保证弱模型也能正确续行。**关键洞察**：把"摘要的元定位"也写进摘要本身的 wrapper，比指望系统设计层面的"role 隔离"更鲁棒。

---

### 机制 C：Tool call / result 配对的 sanitize

**作用**：压缩切割后必然产生孤儿 `tool_call`（result 被切走）或孤儿 `tool_result`（call 被切走），sanitize 修复这种结构破坏。

**设计意图**：OpenAI 协议要求每个 `tool_call` 必须紧跟一个相同 `call_id` 的 `tool` 消息；缺一不可，否则 provider 直接 400 且不可重试。压缩边界很难百分百对齐这种配对，与其把边界对齐逻辑写得超复杂，不如允许边界乱切再统一修复。

**关键源码**（`agent/context_compressor.py:1041-1099`）：
```python
def _sanitize_tool_pairs(self, messages):
    surviving_call_ids = set()
    for msg in messages:
        if msg.get("role") == "assistant":
            for tc in msg.get("tool_calls") or []:
                cid = self._get_tool_call_id(tc)
                if cid: surviving_call_ids.add(cid)

    result_call_ids = {m["tool_call_id"] for m in messages
                       if m.get("role")=="tool" and m.get("tool_call_id")}

    # ① 删除孤儿 tool result
    orphaned_results = result_call_ids - surviving_call_ids
    if orphaned_results:
        messages = [m for m in messages
                    if not (m.get("role")=="tool"
                            and m.get("tool_call_id") in orphaned_results)]

    # ② 给孤儿 tool_call 补 stub result
    missing_results = surviving_call_ids - result_call_ids
    if missing_results:
        patched = []
        for msg in messages:
            patched.append(msg)
            if msg.get("role") == "assistant":
                for tc in msg.get("tool_calls") or []:
                    cid = self._get_tool_call_id(tc)
                    if cid in missing_results:
                        patched.append({"role":"tool",
                            "content":"[Result from earlier conversation — see context summary above]",
                            "tool_call_id": cid})
        messages = patched
    return messages
```

**为什么值得看**：两种孤儿用对称但不同的处理方式 —— 多余的 result 直接删（无下游依赖），缺失的 result 必须补 stub（assistant message 已经声称调过工具，不能凭空消失）。这种"边界乱切 + 终点对齐"的工程思路比尝试在边界查找时就 100% 对齐 tool group 简单得多，也对未来增加新的消息类型更鲁棒。

---

### 机制 D：辅助模型 + 多层 Fallback 的摘要生成

**作用**：把摘要外包给一个独立的便宜模型，失败时不让 session 卡住。

**设计意图**：用 main model 做摘要昂贵且抢占主任务的 quota / 速率限制，但辅助模型可能没配置、可能临时挂掉。需要一个"先用 aux，aux 挂了立刻 fallback 到 main，main 再挂才进 cooldown 丢 turn"的多层降级。

**关键源码**（`agent/context_compressor.py:899-994`，节选关键 fallback 链）：
```python
try:
    response = call_llm(task="compression", main_runtime={...},
                       messages=[{"role":"user", "content":prompt}],
                       max_tokens=int(summary_budget * 1.3))
    summary = redact_sensitive_text(response.choices[0].message.content.strip())
    self._previous_summary = summary  # ← 下一次迭代式更新基础
    return self._with_summary_prefix(summary)

except RuntimeError:  # 完全没配 provider
    self._summary_failure_cooldown_until = time.monotonic() + 600
    return None  # ← 直接放弃；上层会插入 static fallback marker

except Exception as e:
    # ① 模型不存在 / 不可用 → 立刻切 main model 重试一次
    if (_is_model_not_found or _is_timeout) and self.summary_model != self.model \
       and not self._summary_model_fallen_back:
        self._summary_model_fallen_back = True
        self.summary_model = ""  # 后续走 main model
        return self._generate_summary(...)  # 递归重试

    # ② 未知错误也尝试主模型一次（"丢 N turn 比多调一次更糟"）
    if self.summary_model and self.summary_model != self.model \
       and not self._summary_model_fallen_back:
        self._summary_model_fallen_back = True
        self.summary_model = ""
        return self._generate_summary(...)

    # ③ 都失败：60s cooldown，本次返回 None
    self._summary_failure_cooldown_until = time.monotonic() + 60
    return None
```

**为什么值得看**：错误分支不是简单的 `if/else`，而是分了三个语义层：**配置缺失（10 分钟长 cooldown）→ 临时错误 + 可降级（立刻递归重试）→ 全失败（短 cooldown 但仍允许下一轮）**。同时 `_previous_summary` 字段让"迭代式更新"成为可能 —— 多次压缩不是每次从头摘要，而是基于上次的摘要再叠加新 turn，避免老摘要被新摘要稀释。**注意 `redact_sensitive_text` 在 input 和 output 都跑了一次** —— 因为 LLM 可能忽略 prompt 里的"不要保留密钥"指令而把密钥原样写回摘要。

---

### 机制 E：Ephemeral System Prompt + Prompt Caching 协同

**作用**：让"每轮变化的内容"（plugin context、prefill、临时指令）参与 LLM 但不破坏 prompt cache 前缀也不污染持久化历史。

**设计意图**：Anthropic prompt caching 的核心约束是 "prefix 必须字节级稳定"。如果把每轮变化的内容塞进 system prompt，每轮都重新计费 = caching 失效。Hermes 的方案是把"变化的部分"全部往 user 消息或独立的 ephemeral 字段里推，让 system prompt 在整个 session（除压缩外）保持完全相同。

**关键源码**（`run_agent.py:11347-11386`）：
```python
# Build the final system message: cached prompt + ephemeral system prompt.
# Ephemeral additions are API-call-time only (not persisted to session DB).
# External recall context is injected into the user message, not the system
# prompt, so the stable cache prefix remains unchanged.
effective_system = active_system_prompt or ""
if self.ephemeral_system_prompt:
    effective_system = (effective_system + "\n\n" + self.ephemeral_system_prompt).strip()
# NOTE: Plugin context from pre_llm_call hooks is injected into the
# user message (see injection block above), NOT the system prompt.
# This is intentional — system prompt modifications break the prompt
# cache prefix.  The system prompt is reserved for Hermes internals.
if effective_system:
    api_messages = [{"role": "system", "content": effective_system}] + api_messages

# Inject ephemeral prefill messages right after the system prompt
# but before conversation history. Same API-call-time-only pattern.
if self.prefill_messages:
    sys_offset = 1 if effective_system else 0
    for idx, pfm in enumerate(self.prefill_messages):
        api_messages.insert(sys_offset + idx, pfm.copy())

if self._use_prompt_caching:
    api_messages = apply_anthropic_cache_control(
        api_messages, cache_ttl=self._cache_ttl,
        native_anthropic=self._use_native_cache_layout,
    )
```

配合 `agent/prompt_caching.py:41-72` 的 4-breakpoint 策略：
```python
# system_and_3 caching: 4 breakpoints = system + last 3 non-system msgs
if messages[0].get("role") == "system":
    _apply_cache_marker(messages[0], marker, ...)
    breakpoints_used += 1
non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
for idx in non_sys[-remaining:]:
    _apply_cache_marker(messages[idx], marker, ...)
```

**为什么值得看**：这套机制把"哪段算 cache prefix、哪段算 user 输入"的边界**与持久化边界绑死了**：所有写进 SQLite 的东西都属于 cacheable 部分；所有"只送一次给 LLM"的东西都不写盘。设计上极简但极强 —— 永远不会因为某次 plugin 多注入了一段 context 就把 caching prefix 弄断。同时 `apply_anthropic_cache_control` 还区分了 native_anthropic（marker 在 inner content blocks）vs OpenAI-wire 代理（marker 在 message envelope）两种 layout，因为 OpenRouter / MiniMax / 阿里 DashScope 等代理对 cache_control 位置的要求不同。

---

### 机制 F：动态工具 Schema 的"上下文一致性"

**作用**：保证 LLM 看到的工具列表与运行时实际能调用的工具完全一致，避免 hallucination。

**设计意图**：工具的可用性是动态的（API key 配置、Docker 状态、execute_code 沙箱模式、Discord intents 都可能变）。如果 LLM 看到工具描述里说"可以用 web_search"但实际未注册，模型会调一个不存在的工具，循环卡死。

**关键源码**（`model_tools.py:392-460` 节选）：
```python
filtered_tools = registry.get_definitions(tools_to_include, quiet=quiet_mode)

# 真正过了 check_fn 的工具名集合 —— 用这个，不要用 tools_to_include
available_tool_names = {t["function"]["name"] for t in filtered_tools}

# Rebuild execute_code schema 让它只声明真实可用的 sandbox tools
if "execute_code" in available_tool_names:
    sandbox_enabled = SANDBOX_ALLOWED_TOOLS & available_tool_names
    dynamic_schema = build_execute_code_schema(sandbox_enabled, mode=_get_execution_mode())
    # 替换 schema in place
    ...

# Discord schema 按 bot 实际 intents 重建（隐藏不可用的 action）
for discord_tool_name in _discord_schema_fns: ...

# browser_navigate 描述里删掉对不存在的 web_search/web_extract 的引用
if "browser_navigate" in available_tool_names:
    web_tools_available = {"web_search", "web_extract"} & available_tool_names
    if not web_tools_available:
        # 改写描述，去掉 "prefer web_search or web_extract"
        ...

# 进程全局 —— 子代理执行 execute_code 时也读这个
global _last_resolved_tool_names
_last_resolved_tool_names = [t["function"]["name"] for t in filtered_tools]
```

**为什么值得看**：这段代码体现了一个朴素但常被忽略的真理 —— **LLM 看到的工具描述就是它的"工具世界观"，里面任何对其他工具的引用都必须当下真实存在**。Hermes 用了三种重建（execute_code、discord、browser_navigate 描述）来动态修剪交叉引用。`_last_resolved_tool_names` 作为进程全局也是为了让 `execute_code` 在沙箱里生成代码时知道当前可用什么工具 —— 但子代理同时运行时会有竞争，所以 `handle_function_call` 又允许显式传 `enabled_tools` 覆盖这个全局（`model_tools.py:756-764`）。

---

## 5. 与其他维度的交互

```
                       ┌─────────────────────────┐
                       │   上下文管理（本维度）   │
                       └─────────────────────────┘
                          ▲           │
            error 触发    │           │ system prompt
            should_compress           ▼  (含 memory + skills)
        ┌────────────────┴──────────────────────────┐
        │                                            │
   [错误处理]                                  [Prompt 构建]
        │                                            │
        ▼                                            │
   reroute / fallback              ┌─────────────────┘
                                    │
        ┌────────────[记忆系统]◀────┘
        │ on_pre_compress           注入 memory snapshot
        │ memory provider snapshot
        ▼
   持久化用户记忆
                                    ┌─────────────┐
        [工具系统]──────tools[]────▶│ 计入 preflight│
        get_tool_definitions        │ token 估算    │
        _last_resolved_tool_names   └─────────────┘

        [状态管理]──────session_id 旋转、SQLite split──────▶
        compression 后 end_session + create_session（继承 title）

        [子 Agent 编排]──────fork 时继承 system_prompt──────▶
        delegate_task 的子 agent 拿到完整 system + 自己的 ephemeral
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|---------------|
| **依赖** | 记忆系统 | system prompt 里嵌入 MEMORY.md / USER.md 快照；压缩前调 `on_pre_compress` 让 provider 从 turn 中提取 | `run_agent.py:5208-5226` (build), `run_agent.py:9442-9446` (on_pre_compress) |
| **依赖** | Prompt 构建 | 调 `build_system_prompt()` / `build_skills_system_prompt()` / `build_context_files_prompt()` 装配上下文 | `run_agent.py:5114-5299` |
| **依赖** | 工具系统 | preflight 估算必须计入 tools schema；压缩 `_prune_old_tool_results` 知道每种工具的语义生成针对性 summary | `context_compressor.py:199-318` (`_summarize_tool_result`)；`run_agent.py:11018-11022` (estimate 含 tools) |
| **输出** | 错误处理 | `error_classifier` 把 context-length 4xx 标记 `should_compress=True`，触发 `_compress_context` | `run_agent.py:12415, 13095` (classified.should_compress) |
| **输出** | 状态管理 | 压缩成功后旋转 session_id，调 `end_session("compression")` + `create_session(parent_session_id=old)`，并在 SQLite 里通过 title 继承保留 lineage | `run_agent.py:9489-9520` |
| **输出** | 子 Agent 编排 | 子 agent 在 fork 时继承父 agent 的 cached system prompt 但有自己的 ephemeral；`_last_resolved_tool_names` 进程全局对子 agent 的影响通过 `handle_function_call(enabled_tools=...)` 显式参数覆盖 | `model_tools.py:756-764` |
| **辅助调用** | 辅助 LLM 客户端 | 压缩通过 `auxiliary_client.call_llm(task="compression", ...)` 走专用 model + provider + timeout 配置 | `context_compressor.py:870-885` |
| **协同** | Prompt Caching | system prompt 的"稳定性纪律"是 Anthropic prompt caching 工作的前提；4-breakpoint 策略对不稳定 system 完全失效 | `agent/prompt_caching.py:41-72`, `run_agent.py:11375-11380` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

代码里反映的隐含假设：

1. **辅助模型生成的摘要"够好"**：12 个 section 的结构化模板假设 LLM 能稳定填充每一节，且 "Active Task" 一节能被准确 copy verbatim。如果用极弱模型做摘要，会出现 active task 漂移。
2. **provider 回报的 `prompt_tokens` 是真实的**：`should_compress` 默认信任 `last_prompt_tokens`，仅在 0 时回退到 rough estimate。如果 provider 报错（部分 OpenAI-wire 第三方代理回 0），会推迟压缩到下一轮。
3. **prompt cache 的 prefix 稳定性比"完美 system prompt"重要**：很多动态信息（plugin context、@ 引用文件、外部 recall）被强制塞到 user 消息里 —— 假设 LLM 不会因为这些信息位置在 user 而忽视它们。
4. **tool schema 的总 token 数可估**：`estimate_request_tokens_rough(tools=...)` 假设 schema 序列化后的 token 数能用 rough char/4 估出。对多语言 + 复杂嵌套 schema 误差可能 ±20%。
5. **压缩动作"在循环边界"是足够的**：preflight + 响应后 + 错误恢复三个时机覆盖了所有需要压缩的场景；中途响应中断、流式 token 累积超阈值这种边界没有专门处理。

### 6.2 代价/风险

- **State 膨胀**。`ContextCompressor` 实例自己维护了 ~12 个 `_last_*` 字段（`_last_summary_error`, `_last_summary_dropped_count`, `_last_aux_model_failure_*`, `_ineffective_compression_count`, `_summary_failure_cooldown_until` 等），上层 `_compress_context` 在调用后必须主动 inspect 这些字段决定是否 emit warning（`run_agent.py:9455-9479`）。这种"side-channel 状态"很容易在新加分支时被忘记 inspect。
- **多次 fallback 让用户难以诊断真实失败**。aux model fail → fallback to main → main 也失败 → cooldown → 下一轮重试 …… 用户看到的可能只是一个迟到的 warning，但中间已经丢了几个 turn 的摘要保真度。
- **"orphaned tool stub" 的虚假语义**。当 tool_call 的 result 被压缩后，注入的 stub `"[Result from earlier conversation — see context summary above]"` 是占位，但模型有时会把它当真实结果继续推理（"上面写了我已经做过 X"）。
- **System prompt 时间戳每轮变化但被用做 cache prefix**。`_build_system_prompt` 把 `Conversation started: ...` 嵌进 prompt（`run_agent.py:5257-5266`）；这一行只在 build 时确定，但如果 `_invalidate_system_prompt` 被频繁触发（错误恢复时），cache 会反复失效。
- **`_last_resolved_tool_names` 是进程全局**。多代理同进程并发时（`delegate_task` 用 ThreadPoolExecutor），子代理修改这个变量会污染父代理的视图。代码用"显式 enabled_tools 参数 + 复制副本"绕开，但只对 execute_code 这一条路径生效，新工具如果也依赖这个全局会重新踩坑。
- **压缩用 4 字符 ≈ 1 token 估算**。`_CHARS_PER_TOKEN = 4` 对英文准、对中日韩文严重偏低 —— 中文一字往往 1-2 token，4 char 估算会让中文会话过晚触发压缩。

### 6.3 如果要重新设计可能改变什么

1. **把"摘要消息的 role"决策放进 ContextEngine 接口而非硬编码**。现在 `compress()` 内部根据 head/tail 邻居 role 选 user/assistant，再 fallback 到 merge-into-tail；这种"插入消息时考虑序列结构"的逻辑应当外置，因为不同 provider 对连续同 role 的容忍度不同。
2. **辅助模型的失败应该首先 surface 给 user 而不是悄悄 fallback**。现在用户看到的是 warning + "recovered using main model"；但配置一个错误的 aux model 应当被首屏突出展示，避免用户长期付主模型摘要钱却以为省钱。
3. **token 估算抽象成独立服务**。`estimate_messages_tokens_rough`、`estimate_tokens_rough`、`_content_length_for_budget` 三个函数分散在不同文件，且对图片、tool schema、CJK 字符的处理不一致。一个集中的 tokenizer 适配器（按 provider 切换）会让 preflight 决策更可靠。
4. **`_last_resolved_tool_names` 应当随上下文绑定**。现在是进程全局；改为 ContextVar 或 explicit threading-local，避免多 agent 并发污染。
5. **摘要的 12 个 section 应当可配置**。模板写死在 `_generate_summary` 里，对长尾场景（Cron 静默任务、纯代码 agent、LCM 风格的多代理）冗余。可考虑按 platform / role 选 template。
6. **"压缩后 SQLite session split"是个 heavy 操作**。每次压缩都 end + create + 重传 system prompt + auto-number title —— 实际上很多场景只需要 in-memory message 替换。可以让 split 变成可选行为而非必选。

### 6.4 对自己设计 Agent 系统的启示

最核心的两点：

1. **把上下文当做"带预算的写入流"而非"只读输入"**。不是"系统拼好上下文给 LLM 看"，而是"系统持续在多个时机（preflight / 响应后 / 错误恢复 / 手动）压缩、整形、修复"上下文。Preflight 不是可选优化 —— 它是 model switch、history 加载、长 tool result 注入这三种场景下唯一能避免硬死的办法。

2. **Cache prefix 的稳定性要写进系统纪律**。哪些字段进 system prompt 永久持久化、哪些走 ephemeral 只参与一次请求、哪些必须注入到 user 消息侧 —— 这条边界一旦定下来，就成了所有插件 / 工具 / 上层调用方都必须遵守的契约。Hermes 的 `# NOTE: ... NOT the system prompt. This is intentional` 这种代码注释是给未来维护者的"反复提醒"，比单纯的接口约束更管用。

附加但重要的一点：**LLM 生成的摘要要带"自我定位 wrapper"**（`SUMMARY_PREFIX` + END marker），别假设 role 隔离能让模型理解"这是历史不是当前指令"。模型很弱时这个 wrapper 是它续行不出错的唯一锚。
