---
type: source
created: 2026-05-18
updated: 2026-05-18
raw: raw/archive/Superpowers 完全指南：用它少返工80%.md
tags: [superpowers, ai-programming, skill-framework, bmad, openspec, openharness, tdd]
---

# Superpowers 完全指南：用它少返工80%

程康健撰写的 Superpowers 深度指南，涵盖从零开始的安装教程、四款 AI 编程框架的横向对比、七阶段完整工作流详解以及自定义技能高级用法。

## 来源信息

- **作者**：程康健
- **发布时间**：2026-04-11
- **原始链接**：[微信公众号](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487617&idx=1&sn=49fee04bf4d412a7c444d0ea4f750fe4)

## 核心主张

1. **Superpowers 是给 AI 代理装"工作手册"的框架**：它不是独立的 AI 工具，而是一套 Markdown 格式的 SKILL.md 技能文件，附加在现有代理工具（Claude Code、Cursor、Codex 等）上，强制 AI 遵循软件工程最佳实践。

2. **四款工具互补而非竞争**：Superpowers（工程纪律）、BMAD Method（文档驱动敏捷）、OpenSpec（规格驱动开发）、OpenHarness（代理运行引擎）覆盖 AI 开发流水线的四个不同层次，最优组合是 OpenSpec → BMAD → Superpowers → OpenHarness（仅在需要自建时使用）。

3. **TDD 是不可妥协的核心**：Superpowers 严格遵循 RED-GREEN-REFACTOR 循环，未测试覆盖的代码会被要求删除并重新开始。

4. **七阶段工作流强制工程纪律**：头脑风暴 → Git Worktree → 写计划 → 子代理执行 → TDD → 代码审查 → 收尾合并。代理不会擅自合并代码，所有涉及主分支的操作都需要用户明确确认。

5. **子代理驱动开发是最大效率杠杆**：主代理为每个任务派遣全新子代理，上下文隔离、两阶段审查（规格合规性 + 代码质量），可连续自主工作数小时。

## 工具横向对比速览

| 维度 | Superpowers | BMAD Method | OpenSpec | OpenHarness |
|------|-------------|-------------|----------|-------------|
| 本质定位 | 工作流规范（Markdown） | 文档驱动敏捷框架 | 需求规格框架（npm） | 代理运行引擎（Python） |
| 解决什么 | 代理"怎么做事" | 代理"该做什么文档" | 代理"做什么需求" | 代理"能做什么" |
| Star 数 | 146k | 44k | 39k | 8.6k |
| 成熟度 | 高（v5.0.7） | 高（v6.2.1） | 中（v1.2.0） | 低（v0.1.0） |
| TDD 支持 | 核心强制 | 非核心 | 不涉及 | 不涉及 |
| 国内模型 | 不支持 | 不支持 | 不支持 | 支持 |

## 关键技能详解

- **brainstorming**：Socratic 式提问厘清真实需求，产出设计文档
- **writing-plans**：将设计分解为 2-5 分钟可执行的小任务，精确到文件路径和可运行代码
- **subagent-driven-development**：子代理上下文隔离执行，两阶段审查
- **test-driven-development**：RED-GREEN-REFACTOR 强制循环
- **systematic-debugging**：四阶段根因分析（信息收集→假设形成→验证假设→修复验证）
- **dispatching-parallel-agents**：并发子代理处理独立任务

## 选型建议

- **个人开发者快速上手**：直接使用 Superpowers
- **中大型团队项目**：BMAD（规划）+ Superpowers（执行）
- **需求对齐优先**：OpenSpec（需求层）+ Superpowers（执行层）
- **研究代理原理/国内模型**：OpenHarness

## 相关实体

- [[superpowers]] —— Superpowers 技能框架
- [[bmad-method]] —— BMAD 文档驱动敏捷框架
- [[openspec]] —— OpenSpec 规格驱动开发框架
- [[openharness]] —— OpenHarness 代理运行引擎

## 原始文件

- [原始文件](../../raw/archive/Superpowers%20完全指南：用它少返工80%.md)
