---
type: entity
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent-setup, hermes-agent-orchestration-loop, hermes-agent-tool-system, hermes-agent-memory-system, hermes-agent-context-management, hermes-agent-prompt-building, hermes-agent-output-parsing, hermes-agent-state-management, hermes-agent-error-handling, hermes-agent-security, hermes-agent-validation-loop, hermes-agent-sub-agent-orchestration, hermes-agent-initialization-environment]
tags: [hermes-agent, agent-framework, python, nous-research, open-source]
---

# Hermes Agent

**Hermes Agent** 是 NousResearch 开源的 Python AI Agent 框架，定位为一个功能丰富的**网关/CLI 型 Agent**，强调多供应商兼容、生产级错误恢复、可中断的并发执行和深度可扩展的工具/技能/记忆插件体系。

## 核心定位

- **项目类型**：开源 Agent 框架（Python）
- **维护方**：NousResearch
- **代码规模**：`cli.py` ~410KB、`run_agent.py` ~500KB，整体超过 11K 行
- **主要入口**：CLI (`hermes chat`)、Gateway API、Cron/Batch runner
- **包管理**：uv

## 关键模块

| 模块 | 文件/目录 | 职责 |
|---|---|---|
| 执行引擎 | `run_agent.py` | 编排循环、工具调用、上下文压缩、错误恢复、子 Agent 编排 |
| 工具系统 | `tools/`、`model_tools.py`、`tools/registry.py` | 自注册工具总线、MCP 动态工具、Schema 兼容 |
| 记忆系统 | `tools/memory_tool.py`、`agent/memory_manager.py`、`agent/memory_provider.py` | 内置 MEMORY/USER.md + 外部记忆提供者插件 |
| 上下文管理 | `agent/context_compressor.py` | 三段式压缩、孤儿 tool-call 修复、prompt cache 保护 |
| Prompt 构建 | `agent/prompt_builder.py` | 洋葱式 system prompt、SOUL.md、技能索引、上下文文件 |
| 输出解析 | `agent/transports/`、`agent/think_scrubber.py` | 多 provider 响应归一化、reasoning 双轨存储、流式 scrubber |
| 状态管理 | `agent/session_db.py` | SQLite WAL、FTS5 双索引、声明式 schema 迁移 |
| 错误处理 | `agent/error_classifier.py`、`agent/retry_utils.py` | 结构化错误分类、六类恢复动作 |
| 安全防护 | `tools/approval.py`、`tools/url_safety.py`、`agent/redact.py` | 危险命令审批、SSRF 拦截、敏感信息脱敏 |
| 验证循环 | `tools/approval.py`、`agent/tool_guardrails.py`、`schema_sanitizer.py` | 预校验、许可校验、事后护栏 |
| 子 Agent 编排 | `tools/delegate_tool.py` | `delegate_task` 创建受限子 AIAgent 实例 |
| 初始化与环境 | `agent/environment.py`、配置加载、profile 隔离 | 多后端沙箱、环境快照、配置三路合并 |

## 设计哲学

Hermes 的核心取舍是**「生产优先」**：不是最简 Agent，而是在真实多供应商、多故障、长会话场景下仍能稳定运行的 Agent。具体表现为：

- **Fail-closed 安全**：HARDLINE 命令在任何放行模式下都不可绕过
- **缓存友好**：system prompt 会话级锁定，动态内容注入 user 消息
- **错误结构化**：所有异常先分类再决策，而不是用字符串匹配散落处理
- **可中断并发**：线程级中断信号 + ThreadPoolExecutor 并发工具执行

## 相关概念

- [[orchestration-loop]]
- [[agent-tool-system]]
- [[agent-memory-system]]
- [[context-management]]
- [[prompt-building-for-agents]]
- [[output-parsing]]
- [[state-management]]
- [[error-handling]]
- [[agent-security]]
- [[validation-loop]]
- [[sub-agent-orchestration]]
- [[initialization-environment]]

## 相关来源

- [[hermes-agent-setup]] —— 本地启动与项目结构
- [[hermes-agent-orchestration-loop]] —— 编排循环
- [[hermes-agent-tool-system]] —— 工具系统
- [[hermes-agent-memory-system]] —— 记忆系统
- [[hermes-agent-context-management]] —— 上下文管理
- [[hermes-agent-prompt-building]] —— Prompt 构建
- [[hermes-agent-output-parsing]] —— 输出解析
- [[hermes-agent-state-management]] —— 状态管理
- [[hermes-agent-error-handling]] —— 错误处理
- [[hermes-agent-security]] —— 安全防护
- [[hermes-agent-validation-loop]] —— 验证循环
- [[hermes-agent-sub-agent-orchestration]] —— 子 Agent 编排
- [[hermes-agent-initialization-environment]] —— 初始化与环境
