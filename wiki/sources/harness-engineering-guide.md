---
type: source
created: 2026-05-14
updated: 2026-05-18
raw: raw/archive/Harness Engineering 完全指南：让 Claude Code 真正可靠地完成任务.md
tags: [agent-harness, claude-code, engineering-practice, anthropic, reliability]
---

# Harness Engineering 完全指南：让 Claude Code 真正可靠地完成任务

**来源**：微信公众号 / 程康健（基于 Anthropic Engineering Blog）
**链接**：https://mp.weixin.qq.com/s/bDj4Gd2OVWeW3wqVQBJj3A

## 摘要

本文系统阐述 Anthropic 工程团队用于约束 AI Agent 行为的工程化框架——Harness Engineering（脚手架工程）。核心论点是：模型能力强不等于执行可靠，AI 在复杂工程任务中频繁失败的根源在于缺少一套约束其行为的外化框架，而非模型本身不够聪明。

## 核心主张

1. **能力（Capability）≠ 可靠性（Reliability）**。模型能「知道」正确答案，不等于能「持续做对」正确的事。可靠性取决于工具设计、上下文管理、验证机制——这些都是 Harness Engineering 的范畴。
2. **Harness 四要素**：提示词结构（约束行为方向）+ 状态文件（跨会话持久化）+ 工具配置（赋能操作能力）+ 验证机制（保证输出质量）。
3. **最小可行 Harness 目录结构**：
   - `AGENTS.md`：全局工作规范（角色、禁止行为、通用规则）
   - `feature_list.json`：功能清单与完成状态（JSON 结构化约束优于 Markdown）
   - `claude-progress.txt`：人类可读的进度日志
   - `init.sh`：环境初始化脚本（必须幂等）
4. **三 Agent 架构**（进阶）：Planner（规划者，输出 PRD）→ Generator（生成者，逐功能实现）→ Evaluator（评估者，用 Playwright MCP 像真实用户一样验证）。Sprint Contract 协商流程确保「完成标准」在编码前就达成共识。
5. **防止 Agent 提前宣告完成的四种机制**：功能清单强制检查、独立 Evaluator Agent、浏览器自动化强制验证（Puppeteer MCP）、进度文件诚实记录。

## 关键洞察

- **Context Anxiety（上下文焦虑）**：当 Context Window 接近上限时，模型会产生「急于收尾」的冲动，草草结束任务甚至宣布完成。Context Reset（完全重置 + 通过文件传递状态）是根本解法。
- **Initializer Agent 与 Coding Agent 分离**：初始化需要宏观视角（想清楚做什么），编码需要微观执行（专注做好一件事），混用会导致计划和执行交织失控。
- **JSON 格式的 feature_list.json 使模型「不适当地修改已有条目」的概率远低于 Markdown**——结构化约束使模型倾向于只修改 `passes` 字段。
- 评估标准本身就具有引导作用：Anthropic 实验发现，即使 Evaluator 尚未给出反馈，带有明确评估标准的 Generator 产出质量已明显优于无 Harness 基准。
- **Hermes Agent 是 Harness Engineering 思想的产品化实现**：自动技能进化（Learning Loop）≈ 自动 SKILL.md；三层持久记忆 ≈ 自动 AGENTS.md + 进度文件；常驻守护进程 ≈ 消除 Context Reset 需求。

## 与现有知识的关联

- 是 [[agent-harness]] 概念的核心方法论来源
- 与 [[claude-code]] 的 CLAUDE.md / `.claude/` 目录结构直接对应
- Hermes Agent 产品化对应关系见 [[hermes-agent]]
- 三 Agent 架构与 [[multi-agent-collaboration]] 的编排模式形成互补

## 原始文件

- [原始文件](../../raw/archive/Harness%20Engineering%20%E5%AE%8C%E5%85%A8%E6%8C%87%E5%8D%97%EF%BC%9A%E8%AE%A9%20Claude%20Code%20%E7%9C%9F%E6%AD%A3%E5%8F%AF%E9%9D%A0%E5%9C%B0%E5%AE%8C%E6%88%90%E4%BB%BB%E5%8A%A1.md)
