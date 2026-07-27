# 维度名：安全防护

## 1. 一句话定位

nanobot 的安全防护是一套"纵深防御"体系：在**网络层**阻断 SSRF 与内网探测，在**文件/Shell 层**通过 `restrict_to_workspace` 限制操作半径，在**渠道层**通过 `allowFrom` 白名单控制谁能触发 Agent。三个层面相互独立、缺一不可。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **没有 SSRF 防护**：`web_fetch` 可被诱导访问 `http://169.254.169.254/latest/meta-data/`（云厂商元数据服务）或 `http://127.0.0.1:18790`（nanobot 自身 Gateway），导致云凭证泄露、内部 API 被遍历。
- **没有文件系统边界**：`write_file("/../../../etc/cron.d/backdoor", "...")` 或 `read_file("~/.ssh/id_rsa")` 可直接读写用户敏感文件；Agent 的自动修复/编辑行为会无差别覆盖工作区外的系统文件。
- **没有渠道白名单**：任何知道 Telegram Bot Token 或 Webhook URL 的人都能向 nanobot 发送指令，相当于把 root shell 暴露在公网。
- **没有 Shell 命令过滤**：`exec("curl -s http://internal.api/admin | sh")` 可绕过网络层校验直接执行内网请求；`rm -rf /` 或 fork bomb 可在数秒内摧毁宿主机。

### 2.2 nanobot 的具体触发条件

| 触发条件 | 代码位置 |
|---------|---------|
| 用户消息通过任意渠道进入系统时，检查 `sender_id` 是否在 `allow_from` 列表中 | `nanobot/channels/base.py:L79-87` |
| `WebFetchTool.execute()` 被调用时，对 URL 做 DNS 解析并校验解析后的 IP | `nanobot/security/network.py:L30-63` |
| `WebFetchTool._fetch_readability()` 收到重定向响应后，二次校验最终 URL | `nanobot/security/network.py:L65-94` |
| `ExecTool.execute()` 被调用时，扫描命令字符串中的危险模式与内网 URL | `nanobot/agent/tools/shell.py:L144-176` |
| `ReadFileTool/WriteFileTool/EditFileTool/ListDirTool` 被调用时，解析路径并检查是否在 `allowed_dir` 之下 | `nanobot/agent/tools/filesystem.py:L10-25` |
| `AgentLoop.__init__()` 根据 `restrict_to_workspace` 配置决定是否为文件工具注入 `allowed_dir` | `nanobot/agent/loop.py:L116-128` |

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────────────────────────────────────────────────┐
│                        渠道准入层                              │
│  BaseChannel.is_allowed(sender_id)                          │
│   ├─ allow_from == []      → deny all (默认)                │
│   ├─ allow_from == ["*"]   → allow all                     │
│   └─ sender_id in allow_from → allow                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        工具执行层                              │
│  ToolRegistry.execute(name, params)                         │
│   ├─ 参数类型转换 (cast_params)                              │
│   ├─ JSON Schema 校验 (validate_params)                      │
│   └─ Tool.execute(**params)                                  │
│        ├─ FilesystemTool → _resolve_path() → allowed_dir    │
│        ├─ ExecTool       → _guard_command() → deny_patterns │
│        └─ WebFetchTool   → _validate_url_safe() → SSRF      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        网络防护层                              │
│  validate_url_target(url)                                   │
│   ├─ scheme ∈ {http, https}                                 │
│   ├─ hostname 可解析                                         │
│   └─ 解析后的 IP ∉ _BLOCKED_NETWORKS                        │
│  validate_resolved_url(url)  ← 重定向后二次校验               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| SSRF 防护放在独立 `security/` 模块 | 网络校验逻辑集中到 `nanobot/security/network.py`，被 `web.py` 和 `shell.py` 共同引用 | 把校验逻辑内嵌在 `WebFetchTool` 内部 | `shell.py:L157-159` 也需要检测命令字符串中的内网 URL（`contains_internal_url`），说明网络防护是**跨工具**的共享能力，不是某个工具的私有逻辑 |
| `restrict_to_workspace` 在 `loop.py` 初始化时注入 | `AgentLoop._register_default_tools()` 根据配置构造带 `allowed_dir` 的工具实例 | 让工具内部自行读取全局配置判断 | 工具类（如 `ReadFileTool`）是**无状态、无配置依赖**的原子能力；如果让工具自己读配置，会引入对 `Config` 的耦合，破坏工具的可测试性和可复用性。在 `loop.py` 注入相当于"依赖注入"，配置由编排层持有、工具只接收运行时参数 |
| `allowFrom` 默认空列表拒绝所有 | `BaseChannel.is_allowed()` 中 `if not allow_list: return False` | 默认空列表允许所有（常见框架的"开发友好"默认值） | `channels/manager.py:L62-66` 在启动时显式检查空列表并抛出 `SystemExit`，强制用户做出显式选择。这是**安全优先于便利**的设计：一个暴露在互联网的 AI Agent 默认开放等于把系统拱手让人 |
| 文件工具使用 `Path.resolve()` + `relative_to()` 做路径逃逸检测 | 先 `resolve()` 再检查是否在 `allowed_dir` 之下 | 简单的字符串前缀匹配 | `filesystem.py:L28-33` 使用 `relative_to()` 捕获符号链接、目录遍历（`../`）等所有路径逃逸手段，比字符串匹配更可靠 |

