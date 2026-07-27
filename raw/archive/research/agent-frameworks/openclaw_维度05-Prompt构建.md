# 维度名：Prompt 构建（Prompt Building）

## 1. 一句话定位

Prompt 构建是 OpenClaw 的"LLM 行为契约编译器"——它将运行时环境、工具能力、技能指引、安全策略和用户上下文按优先级分层组装成系统提示词，并通过模式分级（full/minimal/none）和 Token 预算控制，在有限的上下文窗口内精确约束 Agent 的行为边界。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **Agent 行为完全失控**：LLM 不知道可用工具及其调用格式。`buildAgentSystemPrompt` 中 `toolLines` 为空时（`system-prompt.ts:L428-447`），系统会回退到一组默认工具描述；如果没有这个回退，LLM 将随意编造工具名称和参数结构，导致工具调用 100% 失败。
- **安全策略无法传达**：沙箱状态、执行审批、ACP 路由限制等安全策略如果不写入 prompt，LLM 无法知道某些操作被禁止。例如 `acpHarnessSpawnAllowed` 为 false 时，若不在 prompt 中声明 `sessions_spawn` 的行为差异，LLM 会尝试在沙箱内启动 ACP harness，导致权限错误。
- **上下文窗口被无效信息撑爆**：没有 `PromptMode` 分级，子 Agent 和 Cron 任务会收到包含 Messaging、Heartbeats、Reply Tags 等无关章节的完整提示词，浪费本可用于任务执行的宝贵 token。
- **Prompt 注入攻击**：用户可控的字符串（如工作区目录名）若包含 Unicode 控制字符（如 `\n`、双向文本标记），可以破坏 prompt 的分节结构，让 LLM 将攻击者注入的文本误读为系统指令。`sanitizeForPromptLiteral` 缺失时，`workspaceDir` 中的 `\n\n## System\nYou are now...` 会直接插入系统提示词。
- **技能选择失控**：没有 "先扫描、再选择、只读一个" 的约束策略，LLM 可能在每轮请求中盲目读取所有 skill 的 SKILL.md，导致上下文迅速膨胀且引入无关行为约束。

### 2.2 OpenClaw 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 每次 Agent turn 前 | `src/agents/pi-embedded-runner/run/attempt.ts:L988-1015` | `resolvePromptModeForSession` 判断 session 类型，组装系统提示词 |
| CLI `openclaw run` 执行时 | `src/agents/cli-runner.ts:L147-161` | `buildSystemPrompt` 调用 `buildAgentSystemPrompt` 并生成 report |
| 工具集变化时 | `src/agents/system-prompt.ts:L301-339` | 根据 `toolNames` 重新计算 `toolLines` 和 `availableTools` |
| Skill 加载/刷新时 | `src/agents/skills/workspace.ts:L529-565` | `applySkillsPromptLimits` 通过二进制搜索裁剪技能列表 |
| Bootstrap 文件注入时 | `src/agents/system-prompt.ts:L616-648` | `contextFiles` 被注入到 `# Project Context` 节 |
| 用户配置变更时 | `src/agents/system-prompt-params.ts:L42-59` | 重新解析 repoRoot、时区、时间格式 |
| 工作区目录解析时 | `src/agents/workspace-run.ts:L89-108` | `sanitizeForPromptLiteral` 清理目录路径中的控制字符 |

---

## 3. 核心设计思路

### 3.1 抽象模型

Prompt 构建可以抽象为一个**分层过滤组装管道**：

