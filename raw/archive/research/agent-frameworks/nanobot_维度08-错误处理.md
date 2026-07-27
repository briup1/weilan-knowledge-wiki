# 维度 8：错误处理

## 1. 一句话定位

nanobot 的错误处理是一个"分层降级"体系：Provider 层做自动重试、Registry 层做工具级错误提示注入、Loop 层做消息级异常兜底、Memory 层做后台任务降级归档。没有统一的 catch-all，而是让每一层只处理自己能恢复的错误，无法恢复的就向上抛或就地降级。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有这套分层错误处理，系统会在多个层面崩溃：

- **Provider 层缺失重试**：当 LLM 返回 429/503 时，`chat_with_retry` 会直接抛出异常，`_run_agent_loop` 没有捕获 Provider 异常（它只捕获 `response.finish_reason == "error"`），导致整个 `_process_message` 异常上抛到 `_dispatch` 的兜底 catch，用户收到一句生硬的 "Sorry, I encountered an error."，且没有任何重试机会。

- **Registry 层缺失错误提示**：工具执行失败（如 Shell 命令不存在）时，如果直接抛出异常，LLM 看不到错误上下文，下一轮迭代会盲目重复同样的工具调用，陷入死循环。`_HINT` 的存在正是为了让 LLM 在收到错误后"分析错误并尝试不同方法"。

- **Loop 层缺失兜底**：`_process_message` 内部任何未捕获异常（如文件 IO 错误、JSON 解析错误）会直接终止整个 Agent 进程，因为 `_run_agent_loop` 没有 try-catch。`_dispatch` 的 `except Exception` 是防止单条消息搞崩整个服务的最后一道防线。

- **Memory 层缺失降级**：如果 `consolidate()` 失败就抛异常，`maybe_consolidate_by_tokens` 会中断 token 清理循环，导致会话历史持续增长，最终超过上下文窗口上限，引发 LLM 400 错误。

### 2.2 OpenCode 的具体触发条件

| 触发条件 | 代码位置 |
|---------|---------|
| LLM 返回 `finish_reason == "error"` | `nanobot/agent/loop.py:L236` |
| 工具执行抛出任意异常 | `nanobot/agent/tools/registry.py:L58` |
| 工具返回字符串以 `"Error"` 开头 | `nanobot/agent/tools/registry.py:L55` |
| 参数校验失败 | `nanobot/agent/tools/registry.py:L52` |
| Provider 返回瞬态错误（429/503 等） | `nanobot/providers/base.py:L269` |
| Memory consolidation 抛出异常 | `nanobot/agent/memory.py:L197` |
| 连续 3 次 consolidation 失败 | `nanobot/agent/memory.py:L203` |
| 消息处理任何未捕获异常 | `nanobot/agent/loop.py:L326` |
| 用户发送 `/stop` | `nanobot/agent/loop.py:L272` |

---

## 3. 核心设计思路

### 3.1 抽象模型

```
[LLM Provider] --(错误响应)--> [Provider 层: 重试/降级]
                                    |
                                    v
[Tool Registry] --(执行异常)--> [Registry 层: 捕获+提示注入]
                                    |
                                    v
[Agent Loop] --(未捕获异常)--> [Loop 层: 兜底/过滤]
                                    |
                                    v
[Memory Store] --(固化失败)--> [Memory 层: 连续失败降级]
```

每一层的错误处理遵循"恢复优先"原则：能恢复的就恢复（重试、提示、降级），不能恢复的就地消化，绝不向上传播导致上层崩溃。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 错误处理分层 | 四层各自处理（Provider/Registry/Loop/Memory） | 统一顶层 try-catch | Loop 没有 catch Provider 异常，Registry 没有 catch Memory 异常，各层职责边界清晰；统一 catch 会丢失分层恢复的机会 |
| 工具错误提示 | 用 `_HINT` 字符串注入到错误返回中 | 在 System Prompt 中统一教 LLM 处理错误 | `_HINT` 只在错误发生时才出现（`registry.py:L55-L59`），避免污染正常对话上下文；且不同工具的错误需要不同提示 |
| Memory 失败降级 | 连续失败 3 次后原始归档 | 失败即抛异常或静默丢弃 | `memory.py:L201-L208` 的 `_fail_or_raw_archive` 保证数据不丢；如果静默丢弃则历史丢失，如果抛异常则阻塞主循环 |
| LLM error 过滤 | `finish_reason=="error"` 时不存入历史 | 直接存入历史让 LLM 自己学习 | `loop.py:L234-L239` 明确注释 "they can poison the context and cause permanent 400 loops"，说明作者被这个问题坑过 |

