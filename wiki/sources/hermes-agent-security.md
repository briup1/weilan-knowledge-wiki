---
type: source
created: 2026-07-26
updated: 2026-07-26
raw: raw/archive/research/agent-frameworks/hermes_agent_维度09-安全防护.md
tags: [hermes-agent, agent-security, prompt-injection, ssrf, command-approval]
---

# Hermes Agent：安全防护

## 摘要

Hermes 的安全防护是一套**「分层纵深 + 多面协同」**的防御体系：从命令执行前的双层模式匹配（HARDLINE/DANGEROUS）与外部二进制扫描（tirith），到运行时 SSRF 拦截、路径穿越阻断、工具调用循环熔断，再到日志与输出中的敏感信息脱敏，以及外部 Skill 的静态威胁扫描。每一层都遵循 fail-closed 原则，各层之间通过统一审批状态机串联。关键源码位于 `tools/approval.py`、`tools/url_safety.py`、`agent/redact.py`、`tools/skills_guard.py`。

## 核心主张

1. **HARDLINE 硬底线**：12 条无恢复路径的命令（如 `rm -rf /`、`mkfs`、`dd` 写设备）在任何放行模式下都不可绕过。
2. **Unicode 归一化**：`_normalize_command_for_detection` 用 `unicodedata.normalize('NFKC')` 和 `strip_ansi` 防御全角字符/null byte 绕过。
3. **SSRF 拦截**：`_ALWAYS_BLOCKED_IPS` 明确包含云元数据端点 `169.254.169.254`、私有网段等，DNS 解析到这些 IP 时阻断请求。
4. **路径穿越阻断**：`validate_within_dir` 用 `Path.resolve()` 后 `relative_to(root_resolved)` 严格校验，防御符号链接穿越。
5. **敏感信息脱敏**：`agent/redact.py` 把 30+ 种已知凭证前缀编译成 alternation，日志写入前自动替换。
6. **Skill 静态威胁扫描**：`tools/skills_guard.py` 100+ 条 THREAT_PATTERNS 覆盖数据外泄、提示注入、持久化、反向 shell、供应链攻击等 12 类。
7. **工具循环 guardrail**：同一工具签名失败超过阈值时直接 block，避免反复失败烧 token。

## 防御层

| 层级 | 机制 | 触发点 |
|---|---|---|
| 命令检测 | HARDLINE / DANGEROUS 模式匹配 | `terminal_tool` 执行前 |
| 外部扫描 | tirith 二进制扫描 | 命令审批路径 |
| 网络安全 | URL/IP 安全检查 | browser/web_search/web_extract |
| 路径安全 | resolve() + relative_to | skill 文件读写 |
| 运行时护栏 | ToolCallGuardrailController | 每次工具调用前后 |
| 日志脱敏 | RedactingFormatter | 所有日志写入 |
| Skill 扫描 | THREAT_PATTERNS | skill 安装流程 |

## 原始文件

- [原始文件](../../raw/archive/research/agent-frameworks/hermes_agent_维度09-安全防护.md)
