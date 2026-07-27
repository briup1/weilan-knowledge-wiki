# 维度 09 — 安全防护（Security）

> 源码基线：`tools/approval.py`、`tools/tirith_security.py`、`tools/path_security.py`、`tools/url_safety.py`、`agent/redact.py`、`agent/tool_guardrails.py`、`tools/skills_guard.py`

---

## 1. 一句话定位

Hermes Agent 的安全防护是一套**「分层纵深 + 多面协同」**的防御体系：从命令执行前的双层模式匹配（HARDLINE/DANGEROUS）与外部二进制扫描（tirith），到运行时 SSRF 拦截、路径穿越阻断、工具调用循环熔断，再到日志与输出中的敏感信息脱敏，以及外部 Skill 的静态威胁扫描——每一层都遵循「fail-closed」原则，且各层之间通过统一的审批状态机串联，确保没有任何单点绕过能穿透整套防线。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

基于代码可反推出以下具体故障：

1. **LLM 被诱导执行破坏性命令**。Agent 的 `terminal` 工具直接暴露 shell 执行能力。如果没有命令检测，`rm -rf /`、`mkfs`、`dd if=/dev/zero of=/dev/sda` 等命令会在用户无感知的情况下执行，导致不可逆数据丢失。`tools/approval.py:156-178` 的 HARDLINE_PATTERNS 就是为此而设——这些命令「没有恢复路径」。

2. **Unicode 全角字符绕过检测**。攻击者可在命令中嵌入全角拉丁字母（如 `ｒｍ` 替代 `rm`）或 null bytes 来绕过简单的字符串匹配。`_normalize_command_for_detection` 中如果没有 `unicodedata.normalize('NFKC')` 和 `strip_ansi`（`tools/approval.py:329-344`），正则检测形同虚设。

3. **SSRF 窃取云实例凭证**。Agent 的 `browser`、`web_search`、`web_extract` 等工具会发起 HTTP 请求。如果没有 URL 安全检查，恶意 prompt 可诱导 Agent 访问 `http://169.254.169.254/latest/meta-data/iam/security-credentials/` 获取 AWS IAM 临时凭证。`tools/url_safety.py:48-54` 的 `_ALWAYS_BLOCKED_IPS` 明确把云元数据端点列为「永不合法」的目标。

4. **符号链接绕过路径限制**。Skill 管理工具允许读写文件。如果没有 `Path.resolve()` 跟进符号链接，攻击者可用 `skill_dir/../../etc/passwd` 穿越出允许目录。`tools/path_security.py:28-33` 的 `validate_within_dir` 用 `resolved.relative_to(root_resolved)` 来阻断这种绕过。

5. **API Key 泄露到日志文件**。Agent 执行命令的输出、HTTP 响应、LLM 返回的内容中可能包含 `sk-xxx`、`ghp_xxx` 等凭证。如果没有脱敏，这些会永久写入 `~/.hermes/logs/` 的轮转日志中。`agent/redact.py:185-187` 把 30+ 种已知前缀编译成一个正则 alternation，在日志格式化阶段自动替换。

6. **恶意 Skill 被静默安装**。Skill 可从外部 registry 下载执行。如果没有静态扫描，一个包含 `curl ... | bash` 或 `os.system('rm -rf /')` 的 Skill 会被直接加载到 Agent 的 toolset 中。`tools/skills_guard.py:86-488` 的 100+ 条 THREAT_PATTERNS 覆盖了数据外泄、提示注入、持久化、反向 shell、供应链攻击等 12 个类别。

7. **Agent 陷入工具调用死循环**。LLM 可能在同一轮中反复调用同一个失败工具（如 `read_file` 读一个不存在的路径）。如果没有 guardrail，这会浪费 token、阻塞执行，甚至触发 provider 的速率限制。`agent/tool_guardrails.py:221-281` 的 `before_call` 会在重复失败达到阈值时直接 `block`。

### 2.2 具体触发条件（代码中的判断逻辑）

