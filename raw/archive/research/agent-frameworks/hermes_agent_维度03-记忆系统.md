# 维度名：记忆系统（Memory System）

## 1. 一句话定位

Hermes 的记忆系统是一个**双层架构**：①**内置 MemoryStore**（`MEMORY.md`+`USER.md`）以"载入时冻结快照、写入时落盘"的方式提供 prefix-cache 友好的持久笔记；②**MemoryProvider 插件层**通过抽象接口让 Honcho/Mem0/Holographic/Supermemory 等外部后端以"prefetch→注入用户消息+sync_turn→后台回写"的统一节奏接入，全程做到**单失败不阻塞模型回复、单后端独占工具命名空间**。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

**反推 1：没有 MemoryProvider ABC（直接硬编码 Honcho/Mem0）**
`run_agent.py:1762-1818` 通过 `_mem_provider_name = mem_config.get("provider", "")` 读取一行配置就能切换后端。如果没有 ABC，每接一个新后端都要在 `run_agent.py` 中添加：① 启动条件分支、② prefetch 调用点、③ sync_turn 调用点、④ 工具 schema 注入、⑤ 工具调用路由分发、⑥ on_session_end 清理。`run_agent.py` 已经超过 11 K 行，再 6 处 × 4 个后端 = 24 处分支会让这个文件无法维护，并且每加一个后端都要改主流程文件。

**反推 2：没有"frozen snapshot"模式（每轮重新读 MEMORY.md）**
`tools/memory_tool.py:138-142` 在 `load_from_disk()` 时**一次性**把 MEMORY/USER 块 render 进 `_system_prompt_snapshot`，并在 `format_for_system_prompt()` 中只返回这个快照。如果每轮都重新读文件、重新渲染：① 模型对 MEMORY 块加自我修正（add）后，下一轮 system prompt 文本变化 → **整个 system prompt 的 prefix cache 失效** → 每轮重缴 cache write 成本 + 几秒延迟。`tools/memory_tool.py:11-14` 注释明确写："Mid-session writes update files on disk immediately (durable) but do NOT change the system prompt — this preserves the prefix cache for the entire session."

**反推 3：没有"context fence"机制（直接把外部 prefetch 拼到用户消息）**
`agent/memory_manager.py:43-58` 定义了 `<memory-context>` fence + `[System note: …]` 提示，并在 `sanitize_context()` 中先**剥离**外部 provider 自带的 fence。如果没有这层封装：① 模型可能把召回出来的"用户偏好"误读为"用户当前要求"（因为它们都被拼到 user 消息里），② 如果 Honcho 召回内容被回流到 `sync_turn` → 下次召回 → 再回流，会形成"用户说过 X"的伪记忆滚雪球。

**反推 4：没有"单 external provider"约束**
`agent/memory_manager.py:213-225` 明确拒绝第二个非 builtin provider。如果允许多个：① 工具名冲突（Honcho、Mem0、Supermemory 都会注册 `*_search`、`*_profile`），② 每轮 prefetch 都要并发调用 N 个 HTTP 后端，时间×N，③ 模型 schema 暴增导致 token 浪费且容易选错工具。

### 2.2 触发条件

| 触发点 | 代码位置 | 条件 |
|--------|----------|------|
| MemoryStore 加载 | `run_agent.py:1745` | `mem_config.memory_enabled` or `user_profile_enabled` 为真 |
| 外部 provider 加载 | `run_agent.py:1764` | `mem_config.provider` 非空字符串 + `is_available()` 返回 True |
| Provider 拒绝（cron 上下文） | `plugins/memory/honcho/__init__.py:286-290` | `agent_context in ("cron","flush")` 或 `platform == "cron"` |
| prefetch 注入 | `run_agent.py:11150-11154`、`run_agent.py:11313-11316` | 每轮 API 调用前一次，缓存到 `_ext_prefetch_cache`，注入到当前 user 消息 |
| sync_turn 触发 | `run_agent.py:4951-4961` | `final_response and original_user_message and not interrupted` |
| on_session_switch | `run_agent.py:9545-9551` | session_id 因 `/resume`、`/branch`、`/reset`、context compression 而轮换 |
| on_pre_compress | `run_agent.py:9442-9446` | 即将进入 `context_compressor.compress()` 之前 |
| on_memory_write 桥接 | `run_agent.py:9725-9737` | 内置 memory tool 执行 `add` 或 `replace` 后，把写入镜像给外部 provider |
| 子 agent 跳过 memory | `run_agent.py:962`+`1739` | `skip_memory=True` 时整个内置 store 和 provider 都不实例化（subagent/cron/batch_runner/test 均传此标志） |

