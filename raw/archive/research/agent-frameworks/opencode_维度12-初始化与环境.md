# 维度：初始化与环境 (Init & Environment)

## 1. 一句话定位

初始化与环境是 OpenCode 的"地基工程"，通过 CLI 入口路由、项目边界探测、配置分层加载和实例上下文隔离，在一个不确定的运行环境中快速构建出确定性的 Agent 运行时。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **项目身份混乱**：如果无法将当前工作目录映射到稳定的项目 ID，不同项目的会话、权限、配置会串扰。`Project.fromDirectory` 使用 git root commit hash 作为项目 ID，即使目录移动也能保持稳定。
- **配置加载顺序失控**：如果没有 7 层配置合并策略，全局配置、项目配置、远程配置、企业策略之间的冲突无法解决。`Config.state` 实现了远程 well-known → 全局 → 项目 → `.opencode` → 内联 → 企业托管的分层覆盖。
- **实例重复创建**：如果没有 `Instance.provide` 的缓存机制，每次命令都会重新执行 Git 探测、配置加载、插件初始化等重操作，造成资源浪费和状态不一致。
- **数据库未迁移**：旧版本的 JSON 存储数据如果没有一次性迁移到 SQLite，用户的历史会话会"消失"。

### 2.2 OpenCode 的具体触发条件

- **CLI 启动时**：`index.ts:L55` 的 yargs 路由和 middleware 初始化
- **命令处理时**：`Instance.provide({ directory: process.cwd() })` 触发项目探测
- **项目切换时**：`Instance.reload()` 或 `Instance.dispose()` 管理实例生命周期

---

## 3. 核心设计思路

### 3.1 抽象模型

```
启动流程：

[CLI 入口] ──► yargs 解析 + middleware（日志初始化、环境标记、数据库迁移）
    │
    ▼
[命令处理器] ──► bootstrap() 或 Instance.provide()
    │
    ▼
[Instance.provide] ──► cache 检查 ──► 命中则复用，未命中则 boot()
    │
    ▼
[boot()] ──► Project.fromDirectory() ──► git 探测 + 项目 ID 计算
    │
    ▼
[context.provide(ctx)] ──► AsyncLocalStorage 绑定
    │
    ▼
[Config.load()] ──► 7 层配置合并
    │
    ▼
[子系统初始化] ──► Plugin、LSP、FileWatcher、Snapshot 等
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **项目 ID 基于 git root commit** | `git rev-list --max-parents=0 --all` | 目录路径哈希 | 目录移动后 ID 仍稳定，避免数据丢失 |
| **配置分层合并** | 7 层优先级 + 数组拼接 | 单层配置或完全覆盖 | 解决个人偏好 vs 团队规范 vs 企业策略的冲突 |
| **AsyncLocalStorage 上下文传递** | `Instance.directory` 等隐式访问 | 显式传递 `ctx` 参数 | 代码更简洁，但增加了"魔法"感 |
| **Instance 缓存** | `Map<string, Promise<Context>>` | 每次重新创建 | 避免重复执行昂贵的项目探测和配置加载 |

### 3.3 数据流/控制流

```
[用户命令行输入]
    │
    ▼
[yargs(hideBin(process.argv))]
    │
    ├──► middleware: Log.init() + 环境标记 + 数据库迁移检测
    │
    └──► 路由到具体命令处理器
            │
            ▼
    [Instance.provide({ directory, fn })]
            │
            ├──► cache.get(directory) ──► 命中？复用
            │
            └──► 未命中 ──► boot()
                    │
                    ├──► Project.fromDirectory(directory)
                    │       │
                    │       ├──► 向上查找 .git
                    │       ├──► 计算项目 ID（root commit hash）
                    │       └──► 返回 { project, sandbox }
                    │
                    ├──► context.provide(ctx) ──► AsyncLocalStorage 绑定
                    │
                    └──► input.init?.() ──► 插件、LSP 等子系统初始化
                            │
                            ▼
                    [执行用户命令 fn()]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：CLI 入口与路由