- **HARDLINE 触发**：`terminal_tool.py` 在命令执行前调用 `check_all_command_guards`（`tools/terminal_tool.py:317-318`），后者先走 `detect_hardline_command`（`tools/approval.py:193-203`）——任何匹配 12 条硬线模式的命令直接返回 `approved: False` + `hardline: True`，不可绕过。
- **DANGEROUS 触发**：同一路径中，若未命中 HARDLINE，则进入 `detect_dangerous_command`（`tools/approval.py:347-358`）匹配 47 条危险模式。命中后根据审批状态决定是否阻塞或提示。
- **tirith 触发**：`check_all_command_guards` 在检测完模式后，还会调用 `check_command_security`（`tools/tirith_security.py:615-691`）运行外部 tirith 二进制扫描，exit code 0/1/2 分别对应 allow/block/warn。
- **URL 安全检查触发**：`gateway/platforms/base.py:572-573`、`slack.py:1368` 等平台适配器在发送/下载媒体前调用 `is_safe_url`，DNS 解析到私有 IP 或云元数据 IP 时返回 False，请求被阻断。
- **路径安全检查触发**：`tools/skill_manager_tool.py:303-331` 在 Skill 文件读写前调用 `has_traversal_component` 做快速过滤，再调用 `validate_within_dir` 做 `resolve()` 后的严格校验。
- **脱敏触发**：`hermes_logging.py:211-243` 在创建 `RotatingFileHandler` 时统一设置 `RedactingFormatter`，所有日志消息在写入磁盘前经过 `redact_sensitive_text`（`agent/redact.py:311-392`）。
- **工具循环 guardrail 触发**：`run_agent.py:9858` 和 `10208` 在每次工具调用前调用 `ToolCallGuardrailController.before_call()`，若同一签名失败次数超过 `exact_failure_block_after`（默认 5）则直接 block。
- **Skill 扫描触发**：`cli.py:2016-2021` 在 Skill 安装流程中调用 `scan_skill`（`tools/skills_guard.py:599-643`），根据 trust level 和 verdict 决定是否允许安装。

---

## 3. 核心设计思路

### 3.1 抽象模型（伪代码）