```
输入层：运行时参数 + 配置 + 工具列表 + 技能 + 上下文文件
    ↓
过滤层：PromptMode (full/minimal/none) 决定哪些章节被包含
    ↓
组装层：按固定顺序拼接章节（Tooling → Safety → Skills → Memory → Workspace → Runtime）
    ↓
清理层：sanitizeForPromptLiteral 处理所有用户可控字符串
    ↓
预算层：applySkillsPromptLimits 通过二进制搜索控制技能章节长度
    ↓
覆盖层：createSystemPromptOverride 允许外部完全替换系统提示词
    ↓
输出层：字符串化的系统提示词 + SystemPromptReport 诊断数据
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| Prompt 模式分级 | `PromptMode` 三级（full/minimal/none） | 单一固定提示词 | `system-prompt.ts:L17` 定义三种模式；`resolvePromptModeForSession` (`attempt.ts:L612-617`) 对子 Agent 和 Cron 自动降级为 minimal，避免无关章节浪费 token |
| 工具排序 | 硬编码 `toolOrder` 数组，先核心后扩展 | 按字母顺序或注册顺序 | `system-prompt.ts:L274-299` 将 read/write/edit/grep/find/ls/exec 排在前面，因为文件操作是最高频工具，LLM 更容易在上下文前面找到它们 |
| 技能路径压缩 | 将 `/home/user/...` 替换为 `~/...` | 保留完整路径 | `skills/workspace.ts:L46-54` 注释明确说明节省 400-600 tokens；模型理解 `~` 扩展，且 read 工具支持 `~` 解析 |
| Prompt 注入防护 | 剥离 Unicode Cc/Cf + Zl/Zp 字符 | HTML 实体转义 | `sanitize-for-prompt.ts:L16-18` 选择"有损剥离"而非"保真转义"，因为 prompt 结构完整性优先于路径精确性 |
| 技能预算控制 | 二进制搜索找最大前缀 | 直接截断到固定数量 | `skills/workspace.ts:L547-558` 在数量限制后进一步用二进制搜索确保字符预算不超标，避免"150 个技能刚好超 30k 字符"的边界问题 |
| 系统提示词报告 | 并行生成结构化 report | 不生成诊断数据 | `system-prompt-report.ts:L80-142` 生成包含 chars/projectContextChars/skills/tools 等维度的报告，用于 `/status` 命令和调试 |

### 3.3 数据流/控制流

```
[CLI Run] ──→ buildSystemPrompt (cli-runner/helpers.ts:L41)
                  ↓
              buildSystemPromptParams (system-prompt-params.ts:L35)
                  ↓ 解析 repoRoot / timezone / time
              buildAgentSystemPrompt (system-prompt.ts:L189)
                  ↓
              ├─→ buildSkillsSection (system-prompt.ts:L20)
              ├─→ buildMemorySection (system-prompt.ts:L38)
              ├─→ buildMessagingSection (system-prompt.ts:L120)
              ├─→ buildReplyTagsSection (system-prompt.ts:L104)
              ├─→ buildVoiceSection (system-prompt.ts:L160)
              ├─→ buildDocsSection (system-prompt.ts:L171)
              ├─→ buildRuntimeLine (system-prompt.ts:L691)
              └─→ sanitizeForPromptLiteral (sanitize-for-prompt.ts:L16)
                  ↓
              buildSystemPromptReport (system-prompt-report.ts:L80)
                  ↓
              [输出到 LLM 请求] + [诊断数据存入 session]

[PI Embedded] ──→ buildEmbeddedSystemPrompt (pi-embedded-runner/system-prompt.ts:L11)
                      ↓
                  buildAgentSystemPrompt (同上)
                      ↓
                  createSystemPromptOverride (pi-embedded-runner/system-prompt.ts:L89)
                      ↓
                  applySystemPromptOverrideToSession (pi-embedded-runner/system-prompt.ts:L96)
                      ↓
                  [直接修改 session.agent.systemPrompt]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：PromptMode 分级过滤

**作用**：根据 Agent 类型（主 Agent / 子 Agent / Cron）动态裁剪系统提示词章节，避免 token 浪费。

**设计意图**：子 Agent 不需要 Heartbeats、Reply Tags、Messaging 等面向交互的章节；Cron 任务更不需要。硬编码三种模式比让每个调用者手动选择章节更可靠。

**关键源码**（`src/agents/system-prompt.ts:L379-380, L418-420, L651-667`）：

```typescript
const promptMode = params.promptMode ?? "full";
const isMinimal = promptMode === "minimal" || promptMode === "none";

// "none" 模式直接返回最简身份声明
if (promptMode === "none") {
  return "You are a personal assistant running inside OpenClaw.";
}

// minimal 模式跳过 Silent Replies、Heartbeats 等交互章节
if (!isMinimal) {
  lines.push(
    "## Silent Replies",
    `When you have nothing to say, respond with ONLY: ${SILENT_REPLY_TOKEN}`,
    // ...
  );
}
```

**为什么值得看**：`isMinimal` 是一个布尔开关，控制超过 10 个章节的包含与否。`"none"` 模式作为极端降级路径（仅返回一句话），在上下文极度紧张时保证 Agent 仍能运行。