### 3.3 数据流/控制流

```
用户消息 → 渠道 (Telegram/Discord/...) 
    → BaseChannel._handle_message()
        → BaseChannel.is_allowed(sender_id) ──→ 拒绝则直接丢弃，不进入 Bus
            → 允许则 publish_inbound() → MessageBus
                → AgentLoop.run() → _dispatch()
                    → _process_message() → _run_agent_loop()
                        → LLM 返回 tool_calls
                            → ToolRegistry.execute()
                                ├── FilesystemTool: _resolve_path() → _is_under()
                                ├── ExecTool: _guard_command() → contains_internal_url()
                                └── WebFetchTool: _validate_url_safe() → validate_url_target()
                                    → 实际 HTTP 请求 → 收到重定向
                                        → validate_resolved_url() 二次校验
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：SSRF 防护 —— DNS 解析时拦截内网 IP

**作用**：在发起 HTTP 请求前，解析目标域名并拒绝指向私有地址的请求，阻断通过域名访问内网服务的 SSRF 攻击。

**设计意图**：为什么不在 HTTP 层拦截？因为 `httpx` 等客户端在建立连接时已经需要解析 DNS，如果在请求后拦截，攻击者仍可通过 DNS 解析阶段探测内网。代码选择在**请求前**做预解析，同时覆盖重定向后的 URL。

**关键源码**（`nanobot/security/network.py:30-63`）：
```python
def validate_url_target(url: str) -> tuple[bool, str]:
    # ① scheme 白名单 — 只允许 http/https，过滤 file://、ftp:// 等
    if p.scheme not in ("http", "https"):
        return False, f"Only http/https allowed, got '{p.scheme or 'none'}'"
    if not p.netloc:
        return False, "Missing domain"

    hostname = p.hostname
    if not hostname:
        return False, "Missing hostname"

    # ② 预解析 DNS — 在真正连接前拿到所有 A/AAAA 记录
    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False, f"Cannot resolve hostname: {hostname}"

    # ③ 逐条检查解析结果 — 任一 IP 落入私网即拒绝
    for info in infos:
        try:
            addr = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if _is_private(addr):
            return False, f"Blocked: {hostname} resolves to private/internal address {addr}"

    return True, ""
```

---

### 机制 B：文件系统沙箱 —— `allowed_dir` 在工具初始化时注入

**作用**：将文件读写操作限制在指定目录（通常是 workspace）之内，防止路径遍历和敏感文件泄露。

**设计意图**：为什么不在 `execute()` 内部读取全局配置？因为 `Tool` 基类（`base.py`）是纯粹的能力抽象，不应依赖 `Config`；`AgentLoop` 作为编排层持有配置，通过构造函数将 `allowed_dir` 注入工具，实现**依赖倒置**——工具只知道自己被允许访问哪个目录，不知道这个目录从何而来。

**关键源码**（`nanobot/agent/loop.py:116-122`）：
```python
def _register_default_tools(self) -> None:
    # ① 根据 restrict_to_workspace 决定是否启用沙箱
    allowed_dir = self.workspace if self.restrict_to_workspace else None
    # ② ReadFileTool 额外允许访问 BUILTIN_SKILLS_DIR（技能文件读取不受限）
    extra_read = [BUILTIN_SKILLS_DIR] if allowed_dir else None
    self.tools.register(ReadFileTool(
        workspace=self.workspace, allowed_dir=allowed_dir, extra_allowed_dirs=extra_read
    ))
    for cls in (WriteFileTool, EditFileTool, ListDirTool):
        self.tools.register(cls(workspace=self.workspace, allowed_dir=allowed_dir))