```python
# 三层防御模型：检测层 → 决策层 → 执行层

def execute_command(cmd, env_type):
    # Layer 1: 检测层（多源并行检测）
    hardline = detect_hardline(cmd)          # 绝对禁止，不可绕过
    dangerous = detect_dangerous(cmd)        # 模式匹配
    tirith = check_command_security(cmd)     # 外部二进制扫描
    
    # Layer 2: 决策层（统一审批状态机）
    warnings = collect_warnings(hardline, dangerous, tirith)
    if hardline:
        return BLOCKED(permanent=True)       # 硬线：无审批入口
    if yolo_enabled or mode == "off":
        return APPROVED                      # YOLO 绕过 DANGEROUS，不绕过 HARDLINE
    if not warnings:
        return APPROVED
    
    # 审批三档：once / session / always
    choice = prompt_or_gateway_approve(warnings)
    persist_approval(choice, warnings)       # 写入会话或永久白名单
    return APPROVED if choice != "deny" else BLOCKED

# 运行时辅助防御（与命令审批并行）
def fetch_url(url):
    if not is_safe_url(url):                 # SSRF 防护
        return BLOCKED
    return http_client.get(url)

def read_skill_file(path, skill_dir):
    if has_traversal_component(path):        # 快速过滤
        return BLOCKED
    if validate_within_dir(path, skill_dir): # 严格 resolve 校验
        return BLOCKED
    return file_read(path)

def log_message(text):
    safe = redact_sensitive_text(text)       # 日志脱敏
    write_to_disk(safe)
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **双层命令检测** | HARDLINE（12 条，绝对禁止）+ DANGEROUS（47 条，可审批） | 单层统一 blocklist | `tools/approval.py:119-136` 的注释明确说明：YOLO 是「信任 agent 处理你的文件和服务」，不是「信任它擦除磁盘」。HARDLINE 是 yolo 之下的地板，只有「无恢复路径」的命令（rm -rf /、mkfs、fork bomb、shutdown）才进入此列表。 |
| **命令归一化前置** | strip ANSI + strip null bytes + NFKC Unicode normalization | 原始字符串直接匹配 | `tools/approval.py:329-344` 的 `_normalize_command_for_detection` 明确防范「全角/半角绕过」和 ANSI 注入。若不做此步，`ｒｍ -ｒｆ /` 可轻松绕过正则。 |
| **审批状态三档** | once（单次）/ session（会话）/ always（永久写入 config.yaml） | 仅支持单次或永久 | `tools/approval.py:575-687` 的 `prompt_dangerous_approval` 提供三档选择。session 级避免重复打扰，always 级通过 `save_permanent_allowlist` 持久化到 `command_allowlist`（`tools/approval.py:560-568`），实现跨会话记忆。 |
| **YOLO 模式** | 全局环境变量 `HERMES_YOLO_MODE` + 会话级 `_session_yolo` set | 完全禁止绕过 | `tools/approval.py:820-821` 允许用户通过 `--yolo` 或 `/yolo` 一次性信任当前会话的所有 DANGEROUS 命令，但 HARDLINE 仍不可绕过。这平衡了「高级用户效率」与「底线安全」。 |
| **网关阻塞审批** | `threading.Event` + FIFO queue（`_ApprovalEntry`） | 轮询或异步 callback | `tools/approval.py:380-445` 中，每个并发请求获得独立的 `_ApprovalEntry`，通过 `threading.Event.wait()` 阻塞直到用户通过 `/approve` 或 `/approve all` 响应。这支持多线程并发（并行子 agent、execute_code RPC）而不丢失顺序。 |
| **tirith 外部二进制** | 独立 Rust 二进制，子进程调用，exit code 定 verdict | 纯 Python 实现 | `tools/tirith_security.py:615-691` 把复杂的内容级威胁检测（同形 URL、终端注入等）外包给专用二进制，避免 Python 正则的维护负担。自动下载 + SHA-256/cosign 校验（`tools/tirith_security.py:282-386`）保证供应链安全。 |
| **fail-closed 默认** | DNS 失败、解析异常、tirith 超时均返回 blocked | fail-open（异常时放行） | `tools/url_safety.py:282-286` 在 DNS 解析失败时返回 False；`tools/tirith_security.py:648-658` 在 tirith spawn 失败时根据 `fail_open` 配置决定（默认 `tirith_fail_open: True`，但 URL 安全没有此开关，始终 fail-closed）。 |
| **日志脱敏在 Formatter 层** | `RedactingFormatter` 继承 `logging.Formatter` | 在每个 log 调用点手动脱敏 | `agent/redact.py:395-403` 把脱敏下沉到 logging 基础设施层，确保「零遗漏」——任何通过标准 logging 路径的输出都会被处理，包括第三方库的日志。 |
| **Skill 信任分级** | builtin（不扫描）/ trusted（openai/anthropics，caution 可过）/ community（任何发现即 block） | 统一扫描标准 | `tools/skills_guard.py:41-51` 的 `INSTALL_POLICY` 矩阵体现了「来源决定容忍度」——官方来源允许 caution 级别通过，社区来源零容忍。 |

### 3.3 数据流/控制流

```
[用户输入 / LLM 生成命令]
        │
        ▼
┌─────────────────────────────────────────┐
│  Layer 1: 命令归一化                     │  tools/approval.py:329-344
│  (strip ANSI, null bytes, NFKC)         │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Layer 2: HARDLINE 检测                  │  tools/approval.py:193-203
│  → 命中 → BLOCKED (不可绕过)             │
└─────────────────────────────────────────┘
        │ 未命中
        ▼
┌─────────────────────────────────────────┐
│  Layer 3: YOLO / mode=off 检查           │  tools/approval.py:820-821, 945
│  → 启用 → APPROVED (跳过 DANGEROUS)      │
└─────────────────────────────────────────┘
        │ 未启用
        ▼
┌─────────────────────────────────────────┐
│  Layer 4: DANGEROUS 模式匹配 (47 条)     │  tools/approval.py:347-358
│  Layer 5: tirith 二进制扫描              │  tools/tirith_security.py:615-691
│  → 无命中 → APPROVED                     │
└─────────────────────────────────────────┘
        │ 有命中
        ▼
┌─────────────────────────────────────────┐
│  Layer 6: 审批状态查询                   │  tools/approval.py:511-522
│  (session_approved / permanent_approved) │
│  → 已批准 → APPROVED                     │
└─────────────────────────────────────────┘
        │ 未批准
        ▼
┌─────────────────────────────────────────┐
│  Layer 7: 交互式 / 网关审批              │  tools/approval.py:575-687 (CLI)
│  (CLI input() / gateway Event queue)     │  tools/approval.py:1052-1207 (gateway)
│  → once/session/always/deny              │
└─────────────────────────────────────────┘
        │
   ┌────┴────┐
   ▼         ▼
