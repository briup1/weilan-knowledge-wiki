# 维度06：输出解析（Output Parsing）

## 1. 一句话定位

输出解析负责将 LLM 返回的原始字节流（结构化 JSON、SSE chunk、XML 标签、原生 SDK 对象）转化为 Agent 内部可统一消费的标准化消息（`assistant_msg`），并从中提取 tool_calls、reasoning content、finish_reason 等语义单元，决定下一步是执行工具还是向用户交付最终回复。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有输出解析层，Agent 将直接面对 provider 的原始响应格式差异，导致以下具体故障：

- **Tool call 提取失败**：不同 provider 对 tool call 的封装截然不同。OpenAI 用 `message.tool_calls[].function.name/arguments`；Anthropic 用 `content_blocks` 中的 `tool_use`；Gemini 用 `parts[].functionCall`；Bedrock Converse 用 `output.message.content[].toolUse`。如果没有统一解析，Agent 循环需要为每个 provider 写独立分支，任何新增 provider 都会侵入核心循环（`run_agent.py` 的 14K+ 行代码将爆炸式增长）。

- **Reasoning content 泄漏或丢失**：DeepSeek/Moonshot 将 reasoning 放在 `reasoning_content` 字段；OpenRouter 用 `reasoning_details` 数组；Anthropic 用 `thinking` content block；MiniMax/GLM 把 `<think>` 标签直接塞进 `content`。如果不提取并隔离 reasoning，它会：
  - 泄漏到用户可见的回复中（#8878、#9568）
  - 污染上下文，在后续轮次中重复计入 token（#9306 观察到 16% 的内容膨胀）
  - 导致 provider 400 错误（DeepSeek V4 Pro 要求 tool-call 轮次必须回传 `reasoning_content`，缺失即 400，#15250、#17400）

- **流式 delta 边界破坏状态**：当 `<think>` 标签被拆成两个 delta（`delta1="<think>"`、`delta2="Let me check"`）时，如果在每个 delta 上独立做正则替换，第一个 delta 会被完全擦除，下游状态机永远看不到开标签，导致 reasoning 内容被当作普通文本泄漏给用户（#17924）。

- **JSON 解析崩溃**：本地模型（GLM-5.1 via Ollama）会生成 trailing comma、Python `None`、未闭合括号等非法 JSON 作为 tool-call arguments，直接 `json.loads` 会抛出异常，中断整个会话。

- **角色交替被破坏**：如果 tool-call 轮次因异常中断，消息历史可能以 orphan `tool` 消息结尾，下一条用户消息会变成 `...tool, user`，大多数 provider 静默返回空内容，触发空回复死循环。

### 2.2 具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| API 返回后进入解析路径 | `run_agent.py:13332` | `_transport.normalize_response(response)` 被调用 |
| 检测到 `assistant_message.tool_calls` | `run_agent.py:13509` | `if assistant_message.tool_calls:` 分支进入工具执行 |
| 检测到 reasoning 字段 | `run_agent.py:3343` | `_extract_reasoning()` 检查 `reasoning`/`reasoning_content`/`reasoning_details` |
| 流式 delta 到达 | `run_agent.py:6895` | `_fire_stream_delta()` 每次收到 delta 时通过 `StreamingThinkScrubber` 处理 |
| JSON 解析失败 | `run_agent.py:13584` | `json.loads(args)` 抛出 `JSONDecodeError` 时进入修复/重试逻辑 |
| 消息序列损坏 | `run_agent.py:11294` | `_repair_message_sequence()` 在每次 API 调用前触发 |

---

## 3. 核心设计思路

### 3.1 抽象模型

