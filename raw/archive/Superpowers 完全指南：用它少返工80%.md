---
title: "Superpowers 完全指南：用它少返工80%"
source: "https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487617&idx=1&sn=49fee04bf4d412a7c444d0ea4f750fe4&scene=21&poc_token=HArmCmqjT2KMG4TDDvM9dG2Lmgg6IGJ9fwFa7sJo"
author:
  - "[[程康健]]"
published:
created: 2026-05-18
description: "我在整理 AI 编程工具的时候，突然意识到一个问题：我们每天用 Claude Code 写代码，效率确实比以前"
tags:
  - "clippings"
---
程康健 *2026年4月11日 09:08*

我在整理 AI 编程工具的时候，突然意识到一个问题：我们每天用 Claude Code 写代码，效率确实比以前高了很多——但我不确定自己是否真的在"用对"它。它有时候写的代码会偏离需求、有时候写完代码不跑测试、有时候做着做着就跑偏了，需要我频繁介入纠正。

后来发现了 Superpowers。

它不是一个新的 AI 工具，而是一套给 AI 编程代理装上"工作手册"的框架。安装之后，Claude Code 会自动在写代码前先问你真正想做什么、自动按 TDD 节奏推进、自动做代码审查……整个工作流变得有纪律多了。

更让我意外的是，围绕这个需求，市面上已经出现了好几个方向截然不同的工具：有人做"文档驱动"、有人做"需求规格化"、有人直接重写了整个代理运行引擎。这些工具到底有什么区别？该怎么选？能不能叠加使用？

这篇文章是我研究这些工具之后整理出来的完整指南。内容包括：

- Superpowers 从零开始的完整安装和使用教程
- 与 BMAD Method、OpenSpec、OpenHarness 的横向对比（附选型建议）
- 七阶段完整工作流详解
- 自定义技能、并行代理等高级用法

无论你是刚开始用 AI 编程工具的新手，还是已经在用 Claude Code 但感觉还没完全发挥出来的开发者，这篇应该都有你需要的东西。

---

Superpowers

完全新手入门指南

AI 编程代理技能框架 · 从零开始掌握完整开发工作流

github.com/obra/superpowers

v5.0.7 | 2026 年 4 月

MIT License | 作者：Jesse Vincent & Prime Radiant

目录

第一章 什么是 Superpowers？

1.1 项目背景与核心价值

1.2 它解决了什么问题

1.3 设计哲学

第二章 工具选型与横向对比

2.1 四款工具定位速览

2.2 Superpowers：工程纪律框架

2.3 BMAD Method：文档驱动的敏捷框架

2.4 OpenSpec：规格驱动开发框架

2.5 OpenHarness：代理运行引擎

2.6 全维度横向对比表

2.7 如何选择与组合使用

第三章 安装与配置

3.1 前置条件

3.2 Claude Code 安装（推荐）

3.3 Cursor 安装

3.4 Codex / OpenCode 安装

3.5 Gemini CLI 安装

3.6 验证安装成功

第四章 核心概念：Skills 技能系统

4.1 Skills 是什么

4.2 Skills 如何触发

4.3 完整技能清单与说明

第五章 标准开发工作流详解

5.1 阶段一：头脑风暴（brainstorming）

5.2 阶段二：建立工作区（using-git-worktrees）

5.3 阶段三：制定计划（writing-plans）

5.4 阶段四：执行计划（subagent-driven-development）

5.5 阶段五：测试驱动开发（test-driven-development）

5.6 阶段六：代码审查（requesting-code-review）

5.7 阶段七：收尾合并（finishing-a-development-branch）

第六章 高级功能

6.1 调试技能（systematic-debugging）

6.2 并行代理（dispatching-parallel-agents）

6.3 自定义技能（writing-skills）

第七章 常见问题与最佳实践

7.1 常见问题（FAQ）

7.2 最佳实践建议

7.3 更新与社区资源

附录：关注作者

第一章 什么是 Superpowers？

1.1 项目背景与核心价值

Superpowers 是一个开源的 AI 编程代理技能框架（Agentic Skills Framework），由 Jesse Vincent 和 Prime Radiant 团队开发，托管于 GitHub（github.com/obra/superpowers）。截至 2026 年，该项目已获得超过 13.7 万个 Star，是目前最受欢迎的 AI 编程辅助框架之一。

