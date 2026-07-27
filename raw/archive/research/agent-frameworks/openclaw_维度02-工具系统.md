# 维度名：工具系统（Tool System）

## 1. 一句话定位

OpenClaw 的工具系统是连接 LLM 意图与外部世界执行的**安全网关与能力编排层**，它通过多层策略管道、沙箱隔离、循环检测和跨 provider 的 schema 适配，将模型生成的结构化调用请求转化为受控的代码执行、文件操作、网络访问和进程管理动作。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有工具系统，LLM 的输出只是纯文本，无法与文件系统、网络、进程或外部服务交互，Agent 将退化为一个只能对话的聊天机器人。更具体地说：

- **没有 schema 标准化**：OpenAI 会拒绝根级为 `anyOf` 的 JSON Schema（`pi-tools.schema.ts:L81`），Gemini 会拒绝包含 `minLength`/`maxLength` 等约束关键字的 schema（`pi-tools.schema.ts:L79`），导致工具调用请求在传输层直接被 provider 拒绝。
- **没有策略管道**：任何会话（包括通过 HTTP 网关触发的匿名请求）都能调用 `exec`、`fs_write`、`sessions_spawn` 等高危工具，直接造成 RCE 或跨会话注入（`dangerous-tools.ts:L9-20`）。
- **没有沙箱隔离**：`exec` 工具默认在 gateway 主机上运行命令，若模型生成 `rm -rf /` 或读取 `/etc/shadow`，将直接破坏宿主环境（`bash-tools.exec.ts:L307` 中 `configuredHost = defaults?.host ?? "sandbox"` 说明安全默认值是 sandbox，但可配置降级）。
- **没有循环检测**：模型在 cron 任务或长轮询场景中可能反复调用 `process action=poll` 或 `read` 同一文件，导致无限循环消耗 token 和计算资源（`tool-loop-detection.ts:L28-30` 定义了 10/20/30 的 warning/critical/circuit-breaker 阈值）。
- **没有参数归一化**：Claude Code 风格的参数名（`file_path`/`old_string`/`new_string`）与 pi-coding-agent 的命名（`path`/`oldText`/`newText`）不一致，模型会陷入参数错误→重试的无效循环（`pi-tools.params.ts:L86-114`）。

### 2.2 OpenCode 的具体触发条件

- **工具列表构建**：每次 Agent 运行时，`createOpenClawCodingTools()` 被调用（`pi-tools.ts:L198`），根据 `sessionKey`、`agentId`、`sandbox` 等上下文动态组装可用工具列表。
- **策略过滤**：当 `resolveEffectiveToolPolicy()` 返回非空策略时（`pi-tools.policy.ts:L268`），`applyToolPolicyPipeline()` 按顺序应用 profile → global → agent → group → sandbox → subagent 六层策略（`tool-policy-pipeline.ts:L65-108`）。
- **循环检测激活**：`beforeToolCall` 钩子在每个工具执行前调用（`pi-tools.before-tool-call.ts:L207`），当同一工具+参数组合在会话历史中达到阈值时触发阻断。
- **沙箱模式切换**：当 `options?.sandbox?.enabled` 为 true 时（`pi-tools.ts:L272`），文件操作工具被替换为通过 `SandboxFsBridge` 转发的版本，exec 工具通过 Docker 执行。

---

## 3. 核心设计思路

### 3.1 抽象模型

