---
title: "多领域知识库迁移验收记录"
type: documentation
updated: 2026-09-17
scope: knowledge
status: reference
projects: []
products: []
topics: [knowledge-management]
tags: [migration, validation]
source: []
related: []
---

# 多领域知识库迁移验收记录

## 基线与范围

- 日期：2026-09-17。
- 执行 `git fetch origin` 后，本地 master 与 origin/master 均为 `546df21`，无需合并。
- 开始时已有 `log.md` 未提交修改和未跟踪 `docker/`；均保留。本次没有 commit、push、reset 或 stash。
- 仓库共有 166 个 wiki Markdown 文件，其中 153 个是五类目录的直接正式页面，另 13 个是历史非标准路径。
- 原有 153 个正式页面**仅新增一行 domains**；没有移动、删除、重命名或重写知识正文，没有刷新旧 updated。
- 所有 191 个 raw 文件逐字节 SHA-256 比对一致；没有摄取新来源或修改原始文件。

## 落地方案

单库、五类知识类型保持不变；新增三领域入口、受控 domains 字段与只读按域检索。方案详见 [architecture.md](architecture.md)，注册信息见 [domains.json](domains.json)。

| 归属 | 唯一页面数 |
|---|---:|
| 仅 software-development | 120 |
| 仅 ai-media | 15 |
| software-development 与 ai-media 同时覆盖 | 4 |
| 仅 shared | 14 |
| 总计 | 153 |

按领域检索的计数因此为软件开发 124、自媒体 19、共享 14；跨域的 4 页不能重复计入总数。

跨域页：Remotion 实体、FlyCut Caption 来源、Hyperframes 来源、OpenCode + Remotion 来源。依据是现有正文同时讨论工程接口/实现与内容创作；并非所有能服务创作的软件都被自动标为跨域。

## 说明文档与工作流

- README：领域入口、按域检索、摄取与巡检命令，移除过期静态规模。
- index：顶部领域导航，保留所有知识页，限定同名 MoneyPrinterTurbo 的来源/实体路径。
- AGENTS / CLAUDE：一致的字段规范、摄取路由、查询范围、时效与验收规则。
- 两份 llm-ingest Skill 及参考文档：引用同一架构规范，增加判域、查重与验收步骤，取消页面数量配额。
- CONTEXT：明确 Agent 评测词汇只适用于软件开发领域，不作为自媒体的默认上下文。
- 自媒体入口：已有资料进入内容生产路径；其他能力诚实标为待建设，未创建空概念或虚构来源。

## 实际验证

| 检查 | 结果 |
|---|---|
| `python3 -m unittest discover -s scripts/knowledge/tests -v` | 25 项通过；覆盖范围隔离、显式共享/跨域、空结果不扩域、元数据错误、索引/来源/回链、只读行为及时效边界 |
| `python3 scripts/knowledge/kb.py audit` | 153 个正式页面；0 errors，5 类历史警告 |
| `search --domain ai-media --query 视频` | 18 个结果，全部包含 ai-media，不混入软件开发专属页 |
| `search --domain ai-media --query 数据库事务` | 0 个结果，未自动扩域 |
| `search --domain ai-media --include-shared --query 知识` | 15 个结果，范围仅 ai-media 与 shared |
| `search --domain software-development --domain ai-media --query Remotion` | 6 个结果，明确跨域，不重复输出同一文件 |
| 原页面内容与日期 | 153 页移除新增 domains 行后，哈希与迁移前完全一致 |
| 原始资料 | 191 个 raw 文件 SHA-256 均与迁移前一致 |
| 两份 Skill / AGENTS 与 CLAUDE | 归一化宿主文件名和宿主说明后，工作流一致 |
| `git diff --check` | 通过 |

以上结果是本次迁移的静态记录，后续维护以重新运行命令为准。关键词检索已实现；语义分类与生成答案仍由 Agent 完成，不宣称已实现语义搜索引擎。

## 既有债务与兼容边界

1. **13 个非标准路径**：`wiki/synthesis/concepts/` 下 12 个副本，以及 `wiki/notes/mcp-permission-middleware.md`。不删除，不纳入默认检索；其中部分副本与正式页不同，后续需逐一比较后治理。
2. **67 处裸 slug 歧义**：由历史嵌套副本、MoneyPrinterTurbo 同名来源/实体造成。新领域入口均使用明确路径，本次不批量重写旧正文。
3. **15 处间接来源引用**：部分旧 sources 指向现存 entity/concept/note，而非 source；另有 5 个非 source 页面 sources 为空。审计提示，但本次不伪造原始证据补齐。
4. **133 个页面超过14天**：其中包含大量超过30天的页面。日期未被迁移操作“洗新”；使用动态事实前需要核验。
5. **安全边界**：domains 只做相关性筛选，不是访问控制。历史原文可能含代码示例和疑似敏感值；本次没有授权公开发布，未执行提交或推送。

### 通用 at-kb 审计

按仓库指引实际执行了：

```bash
python3 /Users/ziyun/.claude/skills/at-kb/scripts/kb-audit.py --kb <仓库绝对路径>
```

该脚本针对另一套 `/Documents/knowledge` 元数据要求（title/scope/projects/source/related 等），会把本库合法的历史 wiki 格式、不可变原文及示例标为问题，不能直接宣称全库通过。

为区分本次问题与历史债务，另对 `git archive HEAD` 的临时副本运行相同脚本：基线 2142 项，工作区 2151 项。归一化因新增字段导致的行号偏移后，差额 9 项全部来自**用户原有的未跟踪 docker/langfuse/README.md**，不是本次修改。新增领域入口与维护文档没有引入该审计的新问题。

没有为了清零通用审计而改写 raw、用户文件或大批历史元数据。本库的权威结构验收使用 `scripts/knowledge/kb.py audit`；通用审计中的敏感值告警仍需在未来发布前单独审查。

## 后续使用

将新资料放入 raw/assets，要求 Agent 按目标领域摄取；通过首页领域入口阅读，或运行按域搜索。优先用一个实际自媒体项目补齐选题、表达、运营与复盘来源，不一次性铺设空页面。
