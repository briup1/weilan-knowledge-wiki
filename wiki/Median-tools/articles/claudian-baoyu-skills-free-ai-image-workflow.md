---
title: "Claudian + baoyu-skills + ModelScope：打造免费 AI 绘图工作流"
source: "https://mp.weixin.qq.com/s/FvF4OOhm1ryWbPHj3jf9JQ"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "AICoding", "ClaudeCode", "type/tutorial", "type/hands-on", "Claudian", "baoyu-skills", "ModelScope", "AI-绘图", "Qwen-Image"]
status: "archived"
references: "Archive/Claudian + baoyu-skills + ModelScope：打造免费AI绘图工作流.md"
---

> 将 Claudian（Obsidian AI 助手）、baoyu-skills（图像生成技能库）与 ModelScope（阿里云免费模型平台）三者结合，实现零成本高质量 AI 绘图。

## 组合定位

| 组件 | 角色 | 核心价值 |
| --- | --- | --- |
| **Claudian** | Obsidian vault 中的 AI 助手 | 直接读写 vault 内文件，无需切换工具 |
| **baoyu-skills** | 可扩展技能包 | 图像生成、封面制作、小红书信息图等 |
| **ModelScope** | 阿里云模型平台 | 免费 API 调用额度，支持 Qwen-Image-2512 |
| **Qwen-Image-2512** | 251 亿参数文生图模型 | 细节丰富、质量高 |

## Claudian 简介

Claudian 是运行在 Obsidian vault 中的 AI 助手，核心特性：

- **直接文件访问**：读写 vault 中的 Markdown、图片等文件
- **技能系统**：通过 baoyu-skills 扩展功能
- **沙箱安全**：被限制在 vault 目录中执行
- **命令执行**：可在 vault 中运行 bash 命令

**关键限制**：Claudian 只能访问 vault 内的文件，无法访问系统级的 `~/.baoyu-skills/` 目录。

## baoyu-skills 核心技能

| 技能名 | 功能 |
| --- | --- |
| `baoyu-image-gen` | AI 图像生成（支持 OpenAI、Google、ModelScope） |
| `baoyu-cover-image` | 文章封面生成 |
| `baoyu-xhs-images` | 小红书风格信息图生成 |
| `baoyu-infographic` | 专业信息图生成 |

### 安装方式

**项目级安装（推荐，适配 Claudian 沙箱）**：

```bash
# 在 vault 根目录
cp -r ~/.baoyu-skills ./vault/.baoyu-skills
```

**多项目同步（Git Submodule）**：

```bash
git submodule add https://github.com/your-username/baoyu-skills-shared.git .baoyu-skills
```

## ModelScope 配置

### 1. 获取 API Key

访问 [ModelScope 官网](https://www.modelscope.cn/) 注册账号并获取 API Key。

### 2. vault 内配置

创建 `.baoyu-skills/.env`：

```bash
MODELSCOPE_API_KEY=ms-your-api-key-here
```

创建 `.baoyu-skills/baoyu-image-gen/EXTEND.md`：

```yaml
---
version: 1
default_provider: modelscope
default_quality: 2k
default_model:
  modelscope: "Qwen/Qwen-Image-2512"
---
```

## Qwen-Image-2512 模型对比

| 特性 | Qwen/Qwen-Image | Qwen/Qwen-Image-2512 |
| --- | --- | --- |
| 参数量 | 20B | 25.1B |
| 生成速度 | ~135 秒 | ~205 秒 |
| 文件大小 | ~650 KB | ~1.3 MB |
| 质量 | 标准 | **更高** |
| 适用场景 | 快速预览 | 高质量输出 |

## 使用示例

### 基础图像生成

```bash
cd .baoyu-skills/baoyu-image-gen
npx -y bun scripts/main.ts \
  --prompt "一只可爱的橘猫坐在窗台上" \
  --image cat.png \
  --ar 1:1
```

### 封面生成

```bash
npx -y bun scripts/main.ts \
  --prompt "科技杂志封面，深蓝色渐变背景，发光的标题文字" \
  --image cover.png \
  --ar 16:9
```

### Claudian 直接调用

在 Claudian 中对话即可：

```
请使用 baoyu-image-gen 为我生成一张图片，
提示词是"日落时分的海滩"，保存为 beach.png
```

```
为这篇文章 [[笔记名称]] 生成小红书图片
```

```
使用 baoyu-cover-image 生成封面，
类型是 typography，深色主题
```

## 关于沙箱限制的最佳实践

Claudian 的沙箱限制是**安全特性**，不应绕过。推荐方案：

**方案 1（简单项目）**：直接在 vault 中使用项目级 baoyu-skills

```
vault/
├── .baoyu-skills/
│   ├── .env                    # API Key
│   ├── baoyu-image-gen/
│   │   └── EXTEND.md           # 模型配置
│   ├── baoyu-cover-image/
│   └── baoyu-xhs-images/
├── notes/
└── attachments/
```

**方案 2（多项目协作）**：使用 Git Submodule 统一管理技能版本。

## 常见问题

**Q：ModelScope API 为什么没有输出？**

A：ModelScope API 是异步的，生成需要 2–4 分钟。检查命令是否正确，并查看输出文件。

**Q：如何确认使用了 2512 模型？**

A：检查生成文件大小：
- 标准模型：~650 KB
- 2512 模型：~1.3 MB

**Q：可以同时使用多个模型吗？**

A：可以，通过 `--model` 参数指定：

```bash
# 标准模型（快速）
--model Qwen/Qwen-Image

# 2512 模型（高质量）
--model Qwen/Qwen-Image-2512
```

## 总结

Claudian + baoyu-skills + ModelScope 是一个**完全免费的本地 AI 绘图方案**：

1. **Claudian** 提供 AI 助手和 vault 文件操作能力
2. **baoyu-skills** 提供丰富的图像生成技能
3. **ModelScope** 提供免费的 API 调用额度
4. **Qwen-Image-2512** 提供高质量输出

---

## 来源与归档

- 原始素材：[Archive/Claudian + baoyu-skills + ModelScope：打造免费AI绘图工作流.md](../../../Archive/Claudian%20+%20baoyu-skills%20+%20ModelScope%EF%BC%9A%E6%89%93%E9%80%A0%E5%85%8D%E8%B4%B9AI%E7%BB%98%E5%9B%BE%E5%B7%A5%E6%B5%81.md)
