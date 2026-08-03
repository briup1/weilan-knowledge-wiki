---
title: "AI 知识库技术演进拆解：从 RAG 到 NotebookLM，再到 LLM Wiki"
source: "https://mp.weixin.qq.com/s/UtN4_bhOYBV3OnYIUGN4LQ?scene=1&click_id=6"
author:
  - "[[叶小钗]]"
published:
created: 2026-05-14
description: "技术拆解：NotebookLM 的七层系统，从文档理解到引用溯源"
tags:
  - "clippings"
---
叶小钗 *2026年5月14日 08:58*

> AI训练营 **10期** ， **6月底** 开班，欢迎咨询

NoteBookLM 是我比较推崇的一款 AI 知识库产品，他是一款基于用户上传资料的 AI 笔记与研究助手。

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/6Uzn2S5AAyRSMZ3McFs1xmFUUMKvWSLjLIBsgmyDuv6vDj79qN1XqcSySWMEfLwQicLzYVxcWbEss5MCPJYajO2x2XiaPyJIJ6o6nQultQw4Q/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

与 ChatGPT 或 Gemini 直接回答不同，它的核心逻辑是： **只根据你喂给它的资料来回答** ，极大地降低了 AI 幻觉。

根据我的测试，NoteBookLM 无论从内容检索精准，还是输出精准都已经勉强达到了 **数字分身/同事.skill** 的最低要求：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/6Uzn2S5AAyTNojbXXcW3Vm3reQqWO1wnMicLtnCDkMg3JHV4aUI4QpFUqTOFwLG6RmyYd2YztP0ZX6BnI9g86nILTVZXjgLmcJYiamy4vxY4M/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

严格来说，一套好的 AI 知识库大概率是一套 RAG 系统，但在 NoteBookLM 这套工具上我又看不到 RAG 存在的痕迹，作为 AI 知识库专研者，我一直对其技术路径非常感兴趣，于是揭秘者就出现了：

> Karpathy 在 2026 年 4 月 4 日发布了 GitHub Gist《LLM Wiki》

他的核心观点是：传统 RAG / NotebookLM / ChatGPT 文件上传，大多是：

> 上传资料 → 查询时召回相关片段 → 临时综合回答

但问题是：每次问问题，模型都在重新从碎片里 **现拼答案** ，知识没有持续沉淀。Karpathy 提出的 LLM Wiki 则是：

> 原始资料不动 → LLM 读取资料 → 增量维护一个结构化 Wiki → 不断更新实体页、主题页、交叉引用、矛盾点和综合结论

也就是说，它不是 **查询时拼答案** ，而是 **提前把知识编译成一个可持续演化的知识结构** ，这就跟我们之前做 ***深度 AI 知识库*** 所用到的知识很类似了：

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/6Uzn2S5AAyQrAV0wicTAMFU8qTbstrWKBAUnjypGoxLBUQSbfIVpicI3ugLwyuzuQ4S7ax39CTuOnQnhjjAUcPzWU9XRX3GibPwnpHlicg3rvNI/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

## NotebookLM 的技术路径

这里需要说明的是 Karpathy 并没有 Google 内部技术路径图，他也是在自己做推衍，但其文档是有一定价值的，提供了一些思路。

更进一步 Google 官方其实已经公开过一些关于 NoteBookLM 非常关键的技术线索：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/6Uzn2S5AAyQ0OicLAOZ5HDyTygUfhaRUafusEKz4rRW0r0yXQ4MibVjUbrBuPgeuNgSyEyDUyiaPFTsG1rNKtZWVRf8wFerj4JicClRmGj8b5KA/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

NotebookLM 是一个基于用户上传 sources 的 AI 笔记与研究助手，它可以根据用户提供的资料进行摘要、问答、生成 study guide，并且回答会带有引用，方便用户回到原文核查；

然后在 2025 年 10 月，更关键的信息产生了：

> Google 明确提到了 NotebookLM 内部存在一个 Retrieval and Ranking 过程，会从不同角度探索用户的 sources，再综合生成回答

这几个信息已经足够关键了。因为它基本说明 NotebookLM 不是一个简单的 **文件上传 + 大模型回答** 工具，而至少包含了几层能力：