其核心价值在于：赋予 AI 编程代理（如 Claude Code、Cursor、Codex 等）一套经过实战验证的、可组合的工作流"技能"。这些技能让 AI 代理不再盲目地写代码，而是遵循软件工程的最佳实践——先理解需求、再制定计划、然后有序实施、最后验证结果。

🌟 一句话理解：Superpowers 就是给 AI 编程代理装上"大脑"，让它像一个经验丰富的高级工程师一样思考和工作，而不是像一个没有判断力的代码打字机。

1.2 它解决了什么问题

在没有 Superpowers 的情况下，AI 编程代理常见的问题包括：

•盲目开始写代码：不问需求直接动手，最终写出来的东西与用户预期不符

•缺乏测试意识：不写测试，或测试覆盖率极低，留下大量隐患

•计划混乱：没有清晰的实现路线，导致代码结构混乱、反复推倒重来

•无法长时间自主工作：需要频繁人工干预，效率低下

•代码审查缺失：没有系统的审查流程，代码质量无法保证

Superpowers 通过引入一套强制性的工作流技能，系统性地解决了上述所有问题。

1.3 设计哲学

Superpowers 的设计遵循以下四条核心哲学：

① 测试驱动开发（Test-Driven Development）

永远先写测试，再写实现代码。这是不可妥协的原则。未经测试覆盖的代码不应该存在于代码库中。

② 系统化优于临时性（Systematic over Ad-hoc）

用有章可循的流程替代临时猜测。每个开发阶段都有明确的步骤和验证标准，不依赖"感觉对了"来判断工作是否完成。

③ 降低复杂度（Complexity Reduction）

简洁是首要目标。遵循 YAGNI（You Aren't Gonna Need It，不要过度设计）和 DRY（Don't Repeat Yourself，不要重复自己）原则，只实现当前真正需要的功能。

④ 证据优于声称（Evidence over Claims）

在宣布某项工作"完成"之前，必须通过实际验证（如运行测试）来证明它确实有效，而不是仅仅声称或相信它能工作。

第二章 工具选型与横向对比

在正式学习 Superpowers 的安装与使用之前，有必要先搞清楚这个问题：市面上解决类似问题的工具不止一个，Superpowers 到底解决的是哪一层的问题？它和 BMAD Method、OpenSpec、OpenHarness 是竞争关系，还是互补关系？本章通过完整的横向对比，帮助你做出清晰的工具选型决策。

2.1 四款工具定位速览

这四款工具解决的是 AI 编程流水线上四个不同层次的问题，本质上不是竞争关系，而是可以叠加使用的互补工具。用一句话分别定位：

🔵 Superpowers —— 给 AI 代理装"工作手册"（工程纪律 + 工作流规范）

🟣 BMAD Method —— 给 AI 代理配"敏捷团队"（文档驱动 + 角色专业化）

🟢 OpenSpec —— 给 AI 代理提供"需求文档"（规格驱动开发框架）

🟠 OpenHarness —— 给 AI 代理造"身体"（基础设施 + 运行引擎）

2.2 Superpowers：工程纪律框架

项目地址：github.com/obra/superpowers ⭐ 146k

Superpowers 的核心是一套 Markdown 格式的"技能文件"（SKILL.md），这些技能文件告诉 AI 代理在特定场景下该怎么工作。它不是一个可独立运行的程序，而是附加在现有代理工具（Claude Code、Cursor 等）上的一套强制性工作流规范。

核心特点：

•以 TDD（测试驱动开发）为核心，强制 RED-GREEN-REFACTOR 循环

•七阶段工作流：头脑风暴 → Git Worktree → 写计划 → 子代理执行 → TDD → 代码审查 → 收尾合并

•技能自动触发，无需手动干预，安装后"开箱即用"

•语言无关，适用于任何编程语言和技术栈

•极简安装，一条命令完成

最适合场景：

个人开发者或小团队，希望让现有 AI 代理更有工程纪律、更少跑偏，特别是需要严格 TDD 的项目。

2.3 BMAD Method：文档驱动的敏捷框架

项目地址：github.com/bmad-code-org/BMAD-METHOD ⭐ 44k

