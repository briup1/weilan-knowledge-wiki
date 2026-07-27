# 维度：状态管理 (State Management)

## 1. 一句话定位

状态管理是 OpenCode 的"神经系统"，通过 Session 状态机（idle/busy/retry）、目录级实例缓存和事件总线，确保多会话并发、长生命周期 Agent 循环和跨进程 UI 之间的状态一致性。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **会话重复执行**：同一 Session 上可能并行触发多个 `loop`，导致消息交错、工具调用重复。`assertNotBusy` 的存在就是为了拦截这种非法并发。
- **实例状态泄漏**：多个项目目录同时打开时，若没有 `Instance.state` 的目录级隔离，项目 A 的 Session 状态会污染项目 B。
- **UI 与后端不同步**：前端无法实时获知 Session 是 idle、busy 还是 retry，只能通过轮询数据库，延迟高且压力大。
- **资源泄漏**：`AbortController` 和挂起的 `callbacks` 如果没有 dispose 机制，会在 Instance reload 时持续占用内存。

### 2.2 OpenCode 的具体触发条件

- **用户发送消息时**：`SessionPrompt.prompt()` 调用 `start(sessionID)` 创建 AbortController
- **状态切换时**：`SessionStatus.set(sessionID, { type: "busy" })` 等
- **实例首次访问时**：`Instance.provide()` 检查 cache Map
- **事件发布时**：`Bus.publish()` 被各处调用

---

## 3. 核心设计思路

### 3.1 抽象模型

```
三层状态隔离：

Layer 1: Global State (进程级)
  GlobalBus: EventEmitter —— 跨进程广播

Layer 2: Instance State (目录级)
  State.create(rootFn, init, dispose):
    recordsByKey: Map<key, Map<initFn, {state, dispose}>>
    // 同一 init 函数在同一 key 下只执行一次

Layer 3: Session State (会话级)
  SessionStatus: Record<sessionID, {type: "idle" | "busy" | "retry", ...}>
  SessionPrompt.state: Record<sessionID, {abort, callbacks}>
```

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| **内存状态优先** | SessionStatus、Bus 订阅存内存，数据库为真相源 | 所有状态直接读写数据库 | 内存访问快，适合高频更新；数据库保证持久化 |
| **AbortSignal 作为取消协议** | 将 AbortController.signal 传递给所有异步操作 | 显式取消函数注册表 | AbortSignal 是 Web 标准，与 ai SDK 原生兼容 |
| **Bus 双模发布** | 既向 Instance 内订阅者分发，又向 GlobalBus 发射 | 纯 EventEmitter 或纯轮询 | 支持 Electron 等多进程架构 |
| **Zod Schema 一体** | 同时承担运行时校验、类型推导和文档 | TypeScript 接口 + 独立校验库 | 一份代码同时获得类型安全和运行时防御 |

### 3.3 数据流/控制流

```
[用户输入] → SessionPrompt.prompt(input)
                │
                ▼
        [assertNotBusy] ──► 若 state[sessionID] 存在则抛 BusyError
                │
                ▼
        [SessionPrompt.start] ──► 创建 AbortController
                │
                ▼
        [SessionPrompt.loop] ──► while(true)
                │
                ├──► [SessionStatus.set(sessionID, busy)] ──► Bus.publish
                │
                ├──► [LLM.stream] ──► 传入 abort.signal
                │
                └──► [SessionPrompt.cancel] ──► abort.abort()
                                │
                                ▼
                        [SessionStatus.set(sessionID, idle)] ──► Bus.publish
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：SessionStatus 状态机

**作用**：维护每个 session 的 idle/busy/retry 状态，通过 Bus 事件发布。

**关键源码**（`packages/opencode/src/session/status.ts:7-75`）：
```typescript
export namespace SessionStatus {
  export const Info = z.union([
    z.object({ type: z.literal("idle") }),
    z.object({ type: z.literal("retry"), attempt: z.number(), message: z.string(), next: z.number() }),
    z.object({ type: z.literal("busy") }),
  ])

  const state = Instance.state(() => {
    const data: Record<string, Info> = {}
    return data
  })

  export function set(sessionID: string, status: Info) {
    Bus.publish(Event.Status, { sessionID, status })
    if (status.type === "idle") {
      delete state()[sessionID]
      return
    }
    state()[sessionID] = status
  }
}
```

**这段代码为什么值得看**：
- 三态设计覆盖 Agent 全部生命周期阶段。
- `retry` 态携带 attempt/message/next，使 UI 可展示倒计时。
- `idle` 态主动 `delete` 释放内存。

### 机制 B：SessionPrompt.state 生命周期管理

**作用**：按 sessionID 存储 AbortController 与回调队列，管理循环生命周期。

**关键源码**（`packages/opencode/src/session/prompt.ts:66-85, 239-284`）：
```typescript
const state = Instance.state(
  () => {
    const data: Record<string, { abort: AbortController; callbacks: { resolve; reject }[] }> = {}
    return data
  },
  async (current) => {
    for (const item of Object.values(current)) {
      item.abort.abort()
    }
  },
)

