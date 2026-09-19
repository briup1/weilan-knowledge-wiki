---
type: domain
created: 2026-09-17
updated: 2026-09-17
domains: [shared]
tags: [navigation]
title: "共享知识与方法"
scope: knowledge
status: reference
projects: []
products: []
topics: []
source: []
related: []
---

# 共享知识与方法

范围：不依赖某个行业的知识管理、研究、检索方法及可复用工具。不是所有 AI 技术的集合，也不是无法分类资料的收容箱。

## 阅读路径

- 组织知识：[[wiki/concepts/agent-wiki|agent-wiki]] → [[wiki/entities/obsidian|obsidian]] → [[wiki/synthesis/knowledge-base-audit-and-flywheel|knowledge-base-audit-and-flywheel]]。
- 获取与编译资料：[[wiki/concepts/wechat-article-ingestion|wechat-article-ingestion]] → [[wiki/sources/obsidian-knowledge-base|Obsidian 知识库来源]]。
- 检索与关联：[[wiki/concepts/knowledge-graph|knowledge-graph]] → [[wiki/concepts/rag|rag]] → [[wiki/synthesis/rag-knowledge-retrieval-landscape|rag-knowledge-retrieval-landscape]]。
- 区分机器记忆与个人知识：[[wiki/synthesis/ai-memory-vs-human-km|ai-memory-vs-human-km]]。

以上旧页面有历史时效边界，技术能力或推荐在实际使用前按需核验。

## 使用方式

```bash
# 只查共享知识
python3 scripts/knowledge/kb.py search --domain shared --query 知识

# 为自媒体问题显式补充共享知识
python3 scripts/knowledge/kb.py search --domain ai-media --include-shared --query 知识
```

选择业务上下文：[[domains/software-development|软件开发与 Agent 工程]] · [[domains/ai-media|AI + 自媒体]]。全量目录见 [[index]]。