BMAD（Build More Architect Dreams）是一个 AI 驱动的敏捷开发框架。与 Superpowers 强调"工程纪律"不同，BMAD 的核心理念是"文档驱动"——先生成 PRD（产品需求文档）、架构设计文档、用户故事等工件，再以这些文档作为"合同"来约束 AI 的实现行为。

BMAD 的另一个显著特点是角色专业化：它内置了 12 个以上的专业代理角色（业务分析师、产品经理、UX 设计师、系统架构师、Scrum Master、开发者、QA 工程师等），不同阶段由不同角色的代理接管工作。

核心特点：

•文档优先：规格文档是代码实现的"合同"，AI 必须严格按文档实现

•多角色代理：12+ 个专业化 AI 代理，覆盖软件开发全生命周期

•规模自适应：自动根据项目复杂度调整规划深度（0 级 bug 修复到企业级系统）

•Party Mode：多个代理角色在同一会话中协作和讨论

•通过 npx bmad-method install 一键安装，支持 Claude Code、Cursor 等多平台

Superpowers vs BMAD 核心区别：

Superpowers 的"头脑风暴"阶段也会产出设计文档，但这个文档主要是为了对齐共识，不是强制约束。BMAD 的文档则是"合同"性质，是所有后续实现的强制性参考基准。前者重在工程执行纪律，后者重在需求规格管控。

选择建议： 个人项目或快速迭代用 Superpowers；有真实用户、外部集成、安全要求，或需要团队协作的中大型项目考虑 BMAD。两者也可以叠加：用 BMAD 做前期规划，用 Superpowers 约束执行阶段的工程纪律。

2.4 OpenSpec：规格驱动开发框架

项目地址：github.com/Fission-AI/OpenSpec ⭐ 39k

OpenSpec 是一个"规格驱动开发"（Spec-Driven Development，SDD）框架，核心理念是：AI 编程工具功能强大，但当需求只存在于聊天历史中时，结果往往不可预测。OpenSpec 在代码之前添加一个轻量级的规格层，让人和 AI 在动手写代码之前先就需求对齐。

OpenSpec 是一个 npm 包，通过斜杠命令驱动。典型工作流程：/opsx:propose（提出想法）→ 自动生成包含 proposal.md、specs/、design.md、tasks.md 的结构化文件夹 → /opsx:apply（执行实现）→ /opsx:archive（归档）。

核心特点：

•每个变更都有专属文件夹：proposal.md + specs/ + design.md + tasks.md

•轻量、渐进式，不强制完整的工作流，可按需使用部分功能

•支持 20+ AI 工具（Claude Code、Cursor、GitHub Copilot 等）

•强调"流动而非刚性"，允许随时更新任何规格文件

与 Superpowers 的关系：

OpenSpec 主要解决的是"做什么"（需求规格化），Superpowers 主要解决的是"怎么做"（工程执行纪律）。两者作用阶段不同，可以组合：先用 OpenSpec 生成规格文档，再用 Superpowers 约束实现过程。

2.5 OpenHarness：代理运行引擎

项目地址：github.com/HKUDS/OpenHarness ⭐ 8.6k

OpenHarness 是一个开源的 Python 实现的 AI 代理运行时（Agent Harness），定位完全不同于前三者。它解决的是基础设施层的问题：模型提供智能，Harness 提供"手、眼睛、记忆和安全边界"。

OpenHarness 是一个独立运行的程序（通过 oh 命令启动），自带 43 个工具、权限管控、React TUI 界面、多代理调度能力，并且支持 Anthropic、OpenAI 兼容、GitHub Copilot 等多种模型后端。

核心特点：

•独立运行，不依附于 Claude Code 或 Cursor 等现有工具

•支持国内模型（通义千问、DeepSeek、Kimi 等）运行类 Claude Code 体验

•内置 43 个工具：文件操作、Shell、Web 搜索、MCP 等

•兼容 Superpowers 的 Skills 格式和 Claude Code 的插件格式

•面向研究者和开发者，可深入理解代理内部运作原理

注意： OpenHarness 于 2026 年 4 月才发布 v0.1.0，是四个工具中最新、生态最不成熟的。如果你的目标是"快速上手提升开发效率"，不建议从 OpenHarness 开始。它更适合想研究代理原理、或需要在国内模型上复刻 Claude Code 体验的开发者。

2.6 全维度横向对比表

