---
title: 多领域知识库架构与操作规范
updated: 2026-09-17
status: adopted
tags: [knowledge-management, multi-domain]
type: documentation
scope: knowledge
projects: []
products: []
topics: []
source: []
related: []
---

# 多领域知识库架构与操作规范

## 决策与边界

采用**单库、类型存储、领域导航、显式范围检索**。保留五类 wiki 页面、现有 slug、raw 归档与 drafts 工作流，不按领域复制目录，不引入数据库或向量服务。

- `wiki/<type>/` 回答“这是什么性质的知识”。
- `domains` frontmatter 回答“该页实际覆盖什么领域”。
- `domains/` 是人工策展的领域入口与能力地图，不是第六类知识页。
- `docs/knowledge/` 是本库的维护规范，不作为外部知识来源。
- `drafts/<project>/` 是有目标读者的创作项目；排期、实时指标不充当已验证知识。
- 这是**相关性隔离，不是权限隔离**。敏感内容不能依赖领域标签保护；不同访问权限、协作或发布边界出现后，再拆仓库。

## 领域注册与页面归属

受控领域 ID、名称、入口、范围的唯一注册表是 [domains.json](domains.json)。当前注册 `software-development`、`ai-media`、`shared`。新增领域先登记、创建入口，再标注页面；不随文章临时造领域。

所有五类 wiki 正式页面必须增加 `domains`，其他已有字段保持兼容：

```yaml
---
type: concept
created: 2026-09-17
updated: 2026-09-17
domains: [ai-media]
sources: [source-slug]
tags: [content-strategy]
---
```

- `domains` 使用非空、无重复的 YAML 行内列表；值只能来自注册表，列表次序不表示优先级。
- 单域页面：`domains: [ai-media]`。
- 页面正文确实覆盖两域：`domains: [software-development, ai-media]`，仍只保留一份正文。
- 真正通用的方法或工具：`domains: [shared]`。`shared` 必须独占，不与业务领域混写；它不是“不知道如何分类”的收容箱。
- Agent Runtime、数据库等不能因为“未来也许能用来做自媒体”就成为共享知识；判断依据是**当前正文**，不是工具的潜在能力。
- 来源按整篇内容归属；提炼的 entity/concept 按自身正文独立归属，不机械继承来源领域。
- 不重复增加 `domain/*` 标签或额外主领域字段。`tags` 只保留主题标签。
- 尚无法分类的新资料留在 `raw/assets/`，列出疑问；不以错误领域强行完成摄取。
- `updated` 表示正文知识最后更新。只修改领域元数据不刷新旧页面日期，迁移日期记入日志；不能借结构调整掩盖陈旧知识。

## 领域入口与概念地图

首页先列领域入口，再保留完整的五类索引。入口负责选择阅读路径，不再维护全量页面清单；全量范围由检索命令提供。

领域地图遵守 AGENTS.md 的四层语义：**模块 → 能力/稳定概念 → 方法/模式 → 技术/实现**。

- 二级能力写成“编号 名称：一句话职责”；已有概念页时链接。
- 暂无资料的能力使用普通文本并标注“待建设”，不创建空卡片或死链。
- 不把文章名、具体产品放到二级，不为美观强行填满四级。
- 地图内维护能力职责，不另建重复的节点说明列表。
- 自媒体地图是建设框架，不意味着已经掌握运营或商业化方法。

## 进入：按域摄取

1. **声明路由**：读取本规范、注册表和 index；根据用户目标与资料正文给出拟归属领域、可能的共享概念。用户指定领域是线索，不能扭曲来源内容。
2. **去重**：先在目标域查已有页面，再查共享域，最后做一次全库同名实体/概念查重。新资料中出现跨域概念，不等于要复制一份。
3. **保存证据**：raw 不改写；新增来源版本另存。source 有 `raw` 和底部“原始文件”链接。自己的实验记录同样可作为原始来源。
4. **编译**：source/entity/concept 分别判定 domains；区分“来源主张、待验证假设、实践观察、综合推断”。非 source 页通过 source 页回溯原文。
5. **综合**：先审视域内地图和方法，再判断是否需要跨域综合；没有新增综合时记录理由。不能为了页面数量制造空概念。
6. **导航**：更新 index 全量目录；只有阅读路径或能力覆盖改变时才更新对应领域入口。
7. **验收与归档**：检查 domains、索引、链接、source/raw 导航，再移动已处理文件到 archive，最终复检并追加日志。

