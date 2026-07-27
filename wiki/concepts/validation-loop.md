---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, validation-loop, guardrails, tool-guardrails]
---

# Validation Loop（验证循环）

## 定义

验证循环是在「LLM 决策 → 实际执行」之间插入的多层把关层，用于校验 LLM 输出的格式、参数、风险和执行结果，防止格式错误、误判风险和卡死循环把代价转嫁给宿主机或用户。

## 为什么需要

- LLM 输出可能包含 provider 不接受的 schema（如 `anyOf`、缺失 `properties` 的 object），导致整轮请求 400。
- 危险命令若直接执行，可能造成不可逆破坏。
- LLM 容易陷入「再试一次」的重复失败循环，浪费 token 和计算资源。
- slash 命令等管理操作可能破坏缓存或状态，需要用户确认。

## 三类验证

| 阶段 | 验证对象 | 典型机制 |
|---|---|---|
| 预校验 | Tool schema、参数类型 | `sanitize_tool_schemas()`、`_repair_tool_call_arguments()`、参数 coerce |
| 许可校验 | 危险命令、安全风险 | HARDLINE/DANGEROUS 模式匹配、外部二进制扫描、SSRF/路径检查 |
| 事后回路校验 | 执行结果、失败模式 | ToolCallGuardrailController：失败计数、相同结果计数、halt 决策 |

## 关键设计点

- **两段式 schema 清理**：无条件做宽 sanitize；仅在后端真的返回 grammar 错误时才做更激进的剥离。
- **HARDLINE 不可绕过**：绝对禁止的命令在任何放行模式之前就先拦截。
- **审批三档粒度**：`once` / `session` / `always`，分别对应临时、会话级、永久授权。
- **护栏默认 warn**：避免误伤合理重复调用；hard stop 需显式 opt-in。
- **网关审批同步阻塞**：让 LLM 只看到 approved 后的结果，不把审批等待误判为工具失败。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 预校验 | `sanitize_tool_schemas` 无条件 + 反应式回退 | 先 `cast_params` 再 `validate_params` | Schema 扁平化 + 参数别名兼容 | zod 参数校验；工具修复 |
| 许可校验 | HARDLINE/DANGEROUS + tirith | `restrict_to_workspace` + `allowFrom` | 6 层策略管道 + 执行审批 | `PermissionNext` 规则引擎 |
| 事后回路 | `ToolCallGuardrailController`：失败计数、halt 决策 | `_HINT` 错误提示让 LLM 自修正 | 工具循环检测向 LLM 注入警告 | Doom Loop 运行时检测 |
| 审批粒度 | once / session / always 三档 | — | off / on-miss / always 三档询问 | `allow/deny/ask` 三态 |
| 独特设计 | HARDLINE 在 YOLO 之上不可绕过 | 手写轻量校验器覆盖 LLM 实际会错的子集 | 循环检测 critical 级别直接阻断 | 结构化输出用工具模式 |

## 与相关概念的关系

- 验证循环是 [[agent-security]] 的实战落地。
- 预校验与 [[agent-tool-system]] 的 schema 编排和 [[output-parsing]] 的参数修复紧密相关。
- 事后校验是 [[error-handling]] 的第一道防线。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `schema_sanitizer.py`、`approval.py`、`tool_guardrails.py` 实现。其他框架待补充。
