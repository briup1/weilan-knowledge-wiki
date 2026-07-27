# 维度 04：上下文管理

## 1. 一句话定位

nanobot 的上下文管理负责将「System Prompt + 未固化历史消息 + 当前用户输入 + 运行时元数据」组装成 LLM 可直接消费的消息列表，并在持久化前对消息进行"消毒"（截断/剥离/过滤），确保历史记录既完整又不会污染后续推理。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有上下文管理，系统会在三个层面出现故障：

1. **LLM 调用失败**：`_build_runtime_context()` 生成的时间/渠道元数据若作为独立消息插入，会形成连续两条 `user` 角色消息（`nanobot/agent/context.py:L133-138`）。部分 Provider（如早期 OpenAI API）会拒绝这种消息序列，直接返回 400。

2. **历史记录中毒**：工具返回结果（如 `cat` 一个大文件）可能长达数万字符。若原样存入 `session.messages`，下次加载时 token 数会瞬间爆炸，触发上下文窗口溢出，导致循环终止或高额 API 费用。

3. **会话状态错乱**：如果历史消息以 `tool` 或 `assistant` 开头（比如上次会话最后一条是工具结果），LLM 会收到一条"没有前置 user 消息"的孤儿工具结果，模型可能产生幻觉回复或拒绝继续对话。

### 2.2 nanobot 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 每次收到用户消息时构建上下文 | `nanobot/agent/loop.py:L421-L427` | `_process_message()` 调用 `build_messages()` |
| 历史消息加载时丢弃非 user 开头 | `nanobot/session/manager.py:L51-L55` | `get_history()` 遍历找到第一个 `role == "user"` |
| 工具结果超过 16K 字符时截断 | `nanobot/agent/loop.py:L466-L467` | `_save_turn()` 中 `len(content) > _TOOL_RESULT_MAX_CHARS` |
| 持久化前剥离 RuntimeContext | `nanobot/agent/loop.py:L468-L475` | `_save_turn()` 检测 `_RUNTIME_CONTEXT_TAG` 并分割 |

---

## 3. 核心设计思路

### 3.1 抽象模型

```
[Session.messages] --(last_consolidated 切割)--> [未固化消息]
                                      |
                                      v
[未固化消息] --(get_history: 丢弃前缀非user)--> [对齐历史]
                                      |
                                      v
[对齐历史] + [System Prompt] + [Runtime Context + 用户输入] --(build_messages)--> [LLM 消息列表]
                                      |
                                      v
[LLM 响应] + [工具结果] --(多轮迭代)--> [完整消息链]
                                      |
                                      v
[完整消息链] --(_save_turn: 截断/剥离/过滤)--> [持久化到 Session.messages]
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| RuntimeContext 合并到 user message | 将运行时元数据拼接到用户消息内容中 | 作为独立 system 消息或独立 user 消息插入 | `context.py:L133-138` 注释明确说明："避免连续同角色消息被 Provider 拒绝"；且 RuntimeContext 是**元数据而非指令**，不应混入 system prompt |
| 丢弃非 user 开头的历史消息 | `get_history()` 遍历找到第一个 user 消息后截断 | 保留所有消息，让 LLM 自行处理 | `manager.py:L51-55` 的注释说明："避免孤儿 tool_result 块"；LLM 协议要求 tool/assistant 消息必须有前置 user 消息 |
| 持久化前剥离 RuntimeContext | `_save_turn()` 分割字符串，只保留用户原文 | 原样保存完整拼接内容 | `loop.py:L468-475`：RuntimeContext 包含动态时间戳，若持久化会导致历史记录膨胀且每次加载都携带过时时间信息 |
| 工具结果截断而非丢弃 | 超过 16K 时保留前 16K + "... (truncated)" | 完全丢弃大结果或分片存储 | `loop.py:L466-467`：截断保留关键信息头部（通常是错误摘要/文件开头），同时防止 token 爆炸 |

### 3.3 数据流/控制流

```
用户消息到达
    |
    v
_process_message() [loop.py:L356]
    |
    +-- session.get_history(max_messages=0)  [manager.py:L46]
    |       +-- 取 messages[last_consolidated:]  
    |       +-- 丢弃前缀非 user 消息
    |       +-- 过滤保留 role/content/tool_calls/tool_call_id/name
    |
    +-- context.build_messages(...) [context.py:L120]
    |       +-- build_system_prompt()  [context.py:L27]
    |       +-- _build_runtime_context()  [context.py:L101]
    |       +-- _build_user_content()  [context.py:L146]
    |       +-- 合并 runtime_ctx + user_content 为单条 user 消息
    |
    +-- _run_agent_loop()  [loop.py:L183]
    |       +-- 迭代调用 LLM
    |       +-- add_assistant_message() / add_tool_result()
    |
    +-- _save_turn()  [loop.py:L458]
    |       +-- 跳过空 assistant 消息
    |       +-- 截断超长 tool 结果
    |       +-- 剥离 RuntimeContext
    |       +-- 将图片 base64 替换为 "[image]" 占位符
    |
    +-- sessions.save(session)  [manager.py:L163]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：RuntimeContext 合并到 User Message

