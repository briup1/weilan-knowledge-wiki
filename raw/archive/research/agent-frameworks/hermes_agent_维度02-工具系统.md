# 维度 02 — 工具系统（Tool System）

> 源码基线：`tools/registry.py`、`model_tools.py`、`toolsets.py`，以及自注册的具体工具文件
> （`tools/file_tools.py`、`tools/terminal_tool.py`、`tools/delegate_tool.py`、`tools/skills_tool.py`、`tools/mcp_tool.py` 等）。

---

## 1. 一句话定位

工具系统是 Hermes Agent 中 **「工具发现 → schema 编排 → 调度分发」** 的中央总线：
通过一个零依赖的全局 `ToolRegistry` 单例，把"每个工具文件自己声明自己"的去中心化注册，统一到一个对 LLM 可见的、按 toolset 分组、按 `check_fn` 过滤、按生成代号失效缓存的工具表，并为
`run_agent.py` 提供唯一的同步分发入口 `handle_function_call()`。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

代码里能直接反推出几种具体故障：

1. **循环导入死锁**。Hermes 内部工具数十个（file/terminal/browser/mcp/discord/feishu/spotify/...），如果 `model_tools.py`
   要"手动 import 每个工具并构造 schema"，则 `tools/*.py` 反向依赖 `model_tools.py` 时立刻成环。`tools/registry.py`
   开头的 docstring 明确把这条画成依赖图：
   ```
   tools/registry.py  (no imports from model_tools or tool files)
          ^
   tools/*.py  (import from tools.registry at module level)
          ^
   model_tools.py  (imports tools.registry + all tool modules)
   ```
   `tools/registry.py:7-15`
2. **schema/handler 永远不同步**。如果 schema 写在一个表里、handler 写在另一个文件里，新增/重命名一个工具就要改两处，
   常见 bug 是 schema 改了名字但 dispatch 表没改 → LLM 调到一个"已注册的影子"。自注册把两件事绑在同一行 `registry.register(...)`。
3. **MCP 动态工具无处安放**。MCP server 启动后 `notifications/tools/list_changed` 会随时增删工具，如果没有运行时可变的注册表，
   只能进程重启。`tools/mcp_tool.py:1056-1094` 的 `_refresh_tools` 直接对 registry 做 nuke-stale + re-register。
4. **provider 兼容性放大爆炸**。每个 provider（DeepSeek/Kimi/Xiaomi MiMo/llama.cpp）对工具列表的容忍度不同：
   重复 tool name 会被拒绝、不规范的 `oneOf` 会被 llama.cpp GBNF 转换器拒绝。如果没有一个统一出口，每个调用方都得自己抄一份过滤。
5. **后端探活反复重算**。`check_terminal_requirements` 会 `subprocess.run(docker version, timeout=5)`、
   browser 探活会启动 playwright；如果每轮都做一次，agent 单 turn 多花几秒。注册表带 30 秒 TTL 的 `_check_fn_cached`
   就是为了把这件事降幅到"一个 turn 顶多一次"。

### 2.2 具体触发条件（代码中的判断逻辑）

- **discovery 触发**：`model_tools.py` 在模块顶部直接调用 `discover_builtin_tools()`（`model_tools.py:180`），
  这一个 import side-effect 把 `tools/*.py` 全部串好。
- **filter 触发**：`registry.get_definitions(tool_names)` 在每次构造工具列表时，对每个 `entry.check_fn` 做 TTL 缓存的 bool 判断
  （`tools/registry.py:331-337`）。返回 False 的工具被静默剔除——LLM 永远看不见。
- **shadow 拒绝**：`registry.register()` 中如果发现同名工具且非"两个 MCP toolset 互覆"的合法情况，直接 `logger.error`
  并 return，杜绝 plugin/MCP 抢内置（`tools/registry.py:240-263`）。
- **agent-loop 拦截**：`_AGENT_LOOP_TOOLS = {"todo", "memory", "session_search", "delegate_task"}`
  这些工具虽然在 registry 里有 schema（让 LLM 看见），但 `handle_function_call` 直接返回错误存根，强制走
  `run_agent.py` 的 agent-level 拦截路径（`model_tools.py:495,709-710`）——因为它们要访问 TodoStore/MemoryStore 等 agent 上下文。

---

## 3. 核心设计思路