| 对比维度 | Superpowers | BMAD Method | OpenSpec | OpenHarness |
| --- | --- | --- | --- | --- |
| 本质定位 | 工作流规范（Markdown） | 文档驱动敏捷框架 | 需求规格框架（npm） | 代理运行引擎（Python） |
| 解决什么 | 代理"怎么做事" | 代理"该做什么文档" | 代理"做什么需求" | 代理"能做什么" |
| 运行方式 | 寄生于现有代理 | 寄生于现有代理 | 寄生于现有代理 | 独立运行程序 |
| Star 数 | 146k ⭐ | 44k ⭐ | 39k ⭐ | 8.6k ⭐ |
| 成熟度 | 高 (v5.0.7) | 高 (v6.2.1) | 中 (v1.2.0) | 低 (v0.1.0) |
| 安装难度 | 极简，一条命令 | 一条命令 | npm install | 需配置 Python 环境 |
| 核心产物 | 技能触发+流程约束 | PRD/架构/用户故事 | proposal+specs 文件夹 | 工具调用+代理执行 |
| 代理角色数 | 1 个（单一代理+Skills） | 12+ 个专业化角色 | 1 个（AI 代理） | 支持多代理协调 |
| TDD 支持 | ✅ 核心强制要求 | ⚠️ 非核心 | ❌ 不涉及 | ❌ 不涉及 |
| 模型支持 | Claude/Cursor等平台 | Claude/Cursor等平台 | 20+ AI 工具 | Anthropic/OpenAI/国内模型 |
| 适合规模 | 个人+小团队 | 中大型项目 | 任意规模 | 研究+自建场景 |
| 国内模型 | ❌ | ❌ | ❌ | ✅ 支持 |

注： github star 数据统计截至 2026.4.11

2.7 如何选择与组合使用

这四款工具覆盖了 AI 开发流水线的不同层次，并非互斥，完全可以叠加使用。以下是几种典型的选择场景：

场景一：个人开发者，快速上手提升效率

推荐：直接使用 Superpowers，一条命令安装，开箱即用。它会自动改善你的 AI 代理的工作方式，不需要额外学习成本。

场景二：中大型项目，有真实用户和团队

推荐：BMAD（规划阶段）+ Superpowers（执行阶段）。BMAD 的文档驱动保证了需求对齐，Superpowers 的 TDD 和代码审查保证了实现质量。

场景三：需要在写代码前先对齐需求

推荐：OpenSpec（需求层）+ Superpowers（执行层）。先用 OpenSpec 生成结构化的规格文档，再用 Superpowers 约束实现过程。

场景四：研究代理原理 / 国内模型用户

推荐：OpenHarness。它是唯一原生支持通义千问、DeepSeek、Kimi 等国内模型的工具，同时兼容 Superpowers 的 Skills 格式。

💡 最优组合（完整链路）：OpenSpec（定义做什么）→ BMAD（规划文档）→ Superpowers（执行纪律）→ OpenHarness（运行引擎，仅在需要自建时使用）

第三章 安装与配置

3.1 前置条件

在安装 Superpowers 之前，请确认你已具备以下条件：

•一个受支持的 AI 编程代理工具（Claude Code、Cursor、Codex、OpenCode 或 Gemini CLI 之一）

•稳定的网络连接（用于访问 GitHub）

•基本的命令行操作能力（仅 Codex/OpenCode 手动安装时需要）

提示： 如果你是完全的新手，强烈推荐从 Claude Code 开始，因为 Superpowers 已上架 Claude Code 官方插件市场，安装最为简单，只需一条命令。

3.2 Claude Code 安装（推荐）

Superpowers 已正式上架 Claude Code 官方插件市场，安装极为简便。

方式一：通过官方市场直接安装（最简单）

在 Claude Code 中输入以下命令：

/plugin install superpowers@claude-plugins-official

方式二：通过自定义市场安装

先注册市场，再安装插件：

/plugin marketplace add obra/superpowers-marketplace

/plugin install superpowers@superpowers-marketplace

3.3 Cursor 安装

在 Cursor 的 Agent 聊天界面中，输入以下命令：

/add-plugin superpowers

或者在 Cursor 插件市场中搜索"superpowers"，找到并安装即可。

3.4 Codex / OpenCode 安装

