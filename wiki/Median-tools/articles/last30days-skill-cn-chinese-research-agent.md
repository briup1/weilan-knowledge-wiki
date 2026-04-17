---
title: "last30days-skill-cn：中国平台深度研究引擎"
source: "https://github.com/Jesseovo/last30days-skill-cn"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "AICoding", "type/tool", "Agent-Skill", "ClaudeCode", "Cursor", "Research", "爬虫", "中国平台"]
status: "archived"
references: "Archive/Jesseovolast30days-skill-cn last30days-cn 是一个 AI Agent 技能（Skill），能够自动搜索中国互联网 8 大主流平台最近 30 天的内容，综合分析后生成有据可查的研究报告。.md"
---

> last30days-skill-cn 是一个 AI Agent 技能（Skill），能够自动搜索中国互联网 8 大主流平台最近 30 天的内容，综合分析后生成有据可查的研究报告。

## 核心能力

**30 天的研究，30 秒的结果。8 大平台。零过时信息。**

本项目基于 [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) 进行深度本土化改造，完全面向中国用户和中文互联网平台。

v2.0 集成 [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) 爬虫引擎思路，大幅减少 API Key 依赖——7/8 平台无需配置即可使用。

## 平台支持

| 平台 | 模块 | 数据获取方式 | 需要配置 |
| --- | --- | --- | --- |
| 微博 | `weibo.py` | API / 爬虫 / 公开接口 | 爬虫模式无需配置 |
| 小红书 | `xiaohongshu.py` | API / 爬虫 / 公开接口 | 爬虫模式无需配置 |
| B 站 | `bilibili.py` | 公开 API / 爬虫备用 | 无需配置 |
| 知乎 | `zhihu.py` | 公开搜索 / 爬虫备用 | 无需配置 |
| 抖音 | `douyin.py` | API / 爬虫 / 公开接口 | 爬虫模式无需配置 |
| 微信 | `wechat.py` | API / 搜狗搜索 | `WECHAT_API_KEY`（可选） |
| 百度 | `baidu.py` | 公开搜索 / API | 基础搜索无需配置 |
| 头条 | `toutiao.py` | 公开接口 | 无需配置 |

## 三级自动降级策略

v2.0 采用三级自动降级策略，确保最大可用性：

```
优先级 1: API 模式（如配置了 API Key）
    ↓ 失败或未配置
优先级 2: 爬虫模式（MediaCrawler，需要 Playwright）
    ↓ 失败或未安装
优先级 3: 公开接口（HTTP 直接请求，无需任何配置）
```

## 安装方式

### Claude Code

```bash
# 方式一：通过 Marketplace 安装（推荐）
claude install Jesseovo/last30days-skill-cn

# 方式二：手动安装
git clone https://github.com/Jesseovo/last30days-skill-cn.git ~/.claude/skills/last30days-cn
```

### Cursor

```bash
git clone https://github.com/Jesseovo/last30days-skill-cn.git
# 将 SKILL.md 添加为项目技能
```

### OpenClaw / ClawHub

```bash
git clone https://github.com/Jesseovo/last30days-skill-cn.git ~/.agents/skills/last30days-cn
```

### 通用 Agent

任何支持 **Bash / Read / Write** 工具的 AI Agent 都可以使用本技能。

## 快速开始

### 安装依赖

```bash
pip install jieba

# 推荐：安装爬虫引擎（启用 7/8 平台零配置）
pip install playwright
playwright install chromium
```

### 诊断配置

```bash
python scripts/last30days.py --diagnose
```

输出各平台的可用状态和爬虫引擎状态。

### 基本用法

```bash
# 紧凑输出
python scripts/last30days.py "AI编程助手" --emit compact

# 深度搜索并保存结果
python scripts/last30days.py "新能源汽车" --deep --save-dir ~/Documents/research

# 仅搜索最近 7 天
python scripts/last30days.py "热门话题" --days 7

# 指定搜索源
python scripts/last30days.py "Python教程" --quick --search bilibili,zhihu

# JSON 格式输出
python scripts/last30days.py "ChatGPT替代品" --emit json
```