**作用**：yargs 路由、日志初始化、环境标记、数据库迁移检测。

**关键源码**（`packages/opencode/src/index.ts:55-128`）：
```typescript
let cli = yargs(hideBin(process.argv))
  .parserConfiguration({ "populate--": true })
  .scriptName("opencode")
  .wrap(100)
  .help("help", "show help")
  .version("version", "show version number", Installation.VERSION)
  .option("print-logs", { describe: "print logs to stderr", type: "boolean" })
  .option("log-level", { describe: "log level", type: "string", choices: ["DEBUG", "INFO", "WARN", "ERROR"] })
  .middleware(async (opts) => {
    await Log.init({
      print: process.argv.includes("--print-logs"),
      dev: Installation.isLocal(),
      level: (() => {
        if (opts.logLevel) return opts.logLevel as Log.Level
        if (Installation.isLocal()) return "DEBUG"
        return "INFO"
      })(),
    })

    process.env.AGENT = "1"
    process.env.OPENCODE = "1"
    process.env.OPENCODE_PID = String(process.pid)

    const marker = path.join(Global.Path.data, "opencode.db")
    if (!(await Filesystem.exists(marker))) {
      // ... 执行 JSON 到 SQLite 的一次性迁移
    }
  })
```

**这段代码为什么值得看**：
- `Installation.isLocal()` 区分开发环境和生产环境，自动调整日志级别。
- 环境标记 `AGENT=1`、`OPENCODE=1` 让子进程知道自己在 Agent 上下文中运行。
- 数据库迁移通过检测标记文件 `opencode.db` 避免重复执行。

### 机制 B：实例启动（boot 函数）

**作用**：构建实例上下文，通过 AsyncLocalStorage 绑定到异步调用链。

**关键源码**（`packages/opencode/src/project/instance.ts:33-52`）：
```typescript
function boot(input: { directory: string; init?: () => Promise<any>; project?: Project.Info; worktree?: string }) {
  return iife(async () => {
    const ctx =
      input.project && input.worktree
        ? { directory: input.directory, worktree: input.worktree, project: input.project }
        : await Project.fromDirectory(input.directory).then(({ project, sandbox }) => ({
            directory: input.directory,
            worktree: sandbox,
            project,
          }))
    await context.provide(ctx, async () => {
      await input.init?.()
    })
    return ctx
  })
}
```

**这段代码为什么值得看**：
- 条件分支 `input.project && input.worktree` 允许调用方跳过项目探测（测试场景）。
- `context.provide` 将实例上下文绑定到 AsyncLocalStorage，后续代码通过 `Instance.directory` 等 getter 隐式访问。
- `iife` 包装器在表达式位置编写异步逻辑。

### 机制 C：项目检测（Project.fromDirectory）

**作用**：从当前目录向上查找 `.git`，计算项目 ID，管理 sandboxes/worktrees。

**关键源码**（`packages/opencode/src/project/project.ts:97-138`）：
```typescript
export async function fromDirectory(directory: string) {
  const matches = Filesystem.up({ targets: [".git"], start: directory })
  const dotgit = await matches.next().then((x) => x.value)
  await matches.return()
  if (dotgit) {
    let sandbox = path.dirname(dotgit)
    const gitBinary = which("git")
    let id = await readCachedId(dotgit)

    if (!gitBinary) {
      return { id: id ?? "global", worktree: sandbox, sandbox, vcs: Info.shape.vcs.parse(Flag.OPENCODE_FAKE_VCS) }
    }

    const worktree = await git(["rev-parse", "--git-common-dir"], { cwd: sandbox })
      .then(async (result) => {
        const common = gitpath(sandbox, await result.text())
        return common === sandbox ? sandbox : path.dirname(common)
      })
      .catch(() => undefined)
    // ... ID 生成和数据库操作
  }
}
```