### 3.3 数据流/控制流

```
用户消息 -> _dispatch() [获取全局锁]
    -> _process_message()
        -> maybe_consolidate_by_tokens() [Token 超限触发]
            -> consolidate() [LLM 驱动固化]
                -> 成功: 更新 MEMORY.md + HISTORY.md
                -> 失败: _fail_or_raw_archive() [3次后降级]
        -> _run_agent_loop()
            -> chat_with_retry() [Provider 调用]
                -> 瞬态错误: 重试 3 次
                -> 非瞬态错误: 返回 finish_reason="error"
            -> 有 tool_calls:
                -> tools.execute() [Registry 执行]
                    -> 参数错误: 返回 Error + _HINT
                    -> 执行异常: 返回 Error + _HINT
                    -> 正常: 返回结果
                -> 继续下一轮迭代
            -> 无 tool_calls:
                -> finish_reason == "error": 过滤，不存历史，break
                -> 正常: 存历史，break
        -> _save_turn() [保存到 session]
    -> publish_outbound() [返回用户]
    -> except Exception: 兜底返回 "Sorry..."
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：Provider 层自动重试

**作用**：对 LLM 瞬态错误（429/503 等）自动重试 3 次，对非瞬态错误（如不支持图片）降级处理。

**设计意图**：把网络/服务波动消化在 Provider 层，不让上层感知。`_safe_chat` 将异常转换为 `LLMResponse(finish_reason="error")`，让重试逻辑可以用统一的分支判断。

**关键源码**（`nanobot/providers/base.py:L225-L284`）：

```python
    async def _safe_chat(self, **kwargs: Any) -> LLMResponse:
        """Call chat() and convert unexpected exceptions to error responses."""
        try:
            return await self.chat(**kwargs)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            return LLMResponse(content=f"Error calling LLM: {exc}", finish_reason="error")

    async def chat_with_retry(self, ...):
        for attempt, delay in enumerate(self._CHAT_RETRY_DELAYS, start=1):
            response = await self._safe_chat(**kw)
            if response.finish_reason != "error":
                return response
            if not self._is_transient_error(response.content):
                if self._is_image_unsupported_error(response.content):
                    stripped = self._strip_image_content(messages)
                    if stripped is not None:
                        return await self._safe_chat(**{**kw, "messages": stripped})
                return response  # 非瞬态错误，直接返回
            logger.warning("...retrying in {}s...", delay)
            await asyncio.sleep(delay)
        return await self._safe_chat(**kw)
```

① `_safe_chat` 把异常转为 error response —— 这样重试循环不需要处理异常分支，统一用 `finish_reason` 判断。
② 瞬态错误重试 3 次 —— `_CHAT_RETRY_DELAYS = (1, 2, 4)` 指数退避。
③ 图片不支持错误自动降级 —— 把 `image_url` 替换为 `[image omitted]` 后重试，而不是抛异常。

---

### 机制 B：Registry 层统一异常捕获 + _HINT 注入

**作用**：所有工具执行的错误被统一捕获，并附加提示语让 LLM 在下一轮迭代中自我修正。

**设计意图**：`_HINT` 不是静态配置，而是动态注入到错误返回中的。这利用了 LLM 的 in-context learning：错误发生时，上下文里立刻出现 "Analyze the error above and try a different approach"，比 System Prompt 中的静态指令更及时、更聚焦。

**关键源码**（`nanobot/agent/tools/registry.py:L38-L59`）：

```python
    async def execute(self, name: str, params: dict[str, Any]) -> str:
        _HINT = "\n\n[Analyze the error above and try a different approach.]"
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found. Available: {', '.join(self.tool_names)}"
        try:
            params = tool.cast_params(params)      # ① 类型转换
            errors = tool.validate_params(params)   # ② Schema 校验
            if errors:
                return f"Error: Invalid parameters..." + _HINT
            result = await tool.execute(**params)
            if isinstance(result, str) and result.startswith("Error"):
                return result + _HINT               # ③ 工具自身返回错误也加提示
            return result
        except Exception as e:
            return f"Error executing {name}: {str(e)}" + _HINT  # ④ 异常捕获
