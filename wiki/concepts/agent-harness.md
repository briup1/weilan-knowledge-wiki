---
type: concept
created: 2026-05-08
updated: 2026-05-18
sources: [agent-harness-anatomy, harness-engineering-guide, hermes-agent-guide]
tags: [agent-harness, ai-engineering, orchestration, scaffolding, production]
---

# Agent Harness

大模型之外的**全部工程化基础设施**——系统提示词、工具调用、状态管理、安全沙箱、记忆系统、验证循环等模型之外的代码、配置与执行逻辑的总称。Harness 是将模型的原始能力转化为可靠生产力的关键层。

## 定义

Agent Harness（智能体驾驭系统）的概念最早在 2023 年 Beren Millidge 的论文《Scaffolded LLMs as Natural Language Computers》中有雏形，2026 年初被 OpenAI、Anthropic 和 LangChain 同时正式命名和采用。

核心公式：**"If you're not the model, you're the harness."**（LangChain 工程师 Vivek Trivedy）

Anthropic 的 Claude Code SDK 就是"the agent harness that powers Claude Code"。OpenAI Codex 团队同样将"agent"和"harness"等同，指代让 LLM 发挥作用的非模型基础设施。

> **Harness 原意是「马具」**——驾驭马匹的皮带、衔铁、缰绳的组合。如果 AI 模型是一匹聪明的马，Harness 就是让它按照预期方向、速度、节奏稳定运行的马具系统。不是让马更聪明，而是让马稳定运行。
> —— Anthropic Engineering Blog, 2025

## 脚手架隐喻

来自建筑行业的脚手架（Scaffolding）隐喻精确描述了 Harness 的本质：

- 脚手架是**临时**基础设施，让工人（LLM）到达原本无法触及的高度
- 脚手架本身不做建设，但没有它工人就无法到达上层楼层
- **脚手架在建筑完工时会被拆除**——Harness 的设计目标应是"为移除而构建"

从计算机架构视角：原始 LLM = CPU，上下文窗口 = RAM，外部数据库 = 磁盘存储，工具集成 = 设备驱动程序，Harness = 操作系统。

## 工程三层演进

| 层次 | 时间 | 焦点 | 核心问题 |
|------|------|------|---------|
| Prompt Engineering | 2022-2024 | 与模型对话 | "怎么说" |
| Context Engineering | 2025 | 模型能看到的信息 | "看什么" |
| Harness Engineering | 2026 | 围绕模型的完整系统 | "怎么控" |

每一层在前一层之上构建，而非取代。Prompt 仍在 Harness 内发挥作用，Context 管理仍是 Harness 的核心组件。

## Harness Engineering 四要素

Anthropic 工程团队将 Harness 抽象为四个核心要素，这是实践层面的最小可操作框架：

| 要素 | 内容 | 作用 |
|------|------|------|
| 提示词结构 | 明确告诉 Agent 角色、任务边界、禁止行为 | 约束行为方向 |
| 状态文件 | AGENTS.md、feature_list.json、claude-progress.txt 等 | 跨会话状态持久化 |
| 工具配置 | git、浏览器自动化、文件读写、代码执行等 | 赋能 Agent 操作能力 |
| 验证机制 | 规定何时、如何验证成果，防止自我认定「完成」 | 保证输出质量 |

**最小可行 Harness 目录结构**：
```
project/
├── AGENTS.md          # 全局工作规范
├── feature_list.json  # 功能清单，每项有 pass/fail 状态
├── claude-progress.txt # 进度日志
├── init.sh            # 环境初始化脚本（必须幂等）
├── .git/              # 版本控制（必须）
└── src/               # 业务代码
```

核心思想：**把 Agent 需要知道的一切外化到文件系统，而非依赖 Agent 的「记忆」**。

## 三 Agent 架构（进阶）

面对高复杂度、长时间、高质量要求的任务，Anthropic 演化出 Planner + Generator + Evaluator 架构：