```
┌─────────────────────────────────────────────────────────────┐
│                    Tool Factory Pipeline                     │
│  (createOpenClawCodingTools)                                 │
├─────────────────────────────────────────────────────────────┤
│  1. Resolve Policies (6 layers)                              │
│     profile → providerProfile → global → agent → group →     │
│     sandbox → subagent                                       │
│  2. Build Base Tools (codingTools from pi-coding-agent)      │
│     read/write/edit → sandboxed or host variants             │
│     bash → replaced by exec + process                        │
│  3. Add OpenClaw Tools (browser, web, message, cron, etc.)   │
│  4. Plugin Tools (resolvePluginTools with allowlist)         │
│  5. Apply Special Policies (memoryFlush, messageProvider,    │
│     modelProvider, ownerOnly)                                │
│  6. Policy Pipeline Filtering (applyToolPolicyPipeline)      │
│  7. Schema Normalization (normalizeToolParameters)           │
│  8. Hook Wrapping (beforeToolCall for loop detection)        │
│  9. Abort Signal Wrapping                                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **策略层级** | 6 层嵌套策略（profile/provider/global/agent/group/sandbox/subagent），后层覆盖前层 | 单层全局 allow/deny 列表 | `pi-tools.ts:L568-588` 中 `applyToolPolicyPipeline` 的 steps 数组显式定义了 7 个过滤步骤，支持按 agent、按 provider、按群组细粒度控制 |
| **沙箱文件系统** | 通过 `SandboxFsBridge` 将文件操作转发为 Docker exec 命令，而非直接挂载 | 直接 bind mount 宿主目录到容器 | `fs-bridge.ts:L68-131` 中 `SandboxFsBridgeImpl` 使用 `pathGuard` 和 `pinned write plan` 确保路径安全，避免 Docker mount 的逃逸风险 |
| **循环检测** | 在 `beforeToolCall` 钩子中基于会话状态做运行时检测，critical 级别直接阻断 | 纯静态规则或依赖模型自我纠正 | `pi-tools.before-tool-call.ts:L110-127` 中 `loopResult.level === "critical"` 时返回 `blocked: true`，不依赖模型配合 |
| **Schema 扁平化** | 将 `anyOf`/`oneOf` 合并为单一 `type: "object"` schema，保留所有 properties | 为每个 provider 维护独立 schema | `pi-tools.schema.ts:L127-198` 中通过合并 properties 和 required 数组生成扁平 schema，注释明确说明这是为了兼容 OpenAI（拒绝无 top-level type）和 Gemini（拒绝 anyOf+type 共存） |
| **参数别名兼容** | 在 schema 中同时声明 `path` 和 `file_path`，执行前归一化为内部格式 | 强制模型使用单一参数名 | `pi-tools.params.ts:L133-150` 中 `patchToolSchemaForClaudeCompatibility` 为 Claude Code 风格的参数名添加别名，避免模型训练数据不一致导致的调用失败 |

### 3.3 数据流/控制流

```
输入：LLM 生成的 tool_call（name + arguments）
  │
  ▼
[① abortSignal 检查] ── pi-tools.abort.ts:L60-64
  │
  ▼
[② beforeToolCall 钩子] ── pi-tools.before-tool-call.ts:L207-248
  ├── 循环检测 → 可能阻断
  └── 插件钩子 → 可能修改参数
  │
  ▼
[③ 参数归一化] ── pi-tools.params.ts:L88-114
  │
  ▼
[④ 工具执行]
  ├── read/write/edit → 沙箱桥接或宿主文件系统
  ├── exec → sandbox/gateway/node 三级主机选择
  ├── process → 进程监管器（ProcessSupervisor）
  └── web/message/cron → 外部服务调用
  │
  ▼
[⑤ 结果后处理]
  ├── 图片消毒（sanitizeToolResultImages）
  ├── 读取截断信息剥离
  └── 循环结果记录（recordLoopOutcome）
  │
  ▼
输出：AgentToolResult（content[] + details）
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：多层策略管道（Tool Policy Pipeline）

**作用**：按优先级顺序应用 6 层工具访问控制策略，实现从全局到会话的细粒度权限管理。

**设计意图**：为什么不用简单的单层 allow/deny？因为 OpenClaw 需要支持多租户（不同群组不同策略）、多 agent（每个 agent 独立配置）、多 provider（同一模型不同 provider 行为不同）、以及沙箱/子 agent 的层级继承。单层策略无法表达这种多维度的权限矩阵。

