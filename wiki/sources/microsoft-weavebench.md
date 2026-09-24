---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/agent-eval-2026/international/12-microsoft-weavebench.md
tags: [agent-eval, computer-use, trajectory]
---

# Microsoft Research：WeaveBench 长程混合界面 Computer Use 评测

## 摘要

WeaveBench 评的是同时使用 GUI、浏览器、CLI、代码和文件的长程 Computer Use。官方页只精确到 2026 年 6 月。核心发现是只看终态会明显高估 Agent。

## 核心要点

- 要同时检查交付物、文件、截图、日志和动作轨迹，而不是只看任务最后是否显示成功。
- 要识别捷径：伪造证据、硬编码结果、绕开环境。
- 轨迹 Judge 会把合法的高效路径误判成捷径，所以 Judge 自己也要校准。

## 局限

环境是 Ubuntu 加上 CLI Runtime，不能直接代表 Windows、移动端或企业 SaaS 的全部交互。

## 关联

- [[trajectory-root-cause]]
- [[hybrid-agent-evaluator]]
- [[enterprise-agent-eval-platform-report]]
- [[agent-eval-platform-landscape]]

## 原始文件

- [原始文件](../../raw/archive/agent-eval-2026/international/12-microsoft-weavebench.md)
