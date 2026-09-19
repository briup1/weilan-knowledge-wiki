---
type: domain
created: 2026-09-17
updated: 2026-09-17
domains: [ai-media]
tags: [navigation, content-creation]
title: "AI + 自媒体"
scope: knowledge
status: reference
projects: []
products: []
topics: []
source: []
related: []
---

# AI + 自媒体

范围：借助 AI 完成有价值的内容创作、传播、经营与验证，而不只是收集制作工具。

**当前覆盖**：已有积累集中在视频生成、剪辑、字幕与创作工具；运营、增长、商业化和合规仍缺系统来源。下面是建设框架，不是已验证的方法全集。“待建设”节点使用普通文本，取得来源后再编译为概念页。

## 能力地图

- 1. 定位与内容策略
  - 1.1 受众理解：明确服务的人群、需求与使用场景（待建设）
  - 1.2 价值定位：确定内容承诺、差异与长期内容支柱（待建设）
- 2. 研究与选题
  - 2.1 需求发现：从问题和反馈中识别值得回答的主题（待建设）
  - 2.2 资料核验：区分原始证据、转述与推断（待建设）
  - 2.3 选题评估：判断选题与受众、目标、资源的匹配程度（待建设）
- 3. 表达与叙事
  - 3.1 信息组织：把资料转化为清楚的观点与论证顺序（待建设）
  - 3.2 叙事设计：安排情节、案例和节奏以服务内容目标（待建设）
  - 3.3 风格一致性：维护语言、视觉和账号表达的一致性（待建设）
- 4. 内容生产
  - 4.1 图文生产：把选题转化为正文与配图（待建设）
  - [[wiki/concepts/ai-video-generation|4.2 AI 视频生成]]：将文本或其他素材转化为可编辑的视频内容
    - 4.2.1 模板驱动合成
      - [[wiki/entities/moneyprinterturbo|4.2.1.1 MoneyPrinterTurbo]]
    - 4.2.2 编程式视频创作
      - [[wiki/entities/remotion|4.2.2.1 Remotion]]
  - 4.3 编辑与质量控制：检查成品的事实、表达、音画与可发布性（待建设）
- 5. 发布与分发
  - 5.1 渠道适配：适配不同渠道的内容形式与使用情境（待建设）
  - 5.2 内容再利用：把同一知识组织成不同形式而非机械搬运（待建设）
- 6. 受众关系与增长
  - 6.1 反馈收集：识别读者的真实问题和体验反馈（待建设）
  - 6.2 关系维护：建立持续互动与信任（待建设）
- 7. 商业化与经营
  - 7.1 价值交付：明确产品或服务为受众解决什么问题（待建设）
  - 7.2 成本与转化管理：评估投入、收益和转化路径（待建设）
- 8. 实验与复盘
  - 8.1 指标设计：为内容目标定义可观察的结果（待建设）
  - 8.2 实验验证：记录变量、条件和局限，避免把相关性当成因果（待建设）
- 9. 权利与风险管理
  - 9.1 素材权利管理：记录素材来源、授权与使用边界（待建设）
  - 9.2 规则与隐私核查：按平台和发布时间核查适用要求（待建设）

## 现有资料入口

- 制作能力全景：[[wiki/synthesis/ai-video-media-landscape|ai-video-media-landscape]]。这是工具与工作流专题，不代替上面的完整领域地图。
- 生成与剪辑来源：[[wiki/sources/aidc-aipixelle-video|aidc-aipixelle-video]]、[[wiki/sources/autoclip|autoclip]]、[[wiki/sources/aicomicbuilder|aicomicbuilder]]。
- 编程创作来源：[[wiki/sources/opencode-remotion|opencode-remotion]]、[[wiki/sources/hyperframes|hyperframes]]。
- 运营研究起点：[[wiki/sources/aitoearn|aitoearn]]。工具的营销主张不能直接当作已经验证的经营方法。

这里只选择阅读入口，不重复罗列所有资料。链接到 source 表示已有资料，不表示已建对应工具实体页或验证其当前能力。

## 开始使用

```bash
python3 scripts/knowledge/kb.py search --domain ai-media --query 视频
python3 scripts/knowledge/kb.py search --domain ai-media --json
```

建议先围绕一个实际内容系列补充来源，再把成果写入 `drafts/<project>/`；实验记录作为新来源回流 raw → source → concept/synthesis。暂不代替用户创建账号或虚构创作项目。

返回 [[index]]；需要通用方法时查 [[domains/shared|共享知识]]，需要工程实现时显式跨到 [[domains/software-development|软件开发]]。
