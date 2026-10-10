import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class ToolCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_tool(self, script, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args)],
                              text=True, capture_output=True, check=False)


class VoiceProfileTest(ToolCase):
    def test_counts_and_differences_follow_one_rule_set(self):
        before = self.write("before.txt", "I think we're ready. You'll see the log (today); maybe later!\n\nIt's fine.")
        after = self.write("after.txt", "We are ready. The log appears today.")
        result = self.run_tool("voice_profile.py", "--before", before, "--after", after)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        old = data["profiles"]["before"]
        self.assertEqual(old["sentence_lengths"], [4, 7, 2])
        self.assertEqual(old["contractions"]["count"], 3)
        self.assertEqual(old["person"]["first"]["count"], 2)
        self.assertEqual(old["person"]["second"]["count"], 1)
        self.assertEqual(old["person"]["third"]["count"], 1)
        self.assertEqual(old["hedges"]["count"], 2)
        self.assertEqual(old["punctuation"]["parentheses"]["count"], 2)
        self.assertEqual(old["punctuation"]["semicolons"]["count"], 1)
        delta = data["after_minus_before"]
        self.assertEqual(delta["contractions"]["count"], {"delta": -3, "relative_change": -1.0})
        self.assertIsNone(delta["punctuation"]["colons"]["count"]["relative_change"])

    def test_possessive_is_not_contraction_and_sample_is_compared(self):
        before = self.write("before.txt", "The team's plan works.")
        after = self.write("after.txt", "The team's plan works.")
        sample = self.write("sample.txt", "Don't wait.")
        data = json.loads(self.run_tool("voice_profile.py", "--before", before, "--after", after,
                                        "--sample", sample).stdout)
        self.assertEqual(data["profiles"]["before"]["contractions"]["count"], 0)
        self.assertEqual(data["before_minus_sample"]["contractions"]["count"]["delta"], -1)

    def test_hedges_match_across_line_breaks(self):
        before = self.write("before.txt", "I\nthink so. I  think so. Sort\nof. PROBABLY.")
        after = self.write("after.txt", "I think so. I think so. Sort of. Probably.")
        result = self.run_tool("voice_profile.py", "--before", before, "--after", after)
        delta = json.loads(result.stdout)["after_minus_before"]["hedges"]["count"]
        self.assertEqual(delta["delta"], 0)

    def test_invalid_input_exits_two(self):
        before = self.root / "missing.txt"
        after = self.root / "bad.txt"
        after.write_bytes(b"\xff")
        self.assertEqual(self.run_tool("voice_profile.py", "--before", before, "--after", after).returncode, 2)
        before.write_text("ok", encoding="utf-8")
        self.assertEqual(self.run_tool("voice_profile.py", "--before", before, "--after", after).returncode, 2)


