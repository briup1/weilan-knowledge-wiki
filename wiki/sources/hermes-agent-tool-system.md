---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度02-工具系统.md
tags: [hermes-agent, agent-tool-system, mcp, tool-registry]
---

# Hermes Agent：工具系统

## 摘要

Hermes Agent 的工具系统是**「工具发现 → schema 编排 → 调度分发」的中央总线**。通过一个零依赖的全局 `ToolRegistry` 单例，把「每个工具文件自己声明自己」的去中心化注册，统一为对 LLM 可见的、按 toolset 分组、按 `check_fn` 过滤的工具表。关键源码位于 `tools/registry.py`、`model_tools.py`、`toolsets.py`。

## 核心主张

1. **自注册避免循环导入**：`tools/registry.py` 不依赖 `model_tools.py` 或具体工具文件；工具模块在顶层调用 `registry.register(...)` 完成注册，使依赖图单向。
2. **schema/handler 绑定**：每个工具用一行 `registry.register(...)` 同时声明对 LLM 暴露的 schema 和实际 handler，避免新增工具改两处。
3. **MCP 动态工具支持**：`_generation` 计数器 + 30 秒 TTL 的 `check_fn` 缓存，使 MCP server 动态增删工具后 registry 能自动失效缓存。
4. **Provider 兼容**：入口处的 `coerce_tool_args` 和 `sanitize_tool_schemas` 处理 DeepSeek/Qwen/GLM/llama.cpp 等后端的 schema/参数差异。
5. **Agent-loop 拦截**：`todo`、`memory`、`session_search`、`delegate_task` 等工具虽在 registry 中可见，但 `handle_function_call` 直接返回错误存根，强制走 agent-level 路径。

## 关键机制

- `discover_builtin_tools()` 用 AST 扫描 `tools/*.py`，识别顶层 `registry.register(...)` 调用，再 import 对应模块。
- `get_tool_definitions()` 以 `(enabled, disabled, _generation, config_mtime)` 为 key 做 memo，避免每轮重算。
- 分发入口 `handle_function_call()` 统一处理 sync/async、hooks、错误降级。

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度02-工具系统.md)