```python
# 核心抽象：Transport 层将任何 provider 的原始响应归一化为 NormalizedResponse
class ProviderTransport:
    def normalize_response(raw_response) -> NormalizedResponse:
        # 提取：content, tool_calls, reasoning, finish_reason, usage
        # 屏蔽 provider 差异

# Agent 层基于 NormalizedResponse 做决策
class AIAgent:
    def run_conversation_turn():
        normalized = transport.normalize_response(raw_response)
        assistant_message = normalized  # NormalizedResponse 兼容 tc.function.name 访问

        if assistant_message.tool_calls:
            # 工具执行分支
            execute_tools(assistant_message.tool_calls)
        else:
            # 最终回复分支
            deliver_to_user(assistant_message.content)
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **Transport 归一化层** | 每个 `api_mode` 有独立的 Transport 类，统一输出 `NormalizedResponse` | 在 `run_agent.py` 中直接写 provider 分支 | `agent/transports/` 目录下 4 个 transport + `types.py` 定义标准结构；`run_agent.py` 中通过 `_get_transport()` 动态获取，核心循环无 provider 感知代码 |
| **Reasoning 双轨存储** | 内部用 `reasoning` 字段存储纯文本；API 回传时用 `reasoning_content`/`reasoning_details` | 统一成一个字段 | `run_agent.py:9201-9269` `_copy_reasoning_content_for_api()` 的五层回退逻辑证明不同 provider 对 reasoning 的 schema 要求完全不同（DeepSeek 要空格占位、Kimi 要 `reasoning_content`、Anthropic 要 `reasoning_details`） |
| **流式状态机 scrubber** | `StreamingThinkScrubber` 维护跨 delta 的状态（`_in_block`、`_buf`） | 每个 delta 独立正则替换 | `agent/think_scrubber.py:64-386` 的完整状态机；`run_agent.py:1313-1319` 注释明确说明 per-delta regex 会破坏下游状态（#17924） |
| **Tool-call 参数修复** | `_repair_tool_call_arguments()` 尝试多种修复策略，最终回退到 `"{}"` | 直接拒绝执行并报错 | `run_agent.py:613-706` 的 5 层修复（control chars、trailing comma、unclosed braces、excess braces、escape invalid chars）；失败返回 `"{}"` 避免会话崩溃 |
| **消息序列防御性修复** | `_sanitize_api_messages()` + `_repair_message_sequence()` + `_drop_trailing_empty_response_scaffolding()` 三重防护 | 信任消息历史总是合法的 | `run_agent.py:5332-5400`、`3901-3999`、`3848-3899` 三个独立函数；注释反复强调 "orphan tool result → silent empty response → infinite loop" 的因果链 |

### 3.3 数据流/控制流

```
[Provider Raw Response]
       │
       ▼
[Transport.normalize_response()]  ←── 入口：agent/transports/{chat_completions,anthropic,bedrock,codex}.py
       │
       ├──→ content: str|None
       ├──→ tool_calls: List[ToolCall]|None
       ├──→ reasoning: str|None
       ├──→ reasoning_content: str|None  (provider_data 中)
       ├──→ reasoning_details: List[dict]|None
       ├──→ finish_reason: str
       └──→ usage: Usage
       │
       ▼
[AIAgent._build_assistant_message()]  ←── run_agent.py:8967
       │
       ├──→ 提取 reasoning（多字段回退）
       ├──→ 清理 content（_strip_think_blocks 移除 <think> 等）
       ├──→ 序列化 tool_calls（处理 call_id/response_item_id/extra_content）
       ├──→ 处理 reasoning_content 占位（DeepSeek/Kimi 需要空格）
       └──→ 生成标准 dict: {"role":"assistant", "content":..., "reasoning":..., "tool_calls":...}
       │
       ▼
[决策分支]  ←── run_agent.py:13509
       │
       ├──→ tool_calls 存在 ──→ _execute_tool_calls() ──→ 继续循环
       │
       └──→ tool_calls 不存在 ──→ 最终回复 ──→ break
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：Transport 层响应归一化

**作用**：将不同 provider 的原始响应统一转换为 `NormalizedResponse`，让上层代码无感知地消费。

**设计意图**：如果不做归一化，`run_agent.py` 中每个使用 `response.choices[0].message` 的地方都需要根据 `api_mode` 分支，核心循环将与 provider 实现深度耦合。

**关键源码**（`agent/transports/types.py:18-77`）：
```python
@dataclass
class ToolCall:
    id: str | None
    name: str
    arguments: str  # JSON string
    provider_data: dict[str, Any] | None = field(default=None, repr=False)

    # 向后兼容：让 NormalizedResponse 可以直接替代旧的 SimpleNamespace
    @property
    def function(self) -> ToolCall:
        """Return self so tc.function.name / tc.function.arguments work."""
        return self

@dataclass
class NormalizedResponse:
    content: str | None
    tool_calls: list[ToolCall] | None
    finish_reason: str
    reasoning: str | None = None
    usage: Usage | None = None
    provider_data: dict[str, Any] | None = field(default=None, repr=False)
```

**为什么值得看**：`ToolCall.function` 返回 `self` 是一个巧妙的兼容性设计——旧的 `run_agent.py` 代码中有 45+ 处直接访问 `tc.function.name`，通过属性代理可以在不修改任何调用点的情况下完成迁移。

---

