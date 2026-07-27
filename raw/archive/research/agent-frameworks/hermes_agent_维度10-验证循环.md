# 维度名：验证循环（Validation Loop）

## 1. 一句话定位

验证循环是 Hermes Agent 在「LLM 决策 → 实际执行」之间插入的多层把关层，它包含三类验证：**预校验**（schema 清理、参数强制类型）、**许可校验**（危险命令审批 / 安全扫描）、**事后回路校验**（同一调用反复失败/无进展时的护栏中止），共同保证 LLM 不会因为格式错误、误判风险、卡死循环而把代价转嫁给宿主机或用户。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

四类具体故障：

1. **schema 不一致导致整轮请求被后端拒绝**：MCP / Pydantic 工具常生成 `{"anyOf":[{"type":"string"},{"type":"null"}]}` 这种"可空联合"，Anthropic 直接 400；llama.cpp 的 `json-schema-to-grammar` 更激进，碰到 `{"type":"object"}` 没有 `properties` 就拒绝整次调用（`schema_sanitizer.py:5-22` 的注释里贴了原始报错 `Unable to generate parser for this template`）。如果不在投递前清理，轮内任何一个工具的 schema 错都会让本轮 LLM 调用直接失败。
2. **危险命令直接 `rm -rf /`**：terminal 工具收到的命令直接交给 shell。没有 `tools/approval.py` 的 HARDLINE/DANGEROUS 模式匹配，LLM 只要一次幻觉或一次 prompt-injection 就能让宿主机不可恢复（恢复路径：注释 `approval.py:131-138` 明确说"only things with no recovery path"）。
3. **agent 卡在死循环里烧 token**：LLM 习惯性地"再试一次"。`tool_guardrails.py:296-345` 的 `after_call` 计数显示，没有这层就只能让 LLM 自己意识到——而这正是它最不擅长的事情。`run_agent.py:13742-13750` 显示一旦 `_tool_guardrail_halt_decision` 触发，整个 turn 直接给出"我停了，因为护栏触发"的最终回复，不再让 LLM 重试。
4. **slash 命令静默炸缓存**：`/reload-mcp` 会让 provider prompt cache 失效。如果不通过 `slash_confirm.py` 走 Once/Always/Cancel，用户在群聊里不小心点一次就要被罚一段重新计费的 cache miss。

### 2.2 具体触发条件

- **schema 清理**：每次构建 LLM 请求时，`model_tools.py:478-482` 都会无条件调用 `sanitize_tool_schemas(filtered_tools)`，作为常规规范化路径。
- **schema 反应式回退**：仅当 LLM 后端返回 llama.cpp grammar 错误时触发。`run_agent.py:12595-12618` 用 `classified.reason == FailoverReason.llama_cpp_grammar_pattern` 判断，并保护性地用 `llama_cpp_grammar_retry_attempted` 标志位防止重复剥离。
- **HARDLINE 拦截**：`approval.py:813-816` 在 `check_dangerous_command` 入口、`approval.py:937-940` 在 `check_all_command_guards` 入口，都先于 `--yolo`、`approvals.mode=off` 这些"放行开关"运行——这是设计上的"floor below yolo"。
- **DANGEROUS 审批**：`approval.py:823-829` 命中 `DANGEROUS_PATTERNS_COMPILED` 中任意一条且未在 `_session_approved` / `_permanent_approved` 中时，进入审批流。
- **tirith 内容扫描**：`approval.py:977-980` 对每条 terminal 命令执行子进程 `tirith check --json`，按 exit code 0/1/2 → allow/block/warn 决策。
- **工具循环护栏**：`run_agent.py:9858`（concurrent path）和 `run_agent.py:10208`（sequential path）在执行前调用 `before_call`；`run_agent.py:9616` 在执行后通过 `_append_guardrail_observation` 调用 `after_call`。
- **clarify 触发**：完全由 LLM 主动决策。`tools/clarify_tool.py:96-103` 的 description 明确写"Use this tool when: 任务模糊、需要决策权衡、想要保存技能"——它不是验证 LLM，而是让 LLM 主动验证用户意图。

---

## 3. 核心设计思路

### 3.1 抽象模型

