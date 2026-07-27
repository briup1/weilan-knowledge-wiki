# 维度12：初始化与环境（Initialization & Environment）

## 1. 一句话定位

Hermes Agent 的「初始化与环境」维度是一套**多层级、profile-aware、后端可插拔的运行时根基系统**：它通过单一事实来源的路径常量 (`get_hermes_home`)、三路合并的配置加载 (`DEFAULT_CONFIG` + 用户 YAML + 环境变量)、交互式设置向导 (`hermes setup`)，以及基于 `BaseEnvironment` ABC 的 7 大执行后端，为 CLI、Gateway、Cron、Subagent 等所有入口提供一致的初始化契约与沙箱执行环境。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

| 缺失场景 | 后果 |
|---------|------|
| 无统一路径根 | 30+ 模块在 import 时硬编码 `~/.hermes`，Docker/自定义部署无法重定向数据目录；跨 profile 写入会导致静默数据污染 |
| 无配置合并策略 | 用户只改了一个 `model.default`，却必须抄写全部 DEFAULT_CONFIG；升级后新增字段丢失，导致旧配置在新版本中断 |
| 无环境快照 | 每次 `terminal()` 调用都丢失 PATH、alias、shell 函数；nvm/pyenv 等工具在 agent 内完全不可用 |
| 无后端抽象 | 本地/Docker/SSH/云沙箱的代码散落在各 tool 中，新增后端需重写整套进程生命周期、超时、中断、CWD 追踪逻辑 |
| 无 profile 隔离 | 同一台机器上的「工作」与「个人」profile 共用 `~/.hermes`，git 身份、SSH key、API key 互相泄漏 |

### 2.2 具体触发条件

- **首次安装**：`hermes setup` 引导用户选择 provider、terminal backend、agent 参数，生成初始 `config.yaml` 与 `.env`
- **CLI 启动**：`hermes chat` / `hermes gateway` 等任何子命令入口，先执行 `_apply_profile_override()` 解析 `--profile` 并设置 `HERMES_HOME`
- **配置读取**：`load_config()` 在运行时热加载，支持 mtime 缓存、deep-merge、环境变量展开、版本迁移
- **工具执行**：`terminal_tool()` 根据 `terminal.backend` 调用 `_create_environment()` 构造对应后端，并执行 `init_session()` 捕获 shell 环境
- **Gateway/Cron 子进程**：systemd 模板与 kanban dispatcher 显式传播 `HERMES_HOME`，防止 fallback 到默认 profile（issue #18594）

---

## 3. 核心设计思路

### 3.1 抽象模型（伪代码）

```
# 路径层 — 单一事实来源
HERMES_HOME = env["HERMES_HOME"] || ~/.hermes
if profile_active:
    HERMES_HOME = ~/.hermes/profiles/<name>

# 配置层 — 三路加载
def load_config():
    base    = deepcopy(DEFAULT_CONFIG)          # 代码内嵌默认值
    user    = yaml.safe_load(~/.hermes/config.yaml) or {}
    merged  = deep_merge(base, user)            # 递归覆盖，保留未改动的嵌套默认值
    merged  = normalize_root_model_keys(merged) # 迁移旧根级 key 到 model 子树
    merged  = expand_env_vars(merged)           # 展开 ${VAR}
    cache_on(mtime, size)                       # 避免重复 IO
    return merged

# 环境层 — ABC + 工厂
def terminal_tool(command):
    env_type = cfg["terminal"]["backend"]       # local|docker|modal|...
    env      = _create_environment(env_type, ...) # 工厂分发
    env.init_session()                          # 一次性的 login shell 快照
    return env.execute(command)                 # 统一：source snapshot → cd → run → re-dump env → emit CWD marker
```

### 3.2 关键设计决策（表格）

