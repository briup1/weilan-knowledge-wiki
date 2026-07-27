---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, prompt-engineering, system-prompt, prompt-cache]
---

# Prompt Building for Agents（Agent 的 Prompt 构建）

## 定义

Agent 的 Prompt 构建是将多源信息（身份、能力、记忆、环境、技能索引、项目上下文等）按严格优先级组装成 system prompt，并在 API 调用前叠加瞬态指令与缓存控制标记的过程。目标是让 LLM 准确理解任务、正确调用工具，同时最大化 prompt cache 命中率。

## 为什么需要

- Agent 的 system prompt 通常由 10+ 个信息层组成，必须有序组装。
- 不同 provider 对 system/user/developer 角色、工具格式、reasoning 字段要求不同。
- 动态内容若直接写入 system prompt，会破坏 prefix cache，显著增加多轮成本。
- 项目上下文文件（如 `CLAUDE.md`、`.cursorrules`）可能包含 prompt injection 攻击，需要扫描。

## 典型层次（洋葱模型）

| 层级 | 内容 | 稳定性 |
|---|---|---|
| 1 | Agent 身份 / SOUL.md | 最稳定 |
| 2 | 产品自指引导 | 稳定 |
| 3 | 工具感知行为引导 | 条件注入 |
| 4 | 模型家族特化引导 | 按模型 |
| 5 | 用户/网关传入的系统消息 | 稳定 |
| 6 | 持久记忆 | 快照稳定 |
| 7 | 外部记忆召回 | 快照稳定 |
| 8 | 技能索引 | 缓存稳定 |
| 9 | 项目上下文文件 | 文件级稳定 |
| 10 | 时间戳、平台格式提示 | 每轮变化但不入缓存 |

## 关键设计点

- **缓存分层**：稳定层进入 `_cached_system_prompt`，变化层作为 `ephemeral_system_prompt` 在 API 调用时才叠加。
- **技能索引缓存**：进程内 LRU + 磁盘 snapshot，避免每轮扫描 skills 目录。
- **上下文文件优先级**：严格互斥，只加载第一个匹配文件，避免多项目上下文冲突。
- **Prompt injection 扫描**：所有上下文文件加载前做威胁模式检测。
- **瞬态提示分离**：`prefill_messages` 等只在 API 调用时插入，不污染持久化 system prompt。

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 系统提示结构 | 洋葱式 11 层组装 | 静态身份 + RuntimeContext + 技能摘要 | PromptMode 三级（full/minimal/none） | 2-part system（header + rest） |
| 缓存策略 | `_cached_system_prompt` 会话级缓存 + SQLite 持久化 | 无特殊缓存，每次构建 | header 不变时缓存命中 | header 不变时缓存命中 |
| 上下文文件 | `.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules` | `AGENTS.md` / `SOUL.md` / `USER.md` / `TOOLS.md` | 项目指令文件 | 向上查找 AGENTS.md/CLAUDE.md |
| 技能处理 | 双层缓存：LRU + 磁盘 snapshot | 摘要索引，按需 `read_file` | 二进制搜索找最大前缀；路径压缩 | Plugin 可修改 system 的 hook |
| 平台/模型特化 | 模型家族特化引导 + 开发者角色转换 | 平台策略硬编码在 Identity 中 | 子 Agent/Cron 自动降级为 minimal | Agent prompt 优先覆盖 provider prompt |
| 注入防护 | `_scan_context_content()` 扫描威胁模式 | Guidelines 硬编码在 Identity 中 | 剥离 Unicode 控制字符 | — |

## 与相关概念的关系

- Prompt 构建依赖 [[agent-memory-system]] 提供的记忆内容。
- 组装好的 prompt 会进入 [[context-management]] 的压缩流程。
- 工具相关提示需要与 [[agent-tool-system]] 的 schema 保持一致。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `prompt_builder` 实现。其他框架待补充。
