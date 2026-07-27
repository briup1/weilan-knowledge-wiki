# Agent 上下文技术分享 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a 45–60 minute internal tech talk deck, speaker notes, diagrams, and a CTA template for backend/full-stack engineers on Agent context management.

**Architecture:** Store all presentation materials in `drafts/agent-context-sharing/` as Markdown files. `slides.md` is the Marp-compatible slide source; `speaker-notes.md` holds timing and spoken content; the Mermaid diagram used in Section 2 lives inside `02-context-anatomy.md`. All content ties back to the four-layer context anatomy model defined in the design spec.

**Tech Stack:** Markdown, Mermaid, optional Marp/Obsidian for slide rendering.

## Global Constraints

- Duration: 45–60 min; target 50–57 min of content plus 3–5 min buffer.
- Audience: backend/full-stack engineers without prior Agent experience.
- Depth: no KV Cache implementation details; no complex tool-matching algorithms; no multi-Agent collaboration.
- Every optimization technique must be mapped to one of the four context layers.
- CTA must be project-agnostic but immediately actionable for the team.
- Prefer existing wiki pages as fact sources: `[[context-management]]`, `[[prompt-building-for-agents]]`, `[[agent-tool-system]]`, `[[agent-memory-system]]`.

---

## File Structure

```
drafts/agent-context-sharing/
├── README.md                        # project status, goal, links
├── 01-opening.md                    # hook story + learning objectives
├── 02-context-anatomy.md            # four-layer model + Mermaid diagram
├── 03-static-prefix.md              # system/tool/skill prompt optimization
├── 04-trajectory-compression.md     # trajectory & large tool-output compression
├── 05-memory-design.md              # memory as long-term context
├── 06-closing-cta.md                # recap + CTA template
├── slides.md                        # assembled Marp slide deck
├── speaker-notes.md                 # per-slide timing and spoken script
└── dry-run-checklist.md             # timing/cut list for rehearsal
```

---

### Task 1: Scaffold presentation directory and README

**Files:**
- Create: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Produces: project metadata, status, links to design spec and wiki sources used by later tasks.

- [ ] **Step 1: Create directory and README**

  Create `drafts/agent-context-sharing/README.md` with the following exact structure:

  ```markdown
  # Agent 上下文技术分享

  **状态**: `writing`

  ## 目标

  为后端/全栈工程师提供一次 45–60 分钟的 Agent 上下文管理入门分享，建立「上下文剖面图」心智模型，并引出压缩与记忆设计的落地价值。

  ## 与 wiki 的关系

  - [[context-management]]
  - [[prompt-building-for-agents]]
  - [[agent-tool-system]]
  - [[agent-memory-system]]

  ## 设计文档

  - `docs/superpowers/specs/2026-07-27-agent-context-sharing-design.md`

  ## 当前进度

  - [ ] 开场与目标
  - [ ] 上下文剖面图
  - [ ] 静态前缀优化
  - [ ] 轨迹与工具输出压缩
  - [ ] 记忆设计
  - [ ] 收束与 CTA
  - [ ] 幻灯片与讲稿整合
  - [ ] 试讲与裁剪清单
  ```

- [ ] **Step 2: Verify README renders correctly**

  Read the file and confirm:
  - All wiki-links use Obsidian `[[...]]` syntax.
  - Status is `writing`.
  - Relative path to design doc is correct.

- [ ] **Step 3: Commit**

  ```bash
  git add drafts/agent-context-sharing/README.md
  git commit -m "chore: scaffold agent-context-sharing presentation"
  ```

---

### Task 2: Opening hook and learning objectives

**Files:**
- Create: `drafts/agent-context-sharing/01-opening.md`
- Modify: `drafts/agent-context-sharing/README.md` (progress checkbox)

**Interfaces:**
- Consumes: design spec Section 1 (opening) and Section 3 (success criteria).
- Produces: a concrete hook story and three learning objectives reused in `slides.md` later.

- [ ] **Step 1: Write the opening section**

  Create `drafts/agent-context-sharing/01-opening.md` with this exact content:

  ```markdown
  # 开场钩子与学习目标的

  ## 故事（3 min）

  我们给 Agent 接了一个「查订单」工具。工具返回了一个 4000+ token 的 JSON，里面包含订单的每一个字段。下一轮 Agent 需要判断「要不要退款」，但它把「用户原始诉求」那部分上下文挤出去了，结果给出了完全无关的建议。

  问题不是工具错了，而是我们没把上下文当成有限资源来经营。

  ## 今天的三个带走

  1. 能画出一次 Agent 推理的上下文剖面图。
  2. 知道静态前缀、轨迹、动态提示词、状态栏分别该怎么优化。
  3. 能为自己团队的 Agent 功能设计一个 2 周内可验证的压缩/记忆实验。
  ```

