# 维度：输出解析（Output Parsing）

## 1. 一句话定位

输出解析是 Agent 循环中将原始 LLM 响应转化为"可消费、可持久化、可展示"结构化内容的边界层，负责在"模型原生输出"与"系统内部语义"之间完成清洗、分流、截断和防腐处理。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有输出解析层，nanobot 会在三个层面出现系统性故障：

**（1）思考块污染用户可见输出**

DeepSeek-R1、Kimi 等模型会在 `content` 中嵌入 `<think>...</think>` 块。若直接透传，用户会在聊天界面看到模型的内部推理过程。commit `715b2db2` 引入 `_strip_think` 之前，模型输出的思考内容会直接出现在 Feishu/Discord/Telegram 等渠道的消息中。

**（2）错误响应导致永久性会话中毒（#1303）**

当 LLM 返回 `content: null` 或 `finish_reason="error"` 时，若直接存入 `session.messages`，下一次请求会将这个 `null`/`error` 作为 assistant 消息发送给 LLM，引发 provider 400 错误（`invalid message content type: <nil>`）。由于错误响应被持久化，后续每一轮都会重复触发 400，形成"中毒循环"直到会话被手动 `/new` 清除。

commit `66063abb` 的修复说明明确记录了这一点：
> "When an LLM returns content: null on a plain assistant message (no tool_calls), the null gets saved to session history and causes permanent 400 errors on every subsequent request."

**（3）工具结果膨胀撑爆上下文窗口**

`cat` 一个大文件或 `web_fetch` 一个长网页可能返回数万字符。若完整存入历史，几轮后就会触发上下文溢出。没有 `_save_turn` 中的截断逻辑，系统会在 `max_iterations` 内迅速耗尽 token 预算。

**（4）运行时元数据污染长期记忆**

`ContextBuilder._build_runtime_context()` 每轮注入 `"[Runtime Context — metadata only, not instructions]\nCurrent Time: ...\nChannel: ..."` 前缀。若直接持久化，历史记录中会充满重复的时间戳和渠道信息，既浪费 token 又可能让模型产生"当前时间是过去的某个时间"的幻觉。

### 2.2 OpenCode 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 模型输出包含 `<think>` 块 | `nanobot/agent/loop.py:L166` | 任何非空响应都会经过 `_strip_think` |
| `finish_reason == "error"` | `nanobot/agent/loop.py:L236` | `_safe_chat` 将异常包装为 `LLMResponse(..., finish_reason="error")` |
| 工具结果长度 > 16,000 字符 | `nanobot/agent/loop.py:L466` | `_TOOL_RESULT_MAX_CHARS = 16_000` |
| 用户消息以 `_RUNTIME_CONTEXT_TAG` 开头 | `nanobot/agent/loop.py:L469` | 每轮 `build_messages` 自动注入 |
| 空 assistant 消息（无 content 无 tool_calls） | `nanobot/agent/loop.py:L464` | 某些 provider 会返回空的 assistant turn |

---

## 3. 核心设计思路

### 3.1 抽象模型

输出解析可以抽象为一个**三层过滤管道**：

