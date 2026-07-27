---
type: concept
created: 2026-07-26
updated: 2026-07-26
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, error-handling, retry, failover, resilience]
---

# Error Handling（错误处理）

## 定义

错误处理是 Agent 系统在真实生产环境中保持「不崩溃、不空转、不放大故障」的能力。它把所有异常（HTTP 错误、传输层抖动、工具崩溃、模型协议级错误）归一到结构化分类器上，再由主循环根据分类结果选择恢复动作。

## 为什么需要

- Agent 依赖外部 API、文件系统、网络，故障是常态而非例外。
- 不同 provider 的错误格式、状态码、嵌套包装差异很大，字符串匹配散落处理容易误判。
- 简单重试可能导致 thundering herd、配额更快耗尽、大会话反复断流。
- 单工具失败不应终止整个会话；错误信息应成为模型下一步决策的输入。

## 结构化错误分类

一个生产级错误分类器至少输出：

| 字段 | 含义 |
|---|---|
| `reason` | 错误类型标签 |
| `retryable` | 是否值得直接重试 |
| `should_compress` | 是否需要压缩上下文 |
| `should_rotate_credential` | 是否需要轮换凭证 |
| `should_fallback` | 是否需要切换 provider |
| `message` | 清洗后给用户/日志的信息 |

## 恢复动作阶梯

1. **凭证轮换** — 当前 key 疑似失效或限流
2. **图片/上下文缩小** — 请求体过大
3. **禁用 beta 功能重建请求** — OAuth/1M context 等权限问题
4. **Token 刷新** — 短周期凭证过期
5. **上下文压缩** — context-length 或网关断流推断
6. **Provider fallback** — 当前 provider 不可用
7. **中止** — 不可恢复错误或用户中断

## 关键机制

| 机制 | 作用 |
|---|---|
| 指数退避 + jitter | 避免多 session 同时重试 |
| 跨进程限流广播 | 文件级共享状态，防止全局 RPH 池被打爆 |
| metadata.raw 嵌套解析 | 识别网关包装后的真实错误 |
| 单工具失败降级 | 把异常转为 tool 消息内容，不中断主循环 |
| Orphan tool 补齐 | 防止协议要求不满足导致后续 400 死循环 |

## 四框架实现对比

| 维度 | Hermes | nanobot | OpenClaw | OpenCode |
|---|---|---|---|---|
| 分类方式 | `ClassifiedError` 纯函数，6 个布尔字段 | 分层降级：Provider/Registry/Loop/Memory 各层处理 | 未处理 rejection 分类：fatal/config/transient/abort | 三级分类：overflow/compaction、可重试、不可重试 |
| 重试策略 | 指数退避 + jitter；跨进程限流广播 | Provider 自动重试；Registry 注入 `_HINT` | 指数退避 + jitter + Retry-After；模型故障转移 | 指数退避；尊重 `retry-after` |
| 凭证/模型恢复 | 凭证轮换、模型 fallback | — | Fallback 模型 + Auth Profile 轮换 | — |
| 上下文恢复 | context-length 触发压缩 | Memory 失败降级为原始归档 | Compaction 超时快照回退 | overflow → compaction |
| 工具失败处理 | 单工具失败降级为字符串 | 错误字符串 + `_HINT` | 工具循环检测 | 工具修复 + Doom Loop 检测 |
| 独特设计 | metadata.raw 嵌套解析避免误判 | error 响应不写入历史防 400 循环 | cooldown 状态驱动的模型选择 | `fromError` 统一错误转换 |

## 与相关概念的关系

- 错误处理在 [[orchestration-loop]] 的每次 API 调用和工具执行后触发。
- context-length 错误需要 [[context-management]] 的压缩配合。
- 工具执行错误需要 [[validation-loop]] 的护栏记录。

## 当前证据

当前分析主要来自 [[hermes-agent]] 的 `error_classifier` 实现。其他框架待补充。
