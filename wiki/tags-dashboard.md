---
title: "标签总览"
created: 2026-04-17
tags: ["Dashboard", "Tags", "Dataview"]
---

# 标签总览

本页使用 Dataview 插件动态聚合全库文章，按标准类型标签分组展示。

---

## 标准类型标签说明

| 嵌套标签             | 类型名称     | 说明                      |
| ---------------- | -------- | ----------------------- |
| `#type/hands-on` | 项目实战型    | 包含可运行代码、完整项目结构、部署配置     |
| `#type/tool`     | 工具/项目推荐型 | 介绍 GitHub 项目、开源工具、第三方服务 |
| `#type/concept`  | 原理解析型    | 深入讲解架构、机制、源码、设计思想       |
| `#type/tips`     | 技巧汇总型    | 收集快捷操作、最佳实践、效率技巧        |
| `#type/tutorial` | 教程/保姆级攻略 | Step-by-step 教学，适合从零跟做  |
| `#type/news`     | 资讯/动态型   | 纯新闻、产品发布、行业动态           |

---

## 项目实战型 (#type/hands-on)

```dataview
TABLE title, category, created
FROM "wiki"
WHERE contains(tags, "type/hands-on")
SORT created DESC
```

---

## 工具/项目推荐型 (#type/tool)

```dataview
TABLE title, category, created
FROM "wiki"
WHERE contains(tags, "type/tool")
SORT created DESC
```

---

## 原理解析型 (#type/concept)

```dataview
TABLE title, category, created
FROM "wiki"
WHERE contains(tags, "type/concept")
SORT created DESC
```

---

## 技巧汇总型 (#type/tips)

```dataview
TABLE title, category, created
FROM "wiki"
WHERE contains(tags, "type/tips")
SORT created DESC
```

---

## 教程/保姆级攻略 (#type/tutorial)

```dataview
TABLE title, category, created
FROM "wiki"
WHERE contains(tags, "type/tutorial")
SORT created DESC
```

---

## 资讯/动态型 (#type/news)

```dataview
TABLE title, category, created
FROM "wiki"
WHERE contains(tags, "type/news")
SORT created DESC
```

---

## 未打类型标签检查

以下文章尚未标注任何 `type/xxx` 标签，请及时补打：

```dataview
TABLE title, category, tags
FROM "wiki"
WHERE file.path != "wiki/tags-dashboard.md"
  AND !contains(tags, "type/")
```

---

## 全库标签分布

```dataview
TABLE length(rows) as count
FROM "wiki"
WHERE file.path != "wiki/tags-dashboard.md"
FLATTEN tags as tag
GROUP BY tag
SORT length(rows) DESC
LIMIT 10
```
