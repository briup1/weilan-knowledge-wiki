# Agent 概念地图实现计划

> **For agentic workers:** REQUIRED SUB-LEVEL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于已批准的设计文档，创建 `wiki/synthesis/agent-concept-map.md`，用 Mermaid `mindmap` 呈现 Agent 系统四级概念地图，并同步更新 `index.md` 与 `log.md`。

**Architecture:** 这是一个纯 Markdown 综合产物，不引入代码。核心是一张四级 Mermaid 思维导图，二级节点链接到现有 `wiki/concepts/` 页面；配套更新仓库的索引与时间线。

**Tech Stack:** Markdown、Mermaid、Obsidian wiki-link、`[[page-name]]`。

## Global Constraints

- 所有 `[[page-name]]` 必须指向 `wiki/` 中已存在的页面。
- 新页面必须包含完整的 YAML frontmatter：`type`、`created`、`updated`、`sources`、`tags`。
- `sources` 字段必须列出本图引用的所有 concept 页面 slug。
- 页面标题使用句首字母大写（sentence case）。
- `index.md` 新增项格式：`[[page-name]] —— 一行摘要`。
- `log.md` 记录格式：`## [YYYY-MM-DD] synthesis | <摘要>`。

---

### Task 1: 创建 Agent 概念地图页面

**Files:**
- Create: `wiki/synthesis/agent-concept-map.md`
- Read: `docs/superpowers/specs/2026-08-02-agent-concept-map-design.md`
- Read for reference: `wiki/concepts/orchestration-loop.md`, `wiki/concepts/context-management.md`, `wiki/concepts/agent-tool-system.md`

**Interfaces:**
- Consumes: 设计文档中的节点层级、`wiki/concepts/` 中已存在的页面 slug。
- Produces: `wiki/synthesis/agent-concept-map.md`，包含完整 Mermaid 图与 wiki-link。

- [ ] **Step 1: 编写页面 frontmatter**

在 `wiki/synthesis/agent-concept-map.md` 顶部写入：

```yaml
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
```

- [ ] **Step 2: 编写引言与 Mermaid 思维导图**

在 frontmatter 后写入引言和四级 Mermaid `mindmap`：

```markdown
# Agent 系统概念地图

一张四级思维导图，从模块（1）到能力（1.1）、方法（1.1.1）、具体技术/算法（1.1.1.1）。每个二级节点链接到对应的 wiki concept 页面。

\`\`\`mermaid
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
\`\`\`
```

- [ ] **Step 3: 添加节点说明与链接**

在 Mermaid 图后追加一个按模块分组的说明列表，重复关键 wiki-link，方便 Obsidian 图谱识别连接：

```markdown
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
```

- [ ] **Step 4: 验证文件存在且 frontmatter 完整**

Run:
```bash
python3 -c "
import re
with open('wiki/synthesis/agent-concept-map.md') as f:
    content = f.read()
assert content.startswith('---'), 'Missing frontmatter'
assert 'type: synthesis' in content
assert 'mindmap' in content
assert 'root((Agent 系统))' in content
print('OK')
"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add wiki/synthesis/agent-concept-map.md
git commit -m "feat(synthesis): add agent concept mind map"
```

---

### Task 2: 更新 index.md

**Files:**
- Modify: `index.md`

**Interfaces:**
- Consumes: 新页面 `wiki/synthesis/agent-concept-map.md` 的 slug `agent-concept-map`。
- Produces: `index.md` 的 `## Synthesis` 分类新增一项。

- [ ] **Step 1: 在 Synthesis 分类下新增条目**

在 `index.md` 中找到 `## Synthesis` 区块，在合适位置插入：

```markdown
[[agent-concept-map]] —— Agent 系统四级概念地图：模块 → 能力 → 方法 → 技术
```

建议放在 `agent-framework-12-dimensions-comparison` 附近，因为两者都聚焦 Agent 框架。

- [ ] **Step 2: 验证插入位置正确**

Run:
```bash
grep -n "agent-concept-map" index.md
```