Codex 和 OpenCode 需要通过指令让代理自动完成安装。

Codex 安装

向 Codex 发送以下指令：

Fetch and follow instructions from

https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.codex/INSTALL.md

Codex 手动安装步骤（可选）

1.克隆仓库到本地：

git clone https://github.com/obra/superpowers.git ~/.codex/superpowers

2.创建技能符号链接：

mkdir -p ~/.agents/skills

ln -s ~/.codex/superpowers/skills ~/.agents/skills/superpowers

3.重启 Codex。

4.（可选）启用多代理功能，在 Codex 配置文件中添加：

\[features\]

multi\_agent = true

Windows 用户说明

Windows 系统需使用 junction（联结点）代替符号链接，无需开发者模式：

New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\\.agents\\skills"

cmd /c mklink /J "$env:USERPROFILE\\.agents\\skills\\superpowers" "$env:USERPROFILE\\.codex\\superpowers\\skills"

OpenCode 安装

向 OpenCode 发送以下指令：

Fetch and follow instructions from

https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md

3.5 Gemini CLI 安装

安装命令：

gemini extensions install https://github.com/obra/superpowers

更新命令：

gemini extensions update superpowers

GitHub Copilot CLI 安装命令：

copilot plugin marketplace add obra/superpowers-marketplace

copilot plugin install superpowers@superpowers-marketplace

3.6 验证安装成功

安装完成后，开启一个新的会话并向代理提出一个能触发技能的请求，例如：

•"帮我规划一下这个功能"（help me plan this feature）

•"让我们调试一下这个问题"（let's debug this issue）

•"我想开发一个新项目"

如果代理自动触发了相关的 Superpowers 技能（如 brainstorming 或 systematic-debugging），说明安装成功。

Codex 故障排查： 如果技能没有显示，请执行以下检查：1）验证符号链接：ls -la ~/.agents/skills/superpowers；2）确认技能存在：ls ~/.codex/superpowers/skills；3）重启 Codex（技能在启动时被发现）。

第四章 核心概念：Skills 技能系统

4.1 Skills 是什么

Skills（技能）是 Superpowers 的核心构成单元。每个技能本质上是一个 Markdown 文件（SKILL.md），其中包含：

•技能的元数据（名称、描述、触发条件）

•详细的操作指令，告诉 AI 代理在特定情况下应该怎么做

•最佳实践、注意事项和验证标准

当 AI 代理面对一个任务时，它会自动扫描可用的技能库，找到最匹配当前任务的技能，并严格按照技能中的指令执行。这意味着你不需要手动告诉代理应该怎么做——Superpowers 已经替你配置好了一切。

💡 类比理解：可以把 Skills 理解成给 AI 代理配备的"工作手册"。就像一个新员工入职时会收到标准操作程序（SOP）一样，Skills 给 AI 代理提供了每个工作场景下的标准操作指南。

4.2 Skills 如何触发

技能的触发方式有三种：

① 自动触发（最常见）

当你的请求内容与某个技能的描述（description 字段）匹配时，代理会自动激活该技能。例如，当你说"帮我开发一个新功能"时，brainstorming 技能会自动触发。

② 名称触发

直接在对话中提到技能名称，例如："请使用 systematic-debugging 帮我排查这个 bug"。

③ 链式触发

using-superpowers 这个元技能会在后台持续运行，监控整个工作流的进展，并在适当时机指示代理调用其他技能，实现技能之间的自动链式调用。

4.3 完整技能清单与说明

Superpowers 内置了以下技能，按功能分类：

| 分类 | 技能名称 | 功能说明 |
| --- | --- | --- |
| 测试 | test-driven-development | 执行 RED-GREEN-REFACTOR 循环（含测试反模式参考） |
| 调试 | systematic-debugging | 四阶段根因分析流程（含根因追踪、纵深防御、条件等待技术） |
| 调试 | verification-before-completion | 确保问题已被真正修复，而非表面修复 |
| 协作 | brainstorming | Socratic 式设计精化，通过提问挖掘真实需求 |
| 协作 | writing-plans | 生成详细、可操作的实现计划 |
| 协作 | executing-plans | 分批执行计划，设置人工检查点 |
| 协作 | dispatching-parallel-agents | 并发子代理工作流，提升执行效率 |
| 协作 | requesting-code-review | 代码审查前的自查清单 |
| 协作 | receiving-code-review | 系统性响应代码审查反馈 |
| 协作 | using-git-worktrees | 使用 Git Worktrees 并行开发多分支 |
| 协作 | finishing-a-development-branch | 合并/PR 决策工作流，安全收尾开发分支 |
| 协作 | subagent-driven-development | 快速迭代，两阶段审查（规格合规性 + 代码质量） |
| 元技能 | writing-skills | 按最佳实践创建新的自定义技能 |
| 元技能 | using-superpowers | 技能系统的入口，介绍并协调整体技能使用 |

