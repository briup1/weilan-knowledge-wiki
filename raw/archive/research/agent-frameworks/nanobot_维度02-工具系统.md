# 维度名：工具系统（Tool System）

## 1. 一句话定位

工具系统是 Agent 与外部世界交互的**唯一执行通道**——把 LLM 输出的"函数调用意图"转化成"对文件、Shell、网络、调度器的真实副作用"，并以统一的 `Tool` 抽象 + `ToolRegistry` 调度，把"参数转换/校验/执行/错误恢复"四步压缩成一行 `await registry.execute(name, params)`。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有这个统一的工具系统抽象层，nanobot 会出现以下具体故障：

1. **LLM 参数错误直接炸到运行时**。LLM 经常把 `offset=1` 输出成 `"1"`、把 `replace_all=true` 输出成 `"true"`。如果没有 `base.py:55-122` 的 `cast_params()`，`ReadFileTool.execute(offset="1")` 会在 `min(start + (limit or self._DEFAULT_LIMIT), total)` 处抛 `TypeError`，回到 `loop.py` 后中断整个迭代。
2. **每个工具自己写错误处理 → 错误格式不一致 → LLM 无法学习恢复**。`registry.py:38-59` 用一个 `_HINT = "\n\n[Analyze the error above and try a different approach.]"` 把所有错误统一加尾巴；如果让每个工具自己 try/except，LLM 在不同工具下面会看到不同形态的错误（`"FileNotFoundError"` vs `"Errno 2"` vs `"Path not found"`），无法形成稳定的"错误 → 修正"模式。
3. **MCP 与原生工具无法共存**。`mcp.py:14-71` 的 `MCPToolWrapper` 也继承 `Tool`，意味着 Registry 不需要知道工具的来源（内置/MCP/插件），只看接口。如果没有 `Tool` ABC，Registry 就要为每种来源开一个分支。
4. **LLM 的 function-call schema 与工具实际签名漂移**。`base.py:172-181` 的 `to_schema()` 直接从 `parameters` 属性派生 OpenAI 格式，保证"暴露给 LLM 的 schema"和"运行时校验的 schema"是同一份数据，不会出现 LLM 看到的字段和实际验证的字段不一致的情况。

### 2.2 nanobot 的具体触发条件

工具系统在两个时刻被激活：

- **构建 `tools` 参数给 LLM**：`registry.py:34-36` 的 `get_definitions()` 把所有注册工具转成 OpenAI `functions` 数组，在 `loop.py` 中传给 Provider。
- **LLM 返回 `tool_calls` 后**：`registry.py:38-59` 的 `execute()` 被调用，按名字查工具 → cast → validate → execute → 错误注入 → 返回字符串结果。

注册时机由 `loop.py:117-134` 的 `_register_default_tools()` 决定：内置工具在 `AgentLoop.__init__` 后立即注册；MCP 工具是**懒加载**的，在第一次进入循环时通过 `_connect_mcp()`（`loop.py:136-`）注入。

---

## 3. 核心设计思路

### 3.1 抽象模型

整个工具系统是一个**"四元组接口 + 字典调度器 + Schema 自描述"** 模型：