### 机制 B：Reasoning Content 的多层提取与隔离

**作用**：从各种 provider 的差异化格式中提取 reasoning，存储到内部 `reasoning` 字段，同时在 API 回传时根据目标 provider 的要求重新映射。

**设计意图**：Reasoning 既是用户可见的调试信息（需要展示），又是 provider 要求必须回传的状态（影响多轮连续性）。必须隔离存储，否则会导致内容泄漏或 API 400 错误。

**关键源码**（`run_agent.py:3343-3408`）：
```python
def _extract_reasoning(self, assistant_message) -> Optional[str]:
    reasoning_parts = []
    # 1. 直接 reasoning 字段（DeepSeek, Qwen）
    if hasattr(assistant_message, 'reasoning') and assistant_message.reasoning:
        reasoning_parts.append(assistant_message.reasoning)
    # 2. reasoning_content 字段（Moonshot AI, Novita）
    if hasattr(assistant_message, 'reasoning_content') and assistant_message.reasoning_content:
        if assistant_message.reasoning_content not in reasoning_parts:
            reasoning_parts.append(assistant_message.reasoning_content)
    # 3. reasoning_details 数组（OpenRouter unified）
    if hasattr(assistant_message, 'reasoning_details') and assistant_message.reasoning_details:
        for detail in assistant_message.reasoning_details:
            if isinstance(detail, dict):
                summary = detail.get('summary') or detail.get('thinking') or detail.get('content')
                if summary and summary not in reasoning_parts:
                    reasoning_parts.append(summary)
    # 4. 内联 <think> 标签回退（无结构化字段时）
    if not reasoning_parts:
        content = getattr(assistant_message, "content", None)
        if isinstance(content, str) and content:
            for pattern in (r"<think>(.*?)</think>", r"<thinking>(.*?)</thinking>", ...):
                for block in re.findall(pattern, content, flags=re.DOTALL | re.IGNORECASE):
                    if block.strip():
                        reasoning_parts.append(block.strip())
    return "\n\n".join(reasoning_parts) if reasoning_parts else None
```

**为什么值得看**：四层回退策略（结构化字段 → 替代字段 → 数组详情 → 正则提取）展示了如何应对 provider 生态的碎片化。特别是第 4 层的内联正则回退，处理了 MiniMax/GLM 等不暴露结构化 reasoning 字段的模型。

---

### 机制 C：流式 Reasoning 的状态机清理

**作用**：在 SSE 流式传输中，跨 delta 边界正确地识别并剔除 `<think>`、`<thinking>`、`<reasoning>` 等标签块，防止 reasoning 内容泄漏到用户可见的输出。

**设计意图**：Per-delta 正则无法处理标签被拆分到多个 delta 的情况。例如 `delta1="<think>"`、`delta2="Let me check"`——如果独立处理，delta1 的正则会匹配 `^<think>...` 并将其完全删除，下游状态机永远不知道有一个 think block 被打开了。

**关键源码**（`agent/think_scrubber.py:64-201`）：
```python
class StreamingThinkScrubber:
    def __init__(self):
        self._in_block: bool = False
        self._buf: str = ""
        self._last_emitted_ended_newline: bool = True

    def feed(self, text: str) -> str:
        if not text:
            return ""
        buf = self._buf + text
        self._buf = ""
        out: list[str] = []

        while buf:
            if self._in_block:
                # 在 block 内：寻找 close tag
                close_idx, close_len = self._find_first_tag(buf, self._CLOSE_TAGS)
                if close_idx == -1:
                    # 没有 close：保留可能的 partial close-tag 前缀，其余丢弃
                    held = self._max_partial_suffix(buf, self._CLOSE_TAGS)
                    self._buf = buf[-held:] if held else ""
                    return "".join(out)
                buf = buf[close_idx + close_len:]
                self._in_block = False
            else:
                # 不在 block 内：寻找 closed pair 或 boundary 处的 open tag
                pair = self._find_earliest_closed_pair(buf)
                open_idx, open_len = self._find_open_at_boundary(buf, out)
                # 选择最早出现的匹配
                if pair is not None and (open_idx == -1 or pair[0] <= open_idx):
                    buf = buf[pair[1]:]  # 跳过整个 closed pair
                    continue
                if open_idx != -1:
                    # Boundary 处的 open tag：进入 block
                    preceding = buf[:open_idx]
                    if preceding:
                        out.append(preceding)
                    self._in_block = True
                    buf = buf[open_idx + open_len:]
                    continue
                # 没有可解析的标签结构：保留可能的 partial tag 前缀
                held = self._max_partial_suffix(buf, self._OPEN_TAGS)
                held_close = self._max_partial_suffix(buf, self._CLOSE_TAGS)
                held = max(held, held_close)
                if held:
                    emit_text = buf[:-held]
                    self._buf = buf[-held:]
                else:
                    emit_text = buf
                    self._buf = ""
                if emit_text:
                    out.append(emit_text)
                return "".join(out)
```

