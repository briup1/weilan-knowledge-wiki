---
type: source
created: 2026-09-23
updated: 2026-09-23
domains: [software-development]
raw: raw/archive/enterprise-agent-platform/docs/part10-security-org/ch/ch50.md
tags: [enterprise-agent-platform, security, prompt-injection, red-team]
---

# 第50章 安全与攻防

## 摘要

本章认为企业 Agent 安全不能停在“让模型更听话”。自然语言输入、外部上下文、工具调用、业务输出和审计响应都在安全边界里。模型不能天然区分指令和数据。工具越权比说错话更严重，因为模型输出会变成真实动作。

## 核心要点

- 攻击面分五层：用户输入、检索上下文、工具调用、业务输出、运维与审计。只在入口过滤一次不够。
- 直接注入在用户输入里。间接注入在网页、PDF、邮件、工单、代码注释或知识库片段里。执行攻击的人可能不是当前用户。
- 工具越权有三种：代做用户无权的动作、把小范围权限放大、把只读请求做成写入或导出。万能的“执行 SQL”或“调用 CRM”入口让策略引擎无法判断风险。
- 红队要有威胁模型、攻击样例、评测环境、评分标准、回归和责任人。第一批样例覆盖直接注入、间接注入、工具越权、数据泄漏、不安全输出和业务逻辑绕过。PyRIT、Garak、OWASP LLM Top 10 是方法入口，不是已完成的企业评测。
- 上线基线要能执行：会话绑定身份和数据域，上下文分层，工具必须过策略引擎，敏感字段在进模型、日志、前端和导出前分别检查。事故时要能冻结会话、撤销令牌、下线工具、回放 Trace。

## 局限

本章是威胁模型和门禁清单，不是一次红队实测报告。没有给出漏过率或工具版本。安全例外和样本库的运营细节需要各企业自己补责任人。

## 关联

- [[agent-security]]
- [[agent-guardrails]]
- [[enterprise-agent-tool-registry]]

## 原始文件

- [原始文件](../../raw/archive/enterprise-agent-platform/docs/part10-security-org/ch/ch50.md)