### 命令行参数

| 参数 | 说明 | 示例 |
| --- | --- | --- |
| `--emit` | 输出模式 | `compact` / `json` / `md` / `context` / `path` |
| `--quick` | 快速搜索 | 更少数据源，更快速度 |
| `--deep` | 深度搜索 | 更多数据源，更全面 |
| `--days N` | 回溯天数 | `--days 7` |
| `--search` | 指定搜索源 | `--search weibo,bilibili,zhihu` |
| `--diagnose` | 诊断配置 | 显示各平台可用状态 |
| `--timeout SECS` | 全局超时秒数 | 覆盖默认全局超时 |
| `--save-dir DIR` | 自动保存原始输出目录 | 将原始输出写入指定目录 |
| `--debug` | 调试模式 | 输出详细日志 |

## 评分系统

每条搜索结果的综合评分（0–100）基于：

| 维度 | 权重 | 说明 |
| --- | --- | --- |
| 相关性 | 45% | 与查询主题的文本匹配度 |
| 时效性 | 25% | 内容发布时间的新鲜程度 |
| 互动度 | 30% | 各平台互动指标（转发/评论/点赞等） |

## 项目架构

```
last30days-skill-cn/
├── SKILL.md              # Agent 技能定义文件
├── README.md
├── requirements.txt
├── scripts/
│   ├── last30days.py     # 主入口 CLI
│   └── lib/
│       ├── crawler_bridge.py  # MediaCrawler 爬虫桥接模块
│       ├── weibo.py          # 微博搜索
│       ├── xiaohongshu.py    # 小红书搜索
│       ├── bilibili.py       # B 站搜索
│       ├── zhihu.py          # 知乎搜索
│       ├── douyin.py         # 抖音搜索
│       ├── wechat.py         # 微信公众号
│       ├── baidu.py          # 百度搜索
│       ├── toutiao.py        # 今日头条
│       ├── schema.py         # 数据结构定义
│       ├── score.py          # 评分系统
│       ├── normalize.py      # 数据标准化
│       ├── dedupe.py         # 去重
│       ├── render.py         # 输出渲染
│       └── ...
├── fixtures/              # 示例数据
├── tests/                 # 测试用例
└── hooks/                 # Agent 钩子
```

## 适用场景

- **竞品调研**：追踪竞品在各平台的最新动态和用户反馈
- **热点追踪**：快速了解某个话题在全网的讨论趋势
- **内容选题**：基于真实数据确定内容创作方向
- **舆情监测**：监控品牌或产品在社交媒体上的口碑

---

## 来源与归档

- 原始素材：[Archive/Jesseovolast30days-skill-cn last30days-cn 是一个 AI Agent 技能（Skill），能够自动搜索中国互联网 8 大主流平台最近 30 天的内容，综合分析后生成有据可查的研究报告。.md](../../../Archive/Jesseovolast30days-skill-cn%20last30days-cn%20%E6%98%AF%E4%B8%80%E4%B8%AA%20AI%20Agent%20%E6%8A%80%E8%83%BD%EF%BC%88Skill%EF%BC%89%EF%BC%8C%E8%83%BD%E5%A4%9F%E8%87%AA%E5%8A%A8%E6%90%9C%E7%B4%A2%E4%B8%AD%E5%9B%BD%E4%BA%92%E8%81%94%E7%BD%91%208%20%E5%A4%A7%E4%B8%BB%E6%B5%81%E5%B9%B3%E5%8F%B0%E6%9C%80%E8%BF%91%2030%20%E5%A4%A9%E7%9A%84%E5%86%85%E5%AE%B9%EF%BC%8C%E7%BB%BC%E5%90%88%E5%88%86%E6%9E%90%E5%90%8E%E7%94%9F%E6%88%90%E6%9C%89%E6%8D%AE%E5%8F%AF%E6%9F%A5%E7%9A%84%E7%A0%94%E7%A9%B6%E6%8A%A5%E5%91%8A%E3%80%82.md)
