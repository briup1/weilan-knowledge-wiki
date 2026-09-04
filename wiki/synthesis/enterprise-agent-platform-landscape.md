---
type: synthesis
created: 2026-09-04
updated: 2026-09-04
sources: [enterprise-agent-platform-boundary, enterprise-agent-platform-architecture-map, enterprise-agent-runtime, enterprise-agent-tool-registry, enterprise-agent-mcp, enterprise-agent-planner, enterprise-agent-agentic-workflow, enterprise-agent-memory]
tags:
  - enterprise-agent-platform
  - platform-architecture
  - agent-eval
  - governance
---

# 企业级 Agent 平台工程全景图

> 基于《企业级 Agent 平台工程》原文章节编译，随章节摄取逐步扩展。来源：datagallery-lab enterprise_agent_platform（固定提交 e5d97a6，2026-07-03，Apache-2.0）。
> 当前覆盖：平台边界（第2章）、参考架构与阅读路径（第4章）、执行骨架（第22-24章）、Planner/局部增强/Memory（第25-27章）。多 Agent 与协议章节（第28-29章）待续。

## 平台定位：从试点到统一治理线

```text
业务 Agent（报价/经营分析/工单/票据…）可各不相同
        ↓ 统一平台契约
模型入口 · 工具契约 · 运行状态 · trace 字段 · 评估样本 · 审批策略
```

触发条件（三信号齐现）：重复建设 · 治理断裂 · 接入摩擦。平台价值不在「再做一个更大的 Agent」，而在把跨场景重复出现、影响权限与成本、关系审计与恢复的能力收口到同一条治理线上。业务可以保留不同节奏与框架，但涉及模型入口、工具注册、权限审批、运行记录与评估回放时必须统一。

## 平台边界（概念方法）

```text
应用/框架/平台三层：业务任务 | 单 Agent 编排 | 多 Agent 共享与治理
        ↓
五类共性问题：模型 · 数据 · 工具 · 流程 · 治理
        ↓ 四问判据（复用性/风险与审计/域特殊规则/接入成本）+ 变化速度
平台收：强共性+高风险+稳定  →  业务留：快变化+域专属+低风险
```

判断尺度：能力是否可复用、证据是否可追踪、失败是否可恢复、责任是否可确认、成本是否可解释。详见 [[agent-platform-boundary]]。

## 四层参考架构

```text
业务任务层      DataAgent/报价/工单/经营分析工作台      用 Agent 完成什么任务
Agent 能力层    任务状态/工具调用/规划/长任务/多Agent/协议   如何把任务推进
智能与数据层    模型推理/结构化输出/RAG/语义层/湖仓/指标口径  Agent 凭什么理解判断
基础设施治理层  网关/可观测/评估/成本/限流/安全/合规/组织     如何稳定可信可控运行
```

层间依赖顺序：业务任务提出目标 → Agent 能力推进任务（须从数据知识层拿可信上下文）→ 数据知识提供证据（受治理层约束）。

## 八能力簇：执行骨架 / 智能放大器 / 反馈系统

```text
执行骨架   Runtime（任务生命周期）· Registry（工具/能力/版本登记）· Policy（权限/审批执行）
智能放大   Planner（决定下一步）· Memory（会话与长期上下文）· RAG/Knowledge（企业知识接入）
反馈系统   Observability（trace/回放）· Eval（版本好坏判断）
```

- **执行骨架**（Runtime/Registry/Policy）：让 Agent 被统一运行和约束；没有它们，系统只能演示、工具变乱、越权迟早出现。
- **智能放大器**（Planner/Memory/RAG/Knowledge）：让 Agent 理解上下文并动态推进；缺它们长任务与多轮任务会失真。
- **反馈系统**（Observability/Eval）：让平台避免黑箱化与失控；缺它们出错无法解释、版本好坏靠感觉。

