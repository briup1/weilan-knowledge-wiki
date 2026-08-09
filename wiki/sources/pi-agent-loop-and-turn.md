---
type: source
created: 2026-08-05
updated: 2026-08-05
raw: raw/archive/pi-agent-loop-and-turn.md
tags: [pi, agent-loop, runtime-turn, steering, follow-up]
---

# Pi 系列 02：Agent loop 与 Runtime Turn

## 来源信息

- 标题：Pi 系列 02｜Agent loop 与 turn：一次 prompt 为什么会拆成 4 趟
- 公众号：CodeAgent
- 发布时间：2026-06-05
- 原始链接：见归档原文

## 摘要

Pi 的 `turn` 不是完整的一问一答，而是 **assistant 的一次行动机会**。一次用户 prompt 可以包含多个 Runtime/Model Turn：模型请求工具、runtime 执行并回填结果，然后再给模型一次行动机会；直到模型只返回文本且没有 steering，内层循环才结束。外层循环随后处理 follow-up。

## 四个 Runtime Turn

```text
Business/User Turn：用户的一次 prompt ────────────────────────────────┐
                                                                    │
Runtime Turn 1：模型请求 bash(ls) → 执行并回填结果                    │
Runtime Turn 2：模型请求 read(package.json) → 执行并回填结果          ├─ 同一业务回合
Runtime Turn 3：模型请求 read(hello.mjs) → 执行并回填结果              │
Runtime Turn 4：模型输出最终文本 → 无工具、无 steering → 内层结束      │
                                                                    │
外层检查 follow-up → 无消息 → agent_end ─────────────────────────────┘
```

## 核心主张

1. **必须区分两种 Turn。** Business/User Turn 是用户输入到最终回答；Runtime/Model Turn 是一次模型响应及其触发的工具结果。
2. **内层循环处理工具调用和 steering。** 工具结果或运行中插话会进入下一 Runtime Turn 的上下文。
3. **外层循环处理 follow-up。** Agent 已结束当前回答后到达的新任务，会开启下一轮内层循环。
4. **真实 tool call 是继续循环的 ground truth。** 不应只依赖 provider 转换后的 `stopReason`。
5. **`firstTurn` 防止重复边界事件。** 外层入口已发出第一次 `turn_start`，内层首圈不能重复发，否则 UI 会出现空 Turn。
6. **steering 与 follow-up 不应合并。** 前者改变正在进行的任务，后者排队开启后续任务，消费时机和用户语义不同。

## 状态机

```text
runAgentLoop
  → agent_start + 首次 turn_start
  → 外层 while：获取 follow-up
       → 内层 while：
            注入 pending steering
            → 调模型
            → 若有 toolCall：执行、回填、turn_end、继续
            → 若无 toolCall 但有 steering：turn_end、继续
            → 若均无：turn_end、退出内层
       → 若有 follow-up：重新进入内层
       → 否则 agent_end
```

## 关联知识

- [[pi-coding-agent]]
- [[agent-turn]]
- [[orchestration-loop]]
- [[agent-runtime-event-stream]]
- [[tool-call-lifecycle]]
- [[pi-agent-runtime-architecture]]

## 本系列其他文章

- [[pi-agent-runtime-event-flow|01｜Runtime 事件流]]
- [[pi-agent-loop-and-turn|02｜Agent loop 与 turn]]
- [[pi-provider-unified-event-protocol|03｜Provider 与统一事件协议]]
- [[pi-tool-call-lifecycle|04｜ToolCall 的一生]]
- [[pi-tool-registration-and-extension|05｜工具供给、暴露与 Extension]]
- [[pi-custom-tools-and-extension|06｜customTools 与 Extension 实战]]
- [[pi-session-system|07｜Session 系统]]

## 原始文件

- [完整原文](../../raw/archive/pi-agent-loop-and-turn.md)