**关键源码**（`src/agents/tool-policy-pipeline.ts:17-63`）：
```typescript
export function buildDefaultToolPolicyPipelineSteps(params: {
  profilePolicy?: ToolPolicyLike;
  // ...
}): ToolPolicyPipelineStep[] {
  return [
    { policy: params.profilePolicy, label: "tools.profile", stripPluginOnlyAllowlist: true },
    { policy: params.providerProfilePolicy, label: "tools.byProvider.profile", stripPluginOnlyAllowlist: true },
    { policy: params.globalPolicy, label: "tools.allow", stripPluginOnlyAllowlist: true },
    { policy: params.globalProviderPolicy, label: "tools.byProvider.allow", stripPluginOnlyAllowlist: true },
    { policy: params.agentPolicy, label: "agent tools.allow", stripPluginOnlyAllowlist: true },
    { policy: params.agentProviderPolicy, label: "agent tools.byProvider.allow", stripPluginOnlyAllowlist: true },
    { policy: params.groupPolicy, label: "group tools.allow", stripPluginOnlyAllowlist: true },
  ];
}
```

**为什么值得看**：`stripPluginOnlyAllowlist: true` 是一个防御性设计——如果某层策略的 allowlist 只包含插件工具名（不含任何核心工具），管道会**剥离该 allowlist 而不是禁用核心工具**（`tool-policy.ts:L151-195`），防止用户配置失误导致系统瘫痪。这是"fail open for core tools"的安全哲学。

---

### 机制 B：子 Agent 深度限制（Subagent Tool Policy）

**作用**：根据子 agent 在 spawn 树中的深度，动态限制可用工具，防止无限递归和资源滥用。

**设计意图**：为什么按深度而不是统一禁用？因为中间层 orchestrator 子 agent 需要 `sessions_spawn` 来管理其子代理，而叶子节点只需要执行任务。深度限制实现了"中间层有管理权，叶子层只有执行权"的分层架构。

**关键源码**（`src/agents/pi-tools.policy.ts:86-94`）：
```typescript
function resolveSubagentDenyList(depth: number, maxSpawnDepth: number): string[] {
  const isLeaf = depth >= Math.max(1, Math.floor(maxSpawnDepth));
  if (isLeaf) {
    return [...SUBAGENT_TOOL_DENY_ALWAYS, ...SUBAGENT_TOOL_DENY_LEAF];
  }
  // Orchestrator sub-agent: only deny the always-denied tools.
  // sessions_spawn, subagents, sessions_list, sessions_history are allowed.
  return [...SUBAGENT_TOOL_DENY_ALWAYS];
}
```

**为什么值得看**：`SUBAGENT_TOOL_DENY_ALWAYS` 包含 `gateway`、`cron`、`memory_search` 等系统级工具（`pi-tools.policy.ts:L51-65`），而 `SUBAGENT_TOOL_DENY_LEAF` 额外包含 `subagents`、`sessions_spawn` 等管理工具（`pi-tools.policy.ts:L71-76`）。这种分层拒绝列表比简单的"子 agent 全禁"更灵活，支持多层 orchestration。

---

### 机制 C：循环检测与断路器（Tool Loop Detection）

**作用**：在工具执行前检测模型是否陷入重复调用循环，critical 级别直接阻断执行，warning 级别发出提示。

**设计意图**：为什么要在工具层而不是在模型层或会话层做检测？因为模型本身无法可靠地自我检测循环（特别是当循环涉及不同工具交替调用时），而会话层（如 compaction）只处理上下文长度，不处理调用模式。工具层是唯一能观察到"调用了什么+结果是什么"的抽象层。

**关键源码**（`src/agents/pi-tools.before-tool-call.ts:100-147`）：
```typescript
const loopResult = detectToolCallLoop(sessionState, toolName, params, args.ctx.loopDetection);

if (loopResult.stuck) {
  if (loopResult.level === "critical") {
    log.error(`Blocking ${toolName} due to critical loop: ${loopResult.message}`);
    return { blocked: true, reason: loopResult.message };
  } else {
    const warningKey = loopResult.warningKey ?? `${loopResult.detector}:${toolName}`;
    if (shouldEmitLoopWarning(sessionState, warningKey, loopResult.count)) {
      log.warn(`Loop warning for ${toolName}: ${loopResult.message}`);
    }
  }
}
```

