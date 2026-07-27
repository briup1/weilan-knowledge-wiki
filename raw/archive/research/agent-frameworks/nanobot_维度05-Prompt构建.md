# 维度名：Prompt 构建（Prompt Building）

## 1. 一句话定位

Prompt 构建是将"静态身份定义、动态运行时信息、用户自定义指令、持久记忆、可选技能"这五类异构素材，组装成 LLM 可消费的 `system` + `messages` 结构化输入的**编译器层**——它决定了 Agent 知道什么、能做什么、以及行为边界在哪里。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果把 `ContextBuilder` 从 nanobot 中移除，直接让 `AgentLoop` 把用户消息裸发给 LLM：

1. **Agent 没有自我认知**：LLM 不知道自己叫 nanobot，不知道工作区在哪里，也不知道如何读写记忆文件。用户说"记住我喜欢 Python"，模型会回复"好的我记住了"——但实际上它没有任何机制把这句话落盘到 `MEMORY.md`。

2. **平台行为不一致**：Windows 用户让 Agent `grep` 某个文件，模型在 Prompt 中默认假设 POSIX 环境，生成 `grep` 工具调用 → `ExecTool` 在 Windows 上找不到 `grep` → 返回 `"Error: command not found"` → LLM 困惑并反复重试。`context.py:63-73` 的平台策略段正是为了预防这类"环境假设错误"。

3. **技能膨胀导致 token 爆炸**：`skills/` 目录下可能有数十个 SKILL.md 文件，总内容量可达数万 token。如果全部注入 System Prompt，一次请求就占满上下文窗口。`build_skills_summary()` 只输出 XML 摘要（`skills.py:101-140`），让 LLM 按需读取，是 token 预算约束下的必要妥协。

4. **Bootstrap 文件无法自定义**：没有 `_load_bootstrap_files()`，用户无法通过在工作区放置 `AGENTS.md` / `SOUL.md` / `USER.md` / `TOOLS.md` 来覆盖或扩展 Agent 行为——所有行为规则必须硬编码在 Python 中，每次调整都要改代码重启进程。

### 2.2 nanobot 的具体触发条件

| 触发点 | 条件 | 代码位置 |
|--------|------|----------|
| 构建 System Prompt | 每次 `_process_message()` 调用 `build_messages()` 时 | `context.py:141` |
| 加载 Bootstrap 文件 | `build_system_prompt()` → `_load_bootstrap_files()`，检查 4 个文件名是否存在 | `context.py:31-33, 108-118` |
| 注入长期记忆 | `build_system_prompt()` → `memory.get_memory_context()`，检查 `MEMORY.md` 是否存在 | `context.py:35-37` |
| 加载常驻技能 | `build_system_prompt()` → `skills.get_always_skills()`，筛选 `always=true` 的技能 | `context.py:39-43` |
| 生成技能摘要 | `build_system_prompt()` → `skills.build_skills_summary()`，列出所有可用技能 | `context.py:45-52` |
| 注入 Runtime Context | `build_messages()` → `_build_runtime_context()`，每次请求动态生成 | `context.py:130, 101-106` |
| 处理图片媒体 | `build_messages()` → `_build_user_content()`，检测到 `media` 参数非空时 | `context.py:131, 146-166` |

---

## 3. 核心设计思路

### 3.1 抽象模型

Prompt 构建是一个**"分层叠加"**模型——每一层都是可选的，按固定优先级拼接，用 `\n\n---\n\n` 作为层间分隔符：

