---
title: "Claude Code + gstack 实战：如何用多 Agent 协作实现 10 倍提效"
source: "https://mp.weixin.qq.com/s/pJ0NhXzb-SbR4Huuwd5wxA"
created: 2026-04-16
category: "ClaudeCode"
tags: ["ClaudeCode", "type/hands-on", "type/tutorial", "gstack", "Multi-Agent", "Skill"]
status: "archived"
references: "Archive/Claude Code + gstack 实战：如何用多 Agent 协作实现 10 倍提效.md"
---

> YC 总裁 Garry Tan 开源的 Claude Code 技能包 gstack，核心理念是把 Claude Code 从通用助手变成完整的虚拟工程团队。本文介绍其 28 个专业角色、Team Mode 多 Agent 协作实战，以及从想法到生产的完整工作流。

## 一、从"单打独斗"到"团队协作"

### 传统 AI 编程的痛点

- **上下文割裂**：问完架构问实现，AI 忘了之前的讨论
- **角色混乱**：一会儿让它当架构师，一会儿当码农，质量参差不齐
- **缺乏流程**：没有规划直接开干，写到一半发现方向错了
- **测试缺失**：代码能跑就行，没人帮你做 Code Review 和 QA

**本质问题**：你把 AI 当"工具"，而不是"团队"。

### gstack 的破局之道

**gstack** 是 Y Combinator 总裁 Garry Tan 开源的 Claude Code 技能包。它的核心理念是：

> **把 Claude Code 从一个通用助手，变成一个完整的虚拟工程团队。**

| 传统模式 | gstack 模式 |
| --- | --- |
| 你和 AI 一对一聊天 | 你和 CEO、架构师、工程师、QA 团队协作 |
| 口头描述需求 | 结构化规划流程（CEO Review → 架构设计 → 编码 → Review → QA → 发布） |
| 写完后简单测试 | 每个环节都有专业角色把关 |
| 一个人串行干活 | 多 Agent 并行处理不同任务 |

**实际效果**：Garry Tan 声称用这套工作流 **60 天写了 60 万行生产代码**（35% 是测试），日均 1-2 万行。

## 二、gstack 核心技能一览

gstack 提供了 **28 个专业角色**（Skills），通过 `/` 命令随时召唤：

### 规划阶段：想清楚再动手

| 技能命令 | 角色 | 职责 |
| --- | --- | --- |
| `/office-hours` | YC 合伙人 | 通过 6 个强制性问题重构产品思路，挑战你的假设 |
| `/plan-ceo-review` | CEO/创始人 | 从用户角度审视需求，寻找 10 星级产品功能 |
| `/plan-eng-review` | 工程经理 | 锁定架构、数据流、边缘情况、测试计划 |
| `/plan-design-review` | 高级设计师 | 对设计维度评分，检测"AI 垃圾内容" |
| `/design-consultation` | 设计合伙人 | 从零构建完整的设计系统 |

**使用示例**：

```
# 开始新项目前，先找"CEO"聊聊
/plan-ceo-review

# 然后让"工程经理"把关架构
/plan-eng-review

# 最后"设计师"审核交互
/plan-design-review
```

### 构建阶段：高质量编码

| 技能命令 | 角色 | 职责 |
| --- | --- | --- |
| `/review` | 偏执的高级工程师 | 发现 CI 通过但生产环境会爆炸的 Bug |
| `/investigate` | 调试专家 | 系统性根因分析，遵循"没有调查就没有修复" |
| `/design-review` | 懂代码的设计师 | 执行设计审计并修复问题 |

**`/review` 能发现的问题**：

- N+1 查询性能陷阱
- 竞态条件
- 违反信任边界
- 错误处理缺失
- 安全漏洞

### 质量阶段：专业级测试

| 技能命令 | 角色 | 职责 |
| --- | --- | --- |
| `/qa` | QA 负责人 | 打开真实浏览器，点击流程，发现 Bug，修复并验证 |
| `/qa-only` | QA 报告员 | 仅生成 Bug 报告，不修改代码 |
| `/browse` | QA 工程师 | 使用真实 Chromium 浏览器（~100ms/命令） |
| `/setup-browser-cookies` | 会话管理 |  |
| `/cso` | 首席安全官 | OWASP Top 10 + STRIDE 威胁模型审计 |
| `/benchmark` | 性能工程师 | 基准测试页面加载时间、Core Web Vitals |

