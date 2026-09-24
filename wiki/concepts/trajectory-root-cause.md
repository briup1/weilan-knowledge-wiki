---
type: concept
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
sources: [trajdebug, atlas-industrial-tool-agents, microsoft-weavebench, amazon-real-world-agent-evaluation, enterprise-agent-eval-platform-report]
tags: [agent-eval, trajectory, root-cause, debugging]
---

# 轨迹根因

轨迹根因是在失败轨迹里定位最早的关键错误，并看这个错误后来被修复了，还是继续传到最终结果。它回答「是哪一步开始错的」，不是「失败了多少次」。

## 为什么终态分数不够

[[microsoft-weavebench]] 说明只看终态会高估长程 Computer Use：交付物、文件、截图、日志和动作轨迹里可能已经出现伪造证据或硬编码结果。[[atlas-industrial-tool-agents]] 把单次请求再拆开，检查意图、工具选择、参数、调用顺序和结果利用。最终答复看起来对，工具链仍可能在中间走错。

[[amazon-real-world-agent-evaluation]] 把失败分到模型、意图、规划、工具、记忆、异常恢复、最终任务和责任安全。这个分类是责任边界，不是最早错误的定位方法。

## 做法

[[trajdebug]] 给出研究基线：保留多粒度轨迹历史，识别最早关键错误，再判断错误是被后续步骤修好，还是继续传播。[[enterprise-agent-eval-platform-report]] 把这件事放进分析模块：从分数下钻到 First Error Span、证据和负责组件。

长视野要另外看。[[atlas-industrial-tool-agents]] 的跨请求诊断检查目标是否延续、偏好是否保持、历史信息是否被用上。一次请求内的最早错误，解释不了跨会话漂移。

## 边界

- 最早关键错误在多因一果、并发工具或环境故障里不一定唯一。[[trajdebug]] 的 486 条轨迹也不能覆盖所有框架。
- 自动诊断用来加快排查。高风险事故仍要人复核原始 [[agent-trace]]。
- 根因结论可以提议新的 [[evaluation-asset]]，但不能未经审核就改 Ground Truth 或发布门禁。
