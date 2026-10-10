#!/usr/bin/env python3
"""Compare English voice markers in UTF-8 texts without modifying them.

CLI: voice_profile.py --before PATH --after PATH [--sample PATH]
JSON to stdout; exit 0 on success, 2 for usage/read/encoding errors.
Counts are lexical observations, not editing instructions or authorship scores.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import statistics


WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
CONTRACTION = re.compile(r"(?:.+n't|(?:i|you|he|she|it|we|they|that|there|here|what|who|where|when|why|how)'(?:m|re|s|ve|d|ll)|let's)$")
PERSON = {
    "first": {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"},
    "second": {"you", "your", "yours", "yourself", "yourselves"},
    "third": {"he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves"},
}
HEDGES = re.compile(r"\b(?:i\s+think|probably|sort\s+of|maybe)\b", re.IGNORECASE)
PUNCTUATION = {"parentheses": "()", "colons": ":", "semicolons": ";", "em_dashes": "—", "en_dashes": "–", "hyphens": "-", "questions": "?", "exclamations": "!", "commas": ",", "full_stops": "."}


def rate(count, total):
    return 100 * count / total if total else 0.0


def profile(text):
    words = [word.lower().replace("’", "'") for word in WORD.findall(text)]
    # Blank lines and terminal punctuation delimit lexical sentence spans.
    sentences = [WORD.findall(part) for part in re.split(r"[.!?]+(?:[\"'’”)]*)(?:\s+|$)|\n\s*\n", text)]
    lengths = [len(sentence) for sentence in sentences if sentence]
    count = len(words)
    bases = [word.split("'")[0] for word in words]
    contractions = sum(bool(CONTRACTION.fullmatch(word)) for word in words)
    hedges = len(HEDGES.findall(text))
    person = {kind: sum(word in pronouns for word in bases) for kind, pronouns in PERSON.items()}
    punctuation = {kind: sum(text.count(char) for char in chars) for kind, chars in PUNCTUATION.items()}
    return {
        "words": count,
        "sentences": len(lengths),
        "sentence_lengths": lengths,
        "median_sentence_words": statistics.median(lengths) if lengths else 0,
        "sentences_under_8_pct": rate(sum(n < 8 for n in lengths), len(lengths)),
        "sentences_over_30_pct": rate(sum(n > 30 for n in lengths), len(lengths)),
        "mean_word_letters": sum(sum(c.isalpha() for c in word) for word in words) / count if count else 0.0,
        "contractions": {"count": contractions, "per_100_words": rate(contractions, count)},
        "person": {kind: {"count": value, "per_100_words": rate(value, count)} for kind, value in person.items()},
        "hedges": {"count": hedges, "per_100_words": rate(hedges, count)},
        "punctuation": {kind: {"count": value, "per_100_sentences": rate(value, len(lengths))} for kind, value in punctuation.items()},
        "recurring_words": {word: n for word, n in sorted(Counter(words).items()) if n >= 3},
    }


def differences(before, after):
    result = {}
    for key, value in before.items():
        if key == "recurring_words":
            continue
        other = after[key]
        if isinstance(value, dict):
            result[key] = differences(value, other)
        elif isinstance(value, (int, float)):
            result[key] = {"delta": other - value, "relative_change": (other - value) / value if value else None}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--sample", type=Path)
    args = parser.parse_args()
    try:
        profiles = {name: profile(path.read_bytes().decode("utf-8")) for name, path in vars(args).items() if path is not None}
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"voice_profile: {error}\n")
    result = {"schema_version": 1, "rules": "english-lexical-v1", "profiles": profiles,
              "after_minus_before": differences(profiles["before"], profiles["after"])}
    if "sample" in profiles:
        result["before_minus_sample"] = differences(profiles["sample"], profiles["before"])
        result["after_minus_sample"] = differences(profiles["sample"], profiles["after"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
