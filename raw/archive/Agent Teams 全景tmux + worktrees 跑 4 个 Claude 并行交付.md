---
title: "Agent Teams 全景:tmux + worktrees 跑 4 个 Claude 并行交付"
source: "https://mp.weixin.qq.com/s/wL0E7IaHZlpEiZY1xaecbw"
author:
  - "[[何谓第一等事]]"
published:
created: 2026-05-18
description: "一个 Claude 写代码只是工具，四个 Claude 并行交付才像团队。本文拆解如何用 tmux + Git worktrees 同时跑多个 Claude：前端、后端、测试、文档各自开工，互不冲突，最后逐个合并。核心不是炫技，而是任务拆分、冲突隔离和并行交付方法论。"
tags:
  - "clippings"
---
何谓第一等事 *2026年4月29日 07:49*

关键词：Claude Code、Agent Teams、Claude 并行开发、tmux、Git worktrees、AI 编程助手、多 Agent 协作、Claude Code 教程、AI 自动化开发、并行交付、AI Agent 团队、Claude sub-agent、/batch、AI 代码生成、程序员效率工具、AI 工程实践、Claude 多实例、Git 分支管理、AI 开发工作流、Boris Cherny

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/SgR2Za9GiaQcyllfudY6BYOQ6rNlEwp8NdgdB3aiaZYoIibWWaP6KIjwBd5C78EzrL3fDmcwPJjylrNriaicibg9TnG7Cn2YVWlA8xdlSicVUf0iao8/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

Agent Teams 全景封面

---

一个 Claude 写代码不稀奇。

四个 Claude 同时在你的 repo 里写代码，互不打架，各自提 PR，最后 merge 到一起。这才稀奇。

这不是实验室 demo。Boris Cherny 在推特上说过:

> ★
> 
> dozens of Claudes running at all times
> 
> — @bcherny

不是一个 Claude 跑快点，是几十个 Claude 同时跑。

这篇是 05 篇(Sub-agents 与并行)的续集。05 讲原理:什么是 sub-agent，什么是 worktree，怎么派活。这篇讲工程落地:你坐在电脑前，怎么真正跑起来 4 个 Claude 并行交付一个完整功能。

---

## Agent Teams 是什么

先把概念摆正。

Agent Teams 不是一个按钮。它是一种工作模式:多个 Claude Code 实例在同一个 repo 上并行工作，通过共享任务池协调分工。

每个 Claude 实例是一个独立进程，有自己的终端、自己的 worktree、自己的上下文。它们之间不直接通信，而是通过 Git 仓库的状态来同步。

想象一个办公室。四个程序员坐在四张桌子前，面前各有一台电脑，屏幕上各打开各自的代码分支。他们不互相说话，但都在看同一块白板上写的任务清单。做完一个就把白板上对应那行打个勾。

Agent Teams 就是这个画面，只不过四个程序员都是 Claude。

---

## tmux:你的控制台

四个 Claude 跑在四个终端里。你怎么同时看？

答案是 tmux。

tmux 把一个终端窗口切成多个 pane，每个 pane 跑一个 Claude Code 实例。你坐在一块屏幕前，同时看到四个 Claude 在干什么。

### 基本操作

```
# 创建一个新的 tmux 会话
tmux new-session -s agent-team

# 横切一刀
Ctrl-b %

# 竖切一刀
Ctrl-b "

# 切成 4 个 pane 的快捷方式
tmux new-session -s agent-team \; \
  split-window -h \; \
  split-window -v \; \
  select-pane -t 0 \; \
  split-window -v
```

切完之后你有一个 2x2 的网格。左上、右上、左下、右下，各一个终端。

### 每个 pane 启动一个 Claude

```
# pane 0: 前端 agent
cd ~/project && claude -w frontend "实现用户登录页面"

# pane 1: 后端 agent
cd ~/project && claude -w backend "实现登录 API 接口"

# pane 2: 测试 agent
cd ~/project && claude -w tests "为登录功能编写端到端测试"

# pane 3: 文档 agent
cd ~/project && claude -w docs "更新 API 文档,添加登录接口说明"
```

