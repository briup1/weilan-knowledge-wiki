---
type: research-source
region: international
publication_date: 2026-02-18
collected: 2026-09-01
source_type: official-research
organization: OpenAI and Paradigm
original_language: en
original_url: https://openai.com/index/introducing-evmbench/
tags: [agent-eval, sandbox, deterministic-replay, programmatic-grader, cybersecurity]
---

# OpenAI 与 Paradigm：EVMbench 智能合约 Agent 评测

## 资料信息

- 原文标题：Introducing EVMbench
- 发布机构：OpenAI、Paradigm
- 发布日期：2026-02-18
- 原文链接：https://openai.com/index/introducing-evmbench/
- 资料类型：官方研究发布 / Benchmark

## 为什么值得阅读

EVMbench 展示了高风险、有副作用 Agent 的理想评测形态：在隔离环境中真实执行任务，用程序化规则检查环境状态，确定性回放行为，并对评测环境主动红队测试以防 Agent 欺骗评分器。

## 主要内容中文译介

EVMbench 评估 Agent 在区块链环境中发现、修补和利用高严重性智能合约漏洞的能力。数据包含来自 40 次审计的 117 个精选漏洞，并补充支付型区块链相关场景。

Benchmark 分为三种模式：

- **Detect**：审计合约仓库，按已知漏洞召回率和相关审计奖励评分。
- **Patch**：修改脆弱合约，在消除可利用性的同时保持预期功能，由自动化测试和 Exploit 检查验证。
- **Exploit**：在沙箱链环境中执行端到端资金攻击，通过交易回放和链上状态程序化评分。

评测 Harness 使用 Rust 构建，负责部署合约、确定性回放 Agent 交易，并限制不安全的 RPC。Exploit 任务运行在隔离的本地 Anvil 环境而非真实网络。团队还编写自定义 Grader，并对环境进行红队测试，查找 Agent 欺骗或绕过评分的方法。

## 方法与评估设计

- **数据集**：117 个漏洞、40 次审计及补充场景。
- **任务类型**：发现、修复、利用三类不同目标。
- **环境**：隔离的本地区块链实例、受限 RPC、可重复部署脚本。
- **评分方式**：漏洞召回、功能测试、Exploit 检查、交易重放和链上状态验证。
- **安全设计**：历史公开漏洞、隔离执行、危险接口限制、Grader 红队测试。
- **可复现性**：通过确定性交易回放减少外部状态和时间变化的影响。

## 对企业级平台的启示

1. 对会写数据、执行代码或调用外部系统的 Agent，应把真实副作用放入隔离沙箱评测。
2. 能由程序判断的结果应优先使用代码 Grader，LLM Judge 只处理不可确定的质量维度。
3. 环境状态、输入镜像、依赖和执行顺序需要版本化，保证失败可重放。
4. 评估器和评测环境也要做安全测试，防止 Reward Hacking、测试污染和权限绕过。
5. 同一业务可以拆为 Detect、Plan/Patch、Execute 等能力模式，分别建立门禁，避免总分掩盖短板。
6. 高风险任务要同时检查目标达成、原有功能保持、安全边界和禁止副作用。

## 局限与阅读警告

EVMbench 聚焦历史智能合约漏洞，本地链状态和单链顺序回放无法覆盖主网时序、跨链与全部现实攻击条件。Detect 模式主要与人工已知漏洞比较，Agent 找到的新问题难以自动判断真假；网络安全具有双重用途，企业使用时必须配套严格授权和隔离。
