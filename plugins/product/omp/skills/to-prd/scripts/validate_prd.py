#!/usr/bin/env python3
"""PRD 파일의 구조를 읽기 전용으로 검사하고 JSON으로 출력한다.

검사 항목:
  metadata            frontmatter 필수 키, 빈 값, 문자열이 아닌 id·status·workflow_status,
                      status·workflow_status 조합, sources 비어 있음
  duplicate-id        문서 안 REQ/NFR/OPEN/RISK/SUCCESS ID의 중복 정의
                      (정의: `### REQ-001: …` 제목, 들여 쓰지 않은 `- REQ-001: …`·`1. REQ-001: …` 목록,
                      첫 열 제목이 `ID`인 표의 행. 들여 쓴 목록의 `- REQ-001: …`은 참조 대상으로만 인정)
  duplicate-document-id  입력과 --existing 문서 사이의 frontmatter id 중복
  undefined-reference 정의되지 않은 내부 ID 참조
  broken-link         상대 링크 대상 파일 없음
  broken-fragment     링크 fragment에 맞는 제목 없음
  placeholder         템플릿 자리표시자, 작성 안내 주석, 빈 필드·표 칸
  outside-allowed-path  --allowed-root 밖의 파일(symlink는 해석한 경로로 판정)

출력: stdout JSON {schema_version, files[{path, findings[{code, line, message}]}],
      checks{allowed_paths: checked|not-checked, document_ids: checked|inputs-only}, summary{files, findings}}
종료 코드: 0 지적 없음, 1 지적 있음, 2 입력 파일을 읽지 못함·인자 오류.
의미, 근거의 진위, 승인 여부는 판정하지 않는다.
"""

import argparse
import json
from pathlib import Path
import re
import sys


DEFAULT_KEYS = ("id", "title", "status", "workflow_status", "revision", "owners", "sources")
STATUS_PAIRS = {"conditional": "draft", "approved": "stable"}
SCALAR_KEYS = ("id", "status", "workflow_status")
ID = r"(?:REQ|NFR|OPEN|RISK|SUCCESS)-\d+"
ID_RE = re.compile(rf"(?<![\w-]){ID}(?![\w-])", re.ASCII)
HEADING_ID_RE = re.compile(rf"^#+\s+\**({ID})\b", re.ASCII)
LIST_ID_RE = re.compile(rf"^(\s*)(?:[-*+]|\d+[.)])\s+\**({ID})\**\s*[:：]")
TABLE_ID_RE = re.compile(rf"^\|\s*\**({ID})\**\s*\|")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ANGLE_RE = re.compile(r"<([^<>\s](?:[^<>\n]*[^<>\s])?)>")
PLACEHOLDER_TEXT = (
    (re.compile(r"\b[A-Z]+-X{3,}\b"), "template ID"),
    (re.compile(r"\(OPEN ID\)"), "unfilled OPEN ID"),
    (re.compile(r"\bP1 \| P2\b"), "unselected priority choice"),
    (re.compile(r"\[해당하는 [^\]]*\]"), "template field guide"),
)


def slug(text):
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", text.strip().lower()))


def split_frontmatter(lines):
    """frontmatter 줄 목록과 본문 시작 인덱스를 돌려준다. 없으면 (None, 0)."""
    if not lines or lines[0].strip() != "---":
        return None, 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], index + 1
    return None, 0


def parse_frontmatter(lines):
    """`key: value`, `key: [a, b]`, 블록 목록(들여쓰기 없는 목록 포함)만 해석하는 최소 YAML 파서."""
    data, current, block = {}, None, False
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s*-(?:\s+(.*))?$", raw)
        if item and block:
            if not isinstance(data[current], list):
                data[current] = []
            data[current].append((item.group(1) or "").strip())
            continue
        pair = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not pair:
            continue
        key, value = pair.group(1), pair.group(2).strip()
        current, block = key, value == ""
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [part.strip() for part in inner.split(",")] if inner else []
        elif value == "":
            data[key] = ""
        else:
            data[key] = value.strip("\"'")
    return data


