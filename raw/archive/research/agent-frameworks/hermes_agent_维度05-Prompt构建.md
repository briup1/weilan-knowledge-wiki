# 维度5：Prompt构建（Prompt Building）

## 1. 一句话定位

Prompt构建维度负责将Agent的"身份、能力、记忆、环境、技能索引"等多源信息按严格优先级组装成稳定的系统提示，并在API调用前叠加瞬态指令与缓存控制标记，以最大化多轮对话的prefix cache命中率并降低token成本。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **身份漂移**：若无`SOUL.md`作为首要身份槽位，Agent将回退到硬编码的`DEFAULT_AGENT_IDENTITY`（`agent/prompt_builder.py:L134-L142`），导致不同会话间人格不一致；网关多平台并发时，各会话可能加载错误的项目上下文（如把hermes-agent自身的`AGENTS.md`当成用户项目上下文）。
- **技能污染**：若无`_skill_should_show()`的条件过滤，当用户禁用某toolset（如`disabled_toolsets=["browser"]`）时，系统提示仍会列出依赖browser的技能，模型会尝试调用不存在的工具，触发API 400错误（`tools not found`）。
- **缓存失效**：若无`_cached_system_prompt`的会话级缓存与SQLite持久化，每次轮询都重建系统提示会导致Anthropic prefix cache完全失效，多轮对话成本上升约4倍（`run_agent.py:L10963-L10976`注释明确说明"producing a different system prompt and breaking the Anthropic prefix cache"）。
- **prompt injection**：若无`_scan_context_content()`扫描，恶意`.cursorrules`或`AGENTS.md`可通过"ignore previous instructions"等模式劫持Agent行为（`agent/prompt_builder.py:L36-L47`定义了9类威胁模式）。

### 2.2 具体触发条件（代码中的判断逻辑）

| 机制 | 触发条件 | 代码位置 |
|------|---------|---------|
| 系统提示重建 | `self._cached_system_prompt is None`（首次会话或压缩后失效） | `run_agent.py:L10963` |
| 上下文文件加载 | `not self.skip_context_files`且`TERMINAL_CWD`或`os.getcwd()`存在匹配文件 | `run_agent.py:L5246-L5252` |
| 技能索引过滤 | `has_skills_tools = any(name in self.valid_tool_names for name in ['skills_list', 'skill_view', 'skill_manage'])` | `run_agent.py:L5228` |
| prompt injection扫描 | 所有上下文文件（SOUL.md/AGENTS.md/.cursorrules/.hermes.md）加载时必经`_scan_context_content()` | `agent/prompt_builder.py:L55-L73` |
| 工具使用强制引导注入 | `_inject = any(p in model_lower for p in TOOL_USE_ENFORCEMENT_MODELS)`（gpt/codex/gemini/grok等） | `run_agent.py:L5188` |
| Anthropic缓存控制 | `self._use_prompt_caching`为True（由`_anthropic_prompt_cache_policy()`根据provider/model判定） | `run_agent.py:L11375` |
| 预填充消息注入 | `self.prefill_messages`非空，在API调用时插入system prompt之后 | `run_agent.py:L11363-L11366` |
| 上下文压缩预检 | `len(messages) > protect_first_n + protect_last_n + 1`且`_preflight_tokens >= threshold_tokens` | `run_agent.py:L11011-L11024` |

---

## 3. 核心设计思路

### 3.1 抽象模型

