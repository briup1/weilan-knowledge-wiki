---
type: synthesis
created: 2026-08-02
updated: 2026-08-02
sources:
  - agent-turn
  - agent-trace
  - orchestration-loop
  - agent-memory-system
  - prompt-building-for-agents
  - output-parsing
  - context-management
  - agent-tool-system
  - mcp
  - state-management
  - validation-loop
  - agent-security
  - error-handling
  - sub-agent-orchestration
  - multi-agent-collaboration
  - claude-code-skills
  - initialization-environment
tags:
  - agent
  - concept-map
  - synthesis
---

# Agent 系统概念地图

一张四级思维导图，从模块（1）到能力（1.1）、方法（1.1.1）、具体技术/算法（1.1.1.1）。每个二级节点链接到对应的 wiki concept 页面。

```mermaid
mindmap
  root((Agent 系统))
    1[交互与可观测]
      1.1[[agent-turn|Agent Turn]]
        1.1.1[业务交互回合]
        1.1.2[预算与持久化边界]
      1.2[[agent-trace|Agent Trace]]
        1.2.1[Trace → Span → Event]
        1.2.2[延迟 / Token / 错误记录]
    2[执行核心]
      2.1[[orchestration-loop|编排循环]]
        2.1.1[ReAct：推理 → 行动 → 观察]
        2.1.2[Token 预算与中断]
        2.1.3[串行 / 并行执行]
    3[认知能力]
      3.1[[agent-memory-system|记忆系统]]
        3.1.1[四类记忆：User / Feedback / Project / Reference]
        3.1.2[本地 Markdown + 索引]
        3.1.3[KAIROS 日志与 /dream 整合]
      3.2[[prompt-building-for-agents|Prompt 构建]]
        3.2.1[洋葱模型分层]
        3.2.2[缓存 vs 临时 system prompt]
        3.2.3[上下文文件优先级]
      3.3[[output-parsing|输出解析]]
        3.3.1[Provider 响应归一化]
        3.3.2[推理 / Tool Calls 提取]
        3.3.3[JSON 修复与孤儿工具保护]
    4[上下文管理]
      4.1[[context-management|上下文压缩]]
        4.1.1[预填充压缩 Preflight]
        4.1.2[响应压缩 Response]
        4.1.3[错误压缩 Error]
      4.2[缓存保护]
        4.2.1[System prompt 隔离]
        4.2.2[缓存前缀固定]
      4.3[工具结果配对]
        4.3.1[孤儿工具调用修复]
    5[工具系统]
      5.1[[agent-tool-system|工具注册与发现]]
        5.1.1[自注册 / 装饰器扫描]
        5.1.2[MCP 动态刷新]
      5.2[Schema 编排]
        5.2.1[Schema 序列化]
        5.2.2[参数强制 / 修复]
      5.3[工具调度]
        5.3.1[Dispatch handler]
        5.3.2[权限钩子]
      5.4[工具裁剪]
        5.4.1[子 Agent 工具集交集]
        5.4.2[黑名单 / 权限组]
      5.5[[mcp|MCP 协议]]
        5.5.1[Client-Server 标准]
        5.5.2[外部服务接入]
    6[状态与持久化]
      6.1[[state-management|运行时状态]]
        6.1.1[内存状态]
        6.1.2[并发控制]
      6.2[持久化状态]
        6.2.1[SQLite / JSONL]
        6.2.2[WAL 与 FTS5]
      6.3[模式演进]
        6.3.1[Schema reconciliation]
    7[安全与验证]
      7.1[[validation-loop|验证循环]]
        7.1.1[Schema 清洗]
        7.1.2[审批状态]
        7.1.3[调用后护栏]
      7.2[[agent-security|安全防护]]
        7.2.1[HARDLINE / DANGEROUS 命令列表]
        7.2.2[SSRF / 路径遍历防护]
        7.2.3[凭证脱敏]
        7.2.4[沙箱后端]
    8[韧性]
      8.1[[error-handling|错误处理]]
        8.1.1[ClassifiedError 分类]
        8.1.2[恢复阶梯]
        8.1.3[指数退避 + 抖动]
        8.1.4[孤儿工具修复]
    9[扩展与协作]
      9.1[[sub-agent-orchestration|子 Agent 编排]]
        9.1.1[delegate_task 触发]
        9.1.2[隔离上下文]
        9.1.3[中断级联]
      9.2[[multi-agent-collaboration|多 Agent 协作]]
        9.2.1[角色分工]
        9.2.2[消息传递]
      9.3[[claude-code-skills|Claude Code Skills]]
        9.3.1[SKILL.md 扩展]
        9.3.2[Slash 命令触发]
    10[运行环境]
      10.1[[initialization-environment|初始化与环境]]
        10.1.1[配置合并]
        10.1.2[Profile 隔离]
        10.1.3[执行后端抽象]
```

## 节点说明

### 1. 交互与可观测
- [[agent-turn]]：一次用户请求到最终响应的完整业务回合。
- [[agent-trace]]：Agent 执行过程的结构化可观测记录。

### 2. 执行核心
- [[orchestration-loop]]：ReAct 主控制流，迭代 LLM 推理 → 工具执行 → 观察。

### 3. 认知能力
- [[agent-memory-system]]：结构化持久记忆。
- [[prompt-building-for-agents]]：洋葱式 system prompt 组装。
- [[output-parsing]]：Provider 响应归一化与防御性修复。

### 4. 上下文管理
- [[context-management]]：上下文窗口的主动经营，包括压缩、缓存保护、孤儿工具修复。

### 5. 工具系统
- [[agent-tool-system]]：工具发现、注册、schema、调度。
- [[mcp]]：标准化工具调用协议。

### 6. 状态与持久化
- [[state-management]]：运行时内存状态与 SQLite/JSONL 持久化。

### 7. 安全与验证
- [[validation-loop]]：执行前后的多层验证门。
- [[agent-security]]：纵深防御与 fail-closed 默认。

### 8. 韧性
- [[error-handling]]：结构化错误分类与恢复阶梯。

### 9. 扩展与协作
- [[sub-agent-orchestration]]：子任务委派与隔离。
- [[multi-agent-collaboration]]：多 Agent 角色分工与消息传递。
- [[claude-code-skills]]：基于 SKILL.md 的能力扩展。

### 10. 运行环境
- [[initialization-environment]]：配置合并、Profile 隔离、执行后端抽象。