APPROVED  BLOCKED
   │         │
   ▼         ▼
[执行命令]  [返回错误给 LLM]

并行防御（独立触发）：
[URL 请求] → is_safe_url() → DNS 解析 → IP 分类检查 → 允许/阻断  (tools/url_safety.py:251-327)
[文件读写] → has_traversal_component() → validate_within_dir() → 允许/阻断  (tools/path_security.py:15-44)
[日志输出] → RedactingFormatter.format() → redact_sensitive_text() → 写入磁盘  (agent/redact.py:395-403)
[工具调用] → ToolCallGuardrailController.before_call/after_call() → warn/block/halt  (agent/tool_guardrails.py:221-375)
[Skill 安装] → scan_skill() → should_allow_install() → 允许/阻断/询问  (tools/skills_guard.py:599-680)
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：双层命令检测（HARDLINE + DANGEROUS）

**作用**：在命令执行前识别 catastrophic（不可恢复）和 dangerous（有风险但可审批）两类命令。

**设计意图**：HARDLINE 是「安全地板」——即使管理员开启了 YOLO 或 approvals.mode=off，这些命令仍然被禁止。DANGEROUS 是「可协商边界」——用户可以根据上下文选择批准。两层分离避免了「一刀切」导致合法开发操作（如 `git reset --hard`）被过度拦截，同时确保最危险的命令绝无例外。

**关键源码**（`tools/approval.py:156-178, 347-358`）：
```python
# HARDLINE_PATTERNS: 12 条绝对禁止模式（节选）
HARDLINE_PATTERNS = [
    (r'\brm\s+(-[^\s]*\s+)*(/|/\*|/ \*)(\s|$)', "recursive delete of root filesystem"),
    (r'\bmkfs(\.[a-z0-9]+)?\b', "format filesystem (mkfs)"),
    (r'\bdd\b[^\n]*\bof=/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*', "dd to raw block device"),
    (r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:', "fork bomb"),
    (_CMDPOS + r'(shutdown|reboot|halt|poweroff)\b', "system shutdown/reboot"),
]

# detect_dangerous_command: 47 条可审批模式匹配
def detect_dangerous_command(command: str) -> tuple:
    command_lower = _normalize_command_for_detection(command).lower()
    for pattern_re, description in DANGEROUS_PATTERNS_COMPILED:
        if pattern_re.search(command_lower):
            pattern_key = description
            return (True, pattern_key, description)
    return (False, None, None)
```

### 机制 B：命令归一化防绕过

**作用**：在正则匹配前消除常见的 obfuscation 技术（Unicode 全角字符、ANSI 转义序列、null bytes）。

**设计意图**：如果不做归一化，攻击者可用 `\x00ｒｍ\x00 -ｒｆ /` 绕过简单的字符串匹配。NFKC 把全角拉丁字母映射回 ASCII，strip_ansi 消除颜色代码注入，null byte 消除则防止「字符串截断」类绕过。

**关键源码**（`tools/approval.py:329-344`）：
```python
def _normalize_command_for_detection(command: str) -> str:
    from tools.ansi_strip import strip_ansi
    command = strip_ansi(command)           # ① 消除 ANSI 转义序列
    command = command.replace('\x00', '')   # ② 消除 null bytes
    command = unicodedata.normalize('NFKC', command)  # ③ 全角→半角归一化
    return command
```

### 机制 C：线程安全的会话级审批状态

**作用**：在多线程并发环境（gateway 并行子 agent、execute_code RPC）中维护每个会话的审批状态，避免 race condition。

**设计意图**：使用 `threading.Lock()` 保护所有状态变更操作（`_session_approved`、`_session_yolo`、`_permanent_approved`），确保并发审批不会导致状态不一致。`_pending` 存储当前待审批请求，`_gateway_queues` 用 FIFO 队列保证多线程阻塞时的顺序性。

