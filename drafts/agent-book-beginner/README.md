# 项目：Agent 系统入门书（实习生比喻版）

**状态**: `writing`

本目录存放基于 `Harness_agent_docs` 整合而来的 Agent 系统入门书稿。

## 项目定位

- **阶段一（已完成）**：对四个开源 Agent 项目（Hermes Agent、nanobot、OpenClaw、OpenCode）的源代码调研。
- **阶段二（进行中）**：面向有 Python/Java 基础但无 Agent 经验的传统开发者，以"实习生入职第一天"的生活化比喻，讲解 Agent 系统的 12 个核心维度。

本书稿是 wiki 知识的**下游产物**：写作时应优先引用 `wiki/synthesis/` 中的综合结论，必要时回查 `raw/research/agent-frameworks/` 中的调研笔记。

## 目录结构

```
drafts/agent-book-beginner/
├── README.md              # 本文件
├── chapters/              # 书稿章节（按七节模板写作）
│   ├── 01_第0章_初识Agent：这位实习生是谁.md
│   ├── 03_第1章_工作节奏——编排循环.md
│   └── ...
└── research/              # 第一阶段调研文档（只读参考）
    ├── hermes_agent/      # Hermes Agent 各维度分析
    ├── nanobot/           # nanobot 各维度分析
    ├── openclaw/          # OpenClaw 各维度分析
    ├── opencode/          # OpenCode 各维度分析
    └── comparison/        # 横向对比文档
```

## 与 wiki 的关系

```
raw/research/agent-frameworks/   ← 调研笔记的规范存档位置
        ↓
wiki/sources/                    ← 待创建：每份调研的 source 页面
        ↓
wiki/entities/ + concepts/ + synthesis/  ← 结构化知识
        ↓
drafts/agent-book-beginner/chapters/     ← 本书稿
```

## 当前进度

- [x] 第 0 章：初识 Agent
- [x] 第一部分：Agent 的骨架
- [x] 第 1 章：工作节奏——编排循环
- [x] 第 2 章：双手——工具系统
- [x] 第 3 章：笔记本——记忆系统
- [x] 第 4 章：理解任务——Prompt 构建
- [x] 第 5 章：汇报成果——输出解析
- [x] 第二部分：Agent 的韧性
- [x] 第 6 章：工作台——状态管理
- [x] 第 7 章：抗压与纠错——错误处理
- [x] 第 8 章：注意力分配——上下文管理
- [x] 第 9 章：职业底线——安全防护
- [x] 第三部分：Agent 的进阶
- [x] 第 10 章：自我检查——验证循环
- [x] 第 11 章：团队协作——子 Agent 编排
- [x] 第 12 章：入职第一天——初始化与环境

## 写作约定

1. **优先用 wiki，少直接引用 research/**
   - 12 个维度的共性、差异、设计权衡，应到 `wiki/synthesis/` 中查证是否已有结论。
   - 只有当 wiki 未覆盖某个具体实现细节时，才回查 `research/<框架>/` 中的原始调研。

2. **源码核实不可跳过**
   - 书中引用的每一行代码都必须回到 `/home/weilan/workdir/excellent_project/*` 的源码中亲自确认。
   - 第一阶段调研文档是索引，不是最终依据。

3. **严格遵循七节模板**
   - 开篇故事 → 业务概念 → 必要设计 → 四项目实现对比 → 独特高价值设计 → 设计思想总结 → 本章小结

4. **术语即时解释**
   - 项目自创名词（如 Hermes 的「自注册」、OpenClaw 的「多层策略管道」、OpenCode 的「Doom Loop」）首次出现必须用 💡 提示框解释。

## 当前状态

- 17 个章节文件已就位，整体处于 `writing` 阶段。
- 下一步：按章节推进写作，优先引用 `wiki/synthesis/` 中的综合结论。
- `drafts/agent-book-beginner/research/` 中的原始调研资料已与 `raw/research/agent-frameworks/` 重复，将在 Task 3 中删除。
