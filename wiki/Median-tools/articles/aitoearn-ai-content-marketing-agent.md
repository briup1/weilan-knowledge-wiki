---
title: "AiToEarn：AI 内容营销智能体"
source: "https://github.com/yikart/AiToEarn/"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "AICoding", "type/tool", "AiToEarn", "Content-Marketing", "Agent", "MCP", "Social-Media", "Open-Source"]
status: "archived"
references: "Archive/yikartAiToEarn Let's use AI to Earn!.md"
---

> AiToEarn 通过 AI 自动化，帮助 OPC（一人公司）、创作者、品牌与企业在全球主流平台上构建、分发并变现内容。支持 12+ 平台，覆盖内容创作、发布、互动、变现全链路。

## 核心定位

**Monetize · Publish · Engage · Create —— 一站式平台。**

AiToEarn 围绕内容创作者的完整变现链路，提供四大 Agent 能力：

## 四大核心能力

### 1. Monetize —— 内容赚钱

创作者可在平台出售内容完成商家推广任务，三种结算模式：

| 结算模式 | 全称 | 含义 |
| --- | --- | --- |
| **CPS** | Cost Per Sale | 按成交额结算 |
| **CPE** | Cost Per Engagement | 按互动量结算 |
| **CPM** | Cost Per Mille | 按播放量结算 |

### 2. Publish —— 内容发布 Agent

一键将内容分发到全球 12+ 主流平台：

抖音、快手、B 站、小红书、TikTok、YouTube、Facebook、Instagram、Threads、X（Twitter）、Pinterest、LinkedIn

- **全网分发**：告别逐个平台手动发布
- **日历排期**：统一规划所有平台的内容发布时间

### 3. Engage —— 内容互动 Agent

通过浏览器插件实现自动化互动运营：

- **自动化操作**：自动点赞、收藏、关注，批量高效运营
- **AI 智能回复**：调用大模型为每条评论生成针对性回复
- **评论挖掘**：识别"求链接""怎么购买"等高转化信号
- **品牌监测**：实时追踪品牌讨论，主动参与热点话题

### 4. Create —— 内容创作 Agent

用 Agent 方式重构内容制作流程：

- **视频内容**：自动调用视频生成模型（Grok、Veo、Seedance 等）、视频翻译、剪辑模块
- **图文内容**：调用 Nano Banana 等图片模型自动生成
- **批量生成**：并行生成多条内容，适合矩阵账号运营

## 使用方式（5 种）

| 方式 | 适合谁 | 需要部署 |
| --- | --- | --- |
| **① 打开网站直接用** | 所有用户 | 不需要 |
| **② 在 OpenClaw 中使用** | OpenClaw 用户 | 不需要 |
| **③ 在 Claude / Cursor 等 AI 助手中使用** | AI 工具用户 | 不需要 |
| **④ Docker 一键部署** | 想私有化部署的团队 | 需要服务器 |
| **⑤ 源码开发** | 开发者 | 需要开发环境 |

## MCP 协议支持

AiToEarn 支持所有兼容 MCP 协议的 AI 助手，以下是常见工具配置：

### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "aitoearn": {
      "type": "http",
      "url": "https://aitoearn.ai/api/unified/mcp",
      "headers": {
        "x-api-key": "你的API-Key"
      }
    }
  }
}
```

### Cursor

在 MCP 设置中添加：

```
MCP 地址：https://aitoearn.ai/api/unified/mcp
认证 Header：x-api-key: 你的API-Key
```

### 通用配置

| 配置项 | 值 |
| --- | --- |
| MCP 地址 | `https://aitoearn.ai/api/unified/mcp` |
| 认证 Header | `x-api-key: 你的API-Key` |
| SSE 长连接 | `https://aitoearn.ai/api/unified/sse` |

## Docker 一键部署

```bash
git clone https://github.com/yikart/AiToEarn.git
cd AiToEarn
docker compose up -d
```

启动后打开 [http://localhost:8080](http://localhost:8080) 即可使用。

### 配置 Relay（推荐）

配置 Relay 后可借用官方 aitoearn.ai 的凭据完成各平台 OAuth 授权，**无需自己申请开发者账号**。

在 `docker-compose.yml` 的 `aitoearn-server` 服务中添加：

```yaml
RELAY_SERVER_URL: https://aitoearn.ai/api
RELAY_API_KEY: 你的API-Key
RELAY_CALLBACK_URL: http://127.0.0.1:8080/api/plat/relay-callback
```

## 项目架构

```
AiToEarn/
├── project/
│   ├── aitoearn-backend/       # NestJS 后端
│   │   ├── apps/aitoearn-ai/   # AI 服务
│   │   └── apps/aitoearn-server/ # 主服务
│   └── aitoearn-web/           # 前端（Next.js）
├── AttAiToEarn/                # Electron 桌面客户端
└── ...
```

## 适用人群

- **独立创作者**：一人公司（OPC）的内容营销自动化
- **品牌方**：多平台内容分发与品牌监测
- **MCN 机构**：批量内容创作与矩阵账号运营
- **出海团队**：全球多平台内容本地化与发布

---

## 来源与归档

- 原始素材：[Archive/yikartAiToEarn Let's use AI to Earn!.md](../../../Archive/yikartAiToEarn%20Let%27s%20use%20AI%20to%20Earn!.md)
