# 维度：安全防护 (Security)

## 1. 一句话定位

安全防护是 OpenCode 的"安检系统"，通过 `PermissionNext` 规则引擎、Bash 命令 AST 解析和模型级工具过滤，在 Agent 执行副作用操作前进行多层次权限校验。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **未授权文件删除**：Agent 可能未经用户同意执行 `rm -rf`，直接造成数据丢失。
- **外部目录泄露**：Agent 可能读取 `~/.ssh/id_rsa` 或 `/etc/passwd` 等敏感文件。
- **危险命令执行**：`curl | bash` 或 `wget | sh` 等管道命令可能引入恶意代码。
- **模型间工具不兼容**：GPT 系列可能收到 `edit` 工具的调用而报错，因为 GPT 更适合 `apply_patch`。

### 2.2 OpenCode 的具体触发条件

- **工具执行前**：每个工具的 `execute` 调用 `ctx.ask`（`permission/next.ts:L131-161`）
- **Bash 命令执行前**：tree-sitter 解析后提取危险模式（`bash.ts:L78-160`）
- **工具注册时**：`ToolRegistry.tools` 按模型过滤（`registry.ts:L131-171`）
- **用户发送 `@agent` 消息时**：`bypassAgentCheck` 检测（`prompt.ts:L601-611`）

---

## 3. 核心设计思路

### 3.1 抽象模型

```
权限评估流程：

Tool Execute Request
    │
    ▼
[PermissionNext.evaluate] ──► allow / deny / ask
    │
    ├──► allow ──► 直接执行
    │
    ├──► deny ──► 抛出 DeniedError
    │
    └──► ask ──► Bus.publish(Event.Asked)
                    │
                    ▼
            [用户响应] ──► once / always / reject
                │
                ├──► once ──► 允许本次
                ├──► always ──► 记录到 approved 规则集
                └──► reject ──► 抛出 RejectedError/CorrectedError
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **规则引擎** | `allow/deny/ask` 三态 + wildcard 匹配 | 简单的布尔白名单 | 支持细粒度控制（如 `edit: { "*.md": "allow", "*": "deny" }`） |
| **权限下沉到工具层** | 每个工具内部调用 `ctx.ask` | 统一的编排层拦截 | 工具可以自定义权限粒度（bash 按命令模式、edit 按文件路径） |
| **AST 解析命令** | tree-sitter 解析 Bash 命令提取文件访问 | 正则表达式匹配 | AST 更精确，能处理复杂命令结构 |
| **模型级工具过滤** | 按模型 ID 决定启用哪些工具 | 统一工具列表 | GPT 用 `apply_patch`，其他用 `edit`/`write` |

### 3.3 数据流/控制流

```
[工具调用请求]
    │
    ├──► [ToolRegistry.tools] ──► 模型过滤（edit vs apply_patch）
    │
    ├──► [resolveTools] ──► 用户禁用 / agent 权限 disabled
    │
    └──► [工具执行]
            │
            ├──► [bash] ──► tree-sitter 解析 ──► 提取外部目录 / 危险命令 ──► ctx.ask()
            │
            ├──► [edit/write] ──► ctx.ask({ permission: "edit", patterns: [filepath] })
            │
            └──► [MCP] ──► ctx.ask({ permission: key, patterns: ["*"] })
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：PermissionNext 规则引擎

**作用**：评估权限请求，返回 allow/deny/ask 三种动作之一。

**关键源码**（`packages/opencode/src/permission/next.ts:131-161, 236-243`）：
```typescript
export const ask = fn(Request.partial({ id: true }).extend({ ruleset: Ruleset }), async (input) => {
  const s = await state()
  const { ruleset, ...request } = input
  for (const pattern of request.patterns ?? []) {
    const rule = evaluate(request.permission, pattern, ruleset, s.approved)
    if (rule.action === "deny")
      throw new DeniedError(ruleset.filter((r) => Wildcard.match(request.permission, r.permission)))
    if (rule.action === "ask") {
      return new Promise<void>((resolve, reject) => {
        s.pending[id] = { info: { id, ...request }, resolve, reject }
        Bus.publish(Event.Asked, info)
      })
    }
    if (rule.action === "allow") continue
  }
})

export function evaluate(permission: string, pattern: string, ...rulesets: Ruleset[]): Rule {
  const merged = merge(...rulesets)
  const match = merged.findLast(
    (rule) => Wildcard.match(permission, rule.permission) && Wildcard.match(pattern, rule.pattern),
  )
  return match ?? { action: "ask", permission, pattern: "*" }
}
```

**这段代码为什么值得看**：
- `findLast` 而非 `find`，说明后定义的规则优先（覆盖前面）。
- `Wildcard.match` 支持 `*` 通配符，如 `edit:*.md` 匹配所有 markdown 文件。
- 默认回退到 `ask`，安全优先。

### 机制 B：Bash 命令安全解析

