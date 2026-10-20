"""Keep numbered runbook prose editable without losing genuine footnotes."""

from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/humanize-korean/scripts"
sys.path.insert(0, str(SCRIPTS))

from checks import check_footnotes, extract_inline_markers  # noqa: E402
from prepare_monolith_input import compute_chunk_spans  # noqa: E402


class KoreanFootnoteTests(unittest.TestCase):
    def test_unreferenced_numbered_steps_remain_editable_chunks(self):
        for prefix in ("{n})", "[{n}]"):
            with self.subTest(prefix=prefix):
                text = (
                    f"{prefix.format(n=1)} 설정 확인 작업을 수행합니다.\n"
                    f"{prefix.format(n=2)} 서버 재시작 작업을 수행합니다.\n"
                )
                spans, _ = compute_chunk_spans(text)
                self.assertTrue(spans)
                self.assertFalse(any(span["passthrough"] for span in spans))
                self.assertEqual(
                    "".join(text[span["start"]:span["end"]] for span in spans),
                    text,
                )

    def test_editing_numbered_steps_does_not_change_footnotes(self):
        for prefix in ("{n})", "[{n}]"):
            with self.subTest(prefix=prefix):
                before = (
                    f"{prefix.format(n=1)} 설정 확인 작업을 수행합니다.\n"
                    f"{prefix.format(n=2)} 서버를 재시작합니다.\n"
                )
                after = before.replace("설정 확인 작업을 수행합니다", "설정을 확인합니다")
                self.assertEqual(check_footnotes(before, after), [])

    def test_referenced_definition_stays_passthrough_and_protected(self):
        text = "재시도 정책은 운영 문서를 따릅니다.1)\n\n1) 운영 정책, 2026.\n"
        spans, _ = compute_chunk_spans(text)
        self.assertFalse(spans[0]["passthrough"])
        self.assertTrue(spans[-1]["passthrough"])
        self.assertEqual(text[spans[-1]["start"]:], "1) 운영 정책, 2026.\n")
        changed = text.replace("운영 정책,", "배포 정책,")
        self.assertIn("footnote_def", {f.code for f in check_footnotes(text, changed)})
        removed = text[:text.rfind("1) 운영 정책")]
        self.assertIn("footnote_def", {f.code for f in check_footnotes(text, removed)})

    def test_footnote_reference_inside_numbered_step_is_preserved(self):
        before = "1) 설정 확인 작업을 수행합니다.2)\n\n2) 운영 정책, 2026.\n"
        after = before.replace("설정 확인 작업을 수행합니다", "설정을 확인합니다")
        spans, _ = compute_chunk_spans(before)
        self.assertFalse(spans[0]["passthrough"])
        self.assertTrue(spans[-1]["passthrough"])
        self.assertEqual(check_footnotes(before, after), [])
        changed = after.replace("운영 정책,", "배포 정책,")
        self.assertIn("footnote_def", {f.code for f in check_footnotes(before, changed)})

    def test_bracketed_reference_protects_only_its_trailing_definition(self):
        text = "운영 문서를 참고합니다 [2].\n\n1) 설정을 확인합니다.\n[2] 운영 정책.\n"
        spans, _ = compute_chunk_spans(text)
        self.assertFalse(spans[0]["passthrough"])
        self.assertEqual(text[spans[-1]["start"]:], "[2] 운영 정책.\n")
        self.assertTrue(spans[-1]["passthrough"])
        self.assertEqual(check_footnotes(text, text), [])
        for after in (
            text.replace("운영 정책.", "배포 정책."),
            text.replace("[2] 운영 정책.\n", ""),
        ):
            with self.subTest(after=after):
                self.assertIn(
                    "footnote_def", {f.code for f in check_footnotes(text, after)}
                )

    def test_bracket_marker_deletion_and_movement_are_detected(self):
        before = "요청은 500건이었다[2]. 다른 요청은 900건이었다.\n\n[2] 운영 정책.\n"
        missing = before.replace("이었다[2]", "이었다", 1)
        self.assertIn(
            "footnote_count", {f.code for f in check_footnotes(before, missing)}
        )
        moved = missing.replace("900건이었다.", "900건이었다[2].")
        self.assertIn(
            "footnote_anchor", {f.code for f in check_footnotes(before, moved)}
        )

    def test_markdown_links_and_code_do_not_protect_numbered_prose(self):
        examples = (
            "[2](https://example.com)",
            "[2][policy]",
            "[policy][2]",
            r"\[2]",
            "`[2]`",
            "``[2] ` literal``",
            "```markdown\n참고[2]\n```",
            "~~~markdown\n참고[2]\n~~~",
            "    참고[2]\n",
            "<!-- 참고[2] -->",
        )
        for example in examples:
            with self.subTest(example=example):
                before = example + "\n\n[2] 설정 확인 작업을 수행합니다.\n"
                after = before.replace("설정 확인 작업을 수행합니다", "설정을 확인합니다")
                self.assertEqual(extract_inline_markers(before), [])
                self.assertEqual(check_footnotes(before, after), [])
                spans, _ = compute_chunk_spans(before)
                self.assertFalse(any(span["passthrough"] for span in spans))

    def test_citation_inside_bracket_numbered_procedure_is_protected(self):
        before = "[1] 설정을 확인합니다[2].\n\n[2] 운영 정책.\n"
        self.assertEqual([n for n, _ in extract_inline_markers(before)], ["2"])
        spans, _ = compute_chunk_spans(before)
        self.assertTrue(spans[-1]["passthrough"])
        after = before.replace("운영 정책.", "배포 정책.")
        self.assertIn("footnote_def", {f.code for f in check_footnotes(before, after)})


if __name__ == "__main__":
    unittest.main()
