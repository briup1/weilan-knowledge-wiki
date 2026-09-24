---
type: domain
created: 2026-09-17
updated: 2026-09-23
domains: [software-development]
tags: [navigation]
title: "软件开发与 Agent 工程"
scope: knowledge
status: reference
projects: []
products: []
topics: []
source: []
related: []
---

# 软件开发与 Agent 工程

范围：软件设计、实现、测试、部署，以及 Agent 系统工程。默认只检索 `software-development`；需要通用知识管理方法时显式加入 shared。

## 从问题进入

- 理解 Agent 系统：[[wiki/synthesis/agent-concept-map|agent-concept-map]] → [[wiki/synthesis/pi-agent-runtime-architecture|pi-agent-runtime-architecture]] → [[wiki/synthesis/agent-framework-12-dimensions-comparison|agent-framework-12-dimensions-comparison]]。
- 建设企业平台：[[wiki/synthesis/enterprise-agent-platform-landscape|enterprise-agent-platform-landscape]] → [[wiki/concepts/agent-platform-boundary|agent-platform-boundary]] → [[wiki/concepts/human-in-the-loop|human-in-the-loop]] → [[wiki/synthesis/agent-eval-platform-landscape|agent-eval-platform-landscape]]。评测资产见 [[wiki/concepts/evaluation-asset|evaluation-asset]]、[[wiki/concepts/hybrid-agent-evaluator|hybrid-agent-evaluator]]；运行时安全控制见 [[wiki/concepts/agent-guardrails|agent-guardrails]]。
- 构建后端服务：[[wiki/synthesis/fastapi-ecosystem-landscape|fastapi-ecosystem-landscape]] → [[wiki/entities/fastapi|fastapi]] → [[wiki/concepts/async-tasks|async-tasks]] → [[wiki/concepts/containerization|containerization]]。
- 改善 AI 辅助开发：[[wiki/synthesis/claude-code-agent-ecosystem-landscape|claude-code-agent-ecosystem-landscape]] → [[wiki/synthesis/ai-coding-context-stack|ai-coding-context-stack]] → [[wiki/synthesis/knowledge-graph-tools-comparison|knowledge-graph-tools-comparison]]。

## 领域边界

- Agent 的 Runtime、ToolCall、会话持久化属于本域，不因其他领域使用了 AI 就默认注入其查询上下文。
- 同时讨论编程与视频创作的页面可属于两域，例如 [[wiki/entities/remotion|remotion]]；不复制第二份实体页。
- 通用方法从 [[domains/shared|共享知识入口]] 补充；以传播内容为目的时转到 [[domains/ai-media|AI + 自媒体入口]]。

## 检索

```bash
python3 scripts/knowledge/kb.py search --domain software-development --query Agent
```

全量目录见 [[index]]；此页只维护阅读路径。入口更新不代表链接页面中的事实已重新核验。