---

## 3. 核心设计思路

### 3.1 抽象模型

**"Manager-Provider 编排 + 双流注入"模式**：

```python
# 伪代码：每轮的记忆生命周期
def each_turn(user_msg):
    # ① 静态层：内置 MemoryStore frozen snapshot 已在 system prompt
    # ② 动态层：每轮调用前同步取一次 prefetch
    memory_manager.on_turn_start(turn_n, user_msg)              # provider 调整 cadence
    ext_ctx = memory_manager.prefetch_all(user_msg)             # 拉所有 provider 的 recall
    
    # ③ 注入：fence + system note 包裹后,拼到当前 user 消息末尾(不改写原 messages)
    api_messages[current_turn_user_idx]["content"] += build_memory_context_block(ext_ctx)
    
    response = call_model(api_messages)
    
    # ④ 写入：完成后回写 + 触发下一轮的后台 prefetch
    if not interrupted:
        memory_manager.sync_all(user_msg, response)             # 持久化本轮
        memory_manager.queue_prefetch_all(user_msg)             # 启动后台线程为下一轮预取

# 工具调用分发(完全独立的入口)
def handle_tool_call(name, args):
    if name == "memory":               # 内置 — 写 MEMORY.md/USER.md
        result = memory_tool(...)
        memory_manager.on_memory_write("add", target, content)  # 桥接给外部 provider
    elif memory_manager.has_tool(name):  # 外部 — honcho_*/mem0_*/fact_store
        return memory_manager.handle_tool_call(name, args)
```

**核心抽象 = 三种数据通路并存**：①**永久层**（MEMORY.md/USER.md frozen 进 system prompt）→ 解决"跨会话稳定的人设/偏好"；②**召回层**（prefetch → user message）→ 解决"针对当前问题的语义召回"；③**工具层**（模型主动调用）→ 解决"模型按需深挖"。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 内置 MEMORY/USER 用 frozen snapshot 而非 live state | 加载时 render 一次到 `_system_prompt_snapshot`（`tools/memory_tool.py:138-142`），mid-session 写入只落盘不刷 prompt | 每轮重新读文件再注入 system | `tools/memory_tool.py:11-14` 直接注释了原因："This keeps the system prompt stable across all turns, preserving the prefix cache." 在长会话里 prefix cache 写入成本 ≫ snapshot 略微滞后的代价。新写入会在**下次会话启动**生效。 |
| 外部 recall 注入 user message 而非 system prompt | `run_agent.py:11311-11322` 仅当 `idx == current_turn_user_idx` 时把 fence 块拼到 user 消息末尾 | 注入到 system prompt | 同理 prefix cache：每轮召回内容不同，若进 system prompt 会让 cache 完全失效；进 user 消息只是当轮 token 增加，前缀 cache 不变。同时**不修改原 messages**（`api_msg = msg.copy()`），保证不污染会话持久化 |
| MemoryProvider 用 ABC 插件而非硬编码 | `agent/memory_provider.py:42` `class MemoryProvider(ABC)` + `plugins/memory/__init__.py:160` `load_memory_provider(name)` 动态发现 | 在 `run_agent.py` 中 if/elif 分发 | 主入口仅一行 `_mp = _load_mem(_mem_provider_name)`（`run_agent.py:1768`）就能切换；新加后端不改主流程；用户可在 `$HERMES_HOME/plugins/<name>/` 放自己的实现（`plugins/memory/__init__.py:86-96`） |
| 一次只允许一个 external provider | `agent/memory_manager.py:213-225` 第二个非 builtin provider 会被 `_has_external` 拒绝 | 允许多个 provider 并存 | 注释直接写了原因："This prevents tool schema bloat and conflicting memory backends." Honcho 5 个工具 + Mem0 3 个 + Supermemory 若干 = 工具数翻倍，模型选错风险倍增 |
| 任一 provider 失败永不阻塞主流程 | `agent/memory_manager.py:296-302/318-326/342-345` 等几乎所有 manager 方法都用 `try/except + logger` 包裹 | 失败抛异常让上层处理 | 注释 "Failures in one provider never block the other"。`run_agent.py:4946` 也强调 "external memory providers are strictly best-effort — a misconfigured or offline backend must not block the user from seeing their response" |
| streaming context fence 用单独状态机而非一次性正则 | `agent/memory_manager.py:62-170` 实现 `StreamingContextScrubber` | 用 `sanitize_context()` 一次性正则替换 | 注释解释："a `<memory-context>` opened in one delta and closed in a later delta leaks its payload to the UI because the non-greedy block regex needs both tags in one string"。流式场景 tag 可能跨 delta 边界，必须状态机 |