**这段代码为什么值得看**：
- `Filesystem.up()` 从当前目录向上遍历查找 `.git`，支持子目录启动。
- `readCachedId` 避免重复执行 Git 命令。
- 非 Git 项目回退到 `"global"` ID，但功能受限。

### 机制 D：配置加载体系

**作用**：7 层配置源按优先级合并，支持数组字段拼接。

**关键源码**（`packages/opencode/src/config/config.ts`）：
```typescript
export const state = Instance.state(async () => {
  let result: Info = {}
  // 1. 远程 well-known 配置
  for (const [key, value] of Object.entries(auth)) {
    if (value.type === "wellknown") {
      const response = await fetch(`${url}/.well-known/opencode`)
      result = mergeConfigConcatArrays(result, await load(JSON.stringify(remoteConfig), {...}))
    }
  }
  // 2. 全局配置
  result = mergeConfigConcatArrays(result, await global())
  // 3. 自定义配置路径
  if (Flag.OPENCODE_CONFIG) { ... }
  // 4. 项目配置
  if (!Flag.OPENCODE_DISABLE_PROJECT_CONFIG) { ... }
  // 5. .opencode 目录配置
  // 6. 内联配置
  // 7. 企业托管配置
})
```

**这段代码为什么值得看**：
- `mergeConfigConcatArrays` 对 `plugin` 和 `instructions` 字段进行集合合并，不是简单覆盖。
- 企业托管配置在最后，确保企业策略可以强制覆盖用户设置。
- `Instance.state` 缓存配置，同一实例内多次读取不重复执行。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 输出到 | 上下文管理 | 工作目录、git 状态 | `Instance.directory`, `Instance.project` |
| 输出到 | 记忆系统 | 项目 ID 作为外键 | `SessionTable.project_id` |
| 输出到 | Prompt构建 | 配置加载的指令文件 | `Config.get().instructions` |
| 依赖 | 工具系统 | 插件初始化 | `Plugin.init()` |
| 输出到 | 状态管理 | 实例缓存 | `Instance.state` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **Git 是项目边界的主要定义方式**：投入大量代码处理 Git 的各种情况，非 Git 项目只能得到简陋回退。
2. **配置冲突应以"叠加"为主**：`mergeConfigConcatArrays` 对插件和指令采用集合合并。
3. **实例生命周期与命令绑定**：`bootstrap()` 在回调结束后立即 dispose，每个命令是无状态的。

### 6.2 这个设计的代价/风险

1. **Git 依赖导致的性能开销**：`Project.fromDirectory` 每次都会执行多个 Git 子进程。
2. **AsyncLocalStorage 调试困难**：堆栈跟踪难以定位是哪个异步边界丢失了上下文。
3. **配置合并的不可预测性**：7 层配置源加上数组拼接语义，最终配置难以直观推断。
4. **数据库迁移阻塞**：首次运行时执行 JSON 到 SQLite 的迁移，可能长时间无响应。

### 6.3 如果要重新设计，可能会改变什么

1. **项目 ID 增加非 Git 支持**：使用目录路径哈希作为非 Git 项目的稳定 ID。
2. **配置引入"冻结"机制**：加载完成后调用 `Object.freeze()` 防止意外修改。
3. **实例缓存引入 TTL**：防止长时间运行的 serve 进程内存泄漏。
4. **数据库迁移改为后台异步**：在首次访问数据库时检测并执行，不影响 CLI 启动速度。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：初始化与环境不是"启动程序"那么简单，而是一个**确定性构建系统**。OpenCode 的设计表明，生产级 Agent 需要在不确定的环境中（不同安装方式、不同目录、不同配置）快速构建出确定的运行时上下文。这个过程中最关键的是三件事：(1) 稳定的身份标识（项目 ID）、(2) 清晰的分层配置（解决冲突）、(3) 高效的实例缓存（避免重复初始化）。缺少任何一点，系统要么无法正确隔离数据，要么会在复杂配置面前行为不可预测。