第五章 标准开发工作流详解

Superpowers 定义了一套完整的、从零到部署的七阶段开发工作流。这套工作流是强制性的——代理在每个任务开始前都会检查并应用相关技能，而不是可选的建议。下面逐一详细介绍每个阶段。

5.1 阶段一：头脑风暴（brainstorming）

触发时机：在开始写任何代码之前。

这是整个工作流中最关键的阶段。当代理检测到你要开始一个新功能或新项目时，它不会立刻动手写代码，而是首先触发 brainstorming 技能。

在这个阶段，代理会通过 Socratic 式对话（苏格拉底式提问法）来帮助你厘清真实需求：

•你真正想解决的问题是什么？

•有哪些可能的实现方案？它们的优劣各是什么？

•当前方案的边界条件和限制是什么？

•成功的标准是什么？怎么衡量功能是否完成？

代理会将讨论内容整理成设计文档，并分段呈现给你确认，每段内容都足够简短，让你能真正读懂并反馈意见——而不是一股脑给你塞一大段让你无从审阅的内容。

关键价值： 这个阶段帮助你和代理建立共识，避免"写完了但不是我想要的"的问题。花 5 分钟在这里，能节省你后续数小时的返工时间。

5.2 阶段二：建立工作区（using-git-worktrees）

触发时机：设计方案获得你的认可之后。

在正式开始编码之前，代理会使用 Git Worktrees 创建一个隔离的开发环境：

5.在新分支上创建独立的工作区（Worktree），与主分支完全隔离

6.运行项目初始化命令（如 npm install、pip install 等）

7.执行一次完整的测试套件，确保基线是干净的（所有测试都应该通过）

使用 Git Worktrees 的优势在于你可以同时在多个功能分支上并行工作，而不会互相干扰。即使正在开发中的功能出现问题，主分支始终保持稳定可用。

5.3 阶段三：制定计划（writing-plans）

触发时机：工作区准备就绪后，开始编码前。

代理会将经过确认的设计方案分解成一系列具体的、可执行的小任务。每个任务都具备以下特征：

•执行时间控制在 2-5 分钟以内

•包含具体的文件路径（精确到需要修改哪个文件的哪个部分）

•包含完整的代码示例（不是伪代码，是可以直接运行的真实代码）

•包含验证步骤（如何确认这个任务完成了）

计划的详细程度被刻意设计得足够具体——具体到"一个热情的初级工程师，即使没有项目背景、品味不佳、判断力有限，也能照着做"的程度。这样的精确性确保了后续执行阶段的顺利进行。

5.4 阶段四：执行计划（subagent-driven-development）

触发时机：实现计划审批通过后。

这是 Superpowers 最强大的阶段之一。当你确认计划可以开始执行时，代理会启动子代理驱动开发（Subagent-Driven Development）模式：

工作原理：

8.主代理为每个任务派遣一个全新的、干净的子代理

9.子代理在上下文隔离的环境中专注执行该任务

10.任务完成后，主代理对结果进行两阶段审查：

\-第一阶段：规格合规性检查——实现是否符合计划的要求？

\-第二阶段：代码质量检查——代码是否整洁、可维护、遵循最佳实践？

11.审查通过后，进入下一个任务；审查未通过则要求子代理修正

这种模式的优势是：每个子代理都是全新启动的，不携带前一个任务的上下文负担，因此能保持高度专注和准确性。实践中，Claude Code 能够在这种模式下连续自主工作数小时而不需要人工干预。

备选方案： 如果你的平台不支持子代理，可以使用 executing-plans 技能，它以批次（batch）方式执行任务，并在每个批次结束后设置人工检查点。

5.5 阶段五：测试驱动开发（test-driven-development）