```
Source 管理
    ↓
文档解析
    ↓
检索与排序
    ↓
长上下文组织
    ↓
基于资料生成
    ↓
引用与可追溯
```

**所以 NotebookLM 其本质也是 RAG，** 只不过他不是我们常见的 **低配 RAG** ，而是一套被长上下文、检索排序、上下文工程、结构化笔记、source grounding 包装过的高阶知识库系统。

传统 RAG 的存在感很强，因为它的链路暴露得很明显：

> 分块 → 向量化 → 检索 → 重排 → 拼上下文 → 回答

但所有可以配置 RAG 的产品，比如 Coze、Dify，其数据处理（包括数据清晰、分块）都是很复杂，很令人头疼的存在，于是大家在 NotebookLM 的产品体验里，你看不到这些东西了，包括：

1. ***知识库配置***
2. ***TopK***
3. ***向量召回***
4. ***重排模型***
5. ***score 阈值***
6. ...

但这并不代表它没有这些东西，而是因为 Google 把这套工程链路自动化、黑盒化了，但如果将他隐藏的工程化部分打开，应该是这么一套系统：

```
用户上传资料 Sources
        ↓
文档解析与结构化
        ↓
多粒度索引
        ↓
Retrieval and Ranking
        ↓
长上下文装配
        ↓
Gemini 基于资料生成
        ↓
引用、摘要、问答、报告、音频
```

接下来，我们继续做展开：

## RAG 产品化

既然 NotebookLM 本质上仍然是 RAG，为什么我们使用的时候完全感受不到 RAG 的存在？

这里我只能根据很多文档以及自己这三年的实践做猜测了：

> 传统 RAG 是一套开发者工具链，而 NotebookLM 更像一套被高度产品化之后的知识系统

传统 RAG 是什么感觉？

你要自己准备资料，自己清洗，自己分块，自己选择 embedding 模型，自己建向量库，自己决定 TopK，自己决定是否上 BM25，自己决定是否上 rerank，自己写 prompt 约束模型，自己处理资料不足时的拒答逻辑。

这一整套链路非常工程化，也 ***非常折磨人*** ，比如一个最普通、也是最恼火的问题： **怎么分块？**

1. 你按固定长度分块，可能会把一个完整观点切碎；
2. 你按标题分块，遇到结构不清晰的文档又会崩；
3. 你按段落分块，可能 chunk 太碎，语义不完整；
4. 你 chunk 太大，召回不准；
5. 你 chunk 太小，回答没有上下文；
6. ......

这里单单还是技术层面的问题，还不说数据怎么集合的问题，所以现在很多企业根本玩不起知识库，全部还在工作流的范畴左右横跳，原因无他，AI 知识库的工程细节过多了。

所以，如何将这套 RAG 工程链路产品化、黑盒化就是 NoteBookLM 类知识库产品在思考的问题了： **把各种复杂的工程配置项变成系统默认能力** 。

从用户视角，只需要关心三点：

1. 我上传了哪些资料？
2. 我想问什么问题？
3. 我是否能回到原文核查？

至于背后的：

1. 怎么解析？
2. 怎么清洗？
3. 怎么切块？
4. 怎么建索引？
5. 怎么召回？
6. 怎么排序？
7. 怎么拼上下文？
8. 怎么做引用？

全部由系统完成，整个黑盒是把知识库工程收进系统内部了。

那问题来了，如果 NotebookLM 把这些复杂工程都藏到了产品后面，那它背后的系统到底可能是什么样？

我认为可以先用一张整体技术架构来理解，可以将整个链路分为七层：

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/6Uzn2S5AAyRYY4pVVPSVrZ2FVJKg7Tuibzsf84p8HmqvIibpUsBWgaOMjdI7eFicfHu3jQOXic46J3qVe9icHNUA6puQmAKNbjYJCDvqm6gVVuEI/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

## 一、Source 接入

NotebookLM 的入口是 sources，这背后是有点逻辑的，名字不同意义就不同。

普通文件上传是：

```
我给模型一些上下文，让它临时读一下
```

sources 的话，意味着：

```
我把这些资料加入一个 Notebook，后续所有问答、摘要、报告都围绕这些 sources 展开
```

所以，NoteBookLM的对象展开就不是单个文件了，而是一个资料节点：