```

① 参数转换和校验失败 —— 返回结构化错误，LLM 能看到具体哪个参数不对。
② 工具返回 `"Error..."` —— 如 Shell 工具返回 `"Error: command not found"`，也追加 `_HINT`。
③ 未捕获异常 —— 任何 bug 都被兜住，不会传播到 Loop 层。
④ `_HINT` 只出现在错误路径 —— 正常返回不带提示，避免污染上下文。

---

### 机制 C：Loop 层 error 响应过滤 + 全局兜底

**作用**：防止 LLM 返回的 error 内容污染会话历史（session poisoning），同时用全局锁保证单条消息的异常不会搞崩整个服务。

**设计意图**：`finish_reason == "error"` 的响应如果存入历史，下一轮迭代 LLM 会基于这个错误上下文继续生成，可能导致永久 400 循环（issue #1303）。所以直接 break 且不保存到 session。

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
                    messages, clean, ...
                )
                final_content = clean
                break
```

① `finish_reason == "error"` 时直接 break —— 不调用 `add_assistant_message`，错误内容不进历史。
② 返回友好的兜底文案 —— 而不是把原始错误堆栈暴露给用户。

**关键源码**（`nanobot/agent/loop.py:L311-L331`）：

```python
    async def _dispatch(self, msg: InboundMessage) -> None:
        """Process a message under the global lock."""
        async with self._processing_lock:
            try:
                response = await self._process_message(msg)
                if response is not None:
                    await self.bus.publish_outbound(response)
                elif msg.channel == "cli":
                    await self.bus.publish_outbound(OutboundMessage(
                        channel=msg.channel, chat_id=msg.chat_id,
                        content="", metadata=msg.metadata or {},
                    ))
            except asyncio.CancelledError:
                logger.info("Task cancelled for session {}", msg.session_key)
                raise
            except Exception:
                logger.exception("Error processing message for session {}", msg.session_key)
                await self.bus.publish_outbound(OutboundMessage(
                    channel=msg.channel, chat_id=msg.chat_id,
                    content="Sorry, I encountered an error.",
                ))
```

① `asyncio.CancelledError` 单独处理并 re-raise —— 让 `/stop` 取消信号能正确传播。
② `except Exception` 是最后一道防线 —— 任何 `_process_message` 内部未处理的异常（文件 IO、JSON 解析、索引越界等）都被兜住。
③ 全局锁 `_processing_lock` —— 保证同一时间只处理一条消息，错误不会并发扩散。

---

### 机制 D：Memory 层连续失败降级

**作用**：LLM 驱动的记忆固化不是关键路径，失败时不应阻塞主循环，但也不能静默丢弃历史数据。

**设计意图**：`consolidate()` 是后台任务（`loop.py:L446` 通过 `_schedule_background` 调用），它的失败不应影响用户响应。但历史数据有价值，所以设计了三阶降级：正常摘要 -> 重试 -> 原始归档。

**关键源码**（`nanobot/agent/memory.py:L114-L208`）：

```python
    async def consolidate(self, messages, provider, model) -> bool:
        try:
            response = await provider.chat_with_retry(..., tool_choice=forced)
            if response.finish_reason == "error" and _is_tool_choice_unsupported(response.content):
                response = await provider.chat_with_retry(..., tool_choice="auto")  # ① 降级 tool_choice
            if not response.has_tool_calls:
                return self._fail_or_raw_archive(messages)          # ② LLM 没调用 save_memory
            args = _normalize_save_memory_args(response.tool_calls[0].arguments)
            if args is None or "history_entry" not in args or ...:
                return self._fail_or_raw_archive(messages)          # ③ 参数格式不对
            # ... 保存成功
            self._consecutive_failures = 0
            return True
        except Exception:
            logger.exception("Memory consolidation failed")
            return self._fail_or_raw_archive(messages)              # ④ 异常也降级

    def _fail_or_raw_archive(self, messages: list[dict]) -> bool:
        self._consecutive_failures += 1
        if self._consecutive_failures < self._MAX_FAILURES_BEFORE_RAW_ARCHIVE:
            return False                                              # ⑤ 前 2 次返回 False，上层可重试
        self._raw_archive(messages)                                   # ⑥ 第 3 次原始归档
        self._consecutive_failures = 0
        return True
```