触发时机：实现阶段的每个具体任务执行期间。

Superpowers 严格遵循 TDD（测试驱动开发）的 RED-GREEN-REFACTOR 循环：

RED（红）——先写测试，运行并确认它失败

在写任何实现代码之前，先编写对应的测试。运行测试，它应该失败（因为功能还没实现）。如果测试莫名其妙地通过了，说明测试本身有问题，需要先修复测试。

GREEN（绿）——写最少量的代码让测试通过

编写实现代码，目标是让刚才失败的测试通过。注意：只写让测试通过所需的最少代码，不要过度实现。再次运行测试，确认它通过了。

REFACTOR（重构）——在测试保护下改善代码质量

在不改变功能行为的前提下，改善代码的可读性、可维护性和结构。每次重构后都运行全部测试，确认没有引入新的问题。重构完成后提交（commit）。

严格规定： 如果发现有代码是在没有对应测试的情况下写出来的，Superpowers 会要求删除这些代码并重新从 RED 阶段开始。这不是惩罚，而是确保代码质量的必要机制。

5.6 阶段六：代码审查（requesting-code-review）

触发时机：每批任务完成之间。

代理会对已完成的代码进行自我审查，检查内容包括：

•实现是否与计划保持一致？有没有偏离原始设计？

•测试覆盖是否充分？是否有遗漏的边界情况？

•代码是否遵循项目的编码规范？

•是否存在安全隐患或性能问题？

审查结果按严重程度分级报告。严重问题（Critical）会阻止工作流继续推进，必须先修复；一般问题（Warning）会被记录但不强制立即修复。

如果你也收到了团队成员的代码审查意见，可以使用 receiving-code-review 技能来系统性地处理这些反馈。

5.7 阶段七：收尾合并（finishing-a-development-branch）

触发时机：所有计划任务完成之后。

开发分支完成后，代理会执行以下收尾步骤：

12.运行完整测试套件，确认所有测试通过

13.向你呈现四个选项，由你决定下一步行动：

\-直接合并（Merge）到主分支

\-创建 Pull Request（PR）供团队审查

\-保留分支，暂不操作（Keep）

\-放弃分支，删除所有更改（Discard）

14.根据你的选择执行操作，并清理对应的 Git Worktree

注意： 代理不会擅自决定是否合并代码，所有涉及主分支的操作都需要你明确确认。这是一道安全阀，确保代码不会在你不知情的情况下被合并。

第六章 高级功能

6.1 调试技能（systematic-debugging）

当你遇到难以定位的 Bug 时，systematic-debugging 技能会引导代理执行一个严谨的四阶段根因分析流程：

第一阶段：信息收集

收集所有相关信息——错误信息、日志输出、复现步骤、环境信息等。在这个阶段，不做任何假设，只收集事实。

第二阶段：假设形成

基于收集到的信息，形成多个可能的原因假设，并按可能性排序。每个假设都需要有具体的证据支撑，不接受"感觉是这里的问题"这样的直觉性猜测。

第三阶段：验证假设

按照可能性从高到低，逐一验证每个假设。验证方法包括：添加日志、编写针对性测试、使用调试器断点等。找到能够证伪或证实假设的确凿证据。

第四阶段：修复与验证

找到根因后，实施修复，并通过 verification-before-completion 技能确认问题已被真正解决——不仅是症状消失，而是根因被消除。

此外，该技能还包含以下高级调试技术的操作指南：

•根因追踪（Root-Cause Tracing）：顺着错误链向上追溯，找到最初的问题源头

•纵深防御（Defense in Depth）：在修复问题的同时，添加预防性措施避免同类问题再次发生

•条件等待（Condition-Based Waiting）：处理异步或时序相关的 Bug 的专项技巧

6.2 并行代理（dispatching-parallel-agents）

当项目规模较大、任务之间相互独立时，可以使用 dispatching-parallel-agents 技能来显著提升开发效率。

该技能会将可以并行执行的任务分配给多个同时运行的子代理，大幅缩短总体执行时间。适用场景包括：

•同时开发多个独立的功能模块

•并行处理多个文件的格式化、重构或测试编写

•同时进行前端和后端的独立开发

注意： 使用此功能需要你的代理平台支持多代理模式。对于 Codex，需要在配置文件中开启 multi\_agent = true。Claude Code 原生支持此功能。

