import contextlib
from datetime import date
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("kb", Path(__file__).resolve().parents[1] / "kb.py")
kb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kb)


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.today = date.today().isoformat()
        config = {}
        for domain in ("software-development", "ai-media", "shared"):
            entry = f"domains/{domain}.md"
            config[domain] = {"title": domain, "entry": entry, "scope": domain}
            self.write(entry, f"---\ntype: domain\ndomains: [{domain}]\n---\n# {domain}\n")
        self.write("docs/knowledge/domains.json", json.dumps(config))
        self.page("concepts/media", ["ai-media"], "video 媒体")
        self.page("concepts/code", ["software-development"], "video 软件")
        self.page("concepts/common", ["shared"], "video 通用")
        self.page("entities/cross", ["software-development", "ai-media"], "video Remotion")
        self.write("raw/archive/source file.md", "immutable evidence")
        self.write("wiki/sources/evidence.md", f"---\ntype: source\ncreated: {self.today}\nupdated: {self.today}\ndomains: [software-development]\nraw: raw/archive/source file.md\n---\n# Evidence\n\n## 原始文件\n\n- [原文](../../raw/archive/source%20file.md)\n")
        self.reindex()

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")

    def page(self, name, domains, body=""):
        kind = kb.TYPES[name.split("/")[0]]
        self.write(f"wiki/{name}.md", f"---\ntype: {kind}\ncreated: {self.today}\nupdated: {self.today}\ndomains: [{', '.join(domains)}]\nsources: [evidence]\ntags: [test]\n---\n# {name}\n\n{body}\n")

    def reindex(self):
        paths = kb.canonical_paths(self.root) + list((self.root / "domains").glob("*.md"))
        self.write("index.md", "\n".join(f"[[{p.relative_to(self.root).with_suffix('')}]]" for p in paths))

    def mutate(self, path, old, new):
        dest = self.root / path
        dest.write_text(dest.read_text().replace(old, new), encoding="utf-8")

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = kb.main(["--root", str(self.root), *args])
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_single_domain_excludes_shared_and_other_domain(self):
        pages, errors = kb.load_pages(self.root)
        self.assertEqual([], errors)
        found = kb.search(pages, ["ai-media"], "video")
        self.assertEqual({"wiki/concepts/media.md", "wiki/entities/cross.md"}, {p["path"] for p in found})

    def test_explicit_shared(self):
        code, out, _ = self.run_cli("search", "--domain", "ai-media", "--include-shared", "--json")
        self.assertEqual(0, code)
        result = json.loads(out)
        self.assertEqual(["ai-media", "shared"], result["scope"])
        self.assertEqual(3, len(result["results"]))

    def test_cross_domain_union_deduplicates(self):
        code, out, _ = self.run_cli("search", "--domain", "ai-media", "--domain", "software-development", "--json")
        self.assertEqual(0, code)
        paths = [p["path"] for p in json.loads(out)["results"]]
        self.assertEqual(4, len(paths))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("wiki/concepts/common.md", paths)

    def test_all_scope_is_explicit(self):
        code, out, _ = self.run_cli("search", "--all", "--json")
        self.assertEqual(0, code)
        self.assertEqual(5, len(json.loads(out)["results"]))
        self.assertEqual(2, self.run_cli("search", "--query", "video")[0])
        self.assertEqual(2, self.run_cli("search", "--all", "--domain", "ai-media")[0])

    def test_unknown_domain_rejected(self):
        self.assertEqual(2, self.run_cli("search", "--domain", "typo")[0])

    def test_no_hits_do_not_expand(self):
        code, out, _ = self.run_cli("search", "--domain", "ai-media", "--query", "软件", "--json")
        self.assertEqual(0, code)
        self.assertEqual([], json.loads(out)["results"])
        self.assertEqual(["ai-media"], json.loads(out)["scope"])

    def test_keywords_casefold_and_all_terms(self):
        pages, _ = kb.load_pages(self.root)
        found = kb.search(pages, ["ai-media"], "VIDEO remotion")
        self.assertEqual(["wiki/entities/cross.md"], [p["path"] for p in found])

    def test_scope_uses_metadata_not_mentions(self):
        self.mutate("wiki/concepts/code.md", "video 软件", "ai-media video software")
        code, out, _ = self.run_cli("search", "--domain", "ai-media", "--json")
        self.assertEqual(0, code)
        self.assertNotIn("wiki/concepts/code.md", [p["path"] for p in json.loads(out)["results"]])

    def test_invalid_domains(self):
        for value in (None, [], "ai-media", ["unknown"], ["ai-media", "ai-media"], ["shared", "ai-media"]):
            with self.subTest(value=value):
                self.assertTrue(kb.domain_errors({"domains": value}, kb.registry(self.root)))

    def test_invalid_metadata_blocks_search_and_audit(self):
        self.mutate("wiki/concepts/media.md", "domains: [ai-media]", "domains: [typo]")
        self.assertEqual(1, self.run_cli("search", "--all")[0])
        self.assertEqual(1, self.run_cli("audit")[0])

    def test_block_domains_rejected_by_vault_convention(self):
        self.mutate("wiki/concepts/media.md", "domains: [ai-media]", "domains:\n  - ai-media")
        self.assertTrue(any("行内列表" in e for e in kb.audit(self.root)["errors"]))

    def test_duplicate_frontmatter_key_rejected(self):
        with self.assertRaises(ValueError):
            kb.metadata("---\ndomains: [ai-media]\ndomains: [shared]\n---\n")

    def test_block_sources_supported(self):
        self.mutate("wiki/concepts/media.md", "sources: [evidence]", "sources:\n  - evidence")
        self.assertEqual([], kb.audit(self.root)["errors"])

    def test_audit_clean_and_percent_encoded_raw_link(self):
        report = kb.audit(self.root)
        self.assertEqual([], report["errors"])
        self.assertEqual([], report["warnings"])

    def test_audit_missing_raw(self):
        (self.root / "raw/archive/source file.md").unlink()
        self.assertTrue(any("raw 缺失" in e for e in kb.audit(self.root)["errors"]))

    def test_audit_rejects_raw_outside_archive(self):
        self.write("outside.md", "outside")
        self.mutate("wiki/sources/evidence.md", "raw: raw/archive/source file.md", "raw: outside.md")
        self.assertTrue(any("raw 缺失或不在 archive" in e for e in kb.audit(self.root)["errors"]))

    def test_audit_missing_raw_backlink(self):
        self.mutate("wiki/sources/evidence.md", "## 原始文件", "## Other")
        self.assertTrue(any("原始文件回链" in e for e in kb.audit(self.root)["errors"]))

    def test_audit_missing_source(self):
        self.mutate("wiki/concepts/media.md", "sources: [evidence]", "sources: [missing]")
        self.assertTrue(any("来源不存在" in e for e in kb.audit(self.root)["errors"]))

    def test_legacy_indirect_sources_are_visible_warnings(self):
        self.mutate("wiki/concepts/media.md", "sources: [evidence]", "sources: [code]")
        report = kb.audit(self.root)
        self.assertEqual([], report["errors"])
        self.assertTrue(any("非 source" in w for w in report["warnings"]))

    def test_audit_missing_index_entry(self):
        self.mutate("index.md", "[[wiki/concepts/media]]", "")
        self.assertTrue(any("索引缺页" in e for e in kb.audit(self.root)["errors"]))

    def test_audit_missing_domain_portal(self):
        (self.root / "domains/ai-media.md").unlink()
        self.assertTrue(any("领域入口不存在" in e for e in kb.audit(self.root)["errors"]))

    def test_audit_broken_links_but_not_code_examples(self):
        self.mutate("wiki/concepts/media.md", "video 媒体", "```\n[[example]]\n```\n`[[inline]]`\n[[missing|alias]]")
        errors = kb.audit(self.root)["errors"]
        self.assertEqual(1, len(errors))
        self.assertIn("死链 missing", errors[0])

    def test_legacy_duplicates_are_excluded_and_reported(self):
        self.write("wiki/synthesis/concepts/media.md", "# old copy\nvideo")
        self.write("wiki/notes/history.md", "# history")
        code, out, _ = self.run_cli("search", "--all", "--json")
        self.assertEqual(0, code)
        self.assertEqual(5, len(json.loads(out)["results"]))
        self.assertTrue(any("2 个历史非标准" in w for w in kb.audit(self.root)["warnings"]))

    def test_no_modification_by_read_only_commands(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.run_cli("search", "--all")
        self.run_cli("audit")
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_freshness_boundaries(self):
        today = date(2026, 9, 17)
        self.assertIn("14天内", kb.freshness("2026-09-03", today))
        self.assertIn("超过14天", kb.freshness("2026-09-02", today))
        self.assertIn("超过14天", kb.freshness("2026-08-18", today))
        self.assertIn("超过30天", kb.freshness("2026-08-17", today))


if __name__ == "__main__":
    unittest.main()
