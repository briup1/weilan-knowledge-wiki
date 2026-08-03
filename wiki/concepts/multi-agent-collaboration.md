---
type: concept
created: 2026-04-20
updated: 2026-05-18
sources: [claude-code-gstack, hermes-agent-setup, openmaic, agent-harness-anatomy, agent-teams-tmux-worktrees, oh-my-claudecode-guide]
tags: [multi-agent, collaboration, team-mode, agent-orchestration, ai-programming]
---

# 多 Agent 协作

将复杂任务分解给多个专业 AI Agent 并行处理，通过角色分工和通信机制实现协同工作，从而突破单一 Agent 的上下文和能力限制。

## 定义

多 Agent 协作是一种分布式 AI 工作流架构。复杂项目被拆分为多个子任务，每个子任务由具备特定角色和专业能力的 Agent 负责。Agent 之间通过结构化通信交换信息、同步进度、解决冲突，最终整合各 Agent 的输出完成整体目标。

## 核心原理

### 角色分工模型

多 Agent 系统的核心是将「一个通用助手」转变为「一个专业团队」。典型角色包括：

- **规划者（Planner）**：负责需求分析、任务拆解和进度安排。如 gstack 的 `/office-hours`（产品思路重构）和 `/plan-ceo-review`（需求审视）。
- **架构师（Architect）**：负责技术方案设计和架构把关。如 `/plan-eng-review` 角色。
- **开发者（Developer）**：负责具体代码实现，可按技术栈细分为前端 Agent、后端 Agent、DevOps Agent。
- **审查者（Reviewer）**：负责代码审查和质量把关。如 `/review`、`/codex`（独立代码审查第二意见）。
- **测试者（Tester）**：负责自动化测试和 QA。如 `/qa`、`/benchmark` 角色。
- **发布者（Releaser）**：负责部署和发布流程。如 `/ship`、`/land-and-deploy`、`/canary` 角色。

### 通信机制

Agent 之间的协作依赖以下通信模式：

- **主从模式**：一个主 Agent（Orchestrator）协调多个子 Agent，分配任务并整合结果。Claude Code 的 Team Mode 采用此模式。
- **消息传递**：Agent 通过共享状态或消息队列交换中间结果，如 gstack 中前端 Agent 将 API 契约传递给后端 Agent。
- **并行执行**：多个 Agent 同时处理独立子任务，通过 tmux 等工具在终端中并行运行多个 CLI worker。
- **评审循环**：一个 Agent 产出结果，另一个 Agent 独立审查并提出修改意见，迭代直至通过。

### Team Mode（团队模式）

Claude Code 的 Team Mode 是多 Agent 协作的具体实现：

- **并行启动**：同时启动多个 Agent 实例，每个实例承担不同角色。
- **相互通信**：Agent 之间可以发送消息、共享文件和同步状态。
- **协作完成**：典型场景如前端/后端/DevOps Agent 并行开发，将全栈应用开发从 8-10 小时缩短到 3-4 小时。

### 工作流编排

oh-my-claudecode（OMC）定义了标准的多 Agent 协作流程：

```
team-plan → team-prd → team-exec → team-verify → team-fix
```

- **plan**：多 Agent 共同分析需求，生成详细计划。
- **prd**：将计划转化为产品需求文档，各 Agent 确认接口和边界。
- **exec**：并行执行开发任务。
- **verify**：独立 Agent 进行测试和审查。
- **fix**：根据验证结果修复问题，循环直至通过。

## Agent Teams 工程模式

当多个 Claude Code 实例在同一 repo 上并行工作时，需要解决**隔离**和**合并**两个核心问题：

**隔离：Git Worktrees**
- `claude -w <name>` 自动创建 worktree，每个实例独立工作目录
- 共享同一个 .git 目录（commit 历史、分支、remote 统一）
- 文件系统层面完全隔离，谁也不碰谁的东西

**任务分派策略**：
| 策略 | 分配方式 | 适用条件 |
|------|---------|---------|
| 按模块分 | 前端/后端/测试/文档各一个 Agent | 模块耦合度低，文件不重叠 |
| 按功能分 | 每个 Agent 负责完整 feature | 每个 Agent 有完整上下文，但可能改到同一基础组件 |
| 按阶段分 | 写代码 → 审代码 → 修代码 | 需要 code review，避免「自己审自己」 |

**合并最佳实践**：
- 逐个合并（先文档→测试→后端→前端），每合一个跑一次测试
- 遇到冲突让 Claude 分析 diff
- 预防冲突：共享类型定义单独文件、package.json 统一处理、每个 Agent 开始前声明文件清单

**成本**：四个 Claude 并行 token 成本约为单 Agent 的 1.6 倍，但时间从 4 小时压缩到 1 小时。

### `/batch` 扇出大规模变更

适合「同一种改动应用到很多文件」的场景（如改 200 个文件的 import 路径）。Claude 自动扫描、按目录分组、为每组启动 sub-agent 并行处理、合并结果。

## OMC 19 Agent 体系

[[oh-my-claudecode]] 提供了最完整的工程化多 Agent 体系：