| 决策 | 选项 A（选中） | 选项 B（放弃） | 理由 |
|------|--------------|--------------|------|
| 路径根解析 | `get_hermes_home()` 函数，支持 `HERMES_HOME` env + profile fallback | 每个模块直接 `Path.home() / ".hermes"` | 单一事实来源；30+ 调用点在 import 时安全调用；Docker/自定义部署可重定向 |
| Profile 切换机制 | 模块级 `_apply_profile_override()` 在 `sys.argv` 解析阶段设置 `HERMES_HOME` env var | 运行时传参给每个函数 | 大量模块在 import 时缓存 `HERMES_HOME`；env var 是最低开销的全局广播 |
| 配置合并策略 | `deep_merge` 递归覆盖 + `DEFAULT_CONFIG` 作为完整基线 | 扁平 dict，用户必须抄写全部字段 | 用户只改关心的 key；升级新增字段自动生效；保留嵌套结构的局部覆盖语义 |
| 环境快照持久化 | `init_session()` 一次性 `bash -l` 捕获 `export -p / declare -f / alias -p` 到临时文件；后续命令 `source` 该文件 | 每次命令都 `bash -l` | 避免重复登录 shell 开销；捕获 nvm/pyenv PATH；支持 CWD 跨调用持久化 |
| CWD 追踪 | 双通道：本地读 `_cwd_file`，远程解析 stdout `_cwd_marker` | 仅文件或仅 marker | 本地无额外输出污染；远程无文件系统依赖（SSH/云沙箱） |
| 后端扩展 | `BaseEnvironment` ABC 定义 `_run_bash()` + `cleanup()`；工厂 `_create_environment()` 按字符串分发 | 每个后端独立 tool | 统一超时、中断、stdin、环境过滤、CWD 追踪；新增后端只需实现 2 个方法 |
| 密钥隔离 | `_build_provider_env_blocklist()` 动态收集所有 `*_API_KEY` / `*_TOKEN`，默认不泄漏到子进程 | 白名单放行 | 安全默认；`HERMES_FORCE_*` 前缀可显式透传；`env_passthrough` 技能声明自动豁免 |
| 配置缓存 | 按 `(mtime_ns, size)` 缓存，key 为 `str(config_path)` | 不缓存或按进程缓存 | profile 切换时路径变，缓存不碰撞；deepcopy 返回防止调用方污染缓存 |

### 3.3 数据流/控制流

```
[用户 shell]
   │ hermes chat --profile coder
   ▼
[main.py] _apply_profile_override()
   │ 解析 --profile → resolve_profile_env("coder")
   │ → HERMES_HOME=~/.hermes/profiles/coder
   ▼
[main.py] main() → 子命令分发
   │
   ├─► [config.py] load_config()
   │      ├─ DEFAULT_CONFIG (代码内嵌 23 版本)
   │      ├─ ~/.hermes/profiles/coder/config.yaml
   │      ├─ deep_merge + normalize + expand_env_vars
   │      └─ 返回完整配置 dict
   │
   ├─► [plugins.py] discover_plugins()
   │      ├─ bundled plugins → user plugins → project plugins → pip plugins
   │      └─ 注册 tools / hooks / context engines
   │
   └─► [terminal_tool.py] terminal_tool("ls -la")
          │
          ├─ _create_environment("docker", image=..., cwd=...)
          │      └─ DockerEnvironment.__init__()
          │            ├─ docker run -d --init --name hermes-xxx ...
          │            ├─ 挂载 credential/skills/cache 目录 (ro)
          │            ├─ 资源限制 --cpus --memory --storage-opt
          │            └─ init_session() → 容器内 bash -l 捕获快照
          │
          └─ env.execute("ls -la")
                 ├─ _wrap_command() → source snapshot → cd /workspace → eval 'ls -la'
                 ├─ _run_bash() → docker exec hermes-xxx bash -c "..."
                 ├─ _wait_for_process() → select() 轮询 + 中断检查
                 ├─ _update_cwd() → 解析 stdout marker 或读 _cwd_file
                 └─ cleanup() (空闲超时或进程退出时) → docker stop / rm
```

---

## 4. 关键机制拆解（含源码）

### 4.1 路径常量：单一事实来源与 profile 感知

