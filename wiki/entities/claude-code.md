---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [claude-code-gstack, claude-code-essential-projects, claude-code-memory-system, boris-cherny-tips]
tags: [claude-code, ai-programming, terminal, anthropic, agent]
---

# Claude Code

Anthropic 推出的终端级 AI 编程助手，将大语言模型能力直接集成到命令行工作流中，支持代码编辑、文件操作、测试运行和 Agent 协作。

## 一句话定义

Claude Code 是一个运行在终端中的 AI 助手，开发者通过自然语言与之交互，完成从代码编写、重构到测试和部署的全链路开发任务。

## 核心组件与特性

- **终端原生交互**：直接在命令行中对话，无需切换 IDE 或浏览器，支持文件读写、bash 命令执行、代码搜索等操作。
- **CLAUDE.md**：项目级配置文件，记录团队编码规范、项目约束和 AI 操作偏差纠正，使 AI 越用越懂团队习惯，形成复利式工程经验。
- **Skills 系统**：通过 SKILL.md 定义可复用的斜杠命令（如 `/review`、`/ship`），将重复工作流固化为一键触发的专业角色。Skills 可全局安装（`~/.claude/skills/`）或项目级安装（`.claude/skills/`）。
- **子 Agent（Subagents）**：在会话中派生独立的子 Agent 处理特定任务，如代码简化、端到端测试验证，主 Agent 继续并行处理其他工作。
- **Plan 模式**：按两次 Shift+Tab 进入规划模式，先与 AI 反复沟通确认方案，满意后再切换到自动执行模式，通常能一次搞定复杂任务。
- **记忆系统**：本地文件式记忆架构，分 user（用户画像）、feedback（工作指导）、project（项目背景）、reference（外部资源）四类，通过 MEMORY.md 索引管理，支持 KAIROS 日志模式和 /dream 夜间整理。
- **权限与安全管理**：支持 `/permissions` 预授权常用命令、安全模式（`/guard`）、编辑锁定（`/freeze`）和破坏性命令警告（`/careful`），避免使用 `--dangerously-skip-permissions`。
- **MCP 扩展**：通过 Model Context Protocol 连接外部工具（如 Slack、BigQuery、Sentry），将 Claude Code 的能力边界扩展到整个技术栈。
- **PostToolUse 钩子**：用钩子函数自动格式化 AI 生成的代码，处理剩余的格式细节，避免 CI 格式错误。

## 使用指南与最佳实践

1. **规划先行**：大多数会话从 Plan mode 开始，反复沟通直到对方案满意，再切换到 auto-accept edits mode。
2. **维护 CLAUDE.md**：将 AI 的操作偏差和纠正记录到 CLAUDE.md，通过 PR 中的 @.claude 标记补充内容，使经验持续累积。
3. **并行工作**：同时运行多个 Claude Code 实例（本地 + 网页），将不同任务分配给不同标签页，通过系统通知获知哪个需要输入。
4. **斜杠命令固化工作流**：将每天重复多次的内循环工作流写成斜杠命令，存放在 `.claude/commands/`，如 `/commit-push-pr`。
5. **验证反馈循环**：为 Claude 建立工作验证机制（bash 命令、测试套件、浏览器测试等），质量可提升 2-3 倍。
6. **模型选择**：所有任务使用最强模型（Opus 4.5），虽然更大更慢，但几乎不需要人工引导且工具调用能力更强，实际效率更高。

## 相关来源

- [[claude-code-gstack]] —— Garry Tan 的 gstack 多 Agent 协作工作流
- [[claude-code-essential-projects]] —— Claude Code 必备开源项目（Claude How-To、oh-my-claudecode、best-practice）
- [[claude-code-memory-system]] —— Claude Code 源码级记忆系统解析
- [[boris-cherny-tips]] —— Boris Cherny 的 13 个高效使用技巧
