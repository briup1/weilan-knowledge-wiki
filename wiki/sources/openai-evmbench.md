---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/14-openai-evmbench.md
tags: [agent-eval, sandbox, code-grader]
---

# OpenAI 与 Paradigm：EVMbench 智能合约 Agent 评测

## 摘要

EVMbench（2026-02-18）评 Agent 发现、修补和利用高严重性智能合约漏洞的能力。数据来自 40 次审计的 117 个精选漏洞。它把高风险、有副作用的任务放进隔离环境，用程序检查真实状态。

## 核心要点

- 三种模式：Detect 按已知漏洞召回和审计奖励评分；Patch 要消除可利用性并保持预期功能；Exploit 在沙箱链上做端到端资金攻击，用交易回放和链上状态评分。
- Harness 用 Rust 部署合约、确定性回放交易，并限制不安全的 RPC。Exploit 跑在本地 Anvil，不跑真实网络。
- 团队写了自定义 Grader，并对评测环境做红队测试，专门找 Agent 欺骗或绕过评分器的方法。

## 局限

历史漏洞、本地链和单链顺序回放覆盖不了主网时序、跨链和全部现实攻击。Detect 主要对照人工已知漏洞，Agent 找到的新问题难以自动判断真假。漏洞利用具有双重用途，企业使用必须有明确授权和隔离，不能把评测环境接到真实资金或生产链。

## 关联

- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/14-openai-evmbench.md)
