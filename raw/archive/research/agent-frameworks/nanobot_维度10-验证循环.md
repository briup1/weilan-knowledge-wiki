# 维度10：验证循环

## 1. 一句话定位

nanobot 的验证循环是在 LLM 返回的原始 JSON 参数与工具 `execute()` 之间建立的一道"类型防火墙"：先按 Schema 做宽松类型转换（cast），再做严格校验（validate），确保工具收到的参数既符合 Python 原生类型预期，又满足业务约束（范围、必填、枚举）。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有 cast + validate 两道关卡，系统会在三个层面出现故障：

1. **类型不匹配导致 Python 运行时异常**：LLM 输出的参数全是 JSON 字符串（如 `"true"`、`"42"`），而 `execute()` 签名期望的是 `bool` / `int`。以 `EditFileTool.execute()` 为例，其签名为 `execute(self, path: str, old_text: str, new_text: str, replace_all: bool = False, **kwargs)`。若 LLM 返回 `{"replace_all": "true"}`，直接传入会导致 `replace_all` 实际为 `str "true"`，在条件判断 `if not replace_all:` 中永远为真（非空字符串为 True），逻辑完全颠倒。

2. **范围越界导致工具行为失控**：`ExecTool` 的 `timeout` 参数有 `"maximum": 600`，若 LLM 返回 `"timeout": 9999`，直接传入会使 `asyncio.wait_for()` 等待近 3 小时，造成资源长时间占用甚至 DoS。

3. **必填字段缺失导致后续空指针/异常**：`ReadFileTool` 的 `path` 是 `"required": ["path"]`，若 LLM 漏传，直接 `execute(**params)` 会因缺少 `path` 抛出 `TypeError`，这个异常会向上传播，打断整个 Agent 循环。

### 2.2 OpenCode 的具体触发条件

验证循环在每次工具执行前无条件触发，入口在 `ToolRegistry.execute()`：

- 触发条件 1：`tool.cast_params(params)` 在 `registry.py:L48` 被调用——对 LLM 原始参数做类型转换
- 触发条件 2：`tool.validate_params(params)` 在 `registry.py:L51` 被调用——对转换后的参数做约束校验
- 触发条件 3：任一环节失败都会提前返回错误字符串，不会进入 `tool.execute()`（`registry.py:L52-L53`）

---

## 3. 核心设计思路

### 3.1 抽象模型

```
LLM 原始参数 (JSON 值)
       |
       v
  ┌─────────────┐
  │  cast_params │  ← 宽松转换："42"→42, "true"→True, "1.5"→1.5
  │  (类型归一化) │
  └─────────────┘
       |
       v
  ┌─────────────┐
  │ validate_params│  ← 严格校验：类型/必填/范围/枚举/长度
  │  (约束检查)   │
  └─────────────┘
       |
       v
  tool.execute(**params)  ← Python 原生类型，可直接消费
```

这是一个**两阶段管道**：第一阶段负责"兼容性修复"（LLM 经常输出字符串化的数字和布尔值），第二阶段负责"正确性保证"。两个阶段顺序不可交换——必须先 cast 再 validate，原因见 4.1。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 校验顺序 | 先 `cast_params` 再 `validate_params` | 直接对原始 JSON 做 validate | `base.py:L83-L86` 中 bool 是 int 子类需要特判，若先 validate 则 `"true"` 会被判定为非法 string，而 cast 能将其转为 `True` 后再通过 validate；LLM 常输出字符串化数值，直接 validate 会产生大量误报 |
| 校验实现 | 手写轻量 JSON Schema 校验器（~120 行） | 引入 `pydantic` 或 `jsonschema` 库 | 项目追求"超轻量级"（`base.py` 仅 181 行，零外部依赖），手写实现只覆盖 OpenAI function calling 实际用到的 schema 子集（type/required/minimum/maximum/minLength/maxLength/enum/items） |
| Schema 来源 | `parameters` property 与 `to_schema()` 共用同一份 dict | 维护两份 Schema（一份用于校验、一份用于 LLM 暴露） | `base.py:L172-L181` 的 `to_schema()` 直接引用 `self.parameters`，避免两份 Schema 漂移；工具开发者只需写一份 parameters |
| 错误处理 | 返回错误字符串而非抛出异常 | 抛出 `ValidationError` 中断循环 | `registry.py:L52-L53` 将校验错误包装为 `"Error: Invalid parameters..."` 字符串返回给 LLM，让 LLM 在下一轮自行修正参数，保持循环连续性 |

