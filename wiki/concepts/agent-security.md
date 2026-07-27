---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, security, prompt-injection, ssrf, sandbox]
---

# Agent Security（Agent 安全防护）

## 定义

Agent 安全防护是一套分层纵深防御体系，防止 LLM 被诱导执行破坏性命令、访问敏感资源、泄露凭证或陷入工具调用死循环。核心原则是 **fail-closed**：没有明确允许就默认阻断。

## 为什么需要

- Agent 的 `terminal` 工具可直接执行 shell，一次幻觉或 prompt injection 就可能造成不可逆数据丢失。
- `browser`、`web_search` 等工具会发起网络请求，可能被诱导访问云元数据端点、私有 IP。
- Skill/插件可从外部下载执行，恶意代码会静默进入 Agent 的 toolset。
- Agent 输出、命令输出、HTTP 响应中可能包含 API key、token，会写入日志永久留存。

## 防御层

| 层级 | 威胁 | 典型机制 |
|---|---|---|
| 命令执行前检测 | 破坏性 shell 命令 | HARDLINE/DANGEROUS 模式匹配、外部二进制扫描 |
| 输入归一化 | Unicode 全角、ANSI、null byte 绕过 | NFKC 归一化、strip_ansi |
| 网络安全 | SSRF、云元数据窃取 | IP 黑名单、DNS 解析后阻断私有 IP |
| 路径安全 | 目录穿越、符号链接绕过 | `Path.resolve()` + `relative_to()` 严格校验 |
| 运行时护栏 | 同一失败工具反复调用 | before_call/after_call 计数与 block |
| 日志脱敏 | 凭证泄露到日志 | 30+ 种前缀的正则自动替换 |
| Skill 静态扫描 | 恶意 Skill 被安装 | THREAT_PATTERNS 覆盖 12 类攻击 |

## 关键设计点

- **HARDLINE 在 YOLO 之上**：绝对禁止的命令不可被任何「放行模式」绕过。
- **审批三档粒度**：`once` / `session` / `always`，兼顾安全与用户体验。
- **外部扫描兜底**：模式匹配之外再用 tirith 等二进制扫描做二次校验。
- **默认 warn 不 block**：只读等合理重复调用不应被误杀，hard stop 需显式 opt-in。
- **网关审批同步阻塞**：避免 LLM 把审批等待误判为工具失败而进入重试循环。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 沙箱策略 | 环境后端 ABC（local/docker/modal/ssh） | `restrict_to_workspace` + 路径解析 | Docker 容器默认 + `SandboxFsBridge` | 规则引擎 + Bash AST 解析 |
| 命令审批 | HARDLINE（12 条）+ DANGEROUS（47 条）+ tirith 外部扫描 | `allowFrom` 默认空列表拒绝所有；路径 `resolve()` 校验 | 三级安全（deny/allowlist/full）+ 三级询问 | `allow/deny/ask` 三态 + wildcard |
| SSRF 防护 | IP 黑名单，DNS 解析后阻断私有 IP | 独立 `security/network.py` 模块；命令字符串检测 | DNS 解析前拦截 + 解析后二次验证 + hostname allowlist | — |
| 密钥/Secret | 黑名单默认不透传 `*_API_KEY` | — | `SecretRef` 引用（env/file/exec） | — |
| 日志脱敏 | 30+ 种前缀正则自动替换 | — | — | — |
| Skill 扫描 | 100+ 条 THREAT_PATTERNS 静态扫描 | — | `skill-scanner.ts` 静态分析 | — |
| 独特设计 | HARDLINE 在 YOLO 之上不可绕过 | `allowFrom` 默认拒绝所有是安全优先 | Docker 沙箱默认 + SecretRef | AST 解析 Bash 命令 |

## 与相关概念的关系

- 安全防护是 [[validation-loop]] 的核心组成部分。
- 危险命令审批在 [[agent-tool-system]] 的 dispatch 路径中触发。
- SSRF/路径安全与 [[initialization-environment]] 的沙箱后端相关。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `approval.py`、`url_safety.py`、`redact.py`、`skills_guard.py` 实现。其他框架待补充。