**作用**：用 tree-sitter 解析 Bash AST，提取文件操作和外部目录访问。

**关键源码**（`packages/opencode/src/tool/bash.ts:78-160`）：
```typescript
async execute(params, ctx) {
  const tree = await parser().then((p) => p.parse(params.command))
  const directories = new Set<string>()
  const patterns = new Set<string>()

  for (const node of tree.rootNode.descendantsOfType("command")) {
    const command = []
    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i)
      if (!["command_name", "word", "string", "raw_string", "concatenation"].includes(child?.type)) continue
      command.push(child.text)
    }
    if (["cd", "rm", "cp", "mv", "mkdir", "touch", "chmod", "chown", "cat"].includes(command[0])) {
      for (const arg of command.slice(1)) {
        const resolved = await fs.realpath(path.resolve(cwd, arg)).catch(() => "")
        if (resolved && !Instance.containsPath(resolved)) {
          directories.add((await Filesystem.isDir(resolved)) ? resolved : path.dirname(resolved))
        }
      }
    }
    if (command.length && command[0] !== "cd") {
      patterns.add(commandText)
    }
  }

  if (directories.size > 0) await ctx.ask({ permission: "external_directory", patterns: globs })
  if (patterns.size > 0) await ctx.ask({ permission: "bash", patterns })
}
```

**这段代码为什么值得看**：
- tree-sitter 解析 AST 而非正则匹配，能处理复杂命令结构（如重定向、管道）。
- `Instance.containsPath(resolved)` 检查是否在工作区内，区分内部和外部目录访问。
- 对文件操作命令（`rm`, `cp`, `mv` 等）特别处理，提取路径并检查权限。

### 机制 C：工具权限过滤

**作用**：按模型和 Agent 权限禁用不合适的工具。

**关键源码**（`packages/opencode/src/tool/registry.ts:131-171`）：
```typescript
export async function tools(model: { providerID: string; modelID: string }, agent?: Agent.Info) {
  const tools = await all()
  const result = await Promise.all(
    tools
      .filter((t) => {
        const usePatch = model.modelID.includes("gpt-") && !model.modelID.includes("oss")
        if (t.id === "apply_patch") return usePatch
        if (t.id === "edit" || t.id === "write") return !usePatch
        return true
      })
      .map(async (t) => {
        // ...
      }),
  )
  return result
}
```

**这段代码为什么值得看**：
- GPT 系列使用 `apply_patch`（Codex 格式），其他模型使用 `edit`/`write`。
- 过滤在运行时进行，同一 Agent 配置可以适配不同模型。

### 机制 D：敏感文件保护

**作用**：对 `.env` 文件读取设置 `ask` 规则。

**关键源码**（`packages/opencode/src/agent/agent.ts:67-72`）：
```typescript
read: {
  "*": "allow",
  "*.env": "ask",
  "*.env.*": "ask",
  "*.env.example": "allow",
}
```

**这段代码为什么值得看**：
- `.env` 和 `.env.*` 需要权限确认，但 `.env.example` 允许直接读取（因为是模板文件，不含敏感信息）。
- 这是"最小权限原则"的实践。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 依赖 | 编排循环 | 工具执行前权限检查 | `ctx.ask` in `resolveTools` |
| 依赖 | 工具系统 | 每个工具内部调用权限 | `bash.ts`, `edit.ts` 等 |
| 输出到 | 状态管理 | 权限请求事件 | `Bus.publish(Event.Asked)` |
| 依赖 | 验证循环 | Doom Loop 检测触发权限 | `processor.ts:L152-176` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **权限检查应该下沉到工具层**：工具开发者最清楚自己的风险特征。
2. **默认拒绝优于默认允许**：`evaluate` 默认回退到 `ask`。
3. **用户愿意做权限决策**：`ask` 模式假设用户会及时响应权限请求。

### 6.2 这个设计的代价/风险

1. **权限逻辑分散**：每个工具自行调用 `ctx.ask`，新增工具时容易遗漏。
2. **MCP 工具权限粒度粗**：统一使用 `patterns: ["*"]`，无法精细化控制。
3. **规则合并简单**：`merge` 只是 `flat()`，没有处理冲突规则的逻辑。

### 6.3 如果要重新设计，可能会改变什么

1. **权限拦截器模式**：将 `ctx.ask` 提取到统一的包装层中。
2. **MCP 工具沙箱化**：为第三方 MCP 工具引入独立进程隔离。
3. **规则冲突检测**：在合并规则时检测并报告冲突。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：安全防护不是"加个密码"那么简单，而是一个**分层防御系统**。OpenCode 的设计表明，生产级 Agent 的安全需要三层防线：(1) 规则引擎（allow/deny/ask）定义策略、(2) 工具层解析实现具体检查（AST 解析命令）、(3) 模型层过滤避免不兼容调用。缺少任何一层，安全模型都会有漏洞。
