# 维度02：工具系统（Tool System）

## 1. 一句话定位

工具系统是 OpenCode Agent 与外部世界（文件系统、Shell、网络、子 Agent、LSP 等）之间的**结构化能力边界层**。它通过统一的 DSL 定义、注册中心与运行时组装机制，将 LLM 的文本意图转换为类型安全、权限受控、可观测、可回滚的副作用操作。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有工具系统，Agent 将退化为纯文本生成器，无法与外部环境交互。具体到代码层面的后果包括：

- **无类型安全的参数校验**：LLM 输出的 JSON 参数可能字段缺失、类型错误，直接传入 `fs.readFile` 或 `child_process.spawn` 会导致运行时崩溃或不可预期的副作用。`Tool.define` 中通过 `zod` schema 在 `execute` 前做 `parse`，正是为了拦截这种风险（`tool.ts:59`）。
- **无权限隔离**：Agent 可能未经用户同意就删除文件、执行危险命令或访问外部目录。`bash.ts` 中通过 tree-sitter 解析命令提取 `rm/cp/mv` 等敏感操作，并调用 `ctx.ask` 进入权限审批流；`external-directory.ts` 对所有超出工作区的路径进行拦截——这些安全网全部依赖工具层的统一封装。
- **无输出截断与流控**：LLM 上下文窗口有限，若 `grep` 返回 10 万行或 `bash` 输出超大日志，直接注入消息会撑爆上下文。`Truncate.output`（`truncation.ts:51`）在工具层统一做行/字节截断，并将完整结果落盘，Agent 只看到摘要。
- **无工具发现与动态切换**：不同模型对工具格式的支持不同（如 GPT 系列支持 `apply_patch` 而其它模型使用 `edit`/`write`），若没有 `ToolRegistry.tools` 中的模型级过滤逻辑（`registry.ts:141-154`），Agent 可能在错误场景调用不兼容的工具。
- **无 MCP 扩展性**：没有 MCP 桥接层，Agent 无法接入外部生态（如数据库、浏览器、第三方 API），能力被锁定在内置工具集。

### 2.2 OpenCode 的具体触发条件

工具系统的激活发生在每次用户消息进入编排循环时。在 `session/prompt.ts` 的 `resolveTools` 中（`L737-925`），触发条件为：

```typescript
// session/prompt.ts L784-788
for (const item of await ToolRegistry.tools(
  { modelID: input.model.api.id, providerID: input.model.providerID },
  input.agent,
)) {
```

这里 `input.model` 和 `input.agent` 由上层编排循环根据当前会话配置决定。只要会话需要调用工具（即非纯文本模式），就会进入 `resolveTools`，将 `ToolRegistry` 中的工具定义转换为 AI SDK 的 `AITool` 对象，并注入到模型请求中。

此外，权限系统的触发嵌入在每个工具的 `execute` 内部，例如 `bash.ts:153-160`：

```typescript
if (patterns.size > 0) {
  await ctx.ask({
    permission: "bash",
    patterns: Array.from(patterns),
    always: Array.from(always),
    metadata: {},
  })
}
```

这意味着工具系统不仅是"能力提供层"，也是"安全闸门层"——每次执行前都必须通过 `ctx.ask` 的权限评估。

---

## 3. 核心设计思路

### 3.1 抽象模型

```typescript
// 伪代码描述核心抽象

interface Tool {
  id: string
  init(ctx?: InitContext): Promise<{
    description: string
    parameters: ZodSchema
    execute(args, ctx: ToolContext): Promise<Result>
  }>
}

interface ToolContext {
  sessionID: string
  messageID: string
  agent: string
  abort: AbortSignal
  callID?: string
  messages: MessageV2.WithParts[]
  metadata(input): void      // 上报执行状态到 UI
  ask(input): Promise<void>  // 触发权限审批
}

interface Result {
  title: string
  metadata: Record<string, any>
  output: string
  attachments?: FilePart[]
}
```

核心抽象是**"延迟初始化 + 运行时上下文注入"**：工具的定义（`Tool.define`）与初始化（`init`）分离，定义时只提供 schema 和工厂函数，运行时由 `resolveTools` 注入会话上下文、权限系统和模型转换逻辑。

### 3.2 关键设计决策

#### 决策1：Zod Schema 作为单一真相源
- **选了什么**：所有工具参数用 `zod` 定义，`Tool.define` 自动将其转为 JSON Schema 供模型消费，并在 `execute` 前自动校验。
- **放弃了什么**：放弃了手动维护 JSON Schema 或依赖模型提供商的 schema 方言。这增加了 `zod` 依赖，但消除了 schema 漂移风险。