### 3.1 抽象模型（伪代码）

```text
# 数据结构：极致小型 dataclass，__slots__ 锁字段
ToolEntry(name, toolset, schema, handler, check_fn,
          requires_env, is_async, description, emoji, max_result_size_chars)

# 单例：tools 字典 + toolset 检查 + 别名 + 一个 generation 计数器
class ToolRegistry:
    _tools: Dict[str, ToolEntry]
    _toolset_checks: Dict[str, Callable]
    _toolset_aliases: Dict[str, str]   # MCP server name -> mcp-<sanitized> toolset
    _lock: RLock                        # 写时序列化，读时取快照
    _generation: int                    # 每次写 +1，外部据此做 memo

# 注册的"协议"：模块顶层一行
registry.register(name=..., toolset=..., schema=..., handler=..., check_fn=..., emoji=...)

# 编排：toolset → tool name → entry → schema
def get_tool_definitions(enabled, disabled, quiet):
    names = ∪ resolve_toolset(t) for t in enabled
    names -= ∪ resolve_toolset(t) for t in disabled
    schemas = registry.get_definitions(names)         # check_fn TTL filter
    schemas = patch_dynamic_schemas(schemas)           # execute_code/discord/browser_navigate
    schemas = sanitize_tool_schemas(schemas)           # llama.cpp/Anthropic 兼容
    return schemas

# 分发：唯一入口
def handle_function_call(name, args, ...):
    args = coerce_tool_args(name, args)                # str→int / str→bool / str→list
    if name in _AGENT_LOOP_TOOLS: return stub_error
    fire("pre_tool_call")
    result = registry.dispatch(name, args, **ctx)
    fire("post_tool_call", duration_ms=...)
    result = fire("transform_tool_result")[0] or result
    return result
```

### 3.2 关键设计决策

| 决策点 | 选了什么 | 放弃了什么 | 代价/收益 |
|---|---|---|---|
| 注册方式 | **模块顶层 `registry.register(...)` 自注册** | 中心化"工具清单"或装饰器+魔法扫描 | 收益：新增工具只改一个文件，且依赖图天然单向；代价：必须显式 import 才会注册（用 AST 扫文件 `_module_registers_tools` 做兜底发现）。 |
| 失效模型 | **`_generation` 单调递增计数 + check_fn 30s TTL** | 显式订阅/事件总线，或每次重算 | 收益：`get_tool_definitions` 可以以 `(enabled, disabled, _generation, config_mtime)` 为键 memo（`model_tools.py:305-319`），MCP 动态刷新自动失效；代价：30s 内 env 变化（如刚启 docker）感知有最长 30s 滞后，作者在源码注释里直接写明这是有意权衡（`tools/registry.py:104-111`）。 |
| dispatch 路径 | **registry 拥有 sync/async 桥接，model_tools 只做拦截+hooks** | 让 agent loop 自己处理 async/await | 收益：每个 handler 自我保护——任何调用方调 `registry.dispatch()` 都安全；代价：要在 registry 里反向 import `model_tools._run_async`（`tools/registry.py:359`），形成一个文档化的循环但因为 lazy import 不会真死锁。 |
| LLM 行为兼容 | **入口处 `coerce_tool_args` + 出口处 `sanitize_tool_schemas`** | 信任模型严格遵守 schema | 收益：DeepSeek/Qwen/GLM 把 `42` 写成 `"42"`、把单 URL 写成 string 而非 list 时不会失败（`model_tools.py:545-563`）；llama.cpp 的 GBNF 转换器不会因 `oneOf` 拒整个请求；代价：可能掩盖模型真实输出 bug。 |

### 3.3 数据流 / 控制流

**启动期（discovery）：**
```
model_tools.py 被 import
  └─ discover_builtin_tools()                          [model_tools.py:180]
      └─ AST 扫 tools/*.py，对含顶层 registry.register 的模块做 importlib.import_module
          └─ 每个工具模块顶层执行 registry.register(...)   [tools/file_tools.py:1140-1143 等]
              └─ ToolRegistry._tools[name] = ToolEntry(...); _generation += 1
  └─ discover_plugins()                                [model_tools.py:196-200]
      └─ entry-point 插件 / 项目级 plugins 同样 registry.register
```