```python
# 伪代码：系统提示的层次化组装（洋葱模型）
def assemble_system_prompt() -> str:
    layers = []
    
    # Layer 1: 身份（最稳定，缓存核心）
    layers.append(load_soul_md() or DEFAULT_AGENT_IDENTITY)
    
    # Layer 2: 产品自指引导
    layers.append(HERMES_AGENT_HELP_GUIDANCE)
    
    # Layer 3: 工具感知行为引导（条件注入）
    if has_tool("memory"): layers.append(MEMORY_GUIDANCE)
    if has_tool("session_search"): layers.append(SESSION_SEARCH_GUIDANCE)
    if has_tool("skill_manage"): layers.append(SKILLS_GUIDANCE)
    if has_tool("kanban_show"): layers.append(KANBAN_GUIDANCE)
    
    # Layer 4: 模型家族特化引导
    if model in TOOL_USE_ENFORCEMENT_MODELS: layers.append(TOOL_USE_ENFORCEMENT_GUIDANCE)
    if "gemini" in model: layers.append(GOOGLE_MODEL_OPERATIONAL_GUIDANCE)
    if "gpt" in model: layers.append(OPENAI_MODEL_EXECUTION_GUIDANCE)
    
    # Layer 5: 用户/网关传入的系统消息
    layers.append(system_message)
    
    # Layer 6: 持久记忆（MEMORY.md + USER.md）
    layers.append(memory_store.format_for_system_prompt())
    layers.append(memory_store.format_for_system_prompt("user"))
    
    # Layer 7: 外部记忆提供者
    layers.append(memory_manager.build_system_prompt())
    
    # Layer 8: 技能索引（条件过滤 + 双层缓存）
    layers.append(build_skills_system_prompt(available_tools, available_toolsets))
    
    # Layer 9: 项目上下文文件（优先级：.hermes.md > AGENTS.md > CLAUDE.md > .cursorrules）
    layers.append(build_context_files_prompt(cwd, skip_soul=True))
    
    # Layer 10: 时间戳与元数据
    layers.append(timestamp_line + model/provider info)
    
    # Layer 11: 平台格式提示
    layers.append(PLATFORM_HINTS.get(platform, ""))
    
    return "\n\n".join(layers)
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **系统提示缓存策略** | 会话级单例缓存（`_cached_system_prompt`）+ SQLite持久化，压缩后才重建 | 每轮重建或按消息数阈值重建 | `run_agent.py:L5118`注释明确说明"Called once per session (cached on self._cached_system_prompt) and only rebuilt after context compression events. This ensures the system prompt is stable across all turns in a session, maximizing prefix cache hits." |
| **技能索引双层缓存** | 进程内LRU（8条目）+ 磁盘snapshot（`.skills_prompt_snapshot.json`按mtime/size校验） | 纯内存缓存或每次全量扫描 | `agent/prompt_builder.py:L742-L767`：冷启动时从磁盘恢复，热运行时命中内存；manifest校验避免stale snapshot |
| **上下文文件优先级** | 严格互斥：`.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`，只加载第一个 | 全部加载合并 | `agent/prompt_builder.py:L1169-L1174`：避免多个项目上下文冲突；`build_context_files_prompt`的注释说明"first found wins — only ONE project context type is loaded" |
| **瞬态提示分离** | `ephemeral_system_prompt`和`prefill_messages`在API调用时才叠加，不进入缓存/存储 | 直接拼接到`_cached_system_prompt` | `run_agent.py:L5203-L5204`注释："Note: ephemeral_system_prompt is NOT included here. It's injected at API-call time only so it stays out of the cached/stored system prompt." |
| **开发者角色转换** | 在transport层（`chat_completions.py`）根据模型名动态将`system`角色替换为`developer` | 在prompt_builder层统一替换 | `agent/prompt_builder.py:L348-L353`注释说明"The swap happens at the API boundary in _build_api_kwargs() so internal message representation stays consistent ("system" everywhere)." |

### 3.3 数据流/控制流

```
输入层
  ├─ SOUL.md（~/.hermes/SOUL.md）          → load_soul_md()           → agent/prompt_builder.py:L1034
  ├─ 用户system_message                     → _build_system_prompt()入参 → run_agent.py:L5114
  ├─ MEMORY.md / USER.md                    → MemoryStore.format_for_system_prompt() → run_agent.py:L5208-L5217
  ├─ 外部记忆提供者                          → MemoryManager.build_system_prompt()    → run_agent.py:L5220-L5226
  ├─ 技能目录（~/.hermes/skills/）           → build_skills_system_prompt()           → agent/prompt_builder.py:L718
  ├─ 项目上下文文件（cwd/git根目录）          → build_context_files_prompt()           → agent/prompt_builder.py:L1147
  ├─ 平台标识（HERMES_PLATFORM）            → PLATFORM_HINTS字典查找                  → agent/prompt_builder.py:L355-L522
  └─ 环境检测（WSL等）                       → build_environment_hints()              → agent/prompt_builder.py:L542