**构建与分析（7 个）**：explore → analyst → planner → architect → executor（并行）→ debugger → architect（验证）

**审查质量（3 个）**：security-reviewer / code-reviewer / critic（构成多维度代码审查流水线）

**领域专家（9 个）**：document-specialist / test-engineer / designer / writer / qa-tester / scientist / git-master / tracer

**三级模型路由**：Haiku（快速查找）→ Sonnet（代码生成）→ Opus（复杂推理），根据任务复杂度自动选择，Ecomode 激进化降级节省 30-50% token。

## 与其他协作模式的对比

| 维度 | 单 Agent 串行 | 多 Agent 协作 | 人类团队协作 |
|------|-------------|-------------|-----------|
| 执行速度 | 慢（串行处理） | 快（并行处理） | 中（受限于人力） |
| 上下文容量 | 受限于单一会话窗口 | 每个 Agent 专注子集 | 人类记忆和沟通成本 |
| 一致性 | 高（单一思维链） | 中（需协调冲突） | 中（需会议对齐） |
| 成本 | 中 | 高（多个实例并行） | 最高 |
| 适用复杂度 | 简单到中等任务 | 复杂项目、多模块系统 | 战略决策、创意工作 |

## 适用场景

- **全栈应用开发**：前端 Agent + 后端 Agent + DevOps Agent 并行开发，将开发周期从数天压缩到数小时。
- **内容生产流水线**：CEO Agent（选题）+ 数据分析 Agent（数据整理）+ 写作 Agent（撰写）+ 审核 Agent（校对），将 4-6 小时工作压缩到 40 分钟。
- **代码审查与质量保证**：独立审查 Agent 对主开发 Agent 的产出进行第二意见审查，提升代码质量。
- **教育互动课堂**：OpenMAIC 中 AI 教师、AI 同学、AI 导演等多 Agent 协作生成沉浸式学习体验。
- **复杂数据分析**：数据清洗 Agent、建模 Agent、可视化 Agent 并行处理大数据项目。

## 挑战与最佳实践

**挑战**：
- **冲突解决**：多个 Agent 对同一文件或接口的修改可能产生冲突，需要明确的锁机制和合并策略。
- **通信开销**：Agent 间频繁通信可能消耗大量 token，需要设计高效的信息交换格式。
- **一致性维护**：确保所有 Agent 对项目目标和约束的理解保持一致。

**最佳实践**：
1. **明确角色边界**：每个 Agent 的职责范围清晰定义，避免重叠和遗漏。
2. **标准化接口**：Agent 之间通过约定好的 API 契约和数据格式通信。
3. **智能模型路由**：简单任务自动路由到轻量级模型（如 Haiku），节省 30-50% token 成本。
4. **阶段性检查点**：在 plan → prd → exec → verify 各阶段设置检查点，确保质量 gate 通过后再进入下一阶段。
5. **从双 Agent 开始**：不要一开始就启动 10 个 Agent，先从 2-3 个角色的协作开始，逐步扩展。

## Harness 视角下的子 Agent 编排

从 [[agent-harness]] 视角看，子 Agent 编排是"并行化的艺术"——当任务复杂度超过单个 Agent 处理能力时的扩展手段。存在两种核心哲学：**中心化管理 vs 去中心化协作**。

### Claude Code 三种执行模型

| 模型 | 隔离级别 | 通信方式 | 适用场景 |
|------|---------|---------|---------|
| Fork | 父上下文字节级精确副本 | 子 Agent 完成后结果返回父 Agent | 完全独立的并行任务 |
| Teammate | 独立终端面板 | 基于文件的邮箱通信，可互相直接通信 | 需协作但不完全独立的任务 |
| Worktree | 各自 git worktree 独立分支 | Git merge 合并 | 最彻底隔离，代码变更互不干扰 |

### OpenAI 两种编排模式

**Handoffs（交接）**：分流 Agent 将对话完全转移给专业 Agent，专业 Agent 成为活跃 Agent。适用于专业 Agent 需要拥有对话控制权的场景。

**Agents-as-Tools（工具模式）**：管理 Agent 保持控制权，将专业 Agent 作为工具调用，结果返回管理 Agent。适用于需要综合多个专家意见的场景。

### Token 经济学

实际测试表明 **Agent Teams 模式在大规模并行任务中通常比子 Agent 模式省 3-5 倍 token**：子 Agent 编排器上下文随每个结果增长，Teams 模式每个 Agent 只加载当前任务相关上下文。

## 相关来源

- [[claude-code-gstack]] —— Garry Tan 的 gstack 多 Agent 协作工作流，28 个专业角色
- [[hermes-agent-setup]] —— Hermes Agent 框架的 Skills 体系和多 Agent 支持
- [[openmaic]] —— 清华大学 OpenMAIC 多智能体互动课堂平台
- [[agent-harness-anatomy]] —— Agent Harness 十二大模块深度解析
- [[agent-teams-tmux-worktrees]] —— Agent Teams 并行交付工程实践
- [[oh-my-claudecode-guide]] —— oh-my-claudecode 19 Agent 体系深度解析