| Agent | 职责 | 关键行为 |
|-------|------|---------|
| **Planner** | 规划者 | 接收高层需求，扩展为完整 PRD，刻意避免过早指定技术细节 |
| **Generator** | 生成者 | 从 PRD 逐功能实现，每个 Sprint 前与 Evaluator 协商 Sprint Contract |
| **Evaluator** | 评估者 | 用 Playwright MCP 像真实用户一样验证，按标准打分，不达标则退回修改 |

**Sprint Contract 协商流程**：Generator 起草「本次目标 + 完成标准 + 验证方式」→ Evaluator 确认标准可测量 → 双方达成一致 → Generator 开始编码 → 自我评估 → Evaluator 独立验证 → 评分达标后提交。

**评估维度与权重**：设计质量（高）/ 原创性（高）/ 工艺精度（中）/ 功能可用性（中）。

关键发现：**评估标准本身就具有引导作用**——即使 Evaluator 尚未给出反馈，带有明确评估标准的 Generator 产出质量已明显优于无 Harness 基准。

## 12 大核心模块

1. **编排循环**：Agent 的心跳，实现 TAO（Thought-Action-Observation）/ ReAct 循环。核心是"while 循环 + 它管理的一切"——复杂度不在循环本身，而在循环所管理的 7 个步骤。跨上下文窗口的连续性通过 Ralph Loop 模式解决。
2. **工具系统**：Agent 的双手。每个工具定义为 schema（name + description + parameters）。沙箱执行（Linux bwrap / macOS sandbox-exec）+ 权限门控（deny-first）。核心原则：**工具超过约 10 个重叠工具时应考虑拆分为多个 Agent**。
3. **记忆系统**：跨越时间尺度的状态保持。Claude Code 三层架构：上下文内记忆（最快最脆弱）→ memory.md 指针索引层（自愈合机制）→ CLAUDE.md 静态记忆（项目宪法）。8 个优先级层级。
4. **上下文管理**：在噪音中找到信号。核心挑战是上下文腐烂——关键内容落在窗口中间时性能下降超 30%。5 种压缩策略：Snip、Microcompact、Context Collapse、Autocompact、Reactive Compact。
5. **Prompt 构建**：模型实际看到的世界。五层组装：基础人格→角色指令→工具定义→上下文注入→动态规则。目标：**最小高信号 token 集合**。
6. **输出解析**：从自由文本到结构化行动。三代演进：自由文本解析→Function Calling→Grammar-Constrained Decoding（接近 100% schema 合规）。
7. **状态管理**：让任务可恢复、可调试。LangGraph 图节点状态机、OpenAI 四种互斥策略、Claude Code Git 即状态机。
8. **错误处理**：在必然的错误中生存。10 步 99% 成功率 → 端到端仅 90.4%。四级分类：瞬态（重试）/LLM 可恢复（返回模型）/用户可修复（Human-in-Loop）/意外（冒泡终止）。核心：**永不因单次工具失败终止循环**。
9. **安全防护**：三层架构——输入 Guardrails（检测注入/PII）→ 工具 Guardrails（参数验证）→ 输出 Guardrails（幻觉/合规）。权限执行与模型推理在架构上分离。
10. **验证循环**：从玩具到生产的分水岭。三种方法：规则反馈（确定性"地面真相"）、视觉反馈（截图比对）、LLM-as-Judge（语义检测）。警惕自我验证偏差。
11. **子 Agent 编排**：并行化的艺术。Claude Code 三种模型：Fork/Teammate/Worktree；OpenAI 两种模式：Handoffs/Agents-as-Tools。Agent Teams 比 Sub-agents 省 3-5 倍 token。
12. **初始化与环境**：为长期记忆提供起点。CLAUDE.md、NOTES.md、环境变量、项目信任建立。

## Context Anxiety 与 Context Reset

Anthropic 工程师观察到：当 Context Window 接近上限时，某些模型会产生「急于收尾」的冲动（Context Anxiety），草草结束任务甚至宣布完成——即使实际上还有大量工作未做。

**两种处理方式对比**：

