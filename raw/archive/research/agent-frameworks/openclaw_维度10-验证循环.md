# 维度名：验证循环（Validation Loop）

## 1. 一句话定位

验证循环是 OpenClaw 的"免疫系统"——它在运行时持续检测 Agent 行为、系统状态、配置正确性和安全合规性，发现问题后通过告警、阻断或自修复来防止小错误演变成系统故障。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

- **Agent 无限循环消耗 API 额度**：没有工具循环检测，一个陷入"反复 cat 同一文件"状态的 Agent 会持续调用 LLM API，直到额度耗尽。
- **损坏的配置静默导致异常行为**：配置错误（如无效的模型名称、错误的路径）不会立即报错，而是让 Agent 以不可预测的方式运行。
- **安全漏洞的代码进入生产**：Skills 是用户可编写的代码，如果没有扫描，恶意或危险的代码（如 `eval`、未授权网络请求）会被 Agent 执行。
- **会话状态损坏累积**：磁盘上的 session 文件可能因进程崩溃而损坏，如果不验证和修复，损坏会传播到后续所有交互。
- **上下文溢出的隐蔽性**：当上下文接近窗口上限时，系统行为会变得异常（模型开始"遗忘"），但用户和 Agent 都未必能直接感知到原因。

### 2.2 OpenClaw 的具体触发条件

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 相同工具重复调用 | `src/agents/tool-loop-detection.ts` | 每轮工具调用后检测历史模式 |
| 配置加载时 | `src/config/validation.ts` | `openclaw config validate` 命令触发 |
| Skill 安装/加载时 | `src/security/skill-scanner.ts` | 扫描 skill 代码中的危险模式 |
| Doctor 命令运行时 | `src/commands/doctor-*.ts` | 手动诊断命令 |
| 会话文件加载时 | `src/agents/session-file-repair.ts` | 自动修复损坏的 session 文件 |
| Compaction 完成后 | `src/agents/compaction.ts` | 验证摘要质量和 token 计数 |
| 工具结果进入上下文前 | `src/agents/pi-embedded-runner/tool-result-context-guard.ts` | 验证工具结果大小 |

---

## 3. 核心设计思路

### 3.1 抽象模型

验证循环可以抽象为一个**多层哨兵系统**：

```
输入流 → [格式验证] → [安全扫描] → [行为检测] → [状态诊断] → [反馈循环]
            ↑             ↑            ↑            ↑
         配置/schema    代码/工具    调用模式    文件/会话
```

每一层哨兵独立运作，发现问题后可以选择：
- **阻断**（block）：阻止当前操作继续
- **告警**（warn）：记录问题但允许继续
- **自修复**（repair）：自动修正问题后放行
- **反馈**（feedback）：将问题信息注入 LLM 上下文，让 Agent 自行调整

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 工具循环检测策略 | 向 LLM 注入警告消息，让 Agent 自行调整 | 强制终止会话 | `tool-loop-detection.ts` 返回 `message` 字段，说明作者认为 LLM 有能力在收到明确反馈后改变行为 |
| 配置验证时机 | 显式命令（`config validate`）+ 运行时懒加载 | 启动时严格验证所有配置 | `validation.ts` 主要是命令行工具，说明作者不想因配置问题阻止启动，而是在需要时检查 |
| Skill 安全扫描 | 静态分析（正则/AST 模式匹配） | 运行时沙箱执行检测 | `skill-scanner.ts` 用文件扫描，说明作者认为静态检测足够且运行时检测成本太高 |
| Session 修复 | 自动修复 + 备份原文件 | 报错让用户手动修复 | `session-file-repair.ts` 自动修复，说明作者认为 session 文件是内部细节，用户不应被暴露 |

### 3.3 数据流/控制流