def mask_body(lines, start, keep_code=False):
    """코드 블록·HTML 주석을 지운 줄과 주석이 있던 줄 번호를 돌려준다.

    줄 번호와 글자 위치는 유지한다. 주석은 공백으로, 인라인 코드는 빈 값으로 오인되지 않도록
    백틱으로 채운다. keep_code가 True이면 인라인 코드 원문을 남긴다(제목 slug용).
    """
    masked, comments, fenced, in_comment = [], [], False, False
    for number, line in enumerate(lines, 1):
        if number <= start:
            masked.append("")
            continue
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            masked.append("")
            continue
        if fenced:
            masked.append("")
            continue
        code = re.sub(r"`[^`]*`", lambda m: "`" * len(m.group(0)), line)
        chars = list(line if keep_code else code)
        position = 0
        if in_comment:
            comments.append(number)
            end = code.find("-->")
            stop = len(code) if end < 0 else end + 3
            chars[:stop] = " " * stop
            in_comment, position = end < 0, stop
        while not in_comment:
            begin = code.find("<!--", position)
            if begin < 0:
                break
            if not comments or comments[-1] != number:
                comments.append(number)
            end = code.find("-->", begin + 4)
            stop = len(code) if end < 0 else end + 3
            chars[begin:stop] = " " * (stop - begin)
            in_comment, position = end < 0, stop
        masked.append("".join(chars))
    return masked, comments


def has_children(masked, number):
    """줄 number(1부터) 뒤 첫 비어 있지 않은 줄이 더 깊게 들여 쓰여 있으면 True."""
    indent = len(masked[number - 1]) - len(masked[number - 1].lstrip())
    for line in masked[number:]:
        if not line.strip():
            continue
        return len(line) - len(line.lstrip()) > indent
    return False


