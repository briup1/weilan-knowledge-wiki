---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch26-agentic-workflow.md
tags: [enterprise-agent-platform, agentic-workflow, reflexion, self-refine, tree-of-thoughts]
---

# 第26章 Agentic Workflow

## 摘要

本章把 Reflexion、Self-Refine、Tree of Thoughts（ToT）定义为 Planner 之上的**局部增强机制**，而非新的 Runtime 或 Planner mode。它们可能提升复杂任务质量，也会放大 token、延迟、Gateway QPS 与不可预测性，因此应默认关闭，按任务/租户/风险显式启用，并具备预算、停止条件、独立 Trace、灰度和策略级回滚。企业不宜照搬 AutoGPT 式无界自主循环，而应拆成「失败后有限反思一次、终稿有限精修一次、高风险动作前有限比较候选」等受控片段。

## 核心要点

- **与编排模式正交**：ReAct/Plan-and-Execute 决定步骤结构；Workflow 增强决定一个 planning 步骤内部是否允许额外 LLM 轮次或候选搜索。增强不改变 Run 六态，也不能绕过 Runtime。
- **三个计数器**：`step_index` 统计 Runtime 完成 planning→executing 闭环；`llm_call_count` 统计 plan/reflect/refine/tot_eval 等 Gateway 调用；`tool_call_count` 只统计 Registry invoke。否则会出现「步骤没变、成本翻倍」却无法归因。
- **Reflexion**：针对模型可自行修正的错误（参数格式、字段、时间窗口、工具选择、空结果）总结失败轨迹并注入 Working Memory；权限拒绝、策略冲突和服务不可用不得靠反思绕过。普通重试假设环境会恢复，反思假设上一轮计划有误，两者共享同一恢复预算。
- **Self-Refine**：用于工具执行结束后的报告/邮件/结构化答案润色。必须把事实槽位与表达槽位分开，数字和 EvidenceRef 只读；否则润色会制造事实漂移。critic 输出结构化 `pass/issues`，迭代通常限 1–3 次。
- **ToT**：Planner 内生成/评分/剪枝候选分支，仅最终选中分支可产出 Tool Call，未选分支绝不能执行。分支数×深度造成指数成本；默认关闭，仅在真实存在方案取舍的高价值离线分析或高风险动作前有限启用，评估需规则+Policy，不只靠 LLM 自评。
- **AutoGPT 生产边界**：无界目标扩展、默认副作用、成本不可预测、未验证中间结论写长期 Memory、缺少 Run/Step/Trace 回放，均与企业治理冲突。自主循环只能降维为有界、可关闭、可计量片段。
- **统一运行约束**：`max_steps`/Run 超时/取消；按 Agent YAML 显式开关；Registry+Policy 副作用网关；长期记忆带来源/时间戳/删除；每次增强调用独立 span；高风险仍进入 `waiting_human`。
- **停止条件优先**：Reflexion 连续两次未修复即结束/降级/转人工；Self-Refine 达上限提交带问题标记草稿或转人工；ToT 分支评分接近时降级保守方案。没有新证据时反复重写收益低。
- **取消传播**：用户取消 Run 时，Planner 内部 reflect/refine/tot_eval 也必须停止，避免前端已结束而后台继续烧 token。
- **发布门禁**：离线 A/B → 影子记录但不改变结果 → 低风险小租户灰度 → 按配置放量；同时验证质量收益、p95 延迟、token 成本、Trace 完整性、事实锚定、取消与退出稳定性。
- **策略级回滚**：可按任务/租户/风险/产物单独关闭某一增强，不回滚整个 Runtime；台账记录策略组合、版本、触发条件、预算、模型路由、评测集与撤回条件。
- **用户状态可解释**：将增强阶段映射为少量稳定状态（收集证据/修订产物/比较候选/等待审批/降级完成/需要人工），提供取消入口，但不暴露完整内部推理。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch26-agentic-workflow.md)
