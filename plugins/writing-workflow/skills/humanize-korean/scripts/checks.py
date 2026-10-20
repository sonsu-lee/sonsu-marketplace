"""Deterministic golden-fixture scorer for humanize-korean.

LLM output is non-deterministic, so these checks are DIRECTIONAL GATES,
never exact-string expectations. Each check asks "did a known failure mode
appear?" — e.g. a count that must not increase, or a structural element
that must not disappear. A legitimate rewrite always passes; only the
documented failure modes fail.

stdlib only. Usage as a library:

    from checks import run_checks  # scripts/ 에 위치
    failures = run_checks(original_text, rewritten_text)
    # empty list == PASS

or from the CLI:

    python3 checks.py input.txt output.txt

Failure codes (stable API — tests and fixtures reference these):
    empty_output       output is blank
    hayeot_injection   '하였' count increased vs original
    cliche_injection   a boilerplate phrase appeared/increased vs original
    colloquial_erased  colloquial sentence endings (해요체) wiped out
    heading_lost       a heading line disappeared entirely
    heading_absorbed   a heading line was merged into body prose
    footnote_count     inline footnote markers decreased
    footnote_numbers   the set of footnote numbers changed
    footnote_def       a footnote definition line was lost or altered
    footnote_anchor    a footnote marker moved to a different sentence
                       (detected via the nearest preceding number token)
    quote_altered      a direct quote is no longer verbatim
    number_injected    a numeric value appears in the output that never
                       occurred in the original (수치 주입)

Advisory (NOT a failure code): 원문 수치의 소실은 문장 병합·표기 통합의
정상 부산물일 수 있어 게이트하지 않는다. `dropped_numbers()`가 소실 값
목록을 반환하며, verify_gates.py가 리포트 전용 축(P4)에서 관측만 한다.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class Failure:
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ===========================================================================
# Register checks — the "격식 역주행" failure mode
# ===========================================================================

HAYEOT_RE = re.compile(r"하였")

# Boilerplate phrases the rewriter must never ADD. Increase-only gate:
# if the original already contains one, keeping it is not a failure.
CLICHE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("기록적인 성과", re.compile(r"기록적인\s*성과")),
    ("괄목할 만한", re.compile(r"괄목할\s*만한")),
    ("~로 평가된다", re.compile(r"로\s*평가(?:된다|받|되)")),
    ("주목받-", re.compile(r"주목받")),
    ("크게 기여", re.compile(r"크게\s*기여")),
    ("중요한 역할을 한다", re.compile(r"중요한\s*역할을\s*(?:한다|했다|할)")),
    ("시사하는 바가 크다", re.compile(r"시사하는\s*바가\s*크")),
    ("의미가 크다", re.compile(r"의미가\s*크다")),
]

# Sentence-final 요 (해요체/구어 종결). Counts "~인데요." "~거든요?" etc.
# 해요체 종결은 용언 활용이다. 그런데 `요` 로 끝나는 한자 명사가 개조식 종결로
# 쓰이면("보완 필요.", "추진 개요.") 같은 표면형이 된다. 그것을 구어 종결로 세면
# `colloquial_erased` 가 발동해 **올바른 윤문 결과를 롤백시킨다**(PR #94 지적).
#
# `요` 직전 한 음절로 배제한다. 목록에 `고` 는 넣지 않는다 — "그렇게 하고요" 처럼
# 진짜 해요체 연결형이 같은 음절을 쓰기 때문이다. 같은 이유로 `세`(주세요)·
# `네`(그렇네요)·`죠` 계열도 건드리지 않는다. 아래 음절들은 해요체 활용으로
# 나타나지 않는 한자 명사의 끝음절 앞자리다.
_YO_NOUN_HEADS = "필중개수주소강동풍"
YO_ENDING_RE = re.compile(
    rf"(?<![{_YO_NOUN_HEADS}])요\s*(?:[.?!…]|$)", re.MULTILINE
)

# colloquial_erased fires only when the original is clearly colloquial
# (>= MIN_YO endings) AND the output keeps less than KEEP_RATIO of them.
# Sentence merging in a legitimate rewrite stays well above this floor.
MIN_YO = 3
KEEP_RATIO = 0.5


def check_register(original: str, output: str) -> list[Failure]:
    fails: list[Failure] = []

    a = len(HAYEOT_RE.findall(original))
    b = len(HAYEOT_RE.findall(output))
    if b > a:
        fails.append(Failure(
            "hayeot_injection",
            f"'하였' 계열이 원문 {a}회 → 윤문본 {b}회로 늘었습니다 (격식 상향 주입)",
        ))

    for name, pat in CLICHE_PATTERNS:
        a = len(pat.findall(original))
        b = len(pat.findall(output))
        if b > a:
            fails.append(Failure(
                "cliche_injection",
                f"상투구 '{name}'이 원문 {a}회 → 윤문본 {b}회로 늘었습니다 (주입 금지)",
            ))

    a = len(YO_ENDING_RE.findall(original))
    b = len(YO_ENDING_RE.findall(output))
    if a >= MIN_YO and b < a * KEEP_RATIO:
        fails.append(Failure(
            "colloquial_erased",
            f"구어 종결(~요)이 원문 {a}회 → 윤문본 {b}회로 격감했습니다 "
            f"(격식 역주행; register는 Before/After 동일이 철칙)",
        ))

    return fails


# ===========================================================================
# Structure checks — the "학술 구조·각주 파괴" failure mode
# ===========================================================================

_HEADING_PREFIX = re.compile(
    r"^(?:#{1,6}\s+"                      # markdown: ## 제목
    r"|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]+\.\s*"          # 로마 숫자: Ⅱ. 제목
    r"|\d{1,2}\.\s+"                      # 아라비아: 1. 제목
    r"|\(\d{1,2}\)\s*"                    # 괄호: (3) 제목
    r"|제\d+[장절]\s*"                    # 제3장 제목
    r")"
)
_PROSE_ENDING = re.compile(r"(?:다|요|음|함|까)\s*[.?!]$")
FOOTNOTE_LINE_RE = re.compile(r"^[ \t]*(?:(\d+)\)\s|\[(\d+)\]\s)")


def extract_headings(text: str) -> list[tuple[str, str]]:
    """Return [(heading_line, core_title_without_numbering), ...]."""
    heads = []
    for line in text.splitlines():
        s = line.strip()
        if not s or len(s) > 50:
            continue
        if FOOTNOTE_LINE_RE.match(s):  # footnote definition, not a heading
            continue
        if not _HEADING_PREFIX.match(s):
            continue
        if _PROSE_ENDING.search(s):  # short prose sentence, not a heading
            continue
        core = _HEADING_PREFIX.sub("", s).strip()
        if not core:
            continue
        heads.append((_norm_ws(s), core))
    return heads


def check_headings(original: str, output: str) -> list[Failure]:
    fails: list[Failure] = []
    out_lines = {_norm_ws(l) for l in output.splitlines() if l.strip()}
    out_joined = _norm_ws(output)
    for line, core in extract_headings(original):
        if line in out_lines:
            continue
        if core in out_joined:
            fails.append(Failure(
                "heading_absorbed",
                f"제목 '{line}'이 독립 줄에서 사라지고 본문에 흡수됐습니다",
            ))
        else:
            fails.append(Failure(
                "heading_lost",
                f"제목 '{line}'이 윤문본에서 사라졌습니다",
            ))
    return fails


# Inline markers are attached to preceding text ("...증가했다.1)").
# A line-leading "N) " can be a procedure step or a definition; its prefix is
# not a marker, but prose later on the same line can contain a real citation.
# Parenthesized headings and years are excluded by the lookbehinds.
_INLINE_MARKER = re.compile(
    r"(?<=\S)(?<![(\d])(\d+)\)"
    r"|(?<![\\\]])\[(\d+)\](?![(:\[])"
)
_DEF_LABEL = re.compile(r"(?:^|(?<=\s))(?:(\d+)\)|\[(\d+)\])\s")
_NUM_TOKEN = re.compile(r"\d+(?:[.,]\d+)*")

ANCHOR_WINDOW = 50  # chars scanned backwards from a marker for its anchor number

_FENCE_LINE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")


def _mask_markdown_examples(text: str) -> str:
    """Mask code examples without changing offsets or line boundaries."""
    lines = []
    fence = ""
    for line in text.splitlines(keepends=True):
        match = _FENCE_LINE_RE.match(line.rstrip("\r\n"))
        protected = bool(fence) or line.startswith(("    ", "\t"))
        if fence:
            if (match and match[1][0] == fence[0]
                    and len(match[1]) >= len(fence) and not match[2].strip()):
                fence = ""
        elif match and not (match[1][0] == "`" and "`" in match[2]):
            fence = match[1]
            protected = True
        lines.append(re.sub(r"[^\r\n]", " ", line) if protected else line)
    return _INLINE_CODE_RE.sub(
        lambda m: re.sub(r"[^\r\n]", " ", m[0]), "".join(lines)
    )


def extract_inline_markers(text: str) -> list[tuple[str, int]]:
    """Return prose citations, excluding definition prefixes, links, and code."""
    prose = _mask_markdown_examples(text)
    prose = re.sub(
        r"<!--[\s\S]*?-->",
        lambda m: re.sub(r"[^\r\n]", " ", m[0]),
        prose,
    )
    markers = []
    offset = 0
    for line in prose.splitlines(keepends=True):
        prefix = FOOTNOTE_LINE_RE.match(line)
        for m in _INLINE_MARKER.finditer(line):
            if prefix and m.start() < prefix.end():
                continue
            group = 1 if m[1] is not None else 2
            markers.append((m[group], offset + m.start(group)))
        offset += len(line)
    return markers


def extract_defs(text: str) -> dict[str, str]:
    """Return {footnote_number: normalized_definition_content}.

    Require an inline reference so numbered procedures remain editable.
    Merged-but-verbatim definitions still support content-identity checks.
    """
    defs: dict[str, str] = {}
    referenced = {number for number, _ in extract_inline_markers(text)}
    prose_lines = _mask_markdown_examples(text).splitlines()
    for line, prose in zip(text.splitlines(), prose_lines):
        if not FOOTNOTE_LINE_RE.match(prose):
            continue
        labels = [(m.start(), m[1] or m[2]) for m in _DEF_LABEL.finditer(line)]
        for i, (pos, num) in enumerate(labels):
            if num not in referenced:
                continue
            end = labels[i + 1][0] if i + 1 < len(labels) else len(line)
            content = _DEF_LABEL.sub("", line[pos:end], count=1)
            defs[num] = _norm_ws(content)
    return defs


def _nearest_num_before(text: str, pos: int) -> str | None:
    seg = text[max(0, pos - ANCHOR_WINDOW):pos]
    nums = _NUM_TOKEN.findall(seg)
    return nums[-1] if nums else None


def check_footnotes(original: str, output: str) -> list[Failure]:
    fails: list[Failure] = []
    in_markers = extract_inline_markers(original)
    out_markers = extract_inline_markers(output)
    if not in_markers and not extract_defs(original):
        return fails  # original has no footnotes; nothing to protect

    if len(out_markers) < len(in_markers):
        fails.append(Failure(
            "footnote_count",
            f"본문 각주 표시가 {len(in_markers)}개 → {len(out_markers)}개로 줄었습니다",
        ))

    in_nums = {n for n, _ in in_markers}
    out_nums = {n for n, _ in out_markers}
    if in_nums != out_nums:
        missing = sorted(in_nums - out_nums, key=int)
        invented = sorted(out_nums - in_nums, key=int)
        parts = []
        if missing:
            parts.append(f"소실 {missing}")
        if invented:
            parts.append(f"신규 {invented}")
        fails.append(Failure(
            "footnote_numbers",
            f"각주 번호 집합이 달라졌습니다: {', '.join(parts)}",
        ))

    # Anchor check: a marker must stay attached to the same sentence.
    # Proxy: the nearest number token within ANCHOR_WINDOW chars before the
    # marker (numbers are immutable under the skill's iron rules, so they
    # survive a legitimate rewrite). Markers with no nearby number in the
    # original are skipped — count/set checks still cover their existence.
    out_first_pos = {}
    for n, p in out_markers:
        out_first_pos.setdefault(n, p)
    for num, pos in in_markers:
        anchor = _nearest_num_before(original, pos)
        if anchor is None or num not in out_first_pos:
            continue
        out_anchor = _nearest_num_before(output, out_first_pos[num])
        if out_anchor != anchor:
            fails.append(Failure(
                "footnote_anchor",
                f"각주 {num})이 원위치를 벗어났습니다 "
                f"(인접 수치 앵커 '{anchor}' → '{out_anchor}'): 인용 출처 변조 위험",
            ))

    in_defs = extract_defs(original)
    out_defs = extract_defs(output)
    for num, content in in_defs.items():
        if num not in out_defs:
            fails.append(Failure(
                "footnote_def",
                f"각주 정의 {num})이 윤문본에서 사라졌습니다",
            ))
        elif out_defs[num] != content:
            fails.append(Failure(
                "footnote_def",
                f"각주 정의 {num})의 내용이 달라졌습니다 (서지사항은 불변이어야 함)",
            ))
    return fails


# ===========================================================================
# Number fidelity — 수치는 철칙상 불변. 주입만 FAIL (방향성 게이트).
# 삭제는 재구성 부산물일 수 있어 advisory(dropped_numbers)로만 관측.
# ===========================================================================

# Single Korean magnitude suffixes are normalized; compound Korean numerals
# remain token-based rather than being interpreted as a quantity expression.
_KO_UNIT_MULT = {
    "백": 100,
    "천": 1_000,
    "만": 10_000,
    "억": 100_000_000,
    "조": 1_000_000_000_000,
}

def _number_values(text: str) -> set[str]:
    """Canonical signed values; units still require direct semantic review.

    Preserve grouping/decimal and single Korean magnitude normalization.
    This remains a set comparison, not a quantity or expression parser.
    """
    values: set[str] = set()
    for m in _NUM_TOKEN.finditer(text):
        token = m[0].replace(",", "")
        # A hyphen between digits is a date/range separator, not a unary sign.
        sign_pos = m.start() - 1
        negative = (
            sign_pos >= 0 and text[sign_pos] in "-−"
            and (sign_pos == 0 or not text[sign_pos - 1].isdigit())
        )
        try:
            value = Decimal(token)
        except InvalidOperation:
            # Preserve existing multi-dot tokens (for example, versions).
            values.add(("-" if negative else "") + token)
            continue
        mult = _KO_UNIT_MULT.get(text[m.end():m.end() + 1], 1)
        value *= mult
        if negative:
            value = -value
        token = format(value, "f")
        if "." in token:
            token = token.rstrip("0").rstrip(".")
        values.add("0" if value == 0 else token)
    return values


def dropped_numbers(original: str, output: str) -> list[str]:
    """원문에는 있는데 윤문본에서 사라진 수치 값 목록 (advisory 전용).

    Failure가 아니다 — 문장 병합·표기 통합에서도 수치가 사라질 수 있어
    게이트하면 양치기 소년이 된다. run_checks는 호출하지 않으며,
    verify_gates.py가 P4(리포트 전용 축)에서 관측만 한다.
    """
    return sorted(_number_values(original) - _number_values(output))


def check_numbers(original: str, output: str) -> list[Failure]:
    """수치 주입 방향성 게이트 — 주입(number_injected)만 FAIL."""
    fails: list[Failure] = []
    injected = sorted(_number_values(output) - _number_values(original))
    if injected:
        fails.append(Failure(
            "number_injected",
            f"원문에 없던 수치가 윤문본에 등장했습니다: {injected} "
            f"(수치 불변 철칙 — 없던 주장 주입 위험)",
        ))
    return fails


# ===========================================================================
# Quote fidelity — direct quotes are immutable under the iron rules
# ===========================================================================

MIN_QUOTE_LEN = 8


def extract_quotes(text: str, min_len: int = MIN_QUOTE_LEN) -> list[str]:
    quotes: list[str] = []
    for op, cl in (("「", "」"), ("『", "』"), ("“", "”")):
        quotes += re.findall(re.escape(op) + r"([^" + cl + r"]+)" + re.escape(cl), text)
    # Straight double quotes: only if balanced.
    parts = text.split('"')
    if len(parts) % 2 == 1:
        quotes += parts[1::2]
    return [q for q in quotes if len(q.strip()) >= min_len]


# ── 인용 분류: 발화 인용 vs 필자의 수사적 자문 (2026-08-29 정책) ─────────
# 큰따옴표라고 다 같은 인용이 아니다. 발화자·발화 동사가 붙은 인용("…"고 말했다,
# 보고서에 따르면 "…")만 불변이고, 필자가 자문(自問)·강조를 따옴표로 감싼 수사
# 장치는 필자 자신의 문장이므로 윤문 대상이다. 저자가 직접 교정한 정답지가 자문
# 인용 안을 고쳤고, 이 구분 없이는 어떤 실행자도 그 수준에 도달할 수 없었다.
# 판정 창은 문장 경계에서 자른다 — 넓게 잡으면 이웃 문장의 발화 동사가
# 자문 인용을 오보호한다(웹 구현 실측).
_SPEECH_MARK_RE = re.compile(
    r"말했|말한다|밝혔|밝힌|강조했|강조한|언급|설명했|설명한다|전했|덧붙"
    r"|지적했|지적한다|답했|묻자|물었|따르면|촉구|당부|호소|주장했|경고했"
)


# 인용 닫힘 직후의 "~고/~라고 + 용언"은 동사가 무엇이든 발화·전거 구문이다
# ("…"고 말했다 / "…"라고 보고하였다 / "…"으로 정의한다). 어휘 사전은 새는 반면
# (실측: "보고하였다" 누락으로 학술 인용이 무보호), 이 구조 신호는 포괄적이다.
_ATTRIB_AFTER_RE = re.compile(r'^["”」』]?\s*(?:[이으]?라고|고|[으]?로)\s*[가-힣]{1,8}(?:하|했|한다|된다|였|입니다)')


def _is_protected_quote(original: str, span: str) -> bool:
    i = original.find(span)
    if i < 0:
        return True  # 못 찾으면 보수적으로 보호
    before = original[max(0, i - 30):i]
    cut = max(before.rfind(". "), before.rfind("다. "))
    if cut >= 0:
        before = before[cut + 1:]
    after = original[i + len(span):i + len(span) + 24]
    cut = after.find(". ")
    if cut >= 0:
        after = after[:cut + 1]
    if _ATTRIB_AFTER_RE.search(after):
        return True
    return bool(_SPEECH_MARK_RE.search(before) or _SPEECH_MARK_RE.search(after))


def check_quotes(original: str, output: str) -> list[Failure]:
    fails = []
    for q in extract_quotes(original):
        if q not in output and _is_protected_quote(original, q):
            fails.append(Failure(
                "quote_altered",
                f"직접 인용 「{q[:30]}…」이 윤문본에 원문 그대로 없습니다 (인용 불변 철칙)",
            ))
    return fails


# ===========================================================================
# Entry point
# ===========================================================================

# The editing role owns this ordered format. Accept only a complete comment
# on its own line at EOF, with optional indented continuations for review data.
_SUMMARY_FIELDS = (
    ("original_characters", r"\d+"),
    ("final_body_characters", r"\d+"),
    ("change_rate", r"\S[^\r\n]*"),
    ("grade", r"\S[^\r\n]*"),
    ("self_check_passed", r"\d+/6"),
    ("categories", r"[^\r\n]*"),
    ("highlights", r"[^\r\n]*"),
    ("residual_findings", r"[^\r\n]*"),
)
_SUMMARY_BLOCK_RE = re.compile(
    r"^<!-- HUMANIZE-SUMMARY[ \t]*\r?\n"
    + "".join(
        name + r":[ \t]*" + value + r"\r?\n(?:[ \t]+[^\r\n]*\r?\n)*"
        for name, value in _SUMMARY_FIELDS
    )
    + r"-->[ \t]*(?:\r?\n[ \t]*)*\Z",
    re.MULTILINE,
)


def split_summary_block(text: str) -> tuple[str, str]:
    """Split only a complete, terminal generated summary outside code examples."""
    match = _SUMMARY_BLOCK_RE.search(text)
    if match is None:
        return text, ""
    # Never let an earlier/nested comment or a fenced/inline example act as
    # metadata. Mask only to establish context; return original bytes.
    if "<!--" in text[match.start() + 4:match.end()]:
        return text, ""
    if "-->" in text[match.start():match.end()].split("\n-->")[0]:
        return text, ""
    visible = _mask_markdown_examples(text)
    if not visible.startswith("<!-- HUMANIZE-SUMMARY", match.start()):
        return text, ""
    prefix = visible[:match.start()]
    if prefix.rfind("<!--") > prefix.rfind("-->"):
        return text, ""
    return text[:match.start()], text[match.start():]


def strip_summary_block(text: str) -> str:
    """Remove generated terminal metadata, preserving markers in source prose."""
    body, _ = split_summary_block(text)
    return body.strip()


def run_checks(original: str, output: str) -> list[Failure]:
    original = strip_summary_block(original)
    output = strip_summary_block(output)
    if not output.strip():
        return [Failure("empty_output", "윤문본이 비어 있습니다")]
    fails: list[Failure] = []
    fails += check_register(original, output)
    fails += check_headings(original, output)
    fails += check_footnotes(original, output)
    fails += check_quotes(original, output)
    fails += check_numbers(original, output)
    return fails


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 checks.py <original.txt> <rewritten.txt>", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        original = f.read()
    with open(argv[2], encoding="utf-8") as f:
        output = f.read()
    failures = run_checks(original, output)
    if failures:
        for x in failures:
            print(f"FAIL {x}")
        return 1
    print("PASS (알려진 실패 모드 없음)")
    return 0


# ── 콘솔 하드닝 (#84) ───────────────────────────────────────────────
# Windows(cp949)에서 한글·em-dash 출력이 UnicodeEncodeError 로 죽는 것을 막는다.
import os as _os  # noqa: E402
import sys as _sys  # noqa: E402

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import console as _console  # noqa: E402

if __name__ == "__main__":
    _console.force_utf8_console()
    raise SystemExit(main(sys.argv))