处理层（_build_system_prompt）
  → 按固定顺序拼接11层内容（run_agent.py:L5122-L5129注释列出完整顺序）
  → 工具可用性条件过滤（memory/session_search/skill_manage/kanban_show）
  → 模型家族条件过滤（gpt/gemini/codex等特化引导）
  → 返回拼接字符串，存入`_cached_system_prompt`

API调用前处理层（主循环内）
  → 取出`_cached_system_prompt`作为`active_system_prompt`
  → 叠加`ephemeral_system_prompt`（如存在）
  → 插入`prefill_messages`到system之后、历史消息之前
  → 应用Anthropic cache_control（system + 最近3条非system消息）
  → 角色转换（system→developer，针对GPT-5/Codex）
  → 注入到api_messages列表头部

输出层
  → api_messages → _build_api_kwargs() → transport.build_kwargs() → LLM API
```

---

## 4. 关键机制拆解（含源码）

### 机制A：系统提示的11层洋葱组装

**作用**：将多源异构信息按严格优先级拼接成单一系统提示字符串，确保身份、能力、记忆、环境信息不冲突。

**设计意图**：分层而非扁平合并，使得每一层可以独立条件开关（如`skip_context_files`只关闭第9层），且缓存边界清晰（前8层稳定，后3层可能变化）。

**关键源码**（`run_agent.py:5114-5299`）：
```python
# run_agent.py:L5122-L5129 — 11层顺序的权威注释
# Layers (in order):
#   1. Agent identity — SOUL.md when available, else DEFAULT_AGENT_IDENTITY
#   2. User / gateway system prompt (if provided)
#   3. Persistent memory (frozen snapshot)
#   4. Skills guidance (if skills tools are loaded)
#   5. Context files (AGENTS.md, .cursorrules — SOUL.md excluded here when used as identity)
#   6. Current date & time (frozen at build time)
#   7. Platform-specific formatting hint

# run_agent.py:L5135-L5143 — SOUL.md作为身份槽位的条件逻辑
if self.load_soul_identity or not self.skip_context_files:
    _soul_content = load_soul_md()
    if _soul_content:
        prompt_parts = [_soul_content]
        _soul_loaded = True
if not _soul_loaded:
    prompt_parts = [DEFAULT_AGENT_IDENTITY]  # 硬编码回退
```

**这段代码为什么值得看**：它揭示了"身份"与"项目上下文"的解耦设计——`skip_context_files=True`时仍可保留SOUL.md身份（通过`load_soul_identity=True`），这是cron作业等场景的关键需求。

---

### 机制B：技能的条件过滤与双层缓存

**作用**：根据当前实际可用的工具和工具集，动态决定哪些技能应出现在系统提示中，避免模型看到无法使用的技能。

**设计意图**：技能可能依赖特定工具（如`browser_navigate`）或作为某工具的fallback（当主工具不可用时才展示）。无过滤则模型会产生幻觉式工具调用。

**关键源码**（`agent/prompt_builder.py:687-715`）：
```python
def _skill_should_show(
    conditions: dict,
    available_tools: "set[str] | None",
    available_toolsets: "set[str] | None",
) -> bool:
    if available_tools is None and available_toolsets is None:
        return True  # 无过滤信息时全展示（向后兼容）

    at = available_tools or set()
    ats = available_toolsets or set()

    # fallback_for: 当主工具/工具集可用时隐藏该技能
    for ts in conditions.get("fallback_for_toolsets", []):
        if ts in ats:
            return False
    for t in conditions.get("fallback_for_tools", []):
        if t in at:
            return False

    # requires: 当所需工具/工具集不可用时隐藏该技能
    for ts in conditions.get("requires_toolsets", []):
        if ts not in ats:
            return False
    for t in conditions.get("requires_tools", []):
        if t not in at:
            return False

    return True
