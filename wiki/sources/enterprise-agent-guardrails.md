---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part10-security-org/ch/ch51-guardrails.md
tags: [enterprise-agent-platform, guardrails, content-safety, policy]
---

# 第51章 Guardrails 与内容安全

## 摘要

本章把 Guardrails 写成平台控制系统，不是一个内容审核 API。内容分类器识别风险，策略引擎做决定，工具层管最小权限，输出层做脱敏和结构校验，观测层管误杀和漏杀。早期目标是可配置、可解释、可回归，不是一次拦住所有风险。

## 核心要点

- 分层检查输入、上下文、工具调用和输出。分类结果必须映射成拒绝、脱敏、审批、降级或放行，不能停在高中低标签。
- 通用分类器覆盖暴力、自伤、色情、仇恨等类别。企业还要补金融、医疗、涉密、客户隐私和品牌风险。分类不是决策。
- 策略引擎按租户、角色、阶段和业务变化做允许、拒绝、脱敏、审批、降级或记录。规则不能只写死在 Prompt 或应用代码里。
- 脱敏不能只放在最终回答前。密钥和隐私会出现在输入、检索片段、工具结果、中间输出、前端状态、日志和导出文件里。答案里看不见，Trace 里仍可能有原文。
- 治理看误杀率、漏杀数、审批通过率和体验影响，不只看拦截率。拦截率上升可能是攻击变多，也可能是策略过严。策略要有负责人、灰度、申诉和复盘。

## 局限

文中的网关评估目录是设想结构，作者写明当前仓库还没有这个实验，不能把它当成已运行的实现。分类器产品名只是类别示例，没有做效果对比。

## 关联

- [[agent-guardrails]]
- [[agent-security]]
- [[validation-loop]]
- [[human-in-the-loop]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part10-security-org/ch/ch51-guardrails.md)