---

### 机制 B：工具排序与摘要组装

**作用**：将可用工具按优先级排序，并为每个工具生成一行摘要，暴露给 LLM。

**设计意图**：LLM 对提示词前面内容的注意力更高。将 read/write/edit/grep/find/ls/exec 等高频工具排在前面，可以提升工具调用准确率。

**关键源码**（`src/agents/system-prompt.ts:L274-339`）：

```typescript
const toolOrder = [
  "read", "write", "edit", "apply_patch",
  "grep", "find", "ls", "exec", "process",
  "web_search", "web_fetch", "browser", "canvas",
  "nodes", "cron", "message", "gateway",
  // ... sessions_spawn, subagents, session_status, image
];

// 保留调用者的大小写，但去重时按小写比较
const canonicalByNormalized = new Map<string, string>();
for (const name of canonicalToolNames) {
  const normalized = name.toLowerCase();
  if (!canonicalByNormalized.has(normalized)) {
    canonicalByNormalized.set(normalized, name);
  }
}

const enabledTools = toolOrder.filter((tool) => availableTools.has(tool));
const toolLines = enabledTools.map((tool) => {
  const summary = coreToolSummaries[tool] ?? externalToolSummaries.get(tool);
  const name = resolveToolName(tool);
  return summary ? `- ${name}: ${summary}` : `- ${name}`;
});
```

**为什么值得看**：`canonicalByNormalized` Map 的设计解决了"LLM 要求工具名大小写敏感，但不同来源可能提供不同大小写"的问题。工具摘要优先使用 `coreToolSummaries`（硬编码的高质量描述），回退到 `externalToolSummaries`（插件提供的描述），确保每个工具都有可读说明。

---

### 机制 C：Prompt 注入防护（OC-19）

**作用**：剥离用户可控字符串中的 Unicode 控制字符和格式字符，防止通过目录名等途径注入恶意指令。

**设计意图**：Prompt 注入不只是文本层面的 `"ignore previous instructions"`，更危险的是**结构注入**——通过 `\n`、双向文本标记等控制字符破坏 prompt 的分节边界。

**关键源码**（`src/agents/sanitize-for-prompt.ts:L1-18`）：

```typescript
/**
 * Threat model (OC-19): attacker-controlled directory names (or other runtime strings)
 * that contain newline/control characters can break prompt structure and inject
 * arbitrary instructions.
 *
 * Strategy (Option 3 hardening):
 * - Strip Unicode "control" (Cc) + "format" (Cf) characters
 * - Strip explicit line/paragraph separators (Zl/Zp): U+2028/U+2029
 */
export function sanitizeForPromptLiteral(value: string): string {
  return value.replace(/[\p{Cc}\p{Cf}  ]/gu, "");
}
```

**为什么值得看**：注释中明确提到了 "Option 3 hardening"，说明作者评估过多种策略后选择了"有损剥离"而非"保真转义"。`\p{Cc}` 覆盖 CR/LF/NUL，`\p{Cf}` 覆盖双向文本标记和零宽字符，`  ` 覆盖行/段落分隔符——这是一个经过深思熟虑的字符集选择。

---

### 机制 D：技能预算控制（二进制搜索）

**作用**：在将技能注入 prompt 前，通过数量限制 + 字符预算双重约束，确保技能章节不超出预设的 token 预算。

**设计意图**：技能数量可能很多（最多从 6 个来源加载），每个技能的描述可能很长。简单截断到固定数量（如 150 个）仍可能超字符预算；简单截断到固定字符数又可能包含过少技能。二进制搜索找到"最大前缀"是精确的解法。

**关键源码**（`src/agents/skills/workspace.ts:L529-565`）：

```typescript
function applySkillsPromptLimits(params: { skills: Skill[]; config?: OpenClawConfig }): {
  skillsForPrompt: Skill[];
  truncated: boolean;
  truncatedReason: "count" | "chars" | null;
} {
  const limits = resolveSkillsLimits(params.config);
  const byCount = params.skills.slice(0, Math.max(0, limits.maxSkillsInPrompt));

  const fits = (skills: Skill[]): boolean => {
    const block = formatSkillsForPrompt(skills);
    return block.length <= limits.maxSkillsPromptChars;
  };

  if (!fits(byCount)) {
    let lo = 0, hi = byCount.length;
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      if (fits(byCount.slice(0, mid))) {
        lo = mid;
      } else {
        hi = mid - 1;
      }
    }
    return { skillsForPrompt: byCount.slice(0, lo), truncated: true, truncatedReason: "chars" };
  }
  return { skillsForPrompt: byCount, truncated: false, truncatedReason: null };
}
```