### 3.3 数据流 / 控制流

```
┌─────────────────────────────────────────────────────────────────────┐
│  启动时 (run_agent.py:1739-1818)                                     │
│  ┌───────────────────────────┐    ┌────────────────────────────┐    │
│  │ MemoryStore.load_from_disk│    │ load_memory_provider(name) │    │
│  │ → _system_prompt_snapshot │    │ → manager.add_provider(_mp)│    │
│  │   (MEMORY.md, USER.md)    │    │ → initialize_all(...)      │    │
│  └─────────┬─────────────────┘    └────────────┬───────────────┘    │
└────────────┼──────────────────────────────────┼────────────────────┘
             │                                  │
             ▼                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│ build_system_prompt (run_agent.py:5208-5226)                       │
│  prompt_parts.append(_memory_store.format_for_system_prompt(...))  │
│  prompt_parts.append(_memory_manager.build_system_prompt())        │
│  → 静态 system prompt，整轮稳定，prefix cache 友好                  │
└────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│ 每轮入口 (run_agent.py:11138-11154)                                 │
│  ① on_turn_start(turn_n, msg)         → provider 更新 cadence       │
│  ② _ext_prefetch_cache = prefetch_all(original_user_message)       │
│     (一次性，整个 tool loop 复用,避免重复 RPC)                      │
└────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│ 每次 API call 构建 api_messages (run_agent.py:11302-11322)          │
│  api_msg = msg.copy()                  # 不污染原 messages          │
│  if idx == current_turn_user_idx:                                  │
│      fenced = build_memory_context_block(_ext_prefetch_cache)      │
│      api_msg["content"] += "\n\n" + fenced                         │
└────────────────────────────────────────────────────────────────────┘
             │
             ▼ (response)
┌────────────────────────────────────────────────────────────────────┐
│ 工具分发 (run_agent.py:9712-9740, 10324-10422)                      │
│  if name == "memory" → memory_tool(store=_memory_store)            │
│      → on_memory_write(...)            # 桥接给外部 provider        │
│  elif manager.has_tool(name) → manager.handle_tool_call(name, args)│
└────────────────────────────────────────────────────────────────────┘
             │
             ▼ (turn done)
┌────────────────────────────────────────────────────────────────────┐
│ 回写 (run_agent.py:4949-4963)                                       │
│  manager.sync_all(user_msg, final_response)   # 后台线程持久化      │
│  manager.queue_prefetch_all(user_msg)          # 后台线程预热下轮    │
└────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│ 边界事件                                                            │
│  压缩前 (run_agent.py:9442) → on_pre_compress(messages)            │
│  压缩后 (run_agent.py:9545) → on_session_switch(new_sid, …)        │
│  会话结束 (run_agent.py:4885) → on_session_end + shutdown_all      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：MemoryProvider ABC + 单 external 强约束

**作用**：把"记忆后端的接入"从 N 个 if/elif 分支抽象成统一的生命周期接口；并以工程而非配置的方式禁止双 external，避免工具命名空间污染。

**设计意图**：避免 `run_agent.py` 因每接一个后端就膨胀 6-8 处分支；同时通过"第一个 external 占坑"的逻辑，让插件作者**不必关心冲突**——MemoryManager 负责拒绝。

**关键源码**（`agent/memory_manager.py:204-243`）：
```python
def add_provider(self, provider: MemoryProvider) -> None:
    is_builtin = provider.name == "builtin"
    if not is_builtin:
        if self._has_external:                       # ① 已有 external 时直接拒绝,不静默覆盖
            existing = next(
                (p.name for p in self._providers if p.name != "builtin"), "unknown"
            )
            logger.warning(
                "Rejected memory provider '%s' — external provider '%s' is "
                "already registered. ...", provider.name, existing,
            )
            return
        self._has_external = True
    self._providers.append(provider)
    for schema in provider.get_tool_schemas():       # ② 同时建立 tool→provider 路由表
        tool_name = schema.get("name", "")
        if tool_name and tool_name not in self._tool_to_provider:
            self._tool_to_provider[tool_name] = provider
        elif tool_name in self._tool_to_provider:    # ③ 工具名同样冲突警告(防止同后端内重名)
            logger.warning("Memory tool name conflict: '%s' ...", tool_name)