```
LLM 原始输出
    │
    ▼
┌─────────────────┐  ← 第一层：语义清洗（think 剥离、error 识别）
│  _strip_think() │
│  finish_reason  │
└─────────────────┘
    │
    ▼
┌─────────────────┐  ← 第二层：历史防腐（什么能进 session，什么不能）
│  _save_turn()   │
│  - 截断工具结果 │
│  - 剥离运行时上下文 │
│  - 过滤空消息   │
└─────────────────┘
    │
    ▼
┌─────────────────┐  ← 第三层：展示格式化（用户可见的进度提示）
│  _tool_hint()   │
└─────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| Think 块剥离放在 loop 层而非 provider 层 | `AgentLoop._strip_think()` 在循环入口统一处理 | 让每个 provider 子类各自处理 | provider 层只负责 API 协议转换，不应感知模型特定的模板泄漏。`strip_think` 后来进一步下沉到 `helpers.py` 成为全局工具（`9d5e511a`），被 memory.py、streaming 等多个消费者复用 |
| Error 响应不进入历史 | `if response.finish_reason == "error": break` 直接跳过 `add_assistant_message` | 将 error 作为特殊 assistant 消息存入，让后续模型看到错误上下文 | commit `66063abb` 明确说明：error 响应会"poison the context and cause permanent 400 loops"。provider 的 `_sanitize_empty_content` 虽然能处理 `None`，但无法处理语义上的错误内容 |
| 工具结果截断阈值固定为 16K | `_TOOL_RESULT_MAX_CHARS = 16_000`（类常量） | 按模型上下文窗口动态计算 | 简单、可预测。动态计算会增加与 provider/model 的耦合，而 nanobot 支持多 provider 切换 |
| 运行时上下文在保存时剥离而非构建时不注入 | `_save_turn` 中 `continue` 跳过带 tag 的用户消息 | 修改 `build_messages` 不将 runtime context 合并到 user message | 某些 provider（如 Anthropic）拒绝连续同角色消息。将 runtime context 与 user content 合并为单条 user 消息是协议兼容性要求，只能在持久化层剥离 |
| Tool hint 只取第一个参数的前 40 字符 | `_fmt()` 中 `val[:40]` | 显示完整参数或所有参数 | 进度提示需要"一行内可读"。40 字符是经验值，后来通过 `toolHintMaxLength` 配置化（`daa4a25c`），默认仍为 40，范围 20-500 |

### 3.3 数据流/控制流

```
_run_agent_loop()
    │
    ├──→ provider.chat_with_retry() ──→ LLMResponse
    │                                      │
    │                              ┌───────┴───────┐
    │                              ▼               ▼
    │                    has_tool_calls==True   has_tool_calls==False
    │                              │               │
    │                              ▼               ▼
    │                    _strip_think(content)   _strip_think(content)
    │                    _tool_hint(tool_calls)  │
    │                    on_progress(thought)    finish_reason=="error"?
    │                    on_progress(hint)       │
    │                              │               ├──→ YES: break (不存历史)
    │                              ▼               └──→ NO: add_assistant_message()
    │                    add_assistant_message()       final_content = clean
    │                    add_tool_result()               break
    │                              │
    │                              ▼
    │                    下一轮迭代
    │
    └──→ 返回 (final_content, tools_used, messages)
              │
              ▼
    _save_turn(session, messages, skip)
        │
        ├──→ 跳过空 assistant 消息
        ├──→ 截断过长 tool 结果
        ├──→ 剥离 runtime context tag
        ├──→ 将 base64 image 替换为 "[image]"
        └──→ 追加到 session.messages
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：思考块剥离（Think Block Stripping）

**作用**：移除模型在 `content` 中嵌入的 `<think>`、`<thought>` 等内部推理标记，防止其进入用户可见输出和历史记录。

**设计意图**：
- 为什么不在 provider 层处理？provider 的职责是"把 API 响应翻译成统一格式"，不应感知模型特定的模板泄漏。`<think>` 是模型行为，不是 API 协议的一部分。
- 为什么用静态方法？`_strip_think` 不依赖实例状态，且被 `_tool_hint`、streaming filter、memory store 等多个调用点使用，静态方法明确了其无副作用的纯函数性质。

**关键源码**（`nanobot/agent/loop.py:L165-L170`）：

```python
@staticmethod
def _strip_think(text: str | None) -> str | None:
    """Remove <think>…</think> blocks that some models embed in content."""
    if not text:
        return None
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip() or None
```

**演进**：这个简单的正则经历了多次加固：
- `2787523f`：增加对孤立 `</think>` 和未闭合 `<think>` 的处理
- `9d5e511a`：将 `strip_think` 下沉到 `helpers.py`，成为 streaming、memory、loop 的统一数据源
- `6b7e78a8`：增加 `<thought>` 块支持（Gemma 4）
- `8e7d8bef`：处理畸形标签如 `<think广场…`（无闭合 `>`），并增加 channel marker 过滤
- `e392c27f`：将未闭合标签正则锚定到字符串开头 `^\s*<think>`，避免误删正文中的 `<think` 提及
- `2c397ad4`：处理流式分片导致的截断标签（如 `<thi`、`<thin`）

