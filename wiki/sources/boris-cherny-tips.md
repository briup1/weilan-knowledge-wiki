---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/结合Claude Code之父Boris Cherny分享13个高效使用技巧，配以详细的解读，让你Vibe Code更高效.md
tags: [claude-code, boris-cherny, vibe-coding, best-practice, tips, claude-md]
---

# 结合 Claude Code 之父 Boris Cherny 分享 13 个高效使用技巧

## 摘要

本文结合 Boris Cherny（Claude Code 核心团队成员）分享的 13 个高效使用技巧，并配以作者的实际开发经验进行详细解读。核心思想是：将 Claude Code 视为可完全信任的资深开发者，通过并行运行多个实例、使用最强模型（Opus 4.5）、维护共享的 CLAUDE.md 文件积累团队经验、规划先行（Plan mode）、将固定工作流打包成斜杠命令和子智能体、利用 MCP 扩展能力边界、建立验证反馈循环等方式，最大化 AI 编程效率。文章强调「复利式工程」（Compounding Engineering）理念——将每次与 AI 交互的经验沉淀到 CLAUDE.md，使 AI 越用越懂团队习惯和项目约束。

## 核心要点

- **尽可能并行**：同时运行 5 个 Claude 实例，将标签页编号并通过系统通知获知哪个需要输入，最大化工作效率。
- **网页和本地同时并行**：在 claude.ai/code 和本地 Claude Code 同时运行多个会话，甚至用手机开启会话稍后查看进度。
- **使用最强模型**：所有任务使用 Opus 4.5，虽然更大更慢，但几乎不需要人工引导且工具调用能力更强，实际效率更高。
- **维护 CLAUDE.md**：团队共享并持续更新 CLAUDE.md，记录 AI 的操作偏差和纠正，使 AI 下次规避同样问题；通过 PR 中的 @.claude 标记补充内容。
- **规划先行（Plan mode）**：大多数会话从 Plan mode（按两次 Shift+Tab）开始，反复沟通直到对方案满意，再切换到 auto-accept edits mode，通常能一次搞定。
- **斜杠命令固化工作流**：将每天重复多次的「内循环」工作流用斜杠命令实现，存放在 `.claude/commands/`，如 `/commit-push-pr` 每天使用几十次。
- **子智能体自动化**：使用子智能体处理常见工作流，如 code-simplifier（代码简化）、verify-app（端到端测试）等。
- **PostToolUse 钩子**：用钩子函数格式化 Claude 生成的代码，处理剩下的 10% 格式细节，避免 CI 格式错误。
- **权限管理**：不使用 `--dangerously-skip-permissions`，而是用 `/permissions` 预先授权安全的常用 bash 命令，设置保存在 `.claude/settings.json` 中并与团队共享。
- **MCP 扩展能力**：通过 MCP 服务器调用所有工具，如搜索并发布 Slack 消息、运行 BigQuery 查询、从 Sentry 获取错误日志等。
- **长任务技巧**：完成后通过后台代理自行验证、使用 Stop 钩子执行验证、在沙箱中使用 `--permission-mode=dontAsk` 避免权限提示阻断连续工作流。
- **验证反馈循环**：为 Claude 建立工作验证机制（bash 命令、测试套件、浏览器测试等），质量可提升 2-3 倍；每次提交改动时通过 Chrome 扩展进行全流程测试。
- **复利式工程**：将开发经验沉淀到 CLAUDE.md，AI 越用越懂团队习惯和项目约束，形成复利效应。

## 原始文件

- [原始文件](../../raw/archive/结合Claude%20Code之父Boris%20Cherny分享13个高效使用技巧，配以详细的解读，让你Vibe%20Code更高效.md)