```
                      ┌─ before_call(name,args) ─→ allow|warn|block
   LLM tool_calls ──→ │                                   │ block 时返回 synthetic result
                      │                                   ▼
                      └─→ pre-exec guards ──→ check_all_command_guards()
                              │                  │ (HARDLINE → 直接 block)
                              │                  │ (yolo / mode=off → bypass)
                              │                  │ (smart approval → 让 aux LLM 仲裁)
                              │                  │ (CLI/gateway → 阻塞等用户)
                              ▼                  ▼
                          actual exec  ─→  after_call(name,args,result,failed)
                              │                  │ failed: 计数 exact_failure / same_tool
                              │                  │ ok+idempotent: 看是否反复返回相同 hash
                              ▼                  ▼
                       result + (warn ⇒ 拼接guidance) | (halt ⇒ 设定 _halt_decision)
                              │
                              ▼
                       turn 结束时若 _halt_decision 非空 → 强制收尾
```

`schema_sanitizer` 在更上游：每次构建 tool 列表时跑一次"等效转换"，把"形式上能让 LLM 调用、但后端会拒"的 schema 折叠为最大公约数形态。本质是个"输出驱动"的 lint。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 危险命令的"硬底线" | HARDLINE 列表完全独立、置于所有放行开关之上 | 全部走可绕过的 DANGEROUS 列表 | `approval.py:131-138` 注释把"trust 边界"画死："opting into yolo is the user trusting the agent with their files and services, **not trusting it to wipe the disk or power the box off**"。代码上 `check_all_command_guards:937-940` 在 `is_truthy_value(HERMES_YOLO_MODE)` 检查**之前**先 `detect_hardline_command`。 |
| schema 清理是无条件 + 反应式两段 | 启动时无条件做"宽 sanitize"，仅在后端真的拒绝时才做更激进的 `strip_pattern_and_format` | 一上来就把所有 schema 剥光 | `schema_sanitizer.py:316-319` 注释："Cloud providers (OpenAI, Anthropic, OpenRouter, Gemini) accept these keywords fine and rely on them as prompting hints"。剥光会损失 LLM 的提示信息（`pattern: '^\d{4}-\d{2}-\d{2}$'` 是给模型看的格式指导），所以分段。 |
| 审批的三种粒度 | once / session / always 三档持久化 | 二档 yes/no | `approval.py:879-884` 把 session 写进内存 set，always 落到 config.yaml。注释 `prompt_dangerous_approval:589` 明确每次审批返回这四值之一 (`once/session/always/deny`)。三档对应三种心智："我现在要做这个"、"这次会话别再问了"、"以后都别问了"。 |
| 护栏默认只 warn 不 block | `hard_stop_enabled: bool = False` | 默认 hard-stop | `tool_guardrails.py:71-76` 注释："Warnings are enabled by default and never prevent tool execution. Hard stops are explicit opt-in"。原因藏在 `before_call` 的 `_is_idempotent` 判断里——只读工具确实可以反复调用查同一个文件（用户可能改了文件），所以默认走"提示但不拦"避免误伤。 |
| 网关审批用同步阻塞而非 polling | `_ApprovalEntry.event = threading.Event()` + 1s 心跳 | 让 LLM 看到 "approval_required" 然后再下一轮 | `approval.py:1102-1138` 用 `event.wait(timeout=1.0)` 切片，配合 `touch_activity_if_due` 心跳避免被网关 watchdog 误杀。这样 agent 看到的就是 approved 后的真实命令输出，**LLM 完全不知道发生了审批**——避免 LLM 把"审批阻塞"误判为"工具失败"而进入重试循环。 |

### 3.3 数据流/控制流

**A. schema 路径**
```
registry.register(schema=...)                    [启动时]
   ↓
build_tools() → filtered_tools                   [model_tools.py:455]
   ↓
sanitize_tool_schemas(filtered_tools)            [model_tools.py:480]  ← 默认无条件
   ↓ 投递给 LLM
LLM 返回 tool_call → assistant_message
   ↓
[若后端报 grammar 错] strip_pattern_and_format(self.tools)   [run_agent.py:12601]  ← 反应式
   ↓
重试 LLM 调用
```