```
Notebook
  ├── Sources：用户上传的资料
  ├── Notes：用户笔记
  ├── Conversations：历史对话
  ├── Indexes：索引系统
  └── Settings：Notebook 配置
```

这里的核心是产品抽象，也就是 **把资料当成可以被引用和追溯的事实来源。**

## 二、文档理解

很多 RAG 的第一步都是 **PDF 转文本，** 但如果你真做过企业知识库就知道，这一步工作量非常大，也容易处理得很粗糙。因为一份资料里真正有价值的不只是正文，还有：

```
标题层级
章节关系
页码
表格
图片
图注
目录
脚注
参考文献
时间
作者
来源
```

而我们在整理的时候，很容易把这些弄丢，于是我们糊弄文档后，就轮着 AI 来糊弄我们了，比如一份报告里有一个结论：

```
企业落地 Agent 最大的风险不是模型能力，而是业务流程不可观测
```

这句话如果单独切出来，模型就不可能知道它属于哪个章节、对应哪个案例、是不是作者结论、有没有限定条件。

如果要做 RAG 产品的话，在文档理解层就要下功夫，要做的不只是抽文本，而是恢复结构：

```
原始文件
    ↓
文本抽取
    ↓
版面分析
    ↓
标题层级识别
    ↓
表格 / 图片 / 图注处理
    ↓
章节树构建
    ↓
元数据绑定
```

这一步决定了知识库的上限，因为后面的 chunk、索引、引用、上下文扩展，都依赖这里的结构。

如果这里做得很差，后面就只能在一堆碎片里 **硬搜** 。

所以这里 RAG 产品第一个难点也可能是最大的难点也就来了： **把原始资料还原成机器可处理、可切分、可索引、可引用的结构化文档。**

这也是很多企业知识库效果差的根源。大家太早进入了向量库和 embedding，却忽略了前面的 document understanding。

这里我也补一句：

> **就算我们知道了这是 NoteBookLM 技术路径的核心，但我们其实也是做不出来的**
> 
> 因为 Google 本来在信息搜索这块就是世界 T0 级别的，所以他们在文档处理这边会很屌，一般的公司技术力没有那个位置
> 
> 比如同样的知识库产品 腾讯IMA，他们技术路径应该是类似的，但效果就会差很多，原因就出在文档理解这里

## 最难：文档理解

这里可以再展开一点，因为我现在越来越觉得， ***文档理解可能是整个 RAG 产品里最难的一层。***

很多人以为 RAG 的难点在向量库，在 embedding，在 rerank，但这些东西更多是 **检索算法层** 的问题；真正决定知识库上限的，往往是前面的资料有没有被正确理解。

> 因为他们本质上都是在 **已经被处理好的材料** 上做优化

如果文档理解做得不好，后面就会进入一种很尴尬的状态：

```
垃圾解析
    ↓
垃圾切块
    ↓
垃圾向量化
    ↓
垃圾召回
    ↓
模型一本正经地基于垃圾回答
```

这也是为什么很多企业知识库一开始 demo 看起来还行，但一进入真实资料就崩。

因为真实企业资料不是干净的 Markdown，而是 PDF、Word、PPT、扫描件、表格、合同、财报、产品手册、培训材料、客服记录的混合体，他们会烂到你看不下去...

人类读文档的时候，会天然理解页面结构。我们知道哪个是标题，哪个是正文，哪个是脚注，哪个是表格，哪个是图注，哪个是附录，哪个是引用来源。

这里的所谓 **文档理解** 其实就是要去模拟着整个部分，但现阶段用 AI 做文本抽取，很容易把这些结构全部打平：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/6Uzn2S5AAyR2LlCCgmYPMxstHmeMMMo57vb9nRLibR40kWlDlNxuRBniaeX0ChH9w1Vfb8j5P1Ttw4WhZkUN69aB6xNQfTCGTOoc8FZvGh39g/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

这里最核心的是两个字： ***还原。*** 不是把文档转成文本，而是尽可能还原文档原本的知识结构。比如一份公司年报里写：

```
7 经营情况讨论与分析
  7.2 收入与成本
    7.2.1 毛利及毛利率
```

如果系统只抽出了

```
2024 年公司毛利率为 38.4%
```

