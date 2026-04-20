---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [claude-code-essential-projects]
tags: [cursor, ai-editor, vscode, ide, ai-programming]
---

# Cursor

AI 驱动的代码编辑器，基于 VS Code 构建，通过深度集成大语言模型提供内联 AI 编辑、智能代码生成和项目级理解能力。

## 一句话定义

Cursor 是一个基于 VS Code 的 AI 原生代码编辑器，将大语言模型能力深度嵌入编辑体验，支持内联编辑、代码生成和项目级智能分析。

## 核心组件与特性

- **VS Code 兼容**：完全基于 VS Code 构建，保留所有插件生态和快捷键习惯，迁移成本极低。
- **内联 AI 编辑（Inline Edit）**：在代码行内直接调用 AI 进行修改，无需切换面板或复制粘贴，支持「选中 → 描述需求 → 即时替换」的流畅流程。
- **Composer**：项目级 AI 编程助手，可以理解整个代码库的上下文，进行跨文件重构、功能实现和架构调整。
- **Tab 自动补全**：基于代码上下文和项目历史的智能 Tab 补全，不仅补全单行长度的代码，还能预测多行逻辑块的结构。
- **Agent 模式**：支持让 AI 自主执行多步骤任务，如「添加用户认证功能」会自动创建模型、路由、中间件和测试文件。
- **Skills 支持**：Cursor 支持通过 `.cursor/skills/` 目录安装自定义 Skills，与 Claude Code 的 Skills 系统类似，允许团队将设计规范、编码标准固化为可复用的 AI 工作流。
- **多模型支持**：支持 Claude、GPT-4、Gemini 等多种模型，用户可按任务类型选择最适合的模型。

## 与 Claude Code 的对比

| 维度 | Cursor | Claude Code |
|------|--------|-------------|
| 形态 | GUI 编辑器 | 终端 CLI |
| 交互方式 | 内联编辑 + 侧边栏聊天 | 纯自然语言对话 |
| 代码修改 | 可视化 diff，一键接受/拒绝 | 命令行确认或自动接受 |
| 适用场景 | 日常编码、可视化调试 | 批量重构、自动化工作流、多 Agent 协作 |
| 学习曲线 | 低（VS Code 用户零成本） | 中（需熟悉终端交互模式） |

## 使用指南与最佳实践

1. **从 VS Code 平滑迁移**：直接导入 VS Code 配置和插件，保持原有工作流不变。
2. **善用 Composer 处理复杂任务**：对于跨文件重构或新功能实现，使用 Composer 而非内联编辑，以获得更好的项目级上下文理解。
3. **结合终端工具使用**：Cursor 适合日常编码和可视化操作，复杂自动化工作流可配合 Claude Code 在终端中执行。
4. **团队 Skills 共享**：将团队设计规范和编码标准写成 Skill.md 放在 `.cursor/skills/`，确保团队成员使用一致的 AI 辅助标准。

## 相关来源

- [[claude-code-essential-projects]] —— Claude Code 必备开源项目，包含 Cursor 相关生态对比
