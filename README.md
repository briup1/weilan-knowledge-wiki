# Knowledge Forest（知识森林）

一个以 Obsidian 仓库形式运作的多领域 **LLM Wiki**：原始资料编译为可追溯知识，再按问题与领域检索输出。

## 先选择一个领域

| 入口 | 用途 |
|---|---|
| [软件开发与 Agent 工程](domains/software-development.md) | 软件设计、开发、测试、部署与 Agent 平台 |
| [AI + 自媒体](domains/ai-media.md) | 定位、研究选题、表达、生产、分发、经营与复盘 |
| [共享知识与方法](domains/shared.md) | 知识管理、研究与检索；查询时按需补充 |

[完整索引](index.md) 保留所有正式页面；领域入口只维护阅读路径，不复制知识。自媒体现有积累主要是制作工具，运营等能力仍待补充来源。

## 组织方式

**存储按类型，导航按领域，实践按项目。**

```text
raw/assets/ → 摄取、判域与查重 → wiki/ → 按域检索 → 回答 / drafts/
                     ↑                               ↓
                     └──── 新实验来源与复盘反馈 ───────┘
```

- `raw/assets/`：待入库资料与附件；`raw/archive/`：已处理的原始资料。原文不可改写。
- `wiki/`：sources、entities、concepts、synthesis、queries 五类知识页。
- `domains/`：三个领域的入口与能力导航，不是新的知识类型。
- `docs/knowledge/`：架构方案、受控领域注册表与迁移验收记录。
- `drafts/<project>/`：有目标读者的创作半成品，按需创建；不囤积原始资料。
- `scripts/knowledge/kb.py`：只读的领域筛选、关键词检索与结构审计。
- `index.md`：全局导航；`log.md`：只追加的操作记录。

每个正式 wiki 页用 `domains: [ai-media]` 等字段声明归属。跨域正文可以声明多个业务领域；通用知识使用独占的 `domains: [shared]`。主题标签仍用 tags，不重复维护领域标签。

领域隔离控制相关性，**不提供访问权限隔离**。需要不同共享权限时应另行拆库。

## 快速使用

需要 Python 3.12+，新工具仅使用标准库；不需要安装数据库、向量库或额外包。

### 摄取新资料

1. 将完整来源放入 `raw/assets/`，不改写已归档原文。
2. 查看待处理文件：

   ```bash
   python3 .agents/skills/llm-ingest/scripts/ingest.py scan .
   ```

3. 告诉 Agent：“将这份资料摄取到自媒体领域；提炼时先查重并独立判定共享知识。”
4. Agent 按 llm-ingest Skill 更新页面、索引和领域入口，归档来源并审计。

扫描脚本负责状态辅助，不会自动完成语义分类或编译。Claude 的对应 Skill 位于 `.claude/skills/llm-ingest/`，规则保持一致。

### 按范围检索

```bash
# 单域，不自动夹带软件工程或共享知识
python3 scripts/knowledge/kb.py search --domain ai-media --query 视频

# 按需加入共享知识
python3 scripts/knowledge/kb.py search --domain ai-media --include-shared --query 知识

# 显式跨域
python3 scripts/knowledge/kb.py search --domain software-development --domain ai-media --query Remotion

# 全库查重；空查询可列出范围内所有页面
python3 scripts/knowledge/kb.py search --all --query Remotion
python3 scripts/knowledge/kb.py search --domain ai-media --json
```

这是关键词工具，不是语义搜索引擎：空格分词、全部匹配、忽略大小写。Agent 根据问题选择范围和关键词，再阅读页面形成带来源的答案。没有结果不会自动扩域。

### 巡检与测试

```bash
python3 scripts/knowledge/kb.py audit
python3 -m unittest discover -s scripts/knowledge/tests -v
```

审计错误返回非零退出码；历史副本、链接歧义、来源链债务和陈旧日期单独警告。巡检仍需人工/Agent 审视矛盾与证据，不能仅靠机械检查。

## 维护约定

- 每份知识尽量只维护一次；同名实体页和来源页用明确路径引用。
- 来源、假设、个人实践观察与综合推断明确区分。
- 综合审视不可省略，但不为了页数创建空概念。
- 超14天提示可能过期，超30天强提示；只改领域字段不刷新知识日期。
- 动态能力和平台规则需要重新核验，不能把历史页面当作当前事实。
- 不擅自提交或推送，不覆盖用户本地改动。

详细规则：[架构与操作规范](docs/knowledge/architecture.md) · [领域注册表](docs/knowledge/domains.json) · [迁移验收记录](docs/knowledge/migration-2026-09-17.md)。

Agent 工作说明：[AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md)。当前页面数可运行审计获得，不在 README 维护易过期的静态规模。
