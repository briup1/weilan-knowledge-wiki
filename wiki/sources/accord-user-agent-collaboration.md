---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/15-accord-user-agent-collaboration.md
tags: [agent-eval, user-preference, collaboration]
---

# AcCoRD：评估真实用户偏好变化下的人机协作

## 摘要

AcCoRD（2026-08-28）认为用户偏好不是一开始就固定、只是没说完。偏好会在看见方案后形成、中途改变，或在没有可行选项时放宽。只测隐藏固定偏好或最终任务成功，会漏掉协作质量。

## 核心要点

- 覆盖在线购物和旅行规划，评了五个前沿 LLM。
- 对照普通 ReAct 和“由不确定性引导”的提示。后者要求模型主动找出并处理偏好里的模糊点。
- 前沿模型相对能处理一开始没说清的偏好，但对交互中途出现或变化的偏好明显更差。只改提示词不足以稳定触发这种识别。
- 协作评估要看何时澄清、是否记住当前偏好、能否识别冲突并适应变化，不能只看最终推荐能不能接受。

## 局限

只有购物和旅行两个领域，用户是模拟的。提示策略不够，不能推出所有记忆、规划或不确定性建模方法都无效。企业还要另测隐私、敏感偏好、身份切换和多方协作。

## 关联

- [[evaluation-asset]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/15-accord-user-agent-collaboration.md)
