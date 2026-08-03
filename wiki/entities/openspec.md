---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [superpowers-guide]
tags: [openspec, ai-programming, spec-driven-development, requirement, agent]
---

# OpenSpec

规格驱动开发（Spec-Driven Development，SDD）框架，核心理念是在代码之前添加一个轻量级的规格层，让人和 AI 在动手写代码之前先就需求对齐。

## 基本信息

| 属性 | 内容 |
|------|------|
| 项目地址 | [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) |
| 当前版本 | v1.2.0 |
| Star 数 | 39k+ |
| 本质定位 | 需求规格框架（npm 包）|
| 支持平台 | 20+ AI 工具（Claude Code、Cursor、GitHub Copilot 等）|

## 核心特点

- **每个变更都有专属文件夹**：`proposal.md` + `specs/` + `design.md` + `tasks.md`
- **轻量、渐进式**：不强制完整工作流，可按需使用部分功能
- **流动而非刚性**：允许随时更新任何规格文件
- **斜杠命令驱动**：`/opsx:propose`（提出想法）→ `/opsx:apply`（执行实现）→ `/opsx:archive`（归档）

## 典型工作流

1. `/opsx:propose` —— 提出变更想法
2. 自动生成结构化文件夹（proposal.md、specs/、design.md、tasks.md）
3. `/opsx:apply` —— 基于规格执行实现
4. `/opsx:archive` —— 归档完成变更

## 与 Superpowers 的关系

OpenSpec 主要解决"做什么"（需求规格化），Superpowers 主要解决"怎么做"（工程执行纪律）。两者作用阶段不同，可以组合：先用 OpenSpec 生成规格文档，再用 Superpowers 约束实现过程。

## 相关实体

- [[superpowers]] —— 工程纪律框架，可与 OpenSpec 组合使用
- [[bmad-method]] —— 文档驱动敏捷框架
- [[openharness]] —— 代理运行引擎

## 相关来源

- [[superpowers-guide]] —— 四款工具的横向对比与选型建议