**`/qa` 的工作流程**：

1. 分析代码 diff，识别受影响页面
2. 打开浏览器访问页面
3. 点击关键流程，截图记录
4. 检查控制台错误
5. 发现 Bug 后自动修复
6. 输出健康评分

### 发布阶段：自动化部署

| 技能命令 | 角色 | 职责 |
| --- | --- | --- |
| `/ship` | 发布工程师 | 同步主分支、运行测试、审计覆盖率、推送并开 PR |
| `/land-and-deploy` | 发布工程师 | 合并 PR，等待 CI/部署，验证生产健康状态 |
| `/canary` | SRE | 部署后监控循环，查找控制台错误和性能退化 |
| `/document-release` | 技术文档 | 更新项目文档匹配刚发布的功能 |
| `/retro` | 工程经理 | 每周复盘，分析提交统计和测试健康状况 |

### 安全工具：保驾护航

| 技能命令 | 功能 |
| --- | --- |
| `/careful` | 执行破坏性命令（如 `rm -rf`）前发出警告 |
| `/freeze` | 编辑锁定，将修改限制在特定目录 |
| `/guard` | 全安全模式（careful + freeze） |
| `/unfreeze` | 解除锁定 |
| `/codex` | 使用 OpenAI Codex CLI 进行独立代码审查（第二意见） |

## 三、多 Agent 协作：Team Mode 实战

### 什么是 Team Mode？

除了串行使用技能，gstack 还支持 **Team Mode（团队模式）**，允许你同时启动多个 Agent，让它们：

- **并行处理** 不同任务
- **相互通信**，共享上下文
- **协作完成** 复杂项目

**典型场景**：

- 前端 Agent 写 UI，后端 Agent 写 API，数据库 Agent 设计 Schema
- 一个 Agent 做代码审查，另一个 Agent 写测试用例
- 多个 Agent 分别处理不同模块的 Bug 修复

### 实战案例：开发一个全栈应用

假设你要开发一个"AI 文章生成器"，可以这样安排多 Agent 协作：

#### Step 1：启动 Team 并分配角色

```
# 创建团队
/team-create --name="ai-writer-project"

# 启动前端开发 Agent
task --name="frontend-dev" --prompt="
你是一名 React + TypeScript 专家。
负责开发 AI 文章生成器的前端界面：
1. 文章编辑器（支持 Markdown）
2. 生成按钮和进度展示
3. 历史记录列表
4. 用户设置页面

技术栈：React 18 + Vite + Tailwind CSS + shadcn/ui
" --mode="acceptEdits"

# 启动后端开发 Agent
task --name="backend-dev" --prompt="
你是一名 Python/FastAPI 专家。
负责开发 AI 文章生成器的后端 API：
1. /api/generate 文章生成接口（集成 OpenAI API）
2. /api/history 历史记录 CRUD
3. /api/user 用户管理
4. 数据库模型设计（SQLAlchemy）

技术栈：FastAPI + PostgreSQL + SQLAlchemy + Pydantic
" --mode="acceptEdits"

# 启动 DevOps Agent
task --name="devops-dev" --prompt="
你是一名 DevOps 专家。
负责搭建部署基础设施：
1. Docker 容器化配置
2. docker-compose 本地开发环境
3. GitHub Actions CI/CD 流水线
4. Nginx 反向代理配置
" --mode="acceptEdits"
```

#### Step 2：使用 gstack 技能协调质量

在每个 Agent 完成任务后，使用 gstack 进行质量把关：

```
# 对前端代码进行 Review
/review --path="frontend/"

# 对后端代码进行安全审计
/cso --path="backend/"

# 对全栈应用进行 QA 测试
/qa http://localhost:3000

# 准备发布
/ship
```

#### Step 3：Agent 间通信

如果前端需要后端的 API 变更，可以通过 `send_message` 通信：

```
# 前端 Agent 发送消息给后端 Agent
send_message --type="message" --recipient="backend-dev" --content="
/generate 接口需要支持流式输出（SSE），
请修改 API 支持 text/event-stream 格式。
" --summary="请求 SSE 流式支持"
```

### 多 Agent vs 单 Agent 效率对比

