---
type: entity
created: 2026-04-20
updated: 2026-04-20
sources: [boris-cherny-tips]
tags: [boris-cherny, claude-code, typescript, anthropic, developer]
---

# Boris Cherny

Claude Code 核心团队成员，TypeScript 专家，被誉为「Claude Code 之父」，主导了 Claude Code 的交互设计和开发者体验优化。

## 一句话定义

Boris Cherny 是 Anthropic 的 Claude Code 核心开发者，TypeScript 生态资深专家，以分享高效 AI 编程实践和推动「复利式工程」理念而闻名。

## 核心背景

- **Claude Code 核心开发**：作为 Claude Code 团队的核心成员，直接参与了产品的交互设计、功能迭代和开发者体验优化。
- **TypeScript 专家**：在 TypeScript 类型系统和工程化实践方面有深厚积累，其技术背景深刻影响了 Claude Code 对代码理解和重构的能力设计。
- **复利式工程倡导者**：提出将每次与 AI 交互的经验沉淀到 CLAUDE.md，使 AI 越用越懂团队习惯和项目约束，形成持续复利的开发效率提升。

## 分享的 13 个高效技巧核心思想

Boris Cherny 分享的技巧围绕一个核心理念：将 Claude Code 视为可完全信任的资深开发者，通过系统性方法最大化 AI 编程效率。

- **并行最大化**：同时运行 5 个 Claude 实例，将标签页编号并通过系统通知获知哪个需要输入。
- **最强模型策略**：所有任务使用 Opus 4.5，虽然更大更慢，但几乎不需要人工引导，实际效率更高。
- **CLAUDE.md 作为团队记忆**：共享并持续更新 CLAUDE.md，记录 AI 的操作偏差和纠正，使 AI 下次规避同样问题。
- **规划先行**：大多数会话从 Plan mode 开始，反复沟通直到对方案满意，再切换到自动执行模式。
- **斜杠命令固化工作流**：将每天重复多次的内循环工作流用斜杠命令实现，存放在 `.claude/commands/`。
- **子智能体自动化**：使用子智能体处理常见工作流，如 code-simplifier、verify-app 等。
- **权限精细化管理**：不使用 `--dangerously-skip-permissions`，而是用 `/permissions` 预先授权安全的常用 bash 命令。
- **MCP 扩展能力边界**：通过 MCP 服务器调用所有工具，如搜索并发布 Slack 消息、运行 BigQuery 查询等。
- **验证反馈循环**：为 Claude 建立工作验证机制，质量可提升 2-3 倍。

## 影响与意义

Boris Cherny 的实践分享不仅提供了具体技巧，更重要的是确立了 AI 辅助编程的范式转变：从「工具使用」到「团队协作」，从「单次交互」到「复利积累」。他的理念直接影响了许多 Claude Code 配套开源项目（如 claude-code-best-practice）的设计方向。

## 相关来源

- [[boris-cherny-tips]] —— Boris Cherny 分享的 13 个高效使用技巧及详细解读
