#!/usr/bin/env python3
"""Read-only, domain-scoped keyword search and structural audit for this vault."""
import argparse
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
TYPES = {"sources": "source", "entities": "entity", "concepts": "concept",
         "synthesis": "synthesis", "queries": "query"}


def metadata(text):
    """Read the vault's flat frontmatter subset; not a general YAML parser."""
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("缺少或损坏 frontmatter")
    fields = {}
    key = None
    for line in match[1].splitlines():
        item = re.match(r"^([\w-]+):\s*(.*)$", line)
        if item:
            key, value = item.groups()
            if key in fields:
                raise ValueError(f"重复字段 {key}")
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            if value.startswith("[") and value.endswith("]"):
                fields[key] = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            elif not value:
                fields[key] = []
            else:
                fields[key] = value.strip("\"'")
        elif re.match(r"^\s+-\s+", line) and key:
            if not isinstance(fields[key], list):
                raise ValueError(f"{key} 列表格式错误")
            fields[key].append(re.sub(r"^\s+-\s+", "", line).strip("\"'"))
    return fields, text[match.end():]


def registry(root):
    return json.loads((root / "docs/knowledge/domains.json").read_text(encoding="utf-8"))


def canonical_paths(root):
    return sorted(p for folder in TYPES for p in (root / "wiki" / folder).glob("*.md"))


def domain_errors(fields, registered):
    domains = fields.get("domains")
    if not isinstance(domains, list) or not domains:
        return ["domains 必须是非空列表"]
    errors = []
    if len(set(domains)) != len(domains):
        errors.append("domains 有重复值")
    if set(domains) - set(registered):
        errors.append("未知领域: " + ", ".join(sorted(set(domains) - set(registered))))
    if "shared" in domains and len(domains) != 1:
        errors.append("shared 必须独占")
    return errors


def freshness(updated, today=None):
    days = ((today or date.today()) - date.fromisoformat(updated)).days
    return "超过30天，强烈建议核验" if days > 30 else "超过14天，可能过期" if days > 14 else "14天内更新（非事实核验保证）"


def load_pages(root):
    registered = registry(root)
    pages, errors = [], []
    paths = canonical_paths(root)
    if not paths:
        errors.append("未找到五类正式 wiki 页面")
    for path in paths:
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
            fields, body = metadata(text)
            issues = domain_errors(fields, registered)
            for field in ("created", "updated"):
                try:
                    date.fromisoformat(fields.get(field, ""))
                except (TypeError, ValueError):
                    issues.append(f"{field} 必须是 ISO 日期")
            if fields.get("type") != TYPES[path.parent.name]:
                issues.append("type 与目录不一致")
            # domains uses a deliberately restricted, auditable inline convention.
            if not re.search(r"^domains: \[[^\n]*\]\s*(?:#.*)?$", text, re.M):
                issues.append("domains 必须使用行内列表")
            errors.extend(f"{rel}: {issue}" for issue in issues)
            if issues:
                continue
            title = re.search(r"^# (.+)$", body, re.M)
            pages.append({"path": rel, "title": title[1] if title else path.stem,
                          "fields": fields, "body": body})
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
    return pages, errors


def search(pages, domains, query=""):
    words = query.casefold().split()
    matches = []
    for page in pages:
        if not set(page["fields"]["domains"]) & set(domains):
            continue
        text = (page["path"] + "\n" + page["title"] + "\n" + page["body"]).casefold()
        if not all(word in text for word in words):
            continue
        fields = page["fields"]
        matches.append({"path": page["path"], "title": page["title"],
                        "domains": fields["domains"], "updated": fields["updated"],
                        "freshness": freshness(fields["updated"])})
    return matches


def links(text):
    text = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    for link in re.findall(r"\[\[([^\]\n]+)\]\]", text):
        target = link.replace("\\|", "|").split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            yield target.removesuffix(".md")


def resolve(target, root, names):
    if "/" in target:
        path = root / (target + ".md")
        return [path] if path.is_file() else []
    return names.get(target, [])