- [ ] **Step 2: Update README progress**

  In `drafts/agent-context-sharing/README.md`, mark `- [ ] 开场与目标` as `- [x] 开场与目标`.

- [ ] **Step 3: Verify and commit**

  Read `01-opening.md` and confirm the story is under 150 words and the three objectives match the design spec.

  ```bash
  git add drafts/agent-context-sharing/01-opening.md drafts/agent-context-sharing/README.md
  git commit -m "feat(opening): add hook story and learning objectives"
  ```

---

### Task 3: Context anatomy diagram

**Files:**
- Create: `drafts/agent-context-sharing/02-context-anatomy.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: design spec Section 2 (context anatomy) and handwritten note categories.
- Produces: a Mermaid diagram and four-layer explanations used in `slides.md`.

- [ ] **Step 1: Write the anatomy section**

  Create `drafts/agent-context-sharing/02-context-anatomy.md`:

  ```markdown
  # 上下文剖面图（12–15 min）

  一次 Agent 推理时，上下文窗口大致可以看成四层：

  ```mermaid
  ---
  config:
    theme: base
  ---
  flowchart TD
    A[静态前缀<br/>system prompt + claude.md + skill.md] --> B[轨迹<br/>user / assistant / tool / tool_result]
    B --> C[动态提示词<br/>skill 详细指令]
    C --> D[状态栏<br/>活跃状态 / 变量]
  ```

  ## 静态前缀

  每次请求都会带上的固定部分。通常最大、最稳定，也最值得一次性优化好。

  ## 轨迹

  多轮对话的历史。Agent 每走一步，历史就被重新塞回去，因此最容易膨胀。

  ## 动态提示词

  运行时根据用户意图注入的某个 skill 的详细说明。只在该 skill 被触发时出现。

  ## 状态栏

  当前会话中的关键变量，例如用户身份、任务阶段、已确认字段。

  ## 一句话总结

  上下文 = 固定前缀 + 历史轨迹 + 动态注入 + 当前状态。
  ```

- [ ] **Step 2: Update README progress**

  Mark `- [ ] 上下文剖面图` as `- [x] 上下文剖面图`.

- [ ] **Step 3: Verify diagram renders**

  Open `02-context-anatomy.md` in Obsidian or a Mermaid renderer and confirm the diagram shows four stacked layers without syntax errors.

- [ ] **Step 4: Commit**

  ```bash
  git add drafts/agent-context-sharing/02-context-anatomy.md drafts/agent-context-sharing/README.md
  git commit -m "feat(anatomy): add four-layer context model and diagram"
  ```

---

### Task 4: Static prefix optimization

**Files:**
- Create: `drafts/agent-context-sharing/03-static-prefix.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: design spec Section 3, `[[prompt-building-for-agents]]`, `[[agent-tool-system]]`.
- Produces: concrete System Prompt and Tool/Skill Prompt design rules used in slides.

- [ ] **Step 1: Write static prefix content**

  Create `drafts/agent-context-sharing/03-static-prefix.md`:

  ```markdown
  # 静态前缀优化（10 min）

  ## System Prompt 设计

  把它想象成新员工的「入职手册」，要回答四个问题：

  1. 你是谁？（角色）
  2. 不能做什么？（约束）
  3. 输出要什么格式？（格式）
  4. 给一两个正面示例。（示例）

  示例结构：

  ```text
  你是订单客服助手。
  你只能回答与订单、退款、物流相关的问题。
  输出必须是 JSON：{"action": "...", "reason": "..."}
  示例：用户问"我想退款" -> {"action": "refund", "reason": "用户主动申请"}
  ```

  ## Skill / Tool Prompt 设计

  每个工具的说明要解决：

  1. 什么时候调用？
  2. 每个参数是什么意思？
  3. 有没有边界条件？
  4. 能否用更通用的描述替代多个定制工具？

  反模式：为「查订单」「查物流」「查库存」各写一个工具。
  更好做法：一个「查询后端 API」工具，通过 `endpoint` 参数区分场景。
  ```

- [ ] **Step 2: Update README progress**

  Mark `- [ ] 静态前缀优化` as `- [x] 静态前缀优化`.

- [ ] **Step 3: Verify content**

  Confirm the file contains exactly one System Prompt example and one Tool Prompt anti-pattern/example pair.

- [ ] **Step 4: Commit**

  ```bash
  git add drafts/agent-context-sharing/03-static-prefix.md drafts/agent-context-sharing/README.md
  git commit -m "feat(static-prefix): add system and tool prompt design rules"
  ```

---

### Task 5: Trajectory and tool-output compression