**为什么值得看**：`_find_open_at_boundary()`（`agent/think_scrubber.py:273-331`）实现了关键的安全策略——只有当 open tag 出现在流的开头、换行后或当前行仅有空白字符时，才将其视为 reasoning block 的开始。这防止了模型在正文中提及 `<think>` 标签（如 "use `<think>` tags here"）时被误删。

---

### 机制 D：Tool-Call 参数修复

**作用**：当模型生成非法 JSON 作为 tool-call arguments 时，尝试多种修复策略，避免会话崩溃。

**设计意图**：本地模型（尤其是通过 Ollama 服务的 GLM-5.1、Qwen 等）经常生成 trailing comma、未闭合括号、Python `None` 等。直接拒绝执行会导致用户体验极差；返回 `"{}"` 让模型在下一轮有机会自我纠正。

**关键源码**（`run_agent.py:613-706`）：
```python
def _repair_tool_call_arguments(raw_args: str, tool_name: str = "?") -> str:
    raw_stripped = raw_args.strip() if isinstance(raw_args, str) else ""
    if not raw_stripped:
        return "{}"
    if raw_stripped == "None":
        return "{}"
    # Pass 0: llama.cpp 有时在 JSON 字符串值中发出字面控制字符
    try:
        parsed = json.loads(raw_stripped, strict=False)
        return json.dumps(parsed, separators=(",", ":"))
    except (ValueError, TypeError):
        pass
    # Pass 1-3: 修复 trailing comma、未闭合结构、多余闭合符号
    fixed = re.sub(r',\s*([}\]])', r'\1', raw_stripped)
    open_curly = fixed.count('{') - fixed.count('}')
    open_bracket = fixed.count('[') - fixed.count(']')
    if open_curly > 0:
        fixed += '}' * open_curly
    if open_bracket > 0:
        fixed += ']' * open_bracket
    for _ in range(50):
        try:
            json.loads(fixed)
            break
        except json.JSONDecodeError:
            if fixed.endswith('}') and fixed.count('}') > fixed.count('{'):
                fixed = fixed[:-1]
            elif fixed.endswith(']') and fixed.count(']') > fixed.count('['):
                fixed = fixed[:-1]
            else:
                break
    try:
        json.loads(fixed)
        return fixed
    except json.JSONDecodeError:
        pass
    # Pass 4: 转义 JSON 字符串内的无效控制字符
    try:
        escaped = _escape_invalid_chars_in_json_strings(fixed)
        if escaped != fixed:
            json.loads(escaped)
            return escaped
    except (ValueError, TypeError):
        pass
    return "{}"
```

**为什么值得看**：五层渐进式修复 + 最终 `"{}"` 回退，展示了如何优雅地处理"模型输出格式不可靠"这一根本假设。`strict=False` 的 `json.loads` 是一个容易被忽视的技巧——它允许字符串值中包含控制字符（tab、newline），这是 llama.cpp 后端的常见输出。

---

### 机制 E：消息序列防御性修复

**作用**：在每次 API 调用前，检测并修复消息历史中的角色交替违规、orphan tool result、consecutive user messages 等问题。

**设计意图**：这些损坏可能来自：异常中断的 tool-call 轮次、session 恢复时的数据不一致、外部调用者（gateway、cron）传入的畸形历史。Provider 对角色交替非常严格， violations 通常导致静默空回复，进而触发空回复死循环。

