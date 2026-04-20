---
title: "万字长文：个人如何用 Obsidian 搭建本地知识库——从入门到构建你的「第二大脑」"
source: "https://mp.weixin.qq.com/s/SPLTD-hFAsyYAA7V1lU8OA"
author:
  - "[[南哥]]"
published:
created: 2026-04-18
description: "引言：为什么你需要一个本地知识库？"
tags:
  - "clippings"
---
南哥 *2026年4月14日 00:30*

## 引言：为什么你需要一个本地知识库？

2026 年 4 月，前 OpenAI 联合创始人 Andrej Karpathy 公开了一个名为「LLM Wiki」的概念，在 48 小时内获得了 5000 颗 GitHub Star。他提出的核心观点振聋发聩： **停止每次从零推导，开始持续编译知识。**

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/3KPdfznexY03hkeLYWhAJLOeZyTStrPRELaMRpD4pFRjS0EYia52enzMDrnp4W37z0PWOocvkoZN6OefA93AD2ZOkADEYwDg8sp7As0RHYRI/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

什么意思？我们每天消费大量信息——技术文章、论文、播客、视频、会议纪要、灵感碎片——但绝大多数人的知识管理方式是「看过即忘」。下次遇到同样的问题，要么重新搜索，要么重新询问 AI。RAG（检索增强生成）每次都从原始材料中重新发现知识，没有积累效应。而一个结构化的知识库，是 **有状态的** ——新知识建立在旧知识之上，不断复利增长。

在 AI 时代，你的知识库不再只是一堆笔记文件。它是你的 **认知基础设施** ，是 AI 助手理解你、帮助你的上下文来源，是你几十年智识积累的持久载体。

那么问题来了：用什么工具来搭建？

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

答案是 **Obsidian** ——一款本地优先、基于 Markdown 的知识管理工具。它的工程团队只有 3 个人，公司总共只有 7 个人（和一只猫），估值却达到了 3.5 亿美元。没有融资，没有会议，全靠用户付费支撑。2700 多个社区插件构成了一个庞大的开源生态系统，覆盖了从任务管理、可视化思考到 AI 集成的方方面面。

这篇文章将从零开始，手把手带你用 Obsidian 搭建一个真正实用的本地知识库。我会覆盖核心理念、知识管理方法论、 **20 个实战插件** 的详细用法，以及如何用本地 AI 让你的知识库「活」起来。

---

## 第一章：为什么选择 Obsidian？

### 1.1 数据主权：你的笔记，你做主

Obsidian 与 Notion 代表了两种截然不同的信息管理哲学。

Notion 是云时代的巅峰之作：数据存储在官方服务器上，随时随地在线协作。但代价是——你的所有笔记、所有思考、所有知识积累，本质上寄存在别人的硬盘上。如果 Notion 倒闭、涨价、或者被收购后改变政策，你的数据命运掌握在他人手中。

Obsidian 的哲学完全相反： **所有笔记都以 `.md` 纯文本格式保存在你自己的硬盘上。** 没有专有格式，没有数据库锁定。即使 Obsidian 公司明天消失，你用任何文本编辑器都能打开这些文件。这不是一个功能特性，而是一个 **根本性的设计决策** 。

对于知识工作者来说，你的知识库可能会伴随你十年、二十年甚至一辈子。选择一个你能完全掌控数据的工具，不是偏执，而是远见。

### 1.2 双向链接与知识图谱：模拟大脑的思考方式

传统的文件夹式笔记管理是 **自上而下** 的——你必须事先决定一个笔记应该放在哪个文件夹里。但知识本身是网状的，一个概念可能同时属于多个领域。

Obsidian 的核心机制是 `[[双向链接]]` 。当你在笔记 A 中写下 `[[笔记 B]]` ，不仅 A 链接到了 B，B 也自动感知到了来自 A 的引用。随着笔记数量的增长，这些链接编织成一张 **知识图谱** ——你可以在图谱视图中看到整个知识网络的全貌，发现意想不到的连接。

这种 **自下而上** 的组织方式更接近人类大脑的工作模式：神经元之间通过突触相互连接，没有文件夹，没有层级，只有关系。

### 1.3 插件生态：3 个工程师 + 2700 个社区插件

受微软开源编辑器 VS Code 的启发，Obsidian 的创始人在产品底层构建了一个极其强大的插件系统。今天，社区已经贡献了超过 2700 个开源插件——从日历、看板、思维导图到复杂的 AI 大模型接入模块。

这相当于 Obsidian 拥有了一支由全球顶级极客组成的「编外工程军团」。官方团队只需要专注于完善底层的文本渲染、性能和基础 API，其余的「摩天大楼」由无数热爱它的用户来建造。

### 1.4 Obsidian 的「反硅谷」传奇

Obsidian 的故事始于 2020 年初疫情期间。两位核心创始人 Erica Xu（现 COO）和 Shida Li（现 CTO）是加拿大滑铁卢大学的校友和长期创业伙伴，被困在隔离房间里。他们试遍了市面上所有笔记软件，深感失望——他们想要一个纯文本、极快、完全离线、能长期安全存储知识的工具，但没有一款主流产品能完美解决这些痛点。

秉持着「买不到就自己造」的极客精神，2020 年 3 月，Obsidian 的第一个 Beta 版本在隔离期的「车库时代」中诞生。

这家公司至今没有接受过任何外部融资。在 SaaS 公司疯狂烧钱获客的今天，他们 100% 靠用户付费（跨平台 Sync 服务、一键 Publish 服务、商业许可证）维持运营。没有资本方的退出压力，不需要强行膨胀团队，也不需要往产品里塞臃肿的商业功能或出售用户数据来拉高营收。他们唯一的「老板」，就是每天使用软件的用户。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

没有会议，怎么保持团队对齐和凝聚？CEO Steph Ango 分享了他们运行两年多的秘密武器——「Ramblings」频道机制。每位成员有一个以自己名字命名的专属频道，只有频道主人能发帖，其他人只能在回复线程里互动。默认静音，没有阅读义务。工作和生活不分：频道里既有产品代码灵感和橡皮鸭调试请求，也有接孩子的抱怨、旅行照片和天马行空的「如果」想法。

### 1.5 2025-2026 年的重要更新

**Bases（核心功能）：** 这是 Obsidian 自 Properties 系统以来最大的更新。Bases 让你可以在笔记之上创建数据库视图——表格视图、卡片视图、支持筛选、排序、分组。它直接读取笔记的 YAML 前置元数据，不需要任何第三方插件。很多用户正在从 Dataview 插件迁移到 Bases 来处理简单的数据查询场景。

**Properties 系统增强：** 笔记的元数据管理变得更加直观，支持更丰富的属性类型和编辑方式。Properties 与 Bases 深度整合，形成了原生的无代码数据管理方案。

**Canvas 改进：** 画布文件现在支持反向链接检测，在图谱视图中被计入链接关系，可以嵌入看板和项目笔记。

---

## 第二章：知识管理方法论——先有体系，再有工具

工具再好，没有方法论也只是一堆散乱的文件。在 Obsidian 中，有三种经过验证的知识管理方法论值得掌握。

### 2.1 PARA 方法：给知识找到「位置」

PARA 方法由 Tiago Forte 提出，将所有信息按 **可操作性** 分为四个层级：

- **Projects（项目）：** 有明确目标和截止日期的当前工作。例如「写一篇公众号文章」「搭建个人网站」。
- **Areas（领域）：** 没有截止日期但需要持续关注的职责范围。例如「健康管理」「财务投资」「技术成长」。
- **Resources（资源）：** 感兴趣的主题或参考资料。例如「机器学习」「设计灵感」「烹饪食谱」。
- **Archives（归档）：** 已完成或不再活跃的内容。

在 Obsidian 中，PARA 直接映射为顶层文件夹结构：

```
Vault/
├── 1-Projects/
│   ├── 公众号文章计划/
│   └── 个人网站重构/
├── 2-Areas/
│   ├── 健康/
│   └── 投资/
├── 3-Resources/
│   ├── 机器学习/
│   └── 设计灵感/
└── 4-Archives/
```

PARA 的核心价值在于它回答了一个最基本的问题： **这条信息应该放在哪里？** 按照可操作性排序——如果它和当前项目相关，放 Projects；如果是持续关注的领域，放 Areas；如果只是参考资料，放 Resources；如果已经完成了，放 Archives。

### 2.2 Zettelkasten 方法：让知识「连接」起来

Zettelkasten（卡片盒笔记法）由德国社会学家 Niklas Luhmann 发明。他用这套方法在一生中出版了 70 多本书、400 多篇论文。核心原则有四条：

**原子化：** 每条笔记只包含一个想法。不要在一个文件里堆砌十个概念。一个笔记，一个思想单元。

**用自己的话重写：** 永远不要直接复制粘贴。用你自己的语言重新表述，才能真正内化知识。

**链接优于层级：** 笔记之间通过 `[[双向链接]]` 相连，而不是靠文件夹嵌套来组织。知识的价值来自于连接，而非分类。

**唯一标识：** 每条笔记有唯一的标识符。在 Obsidian 中，文件名天然就是标识符。

Zettelkasten 的魔力在于 **涌现性** ——当你积累了几百条原子笔记并用链接将它们连起来后，你会发现一些意想不到的连接，产生全新的洞察。这不是搜索能给你的，而是结构带来的。

### 2.3 MOC（Maps of Content）：给知识创建「地图」

MOC 的概念由 Nick Milo 在其 LYT（Linking Your Thinking）框架中推广。MOC 本质上是一个 **导航笔记** ——一个围绕某个主题，精心策划的链接列表。

它不是文件夹，而是一个更高层级的笔记，为一组相关的想法提供结构。例如：

```
# MOC - 机器学习

## 基础概念
- [[监督学习]]
- [[无监督学习]]
- [[强化学习]]

## 核心算法
- [[神经网络]]
- [[反向传播]]
- [[Transformer 架构]]

## 实践项目
- [[我的图像分类项目]]
- [[NLP 情感分析实验]]

## 参考资源
- [[吴恩达深度学习课程笔记]]
- [[Attention Is All You Need 论文精读]]
```

关键原则： **不要预先创建 MOC。** 让它们在某个主题的笔记数量增长到需要导航时自然涌现。三五条笔记不需要 MOC，三五十条才需要。

### 2.4 三种方法的融合

最强大的实践是将三者结合使用：

- **PARA 作为行动枢纽：** 文件夹结构用于组织活跃项目和持续关注的领域。
- **Zettelkasten 作为洞察引擎：** 原子化的链接笔记用于知识构建。
- **MOC 作为导航层：** 在两个系统之间架起桥梁。

PARA 回答「为了当前的工作，这条信息应该放在哪里？」，Zettelkasten 回答「这个想法和我已知的一切有什么关系？」，MOC 回答「围绕这个主题，我都积累了什么？」

三者功能互补、结构互不冲突，可以在同一个 Obsidian Vault 中无缝共存。

---

## 第三章：20 个实战插件——把 Obsidian 变成知识利器

以下 20 个插件按功能分类，每一个都是社区验证过的高频刚需。我会详细介绍每个插件的用法和实际场景，确保你不只是知道它们的名字，而是真正能用起来。

### 一、数据查询与管理

#### 插件 1：Dataview —— 把笔记变成数据库

**下载量：** 390 万+

**它做什么：** Dataview 是 Obsidian 的 SQL。它提供了一种查询语言（DQL），让你从笔记的 YAML 前置元数据和行内字段中动态生成表格、列表和任务视图。把你的静态笔记库瞬间变成一个动态数据库。

**实用场景——阅读仪表盘：**

在任意笔记中插入以下代码块：

```
\`\`\`dataview
TABLE rating AS "评分", author AS "作者", status AS "状态", dateRead AS "阅读日期"
FROM #book
WHERE status = "已读"
SORT rating DESC
\`\`\`
```

这会自动扫描所有带有 `#book` 标签的笔记，提取它们前置元数据中的评分、作者、状态和阅读日期，按评分降序排列生成一张动态表格。每当你新增一条读书笔记，表格自动更新。

你还可以用 Dataview 创建项目管理视图、每日待办汇总、知识库统计面板等。它是 Obsidian 从「笔记本」进化为「知识操作系统」的关键一步。

> **与 Bases 的关系：** Obsidian 原生的 Bases 功能提供了无代码的数据库视图，适合简单场景。Dataview 适合需要复杂查询逻辑、JavaScript 计算或高度定制化的高级用户。两者可以共存互补。

#### 插件 2：Omnisearch —— 真正好用的全文搜索

**它做什么：** 用智能权重算法对搜索结果进行相关性排名。支持 OCR 识别图片中的文字、PDF 全文索引。键盘导航友好。

Obsidian 自带的搜索功能只是基础的关键词匹配。当你的笔记库增长到几百上千条时，找到那条「你隐约记得写过但忘了叫什么名字」的笔记就变成了一件痛苦的事。

Omnisearch 用智能权重算法替代了简单的关键词匹配。输入一个模糊的概念，它就能按相关性排序给出结果——即使你的关键词不在标题里。更厉害的是，它支持 OCR，能搜索图片中的文字，也能索引 PDF 文件的内容。

**实用技巧：** 给 Omnisearch 绑定一个全局快捷键（比如 `Cmd+Shift+F` ），让它成为你知识库的「Google」。当笔记库超过几百条时，Omnisearch 的价值会越来越明显。

### 二、自动化与模板

#### 插件 3：Templater —— 超级模板引擎

**下载量：** 390 万+

**它做什么：** 远超原生模板功能。支持动态变量、JavaScript 执行、系统命令、日期计算、文件操作和用户交互提示。可以在笔记创建时自动运行逻辑。

**实用场景——智能每日笔记模板：**

```
---
date: <% tp.date.now("YYYY-MM-DD") %>
week: <% tp.date.now("wo") %>
tags: daily
---

# <% tp.date.now("YYYY年MM月DD日 dddd", 0, tp.file.title, "YYYY-MM-DD") %>

## 今日目标
- [ ] 

## 会议记录

## 灵感捕获

## 复盘
### 今天学到了什么？

### 明天要做什么？
```

每次创建每日笔记时，日期、星期自动填充。你还可以做更高级的事情：让模板弹出输入框询问项目名称，自动创建对应的文件夹结构，或者自动拉取昨天未完成的待办事项。Templater 的强大在于它的可编程性——任何你能用 JavaScript 描述的逻辑，都可以嵌入模板中。

#### 插件 4：QuickAdd —— 工作流胶水

**下载量：** 150 万+

**它做什么：** 提供三种核心能力——Template（从模板创建笔记）、Capture（快速追加内容到指定文件）、Macro（链式执行多个操作）。还支持 AI 命令和条件分支。

QuickAdd 是把你的各种操作「串联」起来的粘合剂。

**实用场景——闪念捕获：**

