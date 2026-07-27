---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度10-验证循环.md
tags: [hermes-agent, validation-loop, tool-guardrails, schema-sanitization, approval]
---

# Hermes Agent：验证循环

## 摘要

Hermes 的验证循环是在「LLM 决策 → 实际执行」之间插入的多层把关层，包含三类验证：**预校验**（schema 清理、参数强制类型）、**许可校验**（危险命令审批 / 安全扫描）、**事后回路校验**（同一调用反复失败/无进展时的护栏中止）。共同保证 LLM 不会因为格式错误、误判风险、卡死循环而把代价转嫁给宿主机或用户。关键源码位于 `schema_sanitizer.py`、`tools/approval.py`、`agent/tool_guardrails.py`。

## 核心主张

1. **Schema 预校验**：每次构建 tool 列表时无条件 `sanitize_tool_schemas()`，把 provider 后端会拒的 schema 折叠为最大公约数形态。
2. **反应式回退**：仅当后端真的返回 llama.cpp grammar 错误时，才做更激进的 `strip_pattern_and_format`，避免损失提示信息。
3. **HARDLINE 在 YOLO 之上**：`check_all_command_guards` 先运行 `detect_hardline_command`，再检查 `HERMES_YOLO_MODE`——硬底线不可绕过。
4. **审批三档粒度**：`once` / `session` / `always`，分别对应「我现在要做」、「这次会话别再问」、「以后都别问」。
5. **护栏默认 warn 不 block**：只读工具允许合理重复调用，hard stop 需显式 opt-in，避免误伤。
6. **网关审批同步阻塞**：用 `threading.Event()` + 1s 心跳阻塞等待审批结果，LLM 完全不知道发生审批，避免误判为工具失败。

## 验证阶段

| 阶段 | 机制 | 说明 |
|---|---|---|
| 预校验 | schema 清理 + 参数 coerce | 投递给 LLM 前 |
| 许可校验 | HARDLINE / DANGEROUS / tirith | 命令执行前 |
| 执行前 | `ToolCallGuardrailController.before_call()` | 工具调用前 |
| 执行后 | `ToolCallGuardrailController.after_call()` | 失败计数、相同结果计数 |
| Turn 收尾 | `_halt_decision` | 触发时强制收尾 |

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度10-验证循环.md)