```
[工具调用] → recordToolCall() → detectToolCallLoop()
                ↓
        [stuck?] ──是──→ 注入警告消息到 LLM
                ↓ 否
        [正常继续]

[配置变更] → config validate → Zod schema 验证
                ↓
        [有效?] ──否──→ 输出错误列表
                ↓ 是
        [配置生效]

[Skill 加载] → skill-scanner → 正则模式匹配
                ↓
        [发现危险?] ──是──→ 标记为 critical/warn
                ↓
        [加载/拒绝]
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：工具循环检测（已在错误处理维度详细分析，此处聚焦验证视角）

**作用**：从"验证"的角度，工具循环检测是在运行时验证 Agent 行为是否合理。

**设计意图**：不同于静态验证（配置、代码），工具循环检测是**动态行为验证**——它观察 Agent 在运行时的实际行为模式，判断是否存在无意义的重复。

**关键源码**（`src/agents/tool-loop-detection.ts:L372-401`）—— 三层阈值验证：

```typescript
export function detectToolCallLoop(
  state: SessionState,
  toolName: string,
  params: unknown,
  config?: ToolLoopDetectionConfig,
): LoopDetectionResult {
  const currentHash = hashToolCall(toolName, params);
  const noProgress = getNoProgressStreak(history, toolName, currentHash);

  if (noProgressStreak >= resolvedConfig.globalCircuitBreakerThreshold) {
    return {
      stuck: true,
      level: "critical",
      detector: "global_circuit_breaker",
      message: `CRITICAL: ${toolName} has repeated identical no-progress outcomes ${noProgressStreak} times...`,
    };
  }
  // ...
}
```

验证的分层设计：
- **warning**（10次）：通知 LLM，期望它自行纠正
- **critical**（20次）：更强硬的阻断
- **global_circuit_breaker**（30次）：彻底熔断

这种渐进式验证的原因是：**无法确定"重复"一定是错误**。Agent 可能确实需要多次检查同一资源（如等待文件生成）。只有在重复次数足够多、且结果始终无变化时，才判定为循环。

### 机制 B：配置验证

**作用**：确保用户配置符合预期的 schema 和约束。

**设计意图**：OpenClaw 的配置系统非常复杂（模型、provider、工具、通道、安全策略等），手动验证容易出错。Zod schema 验证在配置加载时提供结构化的错误报告。

**关键源码**（`src/config/validation.ts:L50-80`）—— 允许值收集：

```typescript
function collectAllowedValuesFromIssue(issue: unknown): AllowedValuesCollection {
  const record = toIssueRecord(issue);
  const code = typeof record.code === "string" ? record.code : "";

  if (code === "invalid_value") {
    const values = record.values;
    if (!Array.isArray(values)) {
      return { values: [], incomplete: true, hasValues: false };
    }
    return { values, incomplete: false, hasValues: values.length > 0 };
  }

  if (code === "invalid_type") {
    const expected = typeof record.expected === "string" ? record.expected : "";
    if (expected === "boolean") {
      return { values: [true, false], incomplete: false, hasValues: true };
    }
    return { values: [], incomplete: true, hasValues: false };
  }
  // ...
}
```

这段代码的设计意图是：**不仅告诉用户"错了"，还告诉用户"可以填什么"**。`collectAllowedValuesFromIssue` 从 Zod 的错误对象中提取合法的值列表，生成用户友好的提示。

### 机制 C：Skill 安全扫描

**作用**：在 Skill 代码执行前，静态扫描其中的危险模式。

**设计意图**：Skills 是用户（或第三方）编写的代码，Agent 会执行它们。如果 skill 中包含恶意代码（如删除文件、泄露密钥），后果严重。静态扫描作为第一道防线，在加载时就阻止危险代码。

**关键源码**（`src/security/skill-scanner.ts:L74-76`）—— 可扫描文件类型白名单：

```typescript
export function isScannable(filePath: string): boolean {
  return SCANNABLE_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}
```

只扫描 `.js/.ts/.jsx/.tsx` 等已知扩展名，避免对二进制文件、数据文件做无意义的扫描。

**关键设计**：扫描结果缓存（`L63: FILE_SCAN_CACHE`）。文件扫描是 I/O 密集型操作，通过 `mtimeMs` 判断文件是否变更，避免重复扫描未修改的文件。

### 机制 D：Doctor 诊断

**作用**：提供手动诊断工具，验证系统各组件的健康状态。

**设计意图**：自动验证覆盖不了所有场景。Doctor 命令让用户可以主动检查：状态完整性、安全配置、网关认证、沙箱环境等。

**关键源码**（`src/commands/doctor-state-integrity.ts:L46-62`）—— 目录权限检查：

```typescript
function canWriteDir(dir: string): boolean {
  try {
    fs.accessSync(dir, fs.constants.W_OK);
    return true;
  } catch {
    return false;
  }
}

