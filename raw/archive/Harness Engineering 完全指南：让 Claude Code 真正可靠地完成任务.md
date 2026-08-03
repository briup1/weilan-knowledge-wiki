---
title: "Harness Engineering 完全指南：让 Claude Code 真正可靠地完成任务"
source: "https://mp.weixin.qq.com/s/bDj4Gd2OVWeW3wqVQBJj3A"
author:
  - "[[程康健]]"
published:
created: 2026-05-14
description: "如果今天你还是觉得 AI 不行，大概率不是 AI 不行，而是你不行（没驾驭好 AI）。这话听起来有点扎心，但是在 AI Coding 的大多数场景成立。AI 模型在今天已不是问题，表现不行是因为你的项目缺少了一套工程化框架。Harness Engineering 就是这套框架。"
tags:
  - "clippings"
---
程康健 *2026年4月29日 09:29*

如果今天你还是觉得 AI 不行，大概率不是 AI 不行，而是你不行（没驾驭住 AI）。这话听起来有点扎心，但是在 AI 编程的大多数场景下成立。因为今天的 AI 大模型已经足够强，如果表现不好，大概率不是模型的问题，而是你的项目配套的工程化建设在 AI 时代没跟上。

随意举一个老生常谈的例子：

你打开 Claude Code，输入一个需求：「帮我做一个用户管理系统，要有登录、注册、权限控制。」

Agent 开始工作，写了一会儿，输出一大堆代码，然后告诉你： **「任务完成。」**

你去跑一下，发现：登录页面点击按钮没有反应。注册接口返回 500。权限控制根本没实现。

然后你重新开一个会话，Agent 对之前做了什么一无所知，又从头开始。

---

这件事很容易让人得出一个错误结论： **「AI 不行，不能用于真实项目」。**

其实问题不在模型，在于你缺少一套 **约束 Agent 行为的工程化框架** 。

这套框架有个名字： **Harness Engineering（脚手架工程）** 。

Anthropic 的工程师在内部用它驱动 Agent 构建真实生产级应用。核心思路很简单：

- 把所有状态外化到文件系统，不依赖 Agent 的「记忆」
- 用结构化的功能清单定义「什么叫完成」
- 强制端到端验证，而不是单元测试自欺欺人
- 每次会话结束做好交接，下一个 Agent 直接继续

这份指南，由 AI 工具辅助生成、我负责内容结构策划和准确性审核。

这本身就是 Harness Engineering 的一次实践： **用好 AI，做出一个人做不到的效率。**

12 讲 + 5 个附录模板，从零基础到多智能体架构，所有模板开箱即用，复制进你的项目就能跑。

---

完全新手指南 · 2026 Edition

程序员康健 × AI 编程系列

Harness Engineering

完全新手指南

让 AI Agent 真正可靠地完成真实工程任务

| 章节数  12+2 讲 | 适合人群  零基础 | 参考来源  Anthropic |
| --- | --- | --- |

基于 Anthropic Engineering Blog 整理 · walkinglabs.github.io/learn-harness-engineering

目 录

快速上手指南（10 分钟入门）

前言：什么是 Harness Engineering，为什么它重要

Harness Engineering 解决什么问题？

第一部分 · 理论基础

第 01 讲：模型能力强，不等于执行可靠

能力 vs 可靠性对比

三大核心失败模式

第 02 讲：Harness 的定义——什么是脚手架工程

Harness 的四个组成要素

最小可行 Harness 的目录结构

第 03 讲：让代码仓库成为唯一的事实来源

第 04 讲：把指令拆分到不同文件里

第二部分 · 上下文管理

第 05 讲：让跨会话的任务保持上下文连续

第 06 讲：让 Agent 每次工作前先初始化

Initializer Agent 的职责

Coding Agent 每次会话的标准启动流程

第 07 讲：给 Agent 划清每次任务的边界

第三部分 · 验证与控制

第 08 讲：用功能清单（Feature List）约束 Agent

第 09 讲：防止 Agent 提前宣告完成

第 10 讲：跑通完整流程才算真正验证

第 11 讲：让 Agent 的运行过程可观测

第 12 讲：每次会话结束前都做好交接

第四部分 · 进阶架构

多智能体架构：Planner + Generator + Evaluator

Sprint Contract 协商流程

评估维度与打分标准

附录 A：AGENTS.md 最小可用模板

附录 B：feature\_list.json 最小模板

附录 C：claude-progress.txt 初始化模板

附录 D：init.sh 通用模板

附录 E：常见问题 Q&A

延伸：Hermes Agent——Harness 思想的开源产品化

与 Harness Engineering 的对应关系

Hermes Agent 的三大核心机制

Hermes Agent vs Claude Code：不是竞争，是互补

什么情况下应该考虑 Hermes Agent？

与本指南的关系：下一步学什么？

快速上手指南（10 分钟入门）

如果你是第一次接触 Harness Engineering，不需要一次性读完全文。按照下面 7 个步骤操作，10 分钟内就能建立起一个可用的基础 Harness。

📌 适用场景

你正在使用 Claude Code / Cursor / Windsurf 等 AI 编程工具，想要让 Agent 更可靠地完成一个多功能的项目（如 Web 应用、CLI 工具、API 服务等）。

1.在项目根目录创建 AGENTS.md，复制附录 A 的模板，根据项目实际情况修改

2.创建 feature\_list.json，复制附录 B 的模板，将高层需求拆解为具体功能条目（每条包含 steps）

3.创建 claude-progress.txt，复制附录 C 的模板，填写项目名、技术栈