```python
# hermes_constants.py:14-68
def get_hermes_home() -> Path:
    val = os.environ.get("HERMES_HOME", "").strip()
    if val:
        return Path(val)
    # Guard: non-default profile active but HERMES_HOME unset → stderr 警告一次
    global _profile_fallback_warned
    if not _profile_fallback_warned:
        active_path = (Path.home() / ".hermes" / "active_profile")
        active = active_path.read_text().strip() if active_path.exists() else ""
        if active and active != "default":
            _profile_fallback_warned = True
            import sys
            sys.stderr.write(
                f"[HERMES_HOME fallback] HERMES_HOME is unset but active "
                f"profile is {active!r}. Falling back to ~/.hermes ...\n"
            )
    return Path.home() / ".hermes"

# hermes_constants.py:71-107
def get_default_hermes_root() -> Path:
    native_home = Path.home() / ".hermes"
    env_home = os.environ.get("HERMES_HOME", "")
    if not env_home:
        return native_home
    env_path = Path(env_home)
    try:
        env_path.resolve().relative_to(native_home.resolve())
        return native_home  # profile mode under ~/.hermes
    except ValueError:
        pass
    if env_path.parent.name == "profiles":
        return env_path.parent.parent  # Docker profile: /opt/data/profiles/coder
    return env_path  # Docker custom: /opt/data
```

**要点**：`get_hermes_home()` 被 30+ 模块在 import 时调用，因此必须保持**零依赖、零副作用**（不触发 logging）。profile fallback 警告直接写 `stderr`，避免 logging 尚未初始化的问题。

### 4.2 Profile 前置解析：在模块导入前完成

```python
# hermes_cli/main.py:101-179
def _apply_profile_override() -> None:
    argv = sys.argv[1:]
    profile_name = None
    consume = 0
    for i, arg in enumerate(argv):
        if arg in ("--profile", "-p") and i + 1 < len(argv):
            profile_name = argv[i + 1]
            consume = 2
            break
        elif arg.startswith("--profile="):
            profile_name = arg.split("=", 1)[1]
            consume = 1
            break
    # 1b. 拒绝无效 profile 名（如 pytest 的 "-p no:xdist"）
    if profile_name is not None and consume == 2:
        if not _re.match(r"^[a-z0-9][a-z0-9_-]{0,63}$", profile_name):
            profile_name = None
            consume = 0
    # 1.5 若 HERMES_HOME 已设置且无显式 flag，信任它（子进程继承）
    if profile_name is None and os.environ.get("HERMES_HOME"):
        return
    # 2. 回退到 active_profile 文件
    if profile_name is None:
        active_path = get_default_hermes_root() / "active_profile"
        if active_path.exists():
            name = active_path.read_text().strip()
            if name and name != "default":
                profile_name = name
    # 3. 设置 HERMES_HOME 并从 sys.argv 剥离 flag
    if profile_name is not None:
        hermes_home = resolve_profile_env(profile_name)
        os.environ["HERMES_HOME"] = hermes_home
        if consume > 0:
            # 从 sys.argv 移除 --profile 及其值，避免 argparse 报错
            ...

_apply_profile_override()  # 模块顶层立即执行
```

**要点**：该函数在 `main.py` 的模块顶层调用，**早于任何 hermes 子模块的 import**，确保后续所有 `os.getenv("HERMES_HOME")` 都读到正确值。

### 4.3 配置三路加载：默认值 + 用户 YAML + 环境变量展开