#### 决策2：工具执行与权限审批深度耦合
- **选了什么**：每个工具的 `execute` 内部显式调用 `ctx.ask`，将权限检查下沉到工具层而非编排层。
- **放弃了什么**：放弃了统一的"前置权限拦截器"架构。好处是工具可以自定义权限粒度（如 `bash` 按命令模式审批、`edit` 按文件路径审批），代价是新增工具时必须手动编写 `ask` 逻辑，容易遗漏。

#### 决策3：内置工具与 MCP 工具在运行时统一
- **选了什么**：`resolveTools` 将 `ToolRegistry.tools()` 和 `MCP.tools()` 的结果合并到同一个 `Record<string, AITool>` 中，对上层透明。
- **放弃了什么**：放弃了为 MCP 工具单独维护一套调用栈。代价是 MCP 工具的 `execute` 需要额外包装以适配 OpenCode 的 `ToolContext` 和 `Truncate` 逻辑（`prompt.ts:831-922`）。

#### 决策4：输出截断作为工具层的横切关注点
- **选了什么**：`Tool.define` 在 `execute` 后自动调用 `Truncate.output`，除非工具自行设置 `truncated` 标记。
- **放弃了什么**：放弃了让各个工具自行处理截断。这保证了行为一致性，但某些工具（如 `webfetch` 返回图片附件）不需要截断，因此通过 `metadata.truncated !== undefined` 跳过。

### 3.3 数据流/控制流

```
[用户消息] → [编排循环] → [SessionPrompt.resolveTools]
                                    |
                                    ▼
                    ┌───────────────────────────────┐
                    │  ToolRegistry.tools(model, agent) │
                    │  - 过滤模型不兼容工具              │
                    │  - 过滤实验性/权限禁用工具          │
                    └───────────────────────────────┘
                                    |
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              [内置工具]      [自定义工具]      [MCP工具]
                    |               |               |
                    ▼               ▼               ▼
              [t.init()]      [t.init()]      [convertMcpTool]
                    |               |               |
                    └───────────────┴───────────────┘
                                    |
                                    ▼
                    [ProviderTransform.schema]  // 模型级 schema 转换
                                    |
                                    ▼
                    [AI SDK tool()]  // 生成 AITool
                                    |
                                    ▼
                    [返回 tools 对象给编排循环]
                                    |
                    [LLM 生成 tool_call] → [AITool.execute]
                                    |
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              [ctx.ask()]    [实际副作用]      [Truncate.output]
              [权限审批]     [bash/fs/net]     [截断/落盘]
                    |               |               |
                    └───────────────┴───────────────┘
                                    |
                                    ▼
                    [Plugin.trigger("tool.execute.after")]
                                    |
                                    ▼
                    [结果注入消息上下文] → [下一轮 LLM]
```

---

## 4. 关键机制拆解（含源码）

### 机制A：Tool.define DSL（工具定义与参数校验）

**这段代码为什么值得看**：它展示了工具定义的最小契约——`id` + `init` 工厂函数，以及 `execute` 的自动包装逻辑（参数校验 + 截断）。这是整个工具系统的元模型。

```typescript
// packages/opencode/src/tool/tool.ts L48-88
export function define<Parameters extends z.ZodType, Result extends Metadata>(
  id: string,
  init: Info<Parameters, Result>["init"] | Awaited<ReturnType<Info<Parameters, Result>["init"]>>,
): Info<Parameters, Result> {
  return {
    id,
    init: async (initCtx) => {
      const toolInfo = init instanceof Function ? await init(initCtx) : init
      const execute = toolInfo.execute
      toolInfo.execute = async (args, ctx) => {
        try {
          toolInfo.parameters.parse(args)
        } catch (error) {
          if (error instanceof z.ZodError && toolInfo.formatValidationError) {
            throw new Error(toolInfo.formatValidationError(error), { cause: error })
          }
          throw new Error(
            `The ${id} tool was called with invalid arguments: ${error}.\nPlease rewrite the input so it satisfies the expected schema.`,
            { cause: error },
          )
        }
        const result = await execute(args, ctx)
        if (result.metadata.truncated !== undefined) {
          return result
        }
        const truncated = await Truncate.output(result.output, {}, initCtx?.agent)
        return {
          ...result,
          output: truncated.content,
          metadata: {
            ...result.metadata,
            truncated: truncated.truncated,
            ...(truncated.truncated && { outputPath: truncated.outputPath }),
          },
        }
      }
      return toolInfo
    },
  }
}
```

