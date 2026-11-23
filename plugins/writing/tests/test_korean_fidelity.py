"""Exercise signed values, attributed quotes, and generated-summary boundaries."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/humanize-korean/scripts"
sys.path.insert(0, str(SCRIPTS))

from checks import (  # noqa: E402
    check_numbers,
    check_quotes,
    dropped_numbers,
    run_checks,
    split_summary_block,
    strip_summary_block,
)
from restore_modality import find_losses, restore  # noqa: E402


SUMMARY = """<!-- HUMANIZE-SUMMARY
original_characters: 999
final_body_characters: 888
change_rate: pending_gate
grade: pending_review
self_check_passed: 6/6
categories: []
highlights: []
residual_findings: []
-->
"""


class KoreanNumberTests(unittest.TestCase):
    def test_signed_value_changes_are_reported(self):
        for before, after in (
            ("기온은 -5°C이다.", "기온은 5°C이다."),
            ("변동은 +12.5%이다.", "변동은 -12.5%이다."),
            ("잔액은 −1만 원이다.", "잔액은 10,000원이다."),
        ):
            with self.subTest(before=before, after=after):
                self.assertIn("number_injected", {f.code for f in run_checks(before, after)})
                self.assertTrue(dropped_numbers(before, after))

    def test_unchanged_values_and_equivalent_formats_pass(self):
        for before, after in (
            ("기온은 -5°C이다.", "기온은 -5°C이다."),
            ("차이는 −5.00이다.", "차이는 -5이다."),
            ("잔액은 -1만 원이다.", "잔액은 -10,000원이다."),
            ("참가자는 1만 명이다.", "참가자는 10,000명이다."),
            ("길이는 +3.50이다.", "길이는 3.5이다."),
            ("합계는 1.5억 원이다.", "합계는 150,000,000원이다."),
            ("버전은 1.2.3이다.", "버전은 1.2.3이다."),
        ):
            with self.subTest(before=before, after=after):
                self.assertEqual(check_numbers(before, after), [])
                self.assertEqual(dropped_numbers(before, after), [])

    def test_date_and_range_hyphens_are_not_unary_signs(self):
        self.assertEqual(check_numbers("2026-10-20", "2026년 10월 20일"), [])
        self.assertEqual(check_numbers("범위는 5-10이다.", "범위는 5에서 10이다."), [])

    def test_dropped_signed_values_keep_string_report_shape(self):
        self.assertEqual(dropped_numbers("값은 -5와 7이다.", "값은 7이다."), ["-5"])


class KoreanQuoteTests(unittest.TestCase):
    def test_all_supported_closers_preserve_attributed_quotes(self):
        for opening, closing in (("\"", "\""), ("“", "”"), ("「", "」"), ("『", "』")):
            with self.subTest(opening=opening):
                before = f"연구진은 {opening}서비스가 안정적으로 동작한다{closing}라고 보고하였다."
                after = before.replace("안정적으로", "불안정하게")
                self.assertEqual(check_quotes(before, before), [])
                self.assertIn("quote_altered", {f.code for f in check_quotes(before, after)})

    def test_unattributed_rhetorical_quotes_remain_editable(self):
        for opening, closing in (("\"", "\""), ("“", "”"), ("「", "」"), ("『", "』")):
            with self.subTest(opening=opening):
                before = f"오늘의 질문은 {opening}우리는 무엇을 바꿀 수 있을까{closing}이다."
                after = before.replace("무엇을 바꿀 수 있을까", "무엇부터 바꿀까")
                self.assertEqual(check_quotes(before, after), [])


class KoreanSummaryTests(unittest.TestCase):
    def test_complete_terminal_metadata_is_excluded_and_preserved_verbatim(self):
        body = "요청 제한은 500건이다.\n\n"
        for summary in (SUMMARY, SUMMARY.replace("\n", "\r\n") + " \t\r\n"):
            with self.subTest(summary=summary):
                text = body + summary
                self.assertEqual(split_summary_block(text), (body, summary))
                self.assertEqual(strip_summary_block(text), body.strip())
                self.assertEqual(run_checks(body, text), [])

    def test_indented_review_details_are_metadata(self):
        summary = SUMMARY.replace("highlights: []", "highlights:\n  - before: 하였다\n    after: 했다")
        self.assertEqual(strip_summary_block("본문이다.\n\n" + summary), "본문이다.")

    def test_source_markers_and_malformed_comments_are_not_metadata(self):
        examples = (
            "본문의 <!-- HUMANIZE-SUMMARY --> 예제이다.",
            "`<!-- HUMANIZE-SUMMARY -->`",
            "설명: " + SUMMARY,
            "```html\n" + SUMMARY + "```\n",
            "~~~html\n" + SUMMARY + "~~~\n",
            "```html\n" + SUMMARY,
            "    " + SUMMARY.replace("\n", "\n    "),
            SUMMARY + "이 뒤에도 본문이 있다.\n",
            SUMMARY.replace("-->\n", ""),
            SUMMARY.replace("grade: pending_review\n", ""),
            SUMMARY.replace("original_characters: 999", "original_characters: unknown"),
            SUMMARY.replace("highlights: []", "highlights: -->\n  숨겨진 본문"),
            "<!-- outer comment\n" + SUMMARY,
        )
        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(split_summary_block(text), (text, ""))
                self.assertEqual(strip_summary_block(text), text.strip())

    def test_earlier_examples_do_not_hide_changed_tail(self):
        for example in (
            "<!-- HUMANIZE-SUMMARY -->\n",
            "```html\n<!-- HUMANIZE-SUMMARY -->\n```\n",
            "`<!-- HUMANIZE-SUMMARY -->`\n",
            SUMMARY,
        ):
            with self.subTest(example=example):
                before = example + "\n요청 제한은 500건이다.\n"
                after = before.replace("500", "900") + "\n" + SUMMARY
                self.assertIn("number_injected", {f.code for f in run_checks(before, after)})
                self.assertIn("900건", strip_summary_block(after))

    def run_cli(self, script, before, after, *options):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "before.md").write_text(before, encoding="utf-8")
            (root / "after.md").write_text(after, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPTS / script), "--before", "before.md",
                 "--after", "after.md", *options],
                cwd=root, text=True, capture_output=True, check=False,
            )

    def test_gate_clis_include_changed_tail_after_fenced_marker(self):
        before = "자료 형식이다.\n\n```html\n<!-- HUMANIZE-SUMMARY -->\n```\n\n요청 제한은 500건이다.\n"
        after = before.replace("500", "900")
        gate = self.run_cli("verify_gates.py", before, after, "--json")
        self.assertEqual(gate.returncode, 1, gate.stdout + gate.stderr)
        report = json.loads(gate.stdout[gate.stdout.index("\n{") + 1:])
        self.assertGreater(report["change_rate"]["rate"], 0)
        self.assertIn("number_injected", {f["code"] for f in report["golden"]})
        rate = self.run_cli("verify_change_rate.py", before, after)
        self.assertEqual(rate.returncode, 0, rate.stdout + rate.stderr)
        self.assertNotIn("change_rate: 0.0%", rate.stdout)

    def test_gate_clis_exclude_only_real_trailing_metadata(self):
        before = "요청 제한은 500건이다.\n"
        after = before + "\n" + SUMMARY
        gate = self.run_cli("verify_gates.py", before, after, "--json")
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
        report = json.loads(gate.stdout[gate.stdout.index("\n{") + 1:])
        self.assertEqual(report["change_rate"]["rate"], 0)
        self.assertEqual(report["golden"], [])
        rate = self.run_cli("verify_change_rate.py", before, after)
        self.assertEqual(rate.returncode, 0, rate.stdout + rate.stderr)
        self.assertIn("change_rate: 0.0%", rate.stdout)

    def test_modality_tail_is_not_hidden_and_summary_is_not_rewritten(self):
        example = "```html\n<!-- HUMANIZE-SUMMARY -->\n```\n\n"
        sentence = "담당자는 배포 전에 서비스 상태를 반드시 확인해야 한다."
        before = example + sentence
        after = example + sentence.replace("확인해야 한다", "확인한다")
        summary = SUMMARY.replace("highlights: []", f"highlights: {sentence}")
        self.assertTrue(find_losses(before, after + "\n\n" + summary))
        result, restored, skipped = restore(before, after + "\n\n" + summary)
        self.assertTrue(restored)
        self.assertEqual(skipped, [])
        self.assertTrue(result.startswith(example))
        self.assertIn(sentence, split_summary_block(result)[0])
        self.assertTrue(result.endswith(summary))


if __name__ == "__main__":
    unittest.main()