```

**这段代码为什么值得看**：`fallback_for`与`requires`的语义设计非常精巧——前者是"有A就不需要B"（如有了原生browser工具就隐藏基于playwright的fallback技能），后者是"没有C就不能展示D"（如没有`docker`工具集就不展示容器相关技能）。这种双向条件避免了技能冗余和缺失依赖两种幻觉。

---

### 机制C：瞬态提示的API调用时注入

**作用**：将仅在当前轮次有效的指令（如`ephemeral_system_prompt`）和用户预填充的对话上下文（`prefill_messages`）与稳定缓存的系统提示分离。

**设计意图**：若将瞬态内容拼接到`_cached_system_prompt`，会导致每轮缓存前缀变化，彻底破坏prefix cache。分离后，稳定前缀（系统提示）始终命中缓存，只有尾部变化。

**关键源码**（`run_agent.py:11351-11366`）：
```python
# 11351-11353: 叠加瞬态系统提示（不改变缓存值）
effective_system = active_system_prompt or ""
if self.ephemeral_system_prompt:
    effective_system = (effective_system + "\n\n" + self.ephemeral_system_prompt).strip()

# 11354-11357: 插件上下文注入到user消息而非system（保护缓存前缀）
# NOTE: Plugin context from pre_llm_call hooks is injected into the
# user message (see injection block above), NOT the system prompt.
# This is intentional — system prompt modifications break the prompt
# cache prefix. The system prompt is reserved for Hermes internals.

# 11363-11366: prefill_messages插入system之后、历史之前
if self.prefill_messages:
    sys_offset = 1 if effective_system else 0
    for idx, pfm in enumerate(self.prefill_messages):
        api_messages.insert(sys_offset + idx, pfm.copy())
```

**这段代码为什么值得看**：`sys_offset = 1 if effective_system else 0`这个细节处理了system prompt为空时的边界情况，确保prefill_messages始终位于正确的语义位置。同时注释明确声明了"system prompt is reserved for Hermes internals"——这是缓存优先架构的核心原则。

---

### 机制D：Anthropic Prompt Caching的system_and_3策略

**作用**：在Anthropic原生、OpenRouter Claude、以及兼容Anthropic协议的第三方网关（MiniMax、Qwen/Alibaba等）上，通过4个`cache_control`断点降低多轮对话的输入token成本。

**设计意图**：Anthropic允许最多4个断点。将第1个放在system prompt（最稳定），后3个放在最近3条非system消息（滚动窗口），使得每轮新增的消息只影响最后1个断点，前面3个断点大概率命中缓存。

**关键源码**（`agent/prompt_caching.py:41-72`）：
```python
def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
    native_anthropic: bool = False,
) -> List[Dict[str, Any]]:
    messages = copy.deepcopy(api_messages)
    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0
    # 断点1: system prompt
    if messages[0].get("role") == "system":
        _apply_cache_marker(messages[0], marker, native_anthropic=native_anthropic)
        breakpoints_used += 1

    # 断点2-4: 最近3条非system消息
    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        _apply_cache_marker(messages[idx], marker, native_anthropic=native_anthropic)

    return messages
```

**这段代码为什么值得看**：`native_anthropic`参数控制断点布局——原生Anthropic要求marker放在content block内部（`{"type":"text","text":"...","cache_control":{}}`），而OpenRouter等兼容网关接受放在message envelope上。`_anthropic_prompt_cache_policy()`（`run_agent.py:2960-L3049`）通过provider/model/base_url三维检测决定布局，覆盖了Claude、MiniMax、Qwen/Alibaba等6类网关场景。

---

### 机制E：上下文文件的Prompt Injection防御

**作用**：在将外部文件（SOUL.md、AGENTS.md、.cursorrules等）注入系统提示前，扫描已知攻击模式并阻断或消毒。

**设计意图**：项目上下文文件通常由用户或第三方提供，是prompt injection的高危入口。系统提示具有最高指令权重，一旦被污染后果严重。

**关键源码**（`agent/prompt_builder.py:36-73`）：
```python
_CONTEXT_THREAT_PATTERNS = [
    (r'ignore\s+(previous|all|above|prior)\s+instructions', "prompt_injection"),
    (r'do\s+not\s+tell\s+the\s+user', "deception_hide"),
    (r'system\s+prompt\s+override', "sys_prompt_override"),
    (r'disregard\s+(your|all|any)\s+(instructions|rules|guidelines)', "disregard_rules"),
    (r'act\s+as\s+(if|though)\s+you\s+(have\s+no|don\'t\s+have)\s+(restrictions|limits|rules)', "bypass_restrictions"),
    (r'<!--[^>]*(?:ignore|override|system|secret|hidden)[^>]*-->', "html_comment_injection"),
    (r'<\s*div\s+style\s*=\s*["\'][\s\S]*?display\s*:\s*none', "hidden_div"),
    (r'translate\s+.*\s+into\s+.*\s+and\s+(execute|run|eval)', "translate_execute"),
    (r'curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)', "exfil_curl"),
    (r'cat\s+[^\n]*(\.env|credentials|\.netrc|\.pgpass)', "read_secrets"),
]