配置一个「Quick Capture」命令，绑定快捷键（比如 `Cmd+Shift+I` ）。按下快捷键后弹出输入框，输入任何想法，它自动追加到你的每日笔记的「灵感捕获」部分，带上时间戳。整个过程不到 2 秒，不打断你的工作流。

你还可以配置一个宏：一键创建会议笔记 → 应用模板 → 在每日笔记中添加链接 → 打开新笔记。把五步操作缩减为一步。社区里甚至有人用 QuickAdd 配合 AI 命令，实现「一键从 URL 生成阅读笔记」。

#### 插件 5：Linter —— 格式自动清洁工

**它做什么：** 自动强制执行一致的 Markdown 格式规范。可配置的规则涵盖标题样式、空行、YAML 前置元数据排序、尾部空格、换行符等。

当你的笔记来源多样——手动输入、模板生成、网页剪藏、AI 生成——格式很容易变得混乱。Linter 可以配置为在保存时自动运行，统一所有笔记的格式。

**推荐配置：** 设置为「保存时自动 Lint」，启用以下规则：

- YAML 键名统一排序
- 标题前自动空行
- 删除尾部空格
- 统一列表缩进
- 自动补全缺失的 YAML 区域

格式统一不仅让笔记赏心悦目，更重要的是保证 Dataview、Bases 和其他查询工具能正确解析元数据。这是知识库「卫生」的基础。

### 三、任务与项目管理

#### 插件 6：Tasks —— 跨笔记的任务管理

**下载量：** 320 万+

**它做什么：** 基于 Markdown 复选框的全功能任务系统。支持截止日期、计划日期、循环任务、优先级。配备强大的查询语言，可跨笔记全局过滤和展示任务。

Tasks 插件把 Obsidian 变成一个严肃的任务管理工具。关键在于：任务写在各自的笔记里（保持上下文），但可以在全局查询和过滤。

**用法示例：**

在任何笔记里写：

```
- [ ] 提交季度报告 📅 2026-05-01 ⏫
- [ ] 每周复盘 🔁 every week 📅 2026-04-20
- [ ] 阅读《思考快与慢》第三章 📅 2026-04-18
```

然后在一个「任务仪表盘」笔记中写查询：

```
\`\`\`tasks
not done
due before next week
sort by due
group by tags
\`\`\`
```

这样你就有了一个自动更新的、按截止日期和标签分组的全局待办视图。任务完成后在任何地方勾选，所有视图自动同步。

#### 插件 7：Kanban —— 可视化项目看板

**下载量：** 220 万+

**它做什么：** 基于 Markdown 的看板视图。列（如「待办」「进行中」「已完成」）和卡片都以 Markdown 格式存储，完全可搜索、可链接。

**实用场景——内容创作流水线：**

创建一个看板，列名为「灵感池」「正在写」「修改中」「已发布」。每张卡片就是一篇文章的笔记链接。把卡片在列之间拖拽就完成了状态流转。因为底层是 Markdown，所以这些卡片内容完全可搜索、可被 Dataview 查询。

还有人用 Kanban 管理阅读清单（「想读」「在读」「已读」）、学习计划（「待学」「学习中」「已掌握」）、甚至求职流程（「已投递」「面试中」「等 Offer」「已拒绝」）。可视化的列让你一眼看到全貌。

#### 插件 8：Calendar + Periodic Notes —— 时间轴导航

**Calendar 下载量：** 250 万+

**它做什么：** Calendar 在侧边栏提供月视图日历小部件，点击日期即可打开对应的每日笔记。有笔记的日期显示小圆点。Periodic Notes 将每日笔记扩展为每周、每月、每季、每年笔记，每个周期可配独立模板和文件夹。

这两个插件通常搭配使用。Calendar 提供了一个直观的时间导航界面——哪些日子有笔记一目了然。Periodic Notes 则让你建立多层次的时间复盘体系：

- **每日笔记：** 记录当天的工作、灵感、会议。
- **每周笔记：** 汇总一周进展，反思得失。
- **每月笔记：** 审视月度目标完成情况。
- **每年笔记：** 年度复盘与规划。

每个层级都可以配置独立的模板和存放文件夹。配合 Templater，你可以让周报模板自动汇总本周每日笔记中的关键条目。

### 四、可视化思考

#### 插件 9：Excalidraw —— 白板式视觉思考

**下载量：** 570 万+（社区最受欢迎的插件）

**它做什么：** 在 Obsidian 内集成完整的 Excalidraw 手绘白板。支持思维导图、流程图、架构图。关键特性是与 Obsidian 深度集成——画布元素可以链接到笔记、嵌入笔记内容，还有脚本引擎支持 JavaScript 自动化。

**为什么它是社区第一插件？** 因为 Excalidraw 不仅仅是画图工具——它是 **视觉化思考的工作台** ：

- 画布上的元素可以 **链接到 Obsidian 笔记** ，点击直接跳转
- 可以 **嵌入笔记内容** 到画布中，文字更新自动同步
- 支持 LaTeX 公式渲染
- 有脚本引擎，可以用 JavaScript 自动生成或修改图形
- 一个笔记文件可以同时作为普通文本笔记和 Excalidraw 画面的两面
- 不收集任何用户数据，完全本地运行

**实用场景：** 为一本书创建「一页纸总结」——用手绘方式把核心概念、关键引用、个人感悟可视化地组织在一起，每个元素链接到对应的详细笔记。或者画一张系统架构图，每个组件节点链接到对应的技术笔记。

Reddit 上有用户分享：「我用 Excalidraw 替代了所有思维导图工具。Excalidraw 比专门的思维导图插件更强大，因为它是自由画布，不受思维导图的树形结构限制。」

### 五、搜索与导航增强

#### 插件 10：Various Complements —— IDE 级自动补全

**它做什么：** 五种补全模式——当前文件词汇、全库词汇、自定义词典、内部链接补全（不用输入 `[[` 就能建议笔记链接）、前置元数据值补全。

这个插件把编程 IDE 的自动补全体验带到了笔记写作中。

**最强功能——内部链接补全：** 你不需要输入 `[[` 来创建链接。正常打字的时候，它会自动建议你库中已有的笔记名。比如你打「机器学」，它会弹出 `[[机器学习]]` 的链接建议。这极大地降低了创建双向链接的心理摩擦——你不再需要刻意记住要链接，而是在自然书写中完成链接。

**前置元数据值补全：** 在 YAML 区域输入 `status:` 时，它会自动建议你之前用过的值：draft、published、review。确保元数据值的一致性，不会因为拼写不统一导致 Dataview 查询漏掉数据。

#### 插件 11：Commander —— 自定义 UI 指挥官

**它做什么：** 让你把任何 Obsidian 命令添加到界面的任何位置——标题栏、页面头部、侧边栏（ribbon）、右键菜单、状态栏。支持自定义图标、重命名和颜色。

Commander 解决的问题是：Obsidian 有上百个命令，加上插件提供的命令可能有几百个，但你常用的可能就那十几个。与其记忆快捷键或反复打开命令面板，不如把最常用的命令以按钮形式放在触手可及的地方。

**推荐配置：**

- 侧边栏（ribbon）：添加「创建每日笔记」「打开图谱视图」按钮
- 状态栏：添加「运行 Linter」「打开 Omnisearch」按钮
- 页面头部：添加「切换阅读/编辑模式」「在新窗口打开」按钮

几分钟的配置，换来每天节省大量重复操作的时间。

#### 插件 12：Note Toolbar —— 笔记级工具栏

**它做什么：** 为不同类型的笔记创建上下文感知的工具栏。工具栏项可链接到命令、文件、URI、菜单和脚本。根据笔记所在文件夹或属性值自动匹配不同工具栏。内置 100+ 画廊项。

Note Toolbar 比 Commander 更精细——它可以根据笔记所在的文件夹或笔记的属性，显示不同的工具栏。

**实用场景：**

- 每日笔记自动显示：「添加任务」「打开日历」「运行周复盘模板」
- 项目笔记自动显示：「打开看板」「创建会议笔记」「查看项目任务」
- 阅读笔记自动显示：「添加高亮」「生成摘要」「链接到 MOC」

工具栏可以放在笔记顶部、底部或作为浮动按钮。不同类型的笔记有不同的工具集，真正实现了「上下文感知」的操作界面。

### 六、AI 集成——让知识库「活」起来

这一部分是 2025-2026 年最激动人心的变化。在 AI 集成路线上，Obsidian 与 Notion 走了完全不同的道路。

Notion AI 是高度商业化的「开箱即用」方案——按空格键就能调用 AI，但代价是你的数据必须完全暴露给云端的闭源大模型，并持续支付高额订阅费。

Obsidian 官方没有推出强制内置的闭源 AI，而是把选择权完全交给用户。社区涌现了大量开源 AI 插件，用户可以自由配置：追求性能可以接入 ChatGPT 或 Claude API；极致隐私可以通过 Ollama 在本地电脑上运行开源大模型，AI 在完全断网的情况下读取和分析你的私人笔记，不上传一个字节的数据。

#### 插件 13：Smart Connections —— AI 语义关联发现

**它做什么：** 使用 AI 嵌入向量在本地查找语义相关的笔记。侧边栏自动显示与当前笔记内容语义相似的笔记，即使它们没有共同的关键词。嵌入完全在设备上构建，数据不外传。

这是最能体现「AI + 知识库」威力的插件。传统搜索要求你知道要搜什么关键词；Smart Connections 则 **主动** 告诉你什么是相关的。

**工作原理：** 它用 AI 模型为你库中每条笔记生成嵌入向量（一种数学表示），然后通过向量相似度计算找到语义上相近的笔记。

**魔法时刻：** 当你在写一条关于「分布式系统」的笔记时，侧边栏自动浮现你几个月前写的「CAP 定理」笔记、「最终一致性」笔记、以及一篇你已经忘了自己剪藏过的论文——它们都是通过语义相似性找到的，不是关键词匹配。那些你以为已经「丢失」的知识，被 AI 重新发现。

**隐私优势与本地部署：** 推荐使用 Ollama + `nomic-embed-text` 模型构建嵌入。你的笔记内容 **一个字节都不会上传到云端** 。大型笔记库首次索引可能需要几小时，建议过夜运行。

#### 插件 14：Obsidian Copilot —— 本地 AI 对话助手

**它做什么：** 旗舰级 AI 插件。支持基于笔记库的 RAG（检索增强生成）对话——向 AI 提问，它从你的笔记中检索相关内容后生成回答。多供应商支持：OpenAI、Claude、Google、LM Studio、Ollama。完全本地化运行选项。

Copilot 让你可以直接和你的知识库「对话」。它会从你的笔记中检索相关内容，然后用 AI 模型生成回答——回答是基于你自己的知识，而不是互联网上的通用信息。

**完全本地化设置步骤（推荐隐私敏感用户）：**

1. 安装 Ollama： `brew install ollama` （macOS）或从官网下载
2. 拉取模型： `ollama pull llama3.2` （对话模型）、 `ollama pull nomic-embed-text` （嵌入模型）
3. 启动服务： `ollama serve`
4. 在 Copilot 设置中选择 Ollama 作为提供商，填入模型名

整个系统完全离线运行。不需要 API Key，不产生任何费用，你的笔记从头到尾都不会离开你的电脑。

这是 Obsidian 在 AI 时代的杀手锏组合： **本地 Markdown 笔记 + 本地 LLM = 完全私有的智能知识系统** 。这是 Notion AI 无论如何做不到的。

#### 插件 15：Text Generator —— AI 写作辅助

**它做什么：** 连接各种 AI 供应商（OpenAI、Claude、Google、Ollama 本地模型），在笔记中直接生成文本。支持自定义提示词模板，实现一致的生成风格。

**实用场景：**

- 选中一段粗糙的大纲，让 AI 扩展为完整段落
- 选中一段英文，让 AI 翻译为中文并保持技术术语准确
- 选中一段笔记，让 AI 生成简洁摘要
- 基于自定义模板，让 AI 根据你的笔记内容生成特定格式的输出（比如从阅读笔记生成书评）

与 Copilot 的区别在于：Copilot 侧重于「与知识库对话」，Text Generator 侧重于「在编辑器中直接辅助写作」。两者可以共存，各有侧重。

### 七、版本控制与备份

#### 插件 16：Git —— 免费的版本控制备份

**下载量：** 230 万+

**它做什么：** 完整的 Git 版本控制集成。自动定时提交和同步、启动时自动拉取、逐文件暂存、提交历史查看器、差异对比视图（精确到行级变更的指示器）、源控制面板。

这是保护你知识库安全的核心插件。配置好之后，它会：

- 每隔 10 分钟自动提交并推送到你的 GitHub/GitLab 私有仓库
- 每次打开 Obsidian 时自动拉取最新版本
- 提供完整的差异对比视图，你可以查看任何一条笔记被修改的具体内容
- 出了问题随时可以回滚到任何一个历史版本

**为什么比 iCloud / OneDrive 同步更好？** 因为 Git 提供的是 **版本历史** ，不只是文件备份。你可以看到每条笔记每一次被修改的具体内容——改了什么、什么时候改的。对于一个你打算维护十年的知识库来说，这个能力价值巨大。

而且它是完全免费的——GitHub 私有仓库不收费。

#### 插件 17：BRAT —— Beta 插件管理器

**它做什么：** 让你直接从 GitHub 仓库安装和自动更新 Beta 版插件，绕过官方社区插件商店的审核等待。

Obsidian 的社区插件商店有审核流程，新插件或新版本的发布通常要等几天到几周。BRAT 让你可以提前使用开发者发布在 GitHub 上的最新版本。

**实用场景：** 某个 AI 插件刚发布了 Beta 版，增加了 Ollama 本地模型支持。在 BRAT 中粘贴 GitHub 仓库地址，一键安装。如果出问题，一键移除。BRAT 还会自动检查更新，确保你始终使用最新的 Beta 版本。

对于喜欢尝鲜的用户来说，BRAT 是必装插件。Reddit 社区里有不少尚未上架官方商店但质量很高的插件（比如 Sortable），都需要通过 BRAT 安装。

### 八、界面与体验优化

#### 插件 18：Style Settings —— 主题深度定制

**下载量：** 220 万+

**它做什么：** 为主题和插件暴露的 CSS 变量提供图形化的调整界面——颜色选择器、滑块、开关、下拉框。支持设置导入/导出。

Obsidian 有丰富的社区主题（强烈推荐 Minimal 主题），但开箱即用的主题不一定完全符合你的审美和使用习惯。Style Settings 让你不用写一行 CSS 代码，就能通过友好的设置面板调整主题的方方面面。

**搭配 Minimal 主题的推荐设置：**

- 调整标题字体大小和颜色，让层级一目了然
- 设置适合你屏幕的行宽度（太宽阅读不舒服，太窄浪费空间）
- 开启「Focus Mode」减少视觉干扰
- 调整侧边栏宽度和背景色
- 自定义代码块的字体和配色