```

**为什么值得看**：① 三步把"插件注册 + 工具路由 + 冲突防护"一次到位，没有运行时再做 dispatch 表查找的开销；② "拒绝而非覆盖"是个有意识的反默认选择——**如果默认是覆盖，老用户切配置时会丢失记忆而无报错**；③ 把 `_tool_to_provider` 在注册时就建好，等价于"插件路由提前到 init"，所以 `handle_tool_call(name, args)` 的实际派发只是一次 dict lookup（`agent/memory_manager.py:364`）。

---

### 机制 B：Frozen snapshot — 让内置 memory 与 prefix cache 共存

**作用**：MEMORY.md/USER.md 的写入立即落盘（durable），但 system prompt 中只用"载入时的快照"，本会话内永不刷新。

**设计意图**：长会话中如果 system prompt 内容随每次 add/replace 变化，就完全摧毁了 LLM provider 的 prefix cache（缓存命中是按 token 完全匹配的）。这里用一个"会话内一致 + 跨会话刷新"的折衷策略，把 cache 命中维持到极限。

**关键源码**（`tools/memory_tool.py:138-142, 361-372`）：
```python
def load_from_disk(self):
    ...
    # ① 一次性把当前磁盘内容渲染成 frozen 块
    self._system_prompt_snapshot = {
        "memory": self._render_block("memory", self.memory_entries),
        "user":   self._render_block("user",   self.user_entries),
    }

def format_for_system_prompt(self, target: str) -> Optional[str]:
    # ② 永远返回 _system_prompt_snapshot,不读 self.memory_entries
    block = self._system_prompt_snapshot.get(target, "")
    return block if block else None
```

**为什么值得看**：用一个 dict 字段就把"durable 写入"与"prompt 稳定"两个相反目标解耦。**写流程**走 `add()`/`replace()`/`remove()` → 落盘；**读流程**走 `format_for_system_prompt()` → snapshot。两条路径互不影响。代价是新写入要等下一会话才能"被记忆"，但这是一个比"prefix cache 失效"轻得多的代价（注释里也明确"refreshes on the next session start"）。

---

### 机制 C：双流注入 — 静态进 system，动态进 user

**作用**：把"静态的提供者描述（如 'Honcho Memory active, use these tools …'）"放进 system prompt（缓存友好），把"动态的召回结果"拼到当前 user 消息末尾（不破坏前缀缓存）。

**设计意图**：同一个 provider 既要让模型**知道**它存在（指令信息要进 system），又要让模型**用到**它召回的内容（每轮变化的内容必须可变）。这两类信息走两条不同通路。

**关键源码**（`run_agent.py:5219-5226`、`11302-11322`）：
```python
# 静态描述 → system prompt 一次性 append
if self._memory_manager:
    _ext_mem_block = self._memory_manager.build_system_prompt()
    if _ext_mem_block:
        prompt_parts.append(_ext_mem_block)

# ----------- 每轮 API call ---------------
api_messages = []
for idx, msg in enumerate(messages):
    api_msg = msg.copy()                          # ① 关键:copy 而非引用,不污染会话持久化
    if idx == current_turn_user_idx and msg.get("role") == "user":
        _injections = []
        if _ext_prefetch_cache:                   # ② 召回结果只在当轮拼接
            _fenced = build_memory_context_block(_ext_prefetch_cache)
            if _fenced:
                _injections.append(_fenced)
        if _injections:
            _base = api_msg.get("content", "")
            if isinstance(_base, str):
                api_msg["content"] = _base + "\n\n" + "\n\n".join(_injections)
    api_messages.append(api_msg)