### 机制 B：错误响应过滤（Session Poisoning Prevention, #1303）

**作用**：当 LLM 返回错误响应时，阻止其进入会话历史，避免永久性 400 循环。

**设计意图**：
- 为什么 error 不能进历史？因为 `_sanitize_empty_content` 只能处理格式问题（`None` → `"(empty)"`），无法修复语义错误。如果模型返回 `"Error calling LLM: 429 rate limit"` 作为 assistant content，下一轮它会作为正常上下文发送给模型，模型可能再次出错，形成正反馈。
- 为什么是 `break` 而不是 `continue`？error 发生在非 tool-call 分支（`else`），意味着这是最终回复位置。没有有效内容可继续迭代，直接中断是最安全的。

**关键源码**（`nanobot/agent/loop.py:L232-L245`）：

```python
else:
    clean = self._strip_think(response.content)
    # Don't persist error responses to session history — they can
    # poison the context and cause permanent 400 loops (#1303).
    if response.finish_reason == "error":
        logger.error("LLM returned error: {}", (clean or "")[:200])
        final_content = clean or "Sorry, I encountered an error calling the AI model."
        break
    messages = self.context.add_assistant_message(
        messages, clean, reasoning_content=response.reasoning_content,
        thinking_blocks=response.thinking_blocks,
    )
    final_content = clean
    break
```

**配套防御**：provider 层的 `_sanitize_empty_content`（`nanobot/providers/base.py:L108-L152`）在发送前将 `None` content 替换为 `"(empty)"`，防止 API 层面的 400。但 loop 层的 error 过滤是语义层面的——即使 content 非空，只要 `finish_reason == "error"`，就不应进入历史。

### 机制 C：回合持久化防腐（_save_turn）

**作用**：在将本轮消息追加到 `session.messages` 之前，执行最后一道清洗——截断、剥离、过滤。

**设计意图**：
- 为什么不在 `build_messages` 或 `add_assistant_message` 中处理？因为那些函数不知道消息是否"属于当前回合"（`skip` 参数控制）。`_save_turn` 是回合边界上的单一出口，集中处理所有持久化相关的清洗逻辑。
- 为什么 assistant 空消息会 poison session？某些 provider 在 tool-call turn 后会输出一个空的 assistant message（content=None, 无 tool_calls）。如果存入历史，下一轮构建上下文时会出现"assistant 消息后无 user/tool 消息"的畸形序列，触发 provider 400。

**关键源码**（`nanobot/agent/loop.py:L458-L491`）：

```python
def _save_turn(self, session: Session, messages: list[dict], skip: int) -> None:
    """Save new-turn messages into session, truncating large tool results."""
    from datetime import datetime
    for m in messages[skip:]:
        entry = dict(m)
        role, content = entry.get("role"), entry.get("content")
        # ① 过滤空 assistant 消息 —— 它们会 poison session context
        if role == "assistant" and not content and not entry.get("tool_calls"):
            continue
        # ② 截断过长工具结果 —— 防止上下文膨胀
        if role == "tool" and isinstance(content, str) and len(content) > self._TOOL_RESULT_MAX_CHARS:
            entry["content"] = content[:self._TOOL_RESULT_MAX_CHARS] + "\n... (truncated)"
        # ③ 剥离运行时上下文 —— 避免重复元数据污染长期记忆
        elif role == "user":
            if isinstance(content, str) and content.startswith(ContextBuilder._RUNTIME_CONTEXT_TAG):
                parts = content.split("\n\n", 1)
                if len(parts) > 1 and parts[1].strip():
                    entry["content"] = parts[1]
                else:
                    continue
            # ④ 将 base64 图片替换为占位符 —— 节省存储空间
            if isinstance(content, list):
                filtered = []
                for c in content:
                    if c.get("type") == "text" and isinstance(c.get("text"), str) \
                            and c["text"].startswith(ContextBuilder._RUNTIME_CONTEXT_TAG):
                        continue
                    if (c.get("type") == "image_url"
                            and c.get("image_url", {}).get("url", "").startswith("data:image/")):
                        filtered.append({"type": "text", "text": "[image]"})
                    else:
                        filtered.append(c)
                if not filtered:
                    continue
                entry["content"] = filtered
        entry.setdefault("timestamp", datetime.now().isoformat())
        session.messages.append(entry)
    session.updated_at = datetime.now()
```

