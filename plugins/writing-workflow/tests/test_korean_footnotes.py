"""Keep numbered runbook prose editable without losing genuine footnotes."""

from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/humanize-korean/scripts"
sys.path.insert(0, str(SCRIPTS))

from checks import check_footnotes  # noqa: E402
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
        before = "1) 설정 확인 작업을 수행합니다.\n2) 서버를 재시작합니다.\n"
        after = "1) 설정을 확인합니다.\n2) 서버를 재시작합니다.\n"
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


if __name__ == "__main__":
    unittest.main()
