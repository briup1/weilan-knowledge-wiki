---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [superpowers-guide]
tags: [superpowers, ai-programming, skill-framework, tdd, agent, claude-code]
---

# Superpowers

开源的 AI 编程代理技能框架（Agentic Skills Framework），通过一套 Markdown 格式的 SKILL.md 技能文件，赋予 AI 编程代理经过实战验证的、可组合的工作流规范，使其遵循软件工程最佳实践而非盲目写代码。

## 基本信息

| 属性 | 内容 |
|------|------|
| 项目地址 | [github.com/obra/superpowers](https://github.com/obra/superpowers) |
| 作者 | Jesse Vincent & Prime Radiant |
| 许可证 | MIT |
| 当前版本 | v5.0.7（2026 年 4 月）|
| Star 数 | 146k+ |
| 本质定位 | 工作流规范（Markdown 技能文件）|

## 核心设计哲学

1. **测试驱动开发（TDD）**：永远先写测试，再写实现代码。未经测试覆盖的代码不应存在于代码库中。
2. **系统化优于临时性**：用有章可循的流程替代临时猜测，每个阶段都有明确的步骤和验证标准。
3. **降低复杂度**：遵循 YAGNI 和 DRY 原则，只实现当前真正需要的功能。
4. **证据优于声称**：在宣布工作"完成"之前，必须通过实际验证（如运行测试）来证明有效。

## Skills 技能系统

Skills 是 Superpowers 的核心构成单元，每个技能是一个 Markdown 文件（SKILL.md），包含元数据、操作指令、最佳实践和验证标准。

### 触发方式

- **自动触发**：请求内容与技能描述匹配时自动激活
- **名称触发**：直接提及技能名称（如 "使用 systematic-debugging"）
- **链式触发**：`using-superpowers` 元技能在后台监控并自动调用其他技能

### 内置技能清单

| 分类 | 技能名称 | 功能说明 |
|------|---------|---------|
| 测试 | `test-driven-development` | 执行 RED-GREEN-REFACTOR 循环 |
| 调试 | `systematic-debugging` | 四阶段根因分析流程 |
| 调试 | `verification-before-completion` | 确保问题被真正修复 |
| 协作 | `brainstorming` | Socratic 式设计精化，挖掘真实需求 |
| 协作 | `writing-plans` | 生成详细可操作的实现计划 |
| 协作 | `executing-plans` | 分批执行计划并设置人工检查点 |
| 协作 | `dispatching-parallel-agents` | 并发子代理工作流 |
| 协作 | `requesting-code-review` | 代码审查前的自查清单 |
| 协作 | `receiving-code-review` | 系统性响应代码审查反馈 |
| 协作 | `using-git-worktrees` | 使用 Git Worktrees 并行开发多分支 |
| 协作 | `finishing-a-development-branch` | 合并/PR 决策工作流 |
| 协作 | `subagent-driven-development` | 快速迭代，两阶段审查 |
| 元技能 | `writing-skills` | 按最佳实践创建自定义技能 |
| 元技能 | `using-superpowers` | 技能系统入口，协调整体使用 |

## 七阶段标准开发工作流

Superpowers 定义了一套从零到部署的强制性工作流：

1. **头脑风暴（brainstorming）**：通过 Socratic 式提问厘清真实需求，产出设计文档
2. **建立工作区（using-git-worktrees）**：创建隔离的开发环境，确保基线干净
3. **制定计划（writing-plans）**：将设计分解为 2-5 分钟可执行的小任务
4. **执行计划（subagent-driven-development）**：主代理派遣子代理执行，两阶段审查
5. **测试驱动开发（test-driven-development）**：RED-GREEN-REFACTOR 循环
6. **代码审查（requesting-code-review）**：实现一致性、测试覆盖、安全性能检查
7. **收尾合并（finishing-a-development-branch）**：完整测试后由用户决定合并/PR/保留/丢弃

## 安装方式

| 平台 | 安装命令 |
|------|---------|
| Claude Code（推荐）| `/plugin install superpowers@claude-plugins-official` |
| Cursor | `/add-plugin superpowers` |
| Codex | 从 GitHub raw 自动安装或手动符号链接 |
| OpenCode | 从 GitHub raw 自动安装 |
| Gemini CLI | `gemini extensions install https://github.com/obra/superpowers` |
| GitHub Copilot CLI | `copilot plugin install superpowers@superpowers-marketplace` |

## 与同类工具的对比

Superpowers 与 [[bmad-method]]、[[openspec]]、[[openharness]] 并非竞争关系，而是覆盖 AI 开发流水线不同层次的互补工具：

| 维度 | Superpowers | BMAD Method | OpenSpec | OpenHarness |
|------|-------------|-------------|----------|-------------|
| 解决什么 | 代理"怎么做事" | 代理"该做什么文档" | 代理"做什么需求" | 代理"能做什么" |
| 本质 | 工作流规范 | 文档驱动敏捷框架 | 需求规格框架 | 代理运行引擎 |
| 运行方式 | 寄生于现有代理 | 寄生于现有代理 | 寄生于现有代理 | 独立运行程序 |
| TDD 支持 | 核心强制要求 | 非核心 | 不涉及 | 不涉及 |
| 适合规模 | 个人+小团队 | 中大型项目 | 任意规模 | 研究+自建场景 |

**最优组合（完整链路）**：OpenSpec（定义做什么）→ BMAD（规划文档）→ Superpowers（执行纪律）→ OpenHarness（运行引擎，仅在需要自建时使用）

## 与 Claude Code Skills 的关系

[[claude-code-skills]] 是 Claude Code 原生的 SKILL.md 扩展机制，Superpowers 则是跨平台的独立技能框架，两者格式兼容。关键区别：

- Claude Code Skills 强调**自定义斜杠命令**和团队协作规范
- Superpowers 强调**强制性工作流**和 TDD 工程纪律

两者可以叠加使用：Claude Code Skills 处理团队特有的规范模板，Superpowers 处理通用的开发工作流。

## 自定义技能

用户可在 `~/.agents/skills/` 目录下创建自定义 SKILL.md 文件，description 字段决定自动触发条件，重启代理后即可生效。社区贡献通过 Fork 主仓库提交 PR。

## 相关来源

- [[superpowers-guide]] —— Superpowers 完全指南：安装教程、横向对比、七阶段工作流详解
