"""Exercise protected Markdown and actual finding transitions in Japanese lint."""

from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/natural-japanese/scripts"
sys.path.insert(0, str(SCRIPTS))

import lint  # noqa: E402


def findings_for(text, category):
    findings, _ = lint.run_lint(text, genre="tech", experimental=True)
    return [finding for finding in findings if finding.category == category]


def transition(before, after, category):
    baseline = [finding.to_dict() for finding in findings_for(before, category)]
    current = findings_for(after, category)
    return lint.compute_baseline_diff(current, {"findings": baseline})


class JapaneseStructureTests(unittest.TestCase):
    def test_fenced_samples_do_not_create_structural_findings(self):
        sample = (
            "**赤** **青** **白**\n## まとめ\n"
            "ステップ1 ステップ2 ステップ3\n"
            + "- 項目\n" * 12
            + "\U0001f600\U0001f600\U0001f600\n"
        )
        for opener, closer in (("```markdown", "```"), ("~~~~", "~~~~")):
            with self.subTest(opener=opener):
                findings, stats = lint.run_lint(
                    "説明です。\n" + opener + "\n" + sample + closer + "\n",
                    genre="tech", experimental=True,
                )
                structural = stats["structural"]
                for field in ("bold_span_count", "bullet_line_count",
                              "boilerplate_heading_count", "numbered_phase_hit_count",
                              "emoji_symbol_count"):
                    self.assertEqual(structural[field], 0, field)
                self.assertFalse(any(f.category.startswith("high_bold") for f in findings))

    def test_shorter_or_other_fence_does_not_end_protected_example(self):
        text = "````markdown\n```\n~~~\n**赤** **青** **白**\n````\n説明です。\n"
        self.assertEqual(findings_for(text, "high_bold_density"), [])
        unclosed = "```markdown\n**赤** **青** **白**\n"
        self.assertEqual(findings_for(unclosed, "high_bold_density"), [])

    def test_comment_delimiter_inside_fence_does_not_hide_following_prose(self):
        text = "```html\n<!-- unfinished example\n```\n**赤** **青** **白**\n"
        findings = findings_for(text, "high_bold_density")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 4)

    def test_fence_inside_comment_does_not_hide_following_prose(self):
        text = "<!--\n```\n-->\n**赤** **青** **白**\n"
        findings = findings_for(text, "high_bold_density")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 4)

    def test_large_protected_example_does_not_dilute_live_bold_density(self):
        text = "**赤** **青** **白**\n\n```text\n" + "例示コード\n" * 4000 + "```\n"
        findings, stats = lint.run_lint(text, genre="tech")
        self.assertEqual(stats["structural"]["bold_span_count"], 3)
        bold = [f for f in findings if f.category == "high_bold_density"]
        self.assertEqual(len(bold), 1)
        self.assertEqual(bold[0].line, 1)


class JapaneseBaselineTests(unittest.TestCase):
    def test_changing_aggregate_measurements_remain_persisting(self):
        cases = [
            ("high_bold_density", "**赤** **青** **白** **黒**\n", "**赤** **青** **白**\n"),
            ("high_bullet_ratio", "- 項目です。\n" * 12, "- 項目です。\n" * 11),
            ("numbered_phase_structure", "ステップ1 ステップ2 ステップ3 ステップ4\n", "ステップ1 ステップ2 ステップ3\n"),
            ("high_emoji_symbol_density", "説明です。\U0001f600" * 4, "説明です。\U0001f600" * 3),
        ]
        for category, before, after in cases:
            with self.subTest(category=category):
                resolved, summary = transition(before, after, category)
                self.assertEqual(resolved, [])
                self.assertEqual(summary, {"resolved": 0, "new": 0, "persisting": 1})

    def test_nominal_ending_aggregate_survives_changed_sentence_count(self):
        sentence = "この設計では、利用者が設定を確認してから処理を実行します。結果を確認してから次の処理に進みます。\n"
        resolved, summary = transition(sentence * 80, sentence * 79, "nominal_ending")
        self.assertEqual(resolved, [])
        self.assertEqual(summary, {"resolved": 0, "new": 0, "persisting": 1})

    def test_aggregate_can_resolve_and_reappear(self):
        three = "**赤** **青** **白**\n"
        two = "**赤** **青**\n"
        _, resolved = transition(three, two, "high_bold_density")
        self.assertEqual(resolved, {"resolved": 1, "new": 0, "persisting": 0})
        _, appeared = transition(two, three, "high_bold_density")
        self.assertEqual(appeared, {"resolved": 0, "new": 1, "persisting": 0})

    def test_distinct_local_headings_do_not_collapse_to_category_identity(self):
        before = "## まとめ\n説明です。\n\n## おわりに\n別の説明です。\n"
        after = "説明です。\n\n## おわりに\n別の説明です。\n"
        resolved, summary = transition(before, after, "boilerplate_heading")
        self.assertEqual(summary, {"resolved": 1, "new": 0, "persisting": 1})
        self.assertEqual([finding["excerpt"] for finding in resolved], ["## まとめ"])


if __name__ == "__main__":
    unittest.main()
