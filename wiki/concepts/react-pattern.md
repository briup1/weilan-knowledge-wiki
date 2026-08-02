---
type: concept
created: 2026-08-03
updated: 2026-08-03
sources: [hermes-agent, nanobot-framework-analysis, openclaw-framework-analysis, opencode-framework-analysis]
tags: [agent-architecture, reasoning, react, orchestration-loop]
---

# ReAct Pattern

ReAct（Reason + Act）是一种让 LLM Agent 通过**交替进行推理（Reasoning）和行动（Acting）**来解决任务的执行模式。它把 "先想一步，再做一步，再观察结果" 的循环显性化，使 Agent 能在复杂任务中逐步推进、动态调整策略。

## 核心思想

传统单次 prompt 的问题是：模型必须一次性生成完整答案。对于需要查询、计算、调用 API 的任务，模型要么瞎编，要么无法利用外部信息。

ReAct 的解决方式是把任务拆成一串 **Thought → Action → Observation** 步骤：

1. **Thought**：模型用语言描述当前状态、下一步计划、需要什么信息。
2. **Action**：模型输出一个工具调用（如搜索、计算、读文件）。
3. **Observation**：工具返回结果，被重新放入上下文。
4. 重复 1-3，直到模型认为任务完成，输出最终答案。

## 与编排循环的关系

ReAct 是 [[orchestration-loop]] 最常见的一种具体实现。编排循环描述的是更通用的控制结构（迭代、预算、中断、错误恢复），而 ReAct 描述的是**每次迭代里 LLM 应该产出什么**（推理 + 动作 + 观察）。

可以这样理解：

- **编排循环** = 高速公路基础设施（车道、限速、收费站）
- **ReAct** = 路上跑的一种车型（轿车，遵循基础设施规则）

## 最小代码示例

下面是一个不带任何框架的最小 ReAct 实现，展示核心循环：

```python
from typing import Callable
import json

# 假设的工具注册表
tools: dict[str, Callable] = {
    "search": lambda q: f"Search results for '{q}': Paris is the capital of France.",
    "calculate": lambda expr: str(eval(expr)),
    "finish": lambda answer: answer,
}

SYSTEM_PROMPT = """You solve tasks by alternating Thought, Action, and Observation.

Available tools:
- search(query): search the web
- calculate(expression): evaluate a math expression
- finish(answer): return the final answer

Respond in exactly one of these formats:

Thought: <your reasoning>
Action: <tool_name>(<arguments>)

or

Thought: <your reasoning>
Action: finish(<final_answer>)
"""

def react_loop(task: str, llm: Callable[[str], str], max_iterations: int = 5) -> str:
    history = f"Task: {task}\n"

    for i in range(max_iterations):
        response = llm(SYSTEM_PROMPT + "\n" + history)
        print(f"--- Iteration {i + 1} ---")
        print(response)

        # 解析 Thought 和 Action
        thought = ""
        action_line = ""
        for line in response.strip().split("\n"):
            if line.startswith("Thought:"):
                thought = line[len("Thought:"):].strip()
            elif line.startswith("Action:"):
                action_line = line[len("Action:"):].strip()

        if not action_line:
            raise ValueError("No Action found in model response")

        # 解析工具调用：tool_name(args)
        tool_name, _, args_str = action_line.partition("(")
        args_str = args_str.rstrip(")")
        tool_name = tool_name.strip()

        if tool_name == "finish":
            return args_str.strip('"')

        if tool_name not in tools:
            observation = f"Error: unknown tool '{tool_name}'"
        else:
            observation = tools[tool_name](args_str.strip('"'))

        history += f"\nThought: {thought}\nAction: {action_line}\nObservation: {observation}\n"

    raise RuntimeError("Max iterations exceeded")

# 用一个假的 LLM 模拟器来演示
def fake_llm(prompt: str) -> str:
    if "capital of France" in prompt and "Observation" not in prompt:
        return 'Thought: I need to find the capital of France.\nAction: search("capital of France")'
    if "Paris" in prompt:
        return 'Thought: The search result says Paris is the capital. I can finish.\nAction: finish("Paris")'
    return 'Thought: I need to think more.\nAction: finish("I don\'t know")'

answer = react_loop("What is the capital of France?", fake_llm)
print(f"Final answer: {answer}")
```

输出大致是：

```
--- Iteration 1 ---
Thought: I need to find the capital of France.
Action: search("capital of France")
--- Iteration 2 ---
Thought: The search result says Paris is the capital. I can finish.
Action: finish("Paris")
Final answer: Paris
```

## 生产级 ReAct 的关键增强

最小实现只展示思想，生产环境还需要：

| 增强项    | 作用                                       | 相关概念                   |
| ------ | ---------------------------------------- | ---------------------- |
| 结构化输出  | 用 JSON Schema / function calling 替代字符串解析 | [[output-parsing]]     |
| 迭代预算   | 限制最大轮数，防止无限循环                            | [[orchestration-loop]] |
| 工具权限校验 | 执行前检查工具是否允许被调用                           | [[validation-loop]]    |
| 上下文压缩  | 历史过长时摘要或截断                               | [[context-management]] |
| 错误恢复   | 工具失败时重试或降级                               | [[error-handling]]     |
| 可观测性   | 记录每轮 Thought/Action/Observation 为 trace  | [[agent-trace]]        |

## ReAct vs Plan-and-Execute

ReAct 是**边想边做**，每一步都根据最新观察调整。它的优点是灵活、适合动态环境；缺点是长任务里容易"短视"，过早陷入局部最优。

Plan-and-Execute 是**先规划后执行**：模型先生成完整计划，再按计划一步步执行。它的优点是目标明确、步骤清晰；缺点是环境变化时需要重新规划。

实际系统中常把两者结合：先用 Plan-and-Execute 生成高层计划，再用 ReAct 执行计划中需要动态调整的部分。

## 适用场景

- 需要多轮工具调用的问答（查资料、计算、验证）
- 环境反馈不确定的任务（如网页自动化、API 调试）
- 需要逐步推理的复杂问题（数学证明、代码调试）

## 常见问题

**Q: ReAct 必须输出 "Thought:" 文本吗？**
不一定。核心是把推理过程显性化，但形式可以是自然语言、JSON、函数调用参数，甚至内部 hidden reasoning。显性化主要是为了方便调试和可观测。

**Q: ReAct 和 CoT（Chain-of-Thought）有什么区别？**
CoT 只要求模型"一步一步想"，不强制与外部工具交互。ReAct 在 CoT 基础上增加了 Action 和 Observation，让模型能调用工具并基于真实反馈继续推理。

## 与其他概念的关系

- ReAct 运行在 [[orchestration-loop]] 内部。
- 每次 Action 前通常需要 [[prompt-building-for-agents]] 组装合适的 system prompt。
- Action 的输出由 [[output-parsing]] 解析为工具调用。
- 工具调用本身由 [[agent-tool-system]] 分发执行。
- 多轮历史由 [[agent-memory-system]] 或 [[state-management]] 维护。

## 原始文件

- 四框架实现对比见 [[agent-framework-12-dimensions-comparison]]
- 每个框架的源码调研见 [[hermes-agent-orchestration-loop]]、[[nanobot-framework-analysis]]、[[openclaw-framework-analysis]]、[[opencode-framework-analysis]]
