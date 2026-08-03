---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [oh-my-claudecode-guide]
tags: [claude-code, plugin, multi-agent, orchestration, skills]
---

# oh-my-claudecode

oh-my-claudecode（简称 OMC）是 [[claude-code]] 的多智能体编排插件，GitHub 超 31K Star。通过「多 Agent 协同」「并行执行」「智能路由」三大机制，将原生 Claude Code 从「单线程工具」升级为「19 Agent 开发团队」。口号：**A weapon, not a tool**（武器，而非工具）。

## 核心价值

| 维度 | 原生 Claude Code | OMC |
|------|-----------------|-----|
| 执行模式 | 单线程顺序 | 5 种模式，支持并行 |
| Agent 数量 | 单一 AI 实例 | 19 个专属 Agent |
| 任务分发 | 手动指定 | 自动智能路由 |
| 模型选择 | 固定模型 | Haiku/Sonnet/Opus 三级路由 |
| 执行韧性 | 遇错即停 | Ralph 模式持续推进 |
| 知识积累 | 无记忆 | 31+ Skills 自动沉淀 |
| 成本控制 | 无优化 | 节省 30~50% Token |
| Multi-AI | 仅 Claude | Claude + Gemini + Codex |

## 五大执行模式

| 模式 | 关键词 | 适用场景 |
|------|--------|---------|
| **Autopilot** | `autopilot:` | 从无到有构建新项目/新功能，全程自主执行 |
| **Ralph** | `ralph:` | 大规模重构、技术债务清理，持续推进直到验证通过 |
| **Ultrawork** | `ulw:` / `team N:` | 多个独立任务并行，3-5x 速度提升 |
| **Deep Interview** | `/deep-interview` | 需求模糊时先澄清，苏格拉底式追问输出 PRD |
| **Plan / ralplan** | `plan:` / `ralplan:` | 大型项目先规划确认，再持续执行 |

## 19 个专属 Agent

### 构建与分析（7 个）
| Agent | 模型 | 职责 |
|-------|------|------|
| explore | Haiku | 代码库探索、技术栈识别 |
| analyst | Sonnet | 深度代码分析、性能瓶颈识别 |
| planner | Opus | 任务拆解、依赖分析、执行计划 |
| architect | Opus | 架构设计、方案评审、结果验证 |
| debugger | Sonnet | Bug 根因定位、修复方案设计 |
| executor | Sonnet | 代码实现、规范遵循 |
| code-simplifier | Haiku | 消除冗余、提升可维护性 |

**Autopilot 典型流转**：explore → analyst → planner → architect → executor（并行）→ debugger → architect（验证）

### 审查质量（3 个）
- **security-reviewer**（Opus）：OWASP Top 10 扫描、SQL 注入/XSS/CSRF 检查
- **code-reviewer**（Sonnet）：代码风格、可维护性、命名规范
- **critic**（Opus）：全局批判性评审，发现模块间耦合、职责边界模糊等深层问题

### 领域专家（9 个）
document-specialist / test-engineer / designer / writer / qa-tester / scientist / git-master / tracer

## 三级模型智能路由

| 层级 | 适用 Agent | 任务特征 |
|------|-----------|---------|
| Opus（最强） | architect, planner, critic, scientist, security-reviewer | 复杂推理、架构决策、安全评审 |
| Sonnet（均衡） | executor, analyst, debugger, test-engineer 等 | 代码生成、文档编写、常规分析 |
| Haiku（最快） | explore, code-simplifier, git-master, tracer | 快速查找、辅助操作、轻量任务 |

**Ecomode**：将所有可降级任务路由到 Haiku，仅对确实需要复杂推理的任务保留 Sonnet/Opus，实测节省 30~50% Token。

## 31+ 内置 Skills

覆盖前端（8）、后端（7）、测试（5）、DevOps（6）、数据科学（3）、文档（2）六大领域。Skills 本质是**结构化上下文注入**——检测到任务与 trigger 匹配时自动注入，无需每次在 Prompt 中重复规范。

**Autoresearch**（v4.13.0 元技能）：遇到需要最新信息、特定版本 API 或训练数据外的技术时，自动搜索官方文档、GitHub Issues、技术博客，提炼后注入上下文。

## Multi-AI 模式

| AI 角色 | 分工 | 专长 |
|---------|------|------|
| Claude | 指挥官 | 任务拆解、结果汇总、质量验证 |
| Gemini | 设计视觉 | 1M token 大上下文，UI/UX 审查、大规模文档分析 |
| Codex | 代码分析 | 深度静态分析、架构验证、安全审计 |

## Hooks 生命周期

pre-task / post-task / pre-commit / post-commit / on-error / session-start / session-end，支持自定义 Hook（如提交前强制 lint + test）。

## 版本演进

| 版本 | 重要变更 |
|------|---------|
| v1.x | Autopilot + 基础 Agent 系统 |
| v2.x | Swarm/Ultrapilot 并行 + Skills |
| v3.x | MCP 集成 + HUD 状态栏 + Hooks |
| v4.0 | Team 模式 + Multi-AI（Gemini/Codex）|
| v4.13.0 | Autoresearch as Skill + Windows 修复 + ralplan 循环修复 |

## 相关来源

- [[oh-my-claudecode-guide]] —— oh-my-claudecode 深度实战教程