### 3.3 数据流/控制流

```
Agent Loop 收到 tool_call
       |
       v
ToolRegistry.execute(name, params)        [registry.py:L38]
       |
       ├──→ tool.cast_params(params)      [registry.py:L48] → [base.py:L55-L122]
       │         返回 cast 后的 dict
       │
       ├──→ tool.validate_params(params)  [registry.py:L51] → [base.py:L124-L170]
       │         返回 error list（空则通过）
       │
       └──→ await tool.execute(**params)  [registry.py:L54]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：cast_params —— 为什么先 cast 再 validate

**作用**：将 LLM 输出的 JSON 原始值（常是字符串）转换为 Python 原生类型，使后续校验和工具执行都能基于正确的类型进行。

**设计意图**：LLM 的 function calling 输出本质上是一个 JSON object，JSON 没有原生 `int`/`bool` 类型区分——所有值都是 JSON 的 string/number/boolean。但 LLM 有时会输出 `"42"`（字符串）而非 `42`（数字），或 `"true"`（字符串）而非 `true`（布尔）。如果直接 validate，这些合法但类型不精确的值会被判为非法。先 cast 再 validate 相当于给 LLM 一个"容错窗口"。

**关键源码**（`nanobot/agent/tools/base.py:55-122`）：

```python
# L55-62: 入口，只对 object 类型的 schema 做 cast
def cast_params(self, params: dict[str, Any]) -> dict[str, Any]:
    schema = self.parameters or {}
    if schema.get("type", "object") != "object":
        return params
    return self._cast_object(params, schema)

# L79-122: 核心转换逻辑，体现"为什么先 cast"
def _cast_value(self, val: Any, schema: dict[str, Any]) -> Any:
    target_type = schema.get("type")

    # L83-86: bool 是 int 子类，必须先特判 bool 再判 int
    if target_type == "boolean" and isinstance(val, bool):
        return val
    if target_type == "integer" and isinstance(val, int) and not isinstance(val, bool):
        return val

    # L92-96: 字符串→整数转换，LLM 常输出 "42" 而非 42
    if target_type == "integer" and isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return val  # 转换失败保留原值，交给 validate 报错

    # L107-113: 字符串→布尔转换，LLM 可能输出 "true"/"1"/"yes"
    if target_type == "boolean" and isinstance(val, str):
        val_lower = val.lower()
        if val_lower in ("true", "1", "yes"):
            return True
        if val_lower in ("false", "0", "no"):
            return False
        return val
```

这段代码值得细看的三个点：

1. **L83-86 的 bool/int 特判顺序**：Python 中 `bool` 是 `int` 的子类（`isinstance(True, int) == True`）。如果先检查 `isinstance(val, int)`，则 `True` 会被当成整数 `1` 通过，导致 `replace_all=True` 被误 cast 为 `1`。因此必须先判 `bool` 再判 `int`，这是手写校验器必须处理的 Python 语言特性陷阱。

2. **L92-96 的容错设计**：`int("42")` 成功则返回 `42`，失败则保留 `"42"` 让后续 validate 报 `"should be integer"`。这样不会静默吞掉真正的非法值。

3. **L107-113 的语义扩展**：JSON boolean 只有 `true`/`false`，但 LLM 可能输出 `"yes"` 或 `"1"`。cast 层做了语义扩展，比严格的 JSON parse 更宽容。

---

### 机制 B：validate_params —— 手写 Schema 校验的取舍

**作用**：对 cast 后的参数做严格约束检查，包括类型、必填、范围、枚举、字符串长度、数组元素递归校验。

**设计意图**：nanobot 定位为"超轻量级个人 AI 助手"，核心依赖只有 `asyncio`、`httpx`、`loguru` 等基础库。引入 `pydantic` 会增加约 10MB 依赖和复杂的类型元编程；引入 `jsonschema` 会增加一个中等体积的库且其完整 Draft 7 支持对 function calling 场景是过度设计。手写校验器只覆盖实际用到的 schema 关键字，代码可控、行为透明、零额外依赖。

**关键源码**（`nanobot/agent/tools/base.py:124-170`）：

```python
# L124-131: 入口，schema 必须是 object 类型（function calling 的约定）
def validate_params(self, params: dict[str, Any]) -> list[str]:
    if not isinstance(params, dict):
        return [f"parameters must be an object, got {type(params).__name__}"]
    schema = self.parameters or {}
    if schema.get("type", "object") != "object":
        raise ValueError(f"Schema must be object type, got {schema.get('type')!r}")
    return self._validate(params, {**schema, "type": "object"}, "")

