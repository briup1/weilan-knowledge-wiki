---
type: source
created: 2026-05-08
updated: 2026-05-08
raw: raw/archive/万字讲透Agent Harness的十二大模块：2026 年 AI 工程化最核心的基础设施.md
tags: [agent-harness, ai-engineering, orchestration, claude-code, openai, langchain, stripe, production]
---

# Agent Harness 十二大模块深度解析

基于 Akshay Pachaar 的技术分析，综合 Anthropic、OpenAI、LangChain、Stripe 等一线团队的最新实践，对 Agent Harness 进行全方位解剖。

## 核心主张

1. **Harness 是新的战场**：当模型能力跨过阈值后，限制因素不再是模型本身，而是包裹在模型之外的工程化基础设施（Harness）。LangChain 在 TerminalBench 2.0 上保持模型不变仅优化 Harness，排名从 30+ 跃升至第 5。
2. **AI 工程三层演进**：Prompt Engineering（2022-2024，怎么说）→ Context Engineering（2025，看什么）→ Harness Engineering（2026，怎么控）。每一层在前一层之上构建，而非取代。
3. **"如果你不是模型，你就是 Harness"**：系统提示词、工具调用、状态管理、安全沙箱——所有模型之外的代码、配置与执行逻辑都属于 Harness 范畴。
4. **薄 Harness vs 厚 Harness 之争**：Anthropic 押注"薄 Harness + 模型改进"（Claude Code 的"dumb loop"哲学），LangGraph 押注"显式控制"的厚 Harness。两者可以同时成立——描述不同共进化阶段的系统。
5. **更多工具通常意味着更差的性能**：Vercel 移除 80% 工具性能反升；Claude Code 懒加载实现 95% 上下文缩减。核心原则：只暴露当前步骤所需的最小工具集。

## 关键数据

- LangChain TerminalBench 2.0：同一模型，通过 Harness 优化通过率从 52.8% → 66.5%（排名 30+ → 5）
- Meta-Harness（Stanford/MIT）：LLM 自动优化 Harness 达到 76.4% 通过率，超越所有人工设计
- OpenAI Symphony：3 名工程师、5 个月、零行人工代码，100 万行生产级应用
- Stripe Minions：每周 1,300+ 个零人工代码 PR 合并到生产代码库
- Claude Code：约 40 个权限门控工具，懒加载实现 95% 上下文缩减
- 10 步流程每步 99% 成功率 → 端到端仅 90.4%；50 步 → 60.5%

## 12 大核心模块

| 模块         | 关键机制                                                                 | 核心挑战                                   |
| ---------- | -------------------------------------------------------------------- | -------------------------------------- |
| 编排循环       | ReAct/TAO/"dumb loop"                                                | 上下文耗尽时状态保持（Ralph Loop）                 |
| 工具系统       | schema 定义/沙箱执行/权限门控                                                  | 工具过载导致选择困惑                             |
| 记忆系统       | 三层：上下文内/memory.md 指针/CLAUDE.md 静态                                    | "不信任自己的记忆"原则                           |
| 上下文管理      | 5 种压缩策略（Snip/Microcompact/Collapse/Autocompact/Reactive）             | 上下文腐烂（Lost in the Middle）              |
| Prompt 构建  | 五层组装（人格→角色→工具→上下文→动态规则）                                              | 最小高信号 token 集合                         |
| 输出解析       | 自由文本→Function Calling→Grammar-Constrained Decoding                   | 结构化输出 vs 工具调用场景区分                      |
| 状态管理       | LangGraph 图节点/OpenAI 四种策略/Claude Code Git 即状态机                       | 长时任务的检查点与恢复                            |
| 错误处理       | 四级分类：瞬态/LLM 可恢复/用户可修复/意外                                             | 永不因单次工具失败终止循环                          |
| 安全防护       | 三层：输入/工具/输出 Guardrails + Tripwire 机制                                 | 权限执行与模型推理的架构分离                         |
| 验证循环       | 规则反馈/视觉反馈/LLM-as-Judge                                               | 自我验证偏差（确认倾向）                           |
| 子 Agent 编排 | Fork/Teammate/Worktree（Claude Code）；Handoffs/Agents-as-Tools（OpenAI） | Agent Teams 比 Sub-agents 省 3-5 倍 token |
| 初始化与环境     | CLAUDE.md/NOTES.md/环境变量                                              | 为长期记忆提供起点与结构                           |

## 主流框架对比

| 框架 | Harness 哲学 | 核心架构 | 记忆方案 | 状态管理 |
|------|------------|---------|---------|---------|
| Claude Code | 薄 Harness（dumb loop） | Gather-Act-Verify 循环 | 三层文件式记忆（8 优先级层级） | Git 提交即检查点 |
| OpenAI Agents SDK | 代码优先 | Runner 类 + Codex 三层架构 | Sessions（SQLite/Redis） | previous_response_id 链式 |
| LangGraph | 厚 Harness（显式控制） | 图节点的状态机 | 命名空间 JSON Store | Super-step 检查点 + 时间旅行 |
| CrewAI | 角色驱动 | Agent + Task + Crew | ChromaDB RAG 召回 | Flows 确定性骨架 |

## 生产案例

- **OpenAI Symphony**：零人工代码的百万行实验。核心教训——构建时间 > 1 分钟时 Agent 生产力急剧下降；失败时问"缺少什么能力/上下文/结构"而非"换提示"。
- **Stripe Minions**：每周 1300 PR。"牛而非宠物"哲学——标准化 devbox、完整 shell 权限、无确认提示。五层管道：调用→Devbox→Agent 核心→蓝图→CI 循环。
- **LangChain Deep Agents**：Harness 优化的标杆。自验证机制 + 环境上下文注入 + 循环检测打断 + 推理三明治策略。关键工具：LangSmith 追踪分析失败模式。

## 脚手架原则

Harness 设计目标应是"为移除而构建"：随着模型能力提升，Harness 复杂性应降低。未来验证测试：如果替换为更强模型后性能提升且无需增加 Harness 复杂性，则设计合理。

但需注意**模型-Harness 共进化**陷阱：模型与特定 Harness 共同训练，移除脚手架可能导致性能下降。

## 相关概念

- [[agent-harness]] —— Agent Harness 核心概念
- [[agent-memory-system]] —— Agent 记忆系统
- [[multi-agent-collaboration]] —— 多 Agent 协作
- [[claude-code]] —— Claude Code 终端 AI 助手
- [[mcp]] —— Model Context Protocol
- [[langgraph]] —— LangGraph 显式状态图框架
- [[openai-agents-sdk]] —— OpenAI Agents SDK

## 原始文件

- [原始文件](../../raw/archive/万字讲透Agent Harness的十二大模块：2026 年 AI 工程化最核心的基础设施.md)