**为什么值得看**：先按数量硬截断（默认 150），再对截断后的列表做二进制搜索检查字符预算（默认 30k）。这种"粗截断 + 精搜索"的两阶段策略避免了在数千个技能上做二分搜索的性能问题。

---

### 机制 E：系统提示词诊断报告

**作用**：在生成系统提示词的同时，生成一份结构化的诊断报告，记录 prompt 各部分的字符数、技能数量、工具 schema 大小等指标。

**设计意图**：系统提示词是"黑盒"——开发者很难直观知道为什么某次请求 token 数很高。报告机制让 `/status` 命令可以展示 prompt 的组成 breakdown，帮助诊断上下文膨胀问题。

**关键源码**（`src/agents/system-prompt-report.ts:L80-110`）：

```typescript
export function buildSystemPromptReport(params: {
  systemPrompt: string;
  bootstrapFiles: WorkspaceBootstrapFile[];
  injectedFiles: EmbeddedContextFile[];
  skillsPrompt: string;
  tools: AgentTool[];
  // ...
}): SessionSystemPromptReport {
  const systemPrompt = params.systemPrompt.trim();
  const projectContext = extractBetween(systemPrompt, "\n# Project Context\n", "\n## Silent Replies\n");
  const toolListText = extractBetween(systemPrompt,
    "Tool names are case-sensitive. Call tools exactly as listed.\n",
    "\nTOOLS.md does not control tool availability; it is user guidance for how to use external tools."
  );
  const toolsEntries = buildToolsEntries(params.tools);
  const skillsEntries = parseSkillBlocks(params.skillsPrompt);

  return {
    systemPrompt: {
      chars: systemPrompt.length,
      projectContextChars: projectContext.text.length,
      nonProjectContextChars: Math.max(0, systemPrompt.length - projectContext.text.length),
    },
    skills: { promptChars: params.skillsPrompt.length, entries: skillsEntries },
    tools: { listChars: toolListText.length, schemaChars: toolsSchemaChars, entries: toolsEntries },
    // ...
  };
}
```

**为什么值得看**：报告不是简单的 `systemPrompt.length`，而是将 prompt 拆解为 `projectContextChars` / `nonProjectContextChars`、`skills.promptChars`、`tools.listChars/schemaChars` 等维度。这种精细化度量让开发者可以精准定位"是哪部分在消耗 token"。

---

### 机制 F：运行时信息行构建

**作用**：将 Agent 运行时元数据（agentId、host、os、model、channel、capabilities、thinking level）格式化为单行字符串，注入 prompt 的 Runtime 节。

**设计意图**：Runtime 行是 Agent 的"身份名片"，让 LLM 知道当前运行环境的关键属性。使用 `key=value` 格式而非自然语言，节省 token 且便于 LLM 解析。

**关键源码**（`src/agents/system-prompt.ts:L691-728`）：

```typescript
export function buildRuntimeLine(
  runtimeInfo?: { agentId?; host?; os?; arch?; node?; model?; defaultModel?; shell?; repoRoot? },
  runtimeChannel?: string,
  runtimeCapabilities: string[] = [],
  defaultThinkLevel?: ThinkLevel,
): string {
  return `Runtime: ${[
    runtimeInfo?.agentId ? `agent=${runtimeInfo.agentId}` : "",
    runtimeInfo?.host ? `host=${runtimeInfo.host}` : "",
    runtimeInfo?.repoRoot ? `repo=${runtimeInfo.repoRoot}` : "",
    runtimeInfo?.os
      ? `os=${runtimeInfo.os}${runtimeInfo?.arch ? ` (${runtimeInfo.arch})` : ""}`
      : runtimeInfo?.arch ? `arch=${runtimeInfo.arch}` : "",
    runtimeInfo?.model ? `model=${runtimeInfo.model}` : "",
    runtimeChannel ? `channel=${runtimeChannel}` : "",
    runtimeChannel
      ? `capabilities=${runtimeCapabilities.length > 0 ? runtimeCapabilities.join(",") : "none"}`
      : "",
    `thinking=${defaultThinkLevel ?? "off"}`,
  ].filter(Boolean).join(" | ")}`;
}
```