那么这个片段本身当然有用，但它的语境已经丢了一半， **它属于哪个章节？是不是管理层讨论？是不是财务报表注释？有没有同比解释？有没有影响因素？** 这些信息都需要通过章节结构才能找回来。

再比如表格，很多企业知识库真正有价值的信息都在表格里。合同金额、项目周期、产品参数、财务指标、医学推荐等级、实验结果，往往都不是自然段，而是二维结构。如果表格被解析成一串混乱文本：

```
年份 收入 毛利率 2023 100亿 35.2% 2024 120亿 38.4%
```

模型虽然可能猜出来，但这就已经进入不稳定状态了，更好的做法是把表格转成结构化对象(markdown或者HTML都行)：

```
Table
  ├── title：经营指标
  ├── columns：年份 / 收入 / 毛利率
  ├── rows：2023 / 100亿 / 35.2%
  ├── rows：2024 / 120亿 / 38.4%
  └── page：46
```

这样后面无论是检索、引用，还是回答 **2024 年毛利率是多少** ，都会稳定很多。

所以我猜 NotebookLM 这类产品，在文档理解层一定不是简单 OCR，而是会做非常重的 document understanding。它至少要知道：

```
这一段属于哪个 source
属于哪个章节
在第几页
前后文是什么
是不是表格
是不是图注
是不是脚注
是否能作为引用证据
```

这也是为什么 Google 做 NotebookLM 有天然优势。 **因为 Google 本来就是搜索、OCR、文档解析、网页理解、多模态理解领域最强的公司之一。它在文档理解这层的积累，普通创业公司很难复刻。**

至于说如何实现，我觉得 PageIndex 这种技术思路也值得关注：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/6Uzn2S5AAyQBslcHMmKWJ5xw7mxsKCw6vFZmWDnbl3mS4HWkeibI2wYV3icxjxS1VUk7SNq0Z2MFBZCSYSiacvcJuomS9BVvemlCCUy9px8LXo/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

它的核心不是直接把文档切成一堆 chunk，而是先把长文档解析成类似目录树的结构，再基于树搜索去定位相关章节，这个思路其实很接近人读文档的方式：

```
# 7 经营情况讨论与分析（MD&A）
## 7.2 收入与成本
### 7.2.1 毛利及毛利率
... 2024 财年，公司毛利率为 **38.4%**（见合并利润表注释 3）...
```

本身的文档是很大的，他解析出来变成了这样：

```
{
  "title": "Management’s Discussion and Analysis",
"node_id": "0004",
"page_index": 35,
"nodes": [
    {
      "title": "Results of Operations",
      "node_id": "0005",
      "page_index": 40,
      "nodes": [
        {
          "title": "Gross Margin",
          "node_id": "0006",
          "page_index": 45,
          "summary": "2024 年毛利率及同比变动，影响因素为产品结构与成本控制..."
        }
      ]
    }
  ]
}
```

思路肯定是对的，但实际使用起来就差点意思了，而且从底层结构来说，它更适合结构化长文档， **不一定适合客服记录、聊天记录、碎片化 FAQ、短文章合集这类弱结构资料。**

真实系统里，更可能是混合策略，这里就能体现出 RAG 产品的工程复杂度了：

```
结构化长文档 → 文档树 / PageIndex / 树搜索
碎片化知识 → 向量检索 + BM25 + Rerank
表格型资料 → 表格结构化 + 字段查询
多模态资料 → OCR / ASR / 图表理解 / 多模态摘要
```

好了，我们这里不展开，继续打开 NoteBookLM 的七层黑盒：

## 三、Chunk

传统 RAG 喜欢讨论 chunk size，RAG 产品一定不会只有一种 chunk，它更可能维护多种粒度：

```
Source 级别
Chapter 级别
Section 级别
Paragraph 级别
Chunk 级别
Sentence 级别
```

为什么要多粒度？因为不同问题需要不同粒度的证据：

1. 用户问一个细节问题时，需要 paragraph 或 chunk；
2. 用户问一个章节观点时，需要 section；
3. 用户问几份材料的整体结论时，需要 source summary 或 chapter summary；

所以系统不可能只存一种 chunk。更合理的结构是：

```
Document Tree
  ├── Source
  │    ├── Chapter
  │    │    ├── Section
  │    │    │    ├── Paragraph
  │    │    │    └── Chunk
```