```

**为什么值得看**：注释里有句关键的话——"the original message in `messages` is never mutated, so nothing leaks into session persistence"。这条不变量保证了：① 召回内容不被回流到 sync_turn → 不会形成"我说过 X"的伪记忆；② 切换 provider/重启不丢失原始对话；③ 重新跑同一会话能复现（因为原 messages 是确定性的）。一个 `.copy()` 实现了三个性质。

---

### 机制 D：streaming-aware fence scrubber — 防泄漏的状态机

**作用**：当 LLM 在流式输出里回声（echo）了 `<memory-context>...</memory-context>` 标签时，跨 chunk 边界仍能可靠地剥离掉，避免内部上下文出现在用户屏幕上。

**设计意图**：`<memory-context>` 是注入用 fence，模型理论上不应输出。但"模型可能学到这种模式并 echo 出来"是真实风险（特别是 base 模型或越狱场景）。一次性正则在 streaming 下不够用——open tag 可能在 chunk N，close tag 可能在 chunk N+5。

**关键源码**（`agent/memory_manager.py:99-140`）：
```python
def feed(self, text: str) -> str:
    if not text:
        return ""
    buf = self._buf + text                        # ① 拼上次 hold-back 的尾巴
    self._buf = ""
    out: list[str] = []
    while buf:
        if self._in_span:                         # ② 当前在 span 内 — 全部丢弃直到找到 </memory-context>
            idx = buf.lower().find(self._CLOSE_TAG)
            if idx == -1:
                held = self._max_partial_suffix(buf, self._CLOSE_TAG)
                self._buf = buf[-held:] if held else ""
                return "".join(out)               # ③ 找不到 → hold 住可能的部分 close,丢弃 span 内容
            buf = buf[idx + len(self._CLOSE_TAG):]
            self._in_span = False
        else:                                     # ④ 当前在 span 外 — 找 open tag,只对其前内容 emit
            idx = buf.lower().find(self._OPEN_TAG)
            if idx == -1:
                held = self._max_partial_suffix(buf, self._OPEN_TAG)
                if held:
                    out.append(buf[:-held]); self._buf = buf[-held:]
                else:
                    out.append(buf)
                return "".join(out)
            if idx > 0: out.append(buf[:idx])
            buf = buf[idx + len(self._OPEN_TAG):]
            self._in_span = True
```

**为什么值得看**：① `_max_partial_suffix` 是关键——既不能把 `<memo` 当普通文本输出（万一下一 chunk 是 `ry-context>` 就漏了），也不能 hold 住整个 buffer（性能差）。它精确地 hold 住"可能是 tag 前缀"的最长后缀。② `flush()`（line 142）中 "If we're still inside an unterminated span the remaining content is discarded (safer: leaking partial memory context is worse than a truncated answer)" 的注释体现了一个明确的安全权衡：**信息泄漏 > 输出截断**。

---

### 机制 E：Honcho 的 cadence + backoff — 把"每轮调用"做成"按需 + 防退化"

**作用**：Honcho 的 dialectic 调用昂贵（一次 LLM reasoning），不能每轮都打。用 `dialecticCadence` 控制最小间隔，再用"empty-streak backoff"在后端持续返回空时指数式拉长。

**设计意图**：Hermes 把"recall 时机"决策权交给 provider 自己（`MemoryManager.prefetch_all()` 只是周期性问"现在你想给点啥吗"）。Honcho 内部要解决的问题是：① 频繁打 = 钱多 + 慢；② 不打 = recall 失效。代码用 cadence 做基础节流，再用 streak 做自适应。

**关键源码**（`plugins/memory/honcho/__init__.py:825-832, 738-748`）：
```python
def _effective_cadence(self) -> int:
    """Cadence plus empty-streak backoff, capped at _BACKOFF_MAX × base."""
    if self._dialectic_empty_streak <= 0:
        return self._dialectic_cadence
    widened = self._dialectic_cadence + self._dialectic_empty_streak
    ceiling = self._dialectic_cadence * self._BACKOFF_MAX        # 8× 上限
    return min(widened, ceiling)