Expected: 输出包含 `agent-concept-map` 且位于 `## Synthesis` 与下一个 `##` 标题之间。

- [ ] **Step 3: Commit**

```bash
git add index.md
git commit -m "docs(index): add agent-concept-map to synthesis section"
```

---

### Task 3: 更新 log.md

**Files:**
- Modify: `log.md`

**Interfaces:**
- Consumes: 本次合成操作的信息。
- Produces: `log.md` 新增一条时间线记录。

- [ ] **Step 1: 在日志开头追加记录**

在 `# Knowledge Forest 日志` 标题后、第一条现有记录前插入：

```markdown
## [2026-08-02] synthesis | 创建 Agent 系统概念地图

**操作**: 创建 `wiki/synthesis/agent-concept-map.md`，用四级 Mermaid 思维导图呈现 Agent 系统概念体系。

**完成项**:
- 新建 `wiki/synthesis/agent-concept-map.md`，覆盖 10 个一级模块、17 个二级概念、四级深度。
- Mermaid 图中二级节点链接到对应 `wiki/concepts/` 页面。
- 更新 `index.md`，在 Synthesis 分类下加入 `[[agent-concept-map]]`。

**规范遵循**:
- 页面 `sources` 字段列出 17 个引用的 concept 页面。
- 所有 `[[page-name]]` 均指向已存在的 wiki 页面。
```

- [ ] **Step 2: 验证追加成功**

Run:
```bash
head -n 20 log.md | grep -c "创建 Agent 系统概念地图"
```

Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add log.md
git commit -m "docs(log): record agent concept map synthesis"
```

---

### Task 4: 死链检查

**Files:**
- Read: `wiki/synthesis/agent-concept-map.md`
- Read: `index.md`

**Interfaces:**
- Consumes: 页面中的 `[[page-name]]` 链接与 `wiki/` 中的实际文件。
- Produces: 死链清单（应为空）。

- [ ] **Step 1: 提取所有 wiki-link 并检查文件存在性**

Run:
```bash
python3 -c "
import re, os
with open('wiki/synthesis/agent-concept-map.md') as f:
    links = set(re.findall(r'\[\[([^\]|]+)', f.read()))
missing = [l for l in links if not os.path.exists(f'wiki/concepts/{l}.md') and not os.path.exists(f'wiki/synthesis/{l}.md') and not os.path.exists(f'wiki/queries/{l}.md') and not os.path.exists(f'wiki/entities/{l}.md')]
assert not missing, f'Missing pages: {missing}'
print(f'Checked {len(links)} links, all OK')
"
```

Expected: `Checked N links, all OK`（N 为实际链接数）

- [ ] **Step 2: 检查 index.md 中的新链接**

Run:
```bash
grep "agent-concept-map" index.md
```

Expected: 输出包含 `[[agent-concept-map]]`。

- [ ] **Step 3: 如有死链则修复，无死链则完成**

若 Step 1 报告缺失页面，回到 Task 1 将对应 `[[page-name]]` 改为普通文本或创建对应页面。

---

## Self-Review

**Spec coverage:**
- [x] 创建 `wiki/synthesis/agent-concept-map.md` → Task 1
- [x] 四级 Mermaid 思维导图 → Task 1 Step 2
- [x] 二级节点链接到现有 wiki concept 页面 → Task 1 Step 2/3
- [x] 更新 `index.md` → Task 2
- [x] 更新 `log.md` → Task 3
- [x] 死链检查 → Task 4

**Placeholder scan:**
- 无 TBD、TODO、"implement later"、"fill in details"。
- 所有 Mermaid 节点、frontmatter、链接均已给出具体值。

**Type consistency:**
- 所有 `[[page-name]]` 使用统一的 Obsidian wiki-link 语法。
- `sources` 字段中的 slug 与正文中链接的 slug 一致。

## Execution Options

Plan complete and saved to `docs/superpowers/plans/2026-08-02-agent-concept-map.md`.

Two execution options:

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

Which approach do you prefer?