**为什么值得看**：检测器实现了三种模式（`tool-loop-detection.ts:L9-13`）：
1. `generic_repeat`：同一工具+参数重复调用
2. `known_poll_no_progress`：`process` 的 poll/log 动作结果无变化
3. `ping_pong`：两个工具交替调用且结果稳定（如 A→B→A→B）

`shouldEmitLoopWarning` 使用桶计数（每 10 次一个桶）避免日志风暴（`pi-tools.before-tool-call.ts:L42-58`），这是生产环境的关键细节。

---

### 机制 D：Provider 特定的 Schema 清洗（Schema Normalization）

**作用**：将工具参数 schema 转换为当前 LLM provider 可接受的格式，解决不同 provider 对 JSON Schema 的兼容性问题。

**设计意图**：为什么不在定义工具时就为每个 provider 写独立 schema？因为 OpenClaw 支持 10+ 个 provider（OpenAI、Anthropic、Gemini、xAI 等），维护 N 份 schema 会导致任何工具修改都需要同步更新 N 处。运行时清洗是更可持续的方案。

**关键源码**（`src/agents/pi-tools.schema.ts:66-125`）：
```typescript
export function normalizeToolParameters(tool: AnyAgentTool, options?: { modelProvider?: string; modelId?: string }): AnyAgentTool {
  const isGeminiProvider = options?.modelProvider?.toLowerCase().includes("google") ||
                           options?.modelProvider?.toLowerCase().includes("gemini");
  const isXai = isXaiProvider(options?.modelProvider, options?.modelId);

  function applyProviderCleaning(s: unknown): unknown {
    if (isGeminiProvider && !isAnthropicProvider) return cleanSchemaForGemini(s);
    if (isXai) return stripXaiUnsupportedKeywords(s);
    return s;
  }

  // OpenAI rejects function tool schemas unless the *top-level* is `type: "object"`.
  if ("type" in schema && "properties" in schema && !Array.isArray(schema.anyOf)) {
    return { ...tool, parameters: applyProviderCleaning(schema) };
  }
  // Force `type: "object"` so OpenAI accepts the schema.
  if (!("type" in schema) && (typeof schema.properties === "object" || Array.isArray(schema.required))) {
    const schemaWithType = { ...schema, type: "object" };
    return { ...tool, parameters: applyProviderCleaning(schemaWithType) };
  }
  // Flatten union schemas (anyOf/oneOf) into single object for OpenAI compatibility
  // ... merge properties and required arrays
}
```

**为什么值得看**：注释中明确列出了四个 provider 的怪癖（`pi-tools.schema.ts:L78-83`）：Gemini 拒绝约束关键字、OpenAI 拒绝根级 union、Anthropic 需要完整 JSON Schema、xAI 拒绝验证关键字。`normalizeToolParameters` 通过**先扁平化 union 为单一 object，再按 provider 清洗**的两阶段策略，解决了这个多维兼容矩阵。

---

### 机制 E：自适应读取分页（Adaptive Read Paging）

**作用**：根据当前模型的上下文窗口大小，动态调整 read 工具的单次输出上限，避免大文件读取撑爆上下文。

**设计意图**：为什么不用固定上限？因为不同模型的上下文窗口差异巨大（Claude 3.5 Sonnet 200k vs GPT-4 8k），固定 50KB 对小模型可能太大，对大模型又浪费其处理能力。基于上下文窗口的比例缩放是更精细的资源管理策略。