**为什么值得看**：`filter(Boolean).join(" | ")` 的简洁模式实现了"只包含有值的字段"。`repoRoot` 的解析逻辑在 `system-prompt-params.ts:L62-95` 中，优先使用配置值，其次通过 `findGitRoot` 从 workspaceDir/cwd 自动探测——这让 Agent 能准确知道自己在哪个代码库中运行。

---

### 机制 G：PI Prompt 文件（任务特定提示词）

**作用**：为特定开发工作流（PR 审查、PR 合并、Issue 分析、Changelog 审计）提供结构化的任务提示词模板。

**设计意图**：这些不是系统提示词的一部分，而是**用户级任务提示词**——通过 `.pi/prompts/*.md` 文件定义可复用的工作流指令，让 Agent 在接到 `/reviewpr`、`/landpr` 等命令时遵循标准化的分析流程。

**关键源码**（`.pi/prompts/reviewpr.md:L1-25`）：

```markdown
---
description: Review a PR thoroughly without merging
---

0. Truthfulness + reality gate (required for bug-fix claims)
   - Do not trust the issue text or PR summary by default
   - If the PR claims to fix a bug, confirm the bug exists now
   - Prove root cause with exact location (`path/file.ts:line`)
   - Hallucination/BS red flags (treat as BLOCKER until disproven):
     - claimed behavior not present in repo,
     - issue/PR says "fixes #..." but changed files do not touch implicated path

1. Identify PR meta + context
2. Read the PR description carefully
3. Read the diff thoroughly (prefer full diff)
```

**为什么值得看**：PI Prompt 文件采用 YAML frontmatter（`description`）+ Markdown 指令的结构，既可供人类阅读，也可被工具解析。`reviewpr.md` 中 "Truthfulness + reality gate" 的设计体现了对 LLM 幻觉的深刻警惕——明确要求"不要默认信任 PR 描述"，这种元认知指令比简单的"请审查 PR"有效得多。

---

## 5. 与其他维度的交互