| 指标 | 单 Agent | 多 Agent (gstack) |
| --- | --- | --- |
| 开发全栈应用 | 8-10 小时 | 3-4 小时 |
| 代码审查 | 人工 2 小时 | `/review` 10 分钟 |
| QA 测试 | 人工 3 小时 | `/qa` 20 分钟 |
| 部署发布 | 人工 1 小时 | `/ship` 5 分钟 |
| Bug 修复 | 串行排查 | 多 Agent 并行定位 |
| **总体提效** | 1x | **5-10x** |

## 四、安装与配置

### 前置要求

- Claude Code
- Git
- Bun v1.0+（或 Node.js for Windows）

### 快速安装（30 秒）

```bash
# 全局安装 gstack
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack
./setup
```

Claude 会自动在你的 `CLAUDE.md` 配置中添加 gstack 技能列表。

### 项目级安装（推荐）

如果你想让团队成员共享配置：

```bash
# 复制到项目目录
cp -Rf ~/.claude/skills/gstack .claude/skills/gstack
rm -rf .claude/skills/gstack/.git
cd .claude/skills/gstack
./setup
```

然后提交到 Git：

```bash
git add .claude/skills/gstack
git commit -m "Add gstack skills for team collaboration"
```

### 其他 IDE 支持

gstack 也支持其他兼容 **SKILL.md** 标准的工具：

**Codex CLI**：

```bash
git clone https://github.com/garrytan/gstack.git .agents/skills/gstack
cd .agents/skills/gstack && ./setup --host codex
```

**Cursor**：将技能文件复制到 `.cursor/skills/` 目录即可。

## 五、实战工作流：从想法到生产

### 完整 Sprint 流程

### 关键技巧

**技巧 1：用 `/office-hours` 代替头脑风暴**

不要直接开始写代码，先用 `/office-hours` 把你的想法过一遍。它会问 6 个强制性问题：

1. 你解决的是什么问题？
2. 谁是你的用户？
3. 现有解决方案是什么？为什么不够好？
4. 你的独特价值是什么？
5. 如何验证这个想法？
6. 最小可行产品（MVP）是什么？

**技巧 2：用 `/review` 拦截生产事故**

每次提交前运行 `/review`，它能发现：

- 数据库查询性能问题（N+1）
- 并发安全问题（竞态条件）
- 安全漏洞（SQL 注入、XSS）
- 错误处理缺失

**技巧 3：用 `/qa` 代替人工测试**

部署前运行 `/qa http://localhost:3000`，它会：

- 自动遍历所有页面
- 点击关键按钮和表单
- 检查控制台错误
- 截图记录 UI 问题
- 输出健康评分

**技巧 4：用 `/ship` 自动化发布**

告别手动同步分支、运行测试、创建 PR 的繁琐流程。`/ship` 会：

- 自动同步主分支
- 运行全部测试
- 检查测试覆盖率
- 推送分支
- 创建 PR 并添加描述

## 六、常见问题与解决方案

### Q1：技能没有显示怎么办？

```bash
cd ~/.claude/skills/gstack
./setup
```

### Q2：/browse 浏览器操作失败？

```bash
cd ~/.claude/skills/gstack
bun install
bun run build
```

### Q3：Windows 能用吗？

可以，但需要通过 **Git Bash** 或 **WSL** 运行，且必须同时安装 Node.js（Bun 在 Windows 的 Playwright 支持上有已知问题）。

### Q4：如何关闭遥测？

gstack 默认 **关闭** 遥测。如果之前开启了，可以运行：

```bash
gstack-config set telemetry off
```

### Q5：如何升级 gstack？

```
/gstack-upgrade
```

## 七、核心观点

1. **AI 编程的下一个阶段是"团队协作"**：单个 AI 助手的能力有限，但多个专业 Agent 协作可以完成复杂任务。
2. **流程化比单点突破更重要**：gstack 的价值不在于某个技能有多强，而在于它提供了一套 **完整的工程流程**。
3. **人机协作是未来**：AI 负责执行和初稿，人类负责决策和把关。gstack 让这种协作变得高效。

## 相关阅读

- [Boris Cherny 分享的 13 个 Claude Code 高效使用技巧](./claude-code-boris-cherny-13-tips.md)
- [Claude Code 必备的三个开源项目](./claude-code-essential-open-source-projects.md)

---

## 来源与归档

- 原始素材：[Archive/Claude Code + gstack 实战：如何用多 Agent 协作实现 10 倍提效.md](../../../Archive/Claude%20Code%20+%20gstack%20实战：如何用多%20Agent%20协作实现%2010%20倍提效.md)