**关键源码**（`tools/approval.py:365-370, 380-445`）：
```python
_lock = threading.Lock()
_pending: dict[str, dict] = {}
_session_approved: dict[str, set] = {}
_session_yolo: set[str] = set()
_permanent_approved: set = set()

class _ApprovalEntry:
    __slots__ = ("event", "data", "result")
    def __init__(self, data: dict):
        self.event = threading.Event()       # 每个请求独立的事件对象
        self.data = data
        self.result: Optional[str] = None

_gateway_queues: dict[str, list] = {}      # session_key → [_ApprovalEntry, …]

def resolve_gateway_approval(session_key: str, choice: str, resolve_all: bool = False) -> int:
    with _lock:
        queue = _gateway_queues.get(session_key)
        if not queue:
            return 0
        targets = list(queue) if resolve_all else [queue.pop(0)]
    for entry in targets:
        entry.result = choice
        entry.event.set()                    # 唤醒阻塞的 agent 线程
    return len(targets)
```

### 机制 D：网关阻塞审批（同步线程 → 异步用户交互的桥接）

**作用**：在 gateway 模式下，agent 执行线程是同步的，但用户交互是异步的（通过 WebSocket/HTTP）。用 `threading.Event` 实现「同步线程阻塞等待异步响应」。

**设计意图**：如果不阻塞，agent 会在用户还没看到审批请求时就继续执行或报错。`1s poll slice`（`tools/approval.py:1132`）既保证了响应及时性，又通过 `touch_activity_if_due` 防止 gateway 的「不活跃看门狗」在审批等待期间杀死 agent。

**关键源码**（`tools/approval.py:1125-1138`）：
```python
_now = time.monotonic()
_deadline = _now + max(timeout, 0)
_activity_state = {"last_touch": _now, "start": _now}
while True:
    _remaining = _deadline - time.monotonic()
    if _remaining <= 0:
        break
    if entry.event.wait(timeout=min(1.0, _remaining)):  # 1s 轮询，兼顾响应与心跳
        resolved = True
        break
    if touch_activity_if_due is not None:
        touch_activity_if_due(_activity_state, "waiting for user approval")
```

### 机制 E：tirith 外部安全扫描与自动安装

**作用**：用专用二进制对命令做内容级深度分析（同形 URL、管道注入等），并支持自动下载安装。

**设计意图**：把复杂且快速演化的威胁检测逻辑外包给独立项目（Rust 二进制），避免 Python 代码库膨胀。自动安装时通过 SHA-256 + cosign 双重校验保证供应链安全，失败时写入磁盘标记 24h 内不再重试。

**关键源码**（`tools/tirith_security.py:641-658, 346-347`）：
```python
def check_command_security(command: str) -> dict:
    result = subprocess.run(
        [tirith_path, "check", "--json", "--non-interactive", "--shell", "posix", "--", command],
        capture_output=True, text=True, timeout=timeout,
    )
    exit_code = result.returncode
    if exit_code == 0: action = "allow"
    elif exit_code == 1: action = "block"
    elif exit_code == 2: action = "warn"
    # ... JSON 解析丰富 findings，但 verdict 以 exit code 为准

def _verify_checksum(archive_path: str, checksums_path: str, archive_name: str) -> bool:
    # SHA-256 校验 + cosign 供应链验证（若可用）
```

### 机制 F：URL 安全与 SSRF 防护

**作用**：阻止 Agent 访问私有网络地址和云元数据端点，防止 SSRF 攻击。

**设计意图**：即使 `security.allow_private_urls` 开启（用于 VPN/代理环境），云元数据端点（169.254.169.254、metadata.google.internal）仍被绝对禁止——这些是「永不合法的 agent 目标」。DNS 解析失败时 fail-closed，避免「解析不到就放行」的漏洞。

**关键源码**（`tools/url_safety.py:251-327`）：
```python
def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").strip().lower().rstrip(".")
    if hostname in _BLOCKED_HOSTNAMES:       # ① 永远禁止的 hostname
        return False
    allow_all_private = _global_allow_private_urls()
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:                  # ② DNS 失败 → fail-closed
        return False
    for family, _, _, _, sockaddr in addr_info:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip in _ALWAYS_BLOCKED_IPS:        # ③ 云元数据 IP 永远禁止
            return False
        if not allow_all_private and _is_blocked_ip(ip):
            return False
    return True
```

### 机制 G：路径安全与目录穿越防护

**作用**：确保 Skill/工具的文件操作不会通过 `..` 或符号链接逃出允许目录。

**设计意图**：`has_traversal_component` 做快速字符串检查（O(1) 级别），提前拒绝明显的攻击；`validate_within_dir` 用 `Path.resolve()` 跟进符号链接后用 `relative_to` 做严格 containment 检查——这是「防符号链接绕过」的关键。