function dirPermissionHint(dir: string): string | null {
  const uid = typeof process.getuid === "function" ? process.getuid() : null;
  const gid = typeof process.getgid === "function" ? process.getgid() : null;
  try {
    const stat = fs.statSync(dir);
    if (uid !== null && stat.uid !== uid) {
      return `Owner mismatch (uid ${stat.uid}). Run: sudo chown -R $USER "${dir}"`;
    }
  } catch {
    return null;
  }
  return null;
}
```

这段代码体现了验证的**可操作性**：不仅检测问题，还给出具体的修复命令。`dirPermissionHint` 将底层权限问题转化为用户可以直接执行的 shell 命令。

---

## 5. 与其他维度的交互

```
[验证循环] --(循环检测结果)--> [编排循环]
[验证循环] --(配置错误报告)--> [初始化与环境]
[验证循环] --(Skill 扫描结果)--> [工具系统]
[验证循环] --(会话完整性)--> [状态管理]
[验证循环] <--(工具调用历史)-- [工具系统]
[验证循环] <--(配置对象)-- [初始化与环境]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点 |
|---------|------|---------|--------------|
| 输出到 | 编排循环 | 工具循环检测结果影响 turn 执行 | `tool-loop-detection.ts` 的 `LoopDetectionResult` |
| 输出到 | 初始化与环境 | 配置验证结果指导启动流程 | `validation.ts` 的 `OpenClawSchema` |
| 输出到 | 工具系统 | Skill 扫描决定哪些工具可用 | `skill-scanner.ts` 的 `SkillScanSummary` |
| 输出到 | 状态管理 | Doctor 诊断会话文件完整性 | `doctor-state-integrity.ts` |
| 依赖 | 工具系统 | 工具调用历史用于循环检测 | `recordToolCall()` / `recordToolCallOutcome()` |
| 依赖 | 错误处理 | 重试机制为验证提供恢复能力 | `retry.ts` 的 `retryAsync` |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

1. **"LLM 会听从验证反馈"**：工具循环检测到问题后，选择向 LLM 发送警告而非强制终止。这假设 LLM 在收到明确指导后能自我纠正——但实际情况是，某些模型可能会无视警告继续循环。
2. **"静态扫描足够发现大部分安全问题"**：`skill-scanner.ts` 使用正则模式匹配而非动态分析。这假设危险代码模式（如 `eval`、`child_process.exec`）是显式的，但混淆过的恶意代码可能绕过静态检测。
3. **"配置验证不应阻塞启动"**：配置验证主要是命令行工具而非启动强制检查。这假设用户更倾向于"先启动再修复"，但这可能导致运行时的不可预测行为。

### 6.2 这个设计的代价/风险

1. **循环检测的误报成本**：如果 Agent 确实需要多次轮询（如等待 CI 完成），循环检测可能过早触发。`knownPollNoProgress` 检测器试图区分"轮询"和"循环"，但边界仍然模糊。
2. **静态扫描的覆盖盲区**：`skill-scanner.ts` 的正则模式无法检测逻辑漏洞（如 SSRF 通过拼接 URL 绕过），也无法检测运行时动态生成的代码。
3. **验证分散在多处**：工具循环检测、配置验证、安全扫描、Doctor 诊断各自独立，没有一个统一的"验证框架"。新增验证逻辑需要修改多个文件。

### 6.3 如果要重新设计，可能会改变什么

1. **统一的验证框架**：将各类验证（配置、行为、安全、状态）统一为一个可扩展的验证管道，每个验证器注册到框架中，统一处理报告和响应。
2. **循环检测的自适应阈值**：根据任务复杂度动态调整阈值。简单任务（如查看文件）的阈值可以更低，复杂任务（如调试程序）的阈值可以更高。
3. **Skill 的动态沙箱验证**：对高风险 Skill 在执行前进行动态行为分析（如监控网络请求、文件访问），而非仅依赖静态扫描。

### 6.4 对我自己设计 Agent 系统的启示

> **验证不是"检查点"，而是"持续运行的背景进程"**。OpenClaw 的设计启示是：验证应该嵌入到系统的每个关键路径中——工具调用时检测循环、配置加载时验证结构、代码执行前扫描安全、运行时诊断状态。验证的价值不在于"发现所有问题"，而在于"在问题造成严重后果前及时发现"。