4.编写 init.sh，实现一键启动开发服务器

5.git init && git add. && git commit -m 'init: harness structure'

6.启动 Claude Code，在会话开始时发送：\`请先读取 AGENTS.md 和 claude-progress.txt，然后告诉我你的理解\`

7.确认 Agent 理解规则后，发送：\`请从 feature\_list.json 中选择优先级最高的未完成功能开始实现\`

✅ 完成标志

当 Agent 在新会话开始时，能自主读取状态文件、告诉你「上次完成了 Feature X，本次将实现 Feature Y」，说明你的 Harness 已经生效。

前言：什么是 Harness Engineering，为什么它重要

随着 Claude Code、OpenAI Codex 等 AI 编程工具的普及，越来越多的程序员开始让 AI Agent 去执行复杂的工程任务。然而，很多人发现：模型本身很聪明，但实际执行却漏洞百出。任务做到一半就停了、功能没测通就宣布完成、下一轮上下文清空后忘了之前做了什么……

这些问题的根源不在于模型能力不足，而在于缺少一套约束 Agent 行为的工程化框架。这套框架就叫做 Harness Engineering（脚手架工程）。

「想象一个由多个工程师轮班工作的软件项目——每一班的工程师到岗时对前一班做了什么毫无记忆。AI Agent 的跨会话工作就是这种处境。Harness Engineering 就是为他们设计的「交接班制度」。」

— Anthropic Engineering Blog, 2025

Harness Engineering 解决什么问题？

| 问题 | 表现 | 根本原因 |
| --- | --- | --- |
| 上下文断裂 | 每次新会话从零开始，无法感知之前的进度 | 无持久化状态机制 |
| 任务过载 | 一次性尝试完成所有事情，上下文溢出导致烂尾 | 缺乏任务边界约束 |
| 提前宣告完成 | 功能未真正完成就宣告任务已完成 | 缺乏客观完成标准 |
| 验证不充分 | 单元测试通过但端到端用户路径有 Bug | 验证方式不全面 |

── 第一部分 · 理论基础 ──

第 01 讲：模型能力强，不等于执行可靠

很多人在第一次使用 Claude Code 时会困惑：模型在回答问题时非常聪明，但当你让它真正执行一个多步骤的工程任务时，它却频繁出错、偏离目标。这不是模型「不聪明」，而是两个完全不同的能力维度：能力（Capability）≠ 可靠性（Reliability）。

能力 vs 可靠性对比

| 维度 | 模型能力（Capability） | 执行可靠性（Reliability） |
| --- | --- | --- |
| 定义 | 模型能否「知道」正确答案 | 模型能否「持续做对」正确的事 |
| 衡量方式 | Benchmark 得分、推理准确率 | 长任务完成率、错误率、返工率 |
| 影响因素 | 训练数据、参数规模、RLHF | 工具设计、上下文管理、验证机制 |
| 提升方法 | 模型训练（你无法控制） | Harness 工程化设计（你完全掌控） |

▶ 核心洞察

Anthropic 的工程师发现：即便是最强的 Opus 模型，在没有 Harness 的情况下，给它「帮我构建一个 claude.ai 的克隆」这样的高层指令，也无法可靠地完成生产质量的应用。模型能力是必要条件，但不是充分条件。

三大核心失败模式

| 失败模式 | 根本原因 | Harness 解法 |
| --- | --- | --- |
| Agent 试图一次性完成整个应用，上下文溢出时任务烂尾 | 没有拆分任务，没有约束单次会话工作范围 | 每次只做一个功能，每次结束必须提交 git + 写进度文件 |
| Agent 在任务后期看到已有进度，主动宣布「任务完成」 | 缺乏对「什么叫完成」的客观定义，只能主观判断 | 维护结构化功能清单，每个功能有明确的 pass/fail 状态 |
| Agent 执行了 curl/单元测试认为功能通过，但端到端路径有 Bug | 验证方式不够全面，没有模拟真实用户操作 | 强制使用 Puppeteer MCP 进行端到端测试 |

第 02 讲：Harness 的定义——什么是脚手架工程

「Harness」原意是「马具」——驾驭马匹的皮带、衔铁、缰绳的组合。在 AI 工程领域，Harness 是指围绕 AI Agent 建立的一套运行框架，包括：提示词结构、工具配置、状态管理、验证机制、上下文传递规则的总和。

▶ 类比理解

如果 AI 模型是一匹聪明的马，那么 Harness 就是驾驭它的马具系统——不是让马更聪明，而是让马按照预期的方向、速度、节奏稳定运行。

Harness 的四个组成要素

| 要素 | 内容 | 作用 |
| --- | --- | --- |
| 📋 提示词结构 | 明确告诉 Agent 它的角色、任务边界、以及被禁止做的事情 | 约束行为方向 |
| 🗂️ 状态文件 | AGENTS.md、feature\_list.json、claude-progress.txt 等结构化文件 | 跨会话状态持久化 |
| 🔧 工具配置 | git、浏览器自动化、文件读写、代码执行等工具 | 赋能 Agent 操作能力 |
| ✅ 验证机制 | 规定何时、如何验证工作成果，防止 Agent 自我认定「完成」 | 保证输出质量 |

最小可行 Harness 的目录结构

project/

├── AGENTS.md # Agent 工作规范（全局规则）

├── feature\_list.json # 功能清单，每项有 pass/fail 状态

├── claude-progress.txt # 进度日志，每次会话后更新

├── init.sh # 环境初始化脚本

├──.git/ # git 版本控制（必须）

└── src/ # 业务代码

这套结构的核心思想是：把 Agent 需要知道的一切，都外化到文件系统中，而不是依赖 Agent 的「记忆」。每次新会话，Agent 只需要读取这些文件，就能快速恢复工作状态。

第 03 讲：让代码仓库成为唯一的事实来源

Repository as the Single Source of Truth——AI Agent 没有持久记忆，每次会话结束上下文清空。唯一能跨会话存活的，是文件系统中的内容。因此，Harness 第一原则是把代码仓库设计为唯一的事实来源，所有决策、进度、状态都必须以文件形式写入仓库。

为什么 git 是 Harness 的核心组件？

•版本快照：每次完成一个功能，Agent 提交 commit。出现 Bug 可以随时 git revert 回退。

•上下文传递：新会话的 Agent 通过 git log --oneline 快速了解之前做了什么。

•进度可视：commit message 本身就是任务进度的文档，不需要额外记录工作。

•协作基础：多个 Agent 实例或人机协作时，git 提供冲突检测和合并能力。

⚠ 反模式警告

不要让 Agent 只在内存/对话中维护进度。「我已经完成了 Feature A」——这句话在下一个 context window 里等于不存在。必须通过 commit + 文件持久化这个状态。

实践：AGENTS.md 中强制会话末尾提交

\# 会话结束规则（必须遵守）

在每次工作会话结束前，你必须：

1\. 将所有代码更改提交到 git，commit message 格式：

"feat: \[功能名\] - \[简短描述\]"

例如："feat: user-auth - add JWT login endpoint"

2\. 在 claude-progress.txt 中追加本次会话摘要

3\. 更新 feature\_list.json 中相关功能的 pass 状态

禁止：在没有 commit 的情况下结束会话。

第 04 讲：把指令拆分到不同文件里

新手常见的错误是：把所有规则全部塞进一个超长的 AGENTS.md。这会造成：信息密度过高难以检索；文件更新牵一发动全身；Agent 会「遗忘」靠后的内容（注意力衰减）；不同阶段的指令混在一起产生干扰。

推荐的文件分层结构

| 文件 | 作用 | 由谁读取 |
| --- | --- | --- |
| AGENTS.md | 全局工作规范（角色、禁止行为、通用规则） | 所有 Agent 实例 |
| init.sh | 环境启动脚本（如何运行开发服务器） | 每次会话开始时执行 |
| feature\_list.json | 功能清单与完成状态 | Coding Agent，判断下一步做什么 |
| claude-progress.txt | 人类可读的进度日志 | 每次会话开始时阅读 |
| SKILL.md（可选） | 特定领域的技术规范（如前端设计规范） | 需要时按需读取 |

▶ 设计原则

每个文件只负责一件事（Single Responsibility）。Agent 在需要某类信息时，明确知道该读哪个文件，而不是在一个大文件中费力搜索。

── 第二部分 · 上下文管理 ──

第 05 讲：让跨会话的任务保持上下文连续

AI Agent 的工作单位是「会话（Session）」，每次会话对应一个 Context Window。当 Context Window 用完，必须开启全新会话。新会话的 Agent 对之前发生的一切一无所知——就像一个完全不同的人接手了工作。

Context 的两种处理方式对比

| 方式 | Compaction（压缩） | Context Reset（重置） |
| --- | --- | --- |
| 机制 | 将早期对话摘要压缩，同一 Agent 继续工作 | 完全清空 Context，启动新 Agent，通过文件传递状态 |
| 优点 | 保持连续性，无需设计交接流程 | 彻底解决「Context 焦虑」，Agent 以全新状态工作 |
| 缺点 | 仍然累积噪音，不能完全解决 Context Anxiety | 增加交接复杂度，需要设计完善的状态传递文件 |
| 适用场景 | 中短任务，Sonnet 级别模型 | 长期复杂任务，需要稳定多会话执行 |

⚠ Context Anxiety（上下文焦虑）

Anthropic 的工程师观察到：当 Context Window 接近上限时，某些模型会开始「急于收尾」，草草结束任务，甚至宣布完成——即使实际上还有大量工作未做。Context Reset 是解决它的根本方案。

跨会话状态传递流程

| 阶段 | 操作 | 持久化内容 |
| --- | --- | --- |
| 会话 N 结束 | 执行任务，完成 Feature X | git commit + 进度文件更新 |
| 状态写入 | 将工作成果持久化到文件系统 | claude-progress.txt + feature\_list.json |
| 会话 N+1 启动 | 新 Agent 读取状态文件快速定位 | 了解当前进度，继续 Feature Y |

第 06 讲：让 Agent 每次工作前先初始化

Harness 的一个关键设计是：第一次运行使用专用的 Initializer Agent，与后续的 Coding Agent 完全分离。这不是两个不同的模型，而是两个不同的 System Prompt。

Initializer Agent 的职责

1.阅读用户的高层需求，将其展开为详细的功能清单（feature\_list.json），每个功能都标记为 passes: false

2.编写 init.sh 脚本，确保任何人（或任何 Agent）都能一键启动开发环境

3.创建初始 git commit，建立仓库基础结构

4.在 claude-progress.txt 中写入项目启动日志

5.设定技术栈选择、目录结构等全局架构决策

▶ 为什么要分离？

初始化需要宏观视角（想清楚做什么），编码需要微观执行（专注做好一件事）。混用一个 Agent 做两件事，往往导致它一边初始化一边编码，计划和执行交织，容易失控。

Coding Agent 每次会话的标准启动流程

1.运行 pwd，确认工作目录

2.读取 claude-progress.txt，了解上次进度

3.运行 git log --oneline -20，查看最近提交

4.执行./init.sh，启动开发服务器

5.读取 feature\_list.json，确认下一个待完成功能

6.运行基础端到端测试，确认当前代码状态正常

\# Coding Agent 系统提示（每次会话开始）

完成以上步骤后，开始实现 feature\_list.json 中

优先级最高的未完成功能。每次只做一个功能。

第 07 讲：给 Agent 划清每次任务的边界

没有边界约束的 Agent 有两种极端行为：要么贪多嚼不烂（一次性实现 10 个功能，每个都不完整），要么点到为止（实现了 80% 就认为完成了）。两种情况都会导致项目陷入混乱。

边界设计的三个层次

1\. 任务粒度边界

在 AGENTS.md 中明确规定：每次会话只实现 feature\_list.json 中的一个功能。不得在当前功能未完成前开始下一个。不得「顺便」修改未在本次任务范围内的代码。

2\. 完成定义边界

每个功能必须有明确的「完成标准」（Definition of Done）。在多 Agent 架构中，由 Generator 和 Evaluator 在实现前先协商 Sprint Contract：约定这个功能做什么、如何验证成功，双方达成一致后再开始编码。

3\. 代码质量边界

规定「完成」意味着：代码可以合并到主分支——没有重大 Bug，代码整洁有文档，其他开发者无需清理旧代码即可继续开发。这被称为「Clean State」（干净状态）。

⚠ 经典反模式

Agent 在实现 Feature A 时，「顺便」修改了 Feature B 的代码，且没有提交独立的 commit。当 Feature A 出现 Bug 需要回滚时，Feature B 的改动也一起丢失了。务必要求 Agent 每个功能独立 commit。

── 第三部分 · 验证与控制 ──

第 08 讲：用功能清单（Feature List）约束 Agent

功能清单（feature\_list.json）是整个 Harness 中最重要的单一文件。它将用户的高层需求分解为一系列可验证的、有明确完成状态的功能条目。

feature\_list.json 的结构设计

{

"features": \[

{

"id": "auth-001",

"category": "functional",

"description": "用户可以使用邮箱和密码注册账号",

"priority": 1,

"steps": \[

"进入注册页面",

"填写邮箱、密码、确认密码",

"点击注册按钮",

"验证跳转到首页，且顶部显示登录状态"

\],

"passes": false

}

\]

}

▶ 来自 Anthropic 的实践经验

Anthropic 工程师发现：使用 JSON 格式的功能清单，模型不适当地修改或删除已有条目的概率远低于 Markdown 格式。JSON 的结构化约束使模型倾向于只修改 passes 字段，而不是「简化」或「合并」条目。

AGENTS.md 中的操作约束

\# feature\_list.json 操作规则

严格禁止：

\- 删除任何已有的功能条目

\- 修改功能描述或验证步骤

\- 在未实际测试的情况下将 passes 改为 true

仅允许：

\- 完成功能并通过端到端测试后，将 passes 从 false 改为 true

第 09 讲：防止 Agent 提前宣告完成

「提前宣告完成」是 AI Agent 在长任务中最常见的失败模式之一。Agent 看到已经做了一些工作，便产生了任务完成的错觉，然后停止工作——即使功能清单上还有大量条目标记为 pass: false。

为什么 Agent 会提前宣告完成？

•没有客观的「完成标准」，只能依靠主观感受

•上下文接近上限时，Agent 产生「收尾冲动」（Context Anxiety）

•Agent 对自己的工作评分时，天然倾向于给高分（自我评估偏差）

•缺乏独立的外部验证机制

四种防止提前宣告的机制

机制一：功能清单强制检查

在 AGENTS.md 中规定：在每次会话结束前，必须重新读取 feature\_list.json，确认所有 passes: true 的条目都经过了本会话的端到端测试验证。

机制二：独立评估 Agent

在多 Agent 架构中，引入独立的 Evaluator Agent，专门负责验证 Generator Agent 的工作成果。Evaluator 被明确提示：对 LLM 生成的内容要持怀疑态度，而非默认相信。

机制三：浏览器自动化强制验证

对 Web 应用而言，规定只有通过 Puppeteer/Playwright 的端到端测试，功能才能被标记为完成。curl 命令或单元测试不够——必须像真实用户一样点击、输入、提交来验证。

机制四：进度文件不自欺

在 claude-progress.txt 中，明确区分「已完成并验证」和「已实现但未验证」的功能。诚实记录遗留问题，而不是选择性地只写好的进展。

第 10 讲：跑通完整流程才算真正验证

Agent 往往会做以下测试后认为功能已完成：运行单元测试（通过）、用 curl 直接调用 API 端点（返回 200）、在代码中做静态分析（无明显错误）。

但这些都不等于功能对真实用户是可用的。按钮没绑定点击事件、表单提交后没有状态反馈、页面跳转路径断了——这些 Bug 只有在端到端用户路径测试中才能被发现。

Puppeteer MCP：给 Agent 一双真实的眼睛

Anthropic 在实践中为 Agent 接入了Puppeteer MCP服务器，让 Agent 能够真正控制浏览器，像用户一样操作应用。

\# Agent 使用 Puppeteer MCP 进行端到端测试示例

\[Assistant\] 我来验证"用户注册"功能是否正常工作。

\[Tool Use\] puppeteer.navigate("http://localhost:3000/register")

\[Tool Use\] puppeteer.screenshot() # 截图确认页面加载

\[Tool Use\] puppeteer.fill("#email", "test@example.com")

\[Tool Use\] puppeteer.fill("#password", "Test1234!")

\[Tool Use\] puppeteer.click("#register-btn")

\[Tool Use\] puppeteer.screenshot() # 截图确认跳转结果

\[Tool Use\] puppeteer.evaluate("document.querySelector('.user-avatar')!== null")

\[Assistant\] 端到端测试通过，注册功能已验证。将 passes 更新为 true。

▶ 最佳实践

在每次新会话开始时，Coding Agent 应先运行一次基础的端到端烟雾测试（Smoke Test），确认上一次会话留下的代码库处于正常状态。

第 11 讲：让 Agent 的运行过程可观测

在 Harness Engineering 中，可观测性意味着：你随时能知道 Agent 正在做什么、做了什么、下一步打算做什么。

Harness 中的三层可观测性

层一：结构化日志（claude-progress.txt）

每次会话结束后，Agent 追加结构化的进度摘要。格式固定，便于阅读和机器解析。

\== 2025-11-26 Session #7 ==

已完成：feat/user-profile-page

\- 实现用户资料展示页面（/profile/:id）

\- 支持头像、昵称、注册时间展示

\- Puppeteer 端到端测试通过

遗留问题：头像上传功能暂未实现（依赖文件存储服务）

下一步建议：实现 feat/file-upload（feature\_list.json #12）

Git Commit：a3f9c21 feat: user-profile - add profile page

层二：Git 历史（git log）

规范的 commit message 是最轻量级的可观测性工具。要求 Agent 在每次提交时写清楚做了什么，而不是用「update」、「fix」这样的模糊描述。

层三：功能清单状态（feature\_list.json）

通过功能清单的 passes 状态分布，你可以一眼看出项目的整体进度——有多少功能已完成，还剩多少，哪些优先级高。

▶ 可视化建议

用脚本读取 feature\_list.json 生成进度看板： jq '\[.features\[\] | select(.passes == true)\] | length' feature\_list.json 快速显示已完成功能数量。

第 12 讲：每次会话结束前都做好交接

好的会话交接，就像好的 Code Review：你提交的代码，应该是同事可以直接在此基础上继续工作的状态——没有 TODO 地雷，没有半实现的功能，没有未处理的异常。

Clean State 交接清单

1.代码已提交（git commit）：所有本次会话的代码变更都已 commit，commit message 清晰描述了做了什么。

2.功能状态已更新（feature\_list.json）：实现并测试通过的功能已标记为 passes: true，未完成的仍为 false。

3.进度日志已追加（claude-progress.txt）：记录了本次完成情况、遗留问题、下一步建议。

4.开发服务器可正常启动：确认./init.sh 能够正常运行，应用处于可工作状态。

5.基础端到端测试通过：运行一次冒烟测试，确认核心用户路径正常。

▶ 关键原则

下一个 Agent 不应该需要花时间「修复上一个 Agent 留下的烂摊子」。每次交接都应该是「干净的」——可以直接继续推进新功能，而不是先修 Bug。

── 第四部分 · 进阶架构 ──

进阶篇：多智能体架构——Planner + Generator + Evaluator

基础 Harness（Initializer + Coding Agent）已经能解决大多数问题。但在面对高复杂度、长时间、高质量要求的任务时，Anthropic 进一步演化出了三 Agent 架构。

「将生成任务与评估任务分离，是这套架构最核心的洞察。让生成者自我评估，效果远不如让专门的评估者来评估——即使两者都是同一个底层模型。」

三 Agent 架构详解

① Planner Agent（规划者）

接收用户的 1-4 句话高层需求，扩展成完整的产品规格文档（PRD）。它关注「要做什么」，而不是「怎么实现」——刻意避免过早指定技术细节，防止错误的早期技术决策污染后续实现。

② Generator Agent（生成者）

从规格文档中逐功能实现，每次 Sprint 前与 Evaluator 协商Sprint Contract（约定做什么、如何验证），确认后开始编码。每个 Sprint 结束后先自我评估，再交给 Evaluator 进行独立评估。

③ Evaluator Agent（评估者）

使用 Playwright MCP 控制浏览器，像真实用户一样操作应用，检查 UI 功能、API 端点、数据库状态。按照预定标准打分，如有维度低于阈值则退回 Generator 修改，并提供详细修改建议。

Sprint Contract 协商流程

1.Planner 输出产品规格文档（PRD），列出所有功能需求，不涉及具体实现

2.Generator 读取 PRD，选择当前 Sprint 要实现的功能，起草 Sprint Contract

3.Evaluator 审阅 Sprint Contract，确认验证标准可测量，双方达成一致

4.Generator 开始编码，完成后进行自我评估

5.Evaluator 使用浏览器自动化独立验证，按评分标准打分

6.如评分不达标，Evaluator 返回详细修改建议，Generator 修复后重新评估

7.评分达标后，Generator 提交 commit，更新 feature\_list.json 和 claude-progress.txt

▶ Sprint Contract 模板

在开始编码前，Generator 向 Evaluator 发送： 「本次 Sprint 目标：实现\[功能名\]。 完成标准：用户可以\[具体操作\]，验证方式：\[具体测试步骤\]。 请确认此标准是否可测量？」 Evaluator 确认后，Generator 方可开始编码。

评估维度与打分标准

| 维度 | 评估内容 | 最低通过分 | 权重 |
| --- | --- | --- | --- |
| 设计质量 | 颜色、字体、布局是否构成有凝聚力的整体 | 7/10 | 高 |
| 原创性 | 是否有明显自定义设计决策，而非 AI 默认风格 | 7/10 | 高 |
| 工艺精度 | 字体层级、间距一致性、颜色对比度等技术基本功 | 8/10 | 中 |
| 功能可用性 | 用户能否理解界面、找到主操作、完成核心任务 | 9/10 | 中 |

▶ 关键发现

Anthropic 的实验发现：即使是第一轮（Evaluator 给出任何反馈之前），带有明确评估标准的 Generator 产出的质量，已明显优于完全没有 Harness 约束的基准输出。评估标准本身就具有引导作用。

── 附录 · 开箱即用模板 ──

附录 A：AGENTS.md 最小可用模板

\# AGENTS.md — AI Agent 工作规范

\## 角色定义

你是一名专业的软件工程师。你的任务是逐功能实现本项目，

并在每次工作会话结束前完成交接。

\## 每次会话开始（必须执行）

1\. 运行 pwd 确认工作目录

2\. 读取 claude-progress.txt 了解上次进度

3\. 运行 git log --oneline -10 查看最近提交

4\. 执行./init.sh 启动开发环境

5\. 读取 feature\_list.json 确认下一个待完成功能

\## 工作规则（必须遵守）

\- 每次只实现 feature\_list.json 中的一个功能

\- 未经端到端测试，不得将 passes 改为 true

\- 不得删除或修改 feature\_list.json 中已有条目

\- 不得在未完成当前功能时开始下一个功能

\## 每次会话结束（必须执行）

1\. git commit（格式："feat: \[功能ID\] - \[描述\]"）

2\. 更新 feature\_list.json 中的 passes 状态

3\. 在 claude-progress.txt 追加会话摘要

\## 绝对禁止

\- 在没有 commit 的情况下结束会话

\- 删除测试条目或修改测试步骤

\- 宣告任务完成但 feature\_list.json 还有 passes: false 的条目

附录 B：feature\_list.json 最小模板

{

"project": "your-project-name",

"last\_updated": "2025-11-26",

"features": \[

{

"id": "setup-001",

"category": "infrastructure",

"description": "项目基础环境搭建完成，init.sh 可正常运行",

"priority": 1,

"steps": \["运行./init.sh 无报错", "开发服务器在 localhost:3000 正常响应", "数据库连接正常"\],

"passes": false

},

{

"id": "feature-001",

"category": "functional",

"description": "你的第一个功能描述",

"priority": 2,

"steps": \["测试步骤一", "测试步骤二", "验证预期结果"\],

"passes": false

}

\]

}

附录 C：claude-progress.txt 初始化模板

\== PROJECT: \[项目名称\] ==

\== STARTED: \[日期\] ==

\== STACK: \[技术栈，如 React + FastAPI + PostgreSQL\] ==

─── Session #1 (初始化) ───

已完成：

\- 项目结构初始化

\- 基础依赖安装

\- init.sh 编写完成

\- feature\_list.json 创建（共 N 个功能待实现）

遗留问题：无

下一步：实现 feature-001（优先级最高的功能）

附录 D：init.sh 通用模板

init.sh 是整个 Harness 的「发动机」——任何人或任何 Agent 执行它，都能在 30 秒内进入可工作状态。以下是一个通用模板，适用于大多数 Web 项目：

init.sh 应包含的 6 个步骤

1.检查依赖是否安装（node\_modules / venv / go modules 等）

2.安装依赖（npm install / pip install -r requirements.txt 等）

3.设置环境变量（从.env.example 复制.env 如果不存在）

4.启动数据库服务（如果需要）

5.运行数据库迁移（如果需要）

6.启动开发服务器，打印访问地址

#!/bin/bash

\# init.sh — 项目开发环境初始化脚本

set -e # 任何命令失败立即退出

echo '🔧 初始化开发环境...'

\# 1. 检查并安装依赖

if \[! -d 'node\_modules' \]; then

echo '📦 安装依赖...'

npm install

fi

\# 2. 设置环境变量

if \[! -f '.env' \]; then

cp.env.example.env

echo '⚠️ 已创建.env 文件，请检查配置'

fi

\# 3. 数据库迁移（如果需要）

\# npm run db:migrate

\# 4. 启动开发服务器

echo '🚀 启动开发服务器...'

npm run dev &

echo '✅ 开发环境就绪：http://localhost:3000'

▶ 关键要求

init.sh 必须具备幂等性（Idempotent）——无论执行多少次，结果都相同，不会因为「已经安装过依赖」而报错。Agent 每次会话都会执行它，必须保证绝对可靠。

附录 E：常见问题 Q&A

Q1：Agent 总是忽略 AGENTS.md 中的规则，怎么办？

A：AGENTS.md 的内容过多是常见原因。建议：① 把绝对规则放在文件最前面；② 使用强制性语言（「必须」、「绝对禁止」）而非建议性语言（「应该」、「最好」）；③ 在 System Prompt 中补充：「在每次回复前，先检查是否违反了 AGENTS.md 中的任意规则」。

Q2：feature\_list.json 中的步骤应该写多详细？

A：步骤应该细化到「可以被浏览器自动化脚本直接执行」的程度。举例：❌「用户可以登录」（太模糊）；✅「进入 /login 页面 → 输入邮箱和密码 → 点击「登录」按钮 → 验证页面跳转到 / 且顶部导航显示用户头像」（可测量）。

Q3：Agent 把 passes: false 的功能标记为 true 了，怎么处理？

A：① 立即用 git revert 回滚错误的提交；② 在 AGENTS.md 中加强约束：「在将 passes 改为 true 之前，必须粘贴 Puppeteer 测试的截图或日志作为证明」；③ 在多 Agent 架构中，该操作必须由 Evaluator 执行，Generator 无权修改 passes 字段。

Q4：我的项目不是 Web 应用，没有浏览器，如何做端到端验证？

A：针对不同类型项目，端到端验证的方式有所不同：CLI 工具 → 用脚本模拟真实用户的命令行输入和输出；API 服务 → 编写完整的集成测试，覆盖从 HTTP 请求到数据库状态变化的全链路；数据处理脚本 → 用真实规模的样本数据运行，验证输出文件的格式和内容是否符合预期。核心原则不变：模拟真实使用场景，而非只测试代码片段。

Q5：同时运行多个 Agent 实例，如何避免冲突？

A：推荐使用「功能分支」策略：① 每个 Agent 实例在独立的 git 分支上工作（branch-per-feature）；② feature\_list.json 中为每个功能增加 assigned\_to 字段，防止两个 Agent 同时实现同一功能；③ 只有 Orchestrator（主控）Agent 有权合并分支和更新主 feature\_list.json。

── 扩展阅读 · Harness Engineering 的产品化实现 ──

延伸：Hermes Agent——Harness 思想的开源产品化

读完本指南，你已经掌握了手工构建 Harness 的完整方法论。但你可能会问：有没有把这些机制内置好、开箱即用的产品？答案是有——Hermes Agent 就是目前最接近这个方向的开源实现。

Hermes Agent 是 Nous Research 于 2026 年 2 月发布的开源 AI Agent 框架（GitHub: github.com/NousResearch/hermes-agent），标语是「The agent that grows with you」（与你共同成长的 Agent）。

与 Harness Engineering 的对应关系

本指南讲的是「你手工搭建 Harness 的方法」，Hermes Agent 则把这套机制产品化内置了。两者的对应关系如下：

| Harness Engineering（手工方案） | Hermes Agent（产品化实现） |
| --- | --- |
| 手动维护 claude-progress.txt 和 AGENTS.md | 内置三层持久记忆：会话上下文 + 持久事实 + 程序技能，自动跨会话积累 |
| 手工编写 SKILL.md 文件管理技能 | 内置学习循环：每次完成任务后自动提炼、存储、优化可复用 Skill |
| 每次会话开始手动读取状态文件恢复上下文 | 常驻守护进程，持续运行，无需手动恢复 |
| 通过 git commit 追踪进度，终端访问 | 支持 Telegram、Discord、Slack、WhatsApp 等 15+ 平台随时访问 |
| 手动配置 Initializer + Coding Agent 分工 | 内置 Planner/Generator/Evaluator 多 Agent 编排（开发中） |
| 绑定 Claude 模型 | 支持 200+ 模型，hermes model 一键切换，无代码改动 |

Hermes Agent 的三大核心机制

① 自动技能进化（Learning Loop）

这是 Hermes 与其他 Agent 最本质的区别。传统 Agent（包括裸用 Claude Code）每次会话结束后「归零」，下次从头开始。Hermes 则在每次完成复杂任务后，自动将解决方案提炼成可复用的 Skill 文件存入本地库。下次遇到类似任务时，直接调用已有 Skill，越用越快、越用越准。

▶ 对应 Harness 概念

这等同于把你手写 SKILL.md 的过程完全自动化——你不再需要手动总结和维护技能文档，Agent 自己来做。

② 三层持久记忆（Persistent Memory）

Hermes 使用 SQLite + FTS5 全文检索存储所有历史会话，配合 LLM 驱动的摘要层，实现：

•会话记忆：当前对话的完整上下文

•事实记忆：你的偏好、项目约定、反复出现的信息（对应你手动维护的 AGENTS.md）

•技能记忆：历次任务提炼出的可复用操作流程（对应 SKILL.md）

Agent 能主动搜索数周前的历史对话，不再需要你每次手动交接上下文。

③ 多平台网关（Messaging Gateway）

Hermes 作为常驻服务运行在你的服务器或 VPS 上，你可以从 Telegram、Discord、Slack、WhatsApp 等平台随时发消息控制它——不需要开着终端，手机上就能操控 Agent 执行任务、查看进度、接收通知。

Hermes Agent vs Claude Code：不是竞争，是互补

这是最常见的误解。两者解决的是完全不同的问题：

| 维度 | Claude Code | Hermes Agent |
| --- | --- | --- |
| 核心定位 | 专业编码工具，深度理解代码库 | 持久化自主 Agent，长期积累记忆和技能 |
| 生命周期 | 会话式，用完即止 | 常驻守护进程，持续运行 |
| 记忆机制 | 手动维护 CLAUDE.md / AGENTS.md | 自动三层持久记忆，无需手动维护 |
| 编码能力 | 同类最强，深度代码理解和重构 | 通用能力，编码不是强项 |
| 访问方式 | 终端 + IDE | 终端 + Telegram/Discord/Slack 等 15+ 平台 |
| 模型 | 仅 Claude | 200+ 模型自由切换 |
| 开源 | 否（Anthropic 闭源） | 是（MIT 协议） |
| 适合场景 | 专注编码任务、在 IDE 中工作 | 需要离线调度、跨平台访问、长期记忆积累 |

▶ 最佳组合用法

Hermes 做大脑和调度：感知任务、维护长期记忆、定时触发、跨平台通信。Claude Code 做执行引擎：Hermes 可以把繁重的编码任务委托给 Claude Code 作为子 Agent 执行，完成后把结果折叠回自己的记忆库。这是 2026 年最推荐的重度编码用户工作流。

什么情况下应该考虑 Hermes Agent？

| 场景 | 推荐工具 | 原因 |
| --- | --- | --- |
| 专注写代码、调试、重构，在终端/IDE 工作 | Claude Code | 深度代码理解，同类最强 |
| 需要 Agent 记住你的项目约定、偏好，不想每次重复交代 | Hermes Agent | 自动持久记忆，越用越懂你 |
| 需要定时任务，如每天早上汇总新闻/代码变更 | Hermes Agent | 内置自然语言 Cron 调度 |
| 需要在手机/Telegram 上控制 Agent 执行任务 | Hermes Agent | 多平台网关，随时可达 |
| 预算有限，想用更便宜的模型 | Hermes Agent | BYOK，可接入 OpenRouter 廉价模型 |
| 重度编码 + 长期积累双需求 | Claude Code + Hermes 组合 | Hermes 调度，Claude Code 执行 |

与本指南的关系：下一步学什么？

本指南（Harness Engineering）教你从零手工搭建 Agent 可靠运行的工程框架——这是理解 AI Agent 工程化的基础，无论你最终用什么工具，这套思维方式都适用。

Hermes Agent 是这套思想的一个产品化实现。如果你读完本指南后想进一步探索「把 Harness 机制内置化」的方向，Hermes Agent 是目前最值得深入研究的开源项目。

📘 下一本指南：《Hermes Agent 完全新手指南》 — 即将发布，扫描封底二维码关注「程序员康健」第一时间获取。

| 资源 | 链接 |
| --- | --- |
| Hermes Agent GitHub 仓库 | github.com/NousResearch/hermes-agent |
| Hermes Agent 官方文档 | hermes-agent.nousresearch.com/docs |
| Harness Engineering 学习资源 | walkinglabs.github.io/learn-harness-engineering/zh/ |
| Anthropic Engineering Blog | anthropic.com/engineering |

关注「程序员康健」，获取更多 AI 编程实战干货

持续输出 AI 工具实战干货 · 帮助程序员用好 AI 第三杠杆

| 📱 公众号  程序员AI破局指南  深度长文 · AI 工具评测 · 实战案例  ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  ↑ 扫码关注公众号 | 🎬 视频号  程序员康健 · 视频号  Claude Code 实战 · AI 工具深度测评  ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)  ↑ 扫码关注视频号 |
| --- | --- |

本文基于 Anthropic Engineering Blog 及开源资料整理

@程序员康健

---

📚 相关阅读

- [oh-my-claudecode 深度实战：3w星神级插件—5 种模式 + 19 Agent，把 AI 编程提效 2-5 倍](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487747&idx=1&sn=759022d7a049440dac0f29edca04e2bc&scene=21#wechat_redirect)
- [Hermes Agent 完全新手指南：AI界最快破10万星的开源项目](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487693&idx=1&sn=8a9ad0fdf0f219ccba5beaa716d39e96&scene=21#wechat_redirect)
- [OpenAI Codex 完全新手指南：Codex 凭什么和 Claude Code 抢饭碗？](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487684&idx=1&sn=8526ad23259fcccde5483bcd41677ebc&scene=21#wechat_redirect)
- [Ollama 完全新手指南：一行命令实现 token 自由](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487669&idx=1&sn=2da25b6d78e33972dff158ccd0e5a73d&scene=21#wechat_redirect)
- [ReactFlow完全入门指南：从零构建 AI 工作流编辑器](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487646&idx=1&sn=6abf022e43a3251ebbb45a8249ec5433&scene=21#wechat_redirect)
- [微信小程序开发完全新手指南：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487627&idx=1&sn=27307061cf0a25f88ed02b8f902e93bc&scene=21#wechat_redirect)
- [Superpowers 完全指南：用它少返工80%](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487617&idx=1&sn=49fee04bf4d412a7c444d0ea4f750fe4&scene=21#wechat_redirect)
- [OpenSpec 完全新手指南：5分钟上手规范驱动开发](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487610&idx=1&sn=d609ea6bc83f3832886b6062eb6c2b19&scene=21#wechat_redirect)
- [Skills 完全新手指南(2026版)：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487596&idx=1&sn=cc25377c79e2e19c230894be6793973c&scene=21#wechat_redirect)
- [群晖完全新手指南—家里装一台 NAS，从此告别百度网盘和移动硬盘](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487555&idx=1&sn=ab09a5b43c73161f1bb82ff3660e3a4b&scene=21#wechat_redirect)
- [GitHub Copilot 完全指南：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487536&idx=1&sn=24042c775a66b237577e23cc57ebe001&scene=21#wechat_redirect)
- [Cursor深度使用指南：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487483&idx=1&sn=d6ab0a602c4bf67a7aebd331e8b8a7eb&scene=21#wechat_redirect)
- [Claude Code 完全新手指南（2026 版）：从入门到精通](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487467&idx=1&sn=816295fe691f3622449d2ed3966f7f85&scene=21#wechat_redirect)
- [全网最详细的OpenClaw完全新手指南(中文保姆级教程)](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487459&idx=1&sn=ad1d429cddc9f9f0ff206246b65f22d5&scene=21#wechat_redirect)
- [一天烧掉一个亿 Token？程序员的 AI 账单，正在惩罚「偷懒的人」](https://mp.weixin.qq.com/s?__biz=MzU2MDk3NzU0NA==&mid=2247487442&idx=1&sn=523bf616b7f8b154481f3c819b22485b&scene=21#wechat_redirect)