# queue_prefetch 中的应用:
effective = self._effective_cadence()
if (self._turn_count - self._last_dialectic_turn) < effective:
    return                                                       # 跳过本轮
# … 启动后台线程,只有非空结果才推进 _last_dialectic_turn
```

**为什么值得看**：① 把"empty streak"作为状态变量，让 cadence 自适应而非靠 hard-coded 配置——这是真实可观测的反馈控制；② capped at `_BACKOFF_MAX × base` 防止退化到永不调用（让退化曲线有上界，跟 TCP backoff 思路一致）；③ "Cadence advances only on a non-empty result"（line 750-766）这个细节防止一次失败让节流计数前进，相当于把节流和成功率耦合起来。这是个**很值得借鉴**的"最小可观测自适应模式"。

---

### 机制 F：on_memory_write 桥接 — 让两层共享"用户偏好"

**作用**：当模型用内置 `memory(action="add", target="user", ...)` 写入 `USER.md` 时，自动把这条事实**镜像**给外部 provider（如 Honcho 的 `create_conclusion`）。

**设计意图**：用户写在 USER.md 的偏好（如"我喜欢简洁回复"）是高质量人工 ground truth，外部 provider 也应该看到。但反过来不成立——外部 provider 召回出来的"猜测"不应自动写入 USER.md（那是模型主动决策的范畴）。

**关键源码**（`run_agent.py:9725-9737` + `agent/memory_manager.py:483-511`）：
```python
# 调用点(run_agent.py)
if self._memory_manager and function_args.get("action") in ("add", "replace"):
    self._memory_manager.on_memory_write(
        function_args.get("action", ""), target,
        function_args.get("content", ""),
        metadata=self._build_memory_write_metadata(...),         # 携带 task_id/tool_call_id 等溯源
    )

# 分发(memory_manager.py)
def on_memory_write(self, action, target, content, metadata=None):
    for provider in self._providers:
        if provider.name == "builtin":                           # ① 跳过 builtin —— 它就是写入源,避免回流
            continue
        try:
            metadata_mode = self._provider_memory_write_metadata_mode(provider)  # ② 兼容老 plugin 的签名
            if metadata_mode == "keyword":
                provider.on_memory_write(action, target, content, metadata=dict(metadata or {}))
            elif metadata_mode == "positional":
                provider.on_memory_write(action, target, content, dict(metadata or {}))
            else:
                provider.on_memory_write(action, target, content)  # 老 plugin 不带 metadata 参数
        except Exception as e:
            logger.debug(...)