**关键源码**（`run_agent.py:5332-5400`）：
```python
def _sanitize_api_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # 1. 收集所有 assistant message 中声明的 tool_call_id
    surviving_call_ids: set = set()
    for msg in messages:
        if msg.get("role") == "assistant":
            for tc in msg.get("tool_calls") or []:
                cid = AIAgent._get_tool_call_id_static(tc)
                if cid:
                    surviving_call_ids.add(cid)
    # 2. 收集所有 tool message 实际回应的 tool_call_id
    result_call_ids: set = set()
    for msg in messages:
        if msg.get("role") == "tool":
            cid = msg.get("tool_call_id")
            if cid:
                result_call_ids.add(cid)
    # 3. 删除没有对应 assistant tool_call 的 orphan tool result
    orphaned_results = result_call_ids - surviving_call_ids
    if orphaned_results:
        messages = [
            m for m in messages
            if not (m.get("role") == "tool" and m.get("tool_call_id") in orphaned_results)
        ]
    # 4. 为缺少 tool result 的 tool_call 注入 stub result
    missing_results = surviving_call_ids - result_call_ids
    if missing_results:
        patched: List[Dict[str, Any]] = []
        for msg in messages:
            patched.append(msg)
            if msg.get("role") == "assistant":
                for tc in msg.get("tool_calls") or []:
                    cid = AIAgent._get_tool_call_id_static(tc)
                    if cid in missing_results:
                        patched.append({
                            "role": "tool",
                            "name": AIAgent._get_tool_call_name_static(tc),
                            "content": "[Result unavailable — see context summary above]",
                            "tool_call_id": cid,
                        })
        messages = patched
    return messages
```

**为什么值得看**：双向集合差运算（`orphaned_results = result_call_ids - surviving_call_ids` 和 `missing_results = surviving_call_ids - result_call_ids`）简洁地表达了两种损坏模式。注入 stub result 而非删除 assistant message 的选择保护了历史完整性——删除 assistant message 会丢失模型当时的意图表达。

---

### 机制 F：Thinking-Only Assistant Turn 的检测与丢弃

**作用**：检测并丢弃那些只包含 reasoning（thinking block）而没有可见文本或 tool_calls 的 assistant turn，防止 Anthropic 等 provider 返回 400 错误。

**设计意图**：Anthropic 的 API 规定 "The final block in an assistant message cannot be `thinking`." 当模型只输出了 reasoning 时，如果直接回传，会导致 API 拒绝。丢弃这些 turn 并合并相邻的 user messages 可以保持角色交替合法。

**关键源码**（`run_agent.py:5402-5454`）：
```python
def _is_thinking_only_assistant(msg: Dict[str, Any]) -> bool:
    if not isinstance(msg, dict) or msg.get("role") != "assistant":
        return False
    if msg.get("tool_calls"):
        return False
    # content 是否为空或仅包含 thinking blocks
    content = msg.get("content")
    if isinstance(content, str):
        if content.strip():
            return False
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                if block:
                    return False
                continue
            btype = block.get("type")
            if btype in ("thinking", "redacted_thinking"):
                continue
            if btype == "text":
                text = block.get("text", "")
                if isinstance(text, str) and text.strip():
                    return False
            return False
    # content 为空，检查是否有 reasoning
    reasoning = msg.get("reasoning_content") or msg.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return True
    rd = msg.get("reasoning_details")
    if isinstance(rd, list) and rd:
        return True
    return False
```

**为什么值得看**：这个函数与 Claude Code 的 `filterOrphanedThinkingOnlyMessages` 对称（注释明确提及），说明这是行业共识问题。对 `content` 的三种形态（str、list of blocks、None）分别处理，展示了多模态 content 的复杂性。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 工具系统 | 解析出的 `tool_calls`（名称、参数）被传递给 `handle_function_call()` | `model_tools.py:679` `handle_function_call()` |
| 输出到 | 编排循环 | `finish_reason`（stop/tool_calls/length）决定循环是 break 还是 continue | `run_agent.py:13509` `if assistant_message.tool_calls:` |
| 输出到 | 上下文管理 | `assistant_msg`（含 reasoning/tool_calls）被追加到 `messages` 历史 | `run_agent.py:13725` `messages.append(assistant_msg)` |
| 依赖 | Prompt 构建 | 系统提示中的 tool 定义决定了 `valid_tool_names`，用于验证 tool-call 名称 | `run_agent.py:13519` `if tc.function.name not in self.valid_tool_names:` |
| 依赖 | 错误处理 | 解析失败（JSON 非法、tool 名不存在）触发重试/回退逻辑 | `run_agent.py:13589-13657` invalid JSON 处理 |
| 输出到 | 状态管理 | `NormalizedResponse` 中的 `usage` 更新 session token 计数 | `run_agent.py:12071-12106` usage tracking |
| 依赖 | 初始化与环境 | `api_mode`（chat_completions/anthropic_messages/bedrock_converse/codex_responses）决定使用哪个 Transport | `run_agent.py:1057` `if api_mode in {...}` |
| 输出到 | 记忆系统 | reasoning content 通过 `reasoning_callback` 传递给显示层 | `run_agent.py:8990` `self.reasoning_callback(reasoning_text)` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **Provider 生态将长期碎片化**：代码中为 16+ 个 provider（OpenAI、Anthropic、DeepSeek、Kimi、Moonshot、Gemini、OpenRouter、Nous、NVIDIA、Ollama、LM Studio、xAI、TokenHub、MiniMax、GLM、Qwen）分别处理 quirks，说明作者假设统一标准短期内不会出现。