这里最关键的依旧是： ***还原*** ，也就是 **chunk 不能和原文结构脱钩。** 一个 chunk 应该知道：

```
它来自哪个 source
属于哪个章节
前后文是什么
页码是多少
原文位置在哪里
能不能回溯引用
```

这里的 chunk 就是带结构的逻辑单元了，可以粗略理解成：

```
Chunk
  ├── text：文本内容
  ├── source_id：来自哪个资料
  ├── section_id：属于哪个章节
  ├── position：原文位置
  ├── page_range：页码范围
  └── citation_ref：引用回溯信息
```

这里是可溯源的关键，证据早就准备好了。

## 四、索引

与之前一样，如果要做 RAG 产品，那么所有可能的索引形式，什么时候适合什么就全部要熟悉了：

```
Vector Index
处理语义相似。

Keyword / BM25 Index
处理关键词精确匹配。

Metadata Index
处理来源、时间、类型、作者、页码等过滤。

Document Tree Index
处理章节层级和上下文扩展。

Citation Index
处理引用回溯。

Conversation / Note Index
处理用户笔记和历史对话。
```

所以这里可以将整个入库流程串起来了：

```
Source
  ↓
文档解析
  ↓
结构化文档树
  ↓
多粒度切分
  ↓
生成向量索引
  ↓
生成关键词索引
  ↓
生成元数据索引
  ↓
生成引用映射
  ↓
写入 Notebook
```

这一步对比传统 RAG 时候要注意： **高阶 RAG 不是不要向量库，而是不能只有向量库。** 甚至一轮走下来，可能多数情况下可能真的用不上向量库...

> 因为向量检索适合找语义相似，但不适合解决所有问题，甚至多数时候都不适合

比如这些场景下，关键词索引往往更稳定：

```
某个专有名词
某个产品名
某个公式
某个引用页码
某个明确标题
某个用户笔记里的关键词
```

所以 NotebookLM 的 Retrieval and Ranking，很可能不是单一路径，而是混合检索。

## 五、Retrieval and Ranking

到了这里，才进入我们熟悉的 RAG 核心环节。

但 NotebookLM 和低配 RAG 的相比，肯定不可能把用户问题直接丢给向量库搜一下。

它大概率会先做问题理解，这里又是一连串 **RAG 工程改写** 了，比如用户问：

```
这几份资料里，对 AI 知识库未来发展最重要的判断是什么？
```

这个问题其实包含多个子任务：

```
找出每份资料里的核心判断
比较不同资料之间的共同点
识别冲突观点
提炼长期趋势
给出综合结论
```

所以系统需要先生成一个 query plan：

```
用户问题：
这几份资料里，对 AI 知识库未来发展最重要的判断是什么？

Query Plan：
  1. 找出资料中关于 AI 知识库未来趋势的内容
  2. 找出资料中对 RAG 局限的判断
  3. 找出关于知识结构化、Wiki 化、知识图谱的内容
  4. 找出 NotebookLM 与传统知识库的差异
  5. 找出数字分身 / 同事.skill 相关技术路径
```

然后系统再做多路召回：

```
每个子问题
  ↓
向量检索
  ↓
关键词检索
  ↓
元数据过滤
  ↓
候选内容合并
  ↓
去重
```

再进入排序：

```
候选证据
  ↓
相关性评分
  ↓
可信度评分
  ↓
引用质量评分
  ↓
覆盖度判断
  ↓
最终排序
```

这里影响 Ranking 的条件可就多了，除了相关性以外还有：

```
是否来自可信 source
是否覆盖多个 source
是否有足够上下文
是否和问题意图匹配
是否与其他证据重复
是否包含明确结论
是否适合作为引用
```

这一连串工程动作下来，大家就会认为 NoteBookLM 回答得很靠谱了，只不过还是那个逻辑，在整个文档理解那块其实就决定了这里能回答得怎么样，前置数据处理才是上限。

## 六、Context Engineering

NotebookLM 这种系统，在这里会进入 Context Engineering： **它要把候选证据组织成一个模型真正能用的上下文包。**

这个 Context Package 可能包含：