设置完成后可以导出为 JSON 文件备份，换电脑时一键恢复。

#### 插件 19：Supercharged Links —— 给链接加上视觉标记

**它做什么：** 基于笔记的元数据（标签、属性值）自动为链接添加样式（颜色、图标、前缀 emoji）。

这是一个让你的知识库变得「可扫描」的利器。当你在一条 MOC 笔记中面对几十个链接时，如何快速分辨哪些是书籍笔记、哪些是项目、哪些已完成、哪些正在进行中？

**用法示例：** 配合 CSS 片段，实现：

- 带有 `#book` 标签的笔记链接前面显示书本 emoji
- 状态为「进行中」的项目笔记链接显示为绿色
- 已归档的笔记链接显示为灰色
- 带有 `#important` 标签的笔记链接加粗显示

Reddit 用户 ClosingTabs 分享了一段用法：

```
.data-link-text[data-link-path*="Books" i] {
    color: #88AC4B;
    &::before {
        content: "📚 ";
    }
}
```

这让 `Books` 文件夹下的所有笔记链接自动变为绿色并带上书本 emoji。不用点开就能快速辨别类型。

#### 插件 20：Meta Bind —— 笔记内交互组件

**它做什么：** 在笔记内创建交互式输入字段、元数据展示和按钮。输入字段绑定到前置元数据属性并保持实时同步。是已停更的 Buttons 插件的继任者。

Meta Bind 让你的笔记从「静态文本」变成「微型应用」。

**实用场景——读书笔记交互面板：**

```
---
status: reading
progress: 45
rating: 0
---

阅读状态：\`INPUT[toggle:status]\`
阅读进度：\`INPUT[slider(min:0, max:100):progress]\`%
我的评分：\`INPUT[slider(min:0, max:5):rating]\` / 5
```

你可以在笔记中直接拖动滑块、点击开关来更新元数据，而不需要手动编辑 YAML。这些值自动同步到前置元数据，意味着 Dataview 和 Bases 可以立即查询到更新后的值。

还可以创建按钮来触发 Obsidian 命令——比如一个「标记为已读」按钮，点击后自动将 `status` 改为 `done` 、 `date_finished` 填入今天的日期。

---

## 第四章：从零开始搭建你的知识库——实操指南

了解了方法论和插件，现在进入实操环节。

### 4.1 第一步：安装与基础设置

1. **下载 Obsidian：** 从 obsidian.md 下载对应平台的版本（Windows、macOS、Linux、iOS、Android 全平台支持）。
2. **创建 Vault：** 选择一个你能完全控制的本地文件夹作为 Vault 目录。建议放在 `~/Documents/MyBrain` 或类似路径。避免放在云同步服务的特殊目录中（后续可以手动配置同步）。
3. **基础设置推荐：**
- 编辑器 → 开启「行号显示」
	- 编辑器 → 开启「严格换行」（Strict line breaks）
	- 文件与链接 → 开启「自动更新内部链接」（文件重命名时自动更新所有引用它的链接）
	- 外观 → 安装 Minimal 主题（社区最受欢迎的主题之一）
	- 核心插件 → 开启「图谱视图」「反向链接」「标签面板」「大纲」

### 4.2 第二步：建立文件夹结构

基于 PARA 方法，创建以下结构：

```
MyBrain/
├── 00-Inbox/          # 所有新内容先进入收件箱
├── 01-Projects/       # 当前活跃项目
├── 02-Areas/          # 持续关注的领域
├── 03-Resources/      # 参考资料和兴趣主题
├── 04-Archives/       # 已完成或不再活跃的内容
├── 05-Templates/      # 模板文件
├── 06-Attachments/    # 图片、PDF 等附件
└── 07-Daily/          # 每日笔记
```

**重要原则：** 不要在文件夹结构上花太多时间。Obsidian 的核心不是文件夹，而是链接。文件夹只是一个大致的分区，真正的组织靠 `[[链接]]` 和 MOC。你不需要为每个子主题创建子文件夹——让笔记的链接关系来描述结构。

### 4.3 第三步：分批安装插件

不要一次装 20 个插件。按优先级分批安装，每批适应一周再加新的：

**第一批——基础必装（第 1 周）：**

1. Templater —— 创建智能模板
2. Calendar + Periodic Notes —— 每日笔记导航
3. Linter —— 格式统一
4. Git —— 版本备份

**第二批——效率提升（第 2 周）：**

5\. Dataview —— 数据查询

6\. Tasks —— 任务管理

7\. QuickAdd —— 快速捕获

8\. Various Complements —— 自动补全

**第三批——体验优化（第 3 周）：**

9\. Commander —— UI 定制

10\. Style Settings —— 主题调整

11\. Omnisearch —— 增强搜索

12\. Note Toolbar —— 上下文工具栏

**第四批——进阶功能（第 4 周）：**

13\. Excalidraw —— 可视化思考

14\. Kanban —— 项目看板

15\. Meta Bind —— 交互组件

16\. BRAT —— Beta 插件管理

17\. Supercharged Links —— 链接视觉标记

**第五批——AI 集成（按需）：**

18\. Smart Connections —— 语义关联

19\. Copilot —— AI 对话

20\. Text Generator —— AI 写作

### 4.4 第四步：创建核心模板

利用 Templater 创建以下基础模板，保存在 `05-Templates/` 文件夹中：

**每日笔记模板 (tp-daily.md)：**

```
---
date: <% tp.date.now("YYYY-MM-DD") %>
tags: daily
---

# <% tp.date.now("YYYY年MM月DD日 dddd") %>

## 今日焦点
> 今天最重要的一件事是什么？

- [ ] 

## 工作记录

## 灵感捕获

## 今日复盘
- 学到了什么：
- 感恩什么：
- 明天要做：
```

**阅读笔记模板 (tp-book.md)：**

```
---
title: <% await tp.system.prompt("书名") %>
author: <% await tp.system.prompt("作者") %>
status: reading
rating: 0
progress: 0
tags: book
date_started: <% tp.date.now("YYYY-MM-DD") %>
---

# 《<% tp.frontmatter.title %>》阅读笔记

## 核心观点
1. 

## 关键摘录
> 

## 个人思考

## 行动项
- [ ] 

## 相关笔记
-
```

**Zettelkasten 原子笔记模板 (tp-zettel.md)：**

```
---
date: <% tp.date.now("YYYY-MM-DD HH:mm") %>
tags: 
source: 
---

# <% tp.file.title %>

---
## 相关笔记
- 

## 参考来源
-
```

**项目笔记模板 (tp-project.md)：**

```
---
status: 进行中
priority: 
due: 
tags: project
date_created: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.file.title %>

## 项目目标

## 关键成果
- [ ] 
- [ ] 
- [ ] 

## 进展日志

### <% tp.date.now("YYYY-MM-DD") %>
- 

## 相关资源
- 

## 复盘（项目结束后填写）
- 做得好的：
- 可以改进的：
- 学到了什么：
```

### 4.5 第五步：建立工作流

一个完整的知识库工作流应该是这样的循环：

```
捕获 → 处理 → 组织 → 连接 → 产出 → 复盘
```

**捕获（Capture）：** 一切新信息先进入 `00-Inbox` 。使用 QuickAdd 的快速捕获功能，一键把灵感、链接、想法丢进收件箱。不要在捕获阶段做判断，先存下来。在手机上可以用 Obsidian 移动端的快速笔记功能。

**处理（Process）：** 定期清空收件箱（建议每天或每两天一次）。对每条信息做决策：

- 这是一个独立的想法？→ 创建 Zettelkasten 原子笔记，用自己的话重写
- 这属于某个项目？→ 移入对应项目文件夹
- 这是参考资料？→ 移入 Resources，添加标签和元数据
- 没有价值？→ 直接删除（不要囤积）

**组织（Organize）：** 把笔记放到 PARA 结构的正确位置。添加标签和 YAML 前置元数据。确保 Linter 保持格式统一。

**连接（Connect）：** 这是最关键的一步。为每条新笔记至少添加一个 `[[链接]]` 到已有笔记。问自己：「这条信息和我已知的什么有关系？」如果某个主题的笔记越来越多（超过 20-30 条），考虑创建一个 MOC。

**产出（Create）：** 知识库的终极目的不是收藏，而是产出——文章、演讲、方案、决策。当你需要写一篇文章时，从 MOC 出发，遍历相关的原子笔记，素材已经在那里了。

**复盘（Review）：** 利用 Periodic Notes 进行周复盘和月复盘。回顾这段时间新增了什么知识，有什么连接，有什么遗漏。

### 4.6 第六步：配置 Git 自动备份

1. 在 GitHub 创建一个私有仓库（例如 `my-brain` ）
2. 在 Vault 根目录初始化 Git：
	```
	cd ~/Documents/MyBrain
	git init
	git remote add origin git@github.com:你的用户名/my-brain.git
	```
3. `.gitignore`
	```
	.obsidian/workspace.json
	.obsidian/workspace-mobile.json
	.trash/
	```
4. 在 Git 插件设置中配置：
- 自动提交间隔：10 分钟
	- 自动推送：开启
	- 启动时自动拉取：开启
	- 提交信息格式： `vault backup: {{date}}`

从此以后，你的知识库每 10 分钟自动备份到 GitHub，拥有完整的版本历史。完全免费。

---

## 第五章：AI 时代的知识库进阶——从笔记到「第二大脑」

### 5.1 Karpathy 的 LLM Wiki：AI 驱动的知识编译

2026 年 4 月，Karpathy 提出的 LLM Wiki 概念引爆了技术圈。其核心类比极其精妙：

- `raw/` = 源代码
- LLM = 编译器
- `wiki/` = 可执行输出
- `lint` = 测试
- `queries` = 运行时

三层架构和三个核心操作：

```
知识库/
├── raw/        # 不可变的原始资料（文章、论文、网页剪藏）
├── wiki/       # AI 生成和维护的 wiki 页面
│   ├── index.md    # 全局目录
│   └── log.md      # 操作日志
└── CLAUDE.md   # 模式文件：告诉 AI 如何操作这个 wiki
```
- **摄取（Ingest）：** 把原始资料丢进 `raw/` ，AI 阅读后提取关键信息，整合到 wiki 页面中。一次摄取可能触发数十个 wiki 页面的更新。
- **查询（Query）：** 向 AI 提问，它先读索引找到相关页面，然后深入阅读并综合回答，附带 `[[wiki-link]]` 引用。
- **检查（Lint）：** 健康检查——发现并修复孤立页面、过时声明、断裂的交叉引用、结构问题。

**为什么在个人知识库规模上比 RAG 更好？** 在个人规模（约 100 篇文章、约 40 万字）下，Karpathy 认为结构化的 Markdown 加摘要和索引文件， **比向量数据库 RAG 更有效** ：

- RAG 每次查询都从零发现知识（没有积累）
- LLM Wiki 是有状态的——知识建立在先前知识之上
- 没有嵌入、没有向量搜索、没有基础设施开销
- LLM 通过摘要和索引文件导航，在个人规模下足够了

值得注意的是，Karpathy 使用 **Obsidian Web Clipper** 将网页内容转换为 Markdown 文件进行摄取。Obsidian 是这个模式天然的载体。

### 5.2 LLM Wiki v2：知识的生命周期管理

基于 agentmemory 项目的实战经验，LLM Wiki v2 对原始方案做了多个关键扩展。这些扩展回答了一个核心问题： **当知识库规模增长时，如何防止它腐烂？**

**置信度评分（Confidence Scoring）：** 原始 Wiki 把所有内容当作永远等效的。但实际上，知识是有生命周期的。v2 为每个事实附加置信度分数——多少来源支持它、最近一次确认是什么时候、是否有任何矛盾。

当 AI 写下「项目 X 使用 Redis 作为缓存」，这个声明知道自己来自 2 个来源，3 周前最后一次确认，置信度 0.85。置信度随时间衰减，被强化时回升。这把 Wiki 从一个等权重的声明集合，变成了一个活的模型——AI 可以说「我对 X 相当确信，但对 Y 不太确定」。

**记忆层级（Memory Tiers）：** 原始观察和已确立的事实不是一回事。v2 构建了一个升级管道：

- **工作记忆：** 最近的观察，尚未处理。就像你刚看到的一条推文。
- **情景记忆：** 会话摘要，从原始观察中压缩而来。就像你对今天学习会议的记忆。
- **语义记忆：** 跨会话的事实，从情景中整合而来。就像你对某个技术框架的理解。
- **程序记忆：** 工作流和模式，从重复的语义中提取。就像你解决某类问题的方法论。

每个层级比下一个更压缩、更确信、更持久。AI 随着证据的积累将信息向上层级提升。这就是从「我见过一次」到「这就是事物运作的方式」的过程。

**遗忘曲线（Forgetting Curve）：** 不是所有知识都应该永远保留。一个从不遗忘的 Wiki 会变得嘈杂。v2 实现了一个保留曲线：几个月没有被访问或强化的知识会逐渐淡化——不是删除，而是降低优先级。这借鉴了艾宾浩斯遗忘曲线：保留率随时间指数衰减，但每次强化（访问、被新来源确认）都会重置曲线。架构决策缓慢衰减，瞬态 Bug 快速衰减。

**知识图谱（Knowledge Graph）：** 不只是带链接的平面页面。v2 在页面之上叠加了一个类型化的知识图谱——提取实体（人、项目、库、概念、文件、决策），建立类型化关系（「使用」「依赖」「矛盾」「导致」「修复」「取代」）。当有人问「升级 Redis 会有什么影响？」，AI 不是做关键词搜索，而是从 Redis 节点出发，沿着「依赖」和「使用」边向外遍历，找到所有下游影响。

**混合搜索（Hybrid Search）：** 当知识库超过 200 页后，index.md 就不够用了。v2 采用三路搜索融合：

- BM25：关键词匹配（精确术语）
- 向量搜索：语义相似度（概念层面）
- 图遍历：实体感知的关系遍历（结构层面）

用互惠排名融合（Reciprocal Rank Fusion）合并结果。实测在 LongMemEval-S 基准上达到 95.2% 的准确率。

**自动化钩子（Automation Hooks）：** 原始方案一切都是手动的——你丢入来源并告诉 AI 处理。v2 实现了事件驱动的自动化：

- 新来源到来 → 自动摄取、提取实体、更新图谱、更新索引
- 会话开始 → 基于最近活动从 Wiki 加载相关上下文
- 会话结束 → 将会话压缩为观察、归档洞察
- 按计划 → 定期检查、整合、衰减

杀死 Wiki 的是簿记工作——而簿记工作现在完全自动化了。

**矛盾解决（Contradiction Resolution）：** 原始方案只标记矛盾。v2 更进一步——AI 基于来源时效性、来源权威性和支持证据数量，提出哪个声明更可能正确。人类可以覆盖，但默认行为通常是对的。