class PreservationTest(ToolCase):
    SOURCE = """---
title: Release
---
Run `deploy --prod` and read [the guide](docs/run.md "Guide").
See [policy][rules], [rules], <https://example.com>, and ![chart](img/a.png).
He said “keep this”.

```sh
deployctl start
```

> Approved wording
lazy approved line

[rules]: https://example.com/rules
"""

    def check(self, after):
        before = self.write("before.md", self.SOURCE)
        changed = self.write("after.md", after)
        result = self.run_tool("validate_preservation.py", "--before", before, "--after", changed)
        return result.returncode, json.loads(result.stdout) if result.stdout else None

    def test_prose_edit_keeps_protected_strings(self):
        code, data = self.check(self.SOURCE.replace("Run", "Use").replace("See", "Read"))
        self.assertEqual(code, 0)
        self.assertEqual(data["status"], "matched")
        self.assertEqual(data["counts"]["before"], {"frontmatter": 1, "code": 2, "quote": 2, "link_target": 6})

    def test_each_protected_category_reports_location(self):
        cases = {
            "frontmatter": ("title: Release", "title: Launch"),
            "code": ("deployctl start", "deployctl begin"),
            "quote": ("“keep this”", "“change this”"),
            "link_target": ("img/a.png", "img/b.png"),
        }
        for kind, (old, new) in cases.items():
            with self.subTest(kind=kind):
                code, data = self.check(self.SOURCE.replace(old, new, 1))
                self.assertEqual(code, 1)
                difference = next(item for item in data["differences"] if item["kind"] == kind)
                self.assertGreaterEqual(difference["before"][0]["line"], 1)
                self.assertGreaterEqual(difference["before"][0]["column"], 1)

    def test_lazy_blockquote_reference_label_and_duplicate_count_are_protected(self):
        for old, new in (("lazy approved line", "lazy edited line"), ("[rules],", "[rule],"), ("`deploy --prod`", "`deploy --prod` `deploy --prod`")):
            with self.subTest(old=old):
                code, data = self.check(self.SOURCE.replace(old, new, 1))
                self.assertEqual(code, 1, data)

    def test_quote_reordering_on_same_line_changes_sequence(self):
        before = self.write("before.md", "Use “first” then “second”.\n")
        after = self.write("after.md", "Use “second” then “first”.\n")
        result = self.run_tool("validate_preservation.py", "--before", before, "--after", after)
        self.assertEqual(result.returncode, 1)

    def test_apostrophes_are_not_quotes(self):
        before = self.write("before.md", "We're ready and it's done.\n")
        after = self.write("after.md", "We are ready and it is done.\n")
        result = self.run_tool("validate_preservation.py", "--before", before, "--after", after)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_list_continuations_are_prose_and_indented_code_stays_protected(self):
        before = """- Parent item
    - We has fixed the bug.
    - Nested item is utilise here

1. First step

    This step are optional.

Intro paragraph
    lazy line are prose.

    real indented code

- Item with code:

      item code
"""
        after = (before.replace("We has", "We have").replace("utilise", "used")
                 .replace("step are", "step is").replace("line are", "line is"))
        result = self.run_tool("validate_preservation.py", "--before", self.write("before.md", before), "--after", self.write("after.md", after))
        self.assertEqual(result.returncode, 0, result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["counts"]["before"]["code"], 2)
        for old, new in (("real indented code", "real indented text"), ("item code", "item text")):
            with self.subTest(old=old):
                changed = self.write("changed.md", before.replace(old, new))
                result = self.run_tool("validate_preservation.py", "--before", self.write("before.md", before), "--after", changed)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(json.loads(result.stdout)["differences"][0]["kind"], "code")

    def test_heading_or_fence_after_list_closes_it_for_indented_code(self):
        for block in ("## Next section", "```sh\nrun\n```"):
            with self.subTest(block=block):
                before = f"- item one\n- item two\n{block}\n\n    old_code()\n"
                result = self.run_tool("validate_preservation.py", "--before", self.write("before.md", before),
                                       "--after", self.write("after.md", before.replace("old_code", "new_code")))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("code", {item["kind"] for item in json.loads(result.stdout)["differences"]})

    def compare(self, before, after):
        result = self.run_tool("validate_preservation.py", "--before", self.write("before.md", before),
                               "--after", self.write("after.md", after))
        return result.returncode, json.loads(result.stdout)

    def test_list_item_fence_and_quote_are_protected(self):
        before = "- > Approved: ship on Friday.\n\n1. ```sh\n   pip install tool\n   ```\n\nThis are prose.\n\n```\nlater\n```\n"
        for old, new in (("Friday", "Monday"), ("pip install", "pip uninstall")):
            with self.subTest(old=old):
                self.assertEqual(self.compare(before, before.replace(old, new))[0], 1)
        self.assertEqual(self.compare(before, before.replace("This are", "This is"))[0], 0)

    def test_single_quotes_with_apostrophes_are_protected(self):
        for before, after in (("He said 'it's fine' today.\n", "He said 'it's okay' today.\n"),
                              ("She said ‘we’re ready’ today.\n", "She said ‘we’re set’ today.\n")):
            with self.subTest(before=before):
                code, data = self.compare(before, after)
                self.assertEqual((code, data["differences"][0]["kind"]), (1, "quote"))

    def test_footnote_definition_is_prose(self):
        code, data = self.compare("Text[^1].\n\n[^1]: This are a note.\n", "Text[^1].\n\n[^1]: This is a note.\n")
        self.assertEqual(code, 0, data)

    def test_bare_urls_are_protected_without_trailing_punctuation(self):
        for old, new in (("https://x.test/a", "https://x.test/b"), ("www.y.test/a", "www.y.test/b")):
            with self.subTest(old=old):
                before = f"Go to {old}. Then (see {old})."
                code, data = self.compare(before, before.replace(old, new, 1))
                self.assertEqual((code, data["differences"][0]["kind"]), (1, "link_target"))
        code, data = self.compare("Open https://x.test/a.", "Open https://x.test/a!")
        self.assertEqual(code, 0, data)

    def test_invalid_input_exits_two(self):
        before = self.write("before.md", "text")
        result = self.run_tool("validate_preservation.py", "--before", before, "--after", self.root / "missing.md")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