**Turn 期（schema 提供）：**
```
agent loop 准备一次 LLM 调用
  └─ get_tool_definitions(enabled_toolsets, ...)        [model_tools.py:271-332]
      ├─ key = (enabled, disabled, registry._generation, config_mtime)
      ├─ 命中 memo 直接返回
      └─ _compute_tool_definitions
          ├─ resolve_toolset() 把 toolset 名展开成 tool 名集合 [toolsets.py:563]
          ├─ registry.get_definitions(tool_names)        [tools/registry.py:310-341]
          │    └─ 对每个 entry 跑 _check_fn_cached(check_fn)  [TTL 30s]
          ├─ 对 execute_code/discord/browser_navigate 这些"看其他工具脸色"的 schema 重建
          └─ sanitize_tool_schemas() 兼容 llama.cpp 等
```

**Turn 期（dispatch）：**
```
LLM 返回 tool_call
  └─ run_agent.py:10440  handle_function_call(name, args, task_id, tool_call_id, ...)
      ├─ coerce_tool_args(name, args)                  [model_tools.py:503-574]
      ├─ if name in _AGENT_LOOP_TOOLS: return stub      ← agent loop 自己接管
      ├─ pre_tool_call hook（可阻断）                    [model_tools.py:722-737]
      ├─ start = time.monotonic()
      ├─ registry.dispatch(name, args, task_id=, user_task=)
      │    ├─ entry.is_async ? _run_async(handler(args, **kw)) : handler(args, **kw)
      │    └─ except: 返回 {"error": "..."}              ← 永不 crash，统一格式
      ├─ duration_ms = ...
      ├─ post_tool_call hook（observational）
      └─ transform_tool_result hook（first valid str wins）
```

---

## 4. 关键机制拆解（含源码）

### 4.1 自注册 + 一行声明：把元数据和实现绑在一起

> **为什么值得看**：每个工具用一行 `registry.register(...)` 把"对 LLM 暴露什么"和"实际跑什么"写到一处。
> 文件移动、删除、改名只动一处；而且因为是模块顶层，只要被 import 就一定生效，不会出现"实现存在但 LLM 看不见"的隐 bug。

`tools/file_tools.py:1140-1143`：

```python
registry.register(name="read_file",  toolset="file", schema=READ_FILE_SCHEMA,  handler=_handle_read_file,   check_fn=_check_file_reqs, emoji="📖", max_result_size_chars=100_000)
registry.register(name="write_file", toolset="file", schema=WRITE_FILE_SCHEMA, handler=_handle_write_file,  check_fn=_check_file_reqs, emoji="✍️", max_result_size_chars=100_000)
registry.register(name="patch",      toolset="file", schema=PATCH_SCHEMA,      handler=_handle_patch,       check_fn=_check_file_reqs, emoji="🔧", max_result_size_chars=100_000)
registry.register(name="search_files", toolset="file", schema=SEARCH_FILES_SCHEMA, handler=_handle_search_files, check_fn=_check_file_reqs, emoji="🔎", max_result_size_chars=100_000)
```

handler 是个极薄的薄片函数，把 `args` dict 拍平成具名参数，再把 `task_id` 从 `**kw` 里抠出来——**让真正实现的函数（`read_file_tool` 等）保持独立可测**：

`tools/file_tools.py:1093-1095`：
```python
def _handle_read_file(args, **kw):
    tid = kw.get("task_id") or "default"
    return read_file_tool(path=args.get("path", ""), offset=args.get("offset", 1), limit=args.get("limit", 500), task_id=tid)
```

### 4.2 AST 扫描的"零魔法"自动发现

> **为什么值得看**：避免装饰器 + 元类那种"看不懂哪里发生了什么"的魔法，但仍能"忘了写 import 也能跑起来"。
> AST 只识别**顶层**的 `registry.register(...)` 表达式——helper 模块里在函数体内调 register 不会被误识。

`tools/registry.py:42-74`：
```python
def _module_registers_tools(module_path: Path) -> bool:
    try:
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))
    except (OSError, SyntaxError):
        return False
    return any(_is_registry_register_call(stmt) for stmt in tree.body)

def discover_builtin_tools(tools_dir: Optional[Path] = None) -> List[str]:
    tools_path = Path(tools_dir) if tools_dir is not None else Path(__file__).resolve().parent
    module_names = [
        f"tools.{path.stem}"
        for path in sorted(tools_path.glob("*.py"))
        if path.name not in {"__init__.py", "registry.py", "mcp_tool.py"}
        and _module_registers_tools(path)
    ]
    imported: List[str] = []
    for mod_name in module_names:
        try:
            importlib.import_module(mod_name)
            imported.append(mod_name)
        except Exception as e:
            logger.warning("Could not import tool module %s: %s", mod_name, e)
    return imported
```