```
用户问题
问题意图
候选证据
证据所属 source
章节上下文
前后文扩展
多份资料摘要
历史对话
用户笔记
引用映射
回答约束
资料不足时的处理规则
```
![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/6Uzn2S5AAyQ0iatvWrdnLpZ6NDWJiaTK8au1icR5ibaBicfXdRRUOacPCicWCaWUWGRUpRB99DruyyAA33gD9cVibmMPVloasnibV1EQpGFD6SYXvsM/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

有些同学可能就会说了，现在模型不都号称百万 Token 了吗，管他这么多干嘛，直接全塞进去不行？

只不过， **百万上下文不是让你无脑塞全文，而是让你在证据之外，还能放入更多结构化辅助信息。** 比如：

```
证据前后文
章节摘要
source 摘要
历史对话
用户笔记
冲突观点
引用映射
```

模型底层也是具有注意力机制的，千万不要把模型当垃圾场。

## 七、答案生成

最后就是生成了，这类 AI 知识库产品，一般要遵守几个规则：

```
只基于资料回答
资料不足时保守回答
回答中的关键结论要能绑定证据
不同 source 有冲突时要指出冲突
不要把推断说成事实
```

所以生成链路大概是：

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/6Uzn2S5AAyQbLZiaedibLa46Bsg6IbFL9GzO1IqbG6DkryFlmdbbZGRziboZdpkCxE89cJ6mwIbQaNyWzfZcibxox8VZVGCELYIzy5oibqEWdnaM/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

其实核心就是可溯源，也就是：

```
这句话来自哪个 source？
依据是哪几个 evidence block？
能不能回到原文？
如果没有依据，要不要删掉或弱化？
```

## 技术路径的最终演进

把上面全部串起来，一个 NotebookLM 类系统的完整回答流程大概是：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/6Uzn2S5AAyT8W6NwV1m50nxuGzVfM4SG4eEyibHFDWD7Uy0cltoXIWDcLvocNPkPYjOgD9o0ibOPd9CypufPjLYvOhrs9z6E2UUfPsUlMia4Pg/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=9)

所以，如果我们把 NotebookLM 拆开，它并不神秘， **它仍然是 RAG。**

但它不是低配 RAG，而是把 RAG 的前处理、检索、排序、上下文组织、引用追溯和知识产品输出做成了一套完整系统，说实话一般公司应该做不了这东西，挺复杂的...

讲到这里，再回头看 Karpathy 的 LLM Wiki，整个链路就会更加完整了：

1. NotebookLM 主要解决的是： **资料如何被可信地问答和研究？**
2. LLM Wiki 进一步解决的是： **资料如何被持续沉淀成结构化知识？**

所以 **系统自动清洗、切块、索引、检索** 这件事，不能直接叫 Wiki 化，它应该叫：

> RAG 工程自动化

而 Wiki 化是下一层：

> 知识结构沉淀

可以看到，NotebookLM 已经有一些 Wiki 化倾向，比如摘要、Study Guide、Briefing Doc、用户笔记、引用回溯。

这里可能也回答了后续 RAG 类 AI 知识库项目的技术路径会如何演进：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/6Uzn2S5AAyTWPajKyK7n8aov31yRwVV2e6zvavPF7ibpIJepicy1ujFaE3s9QUYrnu1Kp5vZ73g86zfyIG2yGfg35ibw5IPhFQFib9ibeoaUVqJE/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=10)

AI 知识库的技术路径大概会经历三个阶段：

- **第一阶段：低配 RAG**

资料切块 → 向量化 → 检索 → 回答

- **第二阶段：NotebookLM 类产品化 RAG**

文档理解 → 多索引 → Retrieval and Ranking → Context Engineering → Source Grounding → 知识产品输出

- **第三阶段：LLM Wiki / 深度知识库**

知识抽取 → 实体识别 → 主题页生成 → 关系链接 → 冲突检测 → 增量更新 → 持续演化

这三个阶段是一个逐层叠加的过程：

1. 低配 RAG 是底座。
2. NotebookLM 把这个底座产品化、自动化、可信化。
3. LLM Wiki 再进一步，把知识结构沉淀为长期资产。

所以回到最开始的问题： **NotebookLM 的核心实现逻辑，是不是就是系统帮我们做掉了清洗、切块、向量化？**

答案可能是，但各位依旧逃离不了 RAG...

