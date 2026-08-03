---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [superpowers-guide]
tags: [bmad, ai-programming, agile, documentation-driven, agent, multi-agent]
---

# BMAD Method

AI 驱动的敏捷开发框架，核心理念是"文档驱动"——先生成 PRD（产品需求文档）、架构设计文档、用户故事等工件，再以这些文档作为"合同"约束 AI 的实现行为。

## 基本信息

| 属性 | 内容 |
|------|------|
| 项目地址 | [github.com/bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) |
| 当前版本 | v6.2.1 |
| Star 数 | 44k+ |
| 本质定位 | 文档驱动敏捷框架 |
| 安装 | `npx bmad-method install`，支持 Claude Code、Cursor 等多平台 |

## 核心特点

- **文档优先**：规格文档是代码实现的"合同"，AI 必须严格按文档实现
- **多角色代理**：内置 12+ 个专业化 AI 代理角色（业务分析师、产品经理、UX 设计师、系统架构师、Scrum Master、开发者、QA 工程师等），不同阶段由不同角色接管
- **规模自适应**：自动根据项目复杂度调整规划深度（0 级 bug 修复到企业级系统）
- **Party Mode**：多个代理角色在同一会话中协作和讨论

## 与 Superpowers 的核心区别

Superpowers 的"头脑风暴"阶段也会产出设计文档，但主要是为了对齐共识，不是强制约束。BMAD 的文档则是"合同"性质，是所有后续实现的强制性参考基准。

- **Superpowers** 重在工程执行纪律（TDD、代码审查、工作流规范）
- **BMAD** 重在需求规格管控（PRD、架构文档、角色专业化）

## 选择建议

- 个人项目或快速迭代 → 单独使用 Superpowers
- 有真实用户、外部集成、安全要求，或需要团队协作的中大型项目 → BMAD + Superpowers 叠加

## 相关实体

- [[superpowers]] —— 工程纪律框架，可与 BMAD 叠加使用
- [[openspec]] —— 需求规格框架，可与 BMAD 互补
- [[openharness]] —— 代理运行引擎

## 相关来源

- [[superpowers-guide]] —— 四款工具的横向对比与选型建议
