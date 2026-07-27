#!/usr/bin/env python3
"""
download_wechat_album.py

从微信公众号文章合集（album）页面下载所有文章，保存为 Markdown 文件。

用法：
    python3 download_wechat_album.py <album_url> [output_dir]

示例：
    python3 download_wechat_album.py \
        "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&action=getalbum&album_id=..." \
        ./my_articles

说明：
- 需要传入完整的合集页面 URL（在微信里点击“合集”后复制链接即可）。
- 使用 Android 微信 UA 访问，通常可绕过单篇文章的“环境异常”验证页。
- 文章正文会按主题提取并保存为 .md，图片保留为 Markdown 图片链接。
"""

import json
import os
import re
import sys
import time
import html
import urllib.request
import urllib.parse
from html.parser import HTMLParser

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36 "
    "MicroMessenger/8.0.0"
)


class HTMLToMarkdownParser(HTMLParser):
    """极简 HTML -> Markdown 转换器，只处理公众号正文常见标签。"""

    def __init__(self):
        super().__init__()
        self.result = []
        self.stack = []
        self.skip_depth = 0
        self.current_link = None
        self.link_text = []

    BLOCK_TAGS = {
        "p", "div", "section", "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "blockquote", "pre", "figure", "figcaption",
        "br", "hr", "table", "tr", "td", "th", "thead", "tbody",
    }

    def _ensure_block_space(self):
        if self.result and not self.result[-1].endswith("\n"):
            self.result.append("\n")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.skip_depth > 0:
            self.skip_depth += 1
            return
        if tag in {"script", "style", "svg", "canvas", "noscript", "iframe"}:
            self.skip_depth = 1
            return

        self.stack.append(tag)

        if tag == "a" and attrs.get("href"):
            self.current_link = attrs["href"]
            self.link_text = []
            return

        if tag == "img":
            src = attrs.get("data-src") or attrs.get("src", "")
            alt = attrs.get("alt", "")
            if src:
                self._ensure_block_space()
                self.result.append(f"![{alt}]({src})")
            return

        if tag == "br":
            self.result.append("\n")
            return

        if tag in self.BLOCK_TAGS:
            self._ensure_block_space()

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.result.append("#" * int(tag[1]) + " ")
        elif tag == "li":
            parent = self.stack[-2] if len(self.stack) >= 2 else "ul"
            self.result.append("1. " if parent == "ol" else "- ")
        elif tag == "pre":
            self.result.append("```\n")
        elif tag == "code":
            if len(self.stack) < 2 or self.stack[-2] != "pre":
                self.result.append("`")
        elif tag == "blockquote":
            self.result.append("> ")

    def handle_endtag(self, tag):
        if self.skip_depth > 0:
            self.skip_depth -= 1
            return
        if not self.stack:
            return
        try:
            idx = len(self.stack) - 1 - self.stack[::-1].index(tag)
            self.stack = self.stack[:idx]
        except ValueError:
            return

        if tag == "a" and self.current_link:
            link_text = "".join(self.link_text).strip() or self.current_link
            self.result.append(f"[{link_text}]({self.current_link})")
            self.current_link = None
            self.link_text = []
            return

        if tag in self.BLOCK_TAGS:
            self.result.append("\n")

        if tag == "pre":
            self.result.append("```\n")
        elif tag == "code":
            if not self.stack or self.stack[-1] != "pre":
                self.result.append("`")

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        if self.current_link is not None:
            self.link_text.append(data)
        else:
            self.result.append(data)

    def get_markdown(self):
        text = "".join(self.result)
        text = html.unescape(text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_album_info(album_html):
    """从合集 HTML 中提取 __biz、album_id 和文章列表。"""
    # __biz
    biz = None
    m = re.search(r'__biz=([^&"\']+)', album_html)
    if m:
        biz = urllib.parse.unquote(m.group(1))

    # album_id
    album_id = None
    m = re.search(r'album_id=([^&"\']+)', album_html)
    if m:
        album_id = m.group(1)
    else:
        m = re.search(r'albumId:\s*["\']([^"\']+)["\']', album_html)
        if m:
            album_id = m.group(1)

    # article list from cgiData
    articles = []
    # Try to parse the JSON-like cgiData articleList
    m = re.search(r'articleList:\s*\[(.*?)\],\s*\n\s*continue_flag', album_html, re.DOTALL)
    if m:
        try:
            # Convert JS object to JSON (remove trailing commas, single quotes, etc.)
            json_str = "[" + m.group(1) + "]"
            # Quick-and-dirty fix for JS literals: 'a' || -1
            json_str = re.sub(r"'\s*\|\|\s*[^,\}\]]+", "''", json_str)
            json_str = re.sub(r"'\s*\*\s*\d+", "0", json_str)
            data = json.loads(json_str)
            for item in data:
                if "url" in item and "title" in item:
                    articles.append({
                        "title": html.unescape(item["title"]).replace("\xa0", " "),
                        "url": html.unescape(item["url"]).replace("&amp;", "&"),
                        "msgid": item.get("msgid", ""),
                        "itemidx": item.get("itemidx", "1"),
                    })
        except Exception as e:
            print(f"Warning: parse articleList failed: {e}")

    # Fallback: extract from data-link attributes
    if not articles:
        items = re.findall(
            r'<li class="album__list-item[^"]*"[^>]*data-link="([^"]+)"[^>]*data-title="([^"]+)"',
            album_html,
            re.DOTALL,
        )
        for link, title in items:
            articles.append({
                "title": html.unescape(title).replace("\xa0", " "),
                "url": html.unescape(link).replace("&amp;", "&"),
                "msgid": "",
                "itemidx": "1",
            })

    return biz, album_id, articles


def fetch_more_articles(biz, album_id, last_msgid, last_itemidx):
    """当合集存在分页时，调用 JSON 接口加载后续文章。"""
    url = (
        f"https://mp.weixin.qq.com/mp/appmsgalbum?"
        f"__biz={urllib.parse.quote(biz)}&"
        f"action=getalbum&"
        f"album_id={album_id}&"
        f"begin_msgid={last_msgid}&"
        f"begin_itemidx={last_itemidx}&"
        f"count=10&"
        f"f=json"
    )
    try:
        text = fetch(url)
        data = json.loads(text)
        return data.get("getalbum_resp", {}).get("article_list", [])
    except Exception as e:
        print(f"Warning: fetch_more_articles failed: {e}")
        return []


def extract_article_title(html_text):
    m = re.search(r'<h1[^>]*id=["\']activity-name["\'][^>]*>(.*?)</h1>', html_text, re.DOTALL)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', html_text)
    if m:
        return html.unescape(m.group(1))
    return None


def extract_js_content(html_text):
    markers = [
        '<div class="rich_media_content " id="js_content"',
        '<div class="rich_media_content" id="js_content"',
        'id="js_content"',
    ]
    start = -1
    for marker in markers:
        idx = html_text.find(marker)
        if idx >= 0:
            start = html_text.find(">", idx) + 1
            break
    if start < 0:
        return None

    depth = 1
    pos = start
    while pos < len(html_text) and depth > 0:
        next_open = html_text.find("<div", pos)
        next_close = html_text.find("</div>", pos)
        if next_close < 0:
            return None
        if next_open >= 0 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                return html_text[start:next_close]
            pos = next_close + 6
    return None


def article_to_markdown(url, fallback_title=None):
    html_text = fetch(url)
    if not html_text:
        return None, None
    title = extract_article_title(html_text) or fallback_title
    content_html = extract_js_content(html_text)
    if not content_html:
        return title, None
    parser = HTMLToMarkdownParser()
    parser.feed(content_html)
    return title, parser.get_markdown()


def sanitize_filename(title):
    name = title.replace("/", "-").replace("\\", "-")
    name = re.sub(r'[<>":|?*]', "", name)
    name = name.strip()
    return name or "untitled"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    album_url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./wechat_articles"
    os.makedirs(output_dir, exist_ok=True)

    print("Fetching album page...")
    album_html = fetch(album_url)
    biz, album_id, articles = extract_album_info(album_html)

    if not articles:
        print("No articles found. Please check the album URL.")
        sys.exit(1)

    print(f"Found {len(articles)} articles on first page. biz={biz}, album_id={album_id}")

    # Load more pages if needed
    # We detect if there's more by checking the last article and calling the API.
    # Since we don't have continue_flag easily, we try once if article count < 18
    # or if the API returns results. More robust: check if 'continue_flag' in HTML.
    if len(articles) < 20:
        last = articles[-1]
        if last["msgid"]:
            more = fetch_more_articles(biz, album_id, last["msgid"], last["itemidx"])
            for item in more:
                articles.append({
                    "title": html.unescape(item["title"]).replace("\xa0", " "),
                    "url": html.unescape(item["url"]).replace("&amp;", "&"),
                    "msgid": item.get("msgid", ""),
                    "itemidx": item.get("itemidx", "1"),
                })
            print(f"Total articles after loading more: {len(articles)}")

    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] {article['title']}")
        title, md = article_to_markdown(article["url"], fallback_title=article["title"])
        if md is None:
            print("  Failed to extract content, skipping.")
            continue

        filename = sanitize_filename(title) + ".md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"> 原文链接：{article['url']}\n\n")
            f.write(md)
            f.write("\n")
        print(f"  Saved: {filepath}")
        time.sleep(1)

    print(f"\nAll done. Saved to: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
