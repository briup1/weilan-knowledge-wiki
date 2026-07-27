#!/usr/bin/env python3
"""
llm-ingest: LLM Wiki 知识库摄取辅助脚本
基于 Karpathy LLM Wiki 模式 (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

用法:
    python ingest.py scan   <kb_root>          # 扫描 raw/ 并列出未处理文件
    python ingest.py status <kb_root>          # 显示知识库状态摘要
    python ingest.py log    <kb_root> <msg>    # 向 wiki/log.md 追加日志条目
    python ingest.py init   <kb_root>          # 初始化知识库目录结构
    python ingest.py stale  <kb_root>          # 检测 raw/ 中已变更的文件（基于哈希）
"""

import sys
import os
import hashlib
import json
import datetime
from pathlib import Path


# ──────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────
RAW_DIR = "raw"
WIKI_DIR = "wiki"
INDEX_FILE = "index.md"
LOG_FILE = "log.md"
SCHEMA_FILE = "CLAUDE.md"
STATE_FILE = ".ingest_state.json"  # 隐藏的状态文件，存储文件哈希

SUPPORTED_EXTENSIONS = {
    ".md", ".txt", ".pdf", ".html", ".htm",
    ".py", ".js", ".ts", ".json", ".yaml", ".yml",
    ".csv", ".tex", ".rst", ".org"
}