注意 `mcp_tool.py` 被显式排除——MCP 工具是运行时通过网络发现的，不是模块级常量；它有自己的 `discover_mcp_tools()` 入口。

### 4.3 generation 计数 + TTL 缓存的两级失效

> **为什么值得看**：解决"每 turn 都要重算工具表"的性能问题，又不引入 cache invalidation 的痛苦。
> 上层（`get_tool_definitions`）按 `_generation` 锁全表，下层（`get_definitions`）按 `check_fn` 30s TTL 锁 env-probe。
> MCP 动态刷新只需要 `+= 1` 计数器，所有上游缓存自动失效——不需要 publish/subscribe。

`tools/registry.py:226-279`：
```python
def register(self, name, toolset, schema, handler, check_fn=None, ...):
    with self._lock:
        existing = self._tools.get(name)
        if existing and existing.toolset != toolset:
            both_mcp = existing.toolset.startswith("mcp-") and toolset.startswith("mcp-")
            if not both_mcp:
                logger.error("Tool registration REJECTED: '%s' would shadow ...", name)
                return                       # ← 拒绝插件/MCP 抢内置
        self._tools[name] = ToolEntry(name=name, toolset=toolset, schema=schema, handler=handler, ...)
        if check_fn and toolset not in self._toolset_checks:
            self._toolset_checks[toolset] = check_fn
        self._generation += 1                # ← 唯一的失效信号源
```

`model_tools.py:297-319`（caller 侧）：
```python
if quiet_mode:
    cfg_path = get_config_path()
    cfg_stat = cfg_path.stat()
    cfg_fp = (cfg_stat.st_mtime_ns, cfg_stat.st_size)
    cache_key = (
        frozenset(enabled_toolsets) if enabled_toolsets is not None else None,
        frozenset(disabled_toolsets) if disabled_toolsets else None,
        registry._generation,             # ← 自动捕获 register/deregister/MCP refresh
        cfg_fp,                            # ← 自动捕获 config 文件外部编辑
    )
    cached = _tool_defs_cache.get(cache_key)
    if cached is not None:
        return list(cached)               # ← 注意是 shallow copy
```

### 4.4 dispatch 的 sync/async 桥接 + 异常墙

> **为什么值得看**：这是"工具失败永不导致 agent 崩溃"的兜底。任何 handler 抛任何异常，最终都被翻译成
> `{"error": "Tool execution failed: ..."}` 的 JSON 串——LLM 看到错误描述自己决定下一步。
> 同时它把 async handler 透明地桥到 sync 调用上下文，单点维护异步策略。

`tools/registry.py:347-364`：
```python
def dispatch(self, name: str, args: dict, **kwargs) -> str:
    entry = self.get_entry(name)
    if not entry:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        if entry.is_async:
            from model_tools import _run_async   # lazy: 反向依赖只在调用时触发
            return _run_async(entry.handler(args, **kwargs))
        return entry.handler(args, **kwargs)
    except Exception as e:
        logger.exception("Tool %s dispatch error: %s", name, e)
        return json.dumps({"error": f"Tool execution failed: {type(e).__name__}: {e}"})
```

`_run_async` 自己也是工业级实现：识别"已经在 async 上下文里"则起一次性 worker thread 跑，否则用 thread-local 持久 loop——
专门解决 `asyncio.run()` 反复 create-and-close 导致 cached `httpx.AsyncClient` 在 GC 时报 `Event loop is closed` 的真实生产事故（`model_tools.py:60-173` 的注释把事故链写得非常详细）。

### 4.5 LLM 输入污染的入口处治理：`coerce_tool_args`

> **为什么值得看**：开放权重模型（DeepSeek、Qwen、GLM）输出工具参数时类型经常错乱：数字写成字符串、单元素写成裸值。
> 这段代码不修改工具签名、不重写 schema，而是在调度入口按 schema 推断做安全降级——错了就保留原值，让工具自己报错。