**分析**：`Tool.define` 采用**高阶函数**模式，返回的 `Info` 对象包含延迟执行的 `init`。`init` 内部对 `execute` 进行 AOP 式包装：先 `zod.parse` 参数，再执行真实逻辑，最后自动截断输出。这种设计让工具开发者只需关注业务逻辑，无需重复编写校验和截断代码。

---

### 机制B：ToolRegistry（注册、发现、过滤）

**这段代码为什么值得看**：它揭示了工具的来源多样性（内置、自定义文件、插件、MCP）以及模型级动态过滤逻辑（如 GPT 用 `apply_patch`，其它用 `edit`/`write`）。

```typescript
// packages/opencode/src/tool/registry.ts L131-172
export async function tools(
  model: { providerID: string; modelID: string },
  agent?: Agent.Info,
) {
  const tools = await all()
  const result = await Promise.all(
    tools
      .filter((t) => {
        if (t.id === "codesearch" || t.id === "websearch") {
          return model.providerID === "opencode" || Flag.OPENCODE_ENABLE_EXA
        }
        const usePatch =
          model.modelID.includes("gpt-") && !model.modelID.includes("oss") && !model.modelID.includes("gpt-4")
        if (t.id === "apply_patch") return usePatch
        if (t.id === "edit" || t.id === "write") return !usePatch
        return true
      })
      .map(async (t) => {
        using _ = log.time(t.id)
        const tool = await t.init({ agent })
        const output = {
          description: tool.description,
          parameters: tool.parameters,
        }
        await Plugin.trigger("tool.definition", { toolID: t.id }, output)
        return {
          id: t.id,
          ...tool,
          description: output.description,
          parameters: output.parameters,
        }
      }),
  )
  return result
}
```

**分析**：`ToolRegistry` 不仅是静态列表，更是**动态策略引擎**。它根据模型 ID 决定启用哪些编辑工具（`apply_patch` vs `edit`/`write`），根据 provider 决定是否启用搜索工具。这种设计让同一套 Agent 配置可以适配不同模型的能力偏好，避免了"一刀切"的工具列表。

---

### 机制C：resolveTools（运行时工具组装）

**这段代码为什么值得看**：它是内置工具与 MCP 工具的"汇流点"，展示了如何将 OpenCode 的 `ToolContext` 注入到 AI SDK 的 `tool()` 中，以及 MCP 结果如何被适配为 OpenCode 的附件格式。

```typescript
// packages/opencode/src/session/prompt.ts L784-829
for (const item of await ToolRegistry.tools(
  { modelID: input.model.api.id, providerID: input.model.providerID },
  input.agent,
)) {
  const schema = ProviderTransform.schema(input.model, z.toJSONSchema(item.parameters))
  tools[item.id] = tool({
    id: item.id as any,
    description: item.description,
    inputSchema: jsonSchema(schema as any),
    async execute(args, options) {
      const ctx = context(args, options)
      await Plugin.trigger("tool.execute.before", { tool: item.id, sessionID: ctx.sessionID, callID: ctx.callID }, { args })
      const result = await item.execute(args, ctx)
      const output = {
        ...result,
        attachments: result.attachments?.map((attachment) => ({
          ...attachment,
          id: Identifier.ascending("part"),
          sessionID: ctx.sessionID,
          messageID: input.processor.message.id,
        })),
      }
      await Plugin.trigger("tool.execute.after", { tool: item.id, sessionID: ctx.sessionID, callID: ctx.callID, args }, output)
      return output
    },
  })
}
```

**分析**：`resolveTools` 是**连接层**。它将 `ToolRegistry` 的抽象工具转换为 AI SDK 可消费的 `AITool`，同时注入会话上下文（`sessionID`、`messageID`、`abort` 信号）和插件钩子（`tool.execute.before/after`）。`context` 函数（`L749-782`）还构造了 `metadata` 和 `ask` 两个关键方法，前者用于向 UI 实时上报工具执行状态，后者用于触发权限审批。

---

### 机制D：内置工具实现模式（以 bash 为例）

**这段代码为什么值得看**：`bash` 是复杂度最高的内置工具之一，它展示了如何将 LLM 的文本命令转化为安全的系统调用——包括命令解析、权限提取、外部目录检测、流式输出和超时控制。