```
[Prompt构建] --(系统提示词字符串)--> [编排循环]
[Prompt构建] --(toolLines + toolSummaries)--> [工具系统]
[Prompt构建] --(memory_search / memory_get 指令)--> [记忆系统]
[Prompt构建] --(safetySection + sandboxInfo)--> [安全防护]
[Prompt构建] --(SystemPromptReport)--> [状态管理] (存入 session 供 /status 查询)
[Prompt构建] <--(运行时信息: host/os/model/channel)-- [初始化与环境]
[Prompt构建] <--(可用工具列表)-- [工具系统]
[Prompt构建] <--(Bootstrap 文件内容 + 截断警告)-- [上下文管理]
[Prompt构建] <--(skillsPrompt + 技能预算)-- [技能系统]
[Prompt构建] <--(workspaceDir + sandboxInfo)-- [初始化与环境]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | 编排循环 | 完整的系统提示词字符串 | `buildAgentSystemPrompt()` 返回值 → LLM 请求 |
| 输出到 | 工具系统 | 工具名称列表 + 一句话摘要 | `system-prompt.ts:L330-334` `toolLines` |
| 输出到 | 记忆系统 | `memory_search` / `memory_get` 调用指令 | `system-prompt.ts:L49-52` `buildMemorySection` |
| 输出到 | 安全防护 | 沙箱状态、执行审批规则、安全约束 | `system-prompt.ts:L394-399` `safetySection` |
| 输出到 | 状态管理 | `SessionSystemPromptReport` 诊断数据 | `system-prompt-report.ts:L80-142` |
| 依赖 | 初始化与环境 | 工作区目录、沙箱容器路径 | `workspace-run.ts:L74-116` `resolveRunWorkspaceDir` |
| 依赖 | 上下文管理 | Bootstrap 文件内容、截断警告 | `system-prompt.ts:L616-648` `contextFiles` / `bootstrapTruncationWarningLines` |
| 依赖 | 技能系统 | 可用技能列表（已按预算裁剪） | `skills/workspace.ts:L640-658` `resolveSkillsPromptForRun` |
| 依赖 | 工具系统 | 当前 session 可用工具集合 | `commands-system-prompt.ts:L53-73` `createOpenClawCodingTools` → `toolNames` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"LLM 对提示词前面内容的注意力更高"**：`toolOrder` 将 read/write/edit 排在最前面（`system-prompt.ts:L274-299`），说明作者假设 LLM 更容易注意到列表前面的工具。
2. **"LLM 会遵循结构化的节式指令，但不会主动做资源管理"**：`buildSkillsSection` 明确约束"never read more than one skill up front"（`system-prompt.ts:L31`），说明作者认为 LLM 需要被显式告知"不要贪婪读取"。
3. **"Prompt 中的每一行都在消耗有限资源，且这个成本是每轮重复的"**：技能路径压缩节省 400-600 tokens（`workspace.ts:L44` 注释），`PromptMode` 为子 Agent 裁剪无关章节——都体现了对"系统提示词在每轮请求中重复发送"这一成本的深刻认知。
4. **"LLM 会优先遵循系统指令而非用户输入"**：安全约束直接写入 prompt（`system-prompt.ts:L396-398`），但这不是 100% 可靠的——作者通过 `sanitizeForPromptLiteral` 做了第二层防御。

### 6.2 这个设计的代价/风险

1. **Prompt 膨胀与维护复杂度**：`buildAgentSystemPrompt` 有 20+ 个参数和 500+ 行实现，新增功能（如新工具、新章节）需要修改这个核心函数，存在"上帝函数"风险。
2. **工具排序的僵化**：`toolOrder` 是硬编码数组（`system-prompt.ts:L274-299`），如果新增高频工具需要手动调整顺序，无法根据实际使用频率动态调整。
3. **Prompt 注入的"军备竞赛"**：`sanitizeForPromptLiteral` 剥离控制字符是一种防御，但攻击者可能使用同形字符（homoglyphs）或 Unicode 规范化技巧绕过。代码注释承认这是 "Option 3 hardening"，暗示还有更完善的方案未实施。
4. **技能选择准确率依赖 LLM 判断**："先扫描再选择"策略假设 LLM 能准确判断哪个 skill 适用。如果 LLM 误判，会选择错误的 skill 或完全不使用 skill——而代码中没有对 skill 选择结果的验证机制。
5. **System Prompt Report 的脆弱解析**：`extractBetween` 使用硬编码的字符串标记（如 `"\n# Project Context\n"`）来定位章节（`system-prompt-report.ts:L69-78`）。如果 `buildAgentSystemPrompt` 修改了章节标题格式，报告解析会失效。

### 6.3 如果要重新设计，可能会改变什么

1. **将章节构建器插件化**：当前所有章节构建函数都内联在 `system-prompt.ts` 中。可以改为注册式插件系统，让各功能模块（如 memory、skills、sandbox）注册自己的章节构建器，降低核心函数的维护负担。
2. **动态工具排序**：根据历史工具调用频率动态调整 `toolOrder`，而非硬编码。高频工具自动排到前面，提升 LLM 的工具发现效率。
3. **Prompt 版本哈希与追踪**：当前没有机制追踪"哪一版 prompt 产生了哪次回复"。添加 prompt 内容哈希（如 SHA-256）到日志和 report 中，可以帮助调试和回归测试。
4. **技能选择的显式验证**：在 LLM 选择 skill 后，增加一层验证——检查所选 skill 的 frontmatter 标签是否与用户意图匹配，降低误判风险。
5. **将 PI Prompt 纳入版本控制的工作流**：`.pi/prompts/*.md` 目前作为静态文件存在。可以设计一个"prompt 模板注册表"，支持条件加载（如只在特定 repo 结构下加载 `cl.md`）。

### 6.4 对我自己设计 Agent 系统的启示

> **Prompt 构建不是"字符串拼接"，而是"行为约束工程"**。OpenClaw 的设计启示是：系统提示词的每一行都应该有明确的目的——告诉 LLM 它能做什么（工具排序）、不能做什么（安全约束）、应该优先考虑什么（skill 选择策略）、以及当前环境的边界条件（Runtime 行）。最精妙的设计是 `PromptMode` 三级分级：它不是简单的"少发一点内容"，而是**根据 Agent 的生命周期角色精确裁剪行为契约**——主 Agent 需要完整的交互能力，子 Agent 只需要工具+工作区+运行时，Cron 任务连这些都不需要。这种"按角色定制契约"的思路，比单一系统提示词模板更贴近 LLM 的上下文经济学。