**作用**：将当前时间、渠道、Chat ID 等运行时元数据注入到本轮 LLM 调用中，同时避免破坏消息角色交替规则。

**设计意图**：为什么不把 RuntimeContext 作为独立消息或 system prompt 的一部分？

- **不作为 system prompt**：RuntimeContext 是**动态元数据**（时间每次不同），而 system prompt 是相对静态的身份定义，混合会破坏 system prompt 的稳定性。
- **不作为独立 user 消息**：OpenAI 等 Provider 的 API 要求消息序列中不能出现连续同角色消息（`user` 后不能直接跟另一个 `user`），否则返回 400。
- **合并到 user message 是折中**：用 `\n\n` 分隔元数据和用户原文，LLM 仍能清晰区分，同时满足 API 格式要求。

**关键源码**（`nanobot/agent/context.py:L129-L144`）：
```python
# L129-L131: 分别构建运行时元数据和用户内容
runtime_ctx = self._build_runtime_context(channel, chat_id)
user_content = self._build_user_content(current_message, media)

# L133-L138: 合并为单条 user 消息，避免连续同角色消息被 Provider 拒绝
if isinstance(user_content, str):
    merged = f"{runtime_ctx}\n\n{user_content}"
else:
    merged = [{"type": "text", "text": runtime_ctx}] + user_content

return [
    {"role": "system", "content": self.build_system_prompt(skill_names)},
    *history,
    {"role": "user", "content": merged},
]
```

---

### 机制 B：丢弃非 user 开头的历史消息

**作用**：确保返回给 LLM 的历史消息序列始终以 `user` 消息开头，避免孤儿工具结果或 assistant 回复。

**设计意图**：为什么必须丢弃前缀？

nanobot 的消息序列遵循严格的 ReAct 模式：`user -> assistant (tool_calls) -> tool -> assistant -> user -> ...`。如果历史片段以 `tool` 或 `assistant` 开头，意味着上一次会话的最后一条消息是工具结果或模型回复，但 LLM 看不到触发它的用户请求——这会导致模型困惑或产生幻觉。代码中的注释明确称之为 "orphaned tool_result blocks"。

**关键源码**（`nanobot/session/manager.py:L46-L64`）：
```python
def get_history(self, max_messages: int = 500) -> list[dict[str, Any]]:
    """Return unconsolidated messages for LLM input, aligned to a user turn."""
    unconsolidated = self.messages[self.last_consolidated:]
    sliced = unconsolidated[-max_messages:]

    # L51-L55: 丢弃前缀非 user 消息，避免孤儿 tool_result 块
    for i, m in enumerate(sliced):
        if m.get("role") == "user":
            sliced = sliced[i:]
            break

    out: list[dict[str, Any]] = []
    for m in sliced:
        entry: dict[str, Any] = {"role": m["role"], "content": m.get("content", "")}
        for k in ("tool_calls", "tool_call_id", "name"):
            if k in m:
                entry[k] = m[k]
        out.append(entry)
    return out
```

---

### 机制 C：持久化前的消息消毒（_save_turn）

**作用**：在将本轮消息存入 `session.messages` 之前，执行三项消毒操作：截断超长工具结果、剥离 RuntimeContext、过滤空消息和图片 base64。

**设计意图**：为什么不原样保存 LLM 看到的完整消息列表？

1. **RuntimeContext 是临时的**：包含 `Current Time: 2026-05-08 10:30 (Friday) (CST)` 这类动态信息，若持久化，下次加载时历史记录中会充满过时时间戳，既浪费 token 又误导模型。
2. **工具结果可能极大**：`cat /var/log/syslog` 可能返回数万字符，原样保存会导致下次加载时 token 数瞬间超标。
3. **图片 base64 不可持久**：一张图片的 base64 编码可能数 MB，持久化到 JSONL 会急剧膨胀文件体积，因此替换为 `"[image]"` 占位符。