**关键源码**（`src/agents/pi-tools.read.ts:68-81`）：
```typescript
function resolveAdaptiveReadMaxBytes(options?: OpenClawReadToolOptions): number {
  const contextWindowTokens = options?.modelContextWindowTokens;
  if (typeof contextWindowTokens !== "number" || !Number.isFinite(contextWindowTokens) || contextWindowTokens <= 0) {
    return DEFAULT_READ_PAGE_MAX_BYTES; // 50KB fallback
  }
  const fromContext = Math.floor(
    contextWindowTokens * CHARS_PER_TOKEN_ESTIMATE * ADAPTIVE_READ_CONTEXT_SHARE,
  );
  return clamp(fromContext, DEFAULT_READ_PAGE_MAX_BYTES, MAX_ADAPTIVE_READ_MAX_BYTES);
  // clamp between 50KB and 512KB
}
```

**为什么值得看**：`ADAPTIVE_READ_CONTEXT_SHARE = 0.2`（`pi-tools.read.ts:L46`）意味着 read 输出最多占上下文窗口的 20%，`CHARS_PER_TOKEN_ESTIMATE = 4` 是字符/token 的近似换算。`executeReadWithAdaptivePaging`（`pi-tools.read.ts:L208-284`）实现了最多 8 页的分页聚合，当聚合内容超过预算时提前截断并提示续读偏移量——这比简单截断更友好，因为模型可以立即用 `offset=` 继续读取。

---

### 机制 F：exec 工具的三级主机安全模型

**作用**：为 shell 命令执行提供 sandbox → gateway → node 三级安全边界，每级有不同的隔离强度、审批策略和环境控制能力。

**设计意图**：为什么需要三级而不是简单的"沙箱/非沙箱"？因为 sandbox 有启动开销且某些场景（如需要访问宿主 GPU 或特定服务）无法使用；gateway 提供主机访问但受 safeBin/allowlist 约束；node 用于远程主机执行。统一接口让 Agent 无需关心命令实际跑在哪里。

**关键源码**（`src/agents/bash-tools.exec.ts:307-348`）：
```typescript
const configuredHost = defaults?.host ?? "sandbox";
const requestedHost = normalizeExecHost(params.host) ?? null;
let host: ExecHost = requestedHost ?? configuredHost;

if (!elevatedRequested && requestedHost && requestedHost !== configuredHost) {
  throw new Error(
    `exec host not allowed (requested ${renderExecHostLabel(requestedHost)}; ` +
    `configure tools.exec.host=${renderExecHostLabel(configuredHost)} to allow).`
  );
}
if (elevatedRequested) {
  host = "gateway"; // elevated 强制走 gateway
}

if (host === "sandbox" && !sandbox && (sandboxHostConfigured || requestedHost === "sandbox")) {
  throw new Error("exec host=sandbox is configured, but sandbox runtime is unavailable...");
}

// Sandbox gets raw env. Host (gateway/node) must pass validation.
if (host !== "sandbox" && params.env) {
  validateHostEnv(params.env);
}
```

**为什么值得看**：三个关键安全控制点：
1. **主机降级保护**：如果配置默认是 sandbox，模型请求 gateway 会被拒绝（除非开启 elevated 模式）
2. **环境变量消毒**：gateway/node 主机的 env 必须经过 `validateHostEnv`（`bash-tools.exec-runtime.ts`），防止注入 `LD_PRELOAD` 等危险变量
3. **脚本预检**：`validateScriptFileForShellBleed`（`bash-tools.exec.ts:80-149`）在运行前检查 Python/Node 脚本中是否混入了 shell 变量语法（如 `$HOME`），这是针对模型常见错误的防御性设计

---

### 机制 G：Memory Flush 的追加写入限制

**作用**：当工具运行由 memory 触发时（`trigger === "memory"`），将 write 工具限制为只能向指定文件追加内容，防止 memory flush 过程中的任意文件覆盖。

**设计意图**：为什么 memory flush 需要特殊限制？因为 memory flush 通常是自动化触发的（无人在场审批），如果允许任意写入，攻击者可能通过篡改 memory 内容诱导 agent 在 flush 时覆盖关键文件。