`claude -w` 的 `-w` 参数指定 worktree 名称。Claude Code 会自动创建对应的 Git worktree，把自己的工作目录切到那个副本里。

四个 Claude，四个 worktree，四个独立的工作空间。你在 tmux 里一眼看到全部。

---

## Git Worktrees:隔离的基础设施

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

tmux + Git Worktrees 协作架构

为什么非要 worktree？

因为 Git 有一个硬限制:一个工作目录只能有一个 checkout。两个 Claude 在同一个目录里同时改文件，必然打架。

Worktree 是 Git 原生支持的"多工作副本"机制。同一个.git 仓库，多个独立的工作目录，每个目录可以 checkout 不同的分支。

```
# 手动创建 worktree
git worktree add ../project-frontend feature/frontend
git worktree add ../project-backend feature/backend
git worktree add ../project-tests feature/tests
git worktree add ../project-docs feature/docs

# 查看所有 worktree
git worktree list
# /Users/you/project            abc1234 [main]
# /Users/you/project-frontend   def5678 [feature/frontend]
# /Users/you/project-backend    ghi9012 [feature/backend]
# /Users/you/project-tests      jkl3456 [feature/tests]
# /Users/you/project-docs       mno7890 [feature/docs]
```

每个 worktree 是一个完整的文件系统副本。Claude A 在 project-frontend 里改 React 组件，Claude B 在 project-backend 里改 Express 路由。文件系统完全隔离，谁也不碰谁的东西。

但它们共享同一个.git 目录。这意味着:

- commit 历史是共享的
- 分支是共享的
- remote 是共享的

隔离在文件层面，统一在 Git 层面。这正是并行开发需要的。

### claude -w 一键启动

Claude Code 内置了 worktree 支持。 `-w` 参数的完整行为:

1. 检查指定名称的 worktree 是否已经存在
2. 不存在就自动创建(基于当前分支)
3. 把工作目录切到那个 worktree
4. 开始执行任务

你不用手动 `git worktree add` 。 `claude -w frontend` 一条命令搞定。

---

## 任务分派策略

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

三种 Agent 任务分派策略

四个 Claude 跑起来了。怎么给它们分活？

分得好，四个 agent 并行不冲突。分得不好，四个 agent 做完一合并全是冲突。

### 策略一:按模块分

最直观。前端一个、后端一个、测试一个、文档一个。

```
Agent A → src/frontend/
Agent B → src/backend/
Agent C → tests/
Agent D → docs/
```

前提:模块之间耦合度低。如果前端组件里硬编码了后端的数据结构，两个 agent 改完一合并就炸。

### 策略二:按功能分

一个功能一个 agent。每个 agent 负责一个完整的 feature，包括前后端和测试。

```
Agent A → feature/login(前端 + 后端 + 测试)
Agent B → feature/dashboard(前端 + 后端 + 测试)
Agent C → feature/settings(前端 + 后端 + 测试)
Agent D → feature/notifications(前端 + 后端 + 测试)
```

好处:每个 agent 有完整的上下文，不需要跨 agent 协调接口。 坏处:如果两个 feature 都改了同一个基础组件(比如 Button 组件)，合并还是会冲突。

### 策略三:按阶段分

流水线模式。前一个 agent 的产出是后一个 agent 的输入。

```
第一波(并行):
Agent A → 实现 feature/login
Agent B → 实现 feature/dashboard

第二波(前一波完成后):
Agent C → 审阅 Agent A 的代码
Agent D → 审阅 Agent B 的代码

第三波:
Agent A → 根据审阅意见修改
Agent B → 根据审阅意见修改
```

这个策略最适合需要 code review 的场景。写代码的和审代码的不是同一个 agent，避免"自己审自己"。

### 怎么选？

一句话:看文件是否重叠。

如果四个任务改的文件完全不重叠，按模块分。如果有少量重叠，按功能分。如果任务之间有依赖关系(B 依赖 A 的产出)，按阶段分。

不要让两个 agent 同时改同一个文件。这不是建议，是禁令。

---

## 冲突合并:最后一公里

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

逐个合并策略：4 个分支安全合入 main