### 机制 D：工具调用提示格式化（Tool Hint）

**作用**：将 tool_calls 列表转换为人类可读的进度提示，如 `web_search("query")`。

**设计意图**：
- 为什么只取第一个参数？因为大多数工具调用只有一个核心参数（`query`、`path`、`command`），显示全部参数会导致提示过长，失去"进度一闪而过"的轻量感。
- 为什么截断 40 字符？这是经验值，足以显示文件路径的最后一段或搜索查询的关键词，又不至于撑爆一行。后续通过 `toolHintMaxLength` 配置化（`daa4a25c`）。
- 为什么后来重写了整个 `_tool_hint`（`8ca99600`）？原始实现过于简单，无法处理 MCP 工具名（`mcp_server__tool`）、路径缩写、连续同类调用折叠等场景。

**关键源码**（`nanobot/agent/loop.py:L172-L181`，原始实现）：

```python
@staticmethod
def _tool_hint(tool_calls: list) -> str:
    """Format tool calls as concise hint, e.g. 'web_search("query")'."""
    def _fmt(tc):
        args = (tc.arguments[0] if isinstance(tc.arguments, list) else tc.arguments) or {}
        val = next(iter(args.values()), None) if isinstance(args, dict) else None
        if not isinstance(val, str):
            return tc.name
        return f'{tc.name}("{val[:40]}…")' if len(val) > 40 else f'{tc.name}("{val}")'
    return ", ".join(_fmt(tc) for tc in tool_calls)
```

**演进**：`8ca99600` 将其扩展为支持：
- 注册表驱动的格式化（`read_file` → `read {path}`）
- 路径缩写（`abbreviate_path`）
- MCP 工具名解析（`mcp_server__tool` → `server::tool`）
- 连续同类调用折叠（`read × 3`）

---

## 5. 与其他维度的交互