能力簇与已摄取概念的对应：Runtime → [[agent-runtime-event-stream]] / [[state-management]]；Registry → [[agent-tool-system]]（工具供给与契约）；Policy → [[agent-security]]；Memory → [[agent-memory-system]] / [[context-management]]；RAG/Knowledge → [[rag]]；Observability → [[agent-trace]]；Eval → [[agent-eval-platform-landscape]] / [[validation-loop]]。

### 执行骨架落地（第22-24章）

- **Runtime 执行契约**（[[enterprise-agent-runtime]]）：Run/Step/Tool Call 三对象分层 + Run 六态（`pending/planning/executing/waiting_human/succeeded/failed`）作为平台契约，终态只能由 Runtime 判定；SSE `action/result` 成对、检查点/恢复/幂等、三档超时、取消=失败+原因码。统一形态见 [[agent-run-lifecycle]]。
- **Tool Registry 治理**（[[enterprise-agent-tool-registry]]）：Function Calling 只产生意图，Registry 以 `(name, version)` 主键统一注册/校验/版本治理，生产 pin 版本；MCP/HTTP 工具全部收敛为 ToolSpec，模型输出永远不能替代 invoke 前校验。
- **MCP 接入边界**（[[enterprise-agent-mcp]]）：MCP 是 L3 协议、Registry 是 L2 中枢，路径恒为「发现→注册→invoke」；四硬约束（不替代 Registry/主循环不直连/Resources 不替代 RAG/Server 侧审计），Tools/Resources/Prompts 三类能力分流，影子灰度与三版本追溯。

### 智能放大器落地（第25-26章）

- **Planner 稳定接口**（[[enterprise-agent-planner]]）：[[agent-planner]] 只读取受控上下文与 Registry 同源工具视图，输出 FINISH/ASK/TOOL_CALL 提议；Runtime 掌握执行与终态。ReAct 用于探索，Plan-and-Execute 用于计划审批，状态图只承载需要复用/回放的复杂路径。
- **Agentic Workflow 局部增强**（[[enterprise-agent-agentic-workflow]]）：[[agentic-workflow-enhancements]] 将 Reflexion、Self-Refine、ToT 作为 Planner 内默认关闭的可选能力；三计数器分离、事实槽位锁定、未选分支不执行，并按「离线→影子→小流量」验证收益后启用。
- **Memory 四层治理**（[[enterprise-agent-memory]]）：[[agent-memory-system]] 按 Working/Episodic/Profile/Org Context 拆生命周期与责任；Working 进入检查点，长期记忆先具备确认、删除、隔离和版本能力，RAG 与 Memory 不共用权限/索引语义。

## DataAgent 主线

DataAgent 被选为贯穿场景，因为它几乎穿过每一架构层：模型（规划/生成 SQL/解释）、数据（语义层/口径/湖仓）、知识（元数据/历史分析/业务术语）、Agent（Runtime/Planner/人工介入）、治理（权限/trace/评估/审计）、前端（图表/引用/报告）。一次请求的七个检查点：任务创建 → 上下文加载 → 路径规划 → 工具执行 → 结果解释 → 治理记录 → 结果交付。误把 DataAgent 当「NL2SQL + 图表」，平台建设第一天就会跑偏。

## 一年建设路线（公共资产沉淀顺序）

```text
Q1  Runtime/模型入口/工具注册/基础trace/首试点   → 统一任务状态模型 + 工具风险分级
Q2  评估/成本归集/审批/管理界面                  → 评测样本模板 + 上线准入清单
Q3  语义层/RAG/第二业务线复制                   → 口径/数据权限/知识接入规范
Q4  灰度/降级/SLO/供应商接入/平台目录            → 复盘模板 + 成本质量运营报表
```

路线成败检验：第二、三个场景接入时重复步骤是否减少；平台化信号是「后续场景少做重复工作」，不是文档数量增加。能力归属判断（早期底座 vs 后期扩展）见 [[agent-platform-boundary]]。

## 后续扩展计划

- 第28-29章：多 Agent 协作 / Agent 协议与标准
- 第38-42/50-51章（另一半资料）：可观测与评测 / 安全治理
