#!/usr/bin/env python3
"""Render self-contained Fluent Languages skills from shared source fragments."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PLUGIN_ROOT / "sources"
LANGUAGE_SOURCE_ROOT = SOURCE_ROOT / "languages"
INCLUDE_PATTERN = re.compile(r"^\{\{ include: (?P<path>[^{}]+) \}\}$", re.MULTILINE)
UNRESOLVED_INCLUDE_PATTERN = re.compile(
    r"\{\{[^{}\n]*\binclude\b[^{}\n]*\}\}", re.IGNORECASE
)


def _inside_source_root(path: Path) -> bool:
    try:
        path.relative_to(SOURCE_ROOT.resolve())
    except ValueError:
        return False
    return True


def render(source: Path, stack: tuple[Path, ...] = ()) -> str:
    source = source.resolve()
    if not _inside_source_root(source):
        raise ValueError(f"include escapes sources directory: {source}")
    if source in stack:
        chain = " -> ".join(str(path) for path in (*stack, source))
        raise ValueError(f"cyclic include: {chain}")

    text = source.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        include = (source.parent / match.group("path")).resolve()
        return render(include, (*stack, source)).rstrip("\n")

    rendered = INCLUDE_PATTERN.sub(replace, text)
    unresolved = UNRESOLVED_INCLUDE_PATTERN.search(rendered)
    if unresolved:
        raise ValueError(f"unresolved include in {source}: {unresolved.group(0)}")
    return rendered.rstrip("\n") + "\n"


def targets() -> list[tuple[Path, Path]]:
    sources = sorted(LANGUAGE_SOURCE_ROOT.glob("*.md"))
    if not sources:
        raise ValueError(f"no language sources found in {LANGUAGE_SOURCE_ROOT}")
    return [
        (source, PLUGIN_ROOT / "skills" / f"fluent-{source.stem}" / "SKILL.md")
        for source in sources
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render Fluent Languages SKILL.md files from sources."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when a generated skill differs from its sources",
    )
    args = parser.parse_args()

    stale: list[Path] = []
    for source, target in targets():
        rendered = render(source)
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == rendered:
            continue
        if args.check:
            stale.append(target)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(f"rendered {target.relative_to(PLUGIN_ROOT)}")

    if stale:
        for target in stale:
            print(
                f"stale generated skill: {target.relative_to(PLUGIN_ROOT)}",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