```
System Prompt = Identity          ← 硬编码，不可变
              + Bootstrap Files   ← 用户自定义，可选
              + Memory            ← 动态加载，可选
              + Always Skills     ← 常驻技能，可选
              + Skills Summary    ← 技能索引，可选
              -----------------
Messages    = [System Prompt]
              + History (未固化的 session.messages)
              + User Message (Runtime Context + 用户原文 + 媒体)
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **Bootstrap 文件机制** | 用户在工作区放 `AGENTS.md` / `SOUL.md` / `USER.md` / `TOOLS.md`，启动时自动加载 | 全部硬编码在 Python 中；或提供 Web UI 配置界面 | `context.py:19` 定义了 4 个文件名常量，`context.py:108-118` 按顺序检查存在性并读取。文件机制零依赖、零学习成本，任何会写 markdown 的用户都能自定义 Agent 行为，无需改代码 |
| **技能"摘要+按需读取"** | `build_skills_summary()` 输出 XML 索引（名称/描述/路径），LLM 通过 `read_file` 读取完整 SKILL.md | 全部技能内容注入 System Prompt | `skills.py:101-140` 的 XML 摘要通常只有几百 token，而完整 SKILL.md 可能数千 token。 nanobot 面向个人用户，技能数量可能膨胀，渐进加载是 token 预算约束下的必然选择 |
| **平台策略硬编码在 Identity 中** | `_get_identity()` 根据 `platform.system()` 输出 Windows/POSIX 差异化指令 | 把平台检测放在 Shell 工具内部，让工具自己适配 | `context.py:62-73` 把平台策略放在 System Prompt 中，让 LLM **事前知道**环境限制，从而生成更合适的工具调用（如 Windows 下用 `findstr` 而非 `grep`）。如果放在工具层，LLM 已经生成了错误调用，代价是至少一轮往返 |
| **Runtime Context 合并到 User Message** | `_build_runtime_context()` 生成的时间/渠道元数据，通过 `\n\n` 拼接进 user message | 作为独立 system message 追加；或作为 function_call 的额外参数 | `context.py:133-138` 明确注释："to avoid consecutive same-role messages that some providers reject"——OpenAI 等 Provider 会拒绝连续同角色消息。合并到 user message 是兼容性最优解 |
| **Guidelines 硬编码在 Identity 中** | "State intent before tool calls" / "Before modifying a file, read it first" 等 6 条规则直接写在 `_get_identity()` | 放在 Bootstrap 文件中让用户自行决定是否遵守 | `context.py:90-96` 的 Guidelines 是 nanobot 的核心行为契约（如"网络内容不可信"是安全底线），如果让用户可选覆盖，存在安全风险。而 Bootstrap 文件用于扩展行为，不是替代底线 |

### 3.3 数据流/控制流

```
[AgentLoop._process_message()]          loop.py:356
    │
    ├─▶ context.build_messages(...)     context.py:120
    │       │
    │       ├─▶ build_system_prompt()   context.py:27
    │       │       ├─▶ _get_identity()         context.py:56  → 硬编码身份+平台策略+Guidelines
    │       │       ├─▶ _load_bootstrap_files() context.py:108 → AGENTS.md / SOUL.md / USER.md / TOOLS.md
    │       │       ├─▶ memory.get_memory_context() memory.py:98 → MEMORY.md 内容
    │       │       ├─▶ skills.get_always_skills()  skills.py:193 → always=true 技能
    │       │       └─▶ skills.build_skills_summary() skills.py:101 → XML 技能索引
    │       │
    │       ├─▶ _build_runtime_context() context.py:101 → Current Time + Channel + Chat ID
    │       ├─▶ _build_user_content()    context.py:146 → 用户原文 + base64 图片
    │       └─▶ 合并为单条 user message  context.py:135-138
    │
    └─▶ 返回 [{role: system, content: ...}, {role: user, content: ...}, ...]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：分层 System Prompt 组装

**作用**：将五类异构素材按固定优先级拼接成 System Prompt，用 `---` 分隔保证 LLM 能区分层次。

**设计意图**：为什么要用 `\n\n---\n\n` 作为分隔符？因为 `---` 是 markdown 水平线语法，LLM 对它有天然的"段落/章节分隔"语义理解。如果用自定义标记（如 `[SECTION_BREAK]`），不同模型对它的理解不一致。

**关键源码**（`nanobot/agent/context.py:27-54`）：
```python
def build_system_prompt(self, skill_names: list[str] | None = None) -> str:
    """Build the system prompt from identity, bootstrap files, memory, and skills."""
    parts = [self._get_identity()]              # ① 身份是基底，永远存在

    bootstrap = self._load_bootstrap_files()    # ② 用户自定义覆盖层
    if bootstrap:
        parts.append(bootstrap)

    memory = self.memory.get_memory_context()   # ③ 动态记忆层
    if memory:
        parts.append(f"# Memory\n\n{memory}")

    always_skills = self.skills.get_always_skills()  # ④ 常驻技能
    if always_skills:
        always_content = self.skills.load_skills_for_context(always_skills)
        if always_content:
            parts.append(f"# Active Skills\n\n{always_content}")

    skills_summary = self.skills.build_skills_summary()  # ⑤ 技能索引
    if skills_summary:
        parts.append(f"""# Skills\n...""")

    return "\n\n---\n\n".join(parts)            # ⑥ 层间分隔
```

### 机制 B：平台感知 Identity

**作用**：根据运行平台（Windows/macOS/POSIX）动态注入差异化行为指令。

**设计意图**：为什么平台策略放在 System Prompt 中而不是让 Shell 工具自己处理？因为 LLM 生成工具调用时就已经做了"用 grep 还是 findstr"的决策。如果平台检测在工具层，LLM 已经生成了 `grep`，工具只能返回错误，至少浪费一轮迭代。放在 Prompt 中是让 LLM **事前知情**。

