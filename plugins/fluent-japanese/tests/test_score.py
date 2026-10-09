"""自然度の算式・境界・入力エラーを CLI 経由で固定する。"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/fluent-japanese/scripts/score.py"


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.document = self.root / "文書.md"
        self.document.write_text("あ" * 1000, encoding="utf-8")
        self.lint = self.root / "lint.json"
        self.save_lint([])

    def save_lint(self, severities, **extra):
        data = {"file": str(self.document), "stats": {},
                "findings": [{"severity": severity, "category": "translationese"}
                             for severity in severities], **extra}
        self.lint.write_text(json.dumps(data), encoding="utf-8")

    def run_score(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.lint),
                               "--file", str(self.document), *args],
                              cwd=self.root, capture_output=True, text=True)

    def score(self, *args):
        result = self.run_score(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_severity_weights_and_ignored_lanes(self):
        self.save_lint(["critical", "warn", "info"],
                       reading_load={"findings": [{"severity": "critical"}]},
                       baseline={"resolved": [{"severity": "critical"}]},
                       stats={"total_findings": 999})
        data = self.score()
        self.assertEqual(data["counts"], {"critical": 1, "warn": 1, "info": 1})
        self.assertEqual(data["mechanical_score"], 87.5)
        self.assertEqual(data["score"], 87.5)
        self.assertEqual(data["band"], "軽微")
        self.assertEqual(data["adjustment_range"], [0, 0])

    def test_character_normalization_includes_markdown_and_newlines(self):
        text = "# 見出し\n" + "あ" * 1994
        self.document.write_text(text, encoding="utf-8")
        self.save_lint(["critical", "warn", "info"])
        data = self.score()
        self.assertEqual(data["characters"], len(text))
        self.assertEqual(data["mechanical_score"], 100 - 12.5 * 1000 / len(text))

    def test_short_document_boundary(self):
        self.save_lint(["warn"])
        for length in (0, 99, 100, 999, 1000, 1001):
            with self.subTest(length=length):
                self.document.write_text("あ" * length, encoding="utf-8")
                data = self.score()
                self.assertEqual(data["characters"], length)
                if length < 100:
                    self.assertEqual(data["status"], "too-short")
                    for key in ("mechanical_score", "adjustment", "score", "band"):
                        self.assertIsNone(data[key])
                else:
                    self.assertEqual(data["status"], "scored")
                    self.assertEqual(data["score"], 100 - 4 * 1000 / max(length, 1000))

    def test_band_boundaries_keep_fractional_precision(self):
        for count, expected, band in ((0, 100, "自然"), (20, 90, "自然"),
                                      (21, 89.5, "軽微"), (60, 70, "軽微"),
                                      (61, 69.5, "要修正"), (100, 50, "要修正"),
                                      (101, 49.5, "濃厚")):
            with self.subTest(score=expected):
                self.save_lint(["info"] * count)
                data = self.score()
                self.assertEqual((data["score"], data["band"]), (expected, band))

    def test_mechanical_floor_and_negative_adjustment(self):
        self.save_lint(["critical"] * 100)
        data = self.score("--mode", "full", "--adjustment", "-15")
        self.assertEqual(data["mechanical_score"], 20)
        self.assertEqual(data["score"], 5)
        self.assertEqual(data["adjustment_range"], [-15, 15])
        self.assertEqual(data["adjustment"], -15)

    def test_positive_adjustment_clips_at_100(self):
        data = self.score("--mode", "full", "--adjustment", "15")
        self.assertEqual(data["mechanical_score"], 100)
        self.assertEqual(data["score"], 100)

    def test_exp_counts_only_topic_flatness(self):
        semantic = self.root / "semantic.json"
        semantic.write_text(json.dumps({"findings": [
            {"category": "semantic_topic_flatness", "severity": "warn"},
            {"category": "semantic_repetition_max", "severity": "info"},
        ]}), encoding="utf-8")
        data = self.score("--mode", "exp", "--semantic-json", str(semantic),
                          "--adjustment", "-2.5")
        self.assertEqual(data["counts"]["warn"], 1)
        self.assertEqual(data["mechanical_score"], 96)
        self.assertEqual(data["score"], 93.5)

    def test_invalid_adjustments_and_modes(self):
        for args in (("--adjustment", "1"), ("--mode", "full", "--adjustment", "15.1"),
                     ("--mode", "full", "--adjustment", "-15.1"),
                     ("--mode", "full", "--adjustment", "nan"),
                     ("--mode", "full", "--adjustment", "inf"),
                     ("--mode", "exp"), ("--semantic-json", "semantic.json"),
                     ("--mode", "unknown")):
            with self.subTest(args=args):
                result = self.run_score(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")

    def test_invalid_json_and_findings(self):
        for raw in ("{", "[]", "{}", '{"findings":null}', '{"findings":[null]}',
                    '{"findings":[{}]}', '{"findings":[{"severity":"fatal"}]}',
                    '{"findings":[{"severity":[]}]}'):
            with self.subTest(raw=raw):
                self.lint.write_text(raw, encoding="utf-8")
                result = self.run_score()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("エラー:", result.stderr)

    def test_missing_and_non_utf8_input(self):
        self.document.unlink()
        self.assertEqual(self.run_score().returncode, 1)
        self.document.write_bytes(b"\xff")
        self.assertEqual(self.run_score().returncode, 1)
        self.document.write_text("あ" * 100, encoding="utf-8")
        self.lint.unlink()
        self.assertEqual(self.run_score().returncode, 1)
        self.lint.write_bytes(b"\xff")
        self.assertEqual(self.run_score().returncode, 1)

    def test_invalid_semantic_input(self):
        result = self.run_score("--mode", "exp", "--semantic-json", "missing.json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
