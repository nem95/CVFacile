# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cvfacile import build, latex, mcp, model  # noqa: E402
from cvfacile.templates import TEMPLATES  # noqa: E402

EXAMPLE = ROOT / "examples" / "example.json"


class LatexTest(unittest.TestCase):
    def test_escape_special_characters(self):
        self.assertEqual(latex.escape("R&D 100% #1 a_b $"), r"R\&D 100\% \#1 a\_b \$")
        self.assertEqual(latex.escape("\\{x}"), r"\textbackslash{}\{x\}")

    def test_inline_markup(self):
        self.assertEqual(latex.inline("a **b & c** d"), r"a \textbf{b \& c} d")
        self.assertEqual(latex.inline("[site](https://x.io/a_b#c)"), r"\href{https://x.io/a_b\#c}{site}")
        self.assertEqual(latex.inline("**[l](https://a.b)**"), r"\textbf{\href{https://a.b}{l}}")

    def test_unclosed_bold_is_left_as_text(self):
        self.assertEqual(latex.inline("**oops"), "**oops")


class ModelTest(unittest.TestCase):
    def setUp(self):
        self.data = model.load(EXAMPLE)

    def test_example_is_valid(self):
        issues = model.validate(self.data, EXAMPLE.parent)
        self.assertEqual(issues, [])

    def test_localize_and_default_lang(self):
        self.assertEqual(model.default_lang(self.data), "en")
        cv, missing = model.resolve(self.data, "en")
        self.assertEqual(cv["basics"]["label"], "Full-Stack Engineer • Front-End Focus")
        self.assertEqual(missing, [])

    def test_missing_translation_falls_back(self):
        cv, missing = model.resolve({"basics": {"name": "A", "label": {"fr": "Dev"}}}, "en")
        self.assertEqual(cv["basics"]["label"], "Dev")
        self.assertEqual(missing, ["$.basics.label"])

    def test_variant_hides_and_overrides(self):
        cv, _ = model.resolve(self.data, "fr", "no-phone")
        self.assertNotIn("phone", cv["basics"])
        cv, _ = model.resolve(self.data, "fr", "backend")
        self.assertEqual(cv["basics"]["label"], "Développeur Back-End")
        self.assertNotIn("projects", cv)

    def test_unknown_variant(self):
        with self.assertRaises(model.CVError):
            model.resolve(self.data, "fr", "nope")

    def test_validation_reports_paths(self):
        issues = model.validate({"basics": {}, "work": [{"company": "X"}]}, ROOT)
        paths = {i["path"] for i in issues if i["level"] == "error"}
        self.assertEqual(paths, {"$.basics.name", "$.work[0].position"})

    def test_malformed_variants_are_errors_not_crashes(self):
        issues = model.validate({"basics": {"name": "A"}, "variants": {"x": "oops", "y": {"hide": "phone"}}}, ROOT)
        paths = {i["path"] for i in issues if i["level"] == "error"}
        self.assertEqual(paths, {"$.variants.x", "$.variants.y.hide"})


class TemplateTest(unittest.TestCase):
    def test_all_templates_render_every_language(self):
        data = model.load(EXAMPLE)
        for name, tpl in TEMPLATES.items():
            for lang in ("fr", "en"):
                cv, _ = model.resolve(data, lang)
                tex = tpl.render(cv, lang)
                self.assertIn(r"\begin{document}", tex, name)
                self.assertIn(r"\end{document}", tex, name)
                self.assertNotIn("**", tex, name)

    def test_output_stem(self):
        self.assertEqual(build.output_stem(Path("cv.json"), "no-phone", None, "fr"), "cv-no-phone-fr")
        self.assertEqual(build.output_stem(Path("cv.json"), "x/../../evil", None, "en"), "cv-x_.._.._evil-en")

    def test_parse_log(self):
        log = "Output written on cv.pdf (2 pages, 1234 bytes).\nOverfull \\hbox (3pt too wide)\n! Undefined control sequence.\nl.12 \\foo\n"
        parsed = build.parse_log(log)
        self.assertEqual(parsed["pages"], 2)
        self.assertEqual(parsed["overfull"], 1)
        self.assertIn("l.12", parsed["errors"][0])


class McpTest(unittest.TestCase):
    def test_initialize_and_list(self):
        init = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "cvfacile")
        tools = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, {"check_cv", "build_cv", "list_templates", "get_schema"})
        self.assertIsNone(mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_check_tool(self):
        reply = mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                            "params": {"name": "check_cv", "arguments": {"path": str(EXAMPLE)}}})
        self.assertFalse(reply["result"]["isError"])
        self.assertTrue(json.loads(reply["result"]["content"][0]["text"])["ok"])

    def test_schema_is_valid_json(self):
        json.loads(mcp.SCHEMA_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