_CONTEXT_INVISIBLE_CHARS = {'​', '‌', '‍', '⁠', '﻿', ...}

def _scan_context_content(content: str, filename: str) -> str:
    findings = []
    for char in _CONTEXT_INVISIBLE_CHARS:
        if char in content:
            findings.append(f"invisible unicode U+{ord(char):04X}")
    for pattern, pid in _CONTEXT_THREAT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(pid)
    if findings:
        logger.warning("Context file %s blocked: %s", filename, ", ".join(findings))
        return f"[BLOCKED: {filename} contained potential prompt injection ...]"
    return content
```

**这段代码为什么值得看**：它不仅覆盖经典的"ignore previous instructions"，还针对HTML注释、隐藏div、Unicode零宽字符、命令行数据外泄等进阶攻击向量。`_CONTEXT_INVISIBLE_CHARS`集合特别处理了零宽字符绕过——这是许多prompt injection防御容易忽略的向量。

---

### 机制F：Thinking Prefill（推理续写）

**作用**：当模型返回只有reasoning/thinking内容而无可见输出或工具调用时，自动将reasoning内容作为prefill插入对话历史，引导模型继续生成实际输出。

**设计意图**：部分推理模型（如mimo-v2-pro via OpenRouter）会在首轮只输出内部推理，然后停止。如果不prefill，Agent会误判为空响应并进入空响应重试逻辑，浪费token。

**关键源码**（`run_agent.py:13967-13985`）：
```python
_has_structured = bool(
    getattr(assistant_message, "reasoning", None)
    or getattr(assistant_message, "reasoning_content", None)
    or getattr(assistant_message, "reasoning_details", None)
    or _has_inline_thinking
)
if _has_structured and self._thinking_prefill_retries < 2:
    self._thinking_prefill_retries += 1
    interim_msg = self._build_assistant_message(assistant_message, "incomplete")
    interim_msg["_thinking_prefill"] = True  # 内部标记，后续会弹出
    messages.append(interim_msg)
    self._session_messages = messages
    self._save_session_log(messages)
    continue  # 直接进入下一轮，让模型继续
