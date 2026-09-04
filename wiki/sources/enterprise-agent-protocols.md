---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch29-agent.md
tags: [enterprise-agent-platform, agent-protocol, mcp, a2a, agent-card, acp]
---

# 第29章 Agent 协议与标准

## 摘要

本章把协议定位为 L3 跨边界适配层：MCP 面向工具/资源/Prompt，A2A 面向远端 Agent 任务委托，Agent Card 面向能力发现，ACP/事件协议面向持续消息协作。协议解决互操作，平台内核继续负责状态、权限、版本、检查点、审计和恢复。所有外部能力必须先映射为内部 ToolSpec/AgentSpec/Event，再经 Registry、Policy、Runtime 与 Trace；「协议调通」不等于生产接入。

## 核心要点

- **按协作对象选协议**：数据库/文件动作→MCP；外部 Agent 完整分析→A2A；能力元数据→Agent Card；持续事件→ACP 或内部 Event Bus；模型 Function Calling 只表达意图，仍由 Registry 执行。
- **统一收敛链**：外部声明快照→适配器→内部 ToolSpec/AgentSpec/Event envelope→Catalog/Registry→Policy→Runtime→Trace。Runtime 不 import MCP/A2A Client，只依赖 Registry。
- **一能力一入口**：同一副作用若同时以 MCP、A2A、模型 tools API 暴露，Catalog 合并为一个能力资产，明确首选/备用/禁用协议，避免重复执行与审计别名。
- **MCP**：远端 tool 快照版本化后注册 ToolSpec；外部描述改写为明确资源范围、动作、风险、输入/输出和租户。原始 MCP schema 与内部治理后的 ToolSpec 都保留；Server 升级生成新版本而非覆盖旧版。
- **A2A**：A2A Task 映射为外层 Run 中的异步 Tool Call/外部 Handoff，保存 `external_task_id`、状态、artifact hash、供应商版本；补充材料可映射 `waiting_human`，外层取消需传播或将远端任务标为 orphan 并补偿。
- **Agent Card**：只负责发现，不负责执行。导入 L1 Catalog，校验 schema/认证/网络/版本并生成内部 AgentSpec；pin etag/版本，刷新失败标 stale 而非立刻删除；原始 Card 与解析结果双份留证。
- **ACP/事件**：外部消息先转内部事件 envelope，经签名、租户、schema、幂等和 Policy 校验；事件表达「发生了什么」，不能直接变成有副作用的 invoke。
- **外部声明不等于权限**：新增 skill 不自动进入 Planner 可见集；每项能力需 owner、风险等级、租户/数据域、环境和审批策略。出站前检查 PII、密级、驻留、合同范围和脱敏。
- **版本快照**：一次 Run 记录协议/适配器版本、Agent Card etag、MCP tool schema、ToolSpec/AgentSpec、出站策略、远端请求 ID 和 artifact hash；历史回放不能依赖远端当前状态。
- **部分成功语义**：写操作响应超时可能已产生副作用，外部 Task 可能有 artifact 但没完成回调；适配层保存远端 task ID、幂等键、artifact 与补偿动作，恢复时查询状态而非盲重试。
- **错误与退化分层**：连接/认证/协议/schema/业务/策略分别映射内部错误；只读可切备份/缓存，中风险分析保留草稿异步恢复，高风险写操作/跨域发送暂停转人工。替代能力必须重新走 Registry 与 Policy。
- **安全基线**：Agent Card 导入防 SSRF（URL allowlist/egress proxy/禁私网与跳转），Secret 不写 Card；外部 artifact 校验类型、大小、hash、来源与密级；本地 MCP Server 做供应链审查。
- **契约测试与沙箱**：覆盖认证失败、权限拒绝、schema 变化、超时、重复回调、取消、部分结果、stale Card、超大 artifact、事件重复投递和旧版本回放；先脱敏沙箱→观察期→有限租户/只读→逐步放量。
- **生命周期**：draft/disabled/stale/production 等状态；无 owner、合同到期、长期失败、频繁漂移或长期不用即停用。停用不删除历史证据，新 Run 不再命中。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch29-agent.md)