def audit(root):
    pages, errors = load_pages(root)
    warnings = []
    registered = registry(root)
    paths = canonical_paths(root)
    names = defaultdict(list)
    # Include legacy files to detect actual Obsidian ambiguity, not silently hide it.
    for path in list((root / "wiki").rglob("*.md")) + list((root / "domains").glob("*.md")) + [root / "index.md"]:
        names[path.stem].append(path)
    nav = []
    for domain, spec in registered.items():
        path = root / spec["entry"]
        if not path.is_file():
            errors.append(f"领域入口不存在: {spec['entry']}")
            continue
        nav.append(path)
        try:
            fields, _ = metadata(path.read_text(encoding="utf-8"))
            if fields.get("domains") != [domain] or fields.get("type") != "domain":
                errors.append(f"领域入口归属/type 不正确: {spec['entry']}")
        except ValueError as exc:
            errors.append(f"{spec['entry']}: {exc}")
    index = root / "index.md"
    indexed = set()
    if not index.is_file():
        errors.append("缺少 index.md")
    else:
        for target in links(index.read_text(encoding="utf-8")):
            indexed.update(resolve(target, root, names))
        for path in paths + nav:
            if path not in indexed:
                errors.append(f"索引缺页: {path.relative_to(root)}")
    ambiguous = 0
    for path in paths + nav + ([index] if index.exists() else []):
        for target in links(path.read_text(encoding="utf-8")):
            destinations = resolve(target, root, names)
            if not destinations:
                errors.append(f"死链 {target} <- {path.relative_to(root)}")
            elif len(destinations) > 1:
                ambiguous += 1
    if ambiguous:
        warnings.append(f"{ambiguous} 处历史裸 slug 链接存在同名歧义（含嵌套副本）；新增链接使用路径限定")
    empty_sources = []
    indirect_sources = []
    for page in pages:
        fields = page["fields"]
        if fields["type"] == "source":
            raw = fields.get("raw", "")
            if not isinstance(raw, str):
                raw = ""
            candidate = (root / raw).resolve()
            archive = (root / "raw/archive").resolve()
            if not candidate.is_relative_to(archive) or not candidate.is_file():
                errors.append(f"raw 缺失或不在 archive: {page['path']}")
            if "## 原始文件" not in page["body"] or f"](../../{raw})" not in unquote(page["body"]):
                errors.append(f"缺少有效原始文件回链: {page['path']}")
        else:
            sources = fields.get("sources")
            if not isinstance(sources, list):
                errors.append(f"sources 必须是列表: {page['path']}")
            else:
                if not sources:
                    empty_sources.append(page["path"])
                for source in sources:
                    if not (root / "wiki/sources" / (source + ".md")).is_file():
                        if names.get(source):
                            indirect_sources.append(f"{source} <- {page['path']}")
                        else:
                            errors.append(f"来源不存在 {source} <- {page['path']}")
    if indirect_sources:
        warnings.append("历史 sources 指向非 source 页，需另行追溯治理: " + "; ".join(indirect_sources))
    if empty_sources:
        warnings.append(f"{len(empty_sources)} 个历史非 source 页面 sources 为空，尚无原始来源链")
    legacy = sorted(str(p.relative_to(root)) for p in (root / "wiki").rglob("*.md") if p not in paths)
    if legacy:
        warnings.append(f"{len(legacy)} 个历史非标准路径未纳入检索: " + ", ".join(legacy))
    stale = sum("超过" in freshness(p["fields"]["updated"]) for p in pages)
    if stale:
        warnings.append(f"{stale} 个页面超过14天；结构迁移未刷新知识 updated")
    counts = Counter(d for page in pages for d in page["fields"]["domains"])
    return {"pages": len(pages), "domain_counts": dict(sorted(counts.items())),
            "errors": errors, "warnings": warnings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    lookup = sub.add_parser("search", help="显式范围的关键词检索；空查询列出范围内所有页面")
    scope = lookup.add_mutually_exclusive_group(required=True)
    scope.add_argument("--domain", action="append", help="领域 ID，可重复")
    scope.add_argument("--all", action="store_true", help="显式全库查询")
    lookup.add_argument("--include-shared", action="store_true")
    lookup.add_argument("--query", default="")
    lookup.add_argument("--json", action="store_true")
    check = sub.add_parser("audit")
    check.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    try:
        if args.command == "audit":
            report = audit(root)
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                print(f"正式页面: {report['pages']} | 领域计数（可重叠）: {report['domain_counts']}")
                for key in ("errors", "warnings"):
                    for item in report[key]:
                        print(f"{key.upper()}: {item}")
                print(f"结果: {len(report['errors'])} errors, {len(report['warnings'])} warnings")
            return int(bool(report["errors"]))
        registered = registry(root)
        selected = set(registered) if args.all else set(args.domain)
        if args.include_shared:
            selected.add("shared")
        if selected - set(registered):
            parser.error("未知领域: " + ", ".join(sorted(selected - set(registered))))
        pages, errors = load_pages(root)
        if errors:
            print("领域或页面元数据不合法；请先运行 audit:\n" + "\n".join(errors), file=sys.stderr)
            return 1
        results = search(pages, selected, args.query)
        if args.json:
            print(json.dumps({"scope": sorted(selected), "results": results}, ensure_ascii=False, indent=2))
        else:
            print(f"范围: {', '.join(sorted(selected))} | 匹配: {len(results)}")
            for page in results:
                print(f"{page['path']} — {page['title']}\n  {', '.join(page['domains'])} | updated {page['updated']} | {page['freshness']}")
            if not results:
                print("当前范围无匹配；未自动扩域。可调整关键词或显式选择其他领域。")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