**关键源码**（`nanobot/agent/context.py:56-98`）：
```python
def _get_identity(self) -> str:
    workspace_path = str(self.workspace.expanduser().resolve())
    system = platform.system()
    runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"

    platform_policy = ""
    if system == "Windows":
        platform_policy = """## Platform Policy (Windows)
- You are running on Windows. Do not assume GNU tools like `grep`, `sed`, or `awk` exist.
- Prefer Windows-native commands or file tools when they are more reliable."""
    else:
        platform_policy = """## Platform Policy (POSIX)
- You are running on a POSIX system. Prefer UTF-8 and standard shell tools."""

    return f"""# nanobot 🐈
You are nanobot, a helpful AI assistant.
## Runtime
{runtime}
## Workspace
Your workspace is at: {workspace_path}
...
{platform_policy}
## nanobot Guidelines
- State intent before tool calls, but NEVER predict or claim results...
- Before modifying a file, read it first...
..."""
```

### 机制 C：渐进式技能加载

**作用**：避免一次性注入所有技能内容导致 token 爆炸，只输出摘要索引，让 LLM 按需读取。

**设计意图**：为什么用 XML 格式而不是 JSON 或 markdown 列表？因为 XML 的 `<skill>` / `<name>` / `<description>` 标签结构对 LLM 的解析友好度最高——标签明确分隔字段，不易混淆。JSON 的引号和嵌套在大段文本中容易让模型"看串行"。

**关键源码**（`nanobot/agent/skills.py:101-140`）：
```python
def build_skills_summary(self) -> str:
    """Build a summary of all skills for progressive loading."""
    all_skills = self.list_skills(filter_unavailable=False)
    if not all_skills:
        return ""

    lines = ["<skills>"]
    for s in all_skills:
        name = escape_xml(s["name"])
        path = s["path"]
        desc = escape_xml(self._get_skill_description(s["name"]))
        skill_meta = self._get_skill_meta(s["name"])
        available = self._check_requirements(skill_meta)

        lines.append(f'  <skill available="{str(available).lower()}">')
        lines.append(f'    <name>{name}</name>')
        lines.append(f'    <description>{desc}</description>')
        lines.append(f'    <location>{path}</location>')

        if not available:                       # ③ 不可用时提示缺失依赖
            missing = self._get_missing_requirements(skill_meta)
            if missing:
                lines.append(f'    <requires>{escape_xml(missing)}</requires>')
        lines.append("  </skill>")
    lines.append("</skills>")
    return "\n".join(lines)
```

### 机制 D：Runtime Context 与用户消息的合并策略

**作用**：将动态时间/渠道元数据注入到用户消息中，同时避免 Provider API 报错。

**设计意图**：为什么不把 Runtime Context 放在 System Prompt 里？因为 System Prompt 是静态的（同一轮对话中不变），而 `Current Time` 每次请求都会变化。如果把时间放在 System Prompt 中，prompt caching 会失效（System Prompt 变了），且每次都要重新发送完整的 System Prompt，浪费 token。

**关键源码**（`nanobot/agent/context.py:129-144`）：
```python
def build_messages(self, history, current_message, ...):
    runtime_ctx = self._build_runtime_context(channel, chat_id)
    user_content = self._build_user_content(current_message, media)

    # Merge runtime context and user content into a single user message
    # to avoid consecutive same-role messages that some providers reject.
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

### 机制 E：Bootstrap 文件覆盖层

**作用**：让用户通过在工作区放置 markdown 文件来自定义 Agent 行为，无需修改代码。

**设计意图**：为什么是 4 个特定文件名（`AGENTS.md` / `SOUL.md` / `USER.md` / `TOOLS.md`）而不是任意文件？这 4 个名字来自 OpenClaw 生态的约定，nanobot 继承这个约定以保持与现有用户习惯兼容。按顺序加载意味着后面的文件可以补充或微调前面的内容，但不是覆盖——全部内容都会被保留。

**关键源码**（`nanobot/agent/context.py:19, 108-118`）：
```python
BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md"]

def _load_bootstrap_files(self) -> str:
    """Load all bootstrap files from workspace."""
    parts = []
    for filename in self.BOOTSTRAP_FILES:
        file_path = self.workspace / filename
        if file_path.exists():                  # ① 存在才加载，不存在不报错
            content = file_path.read_text(encoding="utf-8")
            parts.append(f"## {filename}\n\n{content}")
    return "\n\n".join(parts) if parts else ""   # ② 全不存在时返回空字符串