```typescript
// packages/opencode/src/tool/bash.ts L78-160
async execute(params, ctx) {
  const cwd = params.workdir || Instance.directory
  const timeout = params.timeout ?? DEFAULT_TIMEOUT
  const tree = await parser().then((p) => p.parse(params.command))
  const directories = new Set<string>()
  const patterns = new Set<string>()
  const always = new Set<string>()

  for (const node of tree.rootNode.descendantsOfType("command")) {
    let commandText = node.parent?.type === "redirected_statement" ? node.parent.text : node.text
    const command = []
    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i)
      if (![ "command_name", "word", "string", "raw_string", "concatenation" ].includes(child?.type)) continue
      command.push(child.text)
    }
    if (["cd", "rm", "cp", "mv", "mkdir", "touch", "chmod", "chown", "cat"].includes(command[0])) {
      for (const arg of command.slice(1)) {
        if (arg.startsWith("-")) continue
        const resolved = await fs.realpath(path.resolve(cwd, arg)).catch(() => "")
        if (resolved && !Instance.containsPath(resolved)) {
          directories.add((await Filesystem.isDir(resolved)) ? resolved : path.dirname(resolved))
        }
      }
    }
    if (command.length && command[0] !== "cd") {
      patterns.add(commandText)
      always.add(BashArity.prefix(command).join(" ") + " *")
    }
  }

  if (directories.size > 0) { /* ctx.ask external_directory */ }
  if (patterns.size > 0) { /* ctx.ask bash */ }
  // ... spawn process
}
```

**分析**：`bash` 工具的安全模型是**"解析后审批"**——不是简单拦截所有命令，而是用 tree-sitter 解析 AST，提取文件操作命令和外部目录访问，然后针对性地请求权限。这比黑名单/白名单更精确：例如 `ls` 不需要审批，但 `rm -rf /` 会被捕获。同时，它通过 `ctx.metadata` 实时流式上报输出到 UI，让用户看到命令执行进度。

---

### 机制E：MCP 工具桥接

**这段代码为什么值得看**：它展示了 MCP 工具如何被转换为 OpenCode 原生工具，以及 MCP 的 `content` 数组（可能包含 text/image/resource）如何被统一适配为 `output` + `attachments`。

```typescript
// packages/opencode/src/session/prompt.ts L831-922
for (const [key, item] of Object.entries(await MCP.tools())) {
  const execute = item.execute
  if (!execute) continue
  const transformed = ProviderTransform.schema(input.model, asSchema(item.inputSchema).jsonSchema)
  item.inputSchema = jsonSchema(transformed)
  item.execute = async (args, opts) => {
    const ctx = context(args, opts)
    await Plugin.trigger("tool.execute.before", { tool: key, sessionID: ctx.sessionID, callID: opts.toolCallId }, { args })
    await ctx.ask({ permission: key, metadata: {}, patterns: ["*"], always: ["*"] })
    const result = await execute(args, opts)
    await Plugin.trigger("tool.execute.after", { tool: key, sessionID: ctx.sessionID, callID: opts.toolCallId, args }, result)
    const textParts: string[] = []
    const attachments: Omit<MessageV2.FilePart, "id" | "sessionID" | "messageID">[] = []
    for (const contentItem of result.content) {
      if (contentItem.type === "text") textParts.push(contentItem.text)
      else if (contentItem.type === "image") attachments.push({ type: "file", mime: contentItem.mimeType, url: `data:${contentItem.mimeType};base64,${contentItem.data}` })
      else if (contentItem.type === "resource") { /* ... */ }
    }
    const truncated = await Truncate.output(textParts.join("\n\n"), {}, input.agent)
    return {
      title: "",
      metadata: { ...(result.metadata ?? {}), truncated: truncated.truncated },
      output: truncated.content,
      attachments: attachments.map((a) => ({ ...a, id: Identifier.ascending("part"), sessionID: ctx.sessionID, messageID: input.processor.message.id })),
      content: result.content,
    }
  }
  tools[key] = item
}
```

**分析**：MCP 桥接的核心是**"格式适配 + 权限兜底"**。MCP 工具的 `execute` 被保留，但外层包装了 OpenCode 的 `ToolContext`、`Plugin` 钩子和 `Truncate` 逻辑。特别值得注意的是 `content: result.content` 的保留——这是为了在某些输出场景下保持 MCP 原始内容的顺序和结构，避免信息丢失。

---

## 5. 与其他维度的交互

