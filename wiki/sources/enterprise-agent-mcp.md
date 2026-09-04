---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch24-mcp.md
tags: [enterprise-agent-platform, mcp, tool-registry, protocol]
---

# 第24章 MCP 与企业工具生态

## 摘要

本章讨论 MCP 在企业平台中的正确位置：**MCP 是 L3 协议层接入标准，Tool Registry 是 L2 能力中枢**。MCP 让外部能力以统一 JSON-RPC 语义暴露 Tools/Resources/Prompts，降低「一 Agent 一集成」的重复成本；但协议只解决发现与调用，**不提供企业 IAM、网络隔离和审计语义**——企业不能直接把任意 MCP Server 接进生产，仍需经过自己的 Registry 做权限、审计与风险分级。核心结论：MCP 不替代 Registry，集成路径永远是「发现 → 注册 → invoke」，Runtime 主循环不直连 MCP Server。

## 核心要点

- **四硬约束**：(1) MCP 不替代 Tool Registry——平台统一命名/版本/校验，MCP 管进程与服务边界上的协议；(2) Run 主循环不直连 Server——先注册为 Registry handler，连接池与熔断在 Client 层复用，避免延迟/连接风暴与责任归属断裂；(3) Resources 不替代 RAG——RAG 负责「搜」，Resource 负责「读某一已知文档版本」；(4) Server 侧审计必须留——协议不自带 IAM，Server 须记录调用方身份/`tenant_id`/参数摘要/结果摘要/`run_id`。
- **三角色**：Host（承载用户会话、编排 LLM 与 Client，≈ Runtime+Planner）、Client（连接多个 Server，负责 `tools/list`/`tools/call` 与传输细节）、Server（独立进程/服务，暴露 Tools/Resources/Prompts）。三者不可混实现。
- **传输方式**：stdio（本地子进程，注意生命周期避免僵尸进程）、Streamable HTTP（远程主流，配 TLS/鉴权/超时/body 限制/网关路由）、HTTP+SSE（2024-11-05 规范遗留兼容）、进程内（教学示例）。
- **三类能力分工**：Tools（执行动作，进 Registry+Runtime）、Resources（只读 URI 对象如 `sales://report/2025Q1`，走带权限的资源读取或缓存，不进副作用审计链）、Prompts（提示模板，进统一 Prompt 仓库避免双源维护）。判断规则：可执行动作进 Registry，只读对象进资源读取/RAG，提示模板进 Prompt 仓库。
- **Client 池四件事**：按 Server 实例复用连接、注册时工具名加前缀（`mcp_db_`）防冲突、Server 连续失败临时摘除并熔断、按租户限制并发 `tools/call`。Agent 只看到可用工具与结果，不感知连接重建/熔断/实例切换。
- **直连 HTTP vs MCP Server**：跨团队共享/需标准发现/被 IDE 或多 Host 复用的能力 → MCP Server；单一业务内部/延迟极端敏感/接口稳定受控 → 直连（如毫秒级交易风控保留 gRPC）。判断标准回到复用范围、治理成本、延迟预算与审计要求，先问「未来会不会被第二个 Host 使用」。
- **接入治理**：身份须用户会话/Agent 配置/工具策略三处交叉确认租户与 scope（任何一处不一致即拒绝，Server 不能只信模型传来的参数）；网络用 Service+NetworkPolicy 限定命名空间访问、公网禁用无鉴权端点、限制 body 大小（结果摘要与原始大对象分离，大对象转受控 artifact URI）；审计两边对上——Registry handler 把 `run_id`/`tool_call_id`/内部 `request_id` 作为结构化字段传给 MCP Client，Server 原样写入访问日志；跨境标注数据域（`cn-north`/`eu`），Policy 拒绝跨域调用，连错误日志与 trace 采样也要检查 PII。
- **失败分类四类**：连接失败（重试/切换副本/熔断）、协议失败（不可重试，摘除新版本并告警）、业务失败（反馈 Planner 调参或结束）、策略失败（停止动作、必要时转审批）。不能只返回「tool failed」让 Planner 猜。用户可见降级提前设计：只读工具不可用提示稍后重试，写工具失败不自动改走备用路径。
- **版本灰度四步**：快照候选（不暴露给 Planner）→ 静态校验（name/描述/inputSchema/返回结构/风险/租户/身份）→ 影子调用（对比新旧结果只记 Trace）→ 按 Agent/租户/业务线放量。记录三类版本并可追溯：`server_version`（提供方）、`tool_spec_version`（平台登记）、`registry_version`（Agent 实际可见）；回滚回滚 Registry 可见版本而非要求 Server 撤代码。
- **工具退化**：Server 仍响应但结果质量下降（限流/凭证收紧/供应商改版）——只监控连接成功率会漏掉。接入时设计替代路径：只读降缓存/静态报表，写操作转 HITL 或暂停，外部工具切内部 Server。给每个生产 MCP 工具加 `degradation_mode` 与 `replacement_path` 两字段。
- **准入与生态**：MCP Server 按生产工具管理——分三类（开发调试=沙箱 / 内部只读=身份审计资源范围 / 生产可写=幂等补偿审批样本回放）；租户级 allowlist（能力拆开看，可只撤某租户某工具）；供应链审查（代码来源/依赖/网络出口/凭证/日志字段/回滚方式），无维护团队的 Server 不进入生产目录。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch24-mcp.md)
