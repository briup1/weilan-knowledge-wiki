---
type: entity
created: 2026-05-18
updated: 2026-05-18
sources: [warp-guide]
tags: [terminal, ai-terminal, ide, developer-tools, rust]
---

# Warp

Warp 是一款由 Rust 构建的现代智能终端（Agentic Development Environment），由前 Google 工程师 Zach Lloyd 于 2021 年创立。目前拥有 70 万+ 开发者用户，支持 macOS / Linux / Windows。

## 核心定位

Warp 的定位不是「更好看的终端」，而是**将终端升级为开发者的智能工作伙伴**。它把现代 IDE 的编辑体验、AI 智能助手、团队协作能力融为一体。

## 核心特性

### Block 化输出
每条命令的输入与输出被封装为独立的可操作单元（Block），而非传统终端的连续文本流：
- 精确导航：Cmd/Ctrl + Up/Down 在 Block 间快速跳转
- 一键复制：仅复制该命令的输出（无需手动框选）
- 独立分享：每个 Block 可生成唯一 Permalink
- AI 关联：失败 Block 右下角自动出现 Get Help 按钮，AI 分析错误

### IDE 级命令行输入
- 鼠标点击精确定位光标
- 多光标编辑（类似 VS Code）
- Vim / Emacs 键位模式
- 语法高亮：不同命令参数以不同颜色显示
- 400+ CLI 工具智能补全（git、docker、kubectl、npm、pip 等），含自动纠错

### AI 原生集成
| 功能 | 触发方式 | 说明 |
|------|---------|------|
| 自然语言生成命令 | `#` + 空格 | 描述需求，AI 生成 shell 命令 |
| AI 助手侧边栏 | Ctrl + Space | 调试错误、解释命令、生成脚本 |
| Agent Mode | Ctrl + Shift + I | AI 自主规划并执行复杂任务 |
| Get Help | 失败 Block 按钮 | AI 自动读取输出上下文并诊断 |

### Warp Drive — 知识与命令管理中心
- **Workflows**：常用命令模板化，支持参数占位符（如 `{{branch_name}}`）和 enum 类型参数
- **Notebooks**：交互式文档，Markdown 与可运行 Shell 代码块混合编排
- **环境变量管理**：一键切换 dev/staging/prod，支持动态引用 1Password / AWS Secrets Manager

### 团队协作
- **Block Permalink**：精确分享某条命令及其输出，告别截图
- **共享 Warp Drive**：团队共享 Workflows、Notebooks、环境变量
- **Session 共享**：实时共享终端会话，类似屏幕共享

## 与 Claude Code / Codex 集成

Warp 的 Agent Toolbelt 功能支持在终端中运行第三方 AI 编程代理：
- 支持 [[claude-code]]、[[codex]]、OpenCode 等
- 提供富文本输入区域、代码审查界面和通知提示
- 在 Warp 中直接审查 AI 生成的 diff 并一键应用

**推荐组合**：Warp + Claude Code，在不离开终端的情况下完成代码编写、测试、调试的完整循环。

## 安全特性

- **Secret Redaction**：命令输出中的 API Key、Token、密码自动替换为 `[REDACTED]`
- 分享 Block Permalink 或截图时自动脱敏
- 可配置自定义脱敏规则（正则表达式）

## 相关来源

- [[warp-guide]] —— Warp 完全指南：70万开发者都在用的AI终端