**B. 危险命令 + 护栏路径**
```
LLM tool_call (terminal, command="...")
   ↓
[run_agent.py:9858] _tool_guardrails.before_call(name, args)
   ↓ allow
[terminal_tool.py:1831] _check_all_guards(command, env_type)
   ↓
   ├─ detect_hardline_command  → block (绝对不可绕过)
   ├─ yolo / mode=off          → bypass
   ├─ tirith subprocess scan
   ├─ detect_dangerous_command (regex)
   ├─ smart approval (aux LLM 仲裁，可选)
   └─ CLI/gateway prompt → once/session/always/deny
   ↓ approved
exec command
   ↓ result
[run_agent.py:9616] _tool_guardrails.after_call(name, args, result, failed=...)
   ↓
decision.action ∈ {warn, halt}
   ↓
[run_agent.py:9622-9625] result += guidance / set _halt_decision
   ↓ turn 末尾
[run_agent.py:13742] 若 _halt_decision 非空 → 强制结束 turn
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：schema sanitizer 的"等效转换"

**作用**：把 LLM 后端无法消化但语义可推断的 schema 形态，原地折叠为最大公约数形态。

**设计意图**：LLM 后端的 schema 接收能力差异极大（Anthropic 拒 nullable union；llama.cpp 拒空 properties；OpenAI Codex 拒顶层 oneOf）。如果让每个工具开发者手动适配每个后端，工具生态会被强耦合。Sanitizer 做"宽进严出"——开发者按 JSON Schema 标准写，sanitizer 负责降级到最差后端能吃的形态。

**关键源码**（`tools/schema_sanitizer.py:171-189`）：
```python
for key in ("anyOf", "oneOf"):
    variants = stripped.get(key)
    if not isinstance(variants, list):
        continue
    non_null = [
        item for item in variants
        if not (isinstance(item, dict) and item.get("type") == "null")
    ]
    # ① 只有"恰好一个非 null 分支"才折叠 — 真联合(string|number)保持不动
    if len(non_null) == 1 and len(non_null) != len(variants):
        replacement = dict(non_null[0]) if isinstance(non_null[0], dict) else {}
        if keep_nullable_hint:
            # ② 折叠后保留 nullable: true 提示 — model_tools._schema_allows_null
            #    会用它来把 LLM emit 的 "null" 字符串映射回 Python None
            replacement.setdefault("nullable", True)
        for meta_key in ("title", "description", "default", "examples"):
            if meta_key in stripped and meta_key not in replacement:
                replacement[meta_key] = stripped[meta_key]
        return strip_nullable_unions(replacement, keep_nullable_hint=keep_nullable_hint)
```

值得看的点：① 区分"nullable union"和"真 union"——这是个语义判断，必须只折叠前者；② "丢了 null 分支但保留 hint"——LLM 后端不能消化 union，但 runtime 协助层（`model_tools.py:606`）能消化 hint，这是把"严格性"在层间合理分配。

### 机制 B：HARDLINE 与 DANGEROUS 的双层防御

**作用**：HARDLINE 列出"无恢复路径"的命令（`rm -rf /`、`mkfs`、`dd of=/dev/sda`、`shutdown`、fork bomb），无论用户开了什么放行开关都拒绝；DANGEROUS 列出"需要审批"的高风险命令。

**设计意图**：把"信任边界"显式化。yolo 模式被设计成"信任 agent 处理我的工作文件"，**不**是"信任 agent 重启我的物理机"。两层分离让 yolo 模式可以被放心使用——用户知道无论 LLM 怎么疯狂，HARDLINE 都不会越线。

**关键源码**（`tools/approval.py:147-178`）：
```python
# ① 命令"位置"匹配 — 只匹配真正在执行的 shell 命令位置，
#    避免 "echo reboot" / "grep 'shutdown' log" 这种字面引用被误判
_CMDPOS = (
    r'(?:^|[;&|\n`]|\$\()'         # start position: 行首 or 分隔符 or 子shell
    r'\s*'
    r'(?:sudo\s+(?:-[^\s]+\s+)*)?'  # 可选 sudo + flags
    r'(?:env\s+(?:\w+=\S*\s+)*)?'   # 可选 env VAR=VAL
    r'(?:(?:exec|nohup|setsid|time)\s+)*'  # 可选 wrapper
    r'\s*'
)