# L133-170: 递归校验器，覆盖 type/enum/minimum/maximum/minLength/maxLength/required/items
def _validate(self, val: Any, schema: dict[str, Any], path: str) -> list[str]:
    t, label = schema.get("type"), path or "parameter"
    # L135-140: 再次特判 bool 不是 int/number
    if t == "integer" and (not isinstance(val, int) or isinstance(val, bool)):
        return [f"{label} should be integer"]
    if t == "number" and (not isinstance(val, self._TYPE_MAP[t]) or isinstance(val, bool)):
        return [f"{label} should be number"]
    if t in self._TYPE_MAP and t not in ("integer", "number") and not isinstance(val, self._TYPE_MAP[t]):
        return [f"{label} should be {t}"]

    errors = []
    if "enum" in schema and val not in schema["enum"]:
        errors.append(f"{label} must be one of {schema['enum']}")
    if t in ("integer", "number"):
        if "minimum" in schema and val < schema["minimum"]:
            errors.append(f"{label} must be >= {schema['minimum']}")
        if "maximum" in schema and val > schema["maximum"]:
            errors.append(f"{label} must be <= {schema['maximum']}")
    if t == "string":
        if "minLength" in schema and len(val) < schema["minLength"]:
            errors.append(f"{label} must be at least {schema['minLength']} chars")
        if "maxLength" in schema and len(val) > schema["maxLength"]:
            errors.append(f"{label} must be at most {schema['maxLength']} chars")
    # L157-164: object 类型递归校验 properties + required
    if t == "object":
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in val:
                errors.append(f"missing required {path + '.' + k if path else k}")
        for k, v in val.items():
            if k in props:
                errors.extend(self._validate(v, props[k], path + "." + k if path else k))
    # L165-169: array 类型递归校验 items
    if t == "array" and "items" in schema:
        for i, item in enumerate(val):
            errors.extend(self._validate(item, schema["items"], f"{path}[{i}]" if path else f"[{i}]"))
    return errors
```

这段代码体现了手写校验器的**精确裁剪**：

- 只支持 `type` 为 `string/integer/number/boolean/array/object`（`base.py:L15-22` 的 `_TYPE_MAP`），这是 OpenAI function calling 实际使用的全部类型。
- 只支持 `required`、`minimum`、`maximum`、`minLength`、`maxLength`、`enum`、`items` 七个约束关键字，覆盖了 nanobot 所有内置工具的 parameters 定义（如 `filesystem.py:L75-92` 的 `minimum: 1`、`shell.py:L52-76` 的 `maximum: 600`）。
- 不支持 `anyOf`、`oneOf`、`$ref`、`pattern` 等高级 JSON Schema 特性——这些在 nanobot 的工具定义中从未出现。

---

### 机制 C：to_schema() 与 parameters 共用同一份 dict

**作用**：`to_schema()` 将工具包装为 OpenAI function calling 格式，而 `parameters` property 提供 JSON Schema 定义。两者共享同一份 dict，避免维护两份可能漂移的 Schema。

**设计意图**：如果校验用一份 Schema、LLM 暴露用另一份，开发者修改参数时容易只改一份，导致"LLM 看到的能力"与"实际校验规则"不一致。nanobot 的做法是让 `to_schema()` 直接引用 `self.parameters`，工具开发者只维护一份 `parameters` property。

**关键源码**（`nanobot/agent/tools/base.py:172-181`）：

```python
def to_schema(self) -> dict[str, Any]:
    """Convert tool to OpenAI function schema format."""
    return {
        "type": "function",
        "function": {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,   # ← 直接引用，不是深拷贝
        },
    }
```

对比 `filesystem.py:L75-92` 中 `ReadFileTool.parameters` 的定义：

```python
@property
def parameters(self) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "The file path to read"},
            "offset": {"type": "integer", "minimum": 1, ...},
            "limit": {"type": "integer", "minimum": 1, ...},
        },
        "required": ["path"],
    }