```python
# hermes_cli/config.py:395-1385  (DEFAULT_CONFIG 节选)
DEFAULT_CONFIG = {
    "model": "",
    "providers": {},
    "agent": {
        "max_turns": 90,
        "gateway_timeout": 1800,
        ...
    },
    "terminal": {
        "backend": "local",
        "cwd": ".",
        "timeout": 180,
        ...
    },
    "_config_version": 23,
}

# hermes_cli/config.py:3978-4023
def load_config() -> Dict[str, Any]:
    with _CONFIG_LOCK:
        ensure_hermes_home()
        config_path = get_config_path()
        path_key = str(config_path)
        try:
            st = config_path.stat()
            cache_key = (st.st_mtime_ns, st.st_size)
        except FileNotFoundError:
            cache_key = None
        cached = _LOAD_CONFIG_CACHE.get(path_key)
        if cached is not None and cache_key is not None and cached[:2] == cache_key:
            return copy.deepcopy(cached[2])
        config = copy.deepcopy(DEFAULT_CONFIG)
        if cache_key is not None:
            with open(config_path, encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            # 兼容旧根级 max_turns → 迁移到 agent.max_turns
            if "max_turns" in user_config:
                agent_user_config = dict(user_config.get("agent") or {})
                if agent_user_config.get("max_turns") is None:
                    agent_user_config["max_turns"] = user_config["max_turns"]
                user_config["agent"] = agent_user_config
                user_config.pop("max_turns", None)
            config = _deep_merge(config, user_config)
        normalized = _normalize_root_model_keys(_normalize_max_turns_config(config))
        expanded = _expand_env_vars(normalized)
        _LAST_EXPANDED_CONFIG_BY_PATH[path_key] = copy.deepcopy(expanded)
        if cache_key is not None:
            _LOAD_CONFIG_CACHE[path_key] = (cache_key[0], cache_key[1], copy.deepcopy(expanded))
        return expanded

# hermes_cli/config.py:3729-3744
def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

# hermes_cli/config.py:3749-3766
def _expand_env_vars(obj):
    if isinstance(obj, str):
        return re.sub(r"\${([^}]+)}", lambda m: os.environ.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    return obj
```

**要点**：
- `deep_merge` 保证用户只覆盖关心的 key，嵌套结构（如 `agent.max_turns`）局部生效，其余保持默认。
- `_expand_env_vars` 支持 `${VAR}` 语法，允许在 `config.yaml` 中引用环境变量而不泄露到版本控制。
- 缓存 key 为 `str(config_path)`，profile 切换时路径变化，缓存自然隔离。

### 4.4 交互式设置向导

```python
# hermes_cli/setup.py:778-850
def setup_model_provider(config: dict, *, quick: bool = False):
    from hermes_cli.main import select_provider_and_model
    select_provider_and_model()  # 与 `hermes model` 共用同一代码路径
    # 关键：从磁盘重新加载，避免 wizard 的 stale dict 覆盖用户选择
    _refreshed = load_config()
    config["model"] = _refreshed.get("model", config.get("model"))

# hermes_cli/setup.py:1292-1360 (setup_terminal_backend 示意)
def setup_terminal_backend(config: dict):
    print_header("Terminal Backend")
    backends = ["local", "docker", "singularity", "modal", "daytona", "vercel_sandbox", "ssh"]
    choice = prompt_choice("Select terminal backend:", backends, default="local")
    config["terminal"]["backend"] = choice
    if choice == "docker":
        config["terminal"]["docker_image"] = prompt_input(
            "Docker image:", default="nikolaik/python-nodejs:python3.11-nodejs20"
        )
```

**要点**：向导采用**模块化、可独立运行**的设计，每个 section 对应一个子命令配置流程（如 `setup_model_provider` 复用 `hermes model` 的 `select_provider_and_model`），避免重复实现。

### 4.5 环境基类：统一执行契约