**Files:**
- Create: `drafts/agent-context-sharing/04-trajectory-compression.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: design spec Section 4, handwritten notes on compression, `[[context-management]]`.
- Produces: compression strategies mapped to trajectory layer.

- [ ] **Step 1: Write compression content**

  Create `drafts/agent-context-sharing/04-trajectory-compression.md`:

  ```markdown
  # 轨迹与工具输出压缩（12 min）

  ## 为什么轨迹会膨胀？

  Agent 每走一步，user / assistant / tool / tool_result 都会被重新送入下一轮。token 数随步数线性甚至超线性增长。

  ## 压缩对象

  1. 过时的 assistant 推理过程（保留结论，省略中间尝试）
  2.  oversized 的 tool_result
  3. 重复的 system/tool 说明（已放在静态前缀里的不必重复）

  ## 压缩时机

  - 单轮内：工具返回后立即压缩。
  - 跨轮：每 N 轮或 token 达到阈值时做一次总结。

  ## 工具返回大量数据的处理

  1. **提取**：只保留 Agent 下一步需要的字段。
  2. **指向**：保留摘要，原始数据放到可检索的位置。
  3. **分段**：把大结果拆成多个小查询，按需调用。

  ## turn / trace 概念（点到为止）

  - turn：一次完整的用户-Agent 交互回合。
  - trace：整个任务执行过程的结构化记录，用于观测而非全部塞进 prompt。
  ```

- [ ] **Step 2: Update README progress**

  Mark `- [ ] 轨迹与工具输出压缩` as `- [x] 轨迹与工具输出压缩`.

- [ ] **Step 3: Verify and commit**

  Confirm the file has three compression objects, two timing strategies, and three tool-output techniques.

  ```bash
  git add drafts/agent-context-sharing/04-trajectory-compression.md drafts/agent-context-sharing/README.md
  git commit -m "feat(trajectory): add compression strategies and turn/trace intro"
  ```

---

### Task 6: Memory as long-term context

**Files:**
- Create: `drafts/agent-context-sharing/05-memory-design.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: design spec Section 5, `[[agent-memory-system]]`.
- Produces: a three-layer memory model used in slides.

- [ ] **Step 1: Write memory design content**

  Create `drafts/agent-context-sharing/05-memory-design.md`:

  ```markdown
  # 记忆设计（8–10 min）

  ## 核心观点

  当上下文窗口装不下时，记忆系统就是「窗口外的长期上下文」。

  ## 三层记忆

  1. **工作记忆**：当前会话中的短期变量，例如用户刚确认的收货地址。
  2. **Episodic 记忆**：近期发生过的事情，例如过去 7 天的对话摘要。
  3. **语义记忆**：长期稳定的知识，例如用户偏好、产品规则。

  ## 与上下文的关系

  - 工作记忆通常直接放进「状态栏」。
  - Episodic/语义记忆通过检索按需注入动态提示词。
  - 不是所有记忆都要塞进 prompt；先检索，再决定放什么。

  ## 一句话总结

  上下文管理解决「当下能装多少」，记忆设计解决「长期需要记得什么」。
  ```

- [ ] **Step 2: Update README progress**

  Mark `- [ ] 记忆设计` as `- [x] 记忆设计`.

- [ ] **Step 3: Verify and commit**

  Confirm the file defines three memory layers and maps each to the context anatomy model.

  ```bash
  git add drafts/agent-context-sharing/05-memory-design.md drafts/agent-context-sharing/README.md
  git commit -m "feat(memory): add three-layer memory model"
  ```

---

### Task 7: Closing CTA and recap

**Files:**
- Create: `drafts/agent-context-sharing/06-closing-cta.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: design spec Section 6 and Section 8 (CTA template).
- Produces: the closing recap and an actionable CTA template.

- [ ] **Step 1: Write closing content**

  Create `drafts/agent-context-sharing/06-closing-cta.md`:

  ```markdown
  # 收束与落地 CTA（5 min）

  ## 一句话回顾

  Agent 上下文 = 静态前缀 + 轨迹 + 动态提示词 + 状态栏。优化的本质是：在有限的 token 预算里，放最相关的信息。

  ## 带走清单

  1. 选出团队当前或 upcoming 的一个 Agent 功能。
  2. 用四层模型画出它的上下文剖面。
  3. 找出最大的 token 消耗项。
  4. 设计一个 2 周内可验证的压缩或记忆化实验。
  5. 记录基线（token 数、延迟、准确率）和实验结果。

  ## 示例实验

  > 把我们的「查订单」工具返回从全量 JSON 改为只返回 5 个关键字段，观察 token 下降和准确率变化。
  ```

- [ ] **Step 2: Update README progress**

  Mark `- [ ] 收束与 CTA` as `- [x] 收束与 CTA`.

- [ ] **Step 3: Verify and commit**

  Confirm the CTA template has exactly five steps and one concrete example experiment.

  ```bash
  git add drafts/agent-context-sharing/06-closing-cta.md drafts/agent-context-sharing/README.md
  git commit -m "feat(closing): add recap and CTA template"
  ```

---

### Task 8: Assemble slide deck and speaker notes

**Files:**
- Create: `drafts/agent-context-sharing/slides.md`
- Create: `drafts/agent-context-sharing/speaker-notes.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: `01-opening.md` through `06-closing-cta.md`.
- Produces: the final presentation source and timed speaker script.