**关键源码**（`tools/path_security.py:15-44`）：
```python
def validate_within_dir(path: Path, root: Path) -> Optional[str]:
    try:
        resolved = path.resolve()            # ① 跟进符号链接、消除 .. 组件
        root_resolved = root.resolve()
        resolved.relative_to(root_resolved)  # ② 严格 containment 检查
    except (ValueError, OSError) as exc:
        return f"Path escapes allowed directory: {exc}"
    return None

def has_traversal_component(path_str: str) -> bool:
    parts = Path(path_str).parts
    return ".." in parts                     # ③ 快速预过滤
```

### 机制 H：敏感信息脱敏（Redaction）

**作用**：在日志、命令输出、HTTP 响应中自动识别并掩码 API Key、Token、密码、JWT、私钥、数据库连接串等敏感数据。

**设计意图**：脱敏在 logging Formatter 层统一处理，确保「零遗漏」；同时支持 `code_file=True` 模式避免在源代码中误伤常量定义。`_REDACT_ENABLED` 在导入时快照环境变量，防止运行时 LLM 生成的 `export HERMES_REDACT_SECRETS=false` 绕过。

**关键源码**（`agent/redact.py:60-67, 311-392`）：
```python
# 导入时快照，防止运行时 env 注入绕过
_REDACT_ENABLED = os.getenv("HERMES_REDACT_SECRETS", "true").lower() in ("1", "true", "yes", "on")

_PREFIX_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(" + "|".join(_PREFIX_PATTERNS) + r")(?![A-Za-z0-9_-])"
)

def redact_sensitive_text(text: str, *, force: bool = False, code_file: bool = False) -> str:
    if not (force or _REDACT_ENABLED):
        return text
    text = _PREFIX_RE.sub(lambda m: _mask_token(m.group(1)), text)   # ① 已知前缀
    if not code_file:
        text = _ENV_ASSIGN_RE.sub(_redact_env, text)                  # ② ENV 赋值
        text = _JSON_FIELD_RE.sub(_redact_json, text)                 # ③ JSON 字段
    text = _AUTH_HEADER_RE.sub(lambda m: m.group(1) + _mask_token(m.group(2)), text)
    text = _PRIVATE_KEY_RE.sub("[REDACTED PRIVATE KEY]", text)       # ④ 私钥块
    text = _DB_CONNSTR_RE.sub(lambda m: f"{m.group(1)}***{m.group(3)}", text)
    text = _JWT_RE.sub(lambda m: _mask_token(m.group(0)), text)      # ⑤ JWT
    # ... URL query params, form body, Discord mentions, phone numbers
    return text
```

### 机制 I：工具调用循环 Guardrail

**作用**：检测并阻止 Agent 在同一轮对话中反复调用同一个失败工具或无进展的只读工具，防止 token 浪费和死循环。

**设计意图**：区分「幂等工具」（read_file、search_files 等，重复相同参数无意义）和「变异工具」（write_file、terminal 等，可能因副作用而需要重试）。对幂等工具检测「相同结果重复」；对所有工具检测「相同参数重复失败」。默认仅 warn，hard_stop 需显式开启。

**关键源码**（`agent/tool_guardrails.py:238-281, 282-375`）：
```python
class ToolCallGuardrailController:
    def before_call(self, tool_name: str, args: Mapping[str, Any] | None) -> ToolGuardrailDecision:
        signature = ToolCallSignature.from_call(tool_name, _coerce_args(args))
        exact_count = self._exact_failure_counts.get(signature, 0)
        if exact_count >= self.config.exact_failure_block_after:       # ① 相同参数失败 5 次
            return ToolGuardrailDecision(action="block", code="repeated_exact_failure_block", ...)
        if self._is_idempotent(tool_name):
            record = self._no_progress.get(signature)
            if record and record[1] >= self.config.no_progress_block_after:  # ② 只读工具无进展 5 次
                return ToolGuardrailDecision(action="block", code="idempotent_no_progress_block", ...)
        return ToolGuardrailDecision(tool_name=tool_name, signature=signature)

    def after_call(self, tool_name: str, args, result, *, failed: bool | None = None):
        if failed:
            self._exact_failure_counts[signature] = exact_count + 1      # ③ 累计失败计数
            self._same_tool_failure_counts[tool_name] = same_count + 1
        elif self._is_idempotent(tool_name):
            result_hash = _result_hash(result)
            previous = self._no_progress.get(signature)
            if previous and previous[0] == result_hash:
                self._no_progress[signature] = (result_hash, previous[1] + 1)  # ④ 相同结果计数
```

