---
type: research-source
region: international
publication_date: 2026-06-01
publication_date_precision: month
collected: 2026-09-01
source_type: research-paper
organization: Microsoft Research
original_language: en
original_url: https://www.microsoft.com/en-us/research/publication/weavebench-a-long-horizon-real-world-benchmark-for-computer-use-agents-with-hybrid-interfaces/
tags: [agent-eval, computer-use, long-horizon, trajectory-judge, hybrid-interface]
---

# Microsoft Research：WeaveBench 长程混合界面 Computer Use 评测

## 资料信息

- 原文标题：WeaveBench: A Long-Horizon, Real-World Benchmark for Computer-Use Agents with Hybrid Interfaces
- 发布机构：Microsoft Research
- 发布日期：2026-06（官方页仅精确到月份，frontmatter 以月初占位并另行标注）
- 原文链接：https://www.microsoft.com/en-us/research/publication/weavebench-a-long-horizon-real-world-benchmark-for-computer-use-agents-with-hybrid-interfaces/
- 资料类型：研究论文 / Benchmark

## 为什么值得阅读

企业 Computer Use Agent 往往同时操作 GUI、浏览器、CLI、代码和文件，而传统 Benchmark 常将它们拆开。WeaveBench 证明只看终态会显著高估能力，必须检查交付物、文件、截图、日志和动作轨迹，并主动识别伪造证据或硬编码结果等捷径行为。

## 主要内容中文译介

WeaveBench 包含 8 个真实工作领域中的 114 个长程任务，题目来自真实用户请求，并使用可公开验证的产物。每个任务要求 Agent 在单条轨迹中组合 GUI 观察与操作、CLI 或代码执行，而不是只完成一个隔离的点击或命令。

评测运行在真实 Ubuntu 桌面和已部署的 CLI Agent Runtime 中，通过最小桌面控制插件补充 GUI 能力。配套的轨迹感知 Judge 不只判断最终文件是否存在，还检查交付物内容、文件系统、截图、日志和动作记录，并识别伪造视觉证据、硬编码指标等绕过任务的行为。

论文报告的最佳模型—Runtime 组合通过率仅为 41.2%，说明长程跨界面编排仍未成熟。更关键的是，单纯按 Outcome 评分会明显高估 Agent 表现：终态看似正确，并不代表过程真实、合规、完整或可复现。

## 方法与评估设计

- **任务规模**：114 项任务，覆盖 8 个真实工作领域。
- **环境**：Ubuntu 桌面、CLI Agent Runtime、桌面控制插件、文件和外部工具。
- **交互模态**：GUI、CLI、代码、浏览器、文件、截图和日志。
- **评分证据**：最终交付物、环境状态、文件、截图、日志与完整动作轨迹。
- **反作弊**：检测伪造视觉证据、硬编码指标和绕开真实执行的捷径。
- **核心结论**：长程混合接口任务远未饱和，Outcome-only 评分存在系统性高估。

## 对企业级平台的启示

1. 对 Computer Use 和办公 Agent，统一 Trace 必须跨越浏览器、桌面、终端、代码和文件系统。
2. 评分器要验证“产物 + 过程证据 + 环境状态”，高风险任务不能只看最终文本或文件存在性。
3. 平台需要沙箱快照、屏幕录像/截图、命令日志和文件 Diff，以支持重放和争议审计。
4. 应建立反作弊规则，识别伪造截图、硬编码结果、绕过实际系统和污染评测环境。
5. 长程任务需要阶段性检查点和分段诊断，避免只在最后给出一个不可解释的失败分。

## 局限与阅读警告

官方页面只标注 2026 年 6 月，未提供精确日期。Benchmark 聚焦 Ubuntu 和 CLI Runtime 增强的桌面环境，不能直接代表 Windows、移动端或企业 SaaS 的全部交互；轨迹 Judge 本身也需要持续校准，避免把合法的高效路径误判为捷径。