HARDLINE_PATTERNS = [
    (r'\brm\s+(-[^\s]*\s+)*(/|/\*|/ \*)(\s|$)', "recursive delete of root filesystem"),
    # ② 把"系统目录列举"硬编码 — 不试图"智能识别敏感路径"，
    #    显式列举可读、可审计、不会有意外
    (r'\brm\s+(-[^\s]*\s+)*(/home|/root|/etc|/usr|/var|/bin|/sbin|/boot|/lib)(\s|$)', ...),
    (r'\bmkfs(\.[a-z0-9]+)?\b', "format filesystem (mkfs)"),
    (r'\bdd\b[^\n]*\bof=/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*', "dd to raw block device"),
    (r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:', "fork bomb"),
    (_CMDPOS + r'(shutdown|reboot|halt|poweroff)\b', "system shutdown/reboot"),
    ...
]
```

值得看的点：① `_CMDPOS` 精心构造 shell 命令"起始位置"的正则前缀——这是为了把假阳性压到最低（`echo reboot` 不会触发但真的 `; reboot` 会触发），假阳性会让用户对警告麻木；② 不去做"智能路径识别"而是硬编码列举系统目录，是一个"宁可漏报、不可错报"的取舍：HARDLINE 漏报会被下一层 DANGEROUS 接住，但 HARDLINE 错报无法被任何手段绕过会让用户砸键盘。

### 机制 C：归一化攻击表面，规避 obfuscation 绕过

**作用**：在做正则匹配前先归一化命令字符串。

**设计意图**：如果直接拿 LLM 给出的 `command` 跑正则，攻击者（或自带 prompt-injection 的 web 内容）可以用全角 r、Unicode 控制符、ANSI 序列、null byte 来构造"看起来是 `rm -rf /`、正则却匹配不到"的命令。

**关键源码**（`tools/approval.py:329-344`）：
```python
def _normalize_command_for_detection(command: str) -> str:
    from tools.ansi_strip import strip_ansi
    # ① 先把 ANSI escape 全清掉 — CSI/OSC/DCS/8-bit C1 都覆盖
    command = strip_ansi(command)
    # ② 干掉 null byte — 某些 shell 把 \x00 之后的部分当独立命令解释
    command = command.replace('\x00', '')
    # ③ NFKC 规范化 — 把全角 'ｒｍ' 折叠回 'rm'，把变体形式打平
    command = unicodedata.normalize('NFKC', command)
    return command
```

值得看的点：把"安全决策"和"显示给用户的原始命令"分离——归一化只用于 detection，审批 UI 上展示给用户看的依然是原始命令（这样用户能看到攻击痕迹）。这是"安全检查用 canonical form，用户展示用 raw form"的标准范式。

### 机制 D：smart approval — 用辅助 LLM 仲裁误报

**作用**：当 `approvals.mode=smart` 时，把命令和触发原因发给 aux LLM，让它判定 APPROVE / DENY / ESCALATE 三档。

**设计意图**：DANGEROUS_PATTERNS 的正则必然有误报（`python -c "print('hello')"` 命中 "script execution via -c flag"，但完全无害）。直接拒会让 agent 寸步难行；直接放过会失去防御；问用户每次会让用户审批疲劳。Smart approval 是"让另一个 LLM 当门神"——它没有 agent 的目标偏置，更可能做出冷静判断。受 OpenAI Codex 启发（注释里直接 cite 了 `openai/codex#13860`）。

**关键源码**（`tools/approval.py:743-787`）：
```python
def _smart_approve(command: str, description: str) -> str:
    try:
        from agent.auxiliary_client import call_llm
        prompt = f"""You are a security reviewer for an AI coding agent. ...
Command: {command}
Flagged reason: {description}
Assess the ACTUAL risk ...
Rules:
- APPROVE if the command is clearly safe ...
- DENY if the command could genuinely damage the system ...
- ESCALATE if you're uncertain
Respond with exactly one word: APPROVE, DENY, or ESCALATE"""
        response = call_llm(task="approval", messages=[...],
                            temperature=0, max_tokens=16)
        answer = (response.choices[0].message.content or "").strip().upper()
        # ① 三档而非二档 — 不确定就升级到人，绝不让 aux LLM 强行决策
        if "APPROVE" in answer:   return "approve"
        elif "DENY" in answer:    return "deny"
        else:                     return "escalate"
    except Exception as e:
        # ② LLM 失败 fail-safe 升级到人，绝不静默放过
        logger.debug("Smart approvals: LLM call failed (%s), escalating", e)
        return "escalate"
```

值得看的点：①  `temperature=0, max_tokens=16` 把 aux LLM 当成 classifier 用而非生成器；② 任何不确定都"escalate to human"，避免把责任全压给 aux LLM；③ APPROVE 后还要 `approve_session(session_key, key)`（`approval.py:1023-1024`），所以 LLM 通过的命令在本会话内不会再次打扰用户。

### 机制 E：tool guardrails 的"无进展"检测

**作用**：检测 LLM 是否在死循环——同一参数反复失败 / 幂等工具反复返回同一结果。

**设计意图**：LLM 模式上倾向"再试一次"。如果是 `terminal` 这种带副作用的，"再试一次"可能就是浪费 token；如果是 `read_file` 这种只读，反复读同一文件只是把上下文塞满。护栏从两个维度拦：副作用类（mutating）只看"失败重试"；只读类（idempotent）多看"返回相同结果"。

**关键源码**（`agent/tool_guardrails.py:354-373`）：
```python
result_hash = _result_hash(result)
previous = self._no_progress.get(signature)
repeat_count = 1
if previous is not None and previous[0] == result_hash:
    repeat_count = previous[1] + 1
self._no_progress[signature] = (result_hash, repeat_count)

# ① 只警告、不阻断 — 第一道防线总是温和提示
if self.config.warnings_enabled and repeat_count >= self.config.no_progress_warn_after:
    return ToolGuardrailDecision(
        action="warn",
        code="idempotent_no_progress_warning",
        message=(
            f"{tool_name} returned the same result {repeat_count} times. "
            "Use the result already provided or change the query instead of "
            "repeating it unchanged."
        ),
        ...
    )
```

值得看的点：① 用 `(args_signature, result_hash)` 做"无进展"判断比单看 args 重复更精准——`read_file` 同 args 不同 result 是用户改了文件，依然算进展；② warning 是把文字直接拼进 tool result（`run_agent.py:9622-9623` 通过 `append_toolguard_guidance`），让 LLM 在下一轮看到这段提示——这比单独发一条 system message 更有效，因为 LLM 看 tool result 时正在判断"接下来做什么"。

### 机制 F：clarify — 反向验证用户意图

**作用**：让 LLM 在不确定时主动问用户，而不是猜。

**设计意图**：传统验证是"系统验证 LLM"，clarify 是"LLM 验证用户"。当任务有"有意义的取舍"时（比如改架构、删数据），让 LLM 先说出选项，让用户拍板。这避免了 LLM 沿着错误方向走出去几百行代码后被打回来。

**关键源码**（`tools/clarify_tool.py:96-103`）：
```python
"Use this tool when:\n"
"- The task is ambiguous and you need the user to choose an approach\n"
"- You want post-task feedback ('How did that work out?')\n"
"- You want to offer to save a skill or update memory\n"
"- A decision has meaningful trade-offs the user should weigh in on\n\n"
# ① 显式劝退 — 危险命令的 yes/no 由 terminal 自己处理，clarify 不要重复
"Do NOT use this tool for simple yes/no confirmation of dangerous "
"commands (the terminal tool handles that). Prefer making a reasonable "
"default choice yourself when the decision is low-stakes."
```

值得看的点：description 里既劝进（"什么时候要用"）又劝退（"什么时候不要用"）。这种"in-prompt 政策"是约束 LLM 行为最便宜的手段——比写代码做后置验证简单一个数量级。

### 机制 G：网关阻塞审批 + 心跳，避免 watchdog 误杀

**作用**：网关模式下，agent 线程要等用户点 /approve 或 /deny，等待期间要持续心跳让网关知道"agent 活着但在等用户"。

**设计意图**：如果用 `event.wait(timeout=300)` 一次性阻塞，网关的 `agent.gateway_timeout`（默认 1800s）watchdog 看不到任何 activity，可能在用户尚未响应时就把 agent kill 掉。要么把 watchdog 调大（用户不响应就一直等），要么主动心跳（更精准）。Hermes 选了后者。

**关键源码**（`tools/approval.py:1121-1138`）：
```python
_now = time.monotonic()
_deadline = _now + max(timeout, 0)
_activity_state = {"last_touch": _now, "start": _now}
resolved = False
while True:
    _remaining = _deadline - time.monotonic()
    if _remaining <= 0:
        break
    # ① 1s 切片 — event.set() 立即唤醒, 切片只控心跳频率
    if entry.event.wait(timeout=min(1.0, _remaining)):
        resolved = True
        break
    if touch_activity_if_due is not None:
        # ② 同一函数在 _wait_for_process 也用, 节奏统一
        touch_activity_if_due(
            _activity_state, "waiting for user approval"
        )
```

值得看的点：① 1s 切片对响应延迟没有任何影响（`event.set` 立刻唤醒），只用于驱动心跳——这是"主循环驱动副作用"的经典写法；② 心跳描述写明 "waiting for user approval"，这条信息会被网关日志/UI 利用，让用户知道"系统不是卡了"。

---

## 5. 与其他维度的交互

```
[验证循环] --(干净的工具 schema)--> [工具系统]
[验证循环] --(允许/阻断的指令)--> [编排循环]
[验证循环] --(synthetic tool result)--> [上下文管理]
[验证循环] <--(命令 + env_type)--- [工具系统/terminal]
[验证循环] <--(失败/成功标志)--- [错误处理]
[验证循环] <--(session_key 隔离审批)--- [状态管理]
[验证循环] <--(aux LLM 调用)--- [Prompt构建/auxiliary_client]
[验证循环] <--(plugin pre_tool_call hook)--- [子Agent编排/plugins]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|-----------|
| 输出到 | 工具系统 | sanitize 后的 schema 列表 | `model_tools.py:480` `sanitize_tool_schemas` 返回 `filtered_tools` |
| 输出到 | 编排循环 | block 决策 → 阻止 tool 执行 | `run_agent.py:9858-9861` `before_call` → `_guardrail_block_result` 写入 `block_result` |
| 输出到 | 编排循环 | halt 决策 → 强制结束 turn | `run_agent.py:13742-13750` 检查 `_tool_guardrail_halt_decision` |
| 输出到 | 上下文管理 | guardrail synthetic result | `tool_guardrails.py:383-391` `toolguard_synthetic_result` 写入 `role=tool` content |
| 输出到 | 上下文管理 | warning 文本拼入 tool result | `tool_guardrails.py:394-403` `append_toolguard_guidance` |
| 输出到 | 状态管理 | 持久化 session/permanent allowlist | `approval.py:560-568` `save_permanent_allowlist` → `command_allowlist` 配置项 |
| 依赖 | 工具系统 | terminal 命令字符串 + env_type | `tools/terminal_tool.py:1831` `_check_all_guards(command, env_type)` |
| 依赖 | 错误处理 | 工具失败标志 | `tool_guardrails.py:188-218` `classify_tool_failure`, 与 `agent.display._detect_tool_failure` 行为对齐 |
| 依赖 | 状态管理 | session_key 用于审批隔离 | `approval.py:62-84` `_approval_session_key` contextvar + `get_session_env` |
| 依赖 | Prompt构建 | aux LLM 用于 smart approval | `approval.py:769-774` `call_llm(task="approval", ...)` |
| 依赖 | 子Agent编排 | plugin 钩子 pre_tool_call_block / pre_approval_request | `run_agent.py:9848-9856`、`approval.py:36-58` `_fire_approval_hook` |
| 反向触发 | LLM ↔ 用户 | clarify 让 LLM 主动问用户 | `tools/clarify_tool.py:64` `user_response = callback(question, choices)` |
| 反向触发 | 网关 | 阻塞 agent 线程等待 /approve | `approval.py:1067-1148` `_ApprovalEntry.event.wait` + 1s 切片心跳 |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"LLM 后端的 schema 接收能力是个公约数集合"**：`schema_sanitizer` 假设最差后端（llama.cpp）能吃的形态，所有后端都能吃。这意味着 sanitize 永远是"丢信息或保信息不变"，不会"加新约束"。
2. **"用户能区分 once/session/always 的语义"**：审批 UI 给的不是 yes/no，而是三档持久化粒度。代码里一旦 always，就直接 `save_permanent_allowlist` 落到 config。这隐含假设用户理解"我现在批的是个 pattern 而不是这一条命令"——文档没怎么解释这点。
3. **"危险命令的正则不会有命中不到的变形"**：HARDLINE 用 regex 匹配，依赖 `_normalize_command_for_detection` 把已知 obfuscation 干掉。但理论上 base64-decode + eval 这类构造可以绕（`echo cm0gLXJmIC8= | base64 -d | bash`）——代码靠 `pipe remote content to shell` 这条 DANGEROUS 模式间接接住，但这是"防御纵深"而非完美防御。
4. **"aux LLM 仲裁比正则更准"**：smart approval 假设 aux LLM 对"这个命令实际危险吗"的判断比正则更准。这在大多数情况成立，但 aux LLM 也是 LLM，也可能被命令里嵌入的 prompt-injection 操纵——代码里没有看到对 aux LLM 输入的"中和"处理。

### 6.2 这个设计的代价/风险

1. **DANGEROUS 模式列表的维护成本**：47 条 regex 各覆盖一类风险，新增/修改都要测试并附 description。`approval.py:226-292` 列表已经很长，每加一条都增加状态管理（`_PATTERN_KEY_ALIASES` 还要做 legacy key 兼容）。
2. **schema sanitizer 是有损的**：折叠 nullable union 后 LLM 不再知道这个字段可以传 null（虽然 nullable hint 留着但不在 schema 里）。`type: [X, "null"]` 折叠为 `X` 时，nullable 信息也丢了。这换来了通用性，但偶尔会让 LLM 漏掉"该传 null"的边界情况。
3. **smart approval 多一次 LLM 调用**：每个被标记危险的命令多花一次 aux LLM 往返。如果 agent 在做大量 shell 工作，延迟会累积。`approval.py:773-774` 用 `temperature=0, max_tokens=16` 把成本压到最低，但仍然不为零。
4. **guardrail 的"幂等工具白名单"是手工维护的**：`tool_guardrails.py:19-38` 写死了 `IDEMPOTENT_TOOL_NAMES`（read_file / search_files / web_search 等）。新工具上线时要记得更新。MCP 动态加载的工具默认进 mutating 那一档（`tool_guardrails.py:377-380`）——保守但可能误伤。
5. **网关审批的 5 分钟硬超时**：`approval.py:1110-1114` 默认 `gateway_timeout: 300`。用户离开座位 6 分钟回来发现 agent 拒了——这是显式取舍（防止僵尸等待），但用户体验上有突兀感。

### 6.3 如果要重新设计，可能会改变什么

- **HARDLINE 写在配置里而不是代码里**：当前 `HARDLINE_PATTERNS` 在源码里，调整需要发版本。可以改成"代码内置 + 配置追加"，让 ops 能在 incident 后立刻加规则而不必等 release。
- **smart approval 与 manual approval 合一**：当前 `mode=smart` 时，aux LLM verdict APPROVE 就直接放过，DENY 就直接拒，ESCALATE 才问人。可以改成"始终问人，但把 aux LLM 的判断作为预填默认值"——既保留人的最终决策权，也利用了 LLM 的判断减少认知负担。
- **schema sanitizer 应该有"诊断模式"**：现在用 logger.debug 输出修改了什么；可以加一个 dry-run 模式，让 MCP 工具开发者能直接看到自己的 schema 被改成了什么，从源头修。
- **guardrail 的 result hash 应当对部分内容做归一化**：`_result_hash` 直接 hash JSON 文本，`{timestamp: 123}` 和 `{timestamp: 124}` 会被当成"有进展"。对于 `read_file` 这种内容稳定但元数据浮动的工具，会漏检无进展循环。
- **统一审批流程的 timeout 配置**：CLI 60s（`callbacks.py:204`）、gateway 300s（`approval.py:1110`）、clarify 120s（`callbacks.py:26`）三种 timeout 散落在不同地方，没有顶层一致性。

### 6.4 对自己设计 Agent 系统的启示

**最关键的一句话**：把 "validate LLM" 和 "validate user" 看作同一个验证循环的两端——前者用代码 (schema sanitizer / guardrails / approval)，后者用 LLM 决策的 tool (clarify)；并且**所有放行开关之上要留一个绝对底线（HARDLINE）**，这是用户敢开 yolo 的前提。

具体可借鉴：① 用"宽进严出"的 sanitizer 隔离工具生态和后端差异；② 危险操作用三档（once/session/always）而非二档审批，匹配人的真实心智；③ guardrail 默认只 warn，把 hard-stop 留给用户显式开启，避免误伤幂等读取；④ 审批阻塞时主动心跳，避免 watchdog 误杀——所有"等用户"的代码都应该想到这点；⑤ smart approval 三档（approve/deny/escalate）+ 任何不确定都升级到人，避免把责任全压到 aux LLM 身上。