### 机制 J：Skill 静态威胁扫描

**作用**：在 Skill 安装前对其内容进行静态分析，检测数据外泄、提示注入、破坏性操作、持久化、反向 shell、供应链攻击等威胁。

**设计意图**：Skill 是「外部代码」，Agent 会将其加载到 toolset 中执行。如果没有扫描，恶意 Skill 可直接调用 `terminal` 或 `execute_code` 执行任意命令。100+ 条 regex 覆盖 12 个威胁类别，结合「信任分级」策略（builtin/trusted/community）实现差异化管控。

**关键源码**（`tools/skills_guard.py:41-51, 86-488, 646-680`）：
```python
INSTALL_POLICY = {
    "builtin":       ("allow",  "allow",   "allow"),
    "trusted":       ("allow",  "allow",   "block"),
    "community":     ("allow",  "block",   "block"),
    "agent-created": ("allow",  "allow",   "ask"),
}

THREAT_PATTERNS = [
    # 数据外泄
    (r'curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD)', "env_exfil_curl", "critical", "exfiltration", ...),
    # 提示注入
    (r'ignore\s+(?:\w+\s+)*(previous|all|above|prior)\s+instructions', "prompt_injection_ignore", "critical", "injection", ...),
    # 破坏性操作
    (r'\brm\s+-rf\s+/', "destructive_root_rm", "critical", "destructive", ...),
    # 供应链
    (r'curl\s+[^\n]*\|\s*(ba)?sh', "curl_pipe_shell", "critical", "supply_chain", ...),
    # ... 共 100+ 条
]

def should_allow_install(result: ScanResult, force: bool = False) -> Tuple[bool, str]:
    policy = INSTALL_POLICY.get(result.trust_level, INSTALL_POLICY["community"])
    vi = VERDICT_INDEX.get(result.verdict, 2)
    decision = policy[vi]                    # 根据信任级别和 verdict 查矩阵
    if decision == "allow": return True, ...
    if force: return True, ...               # --force 可覆盖
    return False, ...
```

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | **工具系统** | `terminal_tool` 执行前调用 `check_all_command_guards` 做安全审批；`skill_manager_tool` / `skills_tool` 调用 `validate_within_dir` 做路径限制 | `tools/terminal_tool.py:317-318`；`tools/skill_manager_tool.py:303-331` |
| 输出到 | **输出解析** | 工具调用循环 guardrail 在 `before_call`/`after_call` 中生成 warn/block/halt 决策，修改或替换 tool result 后返回给 LLM | `run_agent.py:9858, 10208, 9616-9626` |
| 输出到 | **记忆系统** | `RedactingFormatter` 确保写入日志文件（记忆的一种持久化形式）的敏感信息已被掩码 | `hermes_logging.py:211-243` |
| 输出到 | **网关系统** | 网关平台适配器（Slack/微信/企业微信等）在下载媒体前调用 `is_safe_url`；审批系统通过 `register_gateway_notify`/`resolve_gateway_approval` 与 gateway HTTP handler 交互 | `gateway/platforms/base.py:572-573`；`tools/approval.py:394-445` |
| 输出到 | **Cron 调度** | Cron 执行命令时通过 `HERMES_CRON_SESSION` 环境变量进入特殊审批分支，默认 deny 危险命令 | `tools/approval.py:836-847`；`cron/scheduler.py:774-776` |
| 依赖 | **配置系统** | 审批模式（manual/smart/off）、超时、tirith 路径等从 `config.yaml` 读取；永久白名单持久化到 `command_allowlist` | `tools/approval.py:705-727`；`tools/tirith_security.py:68-87` |
| 依赖 | **LLM 调用** | Smart Approval 模式调用 auxiliary LLM 评估命令风险；工具循环 guardrail 的决策最终通过 prompt 注入反馈给主 LLM | `tools/approval.py:743-787`；`agent/tool_guardrails.py:394-403` |
| 依赖 | **子 Agent 编排** | 子 Agent 的并发工具调用共享父 Agent 的审批会话状态（通过 `contextvars` 的 session_key），确保审批隔离 | `tools/approval.py:30-34, 62-84` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **「用户比 agent 更懂自己的环境」**。YOLO 模式、session/always 审批、allow_private_urls 等开关的存在，说明作者假设高级用户需要灵活度，而默认配置（manual 审批、private URL block）保护的是普通用户。
2. **「正则 + 外部二进制足够覆盖已知威胁」**。HARDLINE/DANGEROUS 用 regex，tirith 用 Rust 二进制，skills_guard 用 regex——作者假设命令级和 Skill 级的威胁是「模式可枚举的」，而非需要动态行为分析。
3. **「网关并发是常态」**。`threading.Event` + FIFO queue + `contextvars` 的设计说明作者假设 gateway 模式下会有多线程并发审批需求，而非简单的单用户 CLI 交互。
4. **「日志是泄露敏感信息的最大风险面」**。把脱敏下沉到 `logging.Formatter` 而非每个调用点，说明作者假设「标准 logging 路径」是主要泄露渠道。