### 5.3 在 Obsidian 中渐进式落地

你不需要一步到位实现完整的 LLM Wiki v2。可以渐进式地在 Obsidian 中落地：

**第一阶段：手动 + Obsidian 核心功能（现在就能开始）**

利用 Obsidian 已有的能力建立基础：

- `raw/` 文件夹 → 使用 Obsidian Web Clipper 剪藏网页
- `wiki/` 文件夹 → 手动写 Zettelkasten 笔记
- `index.md` → MOC 导航笔记
- Dataview → 动态索引和查询
- Linter → 定期格式健康检查

这个阶段完全不需要 AI。核心价值在于建立「从原始资料到精炼知识」的流程习惯。

**第二阶段：引入本地 AI 辅助**

加入 Smart Connections 和 Copilot/Text Generator：

- Smart Connections → 自动发现语义关联（向量搜索层）
- Copilot + Ollama → 本地 RAG 对话（可以问知识库问题）
- Text Generator → 辅助将原始资料提炼为笔记

这个阶段，AI 成为你的「初级助手」——帮你发现连接、回答问题、辅助写作，但最终决策和组织仍然由你控制。

**第三阶段：构建自动化流水线**

利用 Templater 的系统命令功能 + QuickAdd 宏，构建自动化流程：

- 新文章剪藏后自动触发 AI 摘要
- 每日笔记创建时自动拉取未完成任务
- 定期运行 Linter 检查格式健康度
- 每周自动生成知识库增长统计

**第四阶段：完整的知识生命周期（前沿探索）**

社区已经有多个开源项目在 Obsidian 中实现 Karpathy 的 LLM Wiki 模式：

- **obsidian-wiki** —— AI 代理自动构建和维护 Obsidian Wiki 的框架
- **obsidian-llm-wiki-local** —— 100% 本地实现，使用 Ollama，零云端依赖
- **claude-obsidian** —— Claude + Obsidian 知识伴侣

这些项目还在早期阶段，但方向已经很清晰：AI 不只是帮你搜索和回答，而是成为你知识库的「图书管理员」——摄取、整理、连接、检查、遗忘，全部自动化。

---

## 第六章：高手的进阶技巧

### 6.1 用 Dataview 构建个人仪表盘

在 Vault 根目录创建一个 `Dashboard.md` ，汇总你最关心的信息：

```
# 我的知识仪表盘

## 本周新增笔记
\`\`\`dataview
TABLE file.cday AS "创建日期", file.tags AS "标签"
WHERE file.cday >= date(today) - dur(7 days)
SORT file.cday DESC
LIMIT 20
\`\`\`

## 进行中的项目
\`\`\`dataview
TABLE status AS "状态", due AS "截止日期"
FROM "01-Projects"
WHERE status = "进行中"
SORT due ASC
\`\`\`

## 最近修改的笔记
\`\`\`dataview
TABLE file.mday AS "修改日期"
WHERE file.mday >= date(today) - dur(3 days)
SORT file.mday DESC
LIMIT 10
\`\`\`

## 待处理收件箱
\`\`\`dataview
LIST
FROM "00-Inbox"
SORT file.cday DESC
\`\`\`
```

把这个仪表盘设置为 Obsidian 的首页（可以在设置中配置启动时打开指定文件），每次打开 Obsidian 就能看到知识库的全貌——新增了什么、项目进展如何、收件箱还有多少待处理。

### 6.2 用 Excalidraw 构建视觉知识地图

对于你最重要的知识领域，创建一张 Excalidraw 视觉地图：

1. 在中心放置领域主题（如「AI/机器学习」）
2. 用分支延伸出子主题（基础理论、核心算法、工程实践、论文精读）
3. 每个子主题的节点链接到对应的 Obsidian 笔记或 MOC
4. 用颜色区分不同的知识状态（绿色=已深入理解，黄色=正在学习，红色=尚未入门）
5. 定期更新，让它成为你知识领域的「GPS 导航图」

这张视觉地图不仅帮助你导航知识，更重要的是帮助你发现 **知识盲区** ——哪些区域是空白的？哪些区域过于拥挤需要拆分？

### 6.3 用 Periodic Notes 建立复盘体系

**每日复盘（2 分钟）：**

- 今天学到了什么？
- 有什么想法需要后续跟进？

**每周复盘（15 分钟）：**

- 这周创建了多少新笔记？哪些主题？
- 最有价值的发现是什么？
- 有没有应该连接但还没连接的笔记？
- 收件箱清空了吗？

**每月复盘（30 分钟）：**

- 这个月知识库哪个领域增长最多？
- 有没有被忽视的重要领域？
- 需要创建新的 MOC 吗？
- 项目进展如何？有需要归档的吗？

**每年复盘（2 小时）：**

- 今年的知识图谱和去年相比有什么变化？
- 哪些领域从零到一了？
- 哪些领域停滞了？为什么？
- 明年要重点深耕哪些方向？

复盘不只是记录，更是 **元认知** ——思考你是如何思考的，管理你的知识管理系统。

### 6.4 多设备同步方案

**方案一：Obsidian Sync（付费，最简单）**

- 官方同步服务，端到端加密
- 全平台无缝支持，包括移动端
- 价格：$4/月（年付）

**方案二：Git + 移动端工具（免费）**

- 桌面端用 Git 插件自动同步
- iOS 使用 Working Copy（或 iSH）手动拉取/推送
- Android 使用 Termux + Git
- 缺点：移动端操作稍显繁琐

**方案三：Syncthing（免费，开源）**

- 去中心化的点对点文件同步
- 设备之间直接同步，不经过任何云服务
- 适合对隐私极度敏感的用户
- 缺点：移动端设置较复杂

**方案四：iCloud / OneDrive（免费，简单但有风险）**

- 把 Vault 文件夹放在云存储的同步目录中
- 简单直接，但没有版本历史
- 可能产生同步冲突，尤其是多设备频繁编辑时
- 不推荐 Dropbox（已知有同步问题）

**推荐组合：** Git（版本历史 + 备份）+ Syncthing 或 Obsidian Sync（多设备同步）。Git 负责「安全」，同步方案负责「便利」。

---

## 第七章：常见问题与避坑指南

### Q1：插件装太多会不会影响性能？

会。Obsidian 的启动速度和运行流畅度确实会受插件数量和质量的影响。建议：

- 安装 **Lazy Plugin Loader** 插件，让不常用的插件延迟加载
- 定期审视插件列表，禁用或删除不再使用的插件
- 20 个左右的活跃插件是一个平衡点——足够强大，又不至于影响性能
- 如果某个插件明显拖慢速度，先检查是否有更轻量的替代品

### Q2：笔记库增长到几千条后，会不会乱成一团？

不会，如果你遵循以下原则：

- 坚持原子化笔记（一条笔记一个想法）
- 坚持添加链接（每条笔记至少链接一条其他笔记）
- 用 MOC 提供导航（20-30 条笔记时创建 MOC）
- 定期复盘和清理（每周 15 分钟）
- 使用 Omnisearch 和 Smart Connections 辅助检索

几千条笔记的知识库，配合 Dataview 查询和 MOC 导航，反而会越来越好用——因为你的知识网络密度越高，搜索和关联的效果就越好。LLM Wiki v2 的作者指出，在 agentmemory 项目中，混合搜索（BM25 + 向量 + 图遍历）在大规模知识库上的表现远优于小规模。

### Q3：Obsidian 能替代 Notion 吗？

取决于你的需求。

**Obsidian 更擅长的场景：**

- 个人深度知识管理和长期知识积累
- 数据安全和可移植性（纯文本，本地存储）
- 极度重视隐私的场景（本地 AI，零数据外传）
- 喜欢折腾和深度定制的用户
- 写作和思考密集型工作

**Notion 更擅长的场景：**

- 多人实时协作
- 开箱即用的项目管理
- 对技术完全零基础的用户
- 轻量级团队文档

很多人的做法是： **工作协作用 Notion，个人知识库用 Obsidian** 。两者不是替代关系，而是互补关系。

### Q4：要不要用 AI 来整理笔记？

建议渐进式引入：

1. **先不用 AI** ——手动建立知识管理的习惯和流程。理解 PARA、Zettelkasten、MOC 的逻辑。
2. **引入 Smart Connections** ——等你有了 200+ 笔记后，让 AI 帮你发现隐藏关联。这是 AI 价值最高且风险最低的切入点。
3. **引入 Copilot/Text Generator** ——等你有大量原始资料需要处理时，让 AI 辅助提炼。
4. **永远不要让 AI 完全取代你的思考** ——AI 是助手，不是替代品。

正如 Karpathy 的 LLM Wiki 设计原则所强调的： **人类负责策展和方向，AI 负责簿记和执行。** 你决定什么值得知道、什么值得深入、什么值得产出。AI 帮你处理摄取、整理、检索、格式化这些机械性工作。

### Q5：从零开始太难了，有没有最小可行的方案？

有。最小可行知识库只需要：

1. 安装 Obsidian
2. 创建一个 `Inbox` 文件夹和一个 `Notes` 文件夹
3. 每天写一条笔记（甚至不用模板，直接写）
4. 每条笔记尽量添加一个 `[[链接]]`
5. 装一个 Calendar 插件方便导航

就这么多。5 分钟内就能启动。

其他的一切——PARA、Zettelkasten、MOC、20 个插件、AI 集成——都可以在你有需要的时候再加入。一个最小但持续使用的知识库，比一个完美但三天后就放弃的系统强一万倍。

### Q6：Obsidian 学习曲线陡峭吗？

比 Notion 陡峭，比 Vim 平缓。

Obsidian 的基础用法（写笔记、加链接、用模板）几乎零门槛。但要发挥它的全部威力（Dataview 查询、Templater 脚本、AI 集成），确实需要一些学习投入。

好消息是： **你不需要一次学完所有东西。** 每周掌握一个新插件或新技巧，一两个月后你就是 Obsidian 高级用户了。社区非常活跃，Reddit 的 r/ObsidianMD 有 24 万+周活跃用户，几乎任何问题都能在那里找到答案。

---

## 结语：你的知识，值得一个好的容器

在这个信息爆炸的时代，我们不缺信息，缺的是 **将信息转化为知识、将知识转化为洞察** 的能力。

Obsidian 给你提供了一个独一无二的组合：

- **本地存储** 保证数据主权——你的知识永远属于你
- **Markdown 纯文本** 保证长期可用——二十年后依然能打开
- **双向链接** 模拟大脑思考——知识在连接中产生价值
- **2700+ 插件** 满足各种需求——从任务管理到 AI 集成
- **本地 AI 集成** 让知识库具备智能——完全私有，零数据外传

三个工程师，零融资，没有会议，七个人加一只猫，3.5 亿美元估值。Obsidian 的故事本身就证明了一件事——在 AI 时代，最有价值的不是最大的系统，而是最锋利的工具。

Karpathy 说得好：「Memex 终于可以构建了。不是因为我们有更好的文档或更好的搜索，而是因为我们有真正做事的图书管理员。」

开始构建你的第二大脑吧。从今天的第一条笔记开始。不需要完美的系统，不需要 20 个插件全部装好，不需要读完所有方法论。只需要打开 Obsidian，新建一条笔记，写下你此刻的想法，加上一个 `[[链接]]` 。

十年后，你会感谢现在的自己。

---

## 附录：本文提到的 20 个插件速查表

| 序号 | 插件名 | 功能定位 | 一句话介绍 |
| --- | --- | --- | --- |
| 1 | Dataview | 数据查询 | 用查询语言把笔记变成动态数据库 |
| 2 | Omnisearch | 全文搜索 | 智能权重排名的全库搜索，支持 OCR 和 PDF |
| 3 | Templater | 模板引擎 | 支持动态变量和 JavaScript 的超级模板系统 |
| 4 | QuickAdd | 工作流自动化 | 快速捕获、模板创建、多步宏操作的胶水插件 |
| 5 | Linter | 格式规范 | 自动统一 Markdown 格式和 YAML 规范 |
| 6 | Tasks | 任务管理 | 基于 Markdown 的跨笔记全局任务系统 |
| 7 | Kanban | 项目看板 | Markdown 存储的可视化看板 |
| 8 | Calendar + Periodic Notes | 时间导航 | 月视图日历 + 周/月/年笔记体系 |
| 9 | Excalidraw | 可视化思考 | 深度集成的手绘白板，支持笔记链接和嵌入 |
| 10 | Various Complements | 自动补全 | IDE 级的文字和链接自动补全 |
| 11 | Commander | UI 定制 | 把任何命令添加到界面任何位置 |
| 12 | Note Toolbar | 笔记工具栏 | 根据笔记类型显示不同的上下文工具栏 |
| 13 | Smart Connections | AI 语义关联 | 本地语义向量搜索，发现隐藏的笔记关联 |
| 14 | Copilot | AI 对话 | 基于笔记库的本地 RAG 对话助手 |
| 15 | Text Generator | AI 写作 | 连接多种 AI 模型的笔记内写作辅助 |
| 16 | Git | 版本备份 | 自动 Git 提交/推送，完整版本历史 |
| 17 | BRAT | 插件管理 | 安装和管理 GitHub 上的 Beta 版插件 |
| 18 | Style Settings | 主题定制 | 图形化调整主题和插件的视觉样式 |
| 19 | Supercharged Links | 链接增强 | 基于元数据为链接添加颜色和图标 |
| 20 | Meta Bind | 交互组件 | 在笔记内创建滑块、开关等交互元素 |

---

*本文涵盖了知识管理方法论（PARA、Zettelkasten、MOC）、20 个经社区验证的实战插件详解、AI 集成方案（Smart Connections、Copilot、Ollama 本地部署）、Karpathy LLM Wiki 与 v2 扩展的深度解读，以及从零搭建知识库的完整实操指南。愿你的第二大脑，从今天开始生长。*

*PS ： 想一起搭建个人知识库的私信我，做个oh-my-obsidian*

继续滑动看下一个

CIT云原生

向上滑动看下一个