```

---

## 5. 与其他维度的交互

```
[Prompt 构建] --(System Prompt + Messages)--> [编排循环]
[Prompt 构建] <--(workspace 路径)-- [初始化与环境]
[Prompt 构建] <--(历史消息)-- [状态管理]
[Prompt 构建] <--(MEMORY.md 内容)-- [记忆系统]
[Prompt 构建] <--(skill 定义)-- [工具系统]
[Prompt 构建] --(Runtime Context 含 channel/chat_id)--> [上下文管理]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环 | 组装好的 messages 列表 | `AgentLoop._process_message()` → `context.build_messages()` |
| 输出到 | 上下文管理 | 带 Runtime Context 的 user message | `_build_runtime_context()` 生成时间/渠道元数据 |
| 依赖 | 状态管理 | 历史消息作为 messages 的一部分 | `build_messages(history=session.get_history())` |
| 依赖 | 记忆系统 | MEMORY.md 内容注入 System Prompt | `memory.get_memory_context()` |
| 依赖 | 工具系统 | 技能定义和技能索引 | `skills.load_skills_for_context()` / `skills.build_skills_summary()` |
| 依赖 | 初始化与环境 | workspace 路径用于定位 Bootstrap 文件和记忆文件 | `ContextBuilder.__init__(workspace)` |
| 输出到 | 验证循环 | 工具参数 schema 来自 Tool.parameters | `tools.get_definitions()` → `build_messages()` 间接使用 |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **LLM 能正确理解 markdown 分隔符 `---`**：作者假设所有主流模型都能把 `---` 识别为章节分隔。如果某个模型把它当作 YAML frontmatter 的开始，System Prompt 的解析会出错。
2. **XML 格式对 LLM 的解析友好度高于 JSON**：作者基于经验选择 XML 作为技能摘要格式，假设模型在解析带标签的文本时比解析嵌套 JSON 更准确。
3. **Bootstrap 文件的用户会写 markdown**：作者假设目标用户（个人 AI 助手使用者）具备基本的 markdown 编辑能力，不需要 GUI 配置界面。
4. **平台策略放在 System Prompt 中比放在工具层更有效**：作者假设 LLM 在生成工具调用前会阅读并遵循 System Prompt 中的平台指令，从而减少错误调用的生成。

### 6.2 这个设计的代价/风险

1. **System Prompt 是同步生成的，每次请求都重新计算**：`build_system_prompt()` 每次都读取 `MEMORY.md`、扫描 `skills/` 目录、检查 Bootstrap 文件存在性。虽然单次开销不大（文件系统缓存），但在高频场景下（如批量任务）会成为瓶颈。没有看到缓存机制。
2. **Bootstrap 文件没有热加载**：`AGENTS.md` 修改后，必须等待新一轮对话才会生效（因为 `build_system_prompt()` 每次重新读取）。但如果用户期望"改完立即生效"，这个设计无法满足。
3. **`_get_identity()` 硬编码 Guidelines，无法被 Bootstrap 文件覆盖**：如果用户想在 `AGENTS.md` 中写"允许修改文件前不读取"，System Prompt 中硬编码的 `"Before modifying a file, read it first"` 会与用户指令冲突，LLM 可能困惑。
4. **Runtime Context 缺少版本号/会话标识**：`_build_runtime_context()` 只输出时间和渠道，没有会话 ID 或请求序号。在调试多轮对话时难以追踪哪条 Runtime Context 对应哪次请求。

### 6.3 如果要重新设计，可能会改变什么

1. **给 System Prompt 加一层缓存**：用 `mtime` 检测 `MEMORY.md` / `skills/` / Bootstrap 文件是否变化，不变时复用上一次的 `build_system_prompt()` 结果。这在高频场景下能显著减少 I/O。
2. **Guidelines 分层**：把 Guidelines 拆分为"不可覆盖底线"（如安全规则）和"可覆盖建议"（如"修改前先读取"），后者允许 Bootstrap 文件覆盖。这样既能保证安全底线，又给用户自定义空间。
3. **Runtime Context 加上请求序列号**：`_build_runtime_context()` 输出 `Request Seq: N`，方便在多轮长对话中追踪上下文。

### 6.4 对我自己设计 Agent 系统的启示

**把 Prompt 构建当作"编译器"来设计，而不是"字符串拼接"来设计。** nanobot 的 `ContextBuilder` 体现了明确的层次结构（Identity → Bootstrap → Memory → Skills → Runtime），每一层有清晰的职责边界和触发条件。最核心的一点是：**System Prompt 的静态部分和动态部分要分离**——静态部分（身份、平台策略、Guidelines）尽量保持不变以利用 prompt caching，动态部分（时间、Runtime Context）放在 user message 中。
