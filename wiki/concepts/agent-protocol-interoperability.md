---
type: concept
created: 2026-09-04
updated: 2026-09-04
sources: [enterprise-agent-protocols]
tags: [agent-architecture, interoperability, protocol, mcp, a2a]
---

# Agent 协议互操作

> 协议降低跨边界连接成本；企业平台仍负责把外部能力翻译成可授权、可版本化、可恢复、可退出的内部对象。

## 协议版图

| 协议/机制 | 协作对象 | 内部映射 |
|---|---|---|
| MCP | 工具、资源、Prompt | ToolSpec / 资源读取 / Prompt 仓库 |
| A2A | 有状态远端 Agent 任务 | 异步 Tool Call 或外部 Handoff |
| Agent Card | Agent endpoint/skill/auth 元数据 | L1 Agent Catalog 中的 AgentSpec |
| ACP / Event | 持续消息与事件协作 | 内部 Event envelope / 异步 Tool |
| 模型 tools API | 模型调用意图 | Registry 导出的 schema |

## 稳定适配边界

```text
外部原始声明/协议消息
  → adapter（传输、认证、错误翻译、版本快照）
  → ToolSpec / AgentSpec / Event envelope
  → Catalog/Registry → Policy → Runtime → Trace
```

Runtime 只依赖 Registry，不持有协议 Client。外部能力升级只影响适配器和登记对象，不改 Run 状态/Trace schema。协议声明不等于内部授权；外部新增 skill、tool 或事件必须重新经过 owner、租户、数据域、风险与审批准入。

## 证据与版本

同时保留外部原始声明和内部治理后对象；一次 Run 固定协议/适配器版本、Card etag、tool schema、ToolSpec/AgentSpec、出站策略、远端 task/request ID 和 artifact hash。历史回放使用快照，不临时读取远端最新状态。

A2A Task 是外层 Run 中的一次异步委托：外层取消需传播，无法传播则标记 orphan 并进入补偿。写操作响应超时按「可能已执行」处理，先用远端 task ID/幂等键查询状态，不能盲重试。

## 安全与生命周期

- 出站前校验身份映射、租户、PII/密级、数据驻留、合同范围和脱敏。
- Card URL 防 SSRF；Secret 只保存引用；artifact 校验类型、大小、hash、来源和密级。
- 同一真实能力只保留一个内部入口，避免 MCP/A2A/模型 tools 多路触发同一副作用。
- draft/disabled/stale/production 状态化；无 owner、频繁漂移、长期失败或合同到期即停用，新 Run 不再命中，历史证据保留。
- 适配器契约测试覆盖版本漂移、认证、权限、超时、取消、重复、部分成功与旧版本回放；先沙箱和观察期，再放量。

## 与 Provider 协议归一化的区别

[[provider-protocol-normalization]] 归一化模型厂商的请求/SSE/ToolCall wire format；本概念归一化企业边界外的工具、Agent 和事件能力。两者都用 adapter 隔离变化，但治理对象不同。

## 关联

- [[mcp]]：工具/资源互操作协议
- [[multi-agent-collaboration]]：平台内 Handoff 与角色协作
- [[agent-tool-system]]：外部能力最终收敛的执行入口
- [[agent-run-lifecycle]]：外部长任务的状态、取消与恢复契约
- 来源：[[enterprise-agent-protocols]]