IGNORE_PATTERNS = {
    ".git", ".DS_Store", "__pycache__", "node_modules",
    ".ingest_state.json", "*.pyc"
}


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────
def file_hash(path: Path) -> str:
    """计算文件内容的 SHA256 哈希（前 4096 字节，快速版）"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(4096))
        h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def load_state(kb_root: Path) -> dict:
    state_path = kb_root / STATE_FILE
    if state_path.exists():
        with open(state_path, encoding="utf-8") as f:
            return json.load(f)
    return {"ingested": {}}


def save_state(kb_root: Path, state: dict):
    state_path = kb_root / STATE_FILE
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def is_ignored(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_PATTERNS or part.startswith("."):
            return True
    return False


def scan_raw(kb_root: Path) -> list[Path]:
    """递归扫描 raw/ 目录，返回支持的文件列表"""
    raw_dir = kb_root / RAW_DIR
    if not raw_dir.exists():
        return []
    files = []
    for f in raw_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            if not is_ignored(f.relative_to(kb_root)):
                files.append(f)
    return sorted(files)


# ──────────────────────────────────────────────
# 命令：init
# ──────────────────────────────────────────────
def cmd_init(kb_root: Path):
    """初始化知识库目录结构"""
    dirs = [
        kb_root / RAW_DIR / "assets",
        kb_root / RAW_DIR / "archive",
        kb_root / WIKI_DIR / "sources",
        kb_root / WIKI_DIR / "entities",
        kb_root / WIKI_DIR / "concepts",
        kb_root / WIKI_DIR / "synthesis",
        kb_root / WIKI_DIR / "queries",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {d.relative_to(kb_root)}/")

    # 创建 index.md
    index_path = kb_root / INDEX_FILE
    if not index_path.exists():
        index_path.write_text(
            "# Knowledge Forest 索引\n\n"
            "> 按类别组织的 wiki 页面目录。每页格式：`[[page-name]] —— 一行摘要`。\n\n"
            "## Entities\n\n"
            "## Concepts\n\n"
            "## Sources\n\n"
            "## Synthesis\n\n"
            "## Queries\n\n"
        )
        print(f"  ✓ {INDEX_FILE}")

    # 创建 log.md
    log_path = kb_root / LOG_FILE
    if not log_path.exists():
        log_path.write_text(
            "# 操作日志\n\n"
            "> 此文件为 append-only 操作记录。格式：`## [日期] 操作类型 | 描述`\n\n"
        )
        print(f"  ✓ {LOG_FILE}")

    # 创建 CLAUDE.md schema 模板
    schema_path = kb_root / SCHEMA_FILE
    if not schema_path.exists():
        schema_path.write_text(
            "# Wiki Schema（知识库配置）\n\n"
            "> 此文件告诉 LLM 知识库的结构和操作约定。\n\n"
            "## 目录结构\n\n"
            "```\n"
            ".\n"
            "├── CLAUDE.md          # 本文件 —— wiki 的架构与约定\n"
            "├── index.md           # 所有 wiki 页面的内容型目录\n"
            "├── log.md             # 只追加的时间线记录（入库/查询/巡检）\n"
            "├── raw/               # 不可变的原始文档（文章、论文、转录稿）\n"
            "│   ├── assets/        # 待入库的新文章 + 本地图片/附件\n"
            "│   └── archive/       # 已入库并处理完毕的文章\n"
            "└── wiki/              # 由 LLM 生成的 markdown（请勿手动编辑）\n"
            "    ├── sources/       # 每个被入库的来源对应一个页面（摘要 + 核心要点）\n"
            "    ├── entities/      # 谁/什么工具：产品、公司、项目、开源库、具体的人\n"
            "    ├── concepts/      # 什么思想/方法：抽象概念、设计模式、方法论、技术范式\n"
            "    ├── synthesis/     # 跨来源的综合：领域内知识全景 + 跨领域分析对比\n"
            "    └── queries/       # 问题的答案，归档以备复用\n"
            "```\n\n"
            "## 摄取约定（Ingest）\n\n"
            "1. 从 `raw/assets/` 中读取新来源\n"
            "2. 创建/更新 `wiki/sources/<slug>.md`，写入摘要与核心主张\n"
            "3. 更新受该来源影响的 `wiki/entities/` 和 `wiki/concepts/` 页面\n"
            "4. 主动产出或更新 `wiki/synthesis/` 综合页面\n"
            "5. 使用 `[[wiki-links]]` 格式添加交叉引用，禁止死链\n"
            "6. 更新 `wiki/index.md` 目录\n"
            "7. 向 `wiki/log.md` 追加记录，并将源文件移动到 `raw/archive/`\n\n"
            "## Wiki 页面 Frontmatter 格式\n\n"
            "```yaml\n"
            "---\n"
            "type: source | entity | concept | synthesis | query\n"
            "created: YYYY-MM-DD\n"
            "updated: YYYY-MM-DD\n"
            "sources: [source-slug-1, source-slug-2]\n"
            "raw: raw/archive/<原始文件名>.md    # 仅 source 页面必填\n"
            "tags: [tag1, tag2]\n"
            "---\n"
            "```\n\n"
            "## 查询约定（Query）\n\n"
            "1. 先读取 `wiki/index.md` 定位相关页面\n"
            "2. 读取相关页面内容并综合答案，使用 `[[page-name]]` 链接引用\n"
            "3. 优质答案归档为 `wiki/queries/<slug>.md` 并更新 index.md\n\n"
            "## 整理约定（Lint）\n\n"
            "- 扫描孤立页面、死链、矛盾和陈旧主张\n"
            "- 检查 source 页面的 `raw` 字段和原始文件链接\n"
            "- 发现缺少独立页面的重要概念\n"
        )
        print(f"  ✓ {SCHEMA_FILE}")

    print(f"\n✅ 知识库初始化完成：{kb_root}")
    print("   下一步：将原始资料放入 raw/，然后运行 `ingest.py scan <kb_root>` 查看待处理文件。")


# ──────────────────────────────────────────────
# 命令：scan
# ──────────────────────────────────────────────
def cmd_scan(kb_root: Path):
    """扫描 raw/ 并区分「已摄取」与「待处理」文件"""
    state = load_state(kb_root)
    ingested = state.get("ingested", {})
    files = scan_raw(kb_root)

    if not files:
        print(f"⚠️  raw/ 目录为空或不存在：{kb_root / RAW_DIR}")
        return

    new_files = []
    changed_files = []
    done_files = []

    for f in files:
        rel = str(f.relative_to(kb_root))
        current_hash = file_hash(f)
        if rel not in ingested:
            new_files.append((f, rel))
        elif ingested[rel]["hash"] != current_hash:
            changed_files.append((f, rel, ingested[rel]["hash"], current_hash))
        else:
            done_files.append((f, rel))

    print(f"\n📂 知识库：{kb_root}")
    print(f"   raw/ 文件总数：{len(files)}")
    print(f"   ✅ 已摄取：{len(done_files)}")
    print(f"   🆕 待摄取（新文件）：{len(new_files)}")
    print(f"   🔄 已变更（需重新摄取）：{len(changed_files)}")

    if new_files:
        print("\n──── 🆕 待摄取文件 ────")
        for f, rel in new_files:
            size_kb = f.stat().st_size / 1024
            print(f"  {rel}  ({size_kb:.1f} KB)")

    if changed_files:
        print("\n──── 🔄 已变更文件 ────")
        for f, rel, old_h, new_h in changed_files:
            print(f"  {rel}  (hash: {old_h} → {new_h})")

    if not new_files and not changed_files:
        print("\n🎉 所有文件均已摄取，知识库是最新的。")
    else:
        total_pending = len(new_files) + len(changed_files)
        print(f"\n💡 共 {total_pending} 个文件待处理。")
        print("   请将待摄取文件路径提供给 LLM，执行 Ingest 操作。")
        print("   完成后运行 `ingest.py log <kb_root> \"ingest | <文件名>\"` 记录日志。")


# ──────────────────────────────────────────────
# 命令：status
# ──────────────────────────────────────────────
def cmd_status(kb_root: Path):
    """显示知识库整体状态"""
    state = load_state(kb_root)
    ingested = state.get("ingested", {})

    # 统计 raw/
    raw_files = scan_raw(kb_root)
    raw_size = sum(f.stat().st_size for f in raw_files)

    # 统计 wiki/
    wiki_dir = kb_root / WIKI_DIR
    wiki_files = list(wiki_dir.rglob("*.md")) if wiki_dir.exists() else []
    wiki_size = sum(f.stat().st_size for f in wiki_files)

    # 最近日志
    log_path = kb_root / LOG_FILE
    recent_logs = []
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").splitlines()
        recent_logs = [l for l in lines if l.startswith("## [")][-5:]

    print(f"\n📊 知识库状态：{kb_root}")
    print(f"   ── 原始来源（raw/）──")
    print(f"   文件数：{len(raw_files)}")
    print(f"   已摄取：{len(ingested)}")
    print(f"   总大小：{raw_size / 1024:.1f} KB")
    print(f"\n   ── Wiki 层（wiki/）──")
    print(f"   页面数：{len(wiki_files)}")
    print(f"   总大小：{wiki_size / 1024:.1f} KB")

    if recent_logs:
        print(f"\n   ── 最近操作（log.md）──")
        for log in recent_logs:
            print(f"   {log}")

    # 检测是否有 index.md
    index_ok = (kb_root / INDEX_FILE).exists()
    schema_ok = (kb_root / SCHEMA_FILE).exists()
    print(f"\n   ── 配置检查 ──")
    print(f"   {'✅' if index_ok else '❌'} index.md {'存在' if index_ok else '缺失（建议创建）'}")
    print(f"   {'✅' if schema_ok else '❌'} CLAUDE.md {'存在' if schema_ok else '缺失（建议创建）'}")


# ──────────────────────────────────────────────
# 命令：log
# ──────────────────────────────────────────────
def cmd_log(kb_root: Path, message: str):
    """向 wiki/log.md 追加一条操作记录"""
    log_path = kb_root / LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = f"\n## [{now_str()}] {message}\n"

    if not log_path.exists():
        log_path.write_text("# 操作日志\n\n> append-only 操作记录。\n")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"✅ 日志已追加：{entry.strip()}")

    # 同时更新 state（如果消息包含 ingest | <文件>，标记为已摄取）
    if message.startswith("ingest |"):
        parts = message.split("|", 1)
        if len(parts) == 2:
            filename = parts[1].strip()
            # 尝试在 raw/ 中找到该文件
            raw_dir = kb_root / RAW_DIR
            matched = list(raw_dir.rglob(f"*{filename}*")) if raw_dir.exists() else []
            if matched:
                state = load_state(kb_root)
                for f in matched:
                    rel = str(f.relative_to(kb_root))
                    state.setdefault("ingested", {})[rel] = {
                        "hash": file_hash(f),
                        "ingested_at": now_str()
                    }
                save_state(kb_root, state)
                print(f"   已标记 {len(matched)} 个文件为「已摄取」")


# ──────────────────────────────────────────────
# 命令：stale
# ──────────────────────────────────────────────
def cmd_stale(kb_root: Path):
    """检测自上次摄取以来内容已变更的文件"""
    state = load_state(kb_root)
    ingested = state.get("ingested", {})
    files = scan_raw(kb_root)

    stale = []
    for f in files:
        rel = str(f.relative_to(kb_root))
        if rel in ingested:
            current_hash = file_hash(f)
            if ingested[rel]["hash"] != current_hash:
                stale.append((rel, ingested[rel].get("ingested_at", "?"), current_hash))

    if not stale:
        print("✅ 所有已摄取文件均未变更。")
    else:
        print(f"🔄 检测到 {len(stale)} 个已变更文件（需重新摄取）：\n")
        for rel, ingested_at, new_hash in stale:
            print(f"  {rel}")
            print(f"    上次摄取：{ingested_at} | 新哈希：{new_hash}")


# ──────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────
def main():
    usage = (
        "用法：\n"
        "  python ingest.py init   <kb_root>        # 初始化知识库\n"
        "  python ingest.py scan   <kb_root>        # 扫描待处理文件\n"
        "  python ingest.py status <kb_root>        # 显示状态摘要\n"
        "  python ingest.py log    <kb_root> <msg>  # 追加操作日志\n"
        "  python ingest.py stale  <kb_root>        # 检测已变更文件\n"
    )

    if len(sys.argv) < 3:
        print(usage)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    kb_root = Path(sys.argv[2]).expanduser().resolve()

    if not kb_root.exists() and cmd != "init":
        print(f"❌ 目录不存在：{kb_root}")
        print("   提示：先运行 `ingest.py init <kb_root>` 初始化知识库。")
        sys.exit(1)

    if cmd == "init":
        kb_root.mkdir(parents=True, exist_ok=True)
        cmd_init(kb_root)
    elif cmd == "scan":
        cmd_scan(kb_root)
    elif cmd == "status":
        cmd_status(kb_root)
    elif cmd == "log":
        if len(sys.argv) < 4:
            print("❌ 缺少日志消息。用法：ingest.py log <kb_root> <message>")
            sys.exit(1)
        msg = " ".join(sys.argv[3:])
        cmd_log(kb_root, msg)
    elif cmd == "stale":
        cmd_stale(kb_root)
    else:
        print(f"❌ 未知命令：{cmd}")
        print(usage)
        sys.exit(1)


if __name__ == "__main__":
    main()
