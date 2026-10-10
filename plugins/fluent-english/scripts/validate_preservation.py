#!/usr/bin/env python3
"""Compare protected Markdown strings without changing either UTF-8 file.

CLI: validate_preservation.py --before PATH --after PATH
JSON includes ordered protected spans and differences with 1-based lines.
Exit 0: extracted strings match; 1: differences; 2: usage/read/encoding error.
This lexical check covers frontmatter, fenced/indented/inline code, blockquotes,
paired inline quotes, Markdown link/image destinations, reference labels,
angle-bracket autolinks, and bare http(s)/www URLs.
A match does not prove semantic preservation or cover arbitrary HTML/MDX.
"""

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re


KINDS = ("frontmatter", "code", "quote", "link_target")


def escaped(text, index):
    start = index
    while start and text[start - 1] == "\\":
        start -= 1
    return (index - start) % 2 == 1


def indent(line):
    """Return leading whitespace width with tabs advancing to the next multiple of 4."""
    width = 0
    for char in line:
        if char == " ":
            width += 1
        elif char == "\t":
            width += 4 - width % 4
        else:
            break
    return width


def extract(text):
    spans = {kind: [] for kind in KINDS}
    masked = list(text)

    def add(kind, start, end):
        spans[kind].append({"text": text[start:end], "line": text.count("\n", 0, start) + 1, "column": start - text.rfind("\n", 0, start)})
        masked[start:end] = ["\n" if char == "\n" else " " for char in text[start:end]]

    lines = text.splitlines(keepends=True)
    offsets = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    i = 0
    if lines and lines[0].strip("\ufeff\r\n") == "---":
        i = 1
        while i < len(lines) and lines[i].strip() not in ("---", "..."):
            i += 1
        i = min(i + 1, len(lines))
        add("frontmatter", 0, offsets[i] if i < len(lines) else len(text))
    # Indented code needs 4 columns past the enclosing list item's content and
    # cannot interrupt a paragraph, so list continuations stay editable prose.
    items = []
    paragraph = False
    while i < len(lines):
        start = i
        line = lines[i]
        if not line.strip():
            paragraph = False
            i += 1
            continue
        width = indent(line)
        stripped = line.lstrip(" \t")
        marker = re.match(r"([-+*]|\d{1,9}[.)])(?:( {1,4}(?=\S)| (?= {4}))|[ \t]*$)", stripped)
        interrupts = re.match(r"#{1,6}(?:[ \t]|$)|`{3,}|~{3,}|>", stripped)
        if marker or not paragraph or interrupts:
            while items and width < items[-1]:
                items.pop()
        base = items[-1] if items else 0
        # A list item can open with a fence or blockquote; re-read its content at the item's column.
        if marker and marker[2] and width - base <= 3 and re.match(r"`{3,}|~{3,}|>", stripped[len(marker[0]):]):
            items.append(width + len(marker[1]) + len(marker[2]))
            width = base = items[-1]
            stripped = stripped[len(marker[0]):]
        fence = re.match(r"(`{3,}|~{3,})", stripped) if width - base <= 3 else None
        if not paragraph and width - base >= 4:
            i += 1
            while i < len(lines) and (not lines[i].strip() or indent(lines[i]) - base >= 4):
                i += 1
            kind = "code"
        elif fence:
            mark = fence[1]
            i += 1
            while i < len(lines) and not (indent(lines[i]) - base <= 3 and re.fullmatch(re.escape(mark[0]) + "{" + str(len(mark)) + r",}[ \t]*\r?\n?", lines[i].lstrip(" \t"))):
                i += 1
            i = min(i + 1, len(lines))
            kind = "code"
        elif width - base <= 3 and stripped.startswith(">"):
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            kind = "quote"
        else:
            if marker:
                items.append(width + len(marker[1]) + (len(marker[2]) if marker[2] else 1))
            paragraph = not re.match(r"#{1,6}(?:[ \t]|$)", stripped)
            i += 1
            continue
        paragraph = False
        add(kind, offsets[start], offsets[i] if i < len(lines) else len(text))

    # Backtick runs close only with a run of the same length.
    source = "".join(masked)
    cursor = 0
    for match in re.finditer(r"`+", source):
        if match.start() < cursor or escaped(source, match.start()):
            continue
        closer = re.search(r"(?<!`)" + re.escape(match[0]) + r"(?!`)", source[match.end():])
        if closer:
            cursor = match.end() + closer.end()
            add("code", match.start(), cursor)

    source = "".join(masked)
    # Reference definitions retain the label, destination, and optional title.
    for match in re.finditer(r"(?m)^ {0,3}\[(?!\^)[^\]\n]+\]:[^\n]*(?:\n[ \t]+[\"'(][^\n]*)?", source):
        add("link_target", match.start(), match.end())
    source = "".join(masked)
    for match in re.finditer(r"\]\(", source):
        if escaped(source, match.start()):
            continue
        start = match.end()
        depth = 1
        j = start
        while j < len(source) and depth:
            if not escaped(source, j):
                if source[j] == "(":
                    depth += 1
                elif source[j] == ")":
                    depth -= 1
            j += 1
        if depth == 0:
            add("link_target", start, j - 1)
    source = "".join(masked)
    for match in re.finditer(r"\[([^\]\n]+)\]\[([^\]\n]*)\]", source):
        # A collapsed reference uses its visible label as the destination ID.
        group = 2 if match[2] else 1
        add("link_target", match.start(group), match.end(group))
    source = "".join(masked)
    for match in re.finditer(r"<(?:[A-Za-z][A-Za-z0-9+.-]*:[^<>\s]+|[^<>\s@]+@[^<>\s@]+)>", source):
        add("link_target", match.start(), match.end())
    source = "".join(masked)
    # GFM renders bare http(s) and www URLs as links; trailing punctuation stays prose.
    for match in re.finditer(r"(?<![\w/])(?:https?://|www\.)[^\s<>]*[^\s<>.,:;!?\"')\]]", source):
        add("link_target", match.start(), match.end())
    source = "".join(masked)
    # Shortcut reference labels resolve through a definition in this document.
    labels = {m[1].casefold() for m in re.finditer(r"(?m)^ {0,3}\[(?!\^)([^\]\n]+)\]:", text)}
    for match in re.finditer(r"\[([^\]\n]+)\](?![\[(])", source):
        if match[1].casefold() in labels:
            add("link_target", match.start(1), match.end(1))
    source = "".join(masked)
    for match in re.finditer(r'''(?<![\w\\])(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\]|(?<=\w)'(?=\w))*'|“[^”]*”|‘(?:[^’]|(?<=\w)’(?=\w))*’)(?!\w)''', source):
        add("quote", match.start(), match.end())
    # Sort by source location, including multiple spans on the same line.
    for kind in spans:
        spans[kind].sort(key=lambda span: (span["line"], span["column"]))
    return spans


def compare(before, after):
    differences = []
    for kind in KINDS:
        old, new = before[kind], after[kind]
        matcher = SequenceMatcher(a=[span["text"] for span in old], b=[span["text"] for span in new], autojunk=False)
        for operation, a, b, c, d in matcher.get_opcodes():
            if operation != "equal":
                differences.append({"kind": kind, "operation": operation, "before": old[a:b], "after": new[c:d]})
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    args = parser.parse_args()
    try:
        before = extract(args.before.read_bytes().decode("utf-8"))
        after = extract(args.after.read_bytes().decode("utf-8"))
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"validate_preservation: {error}\n")
    differences = compare(before, after)
    print(json.dumps({"schema_version": 1, "status": "changed" if differences else "matched",
                      "counts": {"before": {k: len(v) for k, v in before.items()}, "after": {k: len(v) for k, v in after.items()}},
                      "differences": differences}, ensure_ascii=False, indent=2))
    return int(bool(differences))


if __name__ == "__main__":
    raise SystemExit(main())