```
Tool（ABC）
  ├── name          # str    →  function call 中的 key
  ├── description   # str    →  给 LLM 看的说明
  ├── parameters    # dict   →  JSON Schema, 同时承担三个职责：
  │                              ① 暴露给 LLM 作为函数签名
  │                              ② 运行时类型转换的依据
  │                              ③ 运行时校验的依据
  └── execute(**kwargs) -> str  # 唯一副作用入口

ToolRegistry
  ├── _tools: dict[str, Tool]   # 简单字典，O(1) 查名
  └── execute(name, params):
        tool = _tools[name]
        params = tool.cast_params(params)        # ① 容忍 LLM 类型乱来
        errs = tool.validate_params(params)       # ② 校验后给 LLM 反馈
        if errs: return "Error: ..." + _HINT
        result = await tool.execute(**params)     # ③ 实际执行
        if result.startswith("Error"): + _HINT    # ④ 出错也走同样格式
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **抽象基类用 ABC** | `class Tool(ABC)` + `@abstractmethod` 强制子类实现 4 个属性/方法（`base.py:7-53`） | dataclass / Protocol / TypedDict | ABC 在**构造时**就报错（实例化未实现的子类会 `TypeError`），而 Protocol 是"鸭子类型"运行时才暴露问题；同时 ABC 让 `cast_params/validate_params/to_schema` 可以放在基类里被所有工具共享，而 Protocol 不能携带方法实现。 |
| **自己实现 Schema 校验** | `base.py:124-170` 手写约 50 行 `_validate()`，只覆盖 `type / enum / minimum / maximum / minLength / maxLength / required / items / properties` | jsonschema 库 / pydantic | 看 `_validate` 的覆盖面：**只支持 LLM 实际会出错的子集**——LLM 不会输出 `oneOf/anyOf/format/pattern`，不需要支持。pydantic 还会引入"模型类与 schema 字典不同步"的问题（你得维护两份）。手写让"暴露给 LLM 的 schema"和"运行时校验"始终是同一个 dict。代价仅 ~50 行。 |
| **Registry 是 `dict[str, Tool]`** | `registry.py:15-16` 一行字典定义 | trie / 版本化注册表 / 命名空间路由器 | 工具数量级是十几个（内置 8 个 + MCP 几个），O(1) 字典完全够用。复杂结构会引入"按 namespace 查找"等 LLM 根本用不上的能力——LLM 只会拿到一个扁平名字列表。 |
| **`cast_params` 在 `validate_params` 之前** | `registry.py:48-51` 显式两步：先转再验 | 一步合并 / 不做 cast 直接验 | LLM 输出的参数有 90% 的"错误"是类型问题（数字传成字符串、布尔传成 `"true"`），先 cast 能把这些"伪错误"消化掉，剩下的才是真错误。如果直接 validate，会把 `"1"` 当成非法的 integer 拒绝，迫使 LLM 多走一轮，浪费 token。 |
| **工具执行结果统一返回 `str`** | `Tool.execute(**kwargs) -> str`（`base.py:42-53`） | 返回结构化对象 / 多种返回类型 | LLM 的 tool_result 协议本来就只接受字符串。返回 str 让所有工具（包括 web_fetch 这种本来产 JSON 的）都自己负责"序列化成 LLM 能读的文本"——见 `web.py:272-276` 自己包了 `json.dumps`。 |
| **错误以字符串而非异常返回** | `registry.py:55-57` 检测 `result.startswith("Error")` 来追加 `_HINT` | raise + 上层 catch | 异常会破坏迭代循环——主循环 `loop.py` 不会因为某个 tool 失败而断；返回字符串 + 前缀约定让"错误"也是 LLM 可以读、可以学的"信息"。同时 `registry.py:58-59` 的兜底 `except Exception` 把"工具自身也炸了"的情况也转成同形态字符串。 |
| **`_HINT` 后缀** | 固定文案 `"\n\n[Analyze the error above and try a different approach.]"`（`registry.py:40`） | 不加任何提示 / 让 LLM 自由发挥 | LLM 看到错误后默认行为可能是"再试一次同样的调用"。一句明确的"换个思路"提示能显著降低无意义重试。 |

### 3.3 数据流/控制流

```
LLM 响应 (tool_calls)
    │
    ▼
[loop.py] for tc in tool_calls:
    │
    ▼
registry.execute(tc.name, tc.params)
    │
    ├─── _tools.get(name) → 不存在则 "Error: Tool 'X' not found. Available: ..." 返回（暗中也是给 LLM 的下次提示）
    │
    ├─── tool.cast_params(params)       # base.py:55, 类型纠偏
    │       └── 递归走 schema，只对"安全"转换做（str→int 仅当能 parse；str→bool 仅"true/false/yes/no/1/0"）
    │
    ├─── tool.validate_params(params)   # base.py:124, 类型/范围/必填校验
    │       └── 返回错误列表；非空则拼 "Error: ... " + _HINT 直接返回（不进 execute）
    │
    ├─── await tool.execute(**params)   # 真实副作用
    │
    └─── result.startswith("Error") ? + _HINT : 原样返回
            │
            ▼
       loop.py 把结果作为 tool_result 写回上下文，进入下一轮迭代
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：Schema 即"三合一"接口约定