def headings(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.splitlines()
    _, start = split_frontmatter(lines)
    seen, slugs = {}, set()
    for line in mask_body(lines, start, keep_code=True)[0]:
        match = re.match(r"^#+\s+(.*?)\s*#*\s*$", line)
        if match:
            base = slug(match.group(1))
            count = seen.get(base, 0)
            slugs.add(base if count == 0 else f"{base}-{count}")
            seen[base] = count + 1
    return slugs


def check_metadata(meta, keys, add):
    if meta is None:
        add("metadata", 1, "frontmatter 없음")
        return
    for key in keys:
        if key not in meta:
            add("metadata", 1, f"필수 키 없음: {key}")
        elif key in SCALAR_KEYS and not isinstance(meta[key], str):
            add("metadata", 1, f"값이 문자열이 아님: {key}")
        elif key not in ("owners", "sources") and meta[key] in ("", []):
            add("metadata", 1, f"값이 비어 있음: {key}")
    if "sources" in keys and meta.get("sources") in ("", []):
        add("metadata", 1, "sources가 비어 있음")
    workflow, status = meta.get("workflow_status"), meta.get("status")
    if "workflow_status" in keys and isinstance(workflow, str) and workflow:
        if workflow not in STATUS_PAIRS:
            add("metadata", 1, f"workflow_status 값이 conditional·approved가 아님: {workflow}")
        elif "status" in keys and isinstance(status, str) and status and status != STATUS_PAIRS[workflow]:
            add("metadata", 1, f"workflow_status {workflow}에는 status {STATUS_PAIRS[workflow]}가 필요함: {status}")


def text_placeholders(line, number, add):
    for found in ANGLE_RE.finditer(line):
        inner = found.group(1)
        if re.match(r"^[a-z][a-z0-9+.-]*:", inner) or "@" in inner:
            continue
        if " " in inner or any(ord(char) > 127 for char in inner):
            add("placeholder", number, f"자리표시자: <{inner}>")
    for pattern, label in PLACEHOLDER_TEXT:
        for found in pattern.finditer(line):
            add("placeholder", number, f"{label}: {found.group(0)}")


def check_file(path, keys, add):
    lines = path.read_text(encoding="utf-8").splitlines()
    front, start = split_frontmatter(lines)
    meta = parse_frontmatter(front) if front is not None else None
    check_metadata(meta, keys, add)
    for number in range(2, start):
        text_placeholders(lines[number - 1], number, add)
    masked, comments = mask_body(lines, start)
    for number in comments:
        add("placeholder", number, "작성 안내 주석")

    definitions = {}
    nested = set()
    references = []
    table_header = None
    for number, line in enumerate(masked, 1):
        if number <= start:
            continue
        is_table = line.lstrip().startswith("|")
        if is_table and table_header is None:
            table_header = [cell.strip() for cell in line.strip().strip("|").split("|")]
        elif not is_table:
            table_header = None
        item = LIST_ID_RE.match(line)
        match = HEADING_ID_RE.match(line)
        if match is None and item and item.group(1):
            nested.add(item.group(2))
        elif match is None and item:
            match = item
        elif match is None and is_table and table_header and table_header[0] == "ID":
            match = TABLE_ID_RE.match(line.lstrip())
        if match:
            definitions.setdefault(match.group(match.lastindex), []).append(number)
        for found in ID_RE.finditer(line):
            references.append((found.group(0), number))
        text_placeholders(line, number, add)
        if re.match(r"^\s*[-*]\s*$", line) or (
                re.match(r"^\s*[-*]\s+[^:：|]+[:：]\s*$", line) and not has_children(masked, number)):
            add("placeholder", number, "빈 목록 필드")
        if is_table and not re.match(r"^\s*\|[\s:|-]+\|\s*$", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if any(cell == "" for cell in cells):
                add("placeholder", number, "빈 표 칸")
    for identifier, places in sorted(definitions.items()):
        if len(places) > 1:
            add("duplicate-id", places[1], f"{identifier} 중복 정의: 줄 {', '.join(map(str, places))}")
    for identifier, number in references:
        if identifier not in definitions and identifier not in nested:
            add("undefined-reference", number, f"정의되지 않은 ID: {identifier}")

    own_slugs = headings(path)
    own_path = path.resolve()
    for number, line in enumerate(masked, 1):
        if number <= start:
            continue
        for match in LINK_RE.finditer(line):
            target = match.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("//"):
                continue
            target_path, _, fragment = target.partition("#")
            destination = (path.parent / target_path).resolve() if target_path else own_path
            if target_path and not destination.exists():
                add("broken-link", number, f"대상 없음: {target}")
                continue
            if fragment and destination.is_file() and destination.suffix.lower() == ".md":
                slugs = own_slugs if destination == own_path else headings(destination)
                if slugs is not None and fragment not in slugs:
                    add("broken-fragment", number, f"제목 없음: {target}")
    return meta


def main(argv=None):
    parser = argparse.ArgumentParser(description="PRD 구조 검사(읽기 전용)")
    parser.add_argument("files", nargs="+", type=Path, help="검사할 PRD Markdown 파일")
    parser.add_argument("--allowed-root", action="append", type=Path, default=[],
                        help="쓰기가 허용된 디렉터리. 여러 번 지정 가능. 없으면 경로 검사를 생략한다.")
    parser.add_argument("--existing", action="append", type=Path, default=[],
                        help="frontmatter id 중복을 대조할 기존 PRD 디렉터리. 여러 번 지정 가능.")
    parser.add_argument("--metadata-keys", default=",".join(DEFAULT_KEYS),
                        help="필수 frontmatter 키(쉼표 구분). 저장소 관례가 다를 때 지정한다.")
    args = parser.parse_args(argv)
    keys = tuple(key.strip() for key in args.metadata_keys.split(",") if key.strip())

    for root in args.allowed_root + args.existing:
        if not root.is_dir():
            print(f"not a directory: {root}", file=sys.stderr)
            return 2
    for file in args.files:
        try:
            file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            print(f"cannot read: {file}: {error}", file=sys.stderr)
            return 2

    allowed = [root.resolve() for root in args.allowed_root]
    results, ids = [], {}
    for file in args.files:
        findings = []

        def add(code, line, message, findings=findings):
            findings.append({"code": code, "line": line, "message": message})

        real = file.resolve()
        if allowed and not any(real == root or root in real.parents for root in allowed):
            add("outside-allowed-path", 1, f"허용 경로 밖: {real}")
        meta = check_file(file, keys, add)
        if meta and isinstance(meta.get("id"), str) and meta["id"]:
            ids.setdefault(meta["id"], []).append(real)
        results.append({"path": str(file), "findings": findings})

    inputs = {file.resolve() for file in args.files}
    for root in args.existing:
        for doc in sorted(root.resolve().rglob("*.md")):
            if doc in inputs:
                continue
            try:
                front, _ = split_frontmatter(doc.read_text(encoding="utf-8").splitlines())
            except (OSError, UnicodeDecodeError):
                continue
            meta = parse_frontmatter(front) if front is not None else {}
            if isinstance(meta.get("id"), str) and meta["id"]:
                ids.setdefault(meta["id"], []).append(doc)
    for result, file in zip(results, args.files):
        for identifier, owners in ids.items():
            if file.resolve() in owners and len(owners) > 1:
                others = ", ".join(str(owner) for owner in owners if owner != file.resolve())
                result["findings"].append({"code": "duplicate-document-id", "line": 1,
                                           "message": f"id {identifier}가 다른 문서와 같음: {others}"})
    for result in results:
        result["findings"].sort(key=lambda item: (item["line"], item["code"], item["message"]))

    total = sum(len(result["findings"]) for result in results)
    report = {
        "schema_version": 1,
        "files": results,
        "checks": {
            "allowed_paths": "checked" if allowed else "not-checked",
            "document_ids": "checked" if args.existing else "inputs-only",
        },
        "summary": {"files": len(results), "findings": total},
    }
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
