#!/usr/bin/env python3
"""lint JSON と対象文書から自然度の機械ベース・調整範囲・バンドを計算する。

使用例: score.py lint.json --file document.md [--mode full --adjustment -5]
exp: --mode exp --semantic-json semantic.json を指定する。
stdout は JSON。終了コードは判定結果（短すぎる場合も含む）で 0、
入力ファイル・JSON のエラーで 1、引数・モード・調整範囲のエラーで 2。
読み取り専用。読解負荷・baseline の解消済み finding は採点しない。
"""

import argparse
import json
import math
from pathlib import Path
import sys


WEIGHTS = {"critical": 8, "warn": 4, "info": 0.5}
BANDS = ((90, "自然"), (70, "軽微"), (50, "要修正"), (0, "濃厚"))


def read_findings(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        raise ValueError(f"{path}: findings 配列が必要です")
    for finding in data["findings"]:
        if (not isinstance(finding, dict)
                or not isinstance(finding.get("severity"), str)
                or finding["severity"] not in WEIGHTS):
            raise ValueError(f"{path}: severity は critical・warn・info のいずれかです")
    return data["findings"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lint_json", type=Path, help="lint.py --json の出力ファイル")
    parser.add_argument("--file", required=True, type=Path, help="同じ lint の対象文書（UTF-8）")
    parser.add_argument("--mode", choices=("quick", "full", "exp"), default="quick")
    parser.add_argument("--adjustment", type=float, default=0, help="レビューによる調整点")
    parser.add_argument("--semantic-json", type=Path, help="exp 用の semantic.py --json 出力")
    args = parser.parse_args()
    adjustment_limit = 0 if args.mode == "quick" else 15
    if not math.isfinite(args.adjustment) or abs(args.adjustment) > adjustment_limit:
        parser.error(f"{args.mode} の --adjustment は ±{adjustment_limit} の範囲で指定します")
    if (args.mode == "exp") != (args.semantic_json is not None):
        parser.error("--semantic-json は exp のときだけ必須です")

    try:
        characters = len(args.file.read_text(encoding="utf-8"))
        findings = read_findings(args.lint_json)
        counts = dict.fromkeys(WEIGHTS, 0)
        for finding in findings:
            counts[finding["severity"]] += 1
        if args.semantic_json is not None:
            for finding in read_findings(args.semantic_json):
                if finding.get("category") == "semantic_topic_flatness":
                    counts[finding["severity"]] += 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    too_short = characters < 100
    mechanical = score = band = None
    if not too_short:
        penalty = sum(counts[key] * weight for key, weight in WEIGHTS.items())
        mechanical = max(100 - penalty * (1000 / max(characters, 1000)), 20)
        score = min(max(mechanical + args.adjustment, 0), 100)
        band = next(label for minimum, label in BANDS if score >= minimum)
    print(json.dumps({
        "schema_version": 1,
        "status": "too-short" if too_short else "scored",
        "mode": args.mode,
        "characters": characters,
        "counts": counts,
        "mechanical_score": mechanical,
        "adjustment_range": [-adjustment_limit, adjustment_limit],
        "adjustment": None if too_short else args.adjustment,
        "score": score,
        "band": band,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