四个 agent 各干各的，干完了。现在要合到一起。

这是并行开发里最容易翻车的环节。

### 最佳实践:逐个合并

不要四个分支同时往 main 合。一个一个来。

```
# 先合风险最低的
git checkout main
git merge feature/docs          # 文档改动，不太可能冲突

# 再合测试
git merge feature/tests         # 测试文件通常独立

# 再合后端
git merge feature/backend       # 可能跟前端有共享类型定义

# 最后合前端
git merge feature/frontend      # 如果有冲突，这时候处理
```

每合一个，跑一次测试。发现冲突或测试挂了，当场处理。不要攒到最后一起爆炸。

### 遇到冲突怎么办

让 Claude 处理。

```
> 合并 feature/frontend 到 main 时有 3 个文件冲突:
> - src/types/api.ts
> - src/config/routes.ts
> - package.json
>
> 请分析冲突内容,选择正确的合并策略,保留双方有意义的改动。
```

Claude 比你更擅长分析 diff。它能看到两边改了什么，判断哪些改动应该保留，哪些应该丢弃。

### 预防冲突的设计

合并不是目标，不冲突才是。

几个实用技巧:

1. 共享类型定义单独一个文件，不要散在各模块里。改类型定义的只能有一个 agent。
2. package.json 的修改交给一个 agent 统一处理。不要让多个 agent 各自加依赖。
3. 配置文件(环境变量、路由表)同理，指定一个 agent 负责。
4. 让每个 agent 在开始前先声明它会改哪些文件。如果两个 agent 的文件清单有重叠，重新分配任务。

---

## /batch:扇出大规模变更

有一种场景特别适合并行:大规模文件修改。

比如你要把项目里 200 个文件的 import 路径从相对路径改成 alias。一个 Claude 一个个改，慢死。

Boris 提过:

> ★
> 
> use /batch to fan out massive changesets
> 
> — @bcherny

`/batch` 命令把一个大任务自动拆成多个子任务，分发给多个 sub-agent 并行处理。

```
/batch "把所有 .ts 文件的相对 import 改成 @/ 开头的 alias 路径"
```

Claude 会:

1. 扫描所有.ts 文件
2. 按目录分组
3. 为每组启动一个 sub-agent
4. 每个 sub-agent 处理自己那组文件
5. 全部完成后合并结果

你不用手动建 worktree，不用手动分任务。/batch 替你做了。

但注意:/batch 适合"同一种改动应用到很多文件"的场景。如果每个文件的改法不一样，还是手动分配 agent 更可控。

---

## 成本与可观测性

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

单 Agent 串行 vs 4 Agent 并行：成本效益分析

四个 Claude 并行，token 成本是一个 Claude 的四倍吗？

不一定。

每个 agent 的上下文窗口是独立的。如果你把一个大任务拆成四个小任务，每个 agent 需要的上下文更少，单个 agent 的 token 消耗反而可能降低。

但总量一般会增加。四个 agent 各自要读取项目结构、理解代码风格、运行测试。这些"基础开销"被重复了四次。

### 粗略估算

| 模式 | 上下文开销 | 任务 token | 总计 |
| --- | --- | --- | --- |
| 单 agent 串行 | 1x | 4x | ~5x |
| 4 agent 并行 | 4x | 1x 每个 | ~8x |

token 贵了约 60%，但时间从 4 小时变成 1 小时。

值不值？看你的时间值多少钱。

### 监控每个 agent 的进度

tmux 是最直观的监控方式。四个 pane，每个 pane 里 Claude 的输出实时滚动。

更结构化的做法:

```
# 让每个 agent 完成任务后创建一个标记文件
# Agent A 完成后:
touch /tmp/agent-frontend-done

# Agent B 完成后:
touch /tmp/agent-backend-done

# 监控脚本
watch -n 5 'ls /tmp/agent-*-done 2>/dev/null | wc -l'
```

或者用 Git 本身来监控:

```
# 每个 agent 在自己的分支上提交
# 监控所有分支的最新 commit
watch -n 10 'git branch -v --no-merged main'
```