```

**为什么值得看**：① "skip builtin" 这一行避免了 self-loop；② `_provider_memory_write_metadata_mode` 用 `inspect.signature` 在调用点动态判断 provider 的方法签名（`agent/memory_manager.py:457-481`），实现了**前向兼容**——老 plugin 没有 `metadata` 参数也能照常工作。这是一种"对插件作者友好"的 API 演进策略，比直接强制要求新签名优雅得多。

---

## 5. 与其他维度的交互

```
                  ┌───────────────────────┐
                  │  记忆系统 (Memory)     │
                  └───────────────────────┘
                         ▲      │
   工具系统 ─────────────┘      │── prompt 构建：build_system_prompt() 注入 frozen snapshot
   编排循环 ────────────────────┴── 每轮注入 prefetch / 每轮触发 sync
   状态管理 ── session_id 轮换 ──> on_session_switch()
   上下文管理 ── 压缩前 ─────────> on_pre_compress() (provider 抢救要点)
   子 Agent ── skip_memory=True ─> 完全不实例化(避免污染父 session 记忆)
   安全防护 ── _scan_memory_content() ── 注入/外泄模式黑名单
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|---------------|
| 输出到 | Prompt 构建 | 静态 system prompt 块（builtin frozen snapshot + provider 描述）| `run_agent.py:5208-5226` `format_for_system_prompt()`、`build_system_prompt()` |
| 输出到 | 编排循环（每轮 message 构造）| 召回内容 fence-wrap 后拼到当前 user 消息 | `run_agent.py:11313-11322` `build_memory_context_block()` |
| 输出到 | 工具系统 | 外部 provider 的工具 schema 注入 self.tools | `run_agent.py:1826-1840` `get_all_tool_schemas()` |
| 依赖 | 编排循环 | 每轮回调 `on_turn_start`/`prefetch_all`/`sync_all`/`queue_prefetch_all` | `run_agent.py:11138-11154` + `4951-4961` |
| 依赖 | 状态管理 | session_id 切换通知 | `run_agent.py:9545-9551` `on_session_switch()` |
| 依赖 | 上下文管理（压缩） | 压缩前给 provider 一次抢救机会 | `run_agent.py:9442-9446` `on_pre_compress()` |
| 依赖 | 子 Agent 编排 | `skip_memory=True` 时整个系统不启动 | `run_agent.py:962+1739+1760` |
| 依赖 | 工具系统 | 工具调用按 `tool_to_provider` 路由 | `run_agent.py:9739-9740` + `agent/memory_manager.py:356-374` |
| 双向 | 内置 ↔ 外部 provider | `memory` 工具写入时桥接给外部 | `run_agent.py:9725-9737` `on_memory_write()` |
| 输出到 | 安全防护 | 注入内容前用黑名单扫描 | `tools/memory_tool.py:67-104` `_scan_memory_content()` |
| 输出到 | 流式输出 | 每个 chunk 经 `StreamingContextScrubber.feed()` 过滤 | `run_agent.py:1309`+`6922` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **"一次只用一个外部记忆后端就够了"** ——`agent/memory_manager.py:213-225` 的硬约束体现了这个假设。如果有用户希望"Honcho 做用户建模 + Holographic 做事实存储"组合用，他们就需要分两个 profile 或两个 session。
2. **"召回内容不应进入持久化 messages"** —— 通过 `api_msg = msg.copy()`（`run_agent.py:11304`）避免回流。这隐含了"召回内容是衍生数据"的判断。
3. **"prefix cache 命中价值 > 实时性"** —— frozen snapshot 模式假设"会话内的少量过时"换"整段 system prompt 的稳定缓存"是划算的。对短会话不划算，对长会话很划算。
4. **"Provider 失败应静默"** —— 几乎所有 manager 方法用 `try/except + logger.debug`。这假设"召回失败 = 当轮没召回"是可接受的体验，比"召回失败 = 用户看不到回答"好得多。
5. **"模型不会恶意 echo `<memory-context>`"，但也"必须能防住模型 echo"** —— 一边在 prompt 里告诉模型这是"system note，不要当成用户输入"，一边在流式管道里部署 `StreamingContextScrubber`。这是双层 belt-and-suspenders。
6. **"内置 memory 是高质量信号源，外部是噪声放大器"** —— `on_memory_write` 只往外**镜像**，不反向；外部 provider 的 conclusions 不会自动写入 USER.md（必须靠模型显式调 `memory` 工具）。

### 6.2 代价 / 风险

1. **frozen snapshot 让"立即生效"反直觉** —— 用户在会话中说"记住我喜欢简洁回复"，模型 add 到 USER.md，但**本会话不会变得更简洁**（system prompt 不刷新）。要等下次会话才生效。`tools/memory_tool.py:11-14` 注释承认了这一点。普通用户第一次遇到会困惑。
2. **MemoryProvider ABC 已经膨胀到 11 个 hook** ——`memory_provider.py` 包含 `initialize/system_prompt_block/prefetch/queue_prefetch/sync_turn/get_tool_schemas/handle_tool_call/shutdown/on_turn_start/on_session_end/on_session_switch/on_pre_compress/on_delegation/on_memory_write/get_config_schema/save_config/post_setup`。新插件作者需要理解所有这些时机。许多是 optional，但接口的"广度"成了认知负担。
3. **跨会话 session 隔离逻辑分散在 provider 内部** —— `_session_key` 由 `cfg.resolve_session_name()`（Honcho line 366-376）解析，每个 provider 自己实现。MemoryManager 不强制 session 模型。如果以后想统一审计"用户 X 在所有 provider 中存了什么"，要逐个 provider 查询。
4. **"single external provider"约束在多用户 gateway 场景下显得僵硬** —— Telegram 群组里多个用户共用同一个 agent 进程时，所有用户共用同一个 Honcho session_key（除非 provider 自己用 `gateway_session_key` 隔离）。这个负担又落到 provider 实现者身上。
5. **`on_memory_write` 的 `inspect.signature` 兼容代码** —— `memory_manager.py:457-481` 是为兼容老插件的 metadata 参数引入的，这种"反射式向后兼容"虽然友好，但每次调用都要走一次 inspect（虽缓存方便），加大了未来重构成本（老 plugin 永远拖着新接口）。
6. **集成点散布在 `run_agent.py` 多个位置** —— 共有 25+ 处 `_memory_manager` 引用（init/prompt 构建/每轮入口/工具分发/sync/压缩/会话结束/会话切换）。MemoryManager 自己很整洁，但**编排层依然 fragile**——任何一处忘了 try/except 都可能让后端故障传播到主流程。