**关键源码**（`nanobot/agent/loop.py:L458-L491`）：
```python
def _save_turn(self, session: Session, messages: list[dict], skip: int) -> None:
    """Save new-turn messages into session, truncating large tool results."""
    from datetime import datetime
    for m in messages[skip:]:
        entry = dict(m)
        role, content = entry.get("role"), entry.get("content")

        # L464-L465: 跳过空 assistant 消息，防止污染会话上下文
        if role == "assistant" and not content and not entry.get("tool_calls"):
            continue

        # L466-L467: 截断超长工具结果，防止历史记录 token 爆炸
        if role == "tool" and isinstance(content, str) and len(content) > self._TOOL_RESULT_MAX_CHARS:
            entry["content"] = content[:self._TOOL_RESULT_MAX_CHARS] + "\n... (truncated)"

        # L468-L488: 剥离 RuntimeContext，只保留用户原文
        elif role == "user":
            if isinstance(content, str) and content.startswith(ContextBuilder._RUNTIME_CONTEXT_TAG):
                parts = content.split("\n\n", 1)
                if len(parts) > 1 and parts[1].strip():
                    entry["content"] = parts[1]
                else:
                    continue
            if isinstance(content, list):
                filtered = []
                for c in content:
                    # L479-L480: 从多模态消息中剥离 RuntimeContext
                    if c.get("type") == "text" and isinstance(c.get("text"), str) and c["text"].startswith(ContextBuilder._RUNTIME_CONTEXT_TAG):
                        continue
                    # L481-L483: 将图片 base64 替换为占位符，避免 JSONL 膨胀
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

---

## 5. 与其他维度的交互

```
[上下文管理] --(输出 LLM 消息列表)--> [编排循环]
[上下文管理] <--(依赖历史消息)-- [状态管理 (Session)]
[上下文管理] <--(依赖 System Prompt + Memory)-- [Prompt 构建]
[上下文管理] <--(依赖未固化消息边界)-- [记忆系统 (last_consolidated)]
[上下文管理] --(输出 tool_calls/tool_result 格式)--> [工具系统]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环 | 完整的 `messages` 列表供 `_run_agent_loop()` 消费 | `loop.py:L421-L427` `build_messages()` 调用 |
| 依赖 | 状态管理 | `session.get_history()` 返回未固化的历史消息切片 | `manager.py:L46` `get_history()` |
| 依赖 | 记忆系统 | `last_consolidated` 决定历史消息的起始边界 | `manager.py:L48` `self.messages[self.last_consolidated:]` |
| 依赖 | Prompt 构建 | `build_system_prompt()` 组装身份、Bootstrap、Memory、Skills | `context.py:L27` `build_system_prompt()` |
| 输出到 | 工具系统 | `add_tool_result()` / `add_assistant_message()` 将工具执行结果格式化为标准消息 | `context.py:L168-L190` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **作者假设 LLM Provider 对消息格式有严格限制**：`build_messages()` 中显式合并 user 消息，说明作者认为 Provider 会拒绝连续同角色消息（这是 OpenAI 等主流 API 的实际行为）。
2. **作者假设工具结果头部信息更重要**：截断策略保留前 16K 字符而非尾部，说明假设错误信息、文件开头、命令输出的前部包含更多关键上下文。
3. **作者假设 RuntimeContext 是"每次新鲜"的**：剥离策略说明作者认为时间戳和渠道信息只对**当前轮次**有意义，不应污染长期历史。

### 6.2 这个设计的代价/风险

1. **截断可能导致信息丢失**：`loop.py:L466-L467` 的硬截断不区分内容类型，如果工具返回的是 JSON 或代码，截断后可能破坏结构完整性，导致后续轮次解析失败。
2. **图片信息完全丢失**：`loop.py:L481-L483` 将 base64 替换为 `"[image]"`，模型在后续轮次无法"看到"图片内容，只能依赖之前的文本描述。对于多轮视觉任务，这可能造成上下文断裂。
3. **get_history 的丢弃策略过于激进**：`manager.py:L51-L55` 一旦遇到非 user 前缀就丢弃前面所有消息，如果用户连续发送了两条消息（某些渠道允许），第二条会被错误地丢弃前缀。

### 6.3 如果要重新设计，可能会改变什么

1. **结构化截断而非硬截断**：对工具结果按语义截断（如保留完整 JSON 对象、按段落截断），而非简单的字符切割。
2. **保留图片的文本描述**：在替换 base64 为 `"[image]"` 时，同时保存一个 LLM 生成的图片描述到消息中，让后续轮次仍能"理解"图片内容。
3. **更灵活的历史对齐**：`get_history()` 的丢弃策略可以改为"找到第一个可以作为合法起点的消息"（user 或带有完整 tool_calls 的 assistant），而非严格限定 user。

### 6.4 对我自己设计 Agent 系统的启示

> **"临时元数据必须和持久化历史严格分离"**——nanobot 通过 `_save_turn()` 的剥离操作展示了这一原则：运行时注入的动态信息（时间、渠道）只在当前轮次生效，绝不进入长期存储。这是防止历史记录"慢性中毒"的关键设计。