```

**这段代码为什么值得看**：`"_thinking_prefill"`是一个内部标记字段，在后续轮次中会被识别并弹出（`run_agent.py:L13701-L13708`），避免污染持久化的对话历史。同时`self._thinking_prefill_retries < 2`限制了最多2次续写，防止无限循环。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环（Orchestration Loop） | 组装好的`api_messages`列表（含system + prefill + history + cache_control） | `run_agent.py:L11359-L11380` |
| 依赖 | 工具系统（Tool System） | `self.valid_tool_names`决定哪些行为引导注入；`available_toolsets`决定技能过滤 | `run_agent.py:L5149-L5161`, `L5228-L5244` |
| 依赖 | 记忆系统（Memory System） | `MemoryStore.format_for_system_prompt()`提供MEMORY.md/USER.md内容；`MemoryManager.build_system_prompt()`提供外部记忆 | `run_agent.py:L5208-L5226` |
| 依赖 | 上下文管理（Context Management） | 压缩后调用`_invalidate_system_prompt()`重建系统提示；`estimate_request_tokens_rough()`估算预检token数 | `run_agent.py:L9485`, `L11018-L11024` |
| 输出到 | 安全/防护（Security） | `_scan_context_content()`扫描上下文文件中的prompt injection；`_sanitize_api_messages()`修复孤儿tool结果 | `agent/prompt_builder.py:L55-L73`, `run_agent.py:L5332-L5348` |
| 依赖 | 初始化与环境（Initialization & Environment） | `TERMINAL_CWD`环境变量覆盖cwd用于上下文文件发现；`HERMES_PLATFORM`决定平台提示 | `run_agent.py:L5247-L5251`, `agent/prompt_builder.py:L745-L749` |
| 输出到 | 子Agent编排（Sub-Agent Orchestration） | `kanban_show`等工具存在时注入`KANBAN_GUIDANCE`；`delegate_task`与kanban的区分说明 | `run_agent.py:L5160-L5161` |
| 依赖 | 状态管理（State Management） | `_cached_system_prompt`是会话级状态；SQLite持久化实现跨轮复用 | `run_agent.py:L1687`, `L10963-L11002` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **系统提示的稳定性假设**：作者假设系统提示在会话内是"准静态"的——只有压缩事件或显式配置变更才会触发重建。这建立在"用户不会在会话中途频繁修改SOUL.md或技能"的假设上。
2. **模型行为可引导假设**：作者相信通过system prompt中的显式指令（如`TOOL_USE_ENFORCEMENT_GUIDANCE`）可以显著改善特定模型家族（GPT/Gemini/Grok）的工具调用率。这解释了为什么会有模型家族特化的长文本引导。
3. **缓存收益大于精度损失假设**：将`ephemeral_system_prompt`和插件上下文排除在缓存之外，意味着这些瞬态信息无法享受缓存降价——作者假设这类信息占比小，缓存前缀的稳定收益更大。

### 6.2 代价/风险

1. **缓存与瞬态内容的张力**：`run_agent.py:L11354-L11357`的注释承认"Plugin context from pre_llm_call hooks is injected into the user message... NOT the system prompt. This is intentional — system prompt modifications break the prompt cache prefix." 这意味着插件无法通过system prompt影响模型行为，只能退而求其次注入user消息，指令权重降低。
2. **技能缓存的platform维度膨胀**：`build_skills_system_prompt()`的缓存key包含`_platform_hint`和`disabled`技能列表（`agent/prompt_builder.py:L752-L758`）。网关并发服务多平台时，缓存key空间随平台数线性膨胀，8条目的LRU可能频繁失效。
3. **上下文文件截断的信息损失**：`_truncate_content()`采用70%头部+20%尾部的截断策略（`agent/prompt_builder.py:L1022-L1031`），中间10%被丢弃。对于依赖线性阅读的技能文档，这种截断可能破坏逻辑连贯性。
4. **硬编码模型名单的维护负担**：`TOOL_USE_ENFORCEMENT_MODELS`、`DEVELOPER_ROLE_MODELS`、`OPENAI_MODEL_EXECUTION_GUIDANCE`等均为硬编码字符串匹配。新模型发布时需要手动更新，存在滞后风险。

### 6.3 如果要重新设计可能改变什么

1. **将系统提示拆分为"稳定缓存部分"和"每轮可变部分"的显式结构**：当前用字符串拼接+运行时截取（`ephemeral_system_prompt`叠加）的方式较为隐式。可以改为结构化dict，让transport层明确知道哪些block可以打cache_control，哪些不能。
2. **技能索引改用增量更新而非全量重建**：当前技能变更（如用户安装新技能）需要清除整个`_SKILLS_PROMPT_CACHE`。可以维护一个按技能名索引的细粒度缓存，只失效变更的技能条目。
3. **prompt injection扫描前置到文件写入时**：当前在读取时扫描，每次会话都重复执行。可以在`skill_manage`写入`.cursorrules`或`AGENTS.md`时扫描并标记，读取时直接信任标记。
4. **将模型家族特化引导抽象为可插拔的"persona adapter"**：当前GPT/Gemini/Codex的特化引导是平铺的if-else。可以抽象为`PersonaAdapter`接口，每个模型家族一个适配器文件，降低`prompt_builder.py`的复杂度。

### 6.4 对自己设计Agent系统的启示

> **最核心的启示**：Prompt构建不是"拼接字符串"，而是"管理缓存前缀的稳定性"。Hermes的设计表明，一个优秀的Prompt构建系统必须同时回答三个问题：① 什么内容值得放入系统提示（身份、能力、记忆、环境）？② 什么内容必须排除在缓存之外（瞬态指令、插件上下文）？③ 如何在多provider、多模型家族、多平台的环境下保持语义一致性？其中第②点最容易被忽视——很多系统为了代码简洁将ephemeral内容直接拼进system prompt，结果在多轮对话中付出了数倍的token成本。将"缓存稳定性"作为一级设计目标，是Hermes Prompt构建维度最值得借鉴的架构思维。