### 6.3 如果要重新设计可能改变什么

1. **把 `run_agent.py` 中的 25+ 处集成点收敛到一个 `MemoryLifecycleHooks` 装饰器** —— 让主流程只调用一次 `with memory_lifecycle(...) as ctx:` 风格的上下文管理器，而不是每个事件都自己 try/except 包裹。
2. **把 frozen snapshot 改成"懒刷新 + 标记位"** —— 当 mid-session add 后设置 `_dirty=True`，下次 system prompt build 时检测 cache token 余量是否仍允许刷新；token 余量不足时退化为 "append-only" 把新条目附在 user message 而不是改 system prompt。
3. **把 cadence/backoff 抽到 MemoryManager 层** —— Honcho 自己实现的 `_effective_cadence` 是个好模式，但每个 provider 重复实现。可以提供一个 `CadencedRecaller` mixin。
4. **支持"namespaced provider 组合"** —— 允许多 provider 共存的前提是工具命名严格 namespace（`mem0.search`/`honcho.search`），让模型按 prefix 路由。当前的"single external"约束是为了避免命名冲突，但 namespace 是更通用的解。
5. **统一"召回内容生命周期"为可观测对象** —— 现在 prefetch 的 cache 是字符串，无法知道它来自哪个 provider、什么时候过期、是否被消费。如果改成 `RecallSnapshot(provider_name, ttl, content, fired_at)`，就能做"召回 attribution + cache hit rate"等可观测性。
6. **把 `on_memory_write` 的 inspect-based 兼容删除** —— 强制所有新 provider 实现 `on_memory_write(action, target, content, metadata=None)`，老插件给一次 deprecation period。代码一下子能简化几十行。

### 6.4 对自己设计 Agent 系统的启示

1. **"双流注入"是 prefix cache 与 dynamic recall 共存的标准答案** —— 静态 → system，动态 → user message。任何"想加点上下文"的需求都该先问"它每轮都变吗？"，再决定走哪条路。
2. **Provider/Manager 模式适合"功能形状一致、后端可插拔"的场景** —— Memory 是教科书例子。同样的模式可用于：embedding 后端、log sink、metric exporter。关键是**接口稳定 + 单失败不阻塞**。
3. **"frozen snapshot 换 prefix cache"在 LLM 时代是关键性能模式** —— 任何"会随时间变化、但短期可视为常量"的数据（用户 profile、项目元数据、能力清单）都该考虑这种策略。代价是延迟生效，收益是缓存命中。
4. **"failure is best-effort by default"的 try/except 编排** —— 在外部 IO 密集的 agent 主路径里，把所有副作用都用 `try/except + logger.debug` 包起来不是偷懒，是显式的"非阻塞契约"。但要小心：如果 happy path 已经依赖某些"副作用应该成功"的事件，这种契约会让 bug 静默几个月。
5. **任何"插入到模型上下文里的内容"都需要 fence + scrubber 的 belt-and-suspenders 防泄漏** —— 单靠 prompt 里的 "[System note]" 不够，必须在流式输出管道里部署状态机，并明确"信息泄漏 > 输出截断"的安全顺序。
6. **API 演进用 `inspect.signature` 做兼容是友好但有代价的** —— 新接口推出时，旧实现照常工作；但每次都要付反射代价，且永远拖着旧签名。值得借鉴，但要给老接口设 deprecation deadline。