| 交互维度 | 交互方式 | 代码位置 |
|---------|---------|---------|
| **编排循环** | `resolveTools` 由 `SessionPrompt` 调用，生成的 `tools` 对象注入到 LLM 请求中；工具执行结果通过 `AITool.execute` 返回，成为下一轮消息的 `tool_result` | `session/prompt.ts:737-925` |
| **权限系统** | 每个工具的 `execute` 通过 `ctx.ask` 触发 `PermissionNext.ask`，由 `PermissionNext.evaluate` 根据规则集判断 allow/ask/deny | `permission/next.ts:131-161`, `tool/bash.ts:153` |
| **记忆系统** | `TaskTool` 创建子会话（`Session.create`）时继承父会话上下文；`ReadTool` 通过 `FileTime` 记录文件读取历史，防止并发编辑冲突 | `tool/task.ts:72-102`, `tool/read.ts:217`, `file/time.ts` |
| **LSP/验证** | `WriteTool`、`EditTool`、`ApplyPatchTool` 在执行后调用 `LSP.touchFile` 和 `LSP.diagnostics`，将类型错误反馈给 Agent | `tool/write.ts:55-72`, `tool/edit.ts:146-156` |
| **插件系统** | `ToolRegistry.tools` 和 `resolveTools` 中分别触发 `tool.definition` 和 `tool.execute.before/after` 插件事件 | `tool/registry.ts:162`, `session/prompt.ts:795-825` |
| **UI/状态** | `ctx.metadata` 实时更新 `SessionPart` 的状态（running/completed），驱动 UI 展示工具执行进度 | `session/prompt.ts:757-772` |
| **文件监听** | `WriteTool`、`EditTool` 通过 `Bus.publish(FileWatcher.Event.Updated)` 通知文件系统变更，触发 LSP 重新索引 | `tool/write.ts:46-51`, `tool/edit.ts:110-118` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **模型不是可信的**：所有 LLM 输出的参数必须经过 `zod` 校验，所有副作用操作必须经过权限审批。这体现在 `Tool.define` 的自动包装和每个工具内部的 `ctx.ask` 调用。
2. **工具是副作用的主要来源**：因此截断、权限、LSP 诊断等横切关注点都集中在工具层，而非编排层。
3. **MCP 将成为生态标准**：OpenCode 为 MCP 工具提供了与内置工具同等的运行时地位，假设未来大部分外部能力将通过 MCP 接入。
4. **Agent 需要实时反馈**：`ctx.metadata` 的流式上报假设工具执行可能耗时较长（如 `bash` 编译、`webfetch` 下载），UI 需要展示进度。

### 6.2 这个设计的代价/风险

1. **权限逻辑分散**：每个工具自行调用 `ctx.ask`，新增工具时容易遗漏权限检查。例如若开发者忘记在自定义工具中调用 `ask`，该工具将绕过权限系统。
2. **MCP 工具权限粒度粗**：MCP 工具的权限检查统一使用 `patterns: ["*"]`（`prompt.ts:854`），无法像内置工具那样精细化控制。
3. **工具初始化成本**：`ToolRegistry.tools` 对每个工具调用 `t.init()`，若工具数量多或 `init` 耗时（如加载 WASM parser），可能阻塞会话启动。
4. **截断语义不一致**：`Truncate.output` 默认按"头部"截断，但某些工具（如日志查看）可能需要"尾部"截断，目前只有 `Truncate.Options` 支持，但工具层未充分利用。

### 6.3 如果要重新设计，可能会改变什么

1. **权限拦截器模式**：将 `ctx.ask` 从工具内部提取到 `resolveTools` 的统一包装层中，通过声明式配置（如工具的 `permissions` 字段）自动生成审批逻辑，避免遗漏。
2. **工具初始化懒加载**：将 `t.init()` 延迟到工具首次被调用时执行，而非会话启动时全部初始化，降低冷启动延迟。
3. **MCP 工具的沙箱化**：为 MCP 工具引入独立的进程/容器隔离，防止第三方 MCP 服务器的恶意代码影响主机。
4. **工具链组合**：当前工具是原子化的，未来可能需要支持"工具链"——预定义的工具调用序列（如 `read → edit → lsp`），减少 LLM 的往返次数。

### 6.4 对我自己设计 Agent 系统的启示

1. **Schema 即契约**：用 Zod 等运行时类型系统作为工具参数的单一真相源，自动生成模型可用的 JSON Schema，同时保证执行时的类型安全。
2. **权限是工具的属性，不是编排的属性**：将权限检查下沉到工具层，让工具开发者根据自身风险特征定义审批粒度，而非在编排层做统一拦截。
3. **输出截断是必需品，不是优化项**：任何可能返回大数据量的工具（文件读取、命令执行、搜索）都必须有截断机制，且截断后应提供"如何获取完整数据"的指引（如 OpenCode 的 `TaskTool` 提示）。
4. **MCP 桥接要保留原生能力**：在适配 MCP 工具到自身体系时，不要完全丢弃 MCP 的原始输出格式（如 `content` 数组），以便在需要时透传给模型。
5. **工具执行是可观测的**：通过 `metadata` 实时上报执行状态，不仅为了 UI 展示，也为了后续的分析、调试和审计。
