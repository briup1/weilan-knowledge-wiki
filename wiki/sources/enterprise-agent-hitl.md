---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch30-human-in-the-loop.md
tags: [enterprise-agent-platform, hitl, approval, checkpoint]
---

# 第30章 Human-in-the-loop 与长任务

## 摘要

本章把人工介入写成高风险 Agent 的治理能力，而不是模型效果不够时的临时补丁。审批进入 Runtime 的 `waiting_human`，并在同一 `run_id` 上恢复。澄清问题只补全输入，审批才是对动作的授权。

## 核心要点

- 目标分四类：授权高风险动作、复核关键产物的质量、让合规要求可追踪、把人工拒绝和修改收进评测样本。缺了授权会造成越权自动化；这和聊天里补问一句不是同一件事。
- 前置审批在工具执行前暂停，用于转账、删除、改主数据。后置审批先生成草稿，发布或外发前再停。分级审批用于多角色会签。
- 批准不是新 Run。拒绝进入 `failed` 并记下结构化原因。不要在原 Run 里静默改掉已批准的产物再继续，否则审计说不清人批的是哪一版。
- Cancel 是放弃：停未开始的工具、尽力取消进行中的工具、关掉待办，写成 `failed` 加取消原因。已完成的副作用不自动回滚。Hold 是等待补充材料，Run 继续停在 `waiting_human`。
- 引擎检查点给 Runtime 恢复，保存状态、工具结果和 Memory 引用。业务检查点给 Console 和合规回放，保存草稿、审批里程碑和展示状态。两者用同一个 `run_id` 对齐，字段不能混用。
- 业务回放包要回答谁批准、依据什么数据、发布了哪个版本、模型有没有越过人工。前端能点批准但后端另开一次请求，因果链就断了。

## 局限

这是平台契约设计，不是某一套审批产品的实测结果。文中的 mini-platform 示例用来说明同一 Run 上的暂停和恢复，不能当成已在生产验证的默认实现。图片未随 Markdown 下载，图示不能当证据。

## 关联

- [[human-in-the-loop]]
- [[agent-run-lifecycle]]
- [[enterprise-agent-runtime]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part05-agent-capabilities/ch/ch30-human-in-the-loop.md)