① `tool_choice` 不支持时降级为 `"auto"` —— 兼容不同 Provider。
②-④ 任何失败都走到 `_fail_or_raw_archive` —— 不抛异常，不阻塞。
⑤ 前 2 次返回 `False` —— `archive_messages` 会重试（`memory.py:L297-L299`）。
⑥ 第 3 次原始归档 —— 把原始消息 dump 到 HISTORY.md，数据不丢，只是没有 LLM 摘要。

---

## 5. 与其他维度的交互

```
[错误处理] --(错误响应)--> [输出解析]  (finish_reason="error" 过滤)
[错误处理] --(工具错误)--> [工具系统]   (Registry.execute 返回 Error + _HINT)
[错误处理] --(降级归档)--> [记忆系统]   (_fail_or_raw_archive 写入 HISTORY.md)
[错误处理] <--(瞬态错误)-- [LLM Provider] (chat_with_retry 重试逻辑)
[错误处理] <--(未捕获异常)-- [编排循环]   (_dispatch 兜底 catch)
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 输出解析 | `finish_reason == "error"` 时不存入历史，防止 session poisoning | `loop.py:L234-L239` |
| 输出到 | 工具系统 | 工具执行错误通过 `_HINT` 提示注入回传给 LLM | `registry.py:L40-L59` |
| 输出到 | 记忆系统 | 固化失败时原始归档到 HISTORY.md | `memory.py:L210-L219` |
| 依赖 | LLM Provider | Provider 返回瞬态错误时触发重试 | `providers/base.py:L263-L284` |
| 依赖 | 编排循环 | Loop 的 `_dispatch` 是全局异常兜底 | `loop.py:L311-L331` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"LLM 的 error 响应比异常更危险"**：Loop 对 `finish_reason == "error"` 的处理比 `except Exception` 更谨慎（前者过滤不存历史，后者只是兜底返回）。作者假设 LLM 生成的错误内容如果进入上下文，会导致比代码异常更持久的恶性循环。

2. **"工具错误应该让 LLM 自己修"**：`_HINT` 的设计假设 LLM 具备根据错误信息自我修正的能力，不需要人工介入或复杂的错误码体系。

3. **"后台任务可以降级，主循环不能停"**：Memory 固化有 `_fail_or_raw_archive` 而主循环没有，因为作者假设：用户消息处理是关键路径，必须给出响应；记忆固化是后台优化，可以降级为原始存储。

### 6.2 这个设计的代价/风险

1. **`_HINT` 的硬编码英文提示**：如果用户用中文交流，`[Analyze the error above...]` 会混入中文上下文，可能降低 LLM 理解效率。但代码中没有国际化机制，这是"小而美"的妥协。

2. **Memory 原始归档的数据膨胀**：`_raw_archive` 把完整消息 dump 到 HISTORY.md，长期运行后文件会很大。但代码中没有清理机制，作者似乎假设用户会手动管理或文件系统足够大。

3. **Loop 兜底 catch 的粒度太粗**：`_dispatch` 的 `except Exception` 捕获了所有异常，但返回给用户的只有 "Sorry, I encountered an error."，没有错误码或日志指引，调试困难。不过 `logger.exception` 会记录详细堆栈到日志文件。

4. **Provider 重试的延迟是固定的**：`_CHAT_RETRY_DELAYS = (1, 2, 4)` 是硬编码，没有根据 Provider 或错误类型动态调整。对于某些 Provider 的 429，可能需要更长的退避。

### 6.3 如果要重新设计，可能会改变什么

1. **给 `_HINT` 加语言感知**：根据当前对话语言动态选择提示语，或把提示语放到配置中。

2. **Memory 归档加压缩/轮转**：原始归档可以按日期分片，或超过一定大小后触发 LLM 二次摘要。

3. **Loop 兜底返回更友好的错误分类**：比如区分 "LLM 服务暂时不可用"、"工具执行失败"、"内部错误"，让用户知道是暂时问题还是任务本身有问题。

4. **Provider 重试配置化**：把 `_CHAT_RETRY_DELAYS` 和 `_TRANSIENT_ERROR_MARKERS` 放到配置中，方便适配不同 Provider。

### 6.4 对我自己设计 Agent 系统的启示

最核心的启示是：**错误处理应该按"恢复能力"分层，而不是按"调用栈"分层**。Provider 能重试网络错误，Registry 能提示 LLM 自修复，Loop 能兜底防止服务崩溃，Memory 能降级保证数据不丢 —— 每一层只处理自己有能力恢复的错误，没能力恢复的就地消化或向上抛。这比一个巨大的 try-catch 更健壮，也更易维护。