`model_tools.py:540-574`（核心循环）：
```python
for key, value in list(args.items()):
    prop_schema = properties.get(key)
    if not prop_schema: continue
    expected = prop_schema.get("type")

    # array 期望但传来标量：包成单元素列表
    if expected == "array" and value is not None and not isinstance(value, (list, tuple)):
        if isinstance(value, str):
            coerced = _coerce_value(value, expected, schema=prop_schema)  # 先试 JSON 反序列化
            if coerced is not value:
                args[key] = coerced; continue
            args[key] = [value]                                            # 再退化成 wrap
            continue
        args[key] = [value]
        continue

    if not isinstance(value, str): continue
    coerced = _coerce_value(value, expected, schema=prop_schema)
    if coerced is not value:
        args[key] = coerced
```

`_coerce_value` 只对 `"true"/"false"/"42"/"3.14"/"null"` 这类确定模式做转换，转换失败则保持原字符串。

### 4.6 MCP 动态注册：运行时增删工具

> **为什么值得看**：这是 registry 的"运行时可变"特性的真实应用场景。MCP server 启动时发 `tools/list_changed`，
> Hermes 计算 stale set → deregister，然后 in-place re-register 现存工具——避免 nuke-and-repave 期间正在 dispatch
> 的 tool_call 引用到失效的 handler。

`tools/mcp_tool.py:1066-1094`：
```python
async with self._refresh_lock:
    old_tool_names = set(self._registered_tool_names)
    async with self._rpc_lock:
        tools_result = await self.session.list_tools()
    new_mcp_tools = tools_result.tools

    # 只删现已不存在的，不删现存的——避免 in-flight tool_call 失效
    stale_tool_names = old_tool_names - {
        f"mcp_{sanitize_mcp_name_component(self.name)}_"
        f"{sanitize_mcp_name_component(tool.name)}"
        for tool in new_mcp_tools
    }
    for tool_name in stale_tool_names:
        registry.deregister(tool_name)

    self._tools = new_mcp_tools
    self._registered_tool_names = _register_server_tools(self.name, self, self._config)
```

工具命名通过 `sanitize_mcp_name_component()` 把非 `[A-Za-z0-9_]` 字符全部替换成 `_`，前缀 `mcp_<server>_<tool>`——
保证不和内置工具名冲突，也满足各 provider 对 tool name 的字符集校验。

### 4.7 toolset：分组 + 编排 + 跨平台共享

> **为什么值得看**：toolset 不是简单分类，而是一个**可组合的代数**——`includes` 让 toolset 之间继承；`_HERMES_CORE_TOOLS`
> 这种共享列表让所有 messaging 平台（Telegram/Discord/Slack/Feishu/Yuanbao/...）共享同一组核心工具，编辑一处即同步全部。
> 这是 Hermes 跨 ~20 个 messaging 平台仍能保持一致行为的关键。

`toolsets.py:31-68` 中央列表（节选）：
```python
_HERMES_CORE_TOOLS = [
    "web_search", "web_extract",
    "terminal", "process",
    "read_file", "write_file", "patch", "search_files",
    "vision_analyze", "image_generate",
    "skills_list", "skill_view", "skill_manage",
    "browser_navigate", ...,
    "todo", "memory",
    "session_search", "clarify",
    "execute_code", "delegate_task",
    "cronjob",
    "send_message",
    ...
]
```

`toolsets.py:563-634` 递归解析 + 环检测 + 钻石依赖：
```python
def resolve_toolset(name, visited=None):
    if visited is None: visited = set()
    if name in {"all", "*"}:
        all_tools = set()
        for ts_name in get_toolset_names():
            all_tools.update(resolve_toolset(ts_name, visited.copy()))  # 每分支独立 visited
        return sorted(all_tools)
    if name in visited: return []                                       # 环/钻石静默退出
    visited.add(name)
    toolset = get_toolset(name)
    if not toolset:
        if name.startswith("hermes-"):                                   # plugin platform 自动生成
            ...
        return []
    tools = set(toolset.get("tools", []))
    for included_name in toolset.get("includes", []):
        tools.update(resolve_toolset(included_name, visited))           # 共享 visited 避免重算
    return sorted(tools)
```

---

## 5. 与其他维度的交互

