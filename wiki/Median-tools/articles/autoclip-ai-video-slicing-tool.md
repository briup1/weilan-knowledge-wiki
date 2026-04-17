---
title: "AutoClip：AI 自动视频切片工具"
sources:
  - "https://mp.weixin.qq.com/s/JHqzSfkaZjM802DArrz0LA"
  - "https://github.com/zhouxiaoka/autoclip"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "type/tool", "type/hands-on", "AICoding", "AutoClip", "Video-Editing", "AI-Tool", "Fastapi", "Open-Source"]
status: "archived"
references:
  - "Archive/B站油管视频自动切片：内容创作者的时间救星，还是又一个「效率焦虑」产物？.md"
  - "Archive/zhouxiaokaautoclip AutoClip  AI-powered video clipping and highlight generation.md"
merged_from:
  - "B站油管视频自动切片：内容创作者的时间救星，还是又一个「效率焦虑」产物？.md"
  - "zhouxiaokaautoclip AutoClip  AI-powered video clipping and highlight generation.md"
---

> AutoClip 是一个开源的 AI 自动视频切片工具，输入 B 站或 YouTube 链接即可自动识别精彩片段并生成可发布的短片。

## 核心功能

AutoClip 将视频切片流程简化为三步：

1. **粘贴链接**：支持 B 站、YouTube 链接，或直接上传本地文件。
2. **AI 自动分析**：基于通义千问理解视频内容，提取大纲、识别话题时间点，并为每个片段打分。
3. **生成切片**：自动切出精彩片段，支持手动调整后导出或直接上传 B 站。

整个流程采用**异步处理**——提交任务后可关闭页面，处理完成后会收到通知。

## 特色能力

- **智能精彩评分**：AI 对每个片段评分，高分片段优先推荐，减少人工逐帧筛选的工作量。
- **自动生成标题**：为每个切片生成吸引人的标题，降低短视频创作中的标题构思成本。
- **合集打包**：支持将多个相关片段打包成合集，方便系列内容制作。
- **实时进度推送**：通过 WebSocket 推送处理进度，无需盯着页面等待。

## 适用人群

**适合**：

- 知识博主（访谈、课程、演讲视频拆成短片发多平台）
- UP 主（长视频拆成系列短片扩大传播）
- 出海团队（YouTube 视频切片发 TikTok / YouTube Shorts）
- MCN 机构（批量处理旗下博主素材）

**不适合**：

- 纯拍摄型短视频创作者（没有长视频素材）
- 追求极致画面质量的用户（自动剪辑精度仍不如人工）

## 工具定位与竞品对比

| 类型 | 代表 | 优点 | 缺点 |
| --- | --- | --- | --- |
| 在线 AI 剪辑平台 | 各类 SaaS | 上手快 | 收费贵、隐私顾虑、大小限制、导出水印 |
| 专业软件+插件 | Premiere + 插件 | 可控性强 | 手动操作、学习成本高、硬件要求高 |
| **AutoClip** | 开源本地工具 | 本地部署、数据可控、自动化程度高、免费 | 需要一定技术能力部署 |

AutoClip 的价值不在于"替代人工"，而在于**将机械性筛选工作自动化**，让创作者能把时间投入到创意和判断上。

## 系统架构

```
用户界面 --> FastAPI 后端 --> Celery 任务队列 --> AI 处理引擎
                  |                |                    |
               Redis 缓存     SQLite 数据库      视频处理 / 字幕分析 / 内容理解
                  |
           YouTube API / B站 API
```

### 后端技术栈

- **FastAPI**：现代化 Python Web 框架，自动 API 文档生成
- **Celery**：分布式任务队列，支持异步处理
- **Redis**：消息代理和缓存，任务状态管理
- **SQLite**：轻量级数据库，支持升级到 PostgreSQL
- **yt-dlp**：YouTube 视频下载，支持多种格式
- **通义千问 / DashScope**：AI 内容分析与理解
- **WebSocket**：实时通信，进度推送
- **Pydantic**：数据验证和序列化

### 前端技术栈

- **React 18 + TypeScript**：用户界面框架
- **Ant Design**：企业级 UI 组件库
- **Vite**：快速构建工具
- **Zustand**：轻量级状态管理
- **React Router**：路由管理

## 部署指南

### Docker 部署（推荐）

要求：Docker 20.10+、Docker Compose 2.0+、内存最少 4GB（推荐 8GB+）

```bash
git clone https://github.com/zhouxiaoka/autoclip.git
cd autoclip
./docker-start.sh        # 生产环境
./docker-start.sh dev    # 开发环境
```

### 本地部署

要求：Python 3.8+、Node.js 16+、Redis 6.0+、FFmpeg

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
cp env.example .env
# 编辑 .env 填入 API 密钥
```

### 环境变量配置

```bash
# 数据库
DATABASE_URL=sqlite:///./data/autoclip.db

# Redis
REDIS_URL=redis://localhost:6379/0

# AI API
API_DASHSCOPE_API_KEY=your_dashscope_api_key
API_MODEL_NAME=qwen-plus

# 文件存储
UPLOAD_DIR=./data/uploads
PROJECT_DIR=./data/projects
```

## 主要 API 端点

启动后访问 `http://localhost:8000/docs` 查看 Swagger UI。

| 端点 | 方法 | 描述 |
| --- | --- | --- |
| `/api/v1/projects` | GET/POST | 项目列表 / 创建项目 |
| `/api/v1/projects/{id}` | GET | 项目详情 |
| `/api/v1/youtube/parse` | POST | 解析 YouTube 视频信息 |
| `/api/v1/youtube/download` | POST | 下载 YouTube 视频 |
| `/api/v1/bilibili/download` | POST | 下载 B 站视频 |
| `/api/v1/projects/{id}/process` | POST | 开始处理项目 |
| `/api/v1/projects/{id}/status` | GET | 获取处理状态 |

## AI 处理流水线

系统按以下步骤自动执行智能处理：

1. **素材准备**：下载视频和字幕文件
2. **内容分析**：AI 提取视频大纲和关键信息
3. **时间线提取**：识别话题时间区间
4. **精彩评分**：对每个片段进行 AI 评分
5. **标题生成**：为精彩片段生成吸引人标题
6. **合集推荐**：AI 推荐视频合集
7. **视频生成**：生成切片视频和合集视频

## 性能优化建议

- **数据库**：生产环境使用 PostgreSQL 替代 SQLite，配置连接池和查询缓存
- **Redis**：配置内存限制、启用持久化、设置过期策略
- **Celery**：调整并发数、配置任务路由、启用结果后端

## 开源地址

- GitHub: [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip)

---

## 来源与归档

- 原始素材（功能介绍）：[Archive/B站油管视频自动切片：内容创作者的时间救星，还是又一个「效率焦虑」产物？.md](../../../Archive/B站油管视频自动切片：内容创作者的时间救星，还是又一个「效率焦虑」产物？.md)
- 原始素材（GitHub README 技术详情）：[Archive/zhouxiaokaautoclip AutoClip  AI-powered video clipping and highlight generation.md](../../../Archive/zhouxiaokaautoclip%20AutoClip%20%20AI-powered%20video%20clipping%20and%20highlight%20generation.md)