| 方式 | Compaction（压缩） | Context Reset（重置） |
|------|-------------------|----------------------|
| 机制 | 将早期对话摘要压缩，同一 Agent 继续 | 完全清空 Context，新 Agent 通过文件传递状态 |
| 优点 | 保持连续性，无需设计交接 | 彻底解决 Context Anxiety |
| 缺点 | 累积噪音，不能完全解决焦虑 | 增加交接复杂度，需要完善的状态传递文件 |
| 适用场景 | 中短任务 | 长期复杂任务，需要稳定多会话执行 |

Harness Engineering 推荐 Context Reset + 结构化状态文件（feature_list.json + claude-progress.txt）作为根本解法。

## 薄 vs 厚 Harness：2026 年最重要的架构押注

| 立场 | 代表 | 核心论点 |
|------|------|---------|
| 薄 Harness | Anthropic（Boris Cherny）、Noam Brown | 所有秘诀在模型本身；搭脚手架很多时候是添乱；METR 对比显示 Claude Code/Codex 未显著赢过基础脚手架 |
| 厚 Harness | LangChain（Jerry Liu）、LangGraph | 模型驾驭一切——最大障碍是用户的上下文/工作流工程能力；TerminalBench 同模型不同 Harness 排名差 25 位 |
| 调和 | Latent Space 社区 | 脚手架原则——为移除而构建；两者描述不同共进化阶段的系统 |

**未来验证测试**：替换为更强模型后，如果性能提升且无需增加 Harness 复杂性，则设计合理。

## 7 个关键设计决策

1. **单 Agent vs 多 Agent**：首先最大化单 Agent 能力。工具超过约 10 个重叠工具时才拆分。
2. **ReAct vs Plan-and-Execute**：LLMCompiler 报告 Plan-and-Execute 有 3.6 倍速度提升。不确定性高用 ReAct，结构明确用 Plan-and-Execute。
3. **上下文窗口管理**：ACON 研究表明保留推理痕迹而非原始工具输出可实现 26-54% token 缩减，保持 95%+ 准确率。
4. **验证循环设计**：Guides（前馈）+ Sensors（反馈）结合。
5. **权限与安全**：宽容模式（快速但风险高）vs 限制模式（安全但慢）。Stripe 混合方案：隔离环境最大自由 + 真实交互严格权限。
6. **工具范围**：更多工具通常意味着更差性能。只暴露当前步骤所需的最小工具集。
7. **Harness 厚度**：薄 = 信任模型进步速度；厚 = 需要确定性/可审计性/可靠性最大控制权。

## 学术前沿

- **Meta-Harness**（Stanford/MIT，2026-03）：LLM 自动优化 Harness，TerminalBench 76.4%（超越人工 74.7%），跨模型迁移有效。
- **ACON**（上下文压缩优化）：失败驱动的压缩指南优化，26-54% token 缩减。
- **Agent Harness Survey**（2026-04）：22 个系统分类学，形式化框架 H=(E,T,C,S,L,V)，9 个技术挑战领域。

## 相关概念

- [[agent-memory-system]] —— Agent 记忆系统
- [[multi-agent-collaboration]] —— 多 Agent 协作
- [[mcp]] —— MCP 工具调用协议
- [[llm-wiki]] —— LLM Wiki 知识沉淀范式

## 相关实体

- [[claude-code]] —— 薄 Harness 哲学的代表，Harness Engineering 最佳实践
- [[langgraph]] —— 厚 Harness 哲学的代表（显式状态图）
- [[openai-agents-sdk]] —— 代码优先的 Harness 设计
- [[hermes-agent]] —— Harness 思想的产品化实现（自动记忆、自动 Skill、常驻守护）

## 相关脉络

- [[agent-harness-thread]] —— Agent Harness 十二模块技能树

## 来源

- [[agent-harness-anatomy]] —— 万字讲透 Agent Harness 的十二大模块
- [[harness-engineering-guide]] —— Harness Engineering 完全指南（Anthropic 工程团队实践）
- [[hermes-agent-guide]] —— Hermes Agent 完全新手指南（Harness 产品化实现）