| 方向 | 维度 | 交互内容 | 代码中的交互点 |
|---|---|---|---|
| → 编排循环 | 维度 1 | 提供唯一 sync 调用入口 `handle_function_call`，统一返回 JSON 字符串；agent loop 拦截 `_AGENT_LOOP_TOOLS` 自行处理 | `run_agent.py:10440-10470`、`model_tools.py:495,679-818` |
| → 子 Agent 编排 | 维度 11 | `delegate_task` 注册在 `delegation` toolset；handler 接收 `parent_agent` 上下文经 `**kw` 透传 | `tools/delegate_tool.py:2580-2597` |
| → 上下文管理 | 维度 4 | `entry.max_result_size_chars` 控制单次工具结果上下文占用；`get_max_result_size` 查询；`registry.get_emoji` 用于事件渲染 | `tools/registry.py:370-401` |
| → Prompt 构建 | 维度 5 | `get_tool_definitions(enabled, disabled)` 输出 OpenAI 格式 schema 列表，进入 chat completion 的 `tools` 参数 | `model_tools.py:271-332` |
| → 输出解析 | 维度 6 | `coerce_tool_args` 修补开放权重模型输出的类型漂移；`schema_sanitizer` 修补 schema 让模型语法生成器能消费 | `model_tools.py:503-676`、`tools/schema_sanitizer.py` |
| → 状态管理 | 维度 7 | `task_id`、`session_id`、`tool_call_id` 通过 `**kwargs` 透传给 handler；handler 自行用其做隔离（terminal/browser session） | `model_tools.py:756-770` |
| → 错误处理 | 维度 8 | `registry.dispatch` 层吃掉所有异常返回 JSON error；`handle_function_call` 再外包一层兜底 | `tools/registry.py:357-364`、`model_tools.py:815-818` |
| → 安全防护 | 维度 9 | `pre_tool_call` hook 可阻断（plugin），返回 block message；`requires_env` 标注敏感凭证；`check_fn` 在 env 缺失时让工具不可见 | `model_tools.py:722-737`、`tools/registry.py:118-133` |
| → 验证循环 | 维度 10 | `notify_other_tool_call(task_id)` 重置 read-loop 计数（任何非 read/search 调用都触发） | `model_tools.py:741-746` |
| → 初始化与环境 | 维度 12 | `discover_builtin_tools` + `discover_plugins` 在 `model_tools` import 时一次性完成；MCP 在各入口（gateway/cli/tui/acp）显式触发以避免 event loop 阻塞 | `model_tools.py:180-200`、`tools/registry.py:57-74` |
| ← MCP/Plugin | 维度 12 | 插件用 `PluginContext.register_tool` 反向 delegate 到 `registry.register`；MCP server `tools/list_changed` 触发 `_refresh_tools` | `hermes_cli/plugins.py:259-272`、`tools/mcp_tool.py:1056-1094` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 设计假设

1. **工具数量在百量级**：注册表全用 dict，无索引、无分片；`get_definitions` 是 O(N)。如果到了万级会成为瓶颈。
2. **handler 永远返回 str（JSON 序列化的）**：tool_error/tool_result 强制约束。LLM 上下文里也是字符串，保持一致性。
3. **同名工具不允许跨 toolset 存在**（除非两个都是 `mcp-*`）：插件不能"覆盖"内置工具，只能"新增"。
4. **`check_fn` 是廉价的或可缓存的**：30s TTL 是默认；如果某个 check_fn 自身抛异常，被静默当成 unavailable。
5. **`_generation` 单调递增足够标识表状态**：不区分"哪个工具变了"，整表失效。
6. **agent loop 知道哪些工具需要它接管**（`_AGENT_LOOP_TOOLS` 硬编码）：而不是工具自己声明 "needs_agent_state"。

### 6.2 代价 / 风险

