---
title: "MoneyPrinterTurbo：AI 一键生成高清短视频"
source: "https://github.com/harry0703/MoneyPrinterTurbo"
created: 2026-04-17
category: "Median-tools"
tags: ["Median-tools", "type/tool", "type/hands-on", "AI视频", "短视频生成", "自动化内容生产"]
status: "archived"
references: "Archive/harry0703MoneyPrinterTurbo 利用AI大模型，一键生成高清短视频 Generate short videos with one click using AI LLM.md"
---

## 项目简介

[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) 是一个开源的 AI 短视频自动生成工具。只需提供一个**主题**或**关键词**，它就能自动完成文案生成、素材搜索、语音合成、字幕渲染与背景音乐合成，最终输出一条高清短视频。

项目采用完整的 **MVC 架构**，同时提供 **Web 界面**（Streamlit）和 **REST API**，既适合普通用户快速体验，也方便开发者集成到现有工作流中。

## 核心功能

- **AI 自动文案**：支持自定义文案或由大模型自动生成
- **多尺寸高清输出**：支持竖屏 9:16 与横屏 16:9 等常见视频比例
- **批量生成**：一次可生成多个视频版本，方便挑选最优结果
- **多语言支持**：中文与英文文案均支持
- **语音合成（TTS）**：内置多种语音，支持实时试听；2024-04 新增 9 种更真实的 Azure 语音
- **自动字幕**：支持 `edge`（速度快）与 `whisper`（质量高）两种字幕引擎，可自定义字体、位置、颜色、大小及描边
- **背景音乐**：可随机选用或指定本地音乐文件，支持音量调节
- **素材来源**：默认使用高清无版权在线素材，也支持上传本地素材替换

## 模型接入支持

项目几乎覆盖了主流国内外大模型 API：

- **国内可直接访问**：DeepSeek、Moonshot（推荐中国用户使用）、通义千问、文心一言、MiniMax
- **国际平台**：OpenAI、Azure、Google Gemini、Ollama
- **聚合/免费通道**：gpt4free、one-api、Pollinations、ModelScope

## 配置要求

| 项目 | 最低配置 | 推荐配置 | 理想配置 |
|------|----------|----------|----------|
| CPU  | 4 核     | 6–8 核   | 8 核及以上 |
| RAM  | 4 GB     | 8 GB     | 16 GB 及以上 |
| GPU  | 非必须   | 4 GB 显存 | 8 GB 显存及以上 |

> 若主要依赖云端 LLM / TTS 与在线素材源，CPU 与内存比 GPU 更重要；若启用 `faster-whisper` 本地转录或批量生成，GPU 可显著提升速度。

## 部署方式

### 1. Windows 一键启动包（最快体验）

- 百度网盘 / Google Drive 下载 `v1.2.6` 启动包
- 解压后先执行 `update.bat` 更新到最新代码，再运行 `start.bat`
- **注意**：解压路径不能包含中文、空格或特殊字符

### 2. Docker 部署

```bash
cd MoneyPrinterTurbo
docker-compose up
```

- Web 界面：[http://0.0.0.0:8501](http://0.0.0.0:8501)
- API 文档：[http://0.0.0.0:8080/docs](http://0.0.0.0:8080/docs)

### 3. 手动部署（推荐 MacOS / Linux）

使用 `uv` 管理环境（默认 Python 3.11）：

```bash
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
uv python install 3.11
uv sync --frozen
```

额外依赖 **ImageMagick**：

- Windows：下载静态库版本安装，并在 `config.toml` 中配置 `imagemagick_path`
- MacOS：`brew install imagemagick`
- Ubuntu：`sudo apt-get install imagemagick`
- CentOS：`sudo yum install ImageMagick`

启动 Web 界面：

```bash
uv run streamlit run ./webui/Main.py --browser.gatherUsageStats=False
```

启动 API 服务：

```bash
uv run python main.py
```

## 语音与字幕

### 语音列表

全部支持的声音可在项目 [voice-list.txt](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/docs/voice-list.txt) 中查看。

### 字幕引擎对比

| 引擎 | 速度 | 质量 | 配置要求 |
|------|------|------|----------|
| edge | 快 | 可能不稳定 | 无特殊要求 |
| whisper | 慢 | 更可靠 | 需下载约 3GB 模型文件，建议有 GPU |

> whisper 模型默认从 HuggingFace 下载，国内用户可通过网盘手动下载后放入 `./models/whisper-large-v3` 目录。

## 常见问题速查

1. **找不到 ffmpeg**：若自动下载失败，可手动从 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载并配置 `ffmpeg_path`
2. **ImageMagick 安全策略报错**：修改 `policy.xml` 中 `pattern="@"` 的 `rights="none"` 为 `rights="read|write"`
3. **Too many open files**：调高系统文件打开数限制，如 `ulimit -n 10240`
4. **Whisper 模型下载失败**：使用网盘离线下载后放置到 `models/whisper-large-v3`

## 相关阅读

- [OpenMontage：开源 Agentic 视频生产系统](openmontage-agentic-video-production-system.md) — 更偏向大规模、多 Agent 协作的视频工业化生产流水线

---

## 来源与归档

- 原始素材：[Archive/harry0703MoneyPrinterTurbo 利用AI大模型，一键生成高清短视频 Generate short videos with one click using AI LLM.md](../../../Archive/harry0703MoneyPrinterTurbo%20利用AI大模型，一键生成高清短视频%20Generate%20short%20videos%20with%20one%20click%20using%20AI%20LLM.md)
