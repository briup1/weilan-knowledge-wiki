---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Agent Skills 实战：把设计文档（Design）写成 Skill.md
tags: [agent-skills, claude-code, design-doc, skill-system, cursor]
---

# Agent Skills 实战：把设计文档（Design）写成 Skill

## 摘要

本文以设计文档（Design Doc）为例，演示如何将团队设计规范转化为一条可复用的 Agent Skill。核心思路是：把团队设计文档模板（涵盖设计目标、用户场景、信息架构、交互设计、视觉组件、可访问性、交付物七大要素）写入 SKILL.md，使 AI 助手在用户说出「写设计文档」「审一下这份设计」等触发词时，按统一结构输出可直接评审的 Markdown 设计文档，或对已有文档做符合性检查。文章完整展示了从团队规范到 SKILL.md 结构、可选 reference.md 补充规范、可选 scripts 自动化检查、触发方式与团队协作的一整套实战流程，并强调 PRD 定「做什么」、Design 定「怎么做、长什么样、如何交互」的分工关系。

## 核心要点

- **Skill 的目标**：将团队设计文档模板固化到 SKILL.md，使 AI 按统一结构生成或评审 Design Doc，必填节不遗漏、交互与交付物清晰。
- **文档结构（必填节）**：设计目标与范围、用户与关键场景、信息架构、交互设计、视觉与组件、可访问性、交付物；缺项用 `[请补充：xxx]` 占位。
- **SKILL.md 目录结构**：`design-doc/SKILL.md`（主技能文件）+ 可选 `reference.md`（完整模板与规范）+ 可选 `scripts/check-design-sections.sh`（检查必选节）。
- **触发方式**：隐式触发（「写设计文档」「写 Design Doc」「审一下这份设计」等）或显式触发（`/design-doc`）。
- **评审模式**：对已有设计文档输出符合项、缺节列表、交互状态完整性、必改/建议/可选分级修改建议。
- **团队协作**：建议将技能放在项目内 `.cursor/skills/` 并随仓库提交，产品与设计拉代码即有一致模板；新技能或改动走 PR 评审。
- **与 PRD 的衔接**：PRD 定「做什么」，Design 定「怎么做、长什么样、如何交互」，兼具「生成草稿」与「符合性评审」两种用法。

## 原始文件

- [原始文件](../../raw/archive/Agent%20Skills%20实战：把设计文档（Design）写成%20Skill.md)