```

**关键源码**（`nanobot/agent/tools/filesystem.py:10-25`）：
```python
def _resolve_path(
    path: str,
    workspace: Path | None = None,
    allowed_dir: Path | None = None,
    extra_allowed_dirs: list[Path] | None = None,
) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute() and workspace:
        p = workspace / p
    resolved = p.resolve()  # 解析符号链接和 ..
    if allowed_dir:
        all_dirs = [allowed_dir] + (extra_allowed_dirs or [])
        # ③ 使用 relative_to 检查 — 比字符串匹配更可靠
        if not any(_is_under(resolved, d) for d in all_dirs):
            raise PermissionError(f"Path {path} is outside allowed directory {allowed_dir}")
    return resolved
```

---

### 机制 C：渠道准入 —— `allowFrom` 默认空列表拒绝所有

**作用**：控制哪些用户可以向 nanobot 发送消息，防止 Bot Token 泄露后任何人都能操控 Agent。

**设计意图**：为什么不是默认允许所有？因为 nanobot 的 Agent 拥有文件读写、Shell 执行、网络访问等高危能力，如果默认开放，相当于把 root 权限暴露给整个互联网。空列表拒绝所有是一种**"fail-closed"**设计：用户必须显式配置白名单才能启动服务，避免"配置遗漏即被攻破"。

**关键源码**（`nanobot/channels/base.py:79-87`）：
```python
def is_allowed(self, sender_id: str) -> bool:
    """Check if *sender_id* is permitted.  Empty list → deny all; ``"*"`` → allow all."""
    allow_list = getattr(self.config, "allow_from", [])
    if not allow_list:
        logger.warning("{}: allow_from is empty — all access denied", self.name)
        return False
    if "*" in allow_list:
        return True
    return str(sender_id) in allow_list
```

**关键源码**（`nanobot/channels/manager.py:60-66`）—— 启动时强制校验，空列表直接退出：
```python
def _validate_allow_from(self) -> None:
    for name, ch in self.channels.items():
        if getattr(ch.config, "allow_from", None) == []:
            raise SystemExit(
                f'Error: "{name}" has empty allowFrom (denies all). '
                f'Set ["*"] to allow everyone, or add specific user IDs.'
            )
```

---

### 机制 D：Shell 命令多层过滤

**作用**：在 `ExecTool` 执行前，通过正则模式拦截危险命令、内网 URL 和路径遍历。

**设计意图**：Shell 是 Agent 系统中最危险的工具，因为一条命令可以串联多个操作（如 `curl | sh`）。代码采用**多层过滤**：先匹配 deny 模式（黑名单），再检查是否包含内网 URL（复用 `security/network.py`），最后在 `restrict_to_workspace` 模式下检查绝对路径是否越界。

**关键源码**（`nanobot/agent/tools/shell.py:144-176`）：
```python
def _guard_command(self, command: str, cwd: str) -> str | None:
    cmd = command.strip()
    lower = cmd.lower()

    # ① 黑名单正则匹配 — rm -rf、format、fork bomb 等
    for pattern in self.deny_patterns:
        if re.search(pattern, lower):
            return "Error: Command blocked by safety guard (dangerous pattern detected)"

    # ② 白名单模式（如果配置了 allow_patterns）
    if self.allow_patterns:
        if not any(re.search(p, lower) for p in self.allow_patterns):
            return "Error: Command blocked by safety guard (not in allowlist)"

    # ③ 检测命令字符串中是否嵌入了内网 URL（复用 security/network.py）
    from nanobot.security.network import contains_internal_url
    if contains_internal_url(cmd):
        return "Error: Command blocked by safety guard (internal/private URL detected)"

    # ④ restrict_to_workspace 模式下检查路径遍历和越界绝对路径
    if self.restrict_to_workspace:
        if "..\\" in cmd or "../" in cmd:
            return "Error: Command blocked by safety guard (path traversal detected)"
        # ... 绝对路径检查

    return None