### 6.2 这个设计的代价/风险

1. **正则维护负担**。HARDLINE（12 条）+ DANGEROUS（47 条）+ skills_guard（100+ 条）共 160+ 条正则，任何一条的误报都会直接影响用户体验。例如 `python -c "print('hello')"` 被标记为 "script execution via -c flag"，需要 Smart Approval 或用户手动确认。
2. **tirith 的供应链依赖**。自动下载外部二进制引入了网络依赖和信任假设（GitHub releases、cosign/SHA-256）。如果 GitHub 不可达或 release 被篡改，tirith 扫描失效。`fail_open: True` 的默认配置在 tirith 不可用时放行，虽保证可用性但降低了安全性。
3. **审批状态的生命周期模糊**。`_session_approved` 和 `_session_yolo` 是基于内存的，gateway 进程重启后状态丢失。虽然 `always` 会写入 `config.yaml`，但「session 到底何时结束」没有显式边界（`clear_session` 需要调用方主动触发）。
4. **工具循环 guardrail 的 hard_stop 默认关闭**。`hard_stop_enabled: False`（`agent/tool_guardrails.py:72`）意味着默认只 warn 不 block，Agent 仍可能因忽略警告而继续循环浪费 token。
5. **URL 安全检查的 TOCTOU 问题**。`tools/url_safety.py:16-23` 的注释明确承认：DNS rebinding 攻击无法在前置检查阶段完全防御，需要连接级验证（如 egress proxy）。当前实现是「尽力而为」而非「绝对安全」。

### 6.3 如果要重新设计，可能会改变什么

1. **把 DANGEROUS_PATTERNS 从正则迁移到 AST/语义分析**。当前正则误报率较高（如 `python -c` 的 benign 用例），用 shell 解析器做语义分析可以更精确地区分 `python -c "print(1)"` 和 `python -c "import os; os.system('rm -rf /')"`。
2. **引入「审批会话的显式生命周期管理」**。当前 session 状态是隐式的（靠 `clear_session` 调用），可以设计为「每次 agent run 开始时自动创建，run 结束时自动清理」，避免内存泄漏和状态污染。
3. **tirith 的 fail_open 改为可配置且默认 fail-closed**。对于高安全环境，tirith 不可用时应该 block 而非 allow。当前默认 `tirith_fail_open: True` 是一个可用性优先的妥协。
4. **URL 安全增加连接级验证**。如注释所述，DNS rebinding 需要连接时重新验证目标 IP。可以集成 `httpx` 的 event hook 在每次 redirect 后重新调用 `is_safe_url`（部分平台已这样做，但未统一）。
5. **Skill 扫描增加动态沙箱执行**。当前仅静态 regex 扫描，无法检测运行时才展现的恶意行为（如条件分支、动态 eval）。可以引入受限 Python 解释器做轻量级动态分析。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示：安全防护必须是「分层且各层独立生效」的，而不是「一个大门禁解决所有问题」。** Hermes 的设计展示了如何把「命令检测、外部扫描、URL 拦截、路径限制、日志脱敏、工具循环熔断、Skill 静态分析」编织成一张网——每一层都有自己的触发条件和失败模式，且都遵循 fail-closed。最值得借鉴的是「HARDLINE 地板」概念：无论用户如何配置（YOLO、mode=off），总有一些操作是「绝对不可执行」的，这为系统保留了最后的安全底线。