**关键源码**（`src/agents/pi-tools.read.ts:514-562`）：
```typescript
export function wrapToolMemoryFlushAppendOnlyWrite(tool: AnyAgentTool, options: MemoryFlushAppendOnlyWriteOptions): AnyAgentTool {
  const allowedAbsolutePath = path.resolve(options.root, options.relativePath);
  return {
    ...tool,
    description: `${tool.description} During memory flush, this tool may only append to ${options.relativePath}.`,
    execute: async (toolCallId, args, signal, onUpdate) => {
      // ... normalize params ...
      const resolvedPath = resolveToolPathAgainstWorkspaceRoot({ filePath, root: options.root, ... });
      if (resolvedPath !== allowedAbsolutePath) {
        throw new Error(`Memory flush writes are restricted to ${options.relativePath}; use that path only.`);
      }
      await appendMemoryFlushContent({ absolutePath: allowedAbsolutePath, content, ... });
      return { content: [{ type: "text", text: `Appended content to ${options.relativePath}.` }], details: { path: options.relativePath, appendOnly: true } };
    },
  };
}
```

**为什么值得看**：这不是简单的路径检查——`appendMemoryFlushContent`（`pi-tools.read.ts:464-512`）实现了真正的追加语义（读取现有内容 + 拼接 + 写回），而不是依赖底层 append 操作，因为在沙箱场景中需要通过 `SandboxFsBridge` 的 `readFile` + `writeFile` 组合来实现。

---

## 5. 与其他维度的交互

