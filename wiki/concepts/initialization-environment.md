---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, initialization, environment, configuration, sandbox]
---

# Initialization & Environment（初始化与环境）

## 定义

初始化与环境是 Agent 系统的运行时根基：负责路径解析、配置加载、执行后端选择、环境快照捕获、profile 隔离和密钥隔离，为 CLI、Gateway、Cron、Subagent 等所有入口提供一致的初始化契约和沙箱执行环境。

## 为什么需要

- Agent 需要知道数据目录、配置文件、API key、模型参数等启动信息。
- 同一台机器上可能有「工作」和「个人」等多个 profile，需要隔离数据、git 身份、SSH key、API key。
- 命令执行需要继承用户 shell 环境（PATH、alias、函数），否则 nvm/pyenv 等工具不可用。
- 本地/Docker/SSH/云沙箱等不同执行环境需要统一抽象，否则每个工具都要写多份生命周期逻辑。
- 默认不应把 API key 透传给子进程，除非显式声明。

## 核心组成

| 组件 | 作用 |
|---|---|
| 路径根 | 单一事实来源（如 `HERMES_HOME`），支持 profile fallback |
| 配置加载 | 默认值 + 用户 YAML + 环境变量，递归合并 |
| Profile 机制 | 按 profile 隔离数据和配置 |
| 执行环境 ABC | local/docker/modal/ssh/云沙箱等后端统一接口 |
| 环境快照 | 一次性捕获 shell 环境，后续命令 source 复用 |
| CWD 追踪 | 跨命令保持当前工作目录 |
| 密钥隔离 | 默认不透传 `*_API_KEY`，显式豁免 |

## 典型配置合并流程

```
DEFAULT_CONFIG（代码内嵌完整默认值）
  ↓ deep_merge
用户 config.yaml（只写关心的 key）
  ↓ expand_env_vars
环境变量 ${VAR}
  ↓ cache_on(mtime, size)
运行时配置对象
```

## 执行环境抽象

```
BaseEnvironment
  ├─ init_session()   # 捕获环境快照
  ├─ execute(cmd)     # source 快照 → cd → run → 解析 CWD marker
  └─ cleanup()        # 释放资源

LocalEnvironment / DockerEnvironment / ModalEnvironment / SSHEnvironment / ...
```

## 设计权衡

| 权衡 | 选项 A | 选项 B |
|---|---|---|
| Profile 切换 | env var 全局广播 | 运行时传参 |
| 配置合并 | deep_merge 递归覆盖 | 扁平 dict 全量抄写 |
| 环境快照 | 一次性 `bash -l` 捕获 | 每次命令都登录 shell |
| 密钥透传 | 黑名单默认不透传 | 白名单放行 |
| CWD 追踪 | 本地文件 + 远程 marker 双通道 | 单通道 |

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 配置格式 | YAML 三路合并（DEFAULT_CONFIG + 用户 YAML + 环境变量） | 显式 `onboard` CLI；Pydantic 同时支持 camelCase/snake_case | JSON5 + `$include` + `${ENV}` | 7 层配置合并 |
| 路径/profile | `HERMES_HOME` env + profile fallback | — | — | 项目 ID 基于 git root commit |
| Provider 匹配 | — | 关键词 + 前缀匹配 + api_base 回退 | — | — |
| 环境抽象 | `BaseEnvironment` ABC：local/docker/modal/ssh 等 | — | Docker 容器默认 | — |
| 环境快照 | 一次性 `bash -l` 捕获 PATH/alias/函数 | — | — | 实时生成 `environment()` |
| 密钥隔离 | 黑名单默认不透传 `*_API_KEY` | — | `SecretRef` 引用（env/file/exec） | — |
| 插件加载 | 内存 provider ABC + 动态发现 | — | Jiti 运行时 TS 加载 + manifest | — |
| 独特设计 | profile 隔离 + 环境快照 + 后端 ABC | 显式 onboard 避免静默覆盖配置 | respawn 策略 + JSON5 include | AsyncLocalStorage 上下文传递 |

## 与相关概念的关系

- 初始化与环境为 [[agent-tool-system]] 的 `terminal` 类工具提供执行后端。
- 配置系统影响 [[prompt-building-for-agents]] 中模型、provider、技能等选择。
- 环境快照和密钥隔离是 [[agent-security]] 的一部分。
- Profile 隔离使 [[sub-agent-orchestration]] 能在不同配置下运行。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `agent/environment.py`、配置加载和 `hermes setup` 实现。其他框架待补充。
