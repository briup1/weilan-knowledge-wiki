---
title: "万字讲透Agent Harness的十二大模块：2026 年 AI 工程化最核心的基础设施"
source: "https://zhuanlan.zhihu.com/p/2029220210800883392"
author:
  - "[[时光的沙盒已识乾坤大，犹怜草木青。]]"
published:
created: 2026-05-08
description: "当模型不再是瓶颈，Harness 成为了决定性的战场，从 Anthropic、OpenAI、LangChain 到 Stripe 的实战全解析 引言：一场正在发生的工程范式转移2026 年春天，AI 工程圈被一个看似生僻的词汇点燃了。\" Agent Har…"
tags:
  - "clippings"
---
9 人赞同了该文章

> 当模型不再是瓶颈，Harness 成为了决定性的战场，从 Anthropic、OpenAI、 [LangChain](https://zhida.zhihu.com/search?content_id=273382113&content_type=Article&match_order=1&q=LangChain&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzgzOTIxMTksInEiOiJMYW5nQ2hhaW4iLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNzMzODIxMTMsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.izJxeHJb9Sfz9A7Mx5JqIY6V8wJ2OelDKTK-5LGfrIg&zhida_source=entity) 到 Stripe 的实战全解析

---

## 引言：一场正在发生的工程范式转移

2026 年春天，AI 工程圈被一个看似生僻的词汇点燃了。" **Agent Harness** "（ **智能体驾驭系统** ），这个在 2026 年初才被正式命名的概念，在短短几个月内从学术预印本走进了 OpenAI、Stripe、LangChain 的生产系统，成为整个社区最热门的技术议题。

这场讨论的导火索是一组令人震撼的数字：LangChain 团队在 TerminalBench 2.0 基准测试中， **保持底层模型和权重完全不变，仅仅调整了包裹在模型之外的基础设施** ，就将排名从 30 名开外跃升至第 5 名，通过率从 52.8% 提升到 66.5%。而 Stanford 和 MIT 的研究者更进了一步，他们让 LLM 自动优化自身的 Harness，达到了 76.4% 的通过率，超越了所有人工设计的方案。

几乎在同一时间，OpenAI 的 Frontier 团队公布了一项更为激进的实验： **3 名工程师，5 个月时间，零行人工编写的代码** ，完全由 Codex Agent 自主构建和交付了一个超过 100 万行代码的生产级应用。Stripe 的"Minions"项目则证明这不是个例——每周有超过 1,300 个完全由 AI 生成的 Pull Request 被合并到生产代码库中，这些代码处理着超过万亿美元的年支付流水。

这些案例背后指向同一个核心发现： **当模型能力跨过某个阈值后，限制因素不再是模型本身，而是包裹在模型之外的那层基础设施。** 这层基础设施，就是 Agent Harness。

本文将基于 Akshay Pachaar 的深度技术分析，结合 Anthropic、OpenAI、LangChain、Stripe 等一线团队的最新实践，以及学术界的前沿研究，对 Agent Harness 进行一次全方位的深度解剖。我们将探讨：Harness 的本质是什么？它由哪些核心组件构成？主流框架如何实现它？生产级系统面临哪些关键设计决策？以及社区正在激烈争论的"Harness 厚度"问题——这或许是 2026 年 AI 工程领域最重要的架构抉择。

---

## 一、什么是 Agent Harness：从"裸模型"到"能干活的生产力"

### 1.1 核心定义：模型之外的"一切"

Agent Harness 的概念最早在 2023 年 Beren Millidge 的经典论文《Scaffolded LLMs as Natural Language Computers》中有了雏形，但直到 2026 年初才被 OpenAI、Anthropic 和 LangChain 同时正式命名和采用。

用最简洁的话来概括，Harness 就是 **大模型之外的全部工程化基础设施** 。LangChain 工程师 Vivek Trivedy 给出了一个已经成为社区共识的公式：

> "If you're not the model, you're the harness."（如果你不是模型，你就是 Harness。）

这句话的份量在于，它重新定义了 AI Agent 开发的焦点。从系统提示词、工具调用到状态管理、安全沙箱，所有模型之外的代码、配置与执行逻辑，都属于 Harness 的范畴。

Anthropic 的 [Claude Code](https://zhida.zhihu.com/search?content_id=273382113&content_type=Article&match_order=1&q=Claude+Code&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzgzOTIxMTksInEiOiJDbGF1ZGUgQ29kZSIsInpoaWRhX3NvdXJjZSI6ImVudGl0eSIsImNvbnRlbnRfaWQiOjI3MzM4MjExMywiY29udGVudF90eXBlIjoiQXJ0aWNsZSIsIm1hdGNoX29yZGVyIjoxLCJ6ZF90b2tlbiI6bnVsbH0.l56i2QLRNK_XdvX43w6j4J0PqLw9X62DStpRBRlFx8A&zhida_source=entity) 文档对此表述得更为直接：Claude Code SDK 就是"the agent harness that powers Claude Code"。OpenAI 的 Codex 团队也使用同样的框架，明确将"agent"和"harness"两个术语等同起来，用来指代让 LLM 发挥作用的 **非模型基础设施** 。

![](https://picx.zhimg.com/v2-34697578aff94c5ecef2211d449dfea7_1440w.jpg)

### 1.2 脚手架隐喻：从建筑工地的启示

理解 Harness 的最佳隐喻来自建筑行业的 **脚手架** （Scaffolding）。

Construction scaffolding 是临时的基础设施，它让工人（LLM）能够到达原本无法触及的高度。它本身不做建设，但没有它，工人就无法到达上层楼层。最关键的一点是： **脚手架在建筑完工时会被拆除。**

这个隐喻精确地描述了 Harness 的本质特征。一个原始的 LLM 就像是一颗强大的大脑，但没有眼睛（无法感知环境）、没有双手（无法执行操作）、没有记忆（无法保持状态）、没有检查机制（无法验证自己的工作）。Harness 就是给这颗大脑装上感官系统、执行机构、记忆系统和质量控制的完整操作系统。

Beren Millidge 在 2023 年的论文中将这个类比推向了更精确的计算机架构层面： **"我们重新发明了冯·诺依曼架构"** ——原始 LLM 是 CPU，上下文窗口是 RAM（快速但容量有限），外部数据库是磁盘存储（容量大但访问慢），工具集成是设备驱动程序，而 Harness 就是操作系统。

### 1.3 三个工程层次：从 Prompt Engineering 到 Harness Engineering

Harness 概念的正式化标志着 AI 工程领域经历了三个层次的演进：

**第一层：Prompt Engineering（2022-2024）** ——关注如何与模型对话，即"怎么说"。这是最直接的交互优化层，通过精心设计提示词来引导模型产生更好的输出。

**第二层：Context Engineering（2025）** ——关注模型能看到什么信息，即"看什么"。工程师开始系统地管理记忆、持久化和状态，为非技术用户则意味着给 AI 提供真正有用的背景信息。

**第三层：Harness Engineering（2026）** ——关注围绕模型的完整系统，即"怎么控"。这是当前的最高层次，涵盖了从 Prompt Construction 到 Error Handling、从 Verification Loops 到 Subagent Orchestration 的全部基础设施设计。

每一层并没有取代前一层，而是在其上构建。Prompt 仍在 Harness 之内发挥作用，Context 管理仍是 Harness 的核心组件，但 Harness Engineering 将这些元素整合到了一个统一的系统框架中。

---

## 二、生产级 Harness 的 12 大核心组件

综合 Anthropic、OpenAI、LangChain 以及更广泛的实践者社区的研究，一个生产级的 Agent Harness 包含 12 个独立组件。这些组件不是孤立存在的——它们在编排循环的驱动下协同工作，将模型的原始能力转化为可靠的生产力。让我们逐一深入解析每个组件的内部机制、设计哲学和生产实践。

| 模块 | 关键点 | 与记忆/上下文的关系 |
| --- | --- | --- |
| 编排循环 | [ReAct](https://zhida.zhihu.com/search?content_id=273382113&content_type=Article&match_order=1&q=ReAct&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzgzOTIxMTksInEiOiJSZUFjdCIsInpoaWRhX3NvdXJjZSI6ImVudGl0eSIsImNvbnRlbnRfaWQiOjI3MzM4MjExMywiY29udGVudF90eXBlIjoiQXJ0aWNsZSIsIm1hdGNoX29yZGVyIjoxLCJ6ZF90b2tlbiI6bnVsbH0.037MG1R4IXFcmSgXujPjq89u_uroQS7VIn6MGgnRXHA&zhida_source=entity) / TAO / “笨循环” | 决定何时读取/写入记忆、何时做 JIT/Compaction |
| 工具 | schema / 沙箱 / 结果格式化 | 工具结果如何进入短期记忆；工具本身也可以是“记忆读写” |
| 记忆 | 短期/长期/语义/情景/程序 | 直接决定“Agent 记住什么” |
| 上下文管理 | 压缩、笔记、JIT、子智能体 | 决定“哪些记忆进入当前上下文” |
| 提示组装 | 系统提示 + 工具定义 + 历史 + 当前 query | 决定“模型此刻看到的世界” |
| 工具调用与结构化输出 | tool\_calls / Pydantic / RetryWithErrorOutputParser | 保证“记忆与工具结果以结构化方式写回” |
| 状态与检查点 | 图/会话/previous\_response\_id/git commits | 记录“记忆与上下文的演化历史” |
| 错误处理 | 瞬时/LLM/用户/意外 | 避免“错误污染记忆” |
| 护栏 | 输入/输出/工具；权限分层 | 防止“不当记忆写入/泄露” |
| 验证与反馈 | 规则/视觉/LLM-as-judge | 检查“记忆驱动的决策是否合理” |
| 子智能体编排 | Fork/Teammate/Worktree/嵌套图 | 让子智能体在局部记忆空间里深度检索 |
| 初始化与环境搭建 | CLAUDE.md/NOTES.md/环境变量 | 为长期记忆提供“起点与结构” |

---

### 2.1 编排循环（The Orchestration Loop）：Agent 的心跳

编排循环是整个 Harness 的心脏。它实现了经典的 Thought-Action-Observation（TAO）循环，也就是社区熟知的 ReAct（Reasoning + Acting）模式。

### 循环的本质：一个 while 循环，以及它背后的一切

机械地理解，编排循环往往就是一个 `while` 循环。但其 **复杂性不在于循环本身，而在于循环所管理的一切** 。一个完整的循环周期包含七个步骤：

**Step 1（Prompt 组装）** ：Harness 构造完整输入——系统提示词 + 工具 schema + 记忆文件 + 对话历史 + 当前用户消息。关键上下文被精心放置在 Prompt 的开头和结尾位置（这是应对"Lost in the Middle"问题的核心策略）。

**Step 2（LLM 推理）** ：组装后的 Prompt 发送到模型 API，模型生成输出 token：文本、工具调用请求，或两者兼有。

**Step 3（输出分类）** ：如果模型输出纯文本且没有工具调用，循环结束。如果请求了工具调用，进入执行阶段。如果请求了 handoff，更新当前 Agent 并重启循环。

**Step 4（工具执行）** ：对每个工具调用，Harness 依次执行：参数验证 → 权限检查 → 沙箱环境执行 → 结果捕获。 **只读操作可以并发执行，变异操作必须串行执行。**

**Step 5（结果打包）** ：工具结果被格式化为 LLM 可读的消息。错误被捕获并作为错误结果返回，让模型能够自我修正。

**Step 6（上下文更新）** ：结果被追加到对话历史。如果接近上下文窗口限制，Harness 触发压缩（compaction）。

**Step 7（循环）** ：回到 Step 1，重复直到满足终止条件。

### "Dumb Loop" 哲学

Anthropic 将 Claude Code 的运行时描述为一个 **"dumb loop"（愚笨的循环）** ——所有智能都活在模型内部，Harness 只负责管理轮次。这种设计哲学体现了 Anthropic 的"薄 Harness"立场：让模型做模型擅长的事（推理），Harness 只提供最低限度的 orchestration。

这听起来简单，但生产环境中的"愚笨"循环需要处理大量复杂情况：工具调用失败怎么办？模型陷入死循环如何检测？上下文窗口满了怎么处理？安全边界被触及时如何响应？网络超时如何重试？这些才是编排循环真正的工程挑战。

### 从 ReAct 到 Ralph Loop：跨越会话边界的连续性

对于简单的问答任务，一个基本的 ReAct 循环已经足够。但对于跨越多个上下文窗口的长时间运行任务，标准的循环会面临一个致命问题： **当上下文窗口耗尽时，之前所有的推理状态和任务进度都会丢失。**

为了解决这个问题，Anthropic 开发了 **"Ralph Loop"** 模式——一种两阶段的长期任务编排范式：

**第一阶段：Initializer Agent（初始化代理）**

- 设置工作环境（init 脚本、进度文件、功能列表）
- 创建初始的 git commit
- 生成 `feature_list.json` ，列出所有需要实现的功能及其测试用例
- 每个功能标注状态："pending"、"in\_progress"、"passing"、"failed"

**第二阶段：Coding Agent（编码代理）**

- 在每个后续会话中，读取 git 日志和进度文件来自我定位
- 选择最高优先级的未完成的 "pending" 功能
- 实现该功能 → 运行测试 → 更新状态为 "passing" 或 "failed"
- 提交 git commit，写摘要
- 3 秒后自动启动下一个会话

**文件系统提供了跨上下文窗口的连续性。** 即使 Coding Agent 的上下文被完全重置，它也能通过读取 `feature_list.json` 和 git log 迅速恢复到之前的工作状态。

社区在此基础上发展出了更复杂的变体。 `ralph-orchestrator` （2,175 stars，Rust 实现）增加了 **背压门控** （Backpressure Gate）——不允许在测试/Lint/类型检查未通过的情况下继续推进，并在 70k token 时发出警告、80k token 时强制轮换上下文。

一个简单的 Ralph Loop 实现只需要一行 bash：

```
while :; do cat PROMPT.md | claude-code --continue; done
```

这行代码的核心思想是： **持续输入相同的提示，让 AI 看到它在文件系统和 Git 历史中的先前工作成果。** 这不是简单的"输出反馈作为输入"，而是通过外部状态（代码、测试结果、提交记录）形成一个自我引用的迭代循环。

---

### 2.2 工具系统（Tools）：Agent 的双手

工具是 Agent 与外部世界交互的"双手"。在 Harness 中，工具不是简单的函数调用，而是一个完整的多层系统。

### 工具的定义与发现

在 Harness 中，每个工具都被定义为一个 **schema** ，包含三个核心元素：

- **name** ：工具的唯一标识符
- **description** ：工具的功能描述——这是模型决定何时使用该工具的唯一依据
- **parameters** ：参数 schema，使用 JSON Schema 定义每个参数的名称、类型、描述和约束

这些 schema 被注入到 LLM 的上下文中，让模型知道有哪些能力可用。现代 LLM 通过 **指令微调** （instruction tuning）学会了理解这些 schema——在训练过程中，模型被微调以识别自身缺乏完成提示所需信息的情况，并输出结构化的工具调用请求。

OpenAI 的 Agents SDK 支持三类工具：

- **函数工具** ：通过 `@function_tool` 装饰器将 Python 函数暴露为工具
- **托管工具** ：平台内置的能力，如 WebSearch、CodeInterpreter、FileSearch
- **MCP 服务器工具** ：通过 Model Context Protocol 连接的远程工具

Claude Code 的工具系统更为庞大。根据泄露的源码分析，Claude Code 包含 **约 40 个离散的工具** ，横跨六大类别：文件操作（read、edit、glob）、搜索（grep）、执行（bash）、网络访问（fetch）、代码智能（codebase analysis）和子 Agent 生成（spawn）。每个工具都有独立的权限门控。

### 沙箱与权限：安全执行的关键

工具执行的安全模型是 Harness 设计中最关键的部分之一。Claude Code 采用了 **操作系统级沙箱** ：

- **Linux** ：使用 `bwrap` （bubblewrap）进行进程隔离
- **macOS** ：使用 `sandbox-exec` 进行沙箱化命令执行
- **权限模型** ：deny-first，每个工具、每个目录都有独立的权限规则

这种设计确保了一个被越狱的模型无法绕过安全检查——因为权限检查发生在 **完全不同的代码路径** 上，与模型的推理过程在架构上是分离的。

Stripe 的 Minions 系统采用了更激进的安全模型： **"牛，而非宠物"（Cattle, not Pets）** 。每个 Agent 实例运行在标准化的 AWS EC2 实例（称为 devbox）上，拥有完整的 shell 权限而无需确认提示。任何错误都只影响一个可丢弃的实例。这种设计依赖于底层基础设施的完全隔离来保障安全。

### 工具过载问题：少即是多

**生产实践揭示了一个反直觉的原则：更多工具通常意味着更差的性能。**

当 Agent 面对过多的工具选择时，会产生三种典型问题：

1. **选择困惑** ：模型在多个相似工具之间反复横跳，浪费时间
2. **冗余调用** ：模型连续调用多个功能重叠的工具
3. **决策疲劳** ：工具数量增加会提高每个决策步骤的错误率

Vercel 从 v0 中移除了 **80%** 的工具，结果性能反而提升。Claude Code 通过懒加载实现了 **95%** 的上下文缩减。Stripe 的 Minions 系统只为每个工作流提供大约 15 个精心选择的工具。

社区的共识是： **当工具数量超过约 10 个存在重叠的工具时，就应该考虑拆分为多个 Agent。** 核心原则是：只暴露当前步骤所需的最小工具集。

---

### 2.3 记忆系统（Memory）：跨越时间尺度的状态保持

记忆是生产级 Agent 与 Demo 级 Agent 的根本分水岭。一个只能在单次对话中保持上下文的 Agent，几乎无法完成任何需要持续学习的复杂任务。

### 三层记忆架构：Claude Code 的工程杰作

Claude Code 实现了一个生产验证的三层记忆层次结构，这个架构在 2025 年的源码泄露事件中被完整揭示：

**第一层：上下文内记忆（In-Context Memory）**

这是当前会话的对话历史，存在于模型的上下文窗口中。它是最快但最脆弱的记忆形式——一旦会话结束或上下文被压缩，这部分记忆就丢失了。

**第二层：外部文件记忆（ `memory.md` 指针索引层）**

这是 Claude Code 记忆系统的核心创新。 `memory.md` 不是一个存储文件，而是一个 **指针索引** ——它只包含指向其他记忆文件的引用，每个引用约 150 个字符。实际的记忆内容存储在独立的域特定文件中：

```
memory/
  project-context.md    # 项目目标和约束
  decisions.md          # 已做的架构决策及其原因
  code-patterns.md      # 代码约定和模式
  user-preferences.md   # 用户的工作偏好
  bugs.md              # 已知的未解决 bug
```

当 Claude Code 需要回忆某件事时，它先读取 `memory.md` 找到正确的指针，然后只加载需要的那部分文件。这保持了加载上下文的最小化和相关性，而不是一次性把所有内容都塞进上下文窗口。

**"自愈合"（Self-Healing）机制** 是这一层的关键特性：当 Claude Code 发现之前的假设有误时，它不仅会在对话中记录更正，还会 **重写相关的记忆文件** ，使更正持久化。这种能力让长期运行的 Agent 能够逐渐建立一个准确的项目特定知识库，使其随着时间推移越来越有效。

**第三层：项目级静态记忆（ `CLAUDE.md` ）**

`CLAUDE.md` 是放在项目目录中的静态配置文件，作为项目的"宪法"。与动态更新的 `memory.md` 不同， `CLAUDE.md` 倾向于更稳定，包含：

- 项目整体架构和目标
- 编码标准和风格偏好
- 禁区文件或目录
- 测试和构建指令
- 每个会话都应该可用的上下文

Claude Code 的内存层次结构实际上有 **8 个优先级层级** （从低到高）：

1. Auto Memory（自动记忆——最低优先级）
2. User-Level Rules（ `~/.claude/rules/*.md` ）
3. User Memory（ `~/.claude/CLAUDE.md` ）
4. Project Rules（`./.claude/rules/*.md` ）
5. Project Memory（`./.claude/CLAUDE.md` 或 `./CLAUDE.md` ）
6. Managed Drop-ins（ `managed-settings.d/` ）
7. Managed Policy（ `/Library/Application Support/ClaudeCode/CLAUDE.md` ）
8. 动态规则注入（ `system-reminder` ，对话中途注入——最高优先级）

这种分层设计让不同来源的指令可以共存而不会相互冲突——高层级的指令会覆盖低层级的冲突指令。

### "不信任自己的记忆"原则

一个看似矛盾但极其关键的设计原则是： **Agent 被要求不信任自己的记忆。**

据泄露的系统提示词，Claude Code 被明确指示："记忆只是提示——在行动前根据实际文件进行验证。" 考虑到模型幻觉率仍在两位数水平，这种"自我怀疑"策略出人意料地实用。

这意味着记忆系统不是替代文件系统查询的缓存，而是 **引导查询方向的启发式工具** 。当 Claude Code 的记忆说"API 密钥存储在 `.env` 文件中"时，它会把这个当作一个线索去验证，而不是直接当作事实来使用。

### 其他框架的记忆方案

不同框架采取了不同的记忆策略：

- **LangGraph** ：使用命名空间组织的 JSON Store，支持跨会话的持久化状态
- **OpenAI** ：支持由 SQLite 或 Redis 支持的 Sessions
- **Letta** ：内置 compaction 的记忆系统，支持滑动窗口 summarization
- **CrewAI** ：在 ChromaDB 中存储提取的离散事实，通过 RAG 召回

---

### 2.4 上下文管理（Context Management）：在噪音中找到信号

**这是许多 Agent 悄无声息失败的地方。**

### 上下文腐烂（Context Rot）：百万 token 窗口也逃不过的陷阱

核心问题是上下文腐烂。Chroma Research 的研究与 Stanford 经典的 "Lost in the Middle" 发现相互印证： **当关键内容落在上下文窗口的中间位置时，模型性能下降超过 30%。**

更令人警醒的是，2025 年 JetBrains 研究团队在 SWE-bench Verified 上的研究对比了两种 summarization 策略在 250 轮 Agent 轨迹上的表现：

- **Observation masking** （观察遮蔽）：用占位符替换旧的环境观察，保留推理和行动
- **LLM summarization** ：用单独的模型压缩历史交互为叙事摘要

两者都将成本降低了 50% 以上。但反直觉的是， **observation masking 经常匹配甚至超越 LLM summarization 的解决率** 。使用 Qwen3-Coder 480B，masking 实现了高出 2.6% 的解决率，同时便宜 52%。原因是 LLM summarization 无意中通过掩盖自然的停止信号将 Agent 轨迹延长了 13-15%。

即使拥有百万 token 的上下文窗口，随着上下文增长也会遭受指令跟随能力的下降。这不是窗口大小的问题，而是 **注意力机制的本质限制** 。

### 五种 Compaction 策略：Claude Code 的精细化解法

根据泄露的源码分析，Claude Code 拥有 **五种不同的上下文压缩策略** ，每种在特定条件下触发：

**1\. Snip（剪枝）**

- 快速剪除旧消息以释放空间
- 速度快但有损，作为第一道防线

**2\. Microcompact（微压缩）**

- 专门针对工具输出
- 一个 5,000 行的文件读取结果会被保存到磁盘，模型看到的是带引用的摘要
- 单个未压缩的工具输出可能吃掉半个上下文窗口，这是 microcompact 的核心价值

**3\. Context Collapse（上下文坍塌）**

- 渐进式压缩旧的对话段落，保持近期上下文清晰
- 仍在 `CONTEXT_COLLAPSE` 功能标志后迭代，有专门的持久化类型

**4\. Autocompact（自动压缩）**

- 在可配置的 token 阈值处进行全对话 summarization
- 用摘要替换旧历史
- Claude Code CLI 在约 **95% 上下文容量** 时自动触发
- 用户也可以通过 `/compact` 命令手动触发

**5\. Reactive Compact（反应式压缩）**

- 紧急制动——当 API 返回 413（payload 过大）时触发
- 激进地压缩所有内容以防止会话崩溃
- 在 `REACTIVE_COMPACT` 功能标志后

什么内容能"存活"过 compression？

- **保留** ：用户请求、关键代码变更、架构决策
- **丢失** ：详细的早期指令、中间工具输出
- **缓解策略** ：将持久规则放在 `CLAUDE.md` 中——它每轮都会被重新注入，不受 compression 影响

### 生产级上下文管理策略矩阵

综合各框架的最佳实践，生产级系统采用了以下策略组合：

| 策略 | 原理 | 适用场景 | 代表实现 |
| --- | --- | --- | --- |
| Compaction | 总结对话历史，用摘要替换原始消息 | 通用压缩，保留高层语义 | Claude Code, Codex CLI |
| Observation Masking | 隐藏旧工具输出，保留工具调用记录 | 工具输出占主导的 workflow | SWE-agent, JetBrains Junie |
| Just-in-time Retrieval | 维护轻量级标识符，按需加载 | 大文件浏览、代码库探索 | Claude Code (grep/glob/head/tail) |
| Tool Result Clearing | 手术式替换旧 tool\_result 为占位符 | 可重新获取的工具输出 | Claude API 1M context |
| Sub-agent Delegation | 子 Agent 广泛探索，只返回浓缩摘要 | 需要深度探索的任务 | Claude Code subagents |

ACON（Agent Context Optimization）研究框架进一步系统化了这个方向，通过 **失败驱动的压缩指南优化** ，在保持 95% 以上准确率的同时，实现了 **26% 到 54%** 的 token 缩减。

---

### 2.5 Prompt 构建（Prompt Construction）：模型实际看到的世界

Prompt 构建是 Harness 中最被低估的组件。它负责在每个步骤组装模型实际看到的输入——这不是一个静态字符串，而是一个 **运行时动态组装的层次化结构** 。

### 从"字符串拼接"到"架构设计"

很多开发者的入门 Agent 将 system prompt 写成单个字符串常量，塞在代码里，想到什么加什么，越写越长。这被称为 \*\*"prompt 的泥球架构"\*\*——和代码世界里的 Big Ball of Mud 如出一辙。

真实的生产级 Agent 系统采用精心设计的多层架构。Claude Code 的源码泄露揭示了一个五层 Prompt 组装模型：

**第一层：Base Personality（基础人格层）** Agent 最核心的身份定义——你是谁？包括名字、角色定位、基本行为准则、沟通风格。这一层极少变化。

```
你是 Claude，由 Anthropic 开发的 AI 助手。
你诚实、有帮助、无害。当你不确定时，你会明确说明。
```

**第二层：Role Instructions（角色指令层）** 根据具体应用场景定义的专业角色。Claude Code 的角色指令包括：你是一个编程助手，你在命令行环境中运行，你的任务是帮助用户完成编码工作。

**第三层：Tool Definitions（工具定义层）** 所有可用工具的 schema 定义。这是动态变化的——根据当前任务的权限级别，某些工具可能被隐藏。

**第四层：Context Injection（上下文注入层）** 运行时动态收集的上下文：git status、 `CLAUDE.md` 内容、记忆文件、环境信息。

**第五层：Dynamic Rules（动态规则层）** 对话中途注入的临时规则，如用户通过 `/` 命令触发的特殊模式。

### OpenAI Codex 的优先级栈

OpenAI 的 Codex 使用了一个严格的优先级栈，值得所有 Harness 设计者参考：

1. **服务器控制的系统消息** （最高优先级）
2. 工具定义
3. 开发者指令
4. 用户指令（级联的 `AGENTS.md` 文件，32 KiB 限制）
5. 对话历史

这个优先级设计体现了重要的安全原则： **服务器控制的指令始终优先于用户级别的指令** ，防止提示注入攻击改变系统的核心行为。 `AGENTS.md` 的 32 KiB 限制则确保了用户自定义指令不会无限制膨胀。

### 关键原则：最小高信号 token 集合

Anthropic 的上下文工程指南将 Prompt 构建的目标表述为： **找到能实现期望结果的最小高信号 token 集合。** 这不是关于"更多信息"，而是关于"正确的信息，在正确的时间"。

Claude Code 的泄露源码显示，其系统提示词组装使用了 **条件逻辑** ——根据当前模式（如 Thinking 模式、安全模式）、工具可用性和用户上下文动态调整。约 50 个工具的定义在多个上下文层中被管理，通过 `filterInjectedMemoryFiles()` 进行安全过滤。

---

### 2.6 输出解析（Output Parsing）：从自由文本到结构化行动

输出解析是 Harness 与模型之间的关键接口。这个领域经历了从"文本解析"到"原生结构化输出"的重大演进。

### 三代输出解析技术

**第一代：自由文本解析（2023 早期）** 模型输出自由文本，Harness 通过正则表达式或字符串匹配提取工具调用意图。这种方式脆弱、容易出错，且无法处理复杂参数。

**第二代：Function Calling / Tool Calling（2023 中后期）** 模型通过专门的指令微调学会了输出结构化的 JSON 对象，包含工具名称和参数。Harness 解析这个 JSON 对象并执行相应函数。这是当前的主流方式。

**第三代：Grammar-Constrained Decoding（2024+）** 通过 **语法约束解码** ，在生成时数学上限制 token 概率——如果 schema 规定下一个 token 必须是引号或布尔值，所有不合规的 token 概率被设为零（masked out）。这实现了接近 100% 的 schema 合规率。

OpenAI 的 Structured Outputs 和 Outlines 库都采用这种方式。这不是后处理验证，而是在 **生成过程中强制约束** 。

### Native Tool Calling 的核心机制

现代 Harness 依赖于 **Native Tool Calling** ：模型返回结构化的 `tool_calls` 对象，而非需要解析的自由文本。

完整的工具调用循环如下：

1. **定义工具 schema** ：将工具的名称、描述和参数 schema 与用户消息一起发送
2. **模型阅读提示和 schema** ：当用户说"查一下我的支票账户余额"时，模型选择 `get_balance` 工具
3. **输出结构化 JSON** ： `{"name": "get_balance", "arguments": {"account_type": "checking"}}`
4. **应用程序执行实际的 `get_balance` 函数** ：得到 `{"balance": 4821.50}`
5. **将结果作为 tool result 消息发送回模型**
6. **模型生成自然语言响应** ："您的支票账户余额是 $4,821.50"

Harness 的核心逻辑因此变得非常简单：检查是否有 tool\_calls？如果有，执行它们并继续循环。如果没有，那就是最终答案。

### 结构化输出与工具调用的区别

一个重要的区分是 **Structured Outputs** 与 **Function Calling** 的适用场景：

- **Structured Outputs** ：用于模型直接向用户提供结构化的最终答案（如生成 JSON 报告）。约束解码确保 schema 合规。
- **Function Calling** ：用于模型需要与外部系统交互的多轮对话流程。模型暂停文本生成，选择工具，等待执行结果后继续。

对于需要同时输出文本和工具调用的场景，OpenAI 和 LangChain 都支持通过 Pydantic 模型进行 schema 约束的响应。传统的重试解析器（如 RetryWithErrorOutputParser）在边缘情况下仍然可用，但正逐渐被原生工具调用取代。

---

### 2.7 状态管理（State Management）：让任务可恢复、可调试

状态管理决定了 Agent 能否在长时间运行中保持连续性，以及能否在失败后恢复。这是一个从"脚本"到"应用"的分水岭。

### LangGraph：图节点的状态机

LangGraph 将状态管理建模为 **流经图节点的类型化字典** ：

- **状态（State）** ：一个 TypedDict，定义了 workflow 中所有可能的状态字段
- **Reducers** ：函数，定义如何合并状态更新（如追加消息 vs. 替换消息）
- **Checkpointing** ：检查点发生在 **super-step 边界** （即一轮完整的 LLM 调用 + 工具执行之后）

这带来了两个强大的能力：

**时间旅行调试（Time-Travel Debugging）** ：因为每个 super-step 都被保存，你可以查询线程历史，精确看到五步之前的状态是什么样的。你甚至可以 **分叉历史** ——从某个历史检查点重新开始执行，使用不同的输入或修改后的状态，来测试"如果……会怎样"。

**中断后恢复** ：如果 Agent 在第十步因为网络中断而停止，下一次启动时可以从第十步的检查点恢复，而不是从零开始。

### OpenAI 的四种状态策略

OpenAI 提供了四种 **互斥** 的状态持久化策略：

1. **应用内存（Application Memory）** ：在应用进程中维护状态，最简单但无法跨进程恢复
2. **SDK Sessions** ：由 SDK 自动管理的会话状态
3. **服务端 Conversations API** ：使用 OpenAI 服务端存储对话历史
4. **`previous_response_id` 链式调用** ：轻量级的状态传递，每次调用引用前一次的 response ID

### Claude Code：Git 作为状态机

Claude Code 采用了截然不同的哲学—— **Git 提交作为检查点，进度文件作为结构化草稿板** ：

- 每次阶段性边界（完成一个功能、通过一组测试）产生一个 **git commit**
- 进度文件（如 `progress.md` 、 `feature_list.json` ）记录当前任务状态
- 如果第三阶段出了问题，回滚目标是干净的第二阶段提交

这种设计巧妙之处在于： **它利用了开发者已经熟悉的版本控制系统** ，不需要引入新的状态管理基础设施。Git 的不可变提交历史天然提供了状态的可追溯性。

Stripe 的 Minions 系统在此基础上更进一步，将 **devbox（AWS EC2 实例）作为状态容器** ——每个实例预加载完整源代码树、预热的 Bazel 缓存和类型检查结果，确保 Agent 从已知良好的状态开始工作。

---

### 2.8 错误处理（Error Handling）：在必然的错误中生存

错误处理是 Harness 中最容易被忽视但最关键的组件之一。

### 错误累积的数学

一个令人警醒的数学事实：\*\*一个 10 步的流程，即使每步有 99% 的成功率，端到端成功率也只有约 90.4%\*\*（0.99^10 ≈ 0.904）。如果是 50 步的流程，端到端成功率暴跌至 \*\*60.5%\*\*。

这意味着在长时间运行的 Agent 工作流中，错误不是"偶发事件"，而是"必然事件"。Harness 的设计必须假设错误会发生，并系统性地处理它们。

### LangGraph 的四级错误分类

LangGraph 区分了四种错误类型，每种都有针对性的处理策略：

**1\. 瞬态错误（Transient Errors）**

- 原因：网络超时、API 限流、临时服务不可用
- 处理： **指数退避重试** （exponential backoff）
- 典型参数：初始等待 1 秒，每次翻倍，最多 3-5 次重试

**2\. LLM 可恢复错误（LLM-Recoverable Errors）**

- 原因：工具参数格式错误、工具返回非预期结果、权限不足
- 处理：将错误信息包装为 `ToolMessage` 返回给模型， **让模型自行调整**
- 这是 Agent 自我修正能力的核心——模型看到错误后可以在下一轮尝试不同的方法

**3\. 用户可修复错误（User-Fixable Errors）**

- 原因：需要人工判断的问题（如"这段代码有多个重构方案，你选哪个？"）
- 处理： **中断循环并请求人工输入** （Human-in-the-Loop）

**4\. 意外错误（Unexpected Errors）**

- 原因：代码 bug、配置错误、不可恢复的系统故障
- 处理： **冒泡到上层** ，记录详细的调试信息，终止当前任务

### Stripe 的错误处理实践

Stripe 的生产级 Harness 将重试上限 **严格设为两次** 。Anthropic 则在工具处理器内部捕获所有失败，将它们作为错误结果返回给模型，保持循环的持续运行。

一个关键的设计决策是： **永远不要因为单个工具调用的失败而终止整个循环。** 相反，将错误包装为模型可理解的格式，让它决定下一步行动——重试、换一种方法、还是放弃这个子任务继续主线。

---

### 2.9 安全防护（Guardrails and Safety）：速度与安全之间的永恒张力

安全防护是 Harness 中"看似简单实则复杂"的典型代表。OpenAI 的 SDK 实现了三个层次的防护体系：

### 三层 Guardrails 架构

**第一层：输入防护（Input Guardrails）**

- 在模型的第一轮运行前执行
- 检测 prompt injection、PII 泄露、越权请求
- 如果触发 tripwire，Agent 在消耗任何模型 token 之前就被 halt
- 支持并行模式（低延迟）和阻塞模式（零浪费 token）

**第二层：工具防护（Tool Guardrails）**

- 在 **每次工具调用** 时执行
- 验证工具参数是否合规（如转账金额是否在限额内）
- 对工具返回结果进行安全检查

**第三层：输出防护（Output Guardrails）**

- 在 Agent 最终输出返回给用户前执行
- 检测幻觉、PII 泄露、不当内容
- 确保输出符合合规要求

### Tripwire 机制

当 guardrail 检测到违规时，触发 **tripwire** ——一个立即 halt Agent 执行的机制。SDK 会抛出特定的异常（ `InputGuardrailTripwireTriggered` 或 `OutputGuardrailTripwireTriggered` ），Harness 捕获这些异常并进行相应处理。

一个典型的输入 guardrail 实现：

```
async def no_pii_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    pii_patterns = ["social security", "credit card", "ssn", "passport number"]
    input_lower = str(input).lower()
    if any(p in input_lower for p in pii_patterns):
        return GuardrailFunctionOutput(
            output_info={"reason": "PII detected"},
            tripwire_triggered=True,  # 触发绊索，halt 执行
        )
    return GuardrailFunctionOutput(output_info={"reason": "clean"}, tripwire_triggered=False)
```

### 权限与推理的架构分离

Anthropic 的安全模型有一个关键原则： **将权限执行与模型推理在架构上分离** 。模型决定"要尝试做什么"，工具系统决定"允许做什么"。

Claude Code 的权限模型分三个阶段：

1. **项目加载时的信任建立** ：首次进入项目时，评估项目的风险等级
2. **每次工具调用前的权限检查** ：通过 `canUseTool()` 拦截每个工具调用
3. **高风险操作的显式用户确认** ：文件删除、网络请求、代码执行等操作需要用户确认

Claude Code 独立控制约 **40 个离散的工具能力** ，每个都有独立的权限门控。这提供了极高的权限粒度——例如，可以允许读取 `.env` 文件但禁止写入，允许运行测试但禁止执行任意 shell 命令。

Stripe 采用了完全不同的安全哲学： **"宽容模式"** ——在完全隔离的环境中给予 Agent 最大自由。这种设计在速度上有巨大优势，但依赖于底层基础设施的完全隔离来保障安全。

---

### 2.10 验证循环（Verification Loops）：从玩具到生产的分水岭

**验证循环是将 Demo 级 Agent 与生产级 Agent 区分开的关键。** 一个没有验证机制的 Agent 就像一个没有质量控制的工厂——它可以大量产出，但产出物的质量无法保证。

### 三种验证方法

Anthropic 推荐了三种互补的验证方法：

**1\. 基于规则的反馈（Rules-Based Feedback）**

- 测试套件（unit tests、integration tests）
- 静态分析（Linter、type checker、formatter）
- 提供\*\*确定性的"地面真相"\*\*——通过就是通过，失败就是失败
- 这是最可靠但也最有限的验证形式——只能检测已知规则内的问题

**2\. 视觉反馈（Visual Feedback）**

- 通过 Playwright 或 Puppeteer 截图验证 UI 任务
- 比较实际渲染结果与预期设计
- 特别适用于前端开发、移动应用测试

**3\. LLM-as-Judge（模型即裁判）**

- 使用单独的子 Agent 评估主 Agent 的输出质量
- 可以检测语义问题、风格一致性、逻辑连贯性
- 增加延迟和成本，但能发现规则型验证无法捕获的问题

Claude Code 的创造者 Boris Cherny 指出： **给模型一种验证自己工作的方法，可以将质量提高 2 到 3 倍。**

### Guides vs. Sensors：Thoughtworks 的框架

Martin Fowler 的 Thoughtworks 团队从另一个角度框架化了这个问题：将验证分为 **"指南"（Guides）和"传感器"（Sensors）** ：

- **指南（Guides）** ：前馈控制——在行动前引导。例如，给模型明确的编码规范、测试要求、架构约束。
- **传感器（Sensors）** ：反馈控制——在行动后观察。例如，运行测试、检查代码覆盖率、验证输出格式。

两者共同构成将原始 LLM 转化为生产级 Agent 的控制系统。生产级系统通常需要两者结合。

### 自我验证偏差：一个反模式

生产实践中存在一个反模式—— **"自我验证偏差"** 。当 QC Agent 的使命被框架为"验证这 N 个修复是否已应用"时，它倾向于确认而非挑战——就像一个被要求"检查这些文件是否存在"的审计员，而不是被要求"找出这些文件中的问题"的审计员。

Claude Code 的质量控制子 Agent 曾被观察到这种偏差，导致大量 token 浪费在无效的确认循环上。解决方案是 **重新框架验证使命** ——从"验证修复是否已应用"变为"找出修复中的问题"，引入对抗性审查的激励机制。

---

### 2.11 子 Agent 编排（Subagent Orchestration）：并行化的艺术

当任务复杂度超过单个 Agent 的处理能力时，需要子 Agent 编排。这个领域有两种核心哲学： **中心化管理** vs **去中心化协作** 。

### Claude Code 的三种执行模型

Claude Code 支持三种子 Agent 执行模型，每种适用于不同的并行化场景：

**Fork** ：父上下文的字节级精确副本，用于完全独立的并行任务。子 Agent 完成后将结果返回给父 Agent。这是最简单的并行模式。

**Teammate** ：单独的终端面板，通过基于文件的邮箱通信。 teammates 可以直接互相通信，而无需通过主 Agent 路由。这适用于需要协作但不完全独立的任务。

**Worktree** ：每个 Agent 拥有自己的 git worktree，在独立分支上工作。这种模式下，Agent 之间的隔离是最彻底的——各自的代码变更互不干扰，最后通过 git merge 合并。

### OpenAI Agents SDK 的两种编排模式

OpenAI 的 Agents SDK 提供了两种核心的多 Agent 编排模式：

**Handoffs（交接模式）** ：

- 一个分流 Agent（Triage Agent）识别用户需求，将对话 **完全转移** 给专业 Agent
- 专业 Agent 成为当前的活跃 Agent，直接响应用户
- 适用于：专业 Agent 需要拥有对话控制权，使用不同的指令/模型/策略
```
billing_agent = Agent(name="Billing", instructions="Handle billing inquiries.")
refund_agent = Agent(name="Refund", instructions="Handle refund requests.")

triage_agent = Agent(
    name="Triage",
    instructions="Route to the right specialist.",
    handoffs=[billing_agent, refund_agent],
)
```

**Agents-as-Tools（工具模式）** ：

- 管理 Agent 保持对对话的控制权，将专业 Agent 作为工具调用
- 专业 Agent 执行有边界的子任务，将结果返回给管理 Agent
- 适用于：管理 Agent 需要综合多个专家的意见，为最终答案负责
```
summarizer = Agent(name="Summarizer", instructions="Generate concise summaries.")

main_agent = Agent(
    name="Research",
    tools=[summarizer.asTool(toolName="summarize", toolDescription="Summarize text")],
)
```

两种模式可以组合使用：一个分流 Agent handoff 给专业 Agent，该专业 Agent 再调用其他 Agent 作为工具处理更细粒度的子任务。

### Token 经济学：Agent Teams vs. Sub-agents

实际测试表明， **Agent 团队模式在大规模并行任务中通常比子 Agent 模式更省 token** ：

- 在子 Agent 设置中，编排器的上下文窗口会随着每个接收到的结果而增长
- 在团队设置中，每个 Agent 只加载与其当前任务相关的上下文
- 对于 10+ 并行 Agent 产生大量输出的工作流，团队模式可以便宜 **3-5 倍**

---

### 2.12 终止条件（Termination Conditions）：知道何时停下

循环必须在某个时刻终止。生产级 Harness 实现了 **分层的终止条件体系** ：

| 终止条件 | 触发原因 | 处理方式 |
| --- | --- | --- |
| 自然终止 | 模型产生没有 tool\_calls 的响应 | 返回最终答案 |
| 轮次限制 | 超过 max\_turns 阈值 | 抛出 MaxTurnsExceeded 异常 |
| Token 预算耗尽 | 达到预设的 token 上限 | 终止并返回当前最佳结果 |
| Guardrail Tripwire | 输入/输出/工具防护触发 | 抛出 GuardrailTripwireTriggered 异常 |
| 用户中断 | 用户按下 Ctrl+C 或发送停止信号 | 优雅终止，保存当前状态 |
| 安全拒绝 | 模型返回安全拒绝响应 | 终止并返回拒绝信息 |

### 完成问题的挑战

一个看似简单但实际困难的问题是： **Agent 怎么知道什么时候"做完了"？**

这是 Agentic AI 中著名的 **"完成问题"（Completion Problem）** 。系统优化为自主执行的能力，却从根本上缺乏清晰的"完成"原语。Claude Code 曾被观察到在核心任务完成后，继续消耗数千 token 重构功能正常的代码，只因为提示中提到了"clean architecture"。

Ralph Loop 通过添加 **退出门控** （exit gates）、 **断路器** （circuit breakers）和 **提示驱动的完成标准** 来解决这个问题。但工具只是部分解决方案——在实践中， **提示的特异性是决定因素** ：一个精确的提示可以带来 3 轮干净完成，而一个模糊的提示可能导致 20 轮螺旋。

### 跨会话终止：Ralph Loop 的优雅解法

对于长时间运行任务，终止不是"停止工作"，而是"将状态安全地传递给下一个会话"。Ralph Loop 的优雅之处在于： **每个会话自然终止（上下文耗尽或任务阶段完成），而循环自动启动下一个会话。**

状态传递通过以下机制实现：

| 传递机制 | 用途 | 来源 |
| --- | --- | --- |
| feature\_list.json | 功能列表和状态管理 | Anthropic 官方 |
| progress.md / research.md / plan.md | 各阶段的产物 | HumanLayer |
| ROTATION-HANDOVER.md | 上下文轮换时的结构化交接 | VNX system |
| Git commit messages | diff 的意图和下一步行动 | 所有模式 |

这种设计让 Agent 可以无限期地持续工作——每次会话都是一次"新鲜的开始"，但通过文件系统保持了完整的连续性。一个简单的任务可能只需 1-2 轮。一个复杂的重构任务可以跨多个会话串联数十个工具调用。

---

## 三、主流框架的 Harness 实现对比

### 3.1 Anthropic Claude Code：薄 Harness 哲学的极致

Claude Code 是"薄 Harness"立场的代表。它的架构核心是 `query()` 函数——创建一个 Agent 循环并返回流式消息的异步迭代器。

Claude Code 的循环遵循 **Gather-Act-Verify** 周期：收集上下文（搜索文件、阅读代码）、采取行动（编辑文件、运行命令）、验证结果（运行测试、检查输出），然后重复。

关键架构决策包括：

- **将权限执行与模型推理在架构上分离**
- **显式的上下文管理** ：压缩、截断限制、工具搜索、磁盘持久化
- **为会话连续性设计** ：快照、可撤销的文件更改、CLAUDE.md 作为持久锚点
- **Git 提交作为检查点，进度文件作为结构化草稿板**

Claude Code 的工具系统包含约 40 个权限门控工具（社区分析），涵盖文件读写、Shell 执行、Git 操作、Web 获取、Notebook 编辑和 MCP 工具调用。每个工具都独立沙箱化，每个工具调用都经过权限检查。

### 3.2 OpenAI Agents SDK：代码优先的 Harness 设计

OpenAI 的 Agents SDK 通过 `Runner` 类实现 Harness，支持三种模式：异步、同步和流式。SDK 是\*\*"代码优先"的\*\*——工作流逻辑用原生 Python 表达，而非图 DSL。

Codex 的 Harness 在此基础上扩展为三层架构：

- **Codex Core** ：Agent 代码 + 运行时
- **App Server** ：双向 JSON-RPC API
- **客户端界面** ：CLI、VS Code、Web App

所有界面共享同一个 Harness，这解释了为什么"Codex 模型在 Codex 界面上的表现优于通用聊天窗口"。

OpenAI 的 Frontier 团队从他们的百万行代码实验中学到了一个核心教训： **早期进展比预期慢，不是因为 Codex 能力不足，而是因为环境定义不充分。** 这个观察指向一个关键洞察：一旦模型跨过能力阈值，限制因素就是 Harness 如何有效地将能力引导向生产性行动。

### 3.3 LangGraph：显式状态图的哲学

LangGraph 将 Harness 建模为 **显式状态图** 。两个节点（ `llm_call` 和 `tool_node` ）通过条件边连接：如果存在工具调用，路由到 `tool_node` ；如果不存在，路由到 `END` 。

LangGraph 从 LangChain 的 AgentExecutor 演进而来，后者在 v0.2 中被弃用，因为它难以扩展且缺乏多 Agent 支持。LangChain 的 Deep Agents 明确使用了"Agent Harness"这个术语：内置工具、规划（ `write_todos` 工具）、用于上下文管理的文件系统、子 Agent 生成和持久化记忆。

LangGraph 的设计哲学是"厚 Harness"——通过显式控制来确保可靠性和可审计性。这与 Anthropic 的"薄 Harness"形成了鲜明对比。

### 3.4 CrewAI：角色驱动的多 Agent 架构

CrewAI 实现了基于角色的多 Agent 架构：Agent（围绕 LLM 的 Harness，由角色、目标、背景故事和工具定义）、Task（工作单元）和 Crew（Agent 集合）。

CrewAI 的 Flows 层增加了"确定性骨架，在重要处有智能"——管理路由和验证，而 Crew 处理自主协作。这种混合方法在确定性和自主性之间寻求平衡。

### 3.5 AutoGen：对话驱动的编排

AutoGen（正在演化为 Microsoft Agent Framework）开创了对话驱动的编排。其三层架构（Core、AgentChat、Extensions）支持五种编排模式：顺序、并发（扇出/扇入）、群聊、交接和"magentic"（一个管理 Agent 维护动态任务分类账协调专家）。

---

## 四、生产级案例深度研究

### 4.1 OpenAI Symphony：零人工代码的百万行实验

2025 年 8 月，OpenAI 的一个三人团队开始了一项极端实验： **他们不写一行应用代码，全部由 Codex Agent 完成。** 五个月后，代码库积累了约 100 万行代码和 1,500 个合并的 Pull Request。团队估计，如果手工完成，需要十倍的时间。

这个实验产生的核心方法论就是 **Harness Engineering** 。2026 年 3 月，OpenAI 将参考实现作为开源项目发布，命名为 **Symphony** 。

Symphony 解决的核心问题不是"如何让 Agent 更聪明"，而是 **当需要同时处理的问题数量增长到 5 个、10 个或更多时，开发者的注意力成为瓶颈** 。Symphony 的范式转换是："开发者将工作交给 Agent" → "问题追踪器自动召唤 Agent"。

实验中的一个关键发现是 **构建时间的重要性** 。团队近乎偏执地追求快速构建循环——一分钟成为内循环的上限。当构建时间超过这个阈值时，Agent 的生产力急剧下降。团队反复改造构建系统以保持 Agent 的高效。

Ryan Lopopolo（OpenAI Frontier 团队负责人）将这个转变描述为：当 Agent 失败时，团队不再想"让我们试试不同的提示"或告诉它"再努力一下"，而是问： **"缺少什么具体能力、什么类别的上下文、或什么层次的结构？"**

### 4.2 Stripe Minions：每周 1,300 个 PR 的企业级 Harness

如果说 OpenAI 的实验是"从零开始"的理想场景，那么 Stripe 的 Minions 则证明了 Harness 工程在 **大规模、关键任务的现有代码库** 中的可行性。

Stripe 每周合并超过 1,300 个包含零人工代码的 Pull Request。这些 PR 由"Minions"——Stripe 的内部编码 Agent——完全无人值守地运行。其 Harness 架构基于 Goose（Block 的开源编码 Agent）的分支，但针对完全无人值守操作进行了深度改造。

Minions 的核心架构是一个五层管道：

1. **调用** ：工程师通过 Slack（主要路径）、CLI、Web 界面或自动化系统触发
2. **Devbox** ：标准化的 AWS EC2 实例，预加载了 Stripe 的完整源代码树、预热的 Bazel 和类型检查缓存
3. **Agent 核心** ：Goose 的分支，移除了所有为人类设计的元素——中断性、确认对话框、人工触发命令
4. **蓝图（Blueprints）** ：混合工作流，交织确定性代码节点和自由流动的 Agent 子任务
5. **CI 循环** ：本地 Lint（<5 秒）→ 最多 2 轮 CI → 自动应用修复

Stripe 的设计哲学是 **"牛，而非宠物"** ——每个 devbox 都是相同且一次性的。Agent 获得完整的 shell 权限而无需确认提示，任何错误都只影响一个可丢弃的实例。

**最关键的设计决策是蓝图架构** 。蓝图是混合工作流，将确定性节点（固定、可预测的操作，如运行测试或格式化代码）与 Agent 节点（AI 驱动的推理和生成）交织在一起。这种混合方法让 AI 处理它擅长的事情（推理、编写），而可验证的操作通过确定性代码运行。

### 4.3 LangChain Deep Agents：Harness 优化的标杆案例

LangChain 的 Deep Agents 项目提供了 Harness 优化的标杆案例。团队使用同一个模型（gpt-5.2-codex），通过以下 Harness 层面的改进，将 TerminalBench 2.0 的通过率从 52.8% 提升到 66.5%：

- **构建自验证机制** ：引导 Agent 通过测试验证代码
- **环境上下文注入** ：帮助 Agent 更好地理解工作环境
- **检测并打断循环失败** ：防止 Agent 在死胡同中无限循环
- **采用"推理三明治"策略** ：优化推理预算分配

团队强调 **追踪分析（Tracing）** 的巨大价值。使用 LangSmith 大规模总结 Agent 的失败模式，然后针对性地优化 Harness。

---

## 五、社区大辩论：Harness 的厚度问题

### 5.1 两派对立："模型派" vs "Harness 派"

Agent Harness 概念的爆发在社区中引发了激烈的争论，迅速分化为两个阵营。

\*\*"模型派"\*\*认为 Harness 被过度炒作了。这一派最有力的代言人，出人意料地来自 Anthropic 自家。

Claude Code 的创造者 Boris Cherny 在 AI 工程圈极具影响力的播客社区讨论中表态：

> **"Claude Code 的所有秘诀都在模型本身，它是模型上最薄的一层包装，我们不可能做得比这更精简了。"**

OpenAI 的 Noam Brown 更直接：在推理模型上搭脚手架，很多时候都是添乱；模型的推理能力一直在飞速进步，你今天费半天劲搭的编排逻辑，过几个月新模型出来，就成了绊脚石。

METR（专门做 AI 能力评估的机构）的严格对比也支持这一派： **Claude Code 和 Codex 并没有显著赢过一个基础脚手架。**

"Harness 派"则认为 Harness 是决定性的差异化因素。

LangChain 的 Jerry Liu 表示： **"模型驾驭着一切——AI 价值的最大障碍是用户自己进行上下文和工作流工程的能力。"** LlamaIndex 团队的经历表明，即使有强大的模型，缺乏良好 Harness 的系统仍然难以产生可靠的价值。

TerminalBench 2.0 的数据是最有力的证据：同一个模型，不同的 Harness，排名相差 25 位。

### 5.2 脚手架原则：为移除而构建

Latent Space 社区对这个辩论给出了精妙的调和框架： **脚手架原则** ——为移除而构建。

建筑业脚手架的核心特征是临时的。工人在建设期间依赖它，但建筑完成后必须拆除。同样，Harness 的设计目标应该是： **随着模型能力的提升，Harness 的复杂性应该降低。**

实践中已经观察到这个模式。AI 初创公司 Manus 在 6 个月内重建了其 Agent 5 次，每次迭代都剥离复杂性——将复杂的工具定义变为简单的 shell 命令，将"管理 Agent"替换为基本交接。同样，Anthropic 随着新模型版本内化那些能力，系统性地从 Claude Code 的 Harness 中删除了规划步骤。

这引出了 **"未来验证测试"（Future-proofing Test）：** 如果替换为更强大的模型后性能提升，且无需增加 Harness 复杂性，那么 Harness 设计是合理的。

### 5.3 关键陷阱：模型-Harness 共进化

然而，辩论双方都需要面对一个复杂的现实： **模型现在正在与特定 Harness 共同训练。**

Claude Code 的模型学会了使用它构建时的确切脚手架进行推理。改变或移除那个脚手架可能导致性能下降——工人是在那个特定的支撑结构上接受训练的。这种 **紧耦合** 创造了微妙的工程挑战：构建设计为可移除的脚手架，但要仔细且与模型改进同步地移除它。

这解释了为什么 Boris Cherny 的"薄 Harness"声明和 LangChain 的"Harness 决定一切"声明可以同时成立——它们描述的是不同共进化阶段的系统。

---

## 六、七个决定 Harness 命运的关键设计决策

每个 Harness 架构师都面临七个关键选择：

### 6.1 单 Agent vs. 多 Agent

Anthropic 和 OpenAI 都建议： **首先最大化单 Agent 的能力。** 多 Agent 系统增加了开销（路由的额外 LLM 调用、交接时的上下文丢失）。只有在工具数量超过约 10 个重叠工具，或存在明确分离的任务领域时，才考虑拆分。

但 Stripe Minions 的实践表明，在高度并行的场景下（如同时处理 5 个独立问题），多 Agent 可以带来数量级的效率提升。

### 6.2 ReAct vs. Plan-and-Execute

ReAct 在每个步骤交错推理和行动（灵活但每步成本较高）。Plan-and-Execute 将规划与执行分离。LLMCompiler 报告称相比顺序 ReAct 有 **3.6 倍的速度提升** 。

选择取决于任务的确定性程度。对于高度不确定的探索性任务，ReAct 的灵活性更有价值。对于结构明确的任务，Plan-and-Execute 的效率优势更明显。

### 6.3 上下文窗口管理策略

五种生产级方法：基于时间的清除、对话总结、观察遮蔽、结构化笔记和子 Agent 委托。

ACON 研究表明，通过优先保留推理痕迹而非原始工具输出，可以实现 26% 到 54% 的 token 缩减，同时保持 95% 以上的准确率。

### 6.4 验证循环设计

计算验证（测试、Linter）提供确定性的"地面真相"。推理验证（LLM-as-Judge）捕获语义问题但增加延迟。

Martin Fowler 的 Thoughtworks 团队将此框架化为 **"指南"（前馈，在行动前引导）vs."传感器"（反馈，在行动后观察）** 。 生产级系统通常需要两者结合。

### 6.5 权限与安全架构

**宽容模式** （快速但风险高，自动批准大多数操作）vs. **限制模式** （安全但缓慢，每次操作都需要批准）。选择取决于部署上下文。

Stripe 的 Minions 采用了一种巧妙的混合：在完全隔离的环境中给予 Agent 最大自由，但在与真实世界交互时保持严格的权限控制。

### 6.6 工具范围策略

**更多工具通常意味着更差的性能。** Vercel 从 v0 中移除了 80% 的工具，结果性能提升。Claude Code 通过懒加载实现了 95% 的上下文缩减。

核心原则：只暴露当前步骤所需的最小工具集。当工具数量超过约 10 个时，考虑拆分为多个专门的 Agent。

### 6.7 Harness 厚度

**多少逻辑应该活在 Harness 中，多少应该留给模型？**

Anthropic 押注薄 Harness 和模型改进。Graph-based 框架（如 LangGraph）押注明式控制。Anthropic 随着新模型版本内化那些能力，定期从 Claude Code 的 Harness 中删除规划步骤。

这或许是 2026 年最重要的架构押注。选择"薄 Harness"意味着你相信模型的进步速度会超过你维护复杂基础设施的能力。选择"厚 Harness"意味着你需要在确定性、可审计性和可靠性上有最大控制权。

---

## 七、实践指南：如何构建你的第一个生产级 Harness

### 7.1 从薄开始，按需增厚

基于社区的最佳实践，我们推荐以下渐进式策略：

**阶段一：最小可行 Harness（MVP）**

- 实现基础的 ReAct 循环
- 定义 3-5 个核心工具
- 添加基础错误处理（重试 + 失败返回模型）
- 实现简单的上下文截断

**阶段二：生产加固**

- 添加原生工具调用支持
- 实现上下文压缩/总结
- 添加输入/输出防护
- 引入记忆系统（CLAUDE.md / MEMORY.md 模式）
- 添加基础验证循环（测试、Linter）

**阶段三：规模化**

- 实现子 Agent 编排
- 添加详细的状态管理和检查点
- 实现多层次的权限控制
- 引入工具懒加载和动态发现
- 添加全面的可观测性（Tracing、Metrics）

### 7.2 关键设计原则

基于 Anthropic、OpenAI、Stripe 的经验，我们总结了以下设计原则：

**1\. 将推理与权限执行分离。** 模型决定"要尝试做什么"。不同的系统决定"允许做什么"。一个被越狱的模型无法绕过安全检查，因为那是完全不同的代码路径。

**2\. 让上下文管理显式化。** 压缩、截断限制、工具搜索、磁盘持久化——这些都是主动管理模型所见内容的机制。大多数业余 Agent 构建将上下文视为无底袋。它不是。

**3\. 为会话连续性设计。** 快照、可撤销的文件更改、CLAUDE.md 作为持久锚点。长时间运行的 Agent 需要能在上下文压缩中存活的记忆。

**4\. 权限粒度带来回报。** 每个工具、每个模式、每个目录的权限规则，deny-first 评估。这比"允许一切"标志要多做很多工作，但这就是 Demo 和可部署系统之间的区别。

**5\. 构建时间至关重要。** OpenAI 的实验表明，一分钟是 Agent 内循环构建时间的上限。超过这个阈值，Agent 的生产力急剧下降。

**6\. 优化环境，而非模型。** Ryan Lopopolo 提出的关键问题： **如果你停止围绕人类使用习惯优化代码库、工作流和组织，而是开始为 Agent 可读性优化它们，会发生什么？**

---

## 八、学术前沿：Harness 的自动化优化

### 8.1 Meta-Harness：让 LLM 自己设计 Harness

2026 年 3 月，Stanford 和 MIT 的研究者发布了 **Meta-Harness** ，展示了通过 Agent 搜索在 Harness 设计空间上的自动化优化。

Meta-Harness 在 TerminalBench-2 上达到了 76.4% 的通过率（超越人工设计方法的 74.7%），在 5 个 held-out 模型上 IMO 级别数学问题提升 +4.7 个百分点，在文本分类上使用 4 倍更少的 token 提升 +7.7 个百分点—— **所有改进都来自一个发现后应用于多个模型的单一 Harness** 。

这提供了迄今为止最强的实证证据： **Harness 设计是形式可分离且可优化的工程问题。**

### 8.2 ACON：上下文压缩的系统化方法

ACON（Agent Context Optimization）是一个统一的上下文压缩框架，通过失败驱动的指南优化，在三个挑战性基准上实现了 26-54% 的峰值 token 缩减：

- **AppWorld** ：峰值 token 降低超过 25%，同时保持准确率
- **OfficeBench** ：峰值上下文大小降低近 30%，准确率保持在 74% 以上
- **8 目标 QA** ：峰值 token 和依赖分别降低 54.5% 和 61.5%

核心创新是"对比反馈"机制：给定完整上下文成功但压缩上下文失败的成对轨迹，让 LLM 分析失败原因，然后更新压缩指南。这个过程完全是梯度自由的，可直接用于闭源或生产模型。

### 8.3 Agent Harness Survey：22 个系统的分类学

2026 年 4 月发布的《Agent Harness for Large Language Model Agents: A Survey》是领域内的首个系统性综述，分析了 22 个代表系统，提出了形式化框架 H=(E,T,C,S,L,V)，并识别了 9 个技术挑战领域。

该综述将 Harness 生态系统分为五个类别：全栈 Harness、框架、能力模块、评估基础设施和设计工具。其中五个全栈 Harness——DeepAgents、Claude Code、OpenClaw、DeerFlow 和 OpenHands——实现了所有六个治理组件。

---

## 九、Harness 将走向何方

### 9.1 从"厚"到"薄"的长期趋势

领域正在向更薄的 Harness 发展，因为模型在不断提升。但 Harness 本身不会消失——即使是最强大的模型也需要某种东西来管理其上下文窗口、执行工具调用、持久化状态和验证工作。

OpenClaw 社区的观察显示，随着 Claude Sonnet 4.6 和 Opus 4.7 的发布，许多以前需要复杂 Harness 逻辑的任务现在可以用更简单的结构完成。但同时，新模型也打开了以前不可能的更复杂任务的视野，这些任务又需要新的 Harness 能力。

### 9.2 Harness 即产品

两个使用相同模型的产品可以仅凭 Harness 设计就产生天壤之别。 **Harness 不是一个已解决的问题，也不是一个商品层。** 它是真正困难工程所在：将上下文管理视为稀缺资源、设计在失败复合前捕获它们的验证循环、构建提供连续性而不产生幻觉的记忆系统，以及做出关于构建多少脚手架 vs. 留给模型的架构押注。

Stripe 和 OpenAI 的经验表明， **Harness 质量在团队间的差距正在扩大，而模型间的差距在缩小。** 在 2026 年，Harness 设计是决定性的差异化因素。

### 9.3 编程范式本身的转变

Ryan Lopopolo 提出了一个更深层的思考： **软件开发本身正在被重新定义。** 在 OpenAI 的实验中，代码越来越被视为"一次性的"——工作树和合并冲突的重要性降低了，因为 Agent 可以在几分钟内重新解决它们。"幽灵库"的概念正在出现：给定高保真的规范，编码 Agent 可以从头重新复现复杂系统，而无需共享源代码。

这可能指向一种根本不同的软件开发范式： **从高保真规范生成软件，而非手工编写和维护代码。** 在这种范式中，Harness 不是辅助工具，而是主要的"编程环境"。

---

## 十、结论：Harness 是新的战场

Agent Harness 概念的爆发标志着 AI 工程领域的一个关键拐点。社区终于认识到： **当模型跨过能力阈值后，真正的工程挑战不在于让模型更聪明，而在于更有效地引导和约束模型的能力。**

LangChain 的 TerminalBench 突破、OpenAI 的百万行代码实验、Stripe 的每周 1,300 个 PR——这些案例共同指向同一个结论： **Harness 就是产品。**

对于正在构建 AI Agent 的团队，核心启示是： **下次你的 Agent 失败时，不要责怪模型。看看 Harness。**

检查你的上下文管理是否让关键信息淹没在噪音中。检查你的验证循环是否在失败复合前捕获它们。检查你的工具设计是否让 Agent 困惑而非赋能。检查你的记忆系统是否在提供连续性的同时避免幻觉。

2026 年的 AI 工程竞赛不在模型层——OpenAI、Anthropic、Google 正在快速收敛。竞赛在 Harness 层—— **谁能够设计出最优雅、最可靠、最可扩展的基础设施，来将模型的原始智能转化为可信赖的生产力。**

正如 Stripe 的 Minions 系统和 OpenAI 的 Symphony 项目所证明的： **Harness 工程不是未来的概念，而是正在发生的革命。** 它不是关于"是否"拥抱 Harness 思维的问题，而是关于"多快"的问题。

---

## 参考来源与深度阅读

本文写作过程中参考了以下核心来源，按类别组织：

### 原文与核心分析

- \[1\] Akshay Pachaar, "The Anatomy of an Agent Harness", X/Twitter, 2026-04-06. 本文深度解读的核心原文。
- \[2\] Daily Dose of Data Science Blog, "The Anatomy of an Agent Harness", 2026-04-06. 原文的完整博客版本。

### 官方文档与工程博客

- \[3\] Claude Code Agent Harness Architecture Deep Dive, 2026-04-12. Claude Code 架构深度解析。
- \[4\] Anthropic, "Best Practices for Claude Code", 2025. Claude Code 最佳实践官方文档。
- \[5\] WaveSpeed AI, "Claude Code Agent Harness: Architecture Breakdown", 2026-04-06.

### 生产案例研究

- \[6\] Ryan Lopopolo (OpenAI), "Harness Engineering", 2026-03. OpenAI Frontier 团队的百万行代码实验。
- \[7\] Stripe Engineering, "Minions: Stripe's one-shot, end-to-end coding agents", 2026-03. Stripe Minions 系统详解。
- \[8\] ByteByteGo, "How Stripe's Minions Ship 1300 PRs a Week", 2026-03-16.
- \[9\] Awesome Agents, "Stripe's AI 'Minions' Now Ship 1,300 Pull Requests Per Week", 2026-04-08.

### 学术论文

- \[10\] "Agent Harness for Large Language Model Agents: A Survey", Preprints, 2026-04-09. 领域内首个系统性综述。
- \[11\] "Meta-Harness: End-to-End Optimization of Model Harnesses", arXiv:2603.28052, 2026-03-30. Stanford/MIT 的自动化 Harness 优化研究。
- \[12\] "Optimizing Context Compression for Long-horizon LLM Agents (ACON)", arXiv:2510.00615, 2025-10-01. 上下文压缩的系统化方法。
- \[13\] "Lost in the Middle: How Language Models Use Long Contexts", Stanford/UC Berkeley, 2024. 上下文窗口性能衰减的经典研究。

### 社区讨论

- \[14\] Atlan, "What Is Harness Engineering AI? The Definitive 2026 Guide", 2026-04-13.
- \[15\] Logdew, "OpenAI Symphony: From Supervising Coding Agents to Managing Work", 2026-03-09.
- \[16\] TTalk, "通过工程化的Harness改进Deep Agent", 2026-04-14. LangChain TerminalBench 优化详解。

### 播客与访谈

- \[17\] Latent Space Podcast, "Ryan Lopopolo, OpenAI Frontier & Symphony", 2026-04-07.
- \[18\] Station F, "Boris Cherny, Anthropic: 'I have not written a single line of code since November'".
- \[19\] AI Daily Brief, "Harness Engineering 101", 2026-04-13.

---

> **关于本文** ：本文是一篇社区驱动的技术分析，综合了 2026 年 4 月以来 AI 工程社区的核心讨论和最新实践。如果你正在构建 AI Agent 系统，希望本文能为你的 Harness 设计决策提供有价值的参考。

![](https://pic1.zhimg.com/v2-6f29f8455d5d42e03b0823155abac22a_1440w.jpg)

编辑于 2026-04-19 16:13・广东