```python
# tools/environments/base.py:267-340
class BaseEnvironment(ABC):
    _stdin_mode: str = "pipe"
    _snapshot_timeout: int = 30

    def __init__(self, cwd: str, timeout: int, env: dict = None):
        self.cwd = cwd
        self.timeout = timeout
        self.env = env or {}
        self._session_id = uuid.uuid4().hex[:12]
        self._snapshot_path = f"/tmp/hermes-snap-{self._session_id}.sh"
        self._cwd_file = f"/tmp/hermes-cwd-{self._session_id}.txt"
        self._snapshot_ready = False

    @abstractmethod
    def _run_bash(self, cmd_string: str, *, login: bool = False,
                  timeout: int = 120, stdin_data: str | None = None) -> ProcessHandle:
        ...

    @abstractmethod
    def cleanup(self):
        ...

    def init_session(self):
        _quoted_cwd = shlex.quote(self.cwd)
        bootstrap = (
            f"export -p > {self._snapshot_path}\n"
            f"declare -f | grep -vE '^_[^_]' >> {self._snapshot_path}\n"
            f"alias -p >> {self._snapshot_path}\n"
            f"echo 'shopt -s expand_aliases' >> {self._snapshot_path}\n"
            f"echo 'set +e' >> {self._snapshot_path}\n"
            f"echo 'set +u' >> {self._snapshot_path}\n"
            f"builtin cd {_quoted_cwd} 2>/dev/null || true\n"
            f"pwd -P > {self._cwd_file} 2>/dev/null || true\n"
            f"printf '\\n{self._cwd_marker}%s{self._cwd_marker}\\n' \"$(pwd -P)\"\n"
        )
        proc = self._run_bash(bootstrap, login=True, timeout=self._snapshot_timeout)
        result = self._wait_for_process(proc, timeout=self._snapshot_timeout)
        self._snapshot_ready = True
        self._update_cwd(result)
```

**要点**：`init_session()` 是 Hermes 终端可用性的核心——它通过**一次非交互式 login shell** 捕获 `export -p`（环境变量）、`declare -f`（函数）、`alias -p`（别名），后续命令只需 `source` 该快照，无需重复登录 shell。

### 4.6 命令包装：快照 source + CWD 恢复 + 环境回写

```python
# tools/environments/base.py:400-480
def _wrap_command(self, command: str, cwd: str) -> str:
    escaped = command.replace("'", "'\\''")
    parts = []
    if self._snapshot_ready:
        parts.append(f"source {self._snapshot_path} >/dev/null 2>&1 || true")
    quoted_cwd = self._quote_cwd_for_cd(cwd)
    parts.append(f"builtin cd -- {quoted_cwd} || exit 126")
    parts.append(f"eval '{escaped}'")
    parts.append("__hermes_ec=$?")
    if self._snapshot_ready:
        parts.append(f"export -p > {self._snapshot_path} 2>/dev/null || true")
    parts.append(f"pwd -P > {self._cwd_file} 2>/dev/null || true")
    parts.append(f"printf '\\n{self._cwd_marker}%s{self._cwd_marker}\\n' \"$(pwd -P)\"")
    parts.append("exit $__hermes_ec")
    return "\n".join(parts)
```

**要点**：
- `source >/dev/null` 解决 macOS bash 3.2 的 `declare -x` 泄漏问题（issue #15459）。
- `builtin cd --` 防止以 `-` 开头的目录名被解析为选项。
- 执行后重新 `export -p > snapshot`，实现**跨调用的环境变量累积**（如 `cd`、`export FOO=bar` 对后续命令可见）。

### 4.7 后端工厂：7 大执行环境统一分发

```python
# tools/terminal_tool.py:1101-1200
def _create_environment(env_type: str, image: str, cwd: str, timeout: int,
                        ssh_config: dict = None, container_config: dict = None,
                        local_config: dict = None, task_id: str = "default",
                        host_cwd: str = None):
    cc = container_config or {}
    cpu = cc.get("container_cpu", 1)
    memory = cc.get("container_memory", 5120)
    disk = cc.get("container_disk", 51200)
    persistent = cc.get("container_persistent", True)

    if env_type == "local":
        return _LocalEnvironment(cwd=cwd, timeout=timeout)
    elif env_type == "docker":
        return _DockerEnvironment(
            image=image, cwd=cwd, timeout=timeout,
            cpu=cpu, memory=memory, disk=disk,
            persistent_filesystem=persistent, task_id=task_id,
            volumes=cc.get("docker_volumes", []),
            host_cwd=host_cwd,
            auto_mount_cwd=cc.get("docker_mount_cwd_to_workspace", False),
            forward_env=cc.get("docker_forward_env", []),
            env=cc.get("docker_env", {}),
            run_as_host_user=cc.get("docker_run_as_host_user", False),
        )
    elif env_type == "singularity":
        return _SingularityEnvironment(...)
    elif env_type == "modal":
        ...  # managed vs direct 双模式路由
    elif env_type == "daytona":
        from tools.environments.daytona import DaytonaEnvironment as _DaytonaEnvironment
        return _DaytonaEnvironment(...)
    elif env_type == "vercel_sandbox":
        from tools.environments.vercel_sandbox import VercelSandboxEnvironment as _VercelSandboxEnvironment
        return _VercelSandboxEnvironment(...)
    elif env_type == "ssh":
        return _SSHEnvironment(host=..., user=..., ...)
    else:
        raise ValueError(f"Unknown environment type: {env_type}")
```

