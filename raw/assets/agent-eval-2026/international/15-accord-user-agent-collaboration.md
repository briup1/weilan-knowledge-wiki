---
type: research-source
region: international
publication_date: 2026-08-28
collected: 2026-09-01
source_type: research-paper
organization: Academic research collaboration
original_language: en
original_url: https://arxiv.org/abs/2608.27818
tags: [agent-eval, user-simulation, preferences, collaboration, conversational-agent]
---

# AcCoRD：评估真实用户偏好变化下的人机协作

## 资料信息

- 原文标题：AcCoRD: Evaluating User-Agent Collaboration Under Realistic User Preference Dynamics
- arXiv 首次提交：2026-08-28
- 原文链接：https://arxiv.org/abs/2608.27818
- 资料类型：研究论文 / Benchmark

## 为什么值得阅读

企业助手面对的用户偏好并非一次性完整给出，而会在交互中形成、暴露、调整或放宽。AcCoRD 把这种动态纳入 Benchmark，补足了只测“隐藏固定偏好”或最终任务成功的传统方法。

## 主要内容中文译介

现有用户—Agent 协作 Benchmark 通常假设偏好已经存在，只是用户没有完全说明，Agent 的任务是通过澄清找出这些固定约束。AcCoRD 认为真实交互更复杂：用户可能在看见候选方案后才形成偏好，也可能改变原有要求，或在没有可行选项时主动放宽约束。

Benchmark 覆盖在线购物和旅行规划两个领域，并评估五个前沿 LLM。作者比较普通 ReAct 与“由不确定性引导”的提示策略，后者要求模型主动识别和解决用户偏好中的模糊性。

实验显示，前沿模型相对能处理一开始未充分说明的偏好，但对交互中途出现或变化的偏好明显更困难；仅靠提示词也不足以稳定触发需要的不确定性识别。这意味着协作 Agent 的能力不能只由最终推荐是否可接受判断，还要观察其何时澄清、是否记住当前偏好、能否识别冲突并适应变化。

## 方法与评估设计

- **场景领域**：在线购物、旅行规划。
- **偏好动态**：未充分说明、交互中形成、逐步显露、调整和放宽。
- **Agent 策略**：普通 ReAct 与不确定性引导提示。
- **评估对象**：任务完成之外的偏好识别、澄清决策、状态保持和动态适应。
- **关键发现**：模型对固定隐藏偏好相对较好，对中途形成或变化的偏好仍显著不足。

## 对企业级平台的启示

1. 用户模拟器要支持状态演化，而不是用固定 Persona 一次性生成所有回答。
2. Trace 中应显式记录偏好版本、偏好来源、冲突、澄清问题和用户放宽约束的时点。
3. 评估指标应包含无效澄清次数、必要澄清召回、偏好保持率、冲突检测率和适应成功率。
4. 客服、销售、采购、差旅等场景应测试多轮需求变化，防止 Agent 机械坚持旧约束。
5. 不能只用最终成交或推荐命中评分；需要判断过程是否减少用户负担、是否擅自假设以及是否尊重最新意图。
6. Memory 更新行为应纳入评测，区分当前会话偏好、长期偏好和不应永久保存的临时选择。

## 局限与阅读警告

论文只覆盖购物和旅行两个领域，用户模拟与真实用户行为仍有差距；结果表明提示策略不足，但不等于所有 Memory、规划或不确定性建模方法均无效。企业采用时还需增加隐私、敏感偏好、身份切换和多参与方协作测试。