![kimi](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAEv8SURBVHgB3X0JmBzVde6p6p5Fo22079JolwAtSCxaQAiDQBgjwEu+L9iOlxgc57NjbOA9YkcSYF4+x1sgeU6c5BmMk7B4FRiDhG0Qq4RAQvsuNNp3abTMSDPTXfXOf869Vbeqe6RZJCFy9Y26u7q6lnvOPec//zn3lkf/A9vdd99dVVpaOj4Igirf9wfl8/lKz/Oq8IfvwzCsKvY7/r6aX2r4+xp+j79qPsY23rYcn7///e8vp/9hzaMPeYOwS0pKprOAxrHgphvhVtK5aTX8t5yVCorwKl6/+93vVtOHuH3oFOCBBx6oPHHixHju/FtZ2Lc1NZrPV2PFgzIs5+t44gc/+MFC+pC1D40C3HvvvRjdn+MOv43O3Qhva4PbmMd/z37ve9+bRx+CdkErwH333TeehX4rv72bWiD0+vp62r9/Px09eowOHNjPnxvo2LGj/Plo9D22xQ3dEFKnTp2orKyMysvL5LVnzx78Ws6vPalHjx6yrbnN4ImFmUzmwQvZTVyQCoDRzi9z+W96c/bfsWMHC/oA7di+g/bzK4QNgVrBxrdpX93vfP4LzPYM/+Up2S3x7zt16szK0J0GDBggStG/f39qZlvIfw9eiC7iglKA5goeI3jNmrW0efNmHun75LM237xCoJ75g0AzZhu+D5193M92f/e3rqKQ814/l7UrpwGsBMOGDePXAWJBTteMVXiQo4mf0QXSLggFaI7gVehrWOhbeMQjMnMv3R3ZaHZUp2/PFaa7vx35xX6btiBBdBxPNpdQ6Of45yFbhoF08cUXiYU4nTJcSIrwgSrA/fffX5XL5R6n0wh+546dtHrNahF8ff0pKm6e7TZryt193JGedgn2GPZ77GuthVfkN/rqJX7O+3v51HlDVoRL+G80u4kB1FQDYGSM8I0PEiN8IApgQrmv421T++zcuZPeemsRj/adVDiaIQjXX6dNdFrgaVPumv5iv7XHda1BrDie15R7oOgYYRiIogA8TpgwUSzD6bqkQ4cOj3K/1NB5buddAWDuuQMfbyp+h+BffHG+AXJucwWSHqnpljbzvhFawIJxj+ccXT66gJCMEH1KYouwyLnTyuA2VTa4hMmTJ7EiXEzFGtwC98kXzjdQPG8KYEY9/Pzdxb7XEf+WIPpkS3dsutPTYI6a2Pd02/SzCtsVMDn7+kU+s++nLMX4gZz9POcY9phQhI40c+bMJiMIJrgeYQ7hG3Se2nlRAPh65uNfKTbqjx07RvPnLygieLQ0AENH+6n37n6uQqRHqD2GvleLoJ/D0FoJa1nCM1wL9rOCL4Yr0tfkXqueAy4BFqEYWIQ1YGxw7fnABhk6x+2ee+75HHcwWLHe6e+WLVtGzz//Ah0+fMhsSSP7dIhWbHt6nzQGoCLHNls8++qb0e8qgPmTw/hUHEvY42aoqVCxqTF24MA+Wrt2HeVyAUcNBdagkpNQn58yZUo9W8XFdA7bOVUA9vf/yNr8XX5b7m7HqH/22WdpxYoVlM+7ppwo2YGuMNMd6lPTEUFACSGZzRj1KmzdqEIninFFEgPoj1wz7ipWxvlt2Izr9qNXj60Hzp3P5ySkhSIMGzY8zTSiz2ayEsA1vkrnqJ0TFwB/X1tbC6B3W/q7ZcuWi6+vrz9JVDTWTrN06dFmTaqnv/DM9yEj7wLzb5TBE+nzrva7pgge9zzpCMAKMH+a67atKQuUN0rnKjwrhJ+nduUd6Morr6Dx48dTuiFcbN++/RfORZRw1hXA+PvfsvATdwIiZ9GiRbR06VJKh0yFIyU94h2BQZBF/W6RUBEC98x+PJJDjFoge9daeOa3oRdvE3CXiY4ThhRZjfhc1uy7yhYrZxxOWkVSBfK8+J6BPXwf0UbsviZMHE/XTLuW0u1c4YKzqgBNgT2Y/HnznmW/d5BczS/0q8WAFEX+2WA1/qyC1K+bshZWSPY4xajfUPy7nhkKY49TjHcg53fu8QujicTxo21WASjxvSdn1n7IZkpEUTt27EQf//gnCgDiuVCCs4YBmhI+kjS//vWv6ciRw87WtMktIpiIdInNqfhw05HRr80bz0tjgLRpdsMzI2sRAExwqJYiPB3ALLbNNeXp0NEr+tuYb6DUvr5aKT78yZP1tGXLZskxpHBBJdzqtGnTnn3jjTfOijs4KwrQlPCRrAHYq61Vf5/U/mKdSpS2Al7iPzNWQ2uySQXneyasS/8+Nr9h6I7GeD8l9TzHBVjl8YtcX3zdXoIxLLKfGhdVMC8Uq5W8RnMeLz4urjE0Vq2+4SStXbORunXrSl26dHHu6ewqQZsVoCnhI3Hz/PO/lzDHmvo49iaiM4RJcSsGBIPEHujkEEpQkAs4s4eLr8l1TUSFOIWiz14UVeC7LMXA0vmtZ5TLa/paPO5+C2Q9RxHsvtyvtHHjBnEFoJSddtaUoE0KALTP4G5RMeHPnz+fYh9OTYxQd1sx5EyU9rGhp4ydZ0e9De30S+d4bnjpR9dgfmLeux1uTbQdsWRevcT+MYgzbiT0daR7rrtKvi9s1g0pHPUFh7jXi4Ploz7ZsuV96ty5qBJMv+GGG55ZuHDhKWpl86kNzYR6Ve62WPg25i5mQl1/TRSDNEpttzy8/ZwxJtUj1V2EdtppUAxKuJiM+W2xWoCsc+z0uZ3fh/GINiKTURsrC+4xH12b7CnbssZFGODnKLcXAUf9LRQKiuSXVVK29zgqqfoI+eVdeZesc76QFix4ifmCteQ2RFqQAbWhndlGNtGY5JlLqWwefP68ec+R3lya2HEFi1aMsiVqMvwTAsUTc6mjI0NxfGZ9aWi9DRXy8C4HkD4+Jc4fm2N7jQ7ljPsKbSbSp6Tvd0exbZl4G647VArZ9zNy+dlB06hi+mwW/DWJq2isfpVq599D+b2r+ag5stbplltuoaFDhyb2bUv+oFUu4L777kMq97vuNoR6QPuc35fPiZx5k7G9/c4tsvAcl+FajDB1XCv4wEHvoQZWXsofS7PCSZtmuz3vXEMm9VtXSc0+5NQBeE1ZL3Ku3QWQOvorps+hDrf9lDKVVZRu2FZ+2V1y7sbq14yu+1RdXU2DBlURE0PxHYThpMmTJ1czz7KCWtharAAAfcxTP00OvQvhP/PMM3AJ9pJSgM+29KhzY3Vnr8RvvdR3LpPmugdjJbww9VvT6Q7IinMAmdjPkx+FaElARlSIT6xVIeMmioWarsIlS9RABZeN+wK1n/lDOlODZQj3r6LGAxsk+snnA9q+fYdYATdE5HuYzqDwmZaCwhZjACB+SlXoQviowE12WlNmHc01kelUqh+FQvq7uNrGs2Y+YXKtWS/R38jXnrM9onkSPluPpYIRNO5l5b3vZZxz2++p8Lo9c3woEJVSbOq9aLtaCrcP7LVg9H+bmtsqZv0HZdp1iu7/6NEj9LvfPevUQkqrhGwAzKkFrUUKgOROGvS98sorUbm1qwASq6dMXyEL6Jh5LxamjmIXXNltRIWj21qBRuf4aUImsJCdYotjASILxMsZP+ubV/c6g4ipc6/bCw2uYIWyPlp/l9f3xjKElC4XIyobdTv5Rcx+U80rr6RM7/HRvcJa7dt3gJYsSSYKIZu6urq51ILWbAUwhZuJYg6kc5cuXUbFR3u6pVG/3WaAVRRmESUBhEvMmD/P+W0R4cS3Zs9phBWmcYErLCLXbHsRgjfRholA7O9D81tsz2SSCu3ZiCD6je9EAj4Lcwy1tJVUTXOuXQfKe++t5L/3Evuxe77byKpZrVkKALOCMi53G/w+snrxRbnhlN3mtrDoe9f/hkb4oec5KuI7oz8wymKTPOnjF/PBbjQQpM7vGcOQp6RS2lFP0egPo232mF70HmlddVGeuQ/9Xn+jQDV0ytgyLRj9tvnlXcimrQMDCHP5RkmwHT9+PLEvZNVcV9AsBUABZ9r0w++fOgX+IS346CLMO9dnF+xFUbqWVNjSYaGGc0r04BunSAPWPAidUM9xI4lzWbPvhH8RhoivS8/hcgIUnb/gUj0X2OXNrnEoKFRu5PdtsspckxcaNNE66iU4VUNJQKvXiKhLeZe4QVYss7ubc9wzXg1QP6XifYz8pN+3rz4VIl93n2TT0ZJxCDwLnHzHC4SUcAPSkWnUHaauIVCELwxdmuK1+xdaKM/SupGFiYGb9HfgKrurdNZVqDuJ8g7RGPCNvFxL07IGXsAOqg4dOpiwUD/v2LFb3HGqzTWyO207owIwsvxH9zNMf3yyYqPPmMxI+4spgY7s0I4Km9zhH3nR79KXaM+RDv2cEU/kULzu9cXfJ0Gnc92eF5n9pD83lsFLWzWfki7F7QerrPZe43qA1jTwAFAAHLu0tCQKt6FojY2Nsn3lyuUiG7eZORenbae9KiZ8Pp+u6sHoV9Mvl0BJIRQbWUSFyJ1E4J4x4xFxI18HZnvaXLo+Pn2e2B9H/ICTOk5aJ3PbYXzdXjTHIGb34rSzWqRknsG97ozZr1G/9cDMaUgZd0umyD00rwU11XRi3l+S4hWl11FZDODZvqIDn0uJr1OnGpkunp/++fQzAcIzXc1c9wMqd1evXu1sUY33klNl9JsCJG/MZwT2LLzyotGvr74z/gNK0rfGjxdMzLACtmaYBNhJeOYFUQIobm6VrmeuIZM4pprrwJzVtR6xa/N8XxI51qLJvjh9mFO+wUsNEM+eu3kNwj/29Ccoz68KTAMZfPD7IITq6k6KQvTt20cUAfLBrOhUm3u6czSpAGb0V7nbbJInvpv4z3PDuGIjNLKeoZ7UB5WaMXhLO/3WWbcKota/vPMXxNtyjbRl8xaKgaEFZKooFr+FECh499CGZDEdrb7e3kNIVBCre2Yf/c2cOXO40xv5r4H/8uZ9jhrqG6mh8aS8zzXG2xsb9e/ggUNUWdmZIsXBCGbSKLd3uQg3qNlmXqsTn2HykQeo+cllvO/K6Prwa7B/9XxesT4G33DoB6Aue7z55puUaqe1AllquiU0B1k+ZfuaarEPFHDnWgZbbSNpW+NPcVOhU1LF+1ZWNo/EqqoaFKFqxRppPbZ+PTCX5HACUnWTrudPW5Qwsh5zZs8VBWhNq6k5Kn9QJj1eTu755OJ/4r9/TpzPdS3aH6EBj1mDPzTK0HUNQspmS0TZsG3Pnn1UUpJlt1BCW7dWyySb1MQTyHJhsWssagHMahxV7rZkzE8UmfQU+Ivz2a7Z8026NmfOqKZezLMcysAvrwUIOcIJLhDLU9JMWz+cZuSckE/2VeHYGgDbLXNmP8jCn0utadXV2+j6669j08yK6gc6GFj4EdD0jNUSV+H0o2cSTZacMtR1GOh1x65Vf5MtUSWCdYR7gHKnw0I6jRVoygUUGf120QU39i7W3NFkGipxxZ3bEMkthzJpXrXb1PyWd3IGtrluIb6OxGFDV0F8owdZGWmhsyNG/Zw5s6k1DfMdIHwoQRBoCZvMMzTuSvIOoa1nyKSuN2uUNZVN5K8zGS0bQ4gLV2QHUiaToT59+lKnjp1kG4ihgwcPpi+rqCYXKICJHae727SUO91iJdBaNgfskPpcHXw2nLIoiWJhO3G11wqEnACHUc7fXlusqDE2IXJTz0kSygLIrBF+68w+hH/ddddzxq5agBny/hHX5HmyTZTAtx3hUtQZAa/k4igv/p2d1IJRn83q5JKQBxVSwwMHVtGgqoGoDWClC+n1119PX9p0LLmT3ljQ42xKCpB/IbJ0zb+2JOpXAeiWlJsINbASmjS0hZCeYxma21wQKldOsXBTkYMtKae45Ct2BR5pQkdH3ew532rDyF/Owr+O/f4RstYILsDPaBgJ8wyLoCbeRBteDGAjFxb6Tn+R9BmAnh31Qd4qNoPjoJEBYC2tW7eaNmzYINeBEHHXrl2CBdxWbKJOsSE33f0A819o7ot9Tm2zo1xeTajlmt3Q/W3QxHFP1xyKN/ptmPrevsaJHSiAxulocTIISjF3ztw2j3yAPnsfLDOZ+pbPqV/3LP6RUjDzXnQxGVHF9+P0mbm3UJQhL1ERjt+xY3txATU1WgZQUlIigxEg8eTJk+nL/Hp6Q0IB7rnnnsS6e2CWVq9eS0nBOIjaXKgt0oiKJx1zVShUV0jpoo6WNJdqdo8bGodjXUqQCE8D43Y0g2fSweyfZ8+ew6P/76g1DcK/4YYbJC6XEW9mL/m+vSIe+VEpe04UTkCdtfDklKFZckkAcobcaiMFlGY/UgII52xsbJDfACMg/JRzhnpdDQ3uamhUmQaDCQXA4ovu53jKtjvKqIltcThHTp2eOw07OfSt0rTE7KdbMUBqzu+75wnN5A+9zsCcMpvV382d20aff/1H6MiRIyKw0tJSEZKfwbGVg8j4WnmklkZrCDxfLaGtbgawg//2hcTU2sEod2CUIgwtJIiVQkFhDBixT6fOneT9tm3bjQWPG9ZadD/7qS8TPkJHfxLcxf7fbYYxi8AdieaGACkeUbJmrvAYcfVwSy1Bmhp2lC2aCKr+H2AJnat/GhmAYIK/b22ot2LFSpox4zo6fqxOLEt9Y61QsnivMXpe7kuF5Jl+8ORa8B0EHkcyecVDgU11Oe4Jd8qhpFgvSTYZF8P7V1RUcHKovVixkycb5PUouyFUC2GNw23btiWuGQttuqniSAGMaYi+gPnX1bjSPtZVhjjUikMuLwZ1YvYC5yehvQjHLKdj+ZY2F+zZqCQwfzp6Muzz/Uwo4VcmkzX+My9mv/UjfyWHejzyubNB/fp8bC0nC6JRKaF/GBhSzBeBt29fTra/IsUgwxGAvpZwUc27hI1eECmJO0awH1yNMJINjXzcdlEkBhyA7zEDe8uWLQWlY1hq136IFIAvJGEakit2FPPT7oh1BQfNzam/g58L0wCn2Ci3WKAlClAIHm2dfQz8MmTTs75XElG1qB+cM3d2G+N8NfuW0BKSizTs86W+0JrsrPQBRi/+nTrFypIJ2P1kjGBNGVmUMbRhoU/KnGZFSYIgMMfMRyEt3E19wylRZhwfSSI0TRercnXv3p3Wr1+f7DldbldapADp6dyo8Y9beuTrtsIkS1op0n9BMs/vWdDjxsLNbW48b4FoxrEuOFcuCvHQSRj96Jg5c/5WKN7WNBX+DCZbTpjYPEM2txDXAeC8jVpWwKbb91W5NQzUOQ0QmCaSsmSQnfIGrByenyNLWaslk4OSDROxrV27dtS5cxcxsI2s2A0Nmn/AvWMiLn6DvEH37j1p06bN6duIsJ6c2ZA/CQVIWoBipp+oUCnS2CA54r2Ez7ZabrTIa6SWYQAbyhl2zZzBCsHjEe9RuQAz62vz+Qbx9633+UD7N7LPPyEC1LAyZzKAvhE0Gp87LI3v11PgBldUWtKONFLh32bMgAjje/G9sui647IGM9dCKp/1XOXl5XwNanXUwuQN4vdMpKNrMlRXb6HDhw8n7gORHpbZ1zNya2xsLBB+nPM3dxCFHu7EDfd73/lzFcTZz3e/dyt1KRoFzW8ubsgYUxRvg18OqcGMolA6bc6cB1pt9leuXMnCn0FHjx2mTDZjogq9b88wdVoJTcbyOFXKQVYsRcDXlGMl1GRZYPx+PLIVMzSyPBs0UvA0eygWRuoKc6a7Qh7lNXTo0BFyB6dGEV6Cle3QAQtglxaQQnjGgvzGfJ7ufok5/eTE+U37btssqnfRvQsO7WkC57AmCA6tG6CWGYCENQkodJhApV7ja0Z/zJ79rTb5/BkzbuCRX0uw4EE+b/rXhmlaFo7OBymjt5c1IZ/6eM/4c3s9FJXAa+2AdIXUMBDZugg5jp8zimDcGwu5pAThZtZkNa3FI0MAZSUysFPKUT0ErLBv3770bY2PehFP23C/0dU5bUv69DhhklYQd1v6vVEKm4jxzNEkxekmcFrStI4/Or8zv19GlXPc2bP/rtVof+VK9vkzZvCIOyQgDqMM9GsY2CqfOHMnZzNWAeUOwBy6lGwoxBOUoKKiTBShoqKDKItOQ8s43ayRhL03VagwETUBx0IMl112GU2aNJmGDx8mx8c2uxS+1gcQW/KTzBZ2LLAA3K7Bf9b5JFwAVuCO/XvSryfr4jyiAo7AbnOXcvWSu5icgB5PI4aQLFPWkuaafO0wsGWK/PXcP/rRj+hv/uZr1JqGkY9FHWvY3EbVPaGCtSB0U8/mXll4+SAv1ifjg5XTfTBiEX0AE8BPw1plsxWyDTn8BoRpAIsmEwgat7ExMIkjU18RaCLZZgSHDB9KBzjjt3/fATl3t+49OP6vIRCB4Dfat+8gioD1lcEFDB8+PHFvlvH1TYYoiv+hQacv/EgcxnSCO53KCtwtuoitR5w5JEpii7CFLsDijlgh7VTr0JjXxx77f60WPnz+9ddfL4kd31MAKzx8qLX+Ga/Euc/UVPGQzPJ3ek0QNIRaUloiI74kWyo8PQo68/lGsd+lJWVUVl4iwhZl8UDytIsigNAUhOC4WHTj2JGjbN5PUN2pWkH/Q4YMpn4D+lN7DgG7d+8q9QFdu3aVy8HxUMqX5gMABH0+aKIMZ//+A1SI7pviAOx2NymT5ujT+zaBJ8K0NTlTS/MGVrn0Gh577DH6i7/4HLWm/fzn/0mXX3655NUxmshl83CeIBRAR/Z+ohVG43uTuD+0/IQi81y+Xr6HlQBLB18NE19WViIRAgQJi6BTx0OpkNL43xcl1ChDOQR8d+jgIUmpY5eDjNvqauuoXVk7CRGxmAR4Dxxn4MCB8qrYLm54shqOmDD/eMRK3NKjLFVcUTQ0lNunpEVoqsW/b7H1Pw17+Nhjj7dJ+F/60hfIpmQFvQcmlg+9mNK1ZWaeSzv7JuTzxP/b2cbYpllBkhGP7+rra8U829DxFLN2ZWUaIvbu3VfM/66de8yx5KCyL0AemMzdu3dTt27dIuRfU3OMcpwUgsJCqfA9MoR4b+ngdNm4PFYvXfqVDP/I6WSvCeLHfp/e7o7oJJCMV+y04SD6NKSWWQA9nmdDU5Ml05H/F9Sa9vOf/xcL/y7SNXssrgjEp5cAdZsJJ4JZPAWhdpUxLfnSmkc11Xa6GKhoktculd1NgQjyBb4oVmNjveAC9AcsAGhcXVHNhpo64gEcUQ+A42LNoN69e0eoH399+vSWVDSmjUPBcEy7VgPcAY5/6lTCBeD3VT4erOhuTJqJpA8vvi1t2p2Qj+KETHJf97eOS2ixGdDEiYa9GRH+5z7XWuE/wcL/osThQd5X9jDUxA4SNPmcgjLL5EVzFsUCGFrX1wUmUaAJ4fkmFEURSDbr0/ETR4zQDbUrrsWPmEtlCkND8Jil6vnYqALGtShPoAwfij+mTr2KzXiZrDW8Zu1aEfThwwcF+UMpevToSWWl8RoCBw8mXQBfQ+dsGgOoBbBCDqhwsYZio9qMZEcwxYs8iilR+rfNa15KVx577D/aMPJ/Tl/84hfZz5YaCllHvy5Jo+AO/jzL4E1HFZRAp5GFIkdN3wo+oLwCwFBnEIeG5/BMLgIWv6SkVFhJO5cw65cqe+dpGTx0Q+kEthJhg5BBGZR68fe5xlAqtLCG8N69u9i/DxB/bzkIxP2I+SE3LMKN46GBpML5k33oVeGqEwqgZcdp4Rbz52GR7T4ll0pNj3prEYiKW5KWgkA9lvr8tglfJ6rkKZ4/kHWuTbNryLppvsHOCiJD9sSA0JI2MPX5oIE8U+cn1LGPqV0VfJxTMoobmb/HPvmgXu4nKwCQeYYcu4NcnTB4OG9gIBXSyMQsIXIIa9asFmuAnASsNuje0JSOgfjp3LmzKIpiBi2AgeK5TVwA/1fEArgtoKQZTwu1KRfgpX5v3zv1f5FxcX/X3KYupm3Cf8KM/BJSps21SA3iq0tKfBmNoanpU4rXEj+hjvxQp4JF8xJ9FjjVky4/oyMQghWbwCCwoqK9jEYtTCmR4ylR5FFDIwu+nETJGhtVFjgk2EcoC4gzKBNC9REjRsqot+EhhK8Cz5tyME+iCq1JCCQaSDe/2Lq+hbV2xSpu0xbBFbSrFH7qs2km5RnahFBB+Hj6Nm7cRBb+T1stfCDkr33tbsqygKW23rJ5YaihmFfO77PS2QjZIEiAMVEWBoLl5e0k/y9UrQhQOTVYhCCnSR2pPTShY0bSFVmJBOrqavlzmWT+ysqyvF+JnAfEURhgH8wfUFyhYSCfw88YejmIlOX997dIOVhdHYd/5WXyXMO+ffuJEiiXgN83MC1cKYoSz+0ge69VBcOuOMp3Rr87yyZSEmveyfkcFnkf4wnxj5JRK4YVztyWLl3SauGjIY6+995vCsgSxs6MfhFyxhfQVVpq436PSZUeYkIzWY2GTnEYp6STLvIoJt5TXwvkHgQNUdUPRrkifFV0WAZYgtLScuNWciaaIUkfI0QU8imafJqRfhoxYphmNvnTJZeMoc4y7YxktIOgwszhffv2CuEDBais7CKWAegfitmVw8Z0K2J343DP8wq/S5Z3pYVuX10rYU8T+/yoeFQQNDa5+56/Nnv2bPrlL3/BoVOVlFxpnJ3RZI8XCh2LEVh36oQ8xKqhnnPuDXkmWjRdKwkoebCUJqI0LewKTgtDPUNz19fnTJLKFyIJPIDFE5pRJPHvwiGY/YAD8D0MAQpA4d8nT7qSNm3eQHv27pWRDdOO3wMAIi+ABgUAU4j9hw4dIqzjnj17CvqgiALY0eyWVQdF9iFnu7uunjvaLZkSOjcaUhIkOkmVD0AJsPDiSy8toE984lPSmQi5IH/fsHda1eNJ/F1eUSIKcvLkCcMRaF/ZhaDjtQm0z4AbQNtqYQjQf5mpFFYuQXGHXWzKmHv4eFNRBWsCDKKKFbDbOiyupw8TRTfN/GjE8IHowahH7I8/cAl2qfkhQ4ZIYSgmj5SWlBTcfxEFcDe5vrkplG4AXfTepDE9Lc2O6/6aAnqBc56WAsGz0zCr5sknn6L77//fci0ww9rimj0dYXVC2SomAMFTYpQ6K9m/0H0iSRQl6HwAySR6vilH15VCdQUTkzaWs2TMubWuEhYJeEHPr1PRoQSHONbHbK3jjNeQVezdu5d52HVPWVcYox24AFYAkQAeYjl06DC68sorC+69oMfBSxeO5LQv8FLvk0DPS2C+tOK4rsDMkjGd/UE3FIlu2rSBiZUqIVhkGlY2nkouRZj5nIwyCFCvGViGR3te+QItETMMocEEoc2GUyCVvEmrGkQjXL4PdE4BStYlcjDWBSP9BJt0rBIKMAcMg+xfbe1xKQfr0KGjXA0SQLhm7I+aAPwWbgRKYmsV3Oab59hGray8nJIj2gVxxbYl30dFmaITnqMERElMYJIlnjJeESb4gNugQYNo6bvv0p13fkk6FaweWDyttPWMkFjsOZ2ZI6PXN6uBmWZXE4vr/FmgqEbmeL9U3ADci+YYLI2MiAHb4WJg5m3srsLXruzbt7+YdtQAQAkBBFH0CcLn0KGDVHvihAhfS+BC4QaQ0IILeOONN+jSSy9N3Ctk34QLSJvsNKnjpd7bUihP2VxfmTBVbfcYLrYwCDskKuQXPtgGEuWHP/wRPfroo2xW+7IpDaPJmWRAns1jCKcRWALMzn7W/tHRb5Q9gFUoESwhJd2ZvEg1yNvJMTpwEMM3NGjlbzZTLtt1wkk5nThxTMJ0CBtz//bt2y/zAtGGDBkmox9K26dvX77uXrJ99OjR0WuRSb414AGq3S2dOrWnwhFfzA1YH2cRvZo8EW+ombMkX2B5gny0TX97JozxwbXPfvaz9IeX5tPIESPMlryMVICp0DyWXlK9lDMmX+nhyJIZC4davsA8iAoJHQHEVKKhnp832MHMIsp6JtWcoVMNtWQXqsDvQP507dpNav3h40+dqhPeH+6qG2+H9RjJ5FBHthI9e/fgBFEfqWuAUsFlIIHkNpZ9Dc68zd1Y2dk+nsSOSgfYSEsrgu8c0DPlWBYYZqKOi/f1Usd2levsgcB/+qdH6aGHHqK2tkFVg2jlqhV0333/S0YVzHZ9vS3iVPOslTz4BxpdkbbkDyg0mKAkUnYdLNjHYiALJDW7KHSwjZikXF6PB1cCkmf58hWC+OEKYA3g50EG7di5TcLANWtWUS2Hl2VsMbBfX7YGo0aNojFjxhSkg7kdhQVIrC4NwBCbapf+JXNjaetgRrCzZk3sMmLTps0u2BR/TnIGZ8cCPPTQg/SNb3yDX78j07WxxHpb27e//W36zW9+wxFDf04Nq3u0fYF5gCJUM/nTLluj96qTPjyj7EInR27PiX5kKZicmTCigwTYQy1EGKV8gQsQnuKx9EhOnThxkrOCV4tFAE+wa/du6typI/XkBBEKThAJfPrTn+btuxhE1ibuSZ5CNnXq1FH8fqbdCPJg8+ZNRAV0rsbD5JSFKwBSNswrsBb2d84TMqLiRxsvJ5nE8ePH0q233kptaRj1ELyNr7dt20rPPfe8gLtRo0ZSWxpG06xZt5pZ06tM2tY3o9c2T2cGyQJYzM1ntMgjNHG90sehvvetEikewD/gDZuIgmuwE0hKeWAePHhIyKNypn2R8Rs0aKBUB6MrEeL16tVbWM0D+/dJadiVV0ySKmIUjmzavJkG9O8v1UJOe6YIBgC9mCZ2DLr30mAtiJC8bAsLQV5cMxfG+yX4Bd3XOwsPMFPhP6TXIELJyTVXV29loufjohhtbVCkf/3Xn9APfvADVWLJF2RMFGBCP1kzsFFuD8hfCZ5A2Ea7MAaaLB4VmqpgabhupIxzUkgqcw59nW6PwpGBA/vJsRCRoPADIBDhKKp+16/fQBs3rmPrpOVieNrYy6+8LM8WeP75551wNtGW+3yw5e4WkAna0rG7IBaKkR5FFy6PZA0tyEtHChlKPv1Djx0vw2ZzAzlqS7MjP3IlIXxvqXMbHj30nQflWXxnwyX81V/9Fa1bt4ExwgC1jKE7OLIGCGuOACM2oLyUfIVmriLIJOT6YxcZXzdKzoNoShgqeupFgHV1WqsB04+JIRD0nXd+mRH+KLrxxhsliVV7oo727T8gNPH4S8fLubdv305vchjoPmVEesTzanzzFMoIB4BRspMM41p0y2QElKzaMcvAJJZCdesBrQWITqmdRVbgLotYLNJoXoPgY+HHFiY0o9CGUrj26u1bZAEn1AG0tcEarF+/lr76ta9SdO2mriCMsnahgEa4hYaGk5KwQX9poYYLim2/BMoqSh0iGbYxa0Z6Z3EdWBUEtZt4cMQqBqgvv/wKLVv2Hu1loZeVlzIALKX27bTgFOBv4mWXSQSQeghlzfe///3lVmrV7jc9e9rHk9lwzca35i9wrINdDyDhz9ECZ5d4/9D+b7FAG5E/AB/+dIauC6yMIphVFaJl4jjdWl29nb74xb+kb36zVc9ZKmjf+9736N/+7d/EJ2vhqCCBaASHJksUmFpBVJXZKew6ayiIqpnRNRUsPJh6GT6BgkD49rVrVwuww6xkfa0R2rehoV4UATyA1h5W0s4du2jNqtVCDp04dpyP2S592WL5fXOBr7rfDBgwwFw4RTSlNhe4GT+WWGrdCtMFgW5z3EQ0Jy7joOSWRQHfeehh4/MN/ojQNVFiybgCskmB6j//8/9llzBElnNra/vsZz/DLmEdK8K/06CBgygePHqfYFhRa4g0MEaz1haqkgpEMBlRuAikmmUqeFQfqIU6w4YNFdmAE8BoBmGFeZwTJkwU1929ew/q3q07s38oFhkq37/++mtUztlL5ALcxtclD5gSCTEaTeGAHiaDhRmsdrEDsyhy6IJAj5KPhnFjfzvFyUvsHy8Gaatq8hQ/+r35LgCj/kGM/ITiZM0hLDNnldCGqV5CMLgnWAMgaCjD2Wif+cyneaSuo6effpruuOMOpmvHiik/yaSNVudYYfuSW4CQ4RayGY1aEPZBwBo14Ii6L64Xq4Ai2YO43mb/QPX+6U9/ktnC+HzTTTdzhvM2cReIFL7ylb/m7GHv9EMncbyFtqfgKxa6XyLGLCvX8EUWeXB8dfxEzDQ55II/e+FeYl91x6njWSsR1do3r2Hke/b4JixVEGX3CBPniS2EvQ8iO32s5uhhuueb99GXv/zlaLWttraPfexj4hYWLXqLefi3JC/foUM7mSGk5lgjAoRpDVIbqNeF4hMtLjFT3k2GUZQkmxXLsXz5e8IXoMEd3H///RKiwr1gfcBf//qXsh0kEfIBWD8Y1sBtdtBLjwMIppNCPbv3oHgGqwrYAsJ45m0auFmq1/IBtrPtkuoOMWRGavQYFnlp/kra+luKfhvPlLWj37aYhtZ1iu00bI23hc0LAqkA+tnPfkYTJ048K1GC27BgdK4xR7V1x6QCKC+jXh/60K4dFKPCuFq7IIRGD5h/mA/yZhnYWklH28JPcBFIBKGId+2a9fT222+Lkvm+Jq5ee+01uTcs9NGvX7/E9fD25fYR9NGQ44M+6+4Ef6P9pSyVnasuPwlsjaAL/JKMX8wm2tW6ddkUffVS/tqCwtOtXV2suSRK1kQjlpnMpM6NE5RoeGhm2SDm1vQ3FlzQEGnXrt107bXT6eGH/w+drQZzjuqihvq8ScnCzNeKMGtrT4kQIVSdT6iLSMENBIHiGISF+bwvmclu7OPtMcHawl0vX7GMR3tXUwdwShaKRsEorMC+vfupqqoqfUmRy48UgDtlnrvHRRddrL7fDyiieD2dsBCHcKQXGLqULhnM4FNUBSRjz/zWs49lS7sKtJZwAdaaZAWpynETRFR8ntCswaMEjY4umcXLyqA1eQjZdHvHjp2EbXv44Yfok5/4s7NiDTTN61F5mZp+CLq8vIOQNWAFwev37Nlbzl9alhWgiFGPOtNOlR00c4g6Y/b7Y8eOEbKuffsKUdZjjPBRb4iFIK648jIJDTdu3MSAdC1dccWVsiCFnSRqGyveE9G12TfMGUMrEnwAsIAuSxKYjksLjih2DTHgksSIsyR76D5nN2IOXYthtoctYQM9IjcqCe0oNxGFgyd0OpdZRSSawZtldFymUSzvi5HYv38/mRl09Ohx8bG/f+E5mjHjesmlt7VpClhJHEzdxnVjAW7wA1jmDWVm8NMnjtdR126dxW2g5uCKKybT8JEjhN+H1Vq4cKHwNPZxMVCirVvfZ5awL23csFmAYGVlJ2EHMc0fAxHvnVbDLOZC+yHqpUceeQTCT7mBIToxMRHyxSGeZx/yxB2MxEVkAUL3UW/p8JAcQTtAMZFMalaXRtSJtrxRiYzU5YfmvBGR5ZkkTFTLl5cRJQszyXdYduWYKAniatTug6vBbOmPfOQjxKQJtbahyLNDR338O4AZQjYIEImarl27yErf8N/9+vUhnR4eyvaLL76YXlv4Kq1bu0GprIwWmmJwgmTCb6BEiC7+9Kc/0s6d23n0bxRA2I//du/ZzQp0ReJa0pY+Dbt/5n646KKL5OKVR06Gg+bWSF1AGDFbkt93ljyL/S+R51DBBeAxbBkPIORUlJsgZeDkCaCBKb7QqV3inkK7iocX3bYqrERA7FvL5ffwsVgACvdjl8dH/h37f+tb32Jkf0srXULI4eAlNJB9cd3JU3T40EFZyg0jH1YVsXxV1WBZmUWmjbECHDp0SD7D6HZmF4Hv+/TuQ8OHD5XKIGT+0LBfz57dZYHKw4drWMG6SSHqYfb/H//4J6KlYuJ+8xKDPKEAxjQk3ABKiuGTbOWO78cLRemadfFqViiYjFO91vxbXxzGiN/BC9GFtTAZpMSkVSxf191PPIEEdGyjKkYKW8A6AfRZM4oRg6OcOHFcOHrcI0qyUJixa9cOEiKHt7+04CVZHxAxfksahLxl81bavXsHHTt+VJZyRU4C+AMjGQqA1xkzbmQr0V2uHcANkz5xP6hDuOii0dSuolwQPZJCUAjU+4OOxvFAAuFe6pluRkYXCowKIFiJ+L69amYtT2sB0B51P6CiVBcr1NBJV99U060LIqoIRCjgsX0tdrCC9hLIPs4RxJZBTXVLk0Huo1hDz6zG6VoVoH0UU4S6t0YGcdYSa+jgVmDqt23byQCtnP2pFleEpmQbqVuMSCg1YuzKLkyx7twj5Mqdd95VbN2dog19tn//btq1YzcNHzpczg3hoEwceXxwBvDvq1atlFBv/PiJUtwBxcCydL169+AwbzFdffU0YRHXrFnL5n2XsIt79+2lSydMEH4AlnrUyFEyX3Do8GGsLH3Tl7IwvaFAAdI+AhqHp1JJl/PIKC+voNKS0mRuwPzpREazdp3dlhj1MfcfWqbOSRF7LVgqznIAvmNxEg7EKIVl/6JHv3nxY2EBymDlZBmXfKOUXEkxZtYC2fgP/vqkmN1ARt6TT/2cGbnR9NWvfvWMigDhwpVccsko8f+IMlDTj0rd2tqTtHjxYnr//a0yvx+AbfPmDTzaKwTQbdq0ier5fAjLUSJ+6NBhGeGNbD0+wtaoavBgYQKHcHoY8oFLmDZtGl17zXTq2iWJ/tndPVhwbekNyBBRSlMmT5kkNw5/BICETvLMA58jU2/SxGGCCCKKwZoXh/8UxpFAGO8bhs3HALGC5ePIwnNAZcT6BUm4Ef1WJ1xi9S+Z9MGKcMnFY7XiJm+vJy9l4JoM0xU5JUnD29uVtRfc89RTT0vB5de//vXUI/WSrQQFHYeOUP+BA+jmW26h1WtWC0q/8sorpMATi0Jgbj+sA8Bip04dpHgD+Xy8Aow+99zvOFLoJH4e2OXlP/6Rtm/bzpbOYyvRk5WmvSjN3r17BGOk2kJL/ritKeYFmjLdfgCx0KlTF0kyyGLGnlsASVLUoBktuyy6WxqGEQffnEuaY7v6BpIeEsNb19Hcpokka0ks4rBNjxtEuCDKBoapqiUP9Uw+g7MTLJQVYkol9PUaOK1aIbN48/kcxeXZvuyDUixM7sRoREz+05/+O82b9xt2Iz0E8IFRvPrqq2VmDubu9e7Vi/pxmImsHR74CJ9dx2Z+7do14u9R4AE2D1hj8OAqWrLkHVEspHOxsANIHfj7kSNH0m9/+1t2E+OZEl5OR5jqhdUABXz7bbezIpeyq+oqxy4i04LmURPt3nvvfYUcJYCZ+8UvfikCB7AA3Qh/FS2l4iWzfDp3LjbvMUMXOIjcZAOt4HgzHgmnKN5dYs5zhKZgsbp6M8X669QlWiXzbO2CSUrZyMRZjAoRjmbl9J66dq2kvXv2SQIMnLwNe2PQS5rJCy3pRBI5qIuop3blHWmohM5ZWs2pWKzahX6CEEE3VzIhs3r1Cnp/y1YW8hA6xIKF34YFAAfQsWMHQfcjR49ixN9fQnCsSbj0naWySOUNN17PVuA5IXjefPMNcUvIEsKdTJ9+Lb216E2pBRjI2UiAzEjIDP7Ysg+mIq1J6D1lypRt/PJ5+xlsFQALMkwwfRgZtlPceDz5uFa7XQWUDAPtXkZwEtKV0BH2w2Cz9Jl7NZyoOSKvR2uO6eeaI+aZPI6gPSvoGBjGzQGk2N0PoqvAJM88YxZk5EqyZQK88kG81LvvU1TgqSSYLhNXIkkZ8wwgFGxmynXlbuYVQOCU8HuUbF/Ccfyhw4eoN2MohGPAR1CIpe8u4/0zsrBDjx69hAFECfe4cZfKVK7u3btxtHBMavzWrVtPM26YIZEYsAcwAYpBgF0mT54s2AEZwd2798hagHhySZHKn2+89dZbiYzvGRWAf1DNSjCd31bZbUg5YmUKrF+XkzVzMoKcYQnihZLTlb4eJUqeiCg54cRJ19r6erJuxI5+cn7vEyWWhDfH9uIFo5NVRvFvtaI23g6ELw92kGVddOEmuQbPCt6uAWyXaNdrk/n8AhazLGxVliDU2b0NjY2kK3bXCCDDusJI3/76V7+SX2NpN9TyAdjBNcCCYF1/vC5a/BZd95HrqGOHjjLIsny9ndiXz+fwc9y4sbRg/gIR8rBhI4T9Q6kXZABM8LGbZzKNXCbWKJZFNPq/QE20M8HuhN9AvAw/VFdXL34PKUpw0RoBWE/smHuyI9MTzKBVwVlKMoPWQpAJ23JR5GBDRVUKO09e6+3iUjW7YnbWIYbSiSid74iCDLcaGQKwC0zJk8zCnMl/6HVLzkBIQnsstTKItzHRo6J9GQurk3DxmFCTy+uTPU+e1PUAR40cTcOHjaQunStpxLBRgvhRxwdhDxjYn0d4T8noYR7/8BEjBBt0ZmEO498MZRcBSwHaeNbNt9LuXXvE72O0Y20EgL1ejCtGjRohFmPJO++KWylS/FnU99t2WvalmBXo16+/WAF0HjoTmqqramgVK268tLSdMoOefeZtHOcj6aKFD9a+xmDM8vgCMD0ntezZRZn1gRAortRl2MzEC0+/00JQU4Tq5cg+zCp+IENo5s3ZpJWxEF7enNdao7yzZEFefLHCAS14AeDt1rWHKD/YPERFyMbheHCNJ0/W8QhvYNCn1K6sBspJn127dkqJFkJphHOIqAQfICt44qQAwHGXjqPf/Po3QgW/9tqrwhd06dKJVq1eIxEDQscNGzaK74c7mTbtGv67ml1BNX/Xg9xACiE9j/6/pdYqABrHlK+y/7vbfobvgZZhTroudhzPi9dHnHji36DlWNEK/QnaNTSzYu36t76nT9fQpVMyZrWQ+NGqYj+iUe6TJX5wHty4hmMUpXbjNX5CsrNpIwFTvOJXXNFkk1zWOtn5DuYKZDe7b9bU8etn4EbBDqL4WQndTjLFW1FRKufEiL711ltkyhZcQT3H7Du272S/flzm9QG5Q5CY3Ll27Vq66JKLqQfTubV1J2QSKVYCWf7eMkb/hyXxc+PMG6XKdycfY8CAQbJi2KBBgwXoLV68SPrDThF3G8vpJk5k1bRJAXAAtgLohel2GwCL+q9SMUUwibIuTV7XuM3JOni5KE2cfjCkzolXAQV5ywxYoKhRAdKnAFa5fFx5BOIGVbIYZeXlpYJD7BM1bEZScxXmAQsRig/VPYQxbxHjEU/2D60bCd1wNcY1qriaE8Hzh7QuDzNz6uTeYRkhgD2cgBk2bLiYdzy+FWb6/S2bWQF2CB6ACYcFQ/iICRs33jhTOIgX2b8PHjxIFASx/7JlyyQZd/nlV1ADu5Wd7AIwHbxq8AC2DK/Lk0mR6LFFonDNqfZgmvYt1ppFvTFQeiRdMYSFlK+5ZppQp/CV8EW2IkWmMxkBYLaqnMg3qeIwjLgELGSIukNJzIRuIkmXVkWplMw5MPPkQlM2hfOh8EFHrBGRzNW2zJ1VhKyxAnbalnPbkcLodepyrOYhDebhkr55wIW1KDZkxPH79RtgFl/yhafvwiHknj17xbxDSRDWATRjIieEjlDtmquvoe5duzM2GCnr/MFVgAd46skn2QUcFwyw5O0lkvQZN2683APcAoSdZYvqs6K9+MJ8Oe5HP/pReuedJcJeghtwG2TFRNAj1IzWrAwMU5Wn+IJRRfp5uw0dght7//33xR8jfIFAO3XuwNtrxUrg+759ewvShpUwF0fWzw4aWCUzXmRxxLwXLYUOYISQTD4bVs+icI3d9fEycEHI20NZtBQ7FqjiBhMXeGHsG+2q5KFZxlXW2dcFmys5VBMAJ493SSqrKku83Brm6aFAExFBx44VUnsHUzx8+Ah69913+LutAg4xKwkovU+ffnxPx8R3I2WLWb2o5kWEMIG5fPTRkiVLxJ3gD2sS2ZU98YSynqwU+9m6YC2AsWPHy7VhsuiECeOpCIF6+9///d+vp7OlAGgAhBx3duFOmGS3gW6EYMENSElTLn5kGkIgdBoWMYYgYf4qGQ3r8+zKmDSpiBYztmjc8z2DvHNmzfsKOQbcCbh0XQP3lOwLdIwRaUGdCkcjEEvdqtD0ad3J0nYyCqSLP8CVQMnq6+tMibbiPcl8RhxjSD2664qcsHSotUNsjwoiZN6Qpt3FZhpkDrJ3qNnDBBQs2oz7QcQEzh/74v4xSJATAAbAvcBigNmDOwEf0KNHVxb02GiGb5bvE64hy8fB+WEZMJO4o1kLyDbuh0c5q/sTamZrfvaFZNHhB9KuAKtOwP+IyWtXJtU0vXv3obh4hGRUIW7WZVAD0Xa8hymzU5a78w1r55aJcGBB7OIHuEyET/K7QMuj9NFogVlo2Ys4erUSmWg+QxCoAsXsY0wUQVnhZnRpuIzhCGyOQZsNSTUBpgswtmvXXq4VnP3YsRcLYq+s7Cazb2C9JLRjZQcGwEAAQOvB26BwF42+2CTXFFBDierZKrz66qsCALENo//NNxdJaRfQPawaBhkszw3XzxDFuPyKiTSMlc5tJua/m1rQWpSEhyvgqOBZ7uzP88dyOQB3HDQUqUvw2UDDSFzgAYn65Iv6SEB2VWwIXytdT5knbIai1RgpwAwAebAOupauTrFCR8Iq+F4M+CQpRSasM6t3qGCdRRrI1ixkom0YZQIwzdq5sCK5XIMQQZ4XRLE0rrFduwpW7koJ82AppnBiDAydXZUb/P24ceNIgWuWCZqt4gaWvbdUrAQmcqxbt1EyjBB2125dRTmRFcREkvZ8v6ij2Fq9jUYyjsLyL68ufJV9/Ex59CsYUTCwI0cOl2XkYTH6c5oXlieVPKvh808+E+pvkwKg4QRTp07FM2Wihw+iM3FDqFcDsAnMdCYUPHhSaVMqqBgs1uHDRwQF6xr8mo6FG4EyQKB2SXQIRaYyG87dMnJ4Vh6mSUFxgMI7d+4oSNz34mhBjY/OqrXhY+QCMOXaLJysxar6OxRjwkrhulF0CVMOgZeXl4gLs4+ew72BuwcdjXw7ANgrr7wsAlm69F1B5cjGDRs6QjJ3GBiorJo16xYZAOANQO/ClyMMvO22WZLShRLs3LVDlAKsH9b0g3W89NLxkofBoELBCqqSQMsHQUH53N8y6p9PLWytmpMNXjmNB3DjUALMtEEVUfv2HaPFJlCzdvnll4nJRApUlkVt0JBR1+JTggajDNQyTClCG3Q4FkUcwMkNEEfHGPFCwaAo8N0w35gBow9Iyhj0z9fSvr0WSDBAg6+0I138pnngAppd6Qu/yxtqG9YKCgmXNmvWLBbmPhEgAN5Hb76ZGbndLPQRMtkDQtm5cwdz8lPY1+/idKw+4gXJGiwkAYoc9zdgQD/h/Q8cOMgKsV3AMlb7AqePSZ2LF79NgzkjCB+PdYBA8Y4efRFnYfuyhVkiABMDZTRHG3gqSHqSB7cH2e9/l1rRWj0pf9GiRfPZEuBpI6PsNsEBfKHIhNVyVguVKVddhYTFZgErBw4cEgGB2YIQoSC2k7B97Jjx0vm4YQgd6WcIEvHyju3b2PeNE0uBjBkwAkYp4un4WTgZsRRQLlucYl2QJnhU0RQvxIAVv+nSpYcoF0qoL710guT2IST4/K3sh+Hnj584ysmdI9F3kyZdIeYZgoPig6cAAARqB6JHMQ2STH379ROkDwUAT4ApXjbiQeX1mDFjZZQPHDBQVvIAYMR1rFrJjCvfL8591VSklodKX7gNbB8L/yvUytamVRmYiFjAHYrVRaLVh3r07CGlU3V1x8VvY8kzMFbr2Hdh5ID+3Lp1m9wUBIPKVwgFggS5g07BcqcwsQBRGF0oxEQNPIgPdBSEAuIFcTjKufS5O7A2ebPEmj7owT6WDaYYEYU+Rate6hvwHiXa2Ac8PoR78cUXaWTDeGDqVVP5mtdJVu6qq6eKOR7KBM/2Hdtk0sUmBmirmZ7FtcOcg7HLoUyb43wQNrBiEBZWWwE/gJk6uF6EgFOmTBUmFVm7o0drZLo3LAPIL4SFcKm43lmzPiY8P+r/0HfpBtDHx7iJXe8pamVrkwIYULjAPHY+WnYeYAfPrIWQlr+3go4eq+EOqmSma7CY2169+si8ehQyQEkwEweEyR7k4g1NAPR76fgJ3OHbBViiaAL7gH/HkzLgZ+ETIVBYExRhAD8gvQr+wU6hQkeCNKpjmnU0I/CRI0fJKMQ+oKFRuLFz527BK3BRAG6Xcnx+iiMXzMGr4pGOCttKjuX3siAlB8KXiGvBSIWVq6zsKqTYDlbOE3xcLNKA6AiKgQQOrAQsHY6Psi4oK5QaeYD+TCht3LhB6iDe5eQPsMDtt98uIeFbby0SMIwHWNkHP9gm6/tkMtc+/PDDe6kNrc3rsgAUIjJIKwFSxqhwnXj5RHYJaxhkZYQ0QpUtrAQZQIVpy7K2LRNI6DygbjxBo7JrZ3EBYORAicIHgnCBuUWnYHThFQQL9gMRhRi7C/PwGDGDBvWTkBQKAN8O4ARghbx5vXlgA5ZZRZwOMgX4BdamC1umyZOm0G9/M8+kumvZIuRo8pQrxCy/YpZdAZaYOPFSwSpwM8jLo1wbgkSYV80jfNKVk+ill16S6VsYzUgDH+PBgEgBCldRUS5P/MC1X3vtdbSeweGNM6+j//7vpzgKuEnYQgDhdHmXFX6xEq+WtrYvzENNKwEAEeLnMWPH0ErGBeC5MyyMO+74c9rELNoJJkPQgeg8+LcjR46K6dy1ewf17d+PlaKSDkhI2Z47ewJt2LieO+ZmidchGLgIAEBgAvhtuI0+zDxu2LBeqmJgbm+88QYZTeAUYEanTJ0sIG0871/OnVvJuAWlW0sYwY8aPYrWrlknnb5p80Y5HmbtIuybNHkyPf3kU8zI9RJA1445DNTtwwogMsGsIlTq9mEl6MHWb9v2rRKvIgdgWT5YMliu/v0HCu7A5337Dkjl9YsvviBl3wgtsawLuBONcpKA72wKH+2sKABaU0oA04Xih6ohVfKETAhvCLuCgYMGsCAuF2wAk75DfOsIuokFjHq23RxqhaY+fu2aNeI/165dLyNn6dJ3qEPH9tETMqBgHZhNg++EYsDHT59+De1l8mQAAyv4bzxmdfiI4dSfSatXOVwdyPE5snAQxNJ3l7LVydC69etp+rXXiqW46aaPygQO7Ne3Xx+q4PDtMKdwAew2sWKpRerEytGDlfRgZNHgw3sxQAXx88ILv5dRDsILrg7XAWuH0BXv9TGv9Zw5nCUCnzhxnLgNRAmwJCWp1b3PtvDRzpoCoDWlBALSmOHrzv4ZIA2uAIUUGBmoLbjmmmsEDPWX5c85t86mFjH5NgaL27ZV0+AhQ9hanBDhYnIkMMZ2jq+nTZ8upMhwBmfwnet55F/JZncPj0SMtNs+/nEmZN4T1I0qW+AHdCwUD+eAoDes38A5+PHCBFbzfnfddaekqjEfEIsvISsHFL+CrQiWXoHLgMkGlwEXh/sAXXWEowOAg/YdKhi9r5QFH2DqEV7GhBJHP3x/XbGKBysAiDLgAuQU4ILWrF3NbmiqKEwR4S/nfrzpbApfZENnuUEJGK0/wReL8HCU+x0KFjG6wX1DKQ7zqIAJBVuGKtnnnn1WKmG3M5iCiYUPRGcM4FG74KUFTKNeJHE/BNyVQdn+/XtpBXd2NXc0iiK2c6iImB0RxSc/+Sl6Z8m7Ysbv+PSnmUM4KiHk9TOup5/85CeCIdD5OAeWU0WkUsHKuYNj8OUrlguuePHF+fTXf/0VYeMWLHhJgJ99CjeEDyuAhA5YxC0c6pax6d7Gv4ebq2WXozmAUrOI4ynZD9aw/wBOHbcrl2sCqMR1IxmFkBDXla7qQajHbvD2tgK+Yu2sKwAaogMmi55J1xGgoWiyjIUOS3CcSQ9MYsBoQ/w/ZNhQOsR+/WIWIpTihz/8oYSJV8nz8UplFPXo2U3YOwDA0Wa/vn10ahdoUqBxuBnE6ldOniScAkJPPAZmGANORBVY4g1hHEYmFmTCiN23d68o2wSOCt5eslh4iI4dOnPyReldxPCYR4DrQI4fwkfJ9x/+8AfhJEDb4h6wEMRJFjisB/AJzt2RQ0TgjTHjxoqPRwg4beo0eTg1mEQoLfh9HCfdkNxBTV9bQr3TtXOiALaxEixkJcAsSzCG5XY7zFsJJ2AQL2tGrSPntt+REYGlXU+crKVFHAK9zyMOCZAaBooLFiyQoserGMQdPsLugn071r5DJ2N5NAgFGGKgcSPyiBQ215OnTJZQDhYG+fT32KSjrgDgCr4cPD7Krr505530X//5nyJUFGnACowaPVJ4eRwLAO0oWwIgcpRgr1jxnvHrx2VuHtwZwCP2BTYAeD3OYSpGfiNTwPX8N278OJnAeYoJp2FDh0uqGCAVSuzO4TOthjHOV3gQtIrha247pwqAxkqwmEf5M2lcgAbhgx/HevYQIJ6uvXbdWprJAkCoBd6gn1ntAqHYjm07ZL3bqkGDhVlEbgGmGKMHfhmxNwQE9wLLMWDQQAFl8377W5o/fz4rz1S6GgQP8+2wPBjxIJbGsmBQkrb0vWVyHEQNt3DYtmzpMtq+TYkfEFEIa1A2jrxGr969xSWgMAb8ALABzo17AmBFuAveAe4ODCNA6nHO8kGZwQ3gyR/4LSj0dAPYQ2KHR/5COsftnCsAGnABK8Kj6fwBGthAmD4oAkI8hEuTmSmDAuzkSADtPRYIKFsIEzH+K6+8IinTsWxS/8gmGIoAkw9kDYF+5jOfoVWrV9GTTz4pIRwSKkjPolBjxowZsi+yeTj+gj+8JBMw2zPKh+8FGHvj9ddlKRZYEwhPRj5q7flaZ978Udq/dz8D2m6yGhiII4SysGpwKSCkECZ27dpdYnyQTmA9oeB7OK8wjM8rU8XZxRRbvhUmn/39n58Lf1+seXSe27333judb/Lx9PMKbUPmEGTNKPaLR44eoW5M7HRi3PCznz1OM66bIf4U4SRCvDEcxoFLQGHkd77zHcEFyEgC2EEYjz/+OH3slo/J6BzMiqPUq044geAwYrNseue/+CLt5Kjix//yL/SrX/6SsixMmY3LVgJu5W1O1owZcwnjh50y0WOvEEqY6TtMLAvoYF1LISOTNaDECEWxOhdAHo4BawOLFi/Fm2wY9dwnX3BX7zgf7bxYALehsghRAncaMjjT098jlgZ7h6pi8AO/+91ztJHDu/vuu0/CrRdeeIF69+kt1gDPzkGHw/RjvhzA5F133SUCgALcdNNNIvCnnnpKWDwIBD7frtSxgSlYRB2gWgE8f/HMM7IaCKICLK+6eNFi8fNDOLsJsgrP6Xuaj5XjY0Oh6li4FskjREU4+/vf/15AHiIOKNwnP/lJKRCBxUnP2HHag6yMX2huGdfZbOddAdBMlLCQ/fATxhKMSu8DgmTr+1vMs/yyOjOWBQBiCAUoYPkQux9nEAgwN/OmmeJKQA7Bj9saBXD+MLn43bx584T7h4mG/x5sFll4e/FiAWJQHGTt4JYOsuCvuvoqsRZQGiw1/9JLf+DoYKD4/EkcYcByYBYPgCgUCqgeCofqJZh8i0nS5dpOW8j3di2qd88Vyj9Ta+m6bGe1GVLjdh7dn+fXucXcQmepeetEvdmXg0zCFG3MgAEjByHDFCPphDAPMTSKNaYzQfTEE0/Iun+PPPKICAbZuH/4h3+gl19+WUalFrH2EAEB/YNogtWAcgAjICcg6Vk+Hkw7Urwj2epgYgdC1XfffVcU0BI2GPFQQJh+KIw7PatIW0iaw19IH3A77xjgdO10iuA2ECtYCh1CBBF07733CIoHozaBRx1WAoc57tCxg1T9bNiwIQq1YN4xWmGyUXiBkYpYHqttIhePMA6WAb7+H1l57rjj04wlHpORP5AJqSVsLcA7zHt2nixOgSdzwLog6jjNSLdtIV0ggrftglIA2wAU+WUuFcEIxVovTtBITWGgU8JBx2IUgjv41J99ijZv2CQuBaN70qRJtGrVKlkfGA99wJNDf/zjH4sCvLzwFbEiSNUCSC5etEhA6R6mlUEbY2burFtukcWlO7Ll0LWFmtUW0gUmeNsuSAWwjYVSxQTLA+yTrzmTVXAbzDL88G4WGniD60EuMRYA3YsoAXPsWclkUQUQTwjjVq7kUDOjE0IQ+yNERAUuavp0QmeJM9WsWQ3FmY+a+XnL6QJtF7QCuO2ee+65jTsTZBIeKlRJF2arYUWdx9f5xIU42ou1D40CuM24iM/zH+qxx9MH2Mw8CWRA5zGgXP7AAw+cneXGz1P7UCqA2+AmGLiNZ9Q9nYVgFeJcWQgIt5qF/iq/LufzLuQoo5o+xO1DrwDFGkcT41kZoATjWVhV/DrIfK7kz5VN4Qk76wlPUsMfK9VR+55DxOUfdmEXa/8fQ79G5HHSfbcAAAAASUVORK5CYII=)