### 4.8 Docker 后端：安全加固与资源限制

```python
# tools/environments/docker.py:274-520 (关键片段)
class DockerEnvironment(BaseEnvironment):
    def __init__(self, image, cwd="/root", timeout=60, cpu=0, memory=0, disk=0,
                 persistent_filesystem=False, task_id="default", ...):
        ...
        resource_args = []
        if cpu > 0: resource_args.extend(["--cpus", str(cpu)])
        if memory > 0: resource_args.extend(["--memory", f"{memory}m"])
        if disk > 0 and sys.platform != "darwin":
            if self._storage_opt_supported():
                resource_args.extend(["--storage-opt", f"size={disk}m"])
        security_args = _build_security_args(run_as_host_user and bool(user_args))
        # --cap-drop=ALL --security-opt=no-new-privileges --pid-limit ...
        run_cmd = [
            self._docker_exe, "run", "-d",
            "--init", "--name", container_name, "-w", cwd,
            *security_args, *user_args, *writable_args,
            *resource_args, *volume_args, *env_args,
            image, "sleep", "infinity",
        ]
        result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=120, check=True)
        self._container_id = result.stdout.strip()
        self._init_env_args = self._build_init_env_args()
        self.init_session()
```

**要点**：
- `--init` 使用 tini/catatonit 作为 PID 1，防止僵尸进程。
- 安全参数包括 `cap-drop=ALL`、`no-new-privileges`、`pid-limit`。
- `storage-opt` 仅在 overlay2/XFS/pquota 支持时启用，否则优雅降级并告警。
- 持久化模式通过 bind mount `~/.hermes/sandboxes/docker/<task_id>/` 到容器内 `/root` 和 `/workspace`。

### 4.9 SSH 后端：ControlMaster 连接复用

```python
# tools/environments/ssh.py:36-100
class SSHEnvironment(BaseEnvironment):
    def __init__(self, host, user, cwd="~", timeout=60, port=22, key_path=""):
        super().__init__(cwd=cwd, timeout=timeout)
        self.host = host; self.user = user; self.port = port; self.key_path = key_path
        self.control_dir = Path(tempfile.gettempdir()) / "hermes-ssh"
        self.control_dir.mkdir(parents=True, exist_ok=True)
        # 哈希 socket 名以避免 macOS sun_path 104 字节限制
        _socket_id = hashlib.sha256(f"{user}@{host}:{port}".encode()).hexdigest()[:16]
        self.control_socket = self.control_dir / f"{_socket_id}.sock"
        self._establish_connection()
        self._remote_home = self._detect_remote_home()
        self._ensure_remote_dirs()
        self._sync_manager = FileSyncManager(...)
        self._sync_manager.sync(force=True)
        self.init_session()

    def _build_ssh_command(self, extra_args=None):
        cmd = ["ssh"]
        cmd.extend(["-o", f"ControlPath={self.control_socket}"])
        cmd.extend(["-o", "ControlMaster=auto"])
        cmd.extend(["-o", "ControlPersist=300"])
        cmd.extend(["-o", "BatchMode=yes"])
        cmd.extend(["-o", "StrictHostKeyChecking=accept-new"])
        ...
```

