---
title: "Hyper-Extract：一键将文档转为知识图谱"
source: "https://mp.weixin.qq.com/s/G6HIwEe09jelf0Mwo9WABQ"
created: 2026-04-16
category: "Rag"
tags: ["Rag", "type/tool", "type/concept", "AICoding"]
status: "archived"
references: "Archive/Hyper-Extract：一条命令把杂乱文档变成知识图谱.md"
---

> 一句话总结：Hyper-Extract 是一个基于大语言模型的智能知识提取工具，只需一行命令就能把非结构化文档转换成知识图谱、时序图、超图等 8 种结构化格式，内置 80+ 领域模板，支持中英文。

## 它解决什么问题？

传统文档处理方式的痛点：

- **阅读效率低** —— 长文档需要逐页阅读，难以快速定位关键信息
- **信息孤岛** —— 不同文档之间的关联难以发现
- **时间成本高** —— 手工整理笔记、制作脑图耗时耗力
- **难以持续更新** —— 新知识无法方便地整合到已有体系中

Hyper-Extract 的核心思路是：**让 AI 帮你"阅读"和"理解"**，直接输出结构化的知识，而不是原始文本。

## 8 种知识提取格式

**基础类型：**

- **AutoModel** —— 结构化数据模型（类似 JSON）
- **AutoList** —— 有序列表
- **AutoSet** —— 无序唯一集合

**进阶类型：**

- **AutoGraph** —— 知识图谱（实体 + 关系）
- **AutoHypergraph** —— 超图（支持多实体复杂关系）
- **AutoTemporalGraph** —— 时序图（带时间轴的知识演变）
- **AutoSpatialGraph** —— 空间图（带地理位置的知识）
- **AutoSpatioTemporalGraph** —— 时空图（时间 + 空间双重维度）

例如，处理一篇关于特斯拉的人物传记时，AutoGraph 能自动提取出"特斯拉-爱迪生-竞争关系"、"特斯拉-西屋电气-合作关系"等实体关系对，并以可视化图谱呈现。

## 快速上手

安装与使用：

```bash
# 安装 CLI 工具
uv tool install hyperextract

# 配置 API Key
he config init -k YOUR_OPENAI_API_KEY
```

常用命令：

```bash
# 从文档提取知识图谱
he parse tesla.md -t general/biography_graph -o ./output/

# 查询提取的知识
he search ./output/ "特斯拉的主要成就是什么？"

# 可视化知识图谱
he show ./output/

# 追加新文档，让知识图谱"生长"
he feed ./output/ new_article.md
```

## 与其他工具对比

| 对比项 | Hyper-Extract 的优势 |
|--------|----------------------|
| vs GraphRAG | GraphRAG 只能生成知识图谱，Hyper-Extract 还支持时序图、空间图、超图等 8 种格式 |
| vs LightRAG | LightRAG 不支持时序和地理信息，Hyper-Extract 原生支持时空维度 |
| vs 传统 NLP 工具 | 传统工具需要编写复杂的提取规则，Hyper-Extract 用 YAML 模板零代码定义 |
| 独特优势 | 内置 80+ 领域模板（金融、法律、医学、中医、工业等），开箱即用 |

## 80+ 领域模板

Hyper-Extract 提供了 80 多个预设模板，覆盖 6 大领域：

- **金融** —— 财报分析、投资组合、风险评估
- **法律** —— 合同条款、案例关系、法条引用
- **医学** —— 病历结构、药品信息、诊疗流程
- **中医** —— 方剂组成、经络穴位、辨证施治
- **工业** —— 设备参数、工艺流程、供应链关系
- **通用** —— 人物传记、事件时间线、概念图谱

## 背后的技术

Hyper-Extract 集成了 10 多种前沿的知识提取算法：

- **KG-Gen** —— 知识图谱生成
- **iText2KG** —— 迭代式知识图谱构建
- **GraphRAG** —— 基于图谱的检索增强生成
- **LightRAG** —— 轻量级图谱 RAG
- **Hyper-RAG** —— 超图检索增强
- **Cog-RAG** —— 认知 RAG

工具会自动选择最合适的方法，用户无需理解底层技术细节。

## 项目资源

- **GitHub：** [github.com/yifanfeng97/Hyper-Extract](https://github.com/yifanfeng97/Hyper-Extract)
- **文档：** [yifanfeng97.github.io/Hyper-Extract](https://yifanfeng97.github.io/Hyper-Extract)

---

## 来源与归档

- 原始素材：[Archive/Hyper-Extract：一条命令把杂乱文档变成知识图谱.md](../../../Archive/Hyper-Extract：一条命令把杂乱文档变成知识图谱.md)