2. **模型输出不可靠是常态**：`_repair_tool_call_arguments`、`_repair_tool_call`、`_sanitize_tool_call_arguments` 的存在说明作者假设模型可能生成非法 JSON、错误的 tool 名、truncated arguments。

3. **流式输出是默认路径**：`run_agent.py:11570-11618` 中明确 "Always prefer the streaming path — even without stream consumers"，说明作者假设流式是更健壮的路径（有 stale-stream 检测、read timeout）。

4. **Reasoning 是 first-class citizen**：单独提取、存储、回传 reasoning 的设计说明作者假设 reasoning 不仅是调试信息，而是影响多轮对话质量的关键状态。

### 6.2 代价/风险

1. **Transport 层的维护负担**：每新增一个 provider，需要实现 `convert_messages`、`convert_tools`、`build_kwargs`、`normalize_response` 四个方法。`agent/transports/` 已有 4 个 transport + `bedrock_adapter.py`（50K 行）+ `anthropic_adapter.py`（84K 行）+ `gemini_native_adapter.py`（35K 行），新增 provider 的边际成本很高。

2. **Reasoning 双轨存储的复杂性**：`reasoning`（内部）、`reasoning_content`（API 回传）、`reasoning_details`（OpenRouter）、`codex_reasoning_items`（Codex）四个字段的交叉映射在 `_copy_reasoning_content_for_api()` 中形成五层回退逻辑（`run_agent.py:9201-9269`），任何新增 provider 都可能破坏这个 delicate balance。

3. **流式状态机的内存开销**：`StreamingThinkScrubber` 和 `StreamingContextScrubber` 每个 agent 实例各持有一个，在 gateway 高并发场景下会累积。虽然单个 scrubber 状态很小（几个字符串），但并发 1000+ 会话时不可忽视。

4. **防御性修复掩盖根因**：`_sanitize_api_messages`、`_repair_message_sequence`、`_drop_trailing_empty_response_scaffolding` 三重防护虽然防止了崩溃，但也可能掩盖真正的 bug——如果消息历史总是损坏，说明上游有缺陷，但修复层让这个问题变得不可见。

### 6.3 如果要重新设计可能改变什么

1. **Transport 层采用插件架构**：当前 transport 是代码级注册（`register_transport`），可以考虑基于配置文件的动态加载，降低新增 provider 的门槛。

2. **Reasoning 统一为 content block 模型**：参考 Anthropic 的 `thinking`/`redacted_thinking` content block，将所有 reasoning 统一表示为 content 列表中的一个元素，而不是独立的顶层字段。这样可以消除 `reasoning`/`reasoning_content`/`reasoning_details` 的映射复杂性。

3. **Tool-call 参数使用 JSON Schema 验证而非修复**：当前是"先执行再修复"，可以改为"先验证再执行"——用 tool 的 JSON Schema 做结构化验证，在参数非法时直接返回 schema 错误给模型，让模型自我纠正，而不是静默替换为 `"{}"`。

4. **消息序列修复改为断言失败**：当前是"修复后继续"，可以考虑在 debug 模式下改为"检测到损坏即抛出异常"，帮助开发者发现上游 bug。

### 6.4 对自己设计 Agent 系统的启示

1. **尽早引入归一化层**：不要让 provider 差异泄漏到核心循环。`NormalizedResponse` + `Transport` 的抽象是应对碎片化生态的关键。

2. **把"模型不可靠"作为第一性原理设计**：不要假设模型总是返回合法 JSON、正确的 tool 名、完整的响应。为每种不可靠性设计降级路径（修复 → 重试 → 回退 → 报错）。

3. **流式处理需要状态机**：如果支持 SSE 流式输出，任何跨 delta 的语义单元（think block、XML tag、JSON object）都必须用状态机维护，不能用 per-delta 正则。

4. **Reasoning 不是附属品**：如果系统支持 reasoning 模型，reasoning 的提取、存储、回传应该与 content 同等对待，否则会在多轮对话中遇到微妙的 400 错误。