**要点**：SSH 后端通过 `ControlMaster` 实现连接复用，避免每次命令都经历 TCP 握手；socket 路径经 SHA256 截断，解决 macOS 的 Unix domain socket 路径长度限制。

### 4.10 子进程环境隔离：密钥过滤与 profile HOME

```python
# tools/environments/local.py:80-160 (关键片段)
_HERMES_PROVIDER_ENV_BLOCKLIST = _build_provider_env_blocklist()
# 包含 OPENAI_API_KEY, ANTHROPIC_TOKEN, TELEGRAM_BOT_TOKEN, MODAL_TOKEN_ID 等

def _sanitize_subprocess_env(base_env: dict | None, extra_env: dict | None = None) -> dict:
    sanitized: dict[str, str] = {}
    for key, value in (base_env or {}).items():
        if key.startswith(_HERMES_PROVIDER_ENV_FORCE_PREFIX):
            real_key = key[len(_HERMES_PROVIDER_ENV_FORCE_PREFIX):]
            sanitized[real_key] = value
        elif key not in _HERMES_PROVIDER_ENV_BLOCKLIST or _is_passthrough(key):
            sanitized[key] = value
    # Per-profile HOME 隔离
    from hermes_constants import get_subprocess_home
    _profile_home = get_subprocess_home()
    if _profile_home:
        sanitized["HOME"] = _profile_home
    return sanitized
```

**要点**：
- 默认**黑名单过滤**所有 provider key、token、secret，防止 agent 子进程意外泄漏凭证。
- `_HERMES_FORCE_*` 前缀可显式透传特定变量。
- `get_subprocess_home()` 若发现 `{HERMES_HOME}/home/` 存在，则将其设为子进程 `HOME`，实现 git/ssh/npm 等工具配置的 profile 级隔离。

---

## 5. 与其他维度的交互

| 交互维度 | 交互方式 | 关键代码位置 |
|---------|---------|------------|
| **维度1：配置系统** | `load_config()` / `save_config()` 提供全部运行时配置；`DEFAULT_CONFIG` 定义 agent/terminal/display/compression 等全部默认参数 | `hermes_cli/config.py:395-1385` |
| **维度2：CLI 入口** | `main.py` 在模块顶层调用 `_apply_profile_override()`，先于任何 hermes 模块 import | `hermes_cli/main.py:101-179` |
| **维度3：工具系统** | `terminal_tool.py` 通过 `_create_environment()` 为 `terminal()` / `execute_code()` 提供执行后端；插件通过 `register_tool()` 扩展 | `tools/terminal_tool.py:1101`, `hermes_cli/plugins.py:1188` |
| **维度4：Agent 核心** | `agent.max_turns`, `agent.gateway_timeout` 等配置直接控制 agent 循环行为；`init_session()` 的快照使 agent 工具调用能继承 shell 环境 | `hermes_cli/config.py:395-500` |
| **维度5：会话与记忆** | `ensure_hermes_home()` 创建 `sessions/`, `memories/`, `logs/` 子目录；`state.db` 与会话存储共用 HERMES_HOME | `hermes_cli/config.py:345-380` |
| **维度6：Gateway** | Gateway systemd 模板显式传播 `HERMES_HOME`；`gateway_timeout`, `restart_drain_timeout` 等配置控制网关生命周期 | `hermes_cli/gateway.py` (systemd 模板) |
| **维度7：Cron** | Cron 调度器通过 kanban dispatcher 启动子进程时传播 `HERMES_HOME`；`cron_mode` 配置控制危险命令审批策略 | `hermes_cli/kanban_db.py` |
| **维度8：安全** | `security.redact_secrets`, `tirith_enabled` 等配置在 DEFAULT_CONFIG 中定义；子进程环境黑名单防止密钥泄漏 | `hermes_cli/config.py:1300-1320` |
| **维度9：Provider/模型** | `model`, `providers`, `fallback_providers`, `auxiliary` 等配置节在 DEFAULT_CONFIG 中统一定义；`setup_model_provider()` 向导引导用户完成初始化 | `hermes_cli/config.py:395`, `hermes_cli/setup.py:778` |
| **维度10：消息平台** | `slack`, `discord`, `telegram`, `whatsapp` 等平台配置在 DEFAULT_CONFIG 中作为独立节存在 | `hermes_cli/config.py:1200-1280` |
| **维度11：代码执行** | `code_execution.mode` 控制 `execute_code()` 运行在 project 目录还是隔离 temp；`terminal.backend` 决定代码执行所在的沙箱后端 | `hermes_cli/config.py:1350-1360` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计权衡