function start(sessionID: string) {
  const s = state()
  if (s[sessionID]) return
  const controller = new AbortController()
  s[sessionID] = { abort: controller, callbacks: [] }
  return controller.signal
}
```

**这段代码为什么值得看**：
- `if (s[sessionID]) return` 确保单例运行，第二次调用会注册到 callbacks 队列等待结果。
- dispose 钩子自动取消所有运行中的操作。
- `defer(() => cancel(sessionID))` 利用 `using` 语法保证退出清理。

### 机制 C：Instance.state 目录级状态缓存

**作用**：为每个实例目录创建独立的状态空间，同一初始化逻辑只执行一次。

**关键源码**（`packages/opencode/src/project/state.ts`）：
```typescript
export namespace State {
  const recordsByKey = new Map<string, Map<any, Entry>>()

  export function create<S>(root: () => string, init: () => S, dispose?: (state: Awaited<S>) => Promise<void>) {
    return () => {
      const key = root()
      let entries = recordsByKey.get(key)
      if (!entries) {
        entries = new Map()
        recordsByKey.set(key, entries)
      }
      const exists = entries.get(init)
      if (exists) return exists.state as S
      const state = init()
      entries.set(init, { state, dispose })
      return state
    }
  }
}
```

**这段代码为什么值得看**：
- 以 `init` 函数引用作为 Map key，确保同一初始化逻辑在同一目录下只执行一次。
- 双层 Map 结构实现目录级和初始化逻辑级的双重隔离。

### 机制 D：Bus 事件总线

**作用**：Instance 内订阅 + 跨进程广播的双模事件总线。

**关键源码**（`packages/opencode/src/bus/index.ts`）：
```typescript
export namespace Bus {
  const state = Instance.state(() => {
    const subscriptions = new Map<any, Subscription[]>()
    return { subscriptions }
  })

  export async function publish(def, properties) {
    const payload = { type: def.type, properties }
    for (const key of [def.type, "*"]) {
      const match = state().subscriptions.get(key)
      for (const sub of match ?? []) { pending.push(sub(payload)) }
    }
    GlobalBus.emit("event", { directory: Instance.directory, payload })
    return Promise.all(pending)
  }
}
```

**这段代码为什么值得看**：
- wildcard 订阅 (`*`) 实现类似 MQTT 的 topic 通配符。
- `GlobalBus.emit` 桥接到进程级 EventEmitter，支持 Electron 多进程。

---

## 5. 与其他维度的交互

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|----------------|
| 输出到 | 编排循环 | 标记 busy/idle 状态 | `SessionStatus.set` |
| 依赖 | 错误处理 | retry 状态管理 | `SessionRetry` |
| 输出到 | UI | 状态变更事件 | `Bus.publish(Event.Status)` |
| 依赖 | 初始化与环境 | 实例上下文 | `Instance.state` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **Instance（目录）是天然的安全边界**：所有内存状态按目录隔离。
2. **Agent 循环是单线程的（per Session）**：`start()` 的单例保证假设同一 Session 不会并行执行 loop。
3. **事件总线的消费者是可信的**：`Bus.publish` 同步调用订阅者，假设不会阻塞。

### 6.2 这个设计的代价/风险

1. **内存泄漏风险**：全局 Map 没有清理机制，异常退出时状态对象可能滞留。
2. **事件顺序隐式依赖**：先 Instance 内订阅者后 GlobalBus，跨进程消费者可能依赖严格顺序。
3. **单进程假设**：`assertNotBusy` 只在单进程内有效，多进程负载均衡需要分布式锁。

### 6.3 如果要重新设计，可能会改变什么

1. **引入分布式锁**：支持多进程负载均衡。
2. **状态快照与回放**：定期快照到数据库，支持崩溃后精确恢复。
3. **Bus 背压机制**：慢订阅者不应阻塞发布者。

### 6.4 对我自己设计 Agent 系统的启示

> **最核心的启示**：状态管理不是"存储变量"，而是一个**分层隔离系统**。OpenCode 的三层隔离（进程→目录→会话）让复杂系统保持可管理性，每层只关心自己的边界。AbortSignal 作为跨库取消的通用语言，避免了各层自定义取消协议的碎片化。
