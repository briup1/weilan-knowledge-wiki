---
type: concept
created: 2026-04-20
updated: 2026-04-20
sources: [claude-code-gstack, agent-skills-design, fireworks-tech-graph]
tags: [claude-code-skills, skill-system, agent, workflow, slash-command]
---

# Claude Code Skills

Claude Code 的可扩展技能系统，允许用户通过 SKILL.md 文件定义自定义斜杠命令和工作流，将重复性任务固化为可一键触发的专业 AI 角色。

## 定义

Claude Code Skills 是一套基于 SKILL.md 配置文件的扩展机制。用户或团队将特定领域的工作流程、规范模板和上下文知识写入 SKILL.md，Claude Code 在检测到触发词或斜杠命令时，自动加载对应的 Skill 并按预定义流程执行任务。

## 核心原理

### SKILL.md 格式

一个 Skill 通常包含以下要素：

- **元信息**：Skill 名称、描述、版本、作者。
- **触发方式**：隐式触发词（如「写设计文档」「审一下这份设计」）或显式斜杠命令（如 `/design-doc`）。
- **上下文注入**：Skill 加载时注入到系统提示中的背景知识和约束条件。
- **工作流定义**：步骤化的任务执行流程，可包含条件分支和循环。
- **可选资源**：reference.md（补充规范文档）、scripts/（自动化检查脚本）。

### 目录结构

Skills 可安装在两个层级：

```
~/.claude/skills/<skill-name>/          # 全局安装，所有项目可用
├── SKILL.md
├── reference.md（可选）
└── scripts/（可选）

./.claude/skills/<skill-name>/          # 项目级安装，随仓库共享
├── SKILL.md
├── reference.md（可选）
└── scripts/（可选）
```

项目级安装推荐用于团队协作，确保所有成员使用一致的 Skill 配置。

### 触发机制

- **隐式触发**：用户输入包含触发词时，Claude Code 自动识别并加载对应 Skill。
- **显式触发**：用户输入 `/skill-name` 斜杠命令直接调用。
- **上下文感知**：Skill 可根据当前项目结构、文件类型动态调整行为。

### 典型 Skill 示例

- **设计文档 Skill**：将团队设计规范模板（设计目标、用户场景、信息架构、交互设计、视觉组件、可访问性、交付物）固化为 SKILL.md，使 AI 按统一结构生成或评审 Design Doc。
- **fireworks-tech-graph**：用自然语言生成工业级架构图的 Skill，支持 5 种视觉风格和 8 种图表类型，触发词包括「画图」「帮我画」「生成图」「架构图」等。
- **gstack 角色 Skill**：gstack 提供 28 个专业角色 Skill，覆盖规划（`/office-hours`、`/plan-ceo-review`）、构建（`/review`、`/investigate`）、质量（`/qa`、`/cso`）、发布（`/ship`、`/land-and-deploy`）四个阶段。

## 与其他工具扩展机制的对比

| 维度 | Claude Code Skills | VS Code 插件 | Cursor 插件 |
|------|-------------------|-------------|-------------|
| 扩展方式 | SKILL.md 配置文件 | TypeScript/JavaScript 代码 | 类似 VS Code 插件 |
| 开发门槛 | 低（写 Markdown） | 高（需编程） | 高（需编程） |
| 触发方式 | 自然语言 / 斜杠命令 | 命令面板 / 快捷键 | 命令面板 / 快捷键 |
| 适用场景 | AI 工作流、规范模板 | UI 扩展、编辑器功能 | AI 辅助编码 |
| 团队协作 | 随仓库共享 | 通过市场发布 | 通过市场发布 |

## 适用场景

- **团队规范固化**：将设计文档模板、代码审查清单、发布流程检查项写入 Skill，确保团队输出一致。
- **重复工作流自动化**：将每天重复多次的内循环工作流（如 `/commit-push-pr`）固化为斜杠命令。
- **领域知识注入**：为特定技术栈（如 FastAPI + React）创建 Skill，注入最佳实践和常见模式。
- **质量门禁**：创建自动化检查 Skill，在提交前验证代码风格、测试覆盖率和文档完整性。

## 最佳实践

1. **从实际痛点出发**：不要为造 Skill 而造，先观察团队每天重复 3 次以上的工作流。
2. **保持简洁**：一个 Skill 聚焦一个明确任务，避免过度复杂化。
3. **版本控制**：将项目级 Skills 纳入 git 管理，变更走 PR 评审。
4. **补充 reference.md**：对于复杂规范，将完整模板放在 reference.md，SKILL.md 只保留核心流程。
5. **测试验证**：为 Skill 编写测试用例，确保触发词和输出格式符合预期。

## 相关来源

- [[claude-code-gstack]] —— gstack 的 28 个专业角色 Skill 体系
- [[agent-skills-design]] —— 将设计文档写成 Skill 的实战教程
- [[fireworks-tech-graph]] —— 自然语言生成架构图的 Skill 案例
