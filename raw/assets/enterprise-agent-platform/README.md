# 企业级 Agent 平台工程：关键原文集

> 状态：待摄取。本目录仅保存上游原文与来源信息，尚未生成或更新任何 `wiki/` 页面。

## 来源

- 网站：https://datagallery-lab.github.io/enterprise_agent_platform/
- 仓库：https://github.com/datagallery-lab/enterprise_agent_platform
- 固定提交：[`e5d97a66c467045413fff692d28fd2c401503029`](https://github.com/datagallery-lab/enterprise_agent_platform/commit/e5d97a66c467045413fff692d28fd2c401503029)
- 提交时间：2026-07-03
- 许可证：[Apache License 2.0](LICENSE)
- 下载范围：19 篇中文 Markdown 原文

## 筛选口径

保留企业级 Agent 平台的核心工程主线：

```text
平台边界与参考架构
  ↓
Runtime → Tool Registry / MCP → Planner / Workflow → Memory / 多 Agent / 协议 / HITL
  ↓
可观测性 → 离线与在线评估 → 成本与 SLO
  ↓
安全攻防与 Guardrails
```

暂不包含模型、数据基础设施、RAG、DataAgent、部署、前端、组织、案例和附录等专题。

## 文章清单

### 平台边界与架构

1. [第2章 企业级 Agent 平台的边界](docs/part01-overview/ch/ch02-agent.md)
2. [第4章 全书地图：平台参考架构与阅读路径](docs/part01-overview/ch/ch04.md)

### Agent 核心能力

3. [第22章 Agent Runtime](docs/part05-agent-capabilities/ch/ch22-agent-runtime.md)
4. [第23章 Tool Registry & Function Calling](docs/part05-agent-capabilities/ch/ch23-tool-registry-function-calling.md)
5. [第24章 MCP 与企业工具生态](docs/part05-agent-capabilities/ch/ch24-mcp.md)
6. [第25章 Planner 与编排模式](docs/part05-agent-capabilities/ch/ch25-planner.md)
7. [第26章 Agentic Workflow](docs/part05-agent-capabilities/ch/ch26-agentic-workflow.md)
8. [第27章 Memory 系统](docs/part05-agent-capabilities/ch/ch27-memory.md)
9. [第28章 多 Agent 协作](docs/part05-agent-capabilities/ch/ch28-agent.md)
10. [第29章 Agent 协议与标准](docs/part05-agent-capabilities/ch/ch29-agent.md)
11. [第30章 Human-in-the-loop 与长任务](docs/part05-agent-capabilities/ch/ch30-human-in-the-loop.md)
12. [第31章 框架横向对标](docs/part05-agent-capabilities/ch/ch31.md)

### 可观测性、评估与成本

13. [第38章 Agent 可观测性与运行诊断](docs/part07-observability-eval/ch/ch38-trace.md)
14. [第39章 企业级 DataAgent 评测体系设计与 Benchmark 构建](docs/part07-observability-eval/ch/ch39-dataagent-eval-benchmark.md)
15. [第40章 在线评测、模型裁判与持续优化](docs/part07-observability-eval/ch/ch40-llm-as-judge.md)
16. [第41章 成本治理与缓存优化](docs/part07-observability-eval/ch/ch41-cost-governance-cache.md)
17. [第42章 SLO 管理、限流与系统韧性](docs/part07-observability-eval/ch/ch42-slo.md)

### 安全与治理

18. [第50章 安全与攻防](docs/part10-security-org/ch/ch50.md)
19. [第51章 Guardrails 与内容安全](docs/part10-security-org/ch/ch51-guardrails.md)

## 本地资料边界

- 19 篇正文保持上游原文，不做摘要、改写或 frontmatter 注入。
- 原文中的 37 个图片引用仍指向上游目录结构；本轮仅下载 Markdown，未下载图片。
- 摄取时再将本目录移入 `raw/archive/`，并按仓库流程创建 source、entity、concept 与 synthesis 页面。
