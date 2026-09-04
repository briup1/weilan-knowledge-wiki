---
type: concept
created: 2026-09-04
updated: 2026-09-04
sources: [enterprise-agent-agentic-workflow]
tags: [agent-architecture, reflexion, self-refine, tree-of-thoughts, workflow]
---

# Agentic Workflow 增强机制

> 在 Planner 内部按需增加反思、精修或候选搜索；默认关闭，只有质量收益能覆盖成本、延迟和治理代价时才启用。

## 与编排模式的边界

```text
Runtime 六态（不变）
  └─ Planner mode：ReAct / Plan-and-Execute / 状态图
       └─ 可选增强：Reflexion / Self-Refine / ToT
```

编排模式回答「步骤怎样组织」，增强机制回答「当前步是否值得再推理」。增强不能执行工具、改变权限或绕过 Runtime；额外 Gateway 调用必须独立计量和进入 Trace。

## 三类机制

| 机制 | 解决什么 | 可用场景 | 禁止/边界 |
|---|---|---|---|
| Reflexion | 用失败轨迹改进下一步行动 | 参数、字段、时间窗口、可修正空结果 | 权限/策略拒绝、服务不可用不能靠反思绕过 |
| Self-Refine | 改进终稿表达或结构 | 报告、邮件、JSON 格式 | 事实槽位与 EvidenceRef 只读，不改工具结果 |
| Tree of Thoughts | 有限比较多个候选方案 | 高价值离线分析、高风险动作前评估 | 未选分支绝不执行；分支/深度受预算约束 |

## 生产约束

- 三计数器分离：`step_index` / `llm_call_count` / `tool_call_count`。
- 默认全部关闭；按 Agent、租户、任务和风险显式启用。
- 每类机制有最大轮数、token 预算、停止条件和取消传播。
- Reflexion 与工具重试共用恢复预算；同类错误反复出现即停止。
- ToT 只把选中分支转换成一条 `PlannerDecision`；候选仅存在 Planner 内存/Trace。
- 增强中间结果不自动进入长期 Memory，未验证探索不能污染后续 Run。
- 高风险动作仍走 Registry、Policy 与 HITL，模型自评不是审批。

## 发布判据

```text
离线 A/B → 影子（只记录）→ 低风险小流量 → 按配置放量
   任一阶段出现事实漂移 / 成本失控 / 取消失败 / 审批绕过 → 策略级关闭
```

同时比较任务质量、p95 延迟、token/QPS、人工返工、Trace 完整性和失败退出稳定性。没有收益证据的复杂度应删除或保持关闭。

## 关联

- [[agent-planner]]：增强依附的稳定决策接口
- [[agent-run-lifecycle]]：预算、取消、恢复和状态契约
- [[validation-loop]]：事实锚定、停止与副作用护栏
- [[agent-trace]]：每次 reflect/refine/tot_eval 的独立证据
- [[agent-memory-system]]：反思摘要可进入 Working，但不自动晋升长期记忆
- 来源：[[enterprise-agent-agentic-workflow]]
