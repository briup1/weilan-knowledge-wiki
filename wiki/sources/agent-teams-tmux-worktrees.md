---
type: source
created: 2026-05-18
updated: 2026-05-18
raw: raw/archive/Agent Teams 全景tmux + worktrees 跑 4 个 Claude 并行交付.md
tags: [claude-code, multi-agent, tmux, git-worktrees, parallel-development]
---

# Agent Teams 全景：tmux + worktrees 跑 4 个 Claude 并行交付

**来源**：微信公众号 / 何谓第一等事
**链接**：https://mp.weixin.qq.com/s/wL0E7IaHZlpEiZY1xaecbw

## 摘要

本文是「多 Agent 协作」的工程落地实操指南，拆解如何用 tmux 终端分屏 + Git worktrees 同时运行多个 Claude Code 实例，实现前端、后端、测试、文档的并行交付。核心不是炫技，而是任务拆分、冲突隔离和并行交付的方法论。

## 核心主张

1. **Agent Teams 是一种工作模式，不是一个按钮**。多个 Claude Code 实例在同一个 repo 上并行工作，通过 Git 仓库状态同步，不直接通信。每个实例有自己的终端、worktree 和上下文。
2. **`claude -w` 一键 worktree**。Claude Code 内置 worktree 支持：`-w frontend` 会自动检查、创建 worktree、切换目录并开始执行任务，无需手动 `git worktree add`。
3. **三种任务分派策略**：
   - **按模块分**（前端/后端/测试/文档）：最直观，前提是模块耦合度低
   - **按功能分**（每个 agent 负责完整 feature）：每个 agent 有完整上下文，但可能改到同一个基础组件
   - **按阶段分**（流水线模式）：写代码 → 审代码 → 修代码，避免「自己审自己」
4. **冲突合并的最佳实践**：逐个合并（先合风险最低的文档/测试，最后合前端），每合一个跑一次测试；遇到冲突让 Claude 分析 diff；预防冲突的核心是「不要让两个 agent 同时改同一个文件」。
5. **`/batch` 扇出大规模变更**。适合「同一种改动应用到很多文件」的场景（如改 200 个文件的 import 路径），Claude 自动扫描、分组、启动 sub-agent 并行处理。

## 关键洞察

- 四个 Claude 并行的 token 成本约为单 Agent 的 1.6 倍（基础开销被重复 4 次），但时间从 4 小时压缩到 1 小时。
- Boris Cherny（Claude Code 之父）的实践中是「dozens of Claudes running at all times」，并推荐使用 `/batch` fan out massive changesets。
- 管理 Agent Teams 的核心不是技术，是任务分解——分得越清楚，合并越顺畅。
- 预防冲突的实用技巧：共享类型定义单独一个文件、package.json 修改交给一个 agent 统一处理、每个 agent 开始前声明文件清单。

## 与现有知识的关联

- 补充 [[multi-agent-collaboration]] 中「工程落地」的具体方法
- 与 [[claude-code]] 的 `-w` 参数和 `/batch` 命令直接相关
- 呼应 [[agent-harness]] 中「多智能体架构」的 Planner + Generator + Evaluator 模式

## 原始文件

- [原始文件](../../raw/archive/Agent%20Teams%20%E5%85%A8%E6%99%AFtmux%20+%20worktrees%20%E8%B7%91%204%20%E4%B8%AA%20Claude%20%E5%B9%B6%E8%A1%8C%E4%BA%A4%E4%BB%98.md)