```
[工具系统] --(工具列表+schema)--> [LLM 调用层/pi-agent-core]
[工具系统] <--(tool_call 请求)-- [LLM 调用层/pi-agent-core]
[工具系统] --(exec 输出/文件内容)--> [上下文/记忆系统]
[工具系统] <--(历史消息作为输入)-- [上下文/记忆系统]
[工具系统] --(sessions_spawn 调用)--> [子 Agent 系统]
[工具系统] <--(子 agent 深度/角色)-- [子 Agent 系统]
[工具系统] --(plugin tools)--> [插件系统]
[工具系统] <--(before_tool_call hooks)-- [插件系统]
[工具系统] --(sandbox fs ops)--> [Docker 沙箱系统]
[工具系统] <--(SandboxFsBridge)-- [Docker 沙箱系统]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | LLM 调用层 | 本轮可用的工具列表及其标准化 schema | `createOpenClawCodingTools()` 返回 `AnyAgentTool[]`（`pi-tools.ts:L615`） |
| 依赖 | LLM 调用层 | 模型生成的 tool_call（name + arguments） | `tool.execute(toolCallId, params, signal, onUpdate)`（`tools/common.ts` 的 `AgentTool` 接口） |
| 输出到 | 上下文系统 | read/exec 等工具的输出文本进入下一轮对话 | `AgentToolResult.content[]` 中的 `text` 块 |
| 依赖 | 记忆系统 | memory_search/memory_get 被工具系统调用 | `pi-tools.policy.ts:L61-64` 中 `SUBAGENT_TOOL_DENY_ALWAYS` 禁止子 agent 使用 memory 工具 |
| 输出到 | 子 Agent 系统 | sessions_spawn 工具创建子 agent | `tools/sessions-spawn-tool.ts` |
| 依赖 | 子 Agent 系统 | 子 agent 深度决定工具拒绝列表 | `resolveSubagentToolPolicyForSession()`（`pi-tools.policy.ts:L122-141`） |
| 输出到 | 插件系统 | 插件注册的工具被纳入工具列表 | `resolvePluginTools()`（`plugins/tools.ts:L45-139`） |
| 依赖 | 插件系统 | 插件通过 before_tool_call hook 拦截/修改调用 | `getGlobalHookRunner().runBeforeToolCall()`（`pi-tools.before-tool-call.ts:L150-191`） |
| 输出到 | Docker 沙箱 | exec 命令通过 Docker 执行，文件操作通过 fs-bridge | `SandboxFsBridgeImpl`（`sandbox/fs-bridge.ts:L68`） |
| 依赖 | 配置系统 | 六层策略配置、exec 安全级别、fs 工作区限制 | `resolveEffectiveToolPolicy()`（`pi-tools.policy.ts:L268`）、`resolveExecConfig()`（`pi-tools.ts:L133-160`） |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **模型不可靠**：`beforeToolCall` 钩子中的循环检测、exec 的脚本预检、参数归一化都假设模型会犯重复调用、参数名混淆、shell 语法注入等错误。系统不是"信任但验证"，而是"默认不信任"。
2. **Plugin 是二等公民**：`stripPluginOnlyAllowlist` 机制（`tool-policy.ts:L151-195`）假设用户配置 allowlist 时容易遗漏核心工具，因此当 allowlist 只包含插件工具时系统选择**剥离该 allowlist 以保护核心工具可用性**，而非严格执行用户配置。
3. **Context window 是稀缺资源**：自适应读取分页（`pi-tools.read.ts:L68-81`）和 image sanitization（`tool-images.ts`）都假设模型上下文有限，需要在工具层就做预算管理。

### 6.2 这个设计的代价/风险

1. **Schema 扁平化丢失语义**：`normalizeToolParameters` 将 `anyOf` 合并为单一 object（`pi-tools.schema.ts:L179-198`），虽然保留了所有 properties，但丢失了"这些参数组是互斥的"这一约束信息。模型可能同时传入互斥参数，导致工具执行层需要额外校验。
2. **Policy pipeline 的隐式顺序依赖**：六层策略的过滤顺序是硬编码的（`tool-policy-pipeline.ts:L29-63`），如果未来需要插入新层级（如"按时间段的策略"），需要修改核心管道代码，无法通过配置扩展。
3. **Loop detection 的状态耦合**：循环检测依赖 `SessionState.toolCallHistory`（`tool-loop-detection.ts:L382`），这是一个内存中的滑动窗口数组。如果会话状态丢失（如进程重启），循环检测历史也会丢失，短期内可能无法检测到跨重启的循环模式。
4. **SandboxFsBridge 的性能开销**：每次文件操作都转化为 Docker exec 命令（`fs-bridge.ts:L122-130`），相比直接文件系统访问有显著的延迟开销。代码中没有看到批量操作或缓存机制来优化高频小文件操作。

### 6.3 如果要重新设计，可能会改变什么

1. **将策略管道改为可插拔的 middleware 链**：当前 `buildDefaultToolPolicyPipelineSteps` 返回固定数组，可以改为注册式 middleware，让插件也能注入策略层（如"按请求来源 IP 的策略"）。
2. **Schema 清洗改为声明式标注**：当前 provider 清洗逻辑散落在 `normalizeToolParameters` 和多个 `clean-for-*.ts` 文件中，可以改为在工具定义时用装饰器/元数据标注"此字段对 Gemini 不可用"，由统一引擎处理。
3. **Loop detection 使用持久化存储**：将 `toolCallHistory` 持久化到 SQLite（与 session 存储一致），支持跨进程/跨重启的循环检测，同时可以基于历史数据做更智能的异常检测（如"该 agent 在过去 24 小时内平均每个任务调用 read 多少次"）。
4. **exec 工具引入 capability-based 安全模型**：当前 safeBin/allowlist 模型是基于路径和命令名的字符串匹配，可以改为基于 capability 的模型（如"此会话有 `net:connect` 和 `fs:read:/tmp` 能力"），更细粒度且更易于审计。

### 6.4 对我自己设计 Agent 系统的启示

最核心的启示是：**工具系统不是"让模型能调用函数"那么简单，它是整个 Agent 的安全边界和资源管理器**。OpenClaw 的设计表明，一个生产级的工具系统必须同时解决：

- **兼容性**（跨 provider 的 schema 适配）
- **安全性**（多层策略、沙箱隔离、参数消毒）
- **可靠性**（循环检测、错误恢复、边界情况处理）
- **可扩展性**（插件工具、hooks、动态策略）

特别是"在工具执行前做运行时循环检测"这一设计，将原本属于"模型训练"或"提示工程"的问题下沉到系统层解决，是提升 Agent 可靠性的关键架构决策。