- **enabled_toolsets / disabled_toolsets 共用 `_LEGACY_TOOLSET_MAP` 兼容老名字**（`model_tools.py:220-243`）：维护两套命名是历史负债，新增 toolset 容易漏对齐。
- **execute_code/discord/browser_navigate 的 schema 重建写死在 `_compute_tool_definitions` 中**：注释里也承认这是"看其他工具脸色"的耦合，每加一个就要改 model_tools.py，违背"工具自己声明自己"的清洁性。
- **`_run_async` 在 gateway 这种"已经在 event loop 里"的环境会启 short-lived worker thread**，并 `pool.shutdown(wait=False)`。注释明确说"超时后我们已经请求 cancel，工人会在下一个 await 退出"——但若工具 handler 死循环不让出，线程其实会泄漏。
- **`coerce_tool_args` 的"包标量为 list"**：能掩盖模型真实 bug，让训练时收不到坏样本反馈；要做模型评估时需要关掉这一层。
- **AST 扫描静态识别 `registry.register`**：要求文件能被 Python 解析（语法错误的文件直接被忽略），但坏处是不易调试——一个 import 失败的工具，只在 `discover_builtin_tools` 里 logger.warning 一行。
- **schema 缓存把 dict 是按引用共享的**（`return list(cached)` 只浅拷贝）：作者已经在 issue #17335 里踩过 run_agent 改 schema 列表污染缓存的坑，注释解释得很清楚。这说明这层 cache 的语义边界其实很微妙。

### 6.3 如果要重新设计可能改变什么

- **把"可观察"和"可执行"分两层接口**：现在 schema、handler、metadata 全揉在 `ToolEntry`；可考虑分离 `ToolSpec`（纯数据，可序列化）和 `ToolBinding`（带 handler 的运行时态），让 schema 可以独立做 hash/对比/版本管理。
- **change-event bus 替代 generation 计数**：现在所有上层 cache 都得去 poll `_generation`；可以暴露 `on_change(callback)`，订阅者主动失效，避免 caller 必须知道这个内部字段。
- **dynamic schema 让工具自己声明依赖**：把 execute_code、discord、browser_navigate 那些"看其他工具脸色"的逻辑变成 `entry.dynamic_schema_fn(available_names)`，让 model_tools 不需要列举哪些工具是动态的。
- **强类型 args 取代 dict**：Pydantic schema 自动生成 JSON Schema + 解码，能把 `coerce_tool_args` 的体力活让出来，handler 直接拿到 typed model。
- **考虑用 AST 装饰器**或 `@registry.tool(...)` 装饰器代替 `registry.register(...)` 调用，让"哪个函数是工具"在源码里更显眼（当前是看一行最末的 register 调用）；权衡是会引入装饰器的隐式性。
- **MCP 工具刷新引入版本号**：现在 in-place 替换 + stale set，但 in-flight tool_call 的 handler 引用其实可能是旧 closure。给每个 entry 一个 version、dispatch 时校验，能更精确诊断 race。

### 6.4 对自己设计 Agent 系统的启示

1. **registry 是 agent 系统的 "OS 内核"**：把"工具"当作可加载内核模块，每个工具自带元数据 + handler + 可用性探测，dispatch 走单一受信入口。
2. **import side-effect 自注册 + AST 兜底发现**：是个非常实用的折中——不要装饰器魔法，不要中央目录，但允许"忘了 import"。
3. **失效模型用单调计数器是性价比之王**：调用方 `key = (..., generation)`，写方 `_generation += 1`，没有显式订阅、没有线程安全负担。
4. **入口处治理 LLM 输出污染**：与其在每个工具里做 `int(args["x"])` 防御，不如在 dispatcher 一处按 schema 安全降级；这把"模型不守规矩"和"工具实现"解耦。
5. **一致的 JSON-string 返回值**：把所有工具结果归一成 JSON 串，agent loop 不需要 type dispatch；异常也是 `{"error": ...}` 同形——LLM 读到的是同一种"工具自我汇报"语言。
6. **toolset 是 LLM 注意力预算管理的最小单位**：不是"用户能看到几百个工具"，而是"按场景注入十几个最相关的"，配合 `enabled/disabled` 在不同部署形态（CLI/Discord/cron/ACP）裁剪。
7. **cache + TTL + generation 三层组合**：单层都不够（caller 看不见 env 变化、registry 看不见 caller 失效需求）；组合起来可以同时满足"多 caller 复用"和"环境漂移自愈"。
8. **Hook 协议要先于实现存在**：`pre_tool_call`（可阻断）/`post_tool_call`（observational）/`transform_tool_result`（first-wins）三套语义清晰的 hook 是后来 plugin 生态能扩张的前提。
9. **接受性能与魔法的取舍**：作者主动在注释里写明"30s TTL 会让 docker 启动后最长 30s 才被识别"——把权衡显式化，比偷偷优化得能让维护者放心。
