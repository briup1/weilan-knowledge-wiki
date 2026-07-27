# 微信文章合集下载器

从微信公众号合集（album）页面批量下载所有文章，保存为 Markdown。

## 用途

这个脚本解决的是知识库摄取流程的**第一步**：把微信里的系列文章批量下载到本地，随后可以交给 `llm-ingest` 等流程进一步处理。

## 依赖

- Python 3.8+
- 无第三方依赖，只用标准库

## 用法

```bash
python3 scripts/ingest/download_wechat_album.py \
    "<微信合集页面URL>" \
    [输出目录]
```

示例：

```bash
python3 scripts/ingest/download_wechat_album.py \
    "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&action=getalbum&album_id=..." \
    ./raw/assets
```

如果省略输出目录，默认保存到 `./wechat_articles`。

## 输出

每个文章会生成一个 `.md` 文件：

```text
<输出目录>/
├── <文章标题>.md
├── <文章标题>.md
└── ...
```

每个文件头部包含：

```markdown
# 文章标题

> 原文链接：http://mp.weixin.qq.com/s?...

正文...
```

## 工作原理

1. 用 Android 微信 User-Agent 访问合集页面，绕过单篇文章的“环境异常”验证。
2. 从合集 HTML 中的 `cgiData` 提取前 10 篇文章。
3. 如果合集有分页，调用微信 JSON 接口 `f=json` 加载后续文章。
4. 用 HTML 解析器提取每篇文章的 `#js_content`，转换为 Markdown。

## 限制

- 微信反爬策略可能变化，若大量下载失败，可尝试加 Cookie 或使用代理。
- 图片只保留链接，不会下载图片文件本身。
- 合集 URL 必须是 `mp.weixin.qq.com/mp/appmsgalbum` 页面，不是单篇文章链接。

## 与知识库工作流的衔接

推荐流程：

```text
发现微信合集 → 运行本脚本下载到 raw/assets/ → 用 llm-ingest 技能摄取到 wiki/
```
