---
type: source
created: 2026-04-20
updated: 2026-04-20
raw: raw/archive/Claudian + baoyu-skills + ModelScope：打造免费AI绘图工作流.md
tags: [claudian, baoyu-skills, modelscope, ai-drawing, qwen-image, obsidian]
---

# Claudian + baoyu-skills + ModelScope：打造免费AI绘图工作流

## 摘要

本文介绍了一个完全免费的 AI 绘图解决方案，将 Claudian（Obsidian vault 中的 AI 助手）、baoyu-skills（AI 技能包）和 ModelScope（阿里云 AI 模型平台）三者结合，使用阿里云的 Qwen-Image-2512 模型进行高质量 AI 绘图。Claudian 可直接读写 vault 中的文件，baoyu-skills 提供图像生成、封面生成、小红书信息图等功能，ModelScope 提供免费 API 调用额度。文章详细讨论了 Claudian 的沙箱限制（只能访问 vault 内文件，无法访问 `~/.baoyu-skills/` 等外部目录），并给出了四种解决方案：项目级安装（推荐）、Git Submodule 管理共享技能、符号链接（不支持）、修改配置（不推荐）。推荐配置方案是在 vault 中使用项目级 baoyu-skills，通过 `.baoyu-skills/.env` 配置 ModelScope API Key，通过 `EXTEND.md` 配置默认模型为 Qwen/Qwen-Image-2512。

## 核心要点

- **三件套组合**：Claudian（Obsidian AI 助手）+ baoyu-skills（图像生成技能包）+ ModelScope（免费 API）= 零成本高质量 AI 绘图工作流。
- **Qwen-Image-2512**：25.1B 参数文生图模型，生成时间约 205 秒，文件大小约 1.3 MB，质量高于标准版（20B）。
- **Claudian 沙箱限制**：只能访问 vault 内文件，无法访问 `~/.baoyu-skills/` 或系统级目录，这是安全特性。
- **推荐方案**：在 vault 中使用项目级 baoyu-skills（`.baoyu-skills/`），配置集中管理且符合安全机制。
- **Git Submodule 方案**：适合多项目协作，统一管理技能版本，方便更新同步，但配置稍复杂。
- **baoyu-skills 技能列表**：baoyu-image-gen（AI 图像生成）、baoyu-cover-image（文章封面）、baoyu-xhs-images（小红书风格信息图）、baoyu-infographic（专业信息图）。
- **配置模板**：`.baoyu-skills/.env` 存放 API Key，`.baoyu-skills/baoyu-image-gen/EXTEND.md` 配置默认 provider 和模型。
- **实践经验**：文章封面生成约 3-4 分钟，文件约 1.5 MB；小红书信息图风格统一、自动处理文字排版。

## 原始文件

- [原始文件](../../raw/archive/Claudian%20+%20baoyu-skills%20+%20ModelScope：打造免费AI绘图工作流.md)