示例：一篇“用代码生成短视频”的来源可能属于两域；视频生成概念属于 ai-media；已有 Remotion 实体因正文涵盖编程接口与创作用途可属于两域。它们的 domains 不需要一致。

## 输出：先定范围，再检索

查询时先声明：**目标领域、是否包含共享知识、是否跨域、输出用途**。

- 明确单域：只搜目标域，必要时显式加入 shared；不是所有问题都需要共享页。
- 用户未指定，但问题含义明确：说明推断的领域后查询。
- 确有多义且会影响答案：询问一次；不要无提示全库混搜。
- 明确跨域：指定多个领域，标明各领域知识在答案中的用途。
- 没找到：如实说明本域证据不足，提出扩域/补充来源；不能自动扩大范围并冒充本域答案。
- 范围是候选页过滤，不是关联链封锁。可按 source 链追溯证据；若引入另一个领域的新结论，应说明扩域理由。

```bash
# 精确单域；不自动包含共享知识
python3 scripts/knowledge/kb.py search --domain ai-media --query 视频

# 需要通用方法时显式补共享知识
python3 scripts/knowledge/kb.py search --domain ai-media --include-shared --query 知识

# 明确跨域；多个领域取并集
python3 scripts/knowledge/kb.py search --domain software-development --domain ai-media --query Remotion

# 显式全库查重；无 query 时列出整个范围
python3 scripts/knowledge/kb.py search --all --query Remotion
python3 scripts/knowledge/kb.py search --domain ai-media --json
```

该命令是**正文/标题/文件名的关键词检索**，空格分开的词全部匹配，忽略大小写。不做分词、语义召回或答案生成；自然语言问题由 Agent 拆成关键词，多次检索后阅读页面。输出包含路径、领域、updated 与时效提示；JSON 便于后续工具消费。

答案按“结论 → 适用条件 → 依据 → 不确定性/下一步”组织，引用明确页面路径。不能把来源宣传或单次实验写成通用事实。复用价值高的答案归档到 queries，使用本次实际覆盖的 domains，补来源并更新索引和日志。

## 时效与证据

- `updated` 超过 14 天提示可能过期；超过 30 天强提示，均不阻断阅读。
- 工具能力、价格、平台规则等动态主张，回答当前状态前回查权威来源；结构迁移不是事实核验。
- 实验记录保留目标、假设、样本/条件、变量、时间窗口、指标、结果、局限。
- 创作项目复盘中产生的新结论，作为新来源进入 raw，再编译到 wiki；不让 wiki 反向依赖 drafts。

## 维护与兼容

```bash
python3 scripts/knowledge/kb.py audit
python3 -m unittest discover -s scripts/knowledge/tests -v
```

审计覆盖正式页面的领域字段、类型、日期、索引覆盖、wikilink 目标、source/raw 回链及 sources 引用，检查领域入口。错误返回非零状态；时效、历史非标准目录、历史简写歧义，以及指向现存非 source 页或为空的历史 sources 作为警告；真正不存在的来源为错误。新增内容仍必须遵守 source 引用规范，不能把兼容警告当作许可。

正式页面范围为五个类型目录的**直接 Markdown 子文件**。历史 `wiki/synthesis/concepts/` 副本和 `wiki/notes/` 不参与默认检索，不删除，也不能继续向其中新增正式知识。新增嵌套目录需先修改规范与工具。

同名 source/entity 允许表达不同类型的知识，但必须使用路径限定链接，例如 `[[wiki/entities/moneyprinterturbo|MoneyPrinterTurbo 工具]]` 与 `[[wiki/sources/moneyprinterturbo|MoneyPrinterTurbo 来源]]`。`sources` 字段仍只解析到 `wiki/sources/`。历史裸 slug 链接歧义保留警告，新增或改写的正文不得新增歧义。

AGENTS.md 和 CLAUDE.md 保持同一工作流，仅宿主说明不同；两份 llm-ingest Skill 与参考文档同步修改。规范以本文件为单一维护入口，Skill 不另定义一套领域规则。

## 本次验收目标

- 远端状态已检查；用户未提交改动不覆盖、不提交。
- 153 个原有正式页面都有按现有内容判定的受控领域；原正文与原始来源不变。
- 三个领域入口可用，自媒体待建设能力明确可见。
- 单域检索不会夹带只属于其他领域的页面，共享与跨域必须显式选择。
- 领域、索引、导航审计与工具测试通过；遗留问题单独报告，不伪装成全库零债务。