6.3 自定义技能（writing-skills）

Superpowers 支持创建自定义技能，让你能够将团队特有的流程和最佳实践编码化，供代理自动执行。

创建自定义技能的步骤：

15.在 ~/.agents/skills/ 目录下为你的技能创建一个新文件夹：

mkdir -p ~/.agents/skills/my-custom-skill

16.在该文件夹中创建 SKILL.md 文件，遵循以下格式：

\---

name: my-custom-skill

description: 使用当 \[触发条件\] - \[技能功能说明\]

\---

\# 我的自定义技能

\[在这里写你的技能内容\]

17.description 字段是技能自动触发的关键——写成一个清晰的触发条件描述，让代理知道在什么情况下应该使用这个技能。

18.重启代理，新技能会在启动时被自动发现。

如果你想为整个 Superpowers 社区贡献自己的技能，可以 Fork 项目仓库，在 skills/ 目录下添加你的技能，并按照 writing-skills 技能中的指南进行测试后提交 Pull Request。

第七章 常见问题与最佳实践

7.1 常见问题（FAQ）

Q：技能没有自动触发怎么办？

A：请检查以下几点：首先确认安装步骤已正确完成；其次重启你的代理平台（技能在启动时被扫描）；对于 Codex，运行 ls -la ~/.agents/skills/superpowers 验证符号链接是否正常；最后，你也可以直接在对话中提到技能名称来手动触发。

Q：Superpowers 会减慢我的开发速度吗？

A：短期来看，brainstorming 和 writing-plans 阶段会花费一些额外时间。但从整个项目周期看，这些前期投入能避免大量的返工和调试时间，总体效率显著提升。对于复杂项目，子代理驱动的并行开发更是能将执行时间大幅压缩。

Q：我必须使用所有七个阶段吗？

A：不是所有场景都需要完整的七阶段流程。对于简单的 Bug 修复，可以直接使用 systematic-debugging 技能；对于小型改动，可以跳过 writing-plans 直接进入实现。Superpowers 足够灵活，技能可以按需单独使用。

Q：如何更新 Superpowers？

A：在 Claude Code 中执行 /plugin update superpowers；在 Codex 中执行 cd ~/.codex/superpowers && git pull；技能通过符号链接即时生效，无需重新安装。

Q：Superpowers 支持哪些编程语言？

A：Superpowers 本身是语言无关的，它定义的是软件开发的工作流和方法论，而不是具体的编程语言规范。因此，它可以与任何编程语言配合使用，只要你的代理平台支持该语言即可。

7.2 最佳实践建议

•充分参与头脑风暴阶段：不要急于跳过 brainstorming，在这里花时间是最值得的投资

•认真审阅计划文档：在确认计划之前，仔细阅读每个任务的详情，确保你真正理解并认可实现方案

•保持测试优先的习惯：即使在时间紧迫的情况下，也不要跳过 TDD 流程，这是代码质量的最后防线

•善用并行代理：对于可以独立进行的任务，主动告知代理可以并行执行，显著节省时间

•定期检查进度：在子代理工作期间，利用检查点（checkpoints）审阅已完成的工作，及时发现偏差

•记录自定义技能：当你的团队形成了有效的工作模式时，将其编写成自定义技能，让整个团队受益

7.3 更新与社区资源

以下是 Superpowers 的官方资源，欢迎积极参与社区：

| 资源 | 地址 | 说明 |
| --- | --- | --- |
| GitHub 仓库 | github.com/obra/superpowers | 源代码、Issues、PR |
| Discord 社区 | discord.gg/Jd8Vphy9jq | 社区支持、问题解答、交流分享 |
| 官方博客 | blog.fsck.com | 作者 Jesse Vincent 的博客，深度解析 |
| 版本更新 | primeradiant.com/superpowers | 注册接收新版本发布通知 |
| 开源赞助 | github.com/sponsors/obra | 支持作者的开源工作 |

附录：关注作者

如果这份教程对你有帮助，欢迎扫码关注作者的公众号和视频号，获取更多 AI 开发实战内容、工具推荐和技术分享。

| ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  📱 微信公众号 | ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  🎬 微信视频号 |
| --- | --- |

感谢阅读！如果你觉得这份指南有价值，欢迎转发分享给更多朋友。