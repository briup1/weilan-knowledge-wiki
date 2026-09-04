---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch27-memory.md
tags: [enterprise-agent-platform, agent-memory, working-memory, privacy, governance]
---

# 第27章 Memory 系统

## 摘要

本章把 Agent Memory 定义为可恢复、可授权、可过期的上下文子系统，而非「把历史对话全部塞回 Prompt」或企业知识库的别名。Memory 分为 Working、Episodic、Profile、Org Context 四层，分别服务当前任务连续性、跨 Run 任务经验、用户长期偏好和企业正式口径；四层生命周期、权限、责任方与删除规则不同，不能混成一个向量库。企业应先做好 Working 检查点、删除、隔离、版本与审计，再开放长期记忆自动晋升。

## 核心要点

- **Working Memory**：Run/会话级，保存最近输入、Planner 决策、工具结果摘要与错误；由 Runtime 管理并进入检查点，保证恢复后 Planner 知道已看过什么、执行过什么。
- **Episodic Memory**：跨 Run 的历史任务片段、成功路径与人工修正；必须带来源、时间、场景和版本，防止跨用户污染与过期经验继续生效。
- **Profile**：用户长期偏好（格式、语言、常用筛选）；采用「候选提取→去重→敏感检查→用户确认/策略批准→版本化写入」，临时表达不能自动固化。
- **Org Context**：组织、指标、权限、审批与业务术语的正式上下文；来自主数据、语义层或受控配置，不由个人对话生长，必须返回版本与有效期。
- **读取顺序与最小注入**：先组织正式口径，再 Working 连续性，Episodic 按需检索，Profile 只注入相关偏好。用户偏好不能覆盖当前任务目标、权限或企业指标口径。
- **检查点完整性**：仅保存 `state` 不够，至少还需 `step_index`、Tool Call、`working_snapshot`；大型 CSV/PDF/日志存对象存储，Working 只留 sample、schema、行数、hash 和 `result_ref`。
- **模型可见 vs 审计可见**：模型只看任务相关摘要；审计保留原始结果引用、hash、执行时间和当次注入的 MemoryRef，两者可关联但不能全部塞入 Prompt。
- **Memory ≠ RAG**：RAG 面向文档/知识库/表结构/政策，强调 citation 与文档权限；Memory 面向用户/Run/任务经验/组织使用上下文，强调连续性、恢复、删除和作用域。私人对话不得混入共享 RAG 索引。
- **长期写入是治理动作**：模型只能建议；平台根据来源、用户授权、敏感等级、可验证性、有效期和作用域决定落库。Org Context 不能由对话直接覆盖。
- **删除必须可证明**：清理主存储、向量索引、缓存、摘要和下游副本；不可变审计证据可受限保留，但不能继续参与模型检索。支持单条、项目、类别和租户级撤回。
- **污染检测与修复**：比较禁用/候选/生产 Memory 三种条件下的行为；保存 `memory_id`、来源 Run、写入策略、读取记录和用户反馈。错误条目按删除/降权/重摘要/用户确认/过滤策略修复，并回放受影响样本。
- **上下文预算**：Working 只保留近期意图、最后成功结果、关键错误和当前计划；Episodic 限 top-k+租户过滤；Profile/Org 只注入当前任务相关内容；关键数值、SQL、审批意见和 artifact hash 不由 LLM 摘要改写。
- **评测看三件事**：该记住的信息是否正确使用；不该记住的信息是否过滤；过期/撤销信息是否停止生效。评测环境使用受控 Memory 快照，避免读取生产用户历史导致分数失真。
- **最小生产顺序**：先稳定 Working+检查点+删除/导出；再以内部低风险场景试 Profile 候选（确认后写入）；Episodic 只存成功任务摘要与证据引用；Org Context 只读受控配置。没有删除和确认能力时，长期记忆宁可不上。
- **用户控制面**：至少提供查看、纠正、删除、限制使用与命中解释；高风险任务默认少用个人偏好，Memory 只改善连续性，不能替代当前证据与 Policy。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch27-memory.md)