**作用**：`parameters` 属性同时承担 LLM 函数签名、运行时类型转换、运行时校验三个角色，避免出现"暴露给 LLM 的 schema"与"实际接受的参数"漂移。

**设计意图**：常见的替代是用 pydantic 模型描述参数（运行时验证），再单独写一个 dict 给 LLM（schema）。这两份会不同步——加字段时只改了模型忘了改 schema，结果 LLM 不知道这个字段。把 schema 当**单一数据源**，强迫所有派生（LLM 暴露 / 校验 / 转换）走同一份 dict。

**关键源码**（`nanobot/agent/tools/base.py:172-181`）：
```python
def to_schema(self) -> dict[str, Any]:
    """Convert tool to OpenAI function schema format."""
    return {
        "type": "function",
        "function": {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,   # ← 直接复用，不复制不重构
        },
    }
```
对比 `validate_params`（`base.py:124-131`）：
```python
def validate_params(self, params: dict[str, Any]) -> list[str]:
    schema = self.parameters or {}
    if schema.get("type", "object") != "object":
        raise ValueError(...)
    return self._validate(params, {**schema, "type": "object"}, "")
```
注意两个方法都直接读 `self.parameters`——同一份 dict，零冗余。

---

### 机制 B：Schema 驱动的"宽容型"类型转换（cast_params）

**作用**：在校验之前先做一次安全的类型转换，吸收 LLM 输出的"类型噪声"。

**设计意图**：LLM 在 function calling 中经常把 `1` 输出成 `"1"`、把 `true` 输出成 `"true"`。直接验证会拒绝这些参数，迫使 LLM 重试，浪费一轮 token 和延迟。但**不能**做激进转换（如把 `"hello"` 转成 0），那样会把语义错的参数掩盖成语义错的执行。

**关键源码**（`nanobot/agent/tools/base.py:79-122`）：
```python
def _cast_value(self, val: Any, schema: dict[str, Any]) -> Any:
    target_type = schema.get("type")

    # ① 类型已对，直接返回——零开销快路径
    if target_type == "boolean" and isinstance(val, bool):
        return val
    if target_type == "integer" and isinstance(val, int) and not isinstance(val, bool):
        return val
    # 注意：bool 是 int 的子类，所以这里要 not isinstance(val, bool) 排除掉

    # ② 字符串 → 整数：仅当能 parse 才转，parse 失败保持原值（让 validate 报错）
    if target_type == "integer" and isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return val   # ← 故意不抛，留给 validate 给出"类型应为 integer"的标准错误

    # ③ 字符串 → bool：只接受白名单字面量
    if target_type == "boolean" and isinstance(val, str):
        val_lower = val.lower()
        if val_lower in ("true", "1", "yes"): return True
        if val_lower in ("false", "0", "no"): return False
        return val   # ← 其他字符串原样返回，让 validate 拒绝

    # ④ array/object 递归
    if target_type == "object" and isinstance(val, dict):
        return self._cast_object(val, schema)
    return val
```

**为什么这样设计**：每个 cast 分支都是"能转则转、不能转保留"——绝不抛异常、绝不"猜"。这样 cast 失败时，validate 仍会给出标准错误信息（"X should be integer"），LLM 看到的错误形态稳定。

---

### 机制 C：JSON Schema 子集校验（validate_params）

**作用**：拒绝类型错、范围错、缺字段的参数，并在错误信息中包含字段路径，方便 LLM 定位。

**设计意图**：完整的 JSON Schema 标准有几十种关键字（`oneOf/anyOf/not/format/pattern/dependencies/...`）。引入 `jsonschema` 库会带来 ~MB 级依赖、未知错误信息格式、且 90% 的关键字 LLM 永远用不上。手写 50 行覆盖**实际场景**——`type/enum/minimum/maximum/minLength/maxLength/required/properties/items`——足以拦住所有 LLM 出错的情况。

**关键源码**（`nanobot/agent/tools/base.py:133-170`）：
```python
def _validate(self, val: Any, schema: dict[str, Any], path: str) -> list[str]:
    t, label = schema.get("type"), path or "parameter"
    # ① 类型校验。注意 bool/int 的特判（bool 是 int 子类，需排除）
    if t == "integer" and (not isinstance(val, int) or isinstance(val, bool)):
        return [f"{label} should be integer"]
    if t == "number" and (not isinstance(val, self._TYPE_MAP[t]) or isinstance(val, bool)):
        return [f"{label} should be number"]
    if t in self._TYPE_MAP and t not in ("integer", "number") and not isinstance(val, self._TYPE_MAP[t]):
        return [f"{label} should be {t}"]

    errors = []
    # ② enum / 范围 / 长度 — 只在类型对后才检查（短路）
    if "enum" in schema and val not in schema["enum"]:
        errors.append(f"{label} must be one of {schema['enum']}")
    if t in ("integer", "number"):
        if "minimum" in schema and val < schema["minimum"]: errors.append(...)
        if "maximum" in schema and val > schema["maximum"]: errors.append(...)
    # ③ 对象：必填 + 递归校验属性
    if t == "object":
        for k in schema.get("required", []):
            if k not in val:
                errors.append(f"missing required {path + '.' + k if path else k}")
        for k, v in val.items():
            if k in props:
                errors.extend(self._validate(v, props[k], path + "." + k if path else k))
    # ④ 数组：递归每个 item，错误带索引（"items[3].name should be string"）
    return errors
```

**值得注意的两个细节**：
- `bool` 是 `int` 的子类，Python 里 `isinstance(True, int)` 是 `True`。如果不显式排除，schema 写 `integer` 时 LLM 传 `true` 会被错误接受。`base.py:135, 138` 两处的 `isinstance(val, bool)` 检查就是为了这个。
- 错误消息里带路径（`label = path or "parameter"`），让 LLM 在嵌套 object/array 中也能精准定位是哪个字段错了。

---

### 机制 D：Registry 的统一执行入口 + 错误"路标化"

**作用**：把"找工具、转参数、验参数、执行、捕获异常、加提示"压成一行 `await registry.execute(name, params)`，主循环不需要任何条件分支。

**设计意图**：如果让主循环自己处理这些步骤，每加一个工具都要改主循环；如果让每个工具自己处理 cast/validate，会有 8 份重复代码。同时统一的错误格式让 LLM 在所有工具上看到的错误都"长得像"，能形成稳定的恢复策略。

**关键源码**（`nanobot/agent/tools/registry.py:38-59`）：
```python
async def execute(self, name: str, params: dict[str, Any]) -> str:
    _HINT = "\n\n[Analyze the error above and try a different approach.]"

    # ① 工具不存在：不抛异常，返回字符串（同时告诉 LLM 可用列表，引导自我纠正）
    tool = self._tools.get(name)
    if not tool:
        return f"Error: Tool '{name}' not found. Available: {', '.join(self.tool_names)}"

    try:
        # ② cast 在 validate 之前——吸收 90% 的"伪错误"
        params = tool.cast_params(params)
        errors = tool.validate_params(params)
        if errors:
            return f"Error: Invalid parameters for tool '{name}': " + "; ".join(errors) + _HINT
        result = await tool.execute(**params)
        # ③ 工具自己以字符串约定返回错误（如 ReadFileTool 的 "Error: File not found"），
        #    Registry 检测前缀给加 _HINT。这样工具不需要 import _HINT，约定即接口
        if isinstance(result, str) and result.startswith("Error"):
            return result + _HINT
        return result
    except Exception as e:
        # ④ 工具自身崩了也兜住——LLM 看到的依然是同形态字符串
        return f"Error executing {name}: {str(e)}" + _HINT
```

**几个值得品味的设计选择**：
- `tool not found` 时**列出所有可用工具**——这是给 LLM 的隐式 schema 提示，能在 LLM 误打名字时自我纠正（比如把 `read` 拼成 `read_file`）。
- 工具自己用字符串前缀 `"Error"` 约定错误，而非 raise——`filesystem.py:98` `return f"Error: File not found: {path}"`。这是**协议约定**而非类型约束，避免每个工具都 import `_HINT` 常量。
- 最外层 `except Exception` 是**最后的兜底**：哪怕工具实现里有未捕获的 bug，主循环也不会断。

---

### 机制 E：工具携带"执行上下文"的两种范式

**作用**：有些工具需要知道"当前是谁在调用"——比如 `MessageTool` 要知道往哪个 channel/chat 发消息，`SpawnTool` 要把上下文传给子 agent，`CronTool` 要记录调度归属。

**设计意图**：参数 schema 里**不能**让 LLM 自己填 channel/chat_id（LLM 不应该知道也不该决定它在哪个会话里——这是安全边界）。所以这些信息要**带外注入**，而不是通过参数。

**关键源码**——`MessageTool` 的注入式上下文（`nanobot/agent/tools/message.py:25-29`）：
```python
def set_context(self, channel: str, chat_id: str, message_id: str | None = None) -> None:
    """Set the current message context."""
    self._default_channel = channel
    self._default_chat_id = chat_id
    self._default_message_id = message_id
```
主循环每处理一条消息前会调用 `set_context`。LLM 调用时即使不传 `channel/chat_id`，工具也能默认发回原会话——见 `message.py:82-83`：
```python
channel = channel or self._default_channel
chat_id = chat_id or self._default_chat_id
```

**对比 `CronTool` 的 ContextVar 范式**（`nanobot/agent/tools/cron.py:18, 25-31`）：
```python
self._in_cron_context: ContextVar[bool] = ContextVar("cron_in_context", default=False)

def set_cron_context(self, active: bool):
    return self._in_cron_context.set(active)
```
CronTool 用 `ContextVar` 而不是普通属性，是因为要在**任务执行回调内**判断"是否正在 cron 触发的执行中"——属性会被并发污染，`ContextVar` 自动随 task 切换隔离。这一笔保证了 LLM 在 cron 触发的回调里**不能再次创建 cron**（`cron.py:85-86`：避免无限递归）。

---

### 机制 F：MCP 工具的统一适配

**作用**：把外部 MCP 服务器提供的工具，包装成与原生 Tool 完全一样的接口，让 Registry 不区分来源。

**设计意图**：如果 MCP 是 Registry 的特殊分支，每加一种外部协议（OpenAPI、gRPC...）都要改 Registry。让 `MCPToolWrapper` 也继承 `Tool`，Registry 永远只看到 `Tool`。

**关键源码**（`nanobot/agent/tools/mcp.py:14-22`）：
```python
class MCPToolWrapper(Tool):
    def __init__(self, session, server_name: str, tool_def, tool_timeout: int = 30):
        self._session = session
        self._original_name = tool_def.name
        self._name = f"mcp_{server_name}_{tool_def.name}"  # ← 命名空间隔离，防冲突
        self._description = tool_def.description or tool_def.name
        # ↓ 直接借用 MCP 服务端发布的 inputSchema 作为我们的 parameters
        self._parameters = tool_def.inputSchema or {"type": "object", "properties": {}}
        self._tool_timeout = tool_timeout
```
**两个关键妥协**：
1. **强加 `mcp_<server>_<tool>` 前缀**——MCP 服务可能发布与原生工具同名的工具（比如两个 MCP 服务器都有 `search`），这个前缀是命名空间隔离的最简方案。
2. **直接复用 MCP 的 inputSchema**——意味着 nanobot 的 `validate_params` 现在要校验**外部定义的 schema**。这是 `validate_params` 必须只支持"通用子集"的另一个原因——MCP 服务器可能发布带 `oneOf` 的 schema，nanobot 直接忽略未识别的关键字（`_validate` 中没匹配的关键字会自然跳过），保证不会因为 schema 太复杂而拒绝合法参数。

**关键源码续**——异常处理特别小心（`mcp.py:48-55`）：
```python
except asyncio.CancelledError:
    # MCP SDK's anyio cancel scopes can leak CancelledError on timeout/failure.
    # Re-raise only if our task was externally cancelled (e.g. /stop).
    task = asyncio.current_task()
    if task is not None and task.cancelling() > 0:
        raise
    logger.warning("MCP tool '{}' was cancelled by server/SDK", self._name)
    return "(MCP tool call was cancelled)"
```
这是从踩坑得出的经验：MCP SDK 内部用 `anyio` 的 cancel scope，会"泄漏" `CancelledError`，但这不是真的 `/stop`。用 `task.cancelling() > 0` 区分"用户主动取消"和"SDK 内部取消"，仅前者重新抛出。

---

## 5. 与其他维度的交互

```
                   ┌─────────────────────────┐
                   │   编排循环 (Loop)        │
                   └────┬────────────┬───────┘
                        │            │
        get_definitions │            │ execute(name, params)
              ▼            ▼
       ┌──────────────────────────────┐
       │   工具系统 (Tool System)      │
       │   - Tool ABC                  │
       │   - ToolRegistry              │
       │   - cast/validate/_HINT       │
       └──────────────────────────────┘
        ▲    ▲    ▲    ▲    ▲    ▲
        │    │    │    │    │    │
   FS  Shell Web Spawn Msg Cron  MCP
        │              │    │    │
        ▼              ▼    ▼    ▼
   [安全防护]      [子Agent] [Bus] [外部MCP服务]
   网络/路径校验
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|---------------------------|
| 输出到 | 编排循环 | 工具列表（OpenAI function 格式） | `registry.get_definitions()` 在 `loop.py` 中传给 Provider |
| 输入自 | 编排循环 | LLM 选择的工具名 + 参数字典 | `registry.execute(name, params)` 在 `loop.py` 处理 tool_calls 时调用 |
| 依赖 | 安全防护 | URL 校验 / 路径校验 / 命令黑名单 | `shell.py:144-176` 调用 `nanobot.security.network.contains_internal_url`；`filesystem.py:21-25` 的 `allowed_dir` 边界 |
| 注入到 | 子 Agent 编排 | SpawnTool 是主→子的入口 | `spawn.py:55-63` 调用 `SubagentManager.spawn()` |
| 注入到 | 状态管理 | MessageTool 用 Bus 推送出站消息 | `message.py:103` `await self._send_callback(msg)`，回调是 `bus.publish_outbound` |
| 注入到 | 定时任务 | CronTool 增删查 cron 任务 | `cron.py:135-143` 调用 `CronService.add_job` |
| 适配自 | 外部 MCP | 把 MCP 协议工具包成统一接口 | `mcp.py:147-162` `registry.register(MCPToolWrapper(...))` |
| 输出到 | 上下文管理 | 工具结果作为 tool_result 写回 history | `loop.py` 拿 `execute()` 返回的字符串，封装为 message 追加上下文 |
| 上下文注入 | 状态管理 | `set_context()` 把当前 channel/chat 注入有状态工具 | `MessageTool/SpawnTool/CronTool` 都暴露 `set_context()` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **LLM 输出的"参数错误"绝大部分是类型问题**。所以 `cast_params` 优先于 `validate_params`，先吸收类型噪声再做严格检查。如果 LLM 输出错误以"语义错误"为主（比如选错工具），这个设计的收益就小很多。
2. **错误信息也是"prompt"**。错误字符串带 `_HINT`、带可用工具列表、带字段路径——作者**把错误当作给 LLM 的隐式指令**，而不是仅给开发者看的诊断信息。
3. **工具数量保持在十几个量级**。`ToolRegistry` 用 `dict` 而非更复杂的索引结构、`get_definitions()` 一次性返回全部工具——意味着假设工具集小到可以全部塞进 system prompt，不需要"按相关性筛选"或"分组激活"。
4. **JSON Schema 的常用子集足以覆盖 LLM 场景**。手写 50 行 `_validate` 不支持 `oneOf/format/pattern`——假设没有 LLM 会主动构造需要这些的参数，且作者写工具 schema 时也不会用到。
5. **同步/异步行为可以用 `async def execute` 统一**。所有工具都是 `async`，即使 `_resolve_path` 是同步的（filesystem 实际是阻塞 I/O）——作者接受了"小文件场景下同步 I/O 的代价"，没有用 `aiofiles`。

### 6.2 这个设计的代价/风险

1. **错误约定靠"以 'Error' 开头的字符串"——脆弱**。`registry.py:55` 用 `result.startswith("Error")` 检测错误，意味着任何工具的合法输出**不能**以 "Error" 开头。如果未来某个工具返回的内容恰好以 "Error" 开头（比如展示一段错误日志的 grep 结果），会被误加 `_HINT`，污染输出。
2. **`validate_params` 不支持 `oneOf/anyOf` 意味着 MCP 工具的部分能力被静默忽略**。MCP 服务器如果发布带这些关键字的 schema，nanobot 的校验会"无条件放过"，可能传错参数到外部服务，让错误在 MCP 服务端才暴露——错误归因变难。
3. **`ContextVar` 与 `set_context`/`set_send_callback` 的混用**让"工具是有状态的"这件事不易看出。新人添加一个工具时容易忘记在 `loop.py` 的 `_register_default_tools` 中调用 `set_context`，导致工具运行时拿到空的 channel。这是隐式契约，没有类型层面的强制。
4. **`cast_params` 的"宽容"可能掩盖配置错误**。LLM 把 `recursive=true` 输出成字符串 `"true"` 是常态——但开发者写测试时如果传 `"yes"`，也会被静默接受，可能掩盖测试用例的拼写错误。
5. **手写校验放弃了 JSON Schema 标准的兼容性收益**。如果未来想把工具 schema 直接喂给一个标准 JSON Schema 工具链（生成文档、生成 SDK 等），这个手写校验和标准 jsonschema 之间的差异需要每次都解释。

### 6.3 如果要重新设计，可能会改变什么

- **错误信号从"前缀字符串"改为结构化** ——比如工具返回 `Tool` 装饰过的字符串子类 `ToolError(str)`，Registry 用 `isinstance` 检测，避免 `startswith("Error")` 这种字符匹配脆弱性。
- **`set_context` 改为构造一次性的执行上下文对象**，作为隐式参数传给 `execute()`（类似 web 框架的 request 对象），而不是改动工具实例的状态——这样工具不再有"会话粘连"问题，并发安全也更明确。
- **MCP 工具的 schema 在注册时检查"未识别关键字"并 warning**，而不是静默接受——避免"参数发出去到服务端才报错"的归因黑洞。
- **`_HINT` 文案应允许工具自己覆盖**——比如 `EditFileTool` 失败时已经在错误消息里给出了 best-match diff（`filesystem.py:283-290`），再加一句 `"try a different approach"` 反而冗余。

### 6.4 对我自己设计 Agent 系统的启示

**最核心的两句话：**

1. **工具的"接口"是给 LLM 的提示工程**。schema/description/error message 不是给开发者看的诊断信息，而是 LLM 推理的输入——错误信息里多一句 `[Analyze the error above and try a different approach.]`、多列一份可用工具名、多带一个字段路径，能直接降低重试轮次。把"工具系统"当成"prompt 系统"来设计，而不是当成 RPC 框架。

2. **抽象层只解决真问题，不预测未来**。`ToolRegistry` 是 70 行的字典、`validate` 是手写 50 行、`Tool` 只有 4 个抽象成员——作者在每个能用更复杂方案（plugin loader、jsonschema、metaclass）的地方都选了**最简单刚好够**的版本。代价是某些场景下需要重构，但收益是任何人在 30 分钟内能读懂整套工具系统并加一个新工具。在 LLM Agent 这种**接口和需求都还在快速变化**的领域，"够用就好"的结构反而比"考虑周到"的框架更容易演化。