| 权衡点 | 选择 | 代价 | 收益 |
|--------|------|------|------|
| **Env var 作为 profile 广播机制** | 在 `main.py` 模块顶层设置 `HERMES_HOME` | 隐式全局状态，调试时需检查 env | 零改动兼容 30+ 模块的模块级路径缓存；子进程自然继承 |
| **deep_merge 而非 schema validation** | 运行时递归 dict merge | 用户可能写错嵌套类型（如把 dict 写成 str），导致 `cfg_get` 回退到 default | 极大的灵活性；升级新增字段零摩擦；无需维护 JSON Schema |
| **init_session 快照文件** | 临时 shell script 存储 env/alias/function | 多并发命令时存在 race（last-writer-wins） | 实现极简，无需进程内守护进程；兼容所有后端（包括无文件系统的云沙箱可通过 stdout marker 变通） |
| **spawn-per-call 而非持久 shell** | 每次 `execute()` 新建进程（local 除外） | 进程创建开销；local 后端通过 `TERMINAL_LOCAL_PERSISTENT` 可选开启持久 shell | 天然支持超时和中断；后台进程不会意外持有管道；cleanup 语义清晰 |
| **黑名单过滤子进程 env** | 默认阻止所有 `*_API_KEY` / `*_TOKEN` | 某些合法工具需要密钥时需显式配置 `env_passthrough` 或 `docker_forward_env` | 安全默认；防止 agent 编写的脚本意外泄漏凭证到日志或网络 |
| **配置缓存按路径 key** | `_LOAD_CONFIG_CACHE[path_key]` | 内存占用略增（一个 deepcopy 的 dict） | profile 切换时缓存不碰撞；多线程安全（`_CONFIG_LOCK`） |

### 6.2 可借鉴之处

1. **单一事实来源 + 防御性编程**：`get_hermes_home()` 不仅是函数，更是**架构约束**——任何新增的数据目录都必须通过它解析，并在注释中明确说明「所有其他副本应 import 此函数」。配合 `_profile_fallback_warned` 的一次性 stderr 告警，将跨 profile 数据污染从「静默 bug」变为「可诊断事件」。

2. **配置加载的「四层防御」**：DEFAULT_CONFIG（代码内嵌完整基线）→ `deep_merge`（用户局部覆盖）→ `normalize_root_model_keys`（旧配置自动迁移）→ `expand_env_vars`（动态值注入）。这使得**配置文件永远向前兼容**，用户无需在升级后手动迁移。

3. **ABC + 工厂模式统一异构后端**：`BaseEnvironment` 仅要求子类实现 `_run_bash()` 和 `cleanup()`，其余（超时、中断、stdin、CWD 追踪、环境过滤）全部由基类统一处理。新增一个云沙箱后端的工作量从「重写整套工具」降至「实现两个方法 + 工厂分支」。

4. **Login shell 快照解决「agent 内工具不可用」难题**：通过一次 `bash -l` 捕获 `export -p / declare -f / alias -p`，Hermes 在不依赖交互式 TTY 的前提下，让 nvm、pyenv、asdf 等用户 shell 配置对 agent 完全可用。这是终端 agent 的**可用性分水岭**。

5. **子进程 HOME 隔离**：`get_subprocess_home()` 通过目录存在性检测（而非配置开关）激活，将 git/ssh/npm 等系统工具的配置自然隔离到 profile 目录，实现「零配置的多身份切换」。