分支还没合并到 main 的，就是还在干活的。分支有新 commit 了，说明 agent 有进展。

---

## 完整实战:4 个 Claude 并行交付登录功能

把上面所有知识串起来。

### 准备工作

```
# 创建 tmux 会话,切成 4 个 pane
tmux new-session -s login-feature \; \
  split-window -h \; \
  split-window -v \; \
  select-pane -t 0 \; \
  split-window -v
```

### 分派任务

```
# Pane 0 — 后端 Agent
claude -w backend "实现用户登录和注册的后端 API:
- POST /api/auth/login(邮箱 + 密码)
- POST /api/auth/register(邮箱 + 密码 + 用户名)
- JWT token 生成和验证
- 密码 bcrypt 加密
- 完成后在分支上提交并推送"

# Pane 1 — 前端 Agent
claude -w frontend "实现用户登录和注册的前端页面:
- /login 页面:邮箱和密码表单
- /register 页面:邮箱、密码、用户名表单
- 表单验证(前端)
- 调用后端 API 的 service 层
- 完成后在分支上提交并推送"

# Pane 2 — 测试 Agent
claude -w tests "为登录和注册功能编写测试:
- 后端 API 的集成测试(happy path + error cases)
- 前端组件的单元测试
- 登录流程的端到端测试
- 完成后在分支上提交并推送"

# Pane 3 — 基础设施 Agent
claude -w infra "准备登录功能需要的基础设施:
- 数据库 migration:users 表(email, password_hash, username, created_at)
- 环境变量配置:JWT_SECRET, BCRYPT_ROUNDS
- CI 配置:添加 auth 相关测试到 CI pipeline
- 完成后在分支上提交并推送"
```

### 合并

四个 agent 都跑完后:

```
# 回到主终端
git checkout main

# 先合基础设施(数据库 migration 优先)
git merge feature/infra
npm test# 确保没问题

# 再合后端
git merge feature/backend
npm test

# 再合前端
git merge feature/frontend
npm test

# 最后合测试
git merge feature/tests
npm test# 全量测试通过
```

从开始到 4 个分支全部合并，原来一个人串行做 4 小时的活，现在 1 小时搞定。

---

## 你的 Agent Team 搭对了吗

三个问题:

1. 你的多个 agent 之间有没有文件重叠？如果有，合并的时候大概率要手动解冲突。不要抱侥幸心理，提前把文件分清楚。
2. 你有没有用 tmux 或类似工具同时观察所有 agent 的进度？如果只是"启动了就不管了"，某个 agent 卡住你都不知道。盲跑不是并行，是赌博。
3. 你有没有先在小规模任务上试过 Agent Teams？不要第一次用就上四个 agent 做核心功能。先拿一个不紧急的重构任务练手，熟悉了再上正事。

---

## 金句

单 Claude 是写代码的工具。多 Claude 是交付功能的团队。管理 Agent Teams 的核心不是技术，是任务分解。你分得越清楚，合并越顺畅。

---

## 下一篇预告

四个 Claude 跑起来了。但它们之间怎么协调？谁触发谁？谁的输出喂给谁的输入？

下一篇讲 Claude Code 的三元编排:Command 触发入口、Agent 执行主体、Skill 领域知识。三者怎么分工，怎么组合，怎么搭出真正的自动化流水线。

→ 第 16 篇:Orchestration 范式解剖——Command → Agent → Skill 三元编排

---

#Cladue Code · 目录

作者提示: 个人观点，仅供参考

继续滑动看下一个

匠心格物

向上滑动看下一个

搜索范围

全网

文库

学术

所有文献

所有文献

中文库

英文库

---

PubMed

北大核心

中科院分区

全部

---

中科院1区

中科院1-2区

中科院1-3区

JCR

全部

---

JCR：Q1

JCR：Q1-Q2

JCR：Q1-Q3

SCIE

EI

图片

视频

播客

我的

全部

我的

Agent 编排与循环指南

海管家\_货代系统\_货代软件\_跨境物流系统\_国际货代操作系统

强度

深入

简洁

深入

深度研究

先想后搜

先搜后扩

新建自定义技能