```

这份 dict 同时被三个消费者使用：
1. `cast_params()` 读取 `properties` 做类型转换
2. `validate_params()` 读取 `type`/`required`/`minimum` 做约束检查
3. `to_schema()` 整体嵌入 OpenAI function schema 发给 LLM

---

## 5. 与其他维度的交互

```
[验证循环] --(错误字符串)--> [编排循环]
[验证循环] <--(原始 tool_call 参数)-- [输出解析]
[验证循环] <--(parameters Schema)-- [工具系统]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环 | 校验失败时返回 `"Error: Invalid parameters..."` 字符串，Agent Loop 将其作为 tool result 写入历史 | `registry.py:L52-L53` |
| 依赖 | 输出解析 | 接收 LLM 输出的原始 JSON 参数（`tool_call.function.arguments`） | `loop.py` 中解析响应后调用 `registry.execute(name, params)` |
| 依赖 | 工具系统 | 每个 Tool 子类提供 `parameters` property 作为 Schema 来源 | `filesystem.py:L75-92`、`shell.py:L52-76`、`web.py:L79-86` 等 |
| 输出到 | 错误处理 | 校验错误被捕获并包装为 LLM 可理解的错误提示，而非抛出异常中断循环 | `registry.py:L58-L59` 统一 `except Exception` 兜底 |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **LLM 的参数输出是"大致正确但类型不精确"的**：cast 层的存在假设 LLM 知道该传什么值，但有时会包裹成字符串（如 `"true"` 代替 `true`）。如果 LLM 经常传完全无关的值，cast 层就失去意义。

2. **工具参数 Schema 足够简单，不需要完整的 JSON Schema 引擎**：nanobot 的所有内置工具 parameters 都不涉及 `anyOf`、`$ref`、`pattern` 等复杂特性，手写校验器足以覆盖。

3. **错误应该返回给 LLM 自行修正，而非中断用户会话**：`registry.py:L52-L53` 将校验错误作为字符串返回，假设 LLM 看到 `"Error: Invalid parameters..."` 后能在下一轮调用中修正参数。这比抛出异常终止循环更符合 Agent 的自主迭代哲学。

### 6.2 这个设计的代价/风险

1. **手写校验器的行为与标准 JSON Schema 不完全一致**：例如 `jsonschema` 对 `number` 类型的校验包含 `exclusiveMinimum`/`multipleOf` 等关键字，而 nanobot 的校验器不支持。如果未来有工具需要这些特性，必须扩展 `_validate()`。

2. **`to_schema()` 直接引用 `self.parameters` 存在可变风险**：虽然当前所有 `parameters` 都是每次调用返回新 dict（property），但如果某个子类将 `parameters` 定义为类变量并原地修改，会导致 LLM 看到的 Schema 与校验用的 Schema 同时被污染。`web.py:L79-86` 中 `WebSearchTool` 就使用了类变量 `parameters = {...}`，虽然当前没有修改操作，但这是潜在风险点。

3. **cast 层的容错可能掩盖真正的类型错误**：例如 `"maybe"` 作为 boolean 值，cast 层无法识别（不在 `"true"`/`"false"`/`"1"`/`"0"`/`"yes"`/`"no"` 范围内），会保留原字符串 `"maybe"`，然后在 validate 层报 `"should be boolean"`。这个流程是对的，但如果 cast 层的扩展过于宽松（如把 `"1"` 当 `True`），可能让 LLM 养成不良习惯。

### 6.3 如果要重新设计，可能会改变什么

1. **将 `parameters` 统一为 property 而非类变量**：当前 `filesystem.py` 中所有工具都用 `@property def parameters`，而 `web.py` 中 `WebSearchTool` 使用类变量 `parameters = {...}`。统一为 property 可以避免可变共享状态，也更符合"每个工具实例可能有不同 Schema"的扩展方向（如动态 MCP 工具）。

2. **考虑将 cast + validate 合并为一个返回 `(value, errors)` 的函数**：当前分两步调用，中间状态（cast 后的 params）暴露在 `registry.py:L48-L51`。合并可以减少一次 dict 遍历，但会牺牲清晰度。

3. **对 `enum` 值也做 cast**：当前 `_cast_value()` 不处理 `enum`，如果 LLM 输出 `"markdown"`（已经是 string）则没问题，但如果某个 enum 是整数类型而 LLM 输出字符串 `"1"`，会先通过 cast 转为 `1`，再通过 enum 校验。当前实现已能处理这种情况，但 cast 层没有显式考虑 enum 语义。

### 6.4 对我自己设计 Agent 系统的启示

**最核心的一两句话**：当 LLM 是参数的生产者、Python 函数是消费者时，两者之间必须有一层"类型适配层"——不要假设 LLM 会严格遵守 JSON Schema 的类型系统。nanobot 的做法是"先宽容转换、后严格校验"，这比直接引入重型校验库更贴合 Agent 场景的容错需求：LLM 的参数错误应该是可恢复的循环内错误，而不是致命的系统异常。
