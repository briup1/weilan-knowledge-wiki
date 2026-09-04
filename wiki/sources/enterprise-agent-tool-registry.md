---
type: source
created: 2026-09-04
updated: 2026-09-04
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch23-tool-registry-function-calling.md
tags: [enterprise-agent-platform, tool-registry, function-calling, tool-governance]
---

# 第23章 Tool Registry & Function Calling

## 摘要

本章把 Tool Registry 与 Function Calling 放进同一条调用链：**Function Calling 解决模型侧问题**（模型用 JSON 表达「要调用哪个工具、参数是什么」，但只产生调用意图，不执行）；**Tool Registry 解决平台侧问题**（这个调用能否执行、该执行哪一版、参数是否合法、错误如何分类）。工具是 Agent 产生真实副作用的出口，注册、版本、参数契约、权限与审计必须在平台统一，否则会出现重复实现、审计断裂、版本漂移三类事故。核心原则：模型输出不能替代平台校验——即使开启 `strict: true`，Registry 在调 handler 之前仍须强制校验 schema。

## 核心要点

- **平台 API 分层定位**：L1 资源管理（管控面：运维/Console 配置发布）、L2 运行时（数据面）、L3 协议互通（MCP/A2A）。Registry 横跨 L1（注册）与 L2（`(name, version)` 解析并 `invoke`）；注册走管控面，调用走运行时。
- **ToolSpec**：`name`（稳定名）/`version`/`description`（写给模型也写给人——写清适用场景、禁止场景与副作用，降低误选）/`parameters_schema`（JSON Schema）/`handler`。核心操作：`register`（重复注册失败防静默覆盖）、`get`（未找到抛 `TOOL_NOT_FOUND`）、`list_versions`。
- **三条治理线**：Registry 不承载业务实现（存 ToolSpec，handler 可散在进程内/HTTP/MCP 适配器）；Function Calling 只产生调用意图，执行在应用侧；注册面与调用面分开——不得在 Run 主循环里逐次 REST 注册。
- **JSON Schema 的边界**：schema 管形状，Policy 管权限，handler 管业务语义。「合法但危险的 JSON」是生产常态（缺租户过滤、时间范围过大、导出含 PII）。Structured Outputs `strict` 只约束模型输出格式，仍不能替代 invoke 前校验；OpenAI `tools` 定义与 Registry schema 须同源（`to_openai_tool`）。
- **版本治理**：主键 `(name, version)`，多版本并存；生产 Agent **pin 版本**（可审计可复现），实验 Agent 可用 latest，灰度用配置中心按租户路由。对模型只暴露一个逻辑名，版本由 Agent 配置或 Runtime 解析，避免模型在 `v1`/`v2` 间随机选。下架前查 `list_versions` 与 Agent 引用；破坏性变更升主版本并保留兼容窗口。注册信息带 `owner`/`risk_level` 供 Policy 使用。
- **invoke 语义与错误码**：`get` → `validate_parameters` → `handler`；错误统一继承 `RegistryError`（`code`/`message`/`details`）：`TOOL_NOT_FOUND`、`TOOL_ARGUMENT_INVALID`（反馈 Planner ≤3 次修正后仍失败才 `failed`）、`TOOL_UNAVAILABLE`（重试/熔断/失败）。Runtime 负责把错误映射成 `result` 事件，不把底层异常栈抛给用户。
- **最容易出错的四个位置**：Agent 硬编码工具 import（修复：唯一入口改 Registry）；schema 与 handler 签名漂移（修复：注册 CI 对比两者）；把模型输出当已校验参数（修复：invoke 前必须 `validate_parameters`）；多版本同时暴露给模型。
- **工具生命周期治理**：状态序列 候选→可用→限制使用→冻结→退役；按发布前（schema/权限/错误码/回归样本）/运行中（调用量/失败率/人工介入）/下线后（依赖 Agent/历史 Trace 可解释）三段组织。工具描述是可测试资产需运营；影子验证（记录「若启用会选择什么」但真实走旧版）降低写操作升级风险；组合风险（只读+导出+邮件连成数据外泄路径）需 Policy 看同 Run 工具序列。
- **结果证据分级**：`authoritative`（事实可进报告）/`candidate`（需复核）/`status`（只驱动任务流转）三类，避免 Agent 把候选当结论、把执行中状态当完成。返回 schema 标明结果类型/数据时间/权限范围/是否可引用。
- **业务语义保护贴近执行端**：模型与 Planner 给意图、Registry 给 schema 与风险标签、最终由 handler/领域服务确认业务规则；不能把权限依据与审批流程藏进 Prompt。未执行的调用（Policy 拒绝/审批驳回）同样要审计。工具健康状态（维护/高错误率/配额耗尽）纳入发现，让 Planner 少用或不用。
- **兼容发布**：新增可选字段可灰度，删除字段/改含义/扩大权限/只读改写必须新版本；旧版本保留运行能力，历史 Trace 回放能找到当时的 schema 与解释；下线需依赖证据（活跃 Agent/历史 Run/评测样本/审批页差异/owner 确认）。

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch23-tool-registry-function-calling.md)