```

---

## 5. 与其他维度的交互

```
[安全防护] --(allow_from 准入决策)--> [渠道管理]
[安全防护] --(allowed_dir 沙箱边界)--> [工具系统]
[安全防护] --(SSRF 校验结果)--> [工具系统 / WebFetchTool]
[安全防护] --(命令过滤结果)--> [工具系统 / ExecTool]
[安全防护] <--(restrict_to_workspace 配置)-- [初始化与环境 / Config]
[安全防护] <--(sender_id, channel 信息)-- [渠道管理 / BaseChannel]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 渠道管理 | `is_allowed()` 返回布尔值决定是否转发消息到 Bus | `channels/base.py:L79-87` |
| 输出到 | 工具系统 | `validate_url_target()` 被 `WebFetchTool` 调用拦截恶意 URL | `agent/tools/web.py:L236-238` |
| 输出到 | 工具系统 | `contains_internal_url()` 被 `ExecTool` 调用检测命令中的内网 URL | `agent/tools/shell.py:L157-159` |
| 输出到 | 工具系统 | `allowed_dir` 被 `_FsTool._resolve()` 用于路径边界检查 | `agent/tools/filesystem.py:L21-24` |
| 依赖 | 初始化与环境 | `restrict_to_workspace` 配置决定工具初始化参数 | `config/schema.py:L150` |
| 依赖 | 初始化与环境 | `allow_from` 配置决定渠道准入白名单 | 各渠道 Config 类（如 `telegram.py:L158`） |
| 依赖 | 编排循环 | `AgentLoop` 在初始化时将安全参数注入各工具 | `agent/loop.py:L116-128` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"安全默认优于开发便利"**：`allowFrom` 空列表拒绝所有、`restrict_to_workspace` 默认 `False`（但文件工具在没有 `allowed_dir` 时完全不限制）—— 作者假设用户会阅读文档并显式配置安全参数，而不是开箱即用。
2. **"网络防护是共享基础设施"**：`security/network.py` 被 `web.py` 和 `shell.py` 同时引用，作者假设未来还会有其他工具需要网络校验（如 MCP 工具、子 Agent 的 HTTP 调用）。
3. **"DNS 预解析的代价可接受"**：`validate_url_target()` 在每次 `web_fetch` 前都做一次 `socket.getaddrinfo()`，作者假设 Agent 的网络请求频率不高，DNS 查询的延迟在可接受范围内。

### 6.2 这个设计的代价/风险

1. **DNS 预解析的 TOCTOU 窗口**：`validate_url_target()` 解析时返回的 IP 与 `httpx` 实际连接时的 IP 可能不同（DNS 重绑定攻击）。代码在 `validate_resolved_url()` 中对重定向后的 URL 做了二次校验，但**首次请求本身仍存在被重绑定的风险**。
2. **Shell 过滤是正则黑魔法**：`shell.py:L26-36` 的 `deny_patterns` 是正则表示式列表，面对 `r\m -rf`（反斜杠转义）或 `echo rm -rf`（字符串拼接后 eval）等绕过手段显得脆弱。
3. **`restrict_to_workspace=False` 时文件工具完全开放**：默认配置下文件工具没有 `allowed_dir`，可以读写任意路径。这与 `allowFrom` 的"默认拒绝"哲学不一致，是一个**安全默认值的断裂**。
4. **MCP 工具未继承安全边界**：`mcp.py` 中的 `MCPToolWrapper` 直接透传调用，没有 `restrict_to_workspace` 或 SSRF 校验的注入逻辑。如果 MCP Server 提供了文件或网络工具，nanobot 的安全层无法覆盖。

### 6.3 如果要重新设计，可能会改变什么

1. **统一安全策略注入点**：当前安全参数散落在 `loop.py`（文件工具）、`web.py`（网络校验）、`shell.py`（命令过滤）三个地方。可以考虑在 `ToolRegistry.execute()` 前增加一个**安全中间件层**，统一处理所有工具的安全策略，避免 MCP 工具成为漏网之鱼。
2. **`restrict_to_workspace` 默认设为 `True`**：对于个人 AI 助手场景，绝大多数用户只需要在工作区内操作。默认开放反而需要用户主动意识到风险。
3. **引入 DNS-over-HTTPS 或缓存**：在高频 `web_fetch` 场景下，重复的 `getaddrinfo()` 可能成为性能瓶颈，且容易受本地 DNS 劫持影响。

### 6.4 对我自己设计 Agent 系统的启示

> **安全不能只做在工具内部，而要在"配置层 → 编排层 → 工具层"三级分别设防。** nanobot 的巧妙之处在于：网络防护做成独立模块被多工具复用，文件沙箱通过构造函数注入保持工具的无状态性，渠道白名单在消息入口就拦截。这三层彼此解耦、互不依赖，任何一个层被绕过，还有其他层兜底——这才是"小而美"架构在安全上的最佳实践。