```
[输出解析] --(清洗后的 content)--> [记忆系统]
[输出解析] --(error 过滤决策)--> [状态管理]
[输出解析] --(tool_hint 文本)--> [渠道系统]
[输出解析] <--(原始 LLMResponse)-- [Provider 层]
[输出解析] <--(tool result 字符串)-- [工具系统]
[输出解析] <--(session + history)-- [状态管理]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 记忆系统 | 清洗后的 assistant/user/tool 消息 | `_save_turn()` 追加到 `session.messages` |
| 输出到 | 状态管理 | `last_consolidated` 边界、会话更新 | `session.updated_at = datetime.now()` |
| 输出到 | 渠道系统 | 进度提示（thought + tool_hint） | `on_progress(thought)` / `on_progress(hint, tool_hint=True)` |
| 依赖 | Provider 层 | `LLMResponse`（content, tool_calls, finish_reason, reasoning_content） | `provider.chat_with_retry()` |
| 依赖 | 工具系统 | 工具执行结果字符串 | `self.tools.execute()` → `add_tool_result()` |
| 依赖 | 状态管理 | 当前会话历史 | `session.get_history()` |
| 依赖 | Prompt 构建 | `_RUNTIME_CONTEXT_TAG` 用于识别需剥离的元数据 | `ContextBuilder._RUNTIME_CONTEXT_TAG` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **假设 provider 是"不可靠的"**：`_safe_chat` 捕获所有异常包装为 error response，`chat_with_retry` 对 transient error 重试 3 次，loop 层对 error response 拒绝持久化。三层防御假设网络、API、模型都可能出错。
2. **假设模型输出格式不稳定**：`strip_think` 从简单正则演进为覆盖 6 种泄漏场景的复杂过滤器，假设不同模型/部署方式会产生各种畸形的模板泄漏。
3. **假设历史记录是 append-only 的**：`Session.messages` 只增不减（清理由 memory consolidation 负责），所以 `_save_turn` 的过滤必须在写入前完成，一旦写入就无法撤回。
4. **假设用户不关心完整的工具结果**：16K 截断意味着作者假设工具输出的后半部分通常是冗余的（如大文件的尾部、长网页的页脚）。

### 6.2 这个设计的代价/风险

1. **Error 响应完全丢失上下文**：当 `finish_reason == "error"` 时，不仅不存历史，连当前轮次的 `messages` 列表也不会被更新。如果这是多轮 tool-call 后的最终回复，用户看不到任何中间结果。代码中用 `final_content = clean or "Sorry, I encountered an error..."` 做兜底，但信息损失是真实的。
2. **Tool hint 的信息密度过低**：原始实现只显示第一个参数的前 40 字符，对于 `exec` 工具（长命令）或 `write_file`（大段内容）几乎无法传达有效信息。`8ca99600` 的注册表重写缓解了这个问题，但增加了维护负担——每新增一个工具可能需要更新 `FORMATS` 字典。
3. **Runtime context 剥离的脆弱性**：`_save_turn` 用字符串前缀匹配 `ContextBuilder._RUNTIME_CONTEXT_TAG`，如果 `build_messages` 的合并格式改变（如增加/减少换行），剥离逻辑会失效。这是一个跨文件的隐式契约。
4. **Think 剥离与 reasoning_content 的竞态**：`_strip_think` 从 `content` 中移除 `<think>`，但 `reasoning_content` 字段保留了原始推理内容。如果某个 provider 将推理同时放在 `content` 和 `reasoning_content` 中，用户看不到但历史记录中也没有——推理内容被完全丢弃。只有支持 `reasoning_content` 的 provider（Kimi、DeepSeek-R1）能保留它。

### 6.3 如果要重新设计，可能会改变什么

1. **将 `_save_turn` 的过滤规则配置化**：当前 16K 截断、runtime context 剥离、空消息过滤都是硬编码。可以考虑一个 `PersistenceFilter` 抽象，让不同部署场景（轻量个人助手 vs 长会话分析机器人）自定义规则。
2. **Error 响应的降级存储**：不进入 LLM 历史，但存入一个单独的 `errors.jsonl` 供调试。当前 error 只通过 `logger.error` 输出，在 production 环境中可能丢失。
3. **Tool hint 的延迟加载**：当前 `_tool_hint` 在 tool-call 发生时同步执行。如果工具注册表很大，可以考虑异步/缓存。不过当前实现性能足够，这不是瓶颈。
4. **Think 剥离的更早介入**：当前在 loop 层剥离，但 streaming 场景下已经需要在 delta 层面过滤（`_filtered_stream`）。如果所有 provider 都统一返回原始字节流，think 剥离可以下沉到更底层的流处理器。

### 6.4 对我自己设计 Agent 系统的启示

> **输出解析不是"锦上添花"的格式化层，而是系统稳定性的最后一道防线。** nanobot 的代码表明，一个轻量 Agent 的核心脆弱点不在于"模型不够聪明"，而在于"模型的异常输出被反复喂回模型"。`_save_turn` 中 4 行过滤逻辑（空 assistant、截断 tool、剥离 runtime、替换 image）比任何 prompt engineering 都更能保障系统的长期稳定运行。设计 Agent 时，应该为"模型会出错"做防御性架构，而不是假设模型总是返回合法内容。

---

## 附录：关键源码索引

| 机制 | 文件路径 | 行号范围 |
|------|---------|---------|
| Think 块剥离（loop 层） | `nanobot/agent/loop.py` | L165-L170 |
| Think 块剥离（全局工具） | `nanobot/utils/helpers.py` | `strip_think()` 函数 |
| Error 响应过滤 | `nanobot/agent/loop.py` | L232-L245 |
| 空 content 消毒 | `nanobot/providers/base.py` | L108-L152 |
| 回合持久化防腐 | `nanobot/agent/loop.py` | L458-L491 |
| 工具提示格式化（原始） | `nanobot/agent/loop.py` | L172-L181 |
| 工具提示格式化（重写） | `nanobot/agent/loop.py` | `8ca99600` 引入的 `_tool_hint` |
| 流式 think 过滤 | `nanobot/agent/loop.py` | `9d5e511a` 引入的 `_filtered_stream` |
| History think 剥离 | `nanobot/agent/memory.py` | `899a9073` 引入的 `append_history` |
