---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch31.md
tags: [enterprise-agent-platform, framework, build-vs-buy]
---

# 第31章 框架横向对标

## 摘要

本章划分框架、平台和应用。LangGraph、AutoGen、CrewAI 以及 Dify、Coze、Bisheng 可以进入企业架构，但不能替代 Runtime、Registry、Policy、HITL 和 Trace。会改变业务状态的动作，最后都要进企业 Runtime 和 Registry。

## 核心要点

- 框架是嵌入代码的开发库，解决 Planner、角色和多 Agent 怎么写。平台是统一的 `/run`、六态、Registry、Policy、HITL、Trace 和 Console。应用是面向一个岗位或流程的 Agent。
- LangGraph 适合放在 Planner 里表达分支、循环和人工中断。对外仍折叠成 Runtime 状态。`thread_id` 映射 `run_id`，图里的工具调用转到企业 Registry，`interrupt()` 映射 `waiting_human`。它不是独立生产入口。
- 低代码产品强在入口、Bot 渠道和知识管理。画布好用只说明开发方便，不证明有生产治理。
- 自研适合平台内核：统一 Run、Registry、协议适配、Policy、HITL、Trace 和与业务系统的深度集成。采购适合营销 Bot、标准 RAG 问答、非核心只读助手这类要上线速度的场景。
- 已有框架按三步收编：先让工具调用走 Registry，再把运行事件折叠成六态和 `state` / `action` / `result`，最后把写操作、审批和导出迁回企业 Runtime。工具和权限不能拖到最后。
- 能力矩阵用来看清框架强项和平台底座，不是给产品打分。混合可以存在，底线是运行语义不被不同框架拆成多套。

## 局限

对照表是本书相对 mini-platform 的整理，不是这些产品的当前能力测评。采购问题清单也没有附带厂商答复或版本号。框架升级后的真实兼容性要按当时版本再核。

## 关联

- [[agent-platform-boundary]]
- [[enterprise-agent-runtime]]
- [[enterprise-agent-tool-registry]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch31.md)