- [ ] **Step 1: Assemble slides**

  Create `drafts/agent-context-sharing/slides.md` with a Marp header and one slide per major heading from the section files. Each slide should contain:

  - A title matching the section heading.
  - At most 3 bullet points or one diagram reference.
  - A small footer note with the intended duration, e.g. `<!-- 5 min -->`.

  Example first three slides:

  ```markdown
  ---
  marp: true
  theme: default
  ---

  # Agent 上下文：把 token 当有限资源来经营

  ---

  ## 一个让 Agent 突然变傻的故事

  - 工具返回 4000+ token 的 JSON
  - 关键用户诉求被挤出上下文
  - 问题：没把上下文当资源经营

  <!-- 3 min -->

  ---

  ## 今天三个带走

  1. 画出 Agent 上下文剖面图
  2. 知道四层模型分别怎么优化
  3. 设计一个 2 周内可验证的压缩/记忆实验

  <!-- 2 min -->
  ```

- [ ] **Step 2: Write speaker notes**

  Create `drafts/agent-context-sharing/speaker-notes.md` that mirrors the slide sequence and adds:

  - The spoken transition sentence between slides.
  - A timing annotation per slide.
  - A "backup cut" note for any slide that can be skipped if running over time.

- [ ] **Step 3: Update README progress**

  Mark `- [ ] 幻灯片与讲稿整合` as `- [x] 幻灯片与讲稿整合`.

- [ ] **Step 4: Verify and commit**

  Confirm `slides.md` has a Marp header, one slide per section, and all timing comments sum to 50–57 minutes.

  ```bash
  git add drafts/agent-context-sharing/slides.md drafts/agent-context-sharing/speaker-notes.md drafts/agent-context-sharing/README.md
  git commit -m "feat(deck): assemble slides and speaker notes"
  ```

---

### Task 9: Dry-run checklist and backup cuts

**Files:**
- Create: `drafts/agent-context-sharing/dry-run-checklist.md`
- Modify: `drafts/agent-context-sharing/README.md`

**Interfaces:**
- Consumes: `slides.md` and `speaker-notes.md`.
- Produces: a rehearsal runbook.

- [ ] **Step 1: Write the runbook**

  Create `drafts/agent-context-sharing/dry-run-checklist.md`:

  ```markdown
  # 试讲与裁剪清单

  ## 试讲检查项

  - [ ] 总时长控制在 50–57 分钟
  - [ ] Section 2 的四层模型能在白板上画出来
  - [ ] 每个优化技巧都能说清它作用于哪一层
  - [ ] CTA 能在 2 分钟内讲完
  - [ ] 至少准备 1 个听众可能问的问题及答案

  ## 超时裁剪顺序（从后往前砍）

  1. 删除 `turn / trace` 详细解释，只保留一句话。
  2. 删除工具返回压缩的「分段」策略，只保留「提取」。
  3. 删除记忆设计中的 episodic 层，只保留工作记忆 + 语义记忆。
  4. 删除开场故事的细节，只保留核心冲突。
  ```

- [ ] **Step 2: Update README progress**

  Mark `- [ ] 试讲与裁剪清单` as `- [x] 试讲与裁剪清单`.

- [ ] **Step 3: Verify and commit**

  Confirm the checklist has at least five rehearsal items and four ordered backup cuts.

  ```bash
  git add drafts/agent-context-sharing/dry-run-checklist.md drafts/agent-context-sharing/README.md
  git commit -m "feat(runbook): add dry-run checklist and cut list"
  ```

---

## Self-Review

Run this checklist after the plan is written:

1. **Spec coverage:**
   - Opening hook → Task 2
   - Context anatomy → Task 3
   - Static prefix optimization → Task 4
   - Trajectory compression → Task 5
   - Memory design → Task 6
   - Closing CTA → Task 7
   - Timing/buffer → Tasks 8–9
   - Gaps: none.

2. **Placeholder scan:**
   - No TBD/TODO/fill-in-details.
   - All file paths are explicit.
   - All commits include concrete file lists.

3. **Type consistency:**
   - N/A for non-code presentation; all cross-file references use the `drafts/agent-context-sharing/` prefix.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-27-agent-context-sharing-plan.md`.

Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

Which approach do you want?
