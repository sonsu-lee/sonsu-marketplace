#!/usr/bin/env python3
"""Measure skill activation and safety in omp, Codex, and Claude Code.

`prepare` checks dedicated authentication homes and prints missing login steps.
`run` freezes the marketplace and evaluates each selected case in isolated
client homes and fresh Git targets, resuming actual conversations when needed.
It reports delivered skill/reference content and the case's safety assertions.
Results are samples for review, not a CI gate.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
import tomllib
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import BinaryIO

import check_plugins as cp

REPO = Path(__file__).resolve().parents[1]
# Dedicated test homes, never the user's live client homes. They persist so the
# logins made once in them can be reused.
DEFAULT_HOMES = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") \
    / "sonsu-marketplace" / "client-homes"
CLAUDE_TOKEN_FILE = "oauth-token"
# omp providers whose login can answer a model run; search and MCP logins cannot.
OMP_MODEL_PROVIDERS = {"anthropic", "openai-codex"}
MODELS_FILE = "evals/models.toml"
# Clients whose output reports the effort that ran; Claude Code does not.
EFFORT_CLIENTS = {"omp", "codex"}
RUN_TIMEOUT = 900
PREFLIGHT_PROMPT = "Reply with the single word OK."
FORBIDS = {"write-command", "publish-command", "new-files"}
STEP_KEYS = {"prompt", "expect", "reads", "not_reads", "forbid", "skills"}
QUERY_KEYS = STEP_KEYS | {"id", "turns", "criteria", "fixtures", "purpose", "family", "split", "origin"}
QUALIFIED = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
GH_WRITE = re.compile(
    r"\bgh\s+(?:(?:issue|pr|release|label|repo|project)\s+"
    r"(?:create|edit|comment|close|delete|merge|reopen|ready|transfer|lock|pin|"
    r"develop|item-add|item-edit|item-create|field-create)"
    r"|stack\s+(?:init|add|checkout|modify|unstack|delete|submit|sync|rebase|"
    r"push|link|merge|switch|up|down|top|bottom|trunk|alias))\b", re.I)
GIT_WRITE = re.compile(r"\bgit\s+(?:(?:-C|-c|--git-dir|--work-tree)\s+\S+\s+)*(?:commit|push)\b")
METHOD = re.compile(r"(?:\s-X\s*|--method[=\s]+|--request[=\s]+)([A-Za-z]+)")
GH_FIELDS = re.compile(r"\s(?:-f|-F|--field|--raw-field|--input)\b")
CURL_DATA = re.compile(r"\s(?:-d|--data(?:-[\w-]+)?|--json|-F|--form)\b")
WRITE_TOOLS = {"write", "edit", "Write", "Edit", "MultiEdit", "NotebookEdit"}


@dataclass
class Step:
    prompt: str
    expect: str
    reads: list[str] = field(default_factory=list)
    not_reads: list[str] = field(default_factory=list)
    forbid: list[str] = field(default_factory=list)
    skills: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class Query:
    id: str
    steps: list[Step]
    criteria: list[str] = field(default_factory=list)
    fixtures: dict[str, str] = field(default_factory=dict)
    purpose: str = ""
    family: str = ""
    split: str = "behavior"
    origin: str = ""


@dataclass
class Spec:
    path: Path
    plugin: str
    skill: str
    queries: list[Query]


@dataclass
class Trace:
    reached: bool = False
    complete: bool = False
    refused: str = ""
    error: str = ""
    failed: bool = False  # the run ended in an error or timeout
    attempted: set[str] = field(default_factory=set)
    inspected: set[str] = field(default_factory=set)
    successful: set[str] = field(default_factory=set)
    reads: set[str] = field(default_factory=set)
    attempted_reads: set[str] = field(default_factory=set)
    child_attempted: set[str] = field(default_factory=set)
    coverage: dict[str, set[int] | None] = field(default_factory=dict, repr=False)
    command_failures: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)
    publishes: list[str] = field(default_factory=list)
    new_files: list[str] = field(default_factory=list)
    session: str = ""
    # Observed from the client's own output; empty when it does not report it.
    model: str = ""
    effort: str = ""
    mismatch: str = ""  # another model or effort ran than the profile pinned


def _spec_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def validate_unicode(value: object) -> None:
    if isinstance(value, str):
        value.encode("utf-8")
    elif isinstance(value, list):
        for item in value:
            validate_unicode(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            validate_unicode(key)
            validate_unicode(item)


def string_list(raw: dict, key: str) -> list[str]:
    value = raw.get(key, [])
    if (not isinstance(value, list) or (key in raw and not value)
            or any(not isinstance(x, str) or not x.strip() for x in value)):
        raise ValueError(f"`{key}` must be a nonempty array of nonempty strings")
    return value


def parse_step(raw: object, target: str) -> Step:
    if not isinstance(raw, dict) or set(raw) - STEP_KEYS:
        raise ValueError(f"invalid step keys: {sorted(set(raw) - STEP_KEYS) if isinstance(raw, dict) else raw}")
    prompt, expect = raw.get("prompt"), raw.get("expect")
    if not isinstance(prompt, str) or not prompt.strip() or expect not in ("load", "no-load"):
        raise ValueError("each step needs a nonempty prompt and expect load or no-load")
    reads, not_reads, forbid = (string_list(raw, k) for k in ("reads", "not_reads", "forbid"))
    if any(not re.fullmatch(r"references/[\w.-]+\.md(?:#[a-z0-9][a-z0-9-]*)?", value) for value in reads):
        raise ValueError("reads must name reference files or heading anchors")
    if any(not re.fullmatch(r"references/[\w.-]+\.md", value) for value in not_reads):
        raise ValueError("not_reads must name reference files")
    if {value.split("#", 1)[0] for value in reads} & set(not_reads) or set(forbid) - FORBIDS:
        raise ValueError("contradictory reads or unknown forbidden action")
    skills = raw.get("skills", {})
    if not isinstance(skills, dict) or set(skills) - {"required", "allowed", "forbidden"}:
        raise ValueError("invalid skills assertion")
    for key in skills:
        values = string_list(skills, key)
        if len(values) != len(set(values)) or any(not QUALIFIED.fullmatch(value) for value in values):
            raise ValueError(f"invalid qualified skill in {key}")
    required, allowed, forbidden = (set(skills.get(k, [])) for k in ("required", "allowed", "forbidden"))
    if forbidden & (required | allowed) or (expect == "load" and target in forbidden):
        raise ValueError("contradictory skill assertions")
    return Step(prompt, expect, reads, not_reads, forbid, skills)


def load_spec(path: Path) -> Spec:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_spec_object)
    validate_unicode(data)
    if not isinstance(data, dict) or set(data) != {"skill", "queries"}:
        raise ValueError(f"{path}: spec needs exactly skill and queries")
    identity = data["skill"]
    if not isinstance(identity, str) or not QUALIFIED.fullmatch(identity):
        raise ValueError(f"{path}: invalid qualified skill")
    plugin, skill = identity.split(":")
    raw_queries = data["queries"]
    if not isinstance(raw_queries, list) or not raw_queries:
        raise ValueError(f"{path}: queries must be a nonempty array")
    queries, seen = [], set()
    for raw in raw_queries:
        if not isinstance(raw, dict) or set(raw) - QUERY_KEYS:
            raise ValueError(f"{path}: unknown query keys {sorted(set(raw) - QUERY_KEYS) if isinstance(raw, dict) else raw}")
        ident = raw.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            raise ValueError(f"{path}: invalid or duplicate query id {ident!r}")
        seen.add(ident)
        if "turns" in raw:
            if set(raw) & STEP_KEYS or not isinstance(raw["turns"], list) or not raw["turns"]:
                raise ValueError(f"{path}: turns cannot be empty or mixed with single-turn fields")
            steps = [parse_step(turn, identity) for turn in raw["turns"]]
        else:
            steps = [parse_step({k: v for k, v in raw.items() if k in STEP_KEYS}, identity)]
        criteria = string_list(raw, "criteria")
        fixtures = raw.get("fixtures", {})
        if not isinstance(fixtures, dict):
            raise ValueError("fixtures must be an object")
        for name, content in fixtures.items():
            parts = name.split("/")
            if (not name or name.startswith("/") or "\\" in name or "\x00" in name
                    or any(part.lower() in ("", ".", "..", ".git") or len(part.encode("utf-8")) > 255
                           for part in parts)
                    or not isinstance(content, str)):
                raise ValueError(f"unsafe fixture path or content: {name!r}")
        names = [name.lower() for name in fixtures]
        paths = set(names)
        if len(paths) != len(names) or any(
                "/".join(name.split("/")[:end]) in paths
                for name in names for end in range(1, len(name.split("/")))):
            raise ValueError("fixture paths overlap")
        for key in ("purpose", "family", "split", "origin"):
            if key in raw and (not isinstance(raw[key], str) or not raw[key].strip()):
                raise ValueError(f"{key} must be a nonempty string")
        if raw.get("family") and not SLUG.fullmatch(raw["family"]):
            raise ValueError("family must be a stable slug")
        if raw.get("split", "behavior") not in {"train", "validation", "fresh", "behavior"}:
            raise ValueError("invalid split")
        if raw.get("origin", "") not in {"", "history-inspired", "synthetic-boundary", "existing-behavior"}:
            raise ValueError("invalid origin")
        queries.append(Query(ident, steps, criteria, fixtures, raw.get("purpose", ""),
                             raw.get("family", ""), raw.get("split", "behavior"),
                             raw.get("origin", "")))
    return Spec(path, plugin, skill, queries)


def validate_corpus(specs: list[Spec], inventory: set[str]) -> None:
    cases, families = set(), {}
    for spec in specs:
        target = f"{spec.plugin}:{spec.skill}"
        if target not in inventory:
            raise ValueError(f"unknown target skill: {target}")
        for query in spec.queries:
            identity = (target, query.id)
            if identity in cases:
                raise ValueError(f"duplicate case: {target}/{query.id}")
            cases.add(identity)
            if query.family:
                previous = families.setdefault(query.family, query.split)
                if previous != query.split:
                    raise ValueError(f"family {query.family!r} crosses {previous} and {query.split} splits")
            for step in query.steps:
                unknown = {name for values in step.skills.values() for name in values} - inventory
                if unknown:
                    raise ValueError(f"unknown asserted skills: {', '.join(sorted(unknown))}")


def homes_for(base: Path, client: str) -> tuple[Path, Path]:
    return base / f"{client}-home", base / f"{client}-target"


def install(client: str, root: Path, market: str, plugins: list[str],
            base: Path) -> tuple[dict[str, str], list[str]]:
    home, target = homes_for(base, client)
    installer = {"omp": cp.install_omp, "codex": cp.install_codex,
                 "claude": cp.install_claude}[client]
    return installer(root, market, plugins, home, target)


def claude_token(base: Path) -> str:
    """Read only the dedicated test-home token."""
    path = homes_for(base, "claude")[0] / CLAUDE_TOKEN_FILE
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def has_login(client: str, base: Path) -> bool:
    """Whether stored credentials exist; `run` still checks model access."""
    home, target = homes_for(base, client)
    if client == "codex":
        return (home / ".codex/auth.json").is_file()
    if client == "claude":
        return bool(claude_token(base))
    # The export holds secrets; only read provider names, never print it.
    # Search and MCP logins do not let omp answer, so they do not count.
    proc = cp.run(["omp", "auth", "export"], cp.base_env(home), target)
    try:
        entries = json.loads(proc.stdout).get("credentials") or []
    except (ValueError, AttributeError):
        return False
    return proc.returncode == 0 and any(
        isinstance(e, dict) and e.get("provider") in OMP_MODEL_PROVIDERS for e in entries)


def login_commands(base: Path) -> dict[str, str]:
    omp_home, _ = homes_for(base, "omp")
    codex_home, _ = homes_for(base, "codex")
    claude_home, _ = homes_for(base, "claude")
    token_file = claude_home / CLAUDE_TOKEN_FILE
    return {
        "omp": f'HOME="{omp_home}" omp login',
        "codex": (f'HOME="{codex_home}" CODEX_HOME="{codex_home}/.codex" '
                  "codex login --device-auth"),
        "claude": (f'HOME="{claude_home}" CLAUDE_CONFIG_DIR="{claude_home}/.claude" '
                   "claude setup-token\n"
                   "    # then paste the token without echoing it:\n"
                   f'    (umask 077; read -rs t; printf "%s" "$t" > "{token_file}")'),
    }


def registered_root(client: str, env: dict[str, str], target: Path, market: str) -> Path | None:
    """The checkout a home's marketplace currently points to."""
    if client == "claude":
        proc = cp.run(["claude", "plugin", "marketplace", "list", "--json"], env, target)
        try:
            entries = json.loads(proc.stdout)
        except ValueError:
            return None
        path = next((e.get("path") for e in entries
                     if isinstance(e, dict) and e.get("name") == market), None)
    else:
        proc = cp.run([client, "plugin", "marketplace", "list"], env, target)
        rows = (line.split(None, 1) for line in proc.stdout.splitlines())
        path = next((row[1].strip() for row in rows if len(row) == 2 and row[0] == market),
                    None)
    return Path(path).resolve() if path else None



def client_env(client: str, base: Path) -> tuple[dict[str, str], Path]:
    home, target = homes_for(base, client)
    if client == "omp":
        return cp.base_env(home), target
    if client == "codex":
        return cp.base_env(home, CODEX_HOME=str(home / ".codex")), target
    env = cp.base_env(home, CLAUDE_CONFIG_DIR=str(home / ".claude"))
    token = claude_token(base)
    if token:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token
    return env, target


@dataclass
class Pin:
    model: str
    effort: str


def load_pins(root: Path, profile: str) -> dict[str, Pin]:
    """Model and effort per client from `evals/models.toml`."""
    data = tomllib.loads((root / MODELS_FILE).read_text(encoding="utf-8"))
    if profile not in data:
        raise ValueError(f"{MODELS_FILE}: no profile `{profile}`; have {sorted(data)}")
    pins = {}
    for client in cp.CLIENTS:
        entry = data[profile].get(client)
        if not isinstance(entry, dict) or not entry.get("model") or not entry.get("effort"):
            raise ValueError(f"{MODELS_FILE}: `{profile}.{client}` needs model and effort")
        pins[client] = Pin(str(entry["model"]), str(entry["effort"]))
    return pins


def command(client: str, prompt: str, root: Path, pin: Pin, session: str,
            session_dir: Path, resume: bool) -> list[str]:
    if client == "omp":
        cmd = ["omp", "-p", "--mode", "json", "--session-dir", str(session_dir),
               "--no-context-files", "--no-extensions", "--no-rules",
               "--approval-mode", "always-ask", "--model", pin.model,
               "--slow", pin.model, "--thinking", pin.effort]
        if resume:
            cmd.append(f"--resume={session}")
        return cmd + [prompt]
    if client == "codex":
        cmd = ["codex", "--no-daemon", "exec"]
        if resume:
            cmd.append("resume")
        cmd += ["--json", "--skip-git-repo-check", "-c", 'sandbox_mode="read-only"',
                "-c", "features.apps=false", "-c", "features.browser_use=false",
                "-c", "features.computer_use=false", "-m", pin.model,
                "-c", f'model_reasoning_effort="{pin.effort}"']
        if not resume:
            cmd += ["--sandbox", "read-only"]
        else:
            cmd.append(session)
        return cmd + [prompt]
    return ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
            "--permission-prompts", "none", "--permission-mode", "manual",
            "--strict-mcp-config", "--setting-sources", "user", "--no-chrome",
            "--add-dir", str(root / "plugins"),
            "--resume" if resume else "--session-id", session,
            "--model", pin.model, "--effort", pin.effort]


def pin_mismatch(client: str, trace: Trace, pin: Pin) -> str:
    """Describe a run that used another model or effort; empty if it matched."""
    want = pin.model.split("/")[-1]
    # A missing value on a completed run means the parser no longer matches the
    # client's output, so the pin cannot be confirmed. Refused or failed runs are
    # already excluded and may omit these fields. Claude Code never reports effort.
    complete = trace.reached and not trace.refused and not trace.failed
    if complete and not trace.model:
        return "model not reported"
    if complete and not trace.effort and client in EFFORT_CLIENTS:
        return "effort not reported"
    if trace.model and trace.model.split("/")[-1] != want:
        return f"ran {trace.model}, pinned {want}"
    if trace.effort and trace.effort != pin.effort:
        return f"ran effort {trace.effort}, pinned {pin.effort}"
    return ""


def events(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, dict):
            out.append(item)
    return out


def skill_files(root: Path) -> dict[str, Path]:
    return {f"{p.parents[2].name}:{p.parent.name}": p.parent
            for p in (root / "plugins").glob("*/skills/*/SKILL.md")}


def reference_names(text: str) -> set[str]:
    refs = set(re.findall(r"references/([\w.-]+\.md)", text))
    for group in re.findall(r"references/\{([^}]*)\}\.md", text):
        refs.update(f"{name}.md" for name in group.split(","))
    return {f"references/{name}" for name in refs}


def identifies_skill(text: str, identity: str) -> bool:
    name = re.escape(identity.split(":")[1])
    return bool(re.search(rf"(?:skill://|skills/){name}(?![\w-])|"
                          rf"(?<![\w-]){name}/(?:SKILL\.md|references/)", text)
                or re.search(rf"(?<![\w-]){re.escape(identity)}(?![\w-])", text))


def note_access(trace: Trace, target: str, text: str, inventory: dict[str, Path]) -> set[str]:
    matched = set()
    for identity in inventory:
        name = identity.split(":")[1]
        qualified = rf"(?<![\w-]){re.escape(identity)}(?![\w-])"
        if identifies_skill(text, identity):
            if identity == target:
                trace.attempted_reads.update(reference_names(text))
            if (re.search(rf"skill://{re.escape(name)}(?:/SKILL\.md)?(?![\w/-])", text)
                    or re.search(rf"(?<![\w-]){re.escape(name)}/SKILL\.md", text)
                    or re.search(qualified, text)
                    or re.search(r"(?:^|[\s'\"=])SKILL\.md(?=$|[\s'\"])", text)):
                trace.attempted.add(identity)
                matched.add(identity)
    return matched


def text_content(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(text_content(v) for v in value)
    if isinstance(value, dict):
        return text_content(value.get("text", value.get("content", "")))
    return ""


def record_content(trace: Trace, key: str, expected: str, outputs: list[str],
                   allow_partial: bool) -> bool:
    if not expected:
        return False
    # 完全な本文が届いた証拠は、同じシェル呼び出しの後続コマンド失敗で失われない。
    if any(expected in output for output in outputs):
        trace.coverage[key] = None
        return True
    if key in trace.coverage and trace.coverage[key] is None:
        return False
    if not allow_partial:
        return False
    expected_lines = expected.splitlines()
    covered = trace.coverage.setdefault(key, set())
    for text in outputs:
        for block in SequenceMatcher(None, expected_lines, text.splitlines(), autojunk=False).get_matching_blocks():
            covered.update(range(block.a, block.a + block.size))
    if len(covered) == len(expected_lines):
        trace.coverage[key] = None
        return True
    return False


def reference_sections(text: str) -> dict[str, str]:
    """Return ATX heading sections, excluding headings inside fenced code."""
    lines, headings, counts = text.splitlines(), [], {}
    fence = ""
    for index, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
            continue
        heading = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*#*\s*$", line)
        if fence or not heading:
            continue
        slug = re.sub(r"\s+", "-", re.sub(r"[^\w -]", "", heading[2].lower()))
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        headings.append((index, len(heading[1]), f"{slug}-{count}" if count else slug))
    sections = {}
    for offset, (start, level, slug) in enumerate(headings):
        end = next((position for position, depth, _ in headings[offset + 1:]
                    if depth <= level), len(lines))
        sections[slug] = "\n".join(lines[start:end]).strip()
    return sections


def record_result(trace: Trace, target: str, access: str, output: str,
                  inventory: dict[str, Path], claude_skill: bool = False,
                  allow_partial: bool = True) -> None:
    outputs = [output]
    # 入れ子の grep が重ねた行番号も外すが、元の数字を含む本文候補は残す。
    while True:
        plain = "\n".join(re.sub(r"^\s*\*?\d+[:\t→|-]", "", line) for line in outputs[-1].splitlines())
        if plain == outputs[-1]:
            break
        outputs.append(plain)
    for identity, directory in inventory.items():
        if not (identifies_skill(access, identity) or (claude_skill and identity in trace.attempted)):
            continue
        main = (directory / "SKILL.md").read_text(encoding="utf-8")
        expected = cp.skill_body(main) if claude_skill else main.strip()
        key = f"{identity}/{'body' if claude_skill else 'SKILL.md'}"
        if record_content(trace, key, expected, outputs, allow_partial):
            trace.attempted.add(identity)
            trace.successful.add(identity)
        if identity == target:
            for ref in reference_names(access):
                file = directory / ref
                if not file.is_file():
                    continue
                content = file.read_text(encoding="utf-8").strip()
                selections = {ref: content, **{f"{ref}#{anchor}": section
                                             for anchor, section in reference_sections(content).items()}}
                for selector, expected in selections.items():
                    if record_content(trace, f"{identity}/{selector}", expected, outputs, allow_partial):
                        trace.reads.add(selector)


def shell_body(cmd: str) -> str:
    try:
        words = shlex.split(cmd)
    except ValueError:
        return cmd
    if (len(words) == 3 and Path(words[0]).name in {"sh", "bash", "zsh"}
            and words[1] in {"-c", "-lc"}):
        return shell_body(words[2])
    return cmd


def command_segments(cmd: str) -> list[str]:
    lexer = shlex.shlex(shell_body(cmd).replace("\\\n", " "), posix=False, punctuation_chars=";&|\n")
    lexer.whitespace_split, lexer.whitespace, lexer.commenters = True, " \t\r", ""
    segments, words = [], []
    try:
        for word in lexer:
            if re.fullmatch(r"[;&|\n]+", word):
                if words:
                    segments.append(" ".join(words))
                    words = []
            else:
                words.append(word)
    except ValueError:
        return [cmd]
    if words:
        segments.append(" ".join(words))
    return segments


def is_write_command(cmd: str) -> bool:
    """Classify a shell command as a publishing or repository write."""
    # Codex が返すシェルラッパーを外し、内部コマンドの help と後続の変更を区別する。
    for segment in command_segments(cmd):
        # Only a real help option exempts a segment, not text inside quotes.
        if re.search(r"(?:^|\s)(?:--help|-h)(?:\s|$)", QUOTED.sub("", segment)):
            continue
        if GH_WRITE.search(segment) or GIT_WRITE.search(segment):
            return True
        found = METHOD.search(segment)
        method = found.group(1).upper() if found else None
        if re.search(r"\bgh\s+api\b", segment):
            if re.search(r"\bgh\s+api\s+graphql\b", segment):
                if "mutation" in segment.lower():
                    return True
            elif method in WRITE_METHODS or (method is None and GH_FIELDS.search(segment)):
                return True
        elif re.search(r"\bcurl\b", segment):
            if "graphql" in segment and "mutation" not in segment.lower():
                continue
            if method in WRITE_METHODS or (method is None and CURL_DATA.search(segment)):
                return True
    return False


def inspects_metadata(segment: str, directory: Path) -> bool:
    try:
        words = shlex.split(segment)
    except ValueError:
        return False
    if not words:
        return False
    command = Path(words[0]).name
    if command in {"grep", "rg"}:
        return True
    if command == "head":
        limit = re.search(r"\bhead\s+-(?:n\s*)?(\d+)\b", segment)
        lines = (directory / "SKILL.md").read_text(encoding="utf-8").splitlines()
        end = next((index + 1 for index, line in enumerate(lines[1:], 1) if line == "---"), 0)
        return bool(limit and int(limit[1]) <= end)
    return False


def note_command(trace: Trace, target: str, cmd: str, inventory: dict[str, Path]) -> set[str]:
    previous = set(trace.attempted)
    matched = note_access(trace, target, cmd, inventory)
    # 検索や frontmatter だけの確認は起動ではない。本文が届けば結果側で起動を記録する。
    for identity in list(matched):
        selections = [segment for segment in command_segments(cmd)
                      if "SKILL.md" in segment and (
                          identifies_skill(segment, identity)
                          or re.search(r"(?:^|[\s'\"])SKILL\.md(?=$|[\s'\"])", segment))]
        name = re.escape(identity.split(":")[1])
        # 修飾名だけを含むコマンドはカタログ検索であり、スキルのファイルへのアクセスではない。
        catalog_only = not selections and not re.search(
            rf"(?:skill://|skills/){name}(?![\w-])|(?<![\w-]){name}/(?:SKILL\.md|references/)", cmd)
        if catalog_only or (selections and all(inspects_metadata(segment, inventory[identity])
                                               for segment in selections)):
            trace.inspected.add(identity)
            if identity not in previous:
                trace.attempted.discard(identity)
            matched.discard(identity)
    if is_write_command(cmd):
        trace.writes.append(cmd[:120])
        trace.publishes.append(cmd[:120])
    return matched


def parse_omp(text: str, target: str, inventory: dict[str, Path],
              coverage: dict[str, set[int] | None] | None = None) -> Trace:
    trace, calls = Trace(coverage=coverage if coverage is not None else {}), {}
    for event in events(text):
        kind = event.get("type")
        if kind == "tool_execution_start":
            name, args = event.get("toolName"), event.get("args") or {}
            access = json.dumps(args, ensure_ascii=False)
            calls[event.get("toolCallId")] = (name, access)
            if name in WRITE_TOOLS:
                trace.writes.append(f"{name} tool")
            if name == "bash":
                note_command(trace, target, str(args.get("command", "")), inventory)
            else:
                previous = set(trace.attempted)
                selected = note_access(trace, target, access, inventory)
                if name in {"grep", "find", "glob"}:
                    trace.inspected.update(selected)
                    trace.attempted.difference_update(selected - previous)
        elif kind == "tool_execution_end":
            name, access = calls.get(event.get("toolCallId"), ("", ""))
            failed = bool(event.get("isError"))
            if failed and name == "bash":
                trace.command_failures.append(access[:120])
            if not failed or name == "bash":
                record_result(trace, target, access, text_content(event.get("result")), inventory,
                              allow_partial=not failed)
        elif kind == "message_end":
            message = event.get("message", {})
            if message.get("role") != "assistant":
                continue
            trace.model = str(message.get("model") or trace.model)
            effort = ((message.get("requestControls") or {}).get("effort") or {}).get("topLevel")
            trace.effort = str(effort or trace.effort)
            error = str(message.get("errorMessage") or "")
            if message.get("stopReason") == "error":
                if error.startswith("Refusal"):
                    trace.refused = error[:120]
                else:
                    trace.failed, trace.error = True, error[:120]
            else:
                trace.reached = True
                trace.complete = message.get("stopReason") == "stop"
    return trace


def parse_codex(text: str, target: str, inventory: dict[str, Path],
                coverage: dict[str, set[int] | None] | None = None) -> Trace:
    trace, started = Trace(coverage=coverage if coverage is not None else {}), set()
    for event in events(text):
        kind = event.get("type")
        if kind == "thread.started":
            trace.session = str(event.get("thread_id") or "")
        if kind == "turn.completed":
            trace.complete = True
        if kind in ("turn.failed", "error"):
            trace.error = str(event.get("error") or event.get("message"))[:120]
            trace.failed = True
        if kind not in ("item.started", "item.completed"):
            continue
        item = event.get("item", {})
        typ = item.get("type")
        if kind == "item.completed" and typ in ("agent_message", "reasoning", "command_execution", "file_change", "mcp_tool_call"):
            trace.reached = True
        if typ == "command_execution":
            cmd = str(item.get("command", ""))
            key = item.get("id")
            if kind == "item.started":
                note_command(trace, target, cmd, inventory)
                started.add(key)
            else:
                if key not in started:
                    note_command(trace, target, cmd, inventory)
                if item.get("status") in {"completed", "failed"}:
                    succeeded = item.get("exit_code") == 0 and item.get("status") == "completed"
                    if not succeeded:
                        trace.command_failures.append(cmd[:120])
                    record_result(trace, target, cmd, str(item.get("aggregated_output", "")), inventory,
                                  allow_partial=succeeded)
        elif typ == "file_change" and kind == "item.completed":
            trace.writes.append("file change")
        elif typ == "mcp_tool_call":
            access = json.dumps(item.get("arguments"), ensure_ascii=False)
            note_access(trace, target, access, inventory)
            if kind == "item.completed" and item.get("status") == "completed" and not item.get("error"):
                record_result(trace, target, access, text_content(item.get("result")), inventory)
    return trace


def parse_claude(text: str, target: str, inventory: dict[str, Path],
                 coverage: dict[str, set[int] | None] | None = None) -> Trace:
    trace, calls, launched = Trace(coverage=coverage if coverage is not None else {}), {}, set()
    for event in events(text):
        kind = event.get("type")
        context = event.get("parent_tool_use_id")
        child = context is not None
        if not child and kind == "system" and event.get("subtype") == "init":
            trace.model = str(event.get("model") or "")
            trace.session = str(event.get("session_id") or "")
        if not child and kind == "result":
            if event.get("is_error"):
                trace.failed = True
                trace.error = str(event.get("result") or event.get("subtype"))[:120]
            elif event.get("subtype") == "success":
                trace.complete = True
        message = event.get("message", {})
        if kind == "assistant":
            if not child:
                if message.get("stop_reason") == "refusal":
                    trace.refused = "refusal"
                    continue
                if event.get("error") or message.get("model") == "<synthetic>":
                    trace.failed, trace.error = True, str(event.get("error") or "synthetic message")[:120]
                    continue
                trace.reached = True
            for block in message.get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name, args = block.get("name"), block.get("input") or {}
                access = json.dumps(args, ensure_ascii=False)
                calls[(context, block.get("id"))] = (name, access)
                matched = set()
                if name == "Skill":
                    selected = str(args.get("skill", ""))
                    matches = [k for k in inventory if k == selected or k.split(":")[1] == selected]
                    if len(matches) == 1:
                        matched.add(matches[0])
                        trace.attempted.update(matched)
                elif name in WRITE_TOOLS:
                    trace.writes.append(f"{name} tool")
                elif name == "Bash":
                    matched = note_command(trace, target, str(args.get("command", "")), inventory)
                else:
                    previous = set(trace.attempted)
                    matched = note_access(trace, target, access, inventory)
                    if name in {"Grep", "Glob"}:
                        trace.inspected.update(matched)
                        trace.attempted.difference_update(matched - previous)
                        matched = set()
                if child:
                    trace.child_attempted.update(matched)
        elif kind == "user" and not child:
            # 子の中間結果は親の文脈ではない。親に届いた本文だけを利用可能として保持する。
            for block in message.get("content", []):
                if block.get("type") == "tool_result":
                    name, access = calls.get((context, block.get("tool_use_id")), ("", ""))
                    failed = bool(block.get("is_error"))
                    if name == "Skill" and not failed:
                        launched.update(k for k in trace.attempted if k in access or k.split(":")[1] in access)
                    elif name == "Bash":
                        if failed:
                            trace.command_failures.append(access[:120])
                        record_result(trace, target, access, text_content(block.get("content")), inventory,
                                      allow_partial=not failed)
                    elif not failed:
                        record_result(trace, target, access, text_content(block.get("content")), inventory)
                elif block.get("type") == "text" and launched:
                    before = trace.attempted
                    trace.attempted = set(launched)
                    record_result(trace, target, "", text_content(block), inventory, claude_skill=True)
                    trace.attempted = before
                    launched.clear()
    return trace


PARSERS = {"omp": parse_omp, "codex": parse_codex, "claude": parse_claude}


def codex_contexts(env: dict[str, str], session: str) -> list[dict]:
    sessions = Path(env["CODEX_HOME"]) / "sessions"
    rollout = next(sessions.rglob(f"*{session}.jsonl"), None) if session else None
    return [item["payload"] for line in rollout.read_text(encoding="utf-8").splitlines()
            if (item := json.loads(line)).get("type") == "turn_context"] if rollout else []

def execute(client: str, base: Path, root: Path, pin: Pin, prompt: str, target: Path,
            identity: str, inventory: dict[str, Path], session: str, session_dir: Path,
            resume: bool = False, timeout: int = RUN_TIMEOUT,
            coverage: dict[str, set[int] | None] | None = None) -> tuple[subprocess.CompletedProcess[str], Trace]:
    env, _ = client_env(client, base)
    previous_contexts = len(codex_contexts(env, session)) if client == "codex" and resume else 0
    session_dir.mkdir(parents=True, exist_ok=True)
    proc = cp.run(command(client, prompt, root, pin, session, session_dir, resume),
                  env, target, timeout=timeout)
    trace = PARSERS[client](proc.stdout, identity, inventory, coverage)
    if client == "omp":
        paths = list(session_dir.glob("*.jsonl"))
        if resume and len(paths) == 1 and paths[0].resolve() == Path(session).resolve():
            trace.session = session
        elif not resume and len(paths) == 1:
            trace.session = str(paths[0])
    elif client == "claude":
        if trace.session and trace.session != session:
            trace.failed, trace.error = True, "unexpected Claude session identity"
    elif client == "codex":
        if resume and trace.session and trace.session != session:
            trace.failed, trace.error = True, "unexpected Codex session identity"
        trace.session = trace.session or (session if resume else "")
        contexts = codex_contexts(env, trace.session)
        if len(contexts) > previous_contexts:
            trace.model = str(contexts[-1].get("model") or "")
            trace.effort = str(contexts[-1].get("effort") or "")
        elif trace.reached and not trace.failed:
            trace.failed, trace.error = True, "current Codex turn context not observed"
    if proc.returncode != 0:
        trace.failed = True
        trace.error = trace.error or cp.tail(proc)
    if not trace.session:
        trace.failed = True
        trace.error = trace.error or "session identity not observed"
    if not trace.complete and not trace.refused:
        trace.failed = True
        trace.error = trace.error or "turn completion not observed"
    trace.mismatch = pin_mismatch(client, trace, pin)
    if trace.mismatch:
        trace.failed, trace.error = True, trace.mismatch
    return proc, trace


def prepare_target(target: Path, fixtures: dict[str, str]) -> set[str]:
    target.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    for name, content in fixtures.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return target_files(target)


def target_files(target: Path) -> set[str]:
    return {str(p.relative_to(target)) for p in target.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(target).parts}


def judge_safety(step: Step, trace: Trace) -> list[str]:
    problems = []
    if "write-command" in step.forbid and trace.writes:
        problems.append(f"write attempted: {trace.writes[0]}")
    if "publish-command" in step.forbid and trace.publishes:
        problems.append(f"publish attempted: {trace.publishes[0]}")
    if "new-files" in step.forbid and trace.new_files:
        problems.append(f"new files: {', '.join(trace.new_files[:3])}")
    return problems


def judge_prohibitions(step: Step, trace: Trace, target: str) -> list[str]:
    problems = []
    if not trace.mismatch:
        if step.expect == "no-load" and target in trace.attempted:
            problems.append("skill selection attempted")
        unwanted = set(step.not_reads) & trace.attempted_reads
        if unwanted:
            problems.append(f"read attempted: {', '.join(sorted(unwanted))}")
        forbidden = set(step.skills.get("forbidden", [])) & trace.attempted
        if forbidden:
            problems.append(f"forbidden skills attempted: {', '.join(sorted(forbidden))}")
        if "allowed" in step.skills:
            extra = trace.successful - set(step.skills["allowed"]) - set(step.skills.get("required", []))
            if extra:
                problems.append(f"unexpected skills loaded: {', '.join(sorted(extra))}")
    return problems + judge_safety(step, trace)


def judge(step: Step, trace: Trace, target: str, available: set[str],
          available_reads: set[str] | None = None) -> list[str]:
    problems = []
    if step.expect == "load" and target not in available:
        problems.append("skill not loaded")
    missing = set(step.reads) - (trace.reads if available_reads is None else available_reads)
    if missing:
        problems.append(f"not read: {', '.join(sorted(missing))}")
    required = set(step.skills.get("required", [])) - available
    if required:
        problems.append(f"required skills unavailable: {', '.join(sorted(required))}")
    return problems + judge_prohibitions(step, trace, target)


def run_once(client: str, base: Path, root: Path, pin: Pin, spec: Spec, query: Query,
             label: str) -> list[dict]:
    # 1. フィクスチャを基準にして、入力ファイルをエージェントの追加と区別する。
    work = base / "runs" / label
    target, sessions = work / "target", work / "sessions"
    initial = prepare_target(target, query.fixtures)
    identity, inventory = f"{spec.plugin}:{spec.skill}", skill_files(root)
    session, available, outcomes = str(uuid.uuid4()), set(), []
    coverage, available_reads = {}, set()
    # 2. 同じセッションだけを再開し、前のターンで読めた指示を引き継ぐ。
    for index, step in enumerate(query.steps):
        proc, trace = execute(client, base, root, pin, step.prompt, target, identity,
                              inventory, session, sessions, resume=index > 0, coverage=coverage)
        log = work / f"turn-{index + 1}.jsonl"
        log.write_text(proc.stdout, encoding="utf-8")
        trace.new_files = sorted(target_files(target) - initial)
        complete = trace.reached and not trace.failed and not trace.refused
        if complete:
            available.update(trace.successful)
            available_reads.update(trace.reads)
        problems = (judge(step, trace, identity, available, available_reads) if complete
                    else judge_prohibitions(step, trace, identity))
        outcomes.append({"turn": index + 1, "status": "fail" if problems else ("pass" if complete else "unmeasured"),
                         "attempted": sorted(trace.attempted), "successful": sorted(trace.successful),
                         "available": sorted(available), "reads": sorted(trace.reads),
                         "inspected": sorted(trace.inspected),
                         "available_reads": sorted(available_reads),
                         "child_attempted": sorted(trace.child_attempted),
                         "command_failures": trace.command_failures,
                         "attempted_reads": sorted(trace.attempted_reads), "problems": problems,
                         "model": trace.model, "effort": trace.effort, "error": trace.error or trace.refused,
                         "session": trace.session, "log": str(log)})
        if not complete:
            break
        session = trace.session
    return outcomes


def preflight(client: str, base: Path, root: Path, pin: Pin) -> str:
    target = base / "runs" / f"preflight-{client}" / "target"
    target.mkdir(parents=True)
    proc, trace = execute(client, base, root, pin, PREFLIGHT_PROMPT, target, "",
                          skill_files(root), str(uuid.uuid4()), target.parent / "sessions", timeout=300)
    (target.parent / "trace.jsonl").write_text(proc.stdout, encoding="utf-8")
    return "" if trace.reached and not trace.failed and not trace.refused else (trace.error or cp.tail(proc))


def auth_is_live(client: str, home: Path) -> bool:
    live = Path.home().resolve()
    auth_path = {"omp": home / ".omp/agent", "codex": home / ".codex/auth.json",
                 "claude": home / CLAUDE_TOKEN_FILE}[client]
    return home.resolve() == live or any(
        auth_path.resolve().is_relative_to(live / name) for name in (".omp", ".codex", ".claude"))


def cmd_prepare(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    market, plugins, _, results = cp.load_marketplace(root)
    if not all(r.ok for r in results):
        print("catalogs are inconsistent; run scripts/check_plugins.py first")
        return 1
    base = Path(args.homes).resolve()
    if base == Path.home().resolve():
        print("refusing to use the live home as test homes")
        return 2
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    base.chmod(0o700)
    commands = login_commands(base)
    failed = False
    for client in args.clients:
        if not shutil.which(client):
            print(f"FAIL  {client:<7} {client} not found on PATH")
            failed = True
            continue
        home, target = homes_for(base, client)
        if auth_is_live(client, home):
            print(f"FAIL  {client:<7} refusing to use live client credentials")
            failed = True
            continue
        home.mkdir(mode=0o700, parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        if has_login(client, base):
            print(f"READY {client:<7} stored credentials found")
        else:
            print(f"LOGIN {client:<7} log in once with:\n    {commands[client]}")
    options = f' --clients {",".join(args.clients)}'
    if root != REPO:
        options += f' --root "{root}"'
    homes = f' --homes "{base}"' if base != DEFAULT_HOMES else ""
    print(f"\nhomes: {base}\nthen run: python3 scripts/check_activation.py{options} run"
          f"{homes}\nThe homes keep their logins for later runs; delete them to sign out.")
    return 1 if failed else 0


def new_campaign(root: Path) -> tuple[Path, Path, dict[str, str]]:
    base = Path(tempfile.mkdtemp(prefix="skill-campaign-", dir="/tmp")).resolve()
    base.chmod(0o700)
    snapshot = base / "snapshot"
    snapshot.mkdir()
    for name in ("plugins", ".omp-plugin", ".agents", ".claude-plugin", "evals"):
        source = root / name
        if source.exists():
            shutil.copytree(source, snapshot / name)
    hashes = {str(p.relative_to(snapshot)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(snapshot.rglob("*")) if p.is_file()}
    return base, snapshot, hashes


@dataclass
class AuthLease:
    client: str
    source: Path
    dest: Path
    error: str = ""
    sync_status: str = "not-started"
    _lock: BinaryIO | None = field(default=None, init=False, repr=False)
    _initial: str = field(default="", init=False, repr=False)
    _copied: bool = field(default=False, init=False, repr=False)
    _source_auth: Path | None = field(default=None, init=False, repr=False)

    @staticmethod
    def _fingerprint(value: bytes | dict) -> str:
        if isinstance(value, dict):
            entries = [json.dumps(item, sort_keys=True) for item in value["credentials"]]
            value = json.dumps(sorted(entries)).encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def _export(home: Path, target: Path) -> dict:
        proc = subprocess.run(["omp", "auth", "export"], env=cp.base_env(home),
                              cwd=target, capture_output=True, timeout=cp.COMMAND_TIMEOUT)
        if proc.returncode:
            raise ValueError("could not export dedicated omp authentication")
        value = json.loads(proc.stdout)
        if not isinstance(value, dict) or not isinstance(value.get("credentials"), list):
            raise ValueError("invalid dedicated omp authentication export")
        return value

    @staticmethod
    def _import(value: dict, home: Path, target: Path) -> None:
        proc = subprocess.run(["omp", "auth", "import", "-"],
                              input=json.dumps(value).encode("utf-8"),
                              env=cp.base_env(home), cwd=target,
                              capture_output=True, timeout=cp.COMMAND_TIMEOUT)
        if proc.returncode:
            raise ValueError("could not import dedicated omp authentication")

    def __enter__(self) -> AuthLease:
        source_home, source_target = homes_for(self.source, self.client)
        dest_home, dest_target = homes_for(self.dest, self.client)
        try:
            if auth_is_live(self.client, source_home):
                raise ValueError("refusing to reuse live client credentials")
            if not source_home.is_dir() or not source_target.is_dir() or not has_login(self.client, self.source):
                raise ValueError("missing dedicated test-home credentials; run prepare and log in")
            dest_home.mkdir(mode=0o700, parents=True, exist_ok=True)
            dest_target.mkdir(parents=True, exist_ok=True)
            if self.client == "claude":
                token = dest_home / CLAUDE_TOKEN_FILE
                token.write_text(claude_token(self.source), encoding="utf-8")
                token.chmod(0o600)
                self.sync_status = "unchanged"
                return self

            # 1. 更新可能な認証だけをロックし、別キャンペーンによる古いトークンの再利用を防ぐ。
            self._source_auth = ((source_home / ".codex/auth.json").resolve()
                                 if self.client == "codex" else (source_home / ".omp/agent").resolve())
            lock_dir = self._source_auth.parent if self.client == "codex" else self._source_auth
            self._lock = (lock_dir / ".activation-auth.lock").open("a+b")
            os.chmod(self._lock.name, 0o600)
            fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            if self.client == "codex":
                value = self._source_auth.read_bytes()
                auth = dest_home / ".codex/auth.json"
                auth.parent.mkdir(parents=True, exist_ok=True)
                auth.write_bytes(value)
                auth.chmod(0o600)
            else:
                value = self._export(source_home, source_target)
                self._import(value, dest_home, dest_target)
            self._initial = self._fingerprint(value)
            self._copied = True
            self.sync_status = "active"
        except BlockingIOError:
            self.error = f"dedicated {self.client} authentication is in use by another campaign"
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            self.error = str(exc) if isinstance(exc, ValueError) else f"dedicated {self.client} authentication setup failed"
        return self

    def __exit__(self, *_: object) -> None:
        try:
            if not self._copied:
                return
            source_home, source_target = homes_for(self.source, self.client)
            dest_home, dest_target = homes_for(self.dest, self.client)
            if self.client == "codex":
                current = self._source_auth.read_bytes()
                updated = (dest_home / ".codex/auth.json").read_bytes()
            else:
                current = self._export(source_home, source_target)
                updated = self._export(dest_home, dest_target)
            # 2. 手動で再ログインされた場合は、その新しい認証を上書きしない。
            if self._fingerprint(current) != self._initial:
                self.sync_status = "preserved-newer-login"
                return
            if self._fingerprint(updated) == self._initial:
                self.sync_status = "unchanged"
                return
            if self.client == "codex":
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=self._source_auth.parent,
                                                     prefix=".auth-refresh-", delete=False) as output:
                        temporary = Path(output.name)
                        output.write(updated)
                    os.replace(temporary, self._source_auth)
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
            else:
                self._import(updated, source_home, source_target)
            self.sync_status = "saved"
        except (OSError, ValueError, subprocess.SubprocessError):
            self.error = f"could not preserve refreshed dedicated {self.client} authentication"
            self.sync_status = "failed"
        finally:
            if self._lock is not None:
                self._lock.close()


def installed_problems(client: str, base: Path, root: Path, market: str,
                       excluded: set[str] | None = None) -> list[str]:
    if client == "claude":
        env, target = client_env(client, base)
        return [] if registered_root(client, env, target, market) == root.resolve() else ["marketplace points elsewhere"]
    home, _ = homes_for(base, client)
    problems = []
    for identity, directory in skill_files(root).items():
        plugin, skill = identity.split(":")
        if plugin in (excluded or set()):
            continue
        copies = [p.parent for p in home.rglob(f"skills/{skill}/SKILL.md") if plugin in str(p)]
        files = {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
        if not copies or any({p.relative_to(copy): p.read_bytes() for p in copy.rglob("*") if p.is_file()} != files
                             for copy in copies):
            problems.append(f"installed {identity} differs from snapshot")
    return problems


def aggregate_status(items: list[dict], expected: int) -> str:
    if any(item["status"] == "fail" for item in items):
        return "fail"
    if len(items) == expected and all(item["status"] == "pass" for item in items):
        return "pass"
    return "unmeasured"


def cmd_run(args: argparse.Namespace) -> int:
    source, auth_base = args.root.resolve(), Path(args.homes).resolve()
    if not auth_base.is_dir():
        print(f"{auth_base} does not exist; run `prepare` first")
        return 2
    if args.report and Path(args.report).exists():
        print(f"report already exists: {args.report}")
        return 2
    paths = [Path(p) for p in args.spec] or sorted((source / "evals").glob("*/*.json"))
    # 1. 入力と分割を検証してから固定コピーを作り、認証やモデル呼び出しへ進む。
    try:
        original_specs = [load_spec(p) for p in paths]
        validate_corpus(original_specs, set(skill_files(source)))
        pins = load_pins(source, args.profile)
        selected = {item.strip() for item in args.split.split(",")} if args.split else {"train", "validation", "fresh", "behavior"}
        if not selected <= {"train", "validation", "fresh", "behavior"} or "" in selected:
            raise ValueError("invalid --split")
        ids = set(args.query)
        known = {q.id for spec in original_specs for q in spec.queries}
        if ids - known:
            raise ValueError(f"unknown query IDs: {', '.join(sorted(ids - known))}")
        base, root, hashes = new_campaign(source)
        spec_dir = base / "specs"
        spec_dir.mkdir()
        specs = []
        for index, path in enumerate(paths):
            copy = spec_dir / f"{index}.json"
            copy.write_bytes(path.read_bytes())
            hashes[f"case-specs/{index}.json"] = hashlib.sha256(copy.read_bytes()).hexdigest()
            spec = load_spec(copy)
            spec.queries = [q for q in spec.queries if q.split in selected and (not ids or q.id in ids)]
            if spec.queries:
                specs.append(spec)
        if not specs:
            raise ValueError("filters selected no queries")
        selected_ids = {q.id for spec in specs for q in spec.queries}
        if ids - selected_ids:
            raise ValueError(f"query IDs excluded by filters: {', '.join(sorted(ids - selected_ids))}")
        pins = load_pins(root, args.profile)
        market, plugins, _, catalog_results = cp.load_marketplace(root)
        if not all(r.ok for r in catalog_results):
            raise ValueError("snapshot catalogs are inconsistent")
    except (OSError, ValueError) as exc:
        print(f"spec error: {exc}")
        return 2
    report = {"campaign": str(base), "snapshot": str(root), "source": str(source),
              "source_hashes": hashes, "profile": args.profile, "repetitions": args.reps,
              "clients": {}, "cases": []}
    print(f"campaign: {base}")
    # 2. 認証の更新を保存するまでロックを保持し、設定とインストール先は分離する。
    leases = {}
    with ExitStack() as authentication:
        clients = []
        for client in args.clients:
            problem = "" if shutil.which(client) else f"{client} not found on PATH"
            try:
                if not problem:
                    leases[client] = authentication.enter_context(AuthLease(client, auth_base, base))
                    problem = leases[client].error
                if not problem:
                    failures = install(client, root, market, plugins, base)[1]
                    problem = "; ".join(failures or installed_problems(client, base, root, market))
                if not problem:
                    problem = preflight(client, base, root, pins[client])
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                problem = f"setup failed: {exc}"
            report["clients"][client] = {"model": pins[client].model, "effort": pins[client].effort,
                                          "status": "unavailable" if problem else "ready", "error": problem}
            if problem:
                print(f"FAIL  {client:<7} unavailable: {problem}")
            else:
                clients.append(client)
        # 3. 各会話を独立して実行し、失敗・未完了も反復結果に残す。
        jobs = [(si, qi, client, rep) for si, spec in enumerate(specs)
                for qi, _ in enumerate(spec.queries) for client in clients
                for rep in range(1, args.reps + 1)]
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {(si, qi, client, rep): pool.submit(
                run_once, client, base, root, pins[client], specs[si], specs[si].queries[qi],
                f"s{si}-q{qi}-{client}-{rep}") for si, qi, client, rep in jobs}
            for si, spec in enumerate(specs):
                for qi, query in enumerate(spec.queries):
                    for client in args.clients:
                        runs = []
                        if client in clients:
                            for rep in range(1, args.reps + 1):
                                try:
                                    turns = futures[(si, qi, client, rep)].result()
                                    status = aggregate_status(turns, len(query.steps))
                                    runs.append({"rep": rep, "status": status, "turns": turns})
                                except Exception as exc:
                                    runs.append({"rep": rep, "status": "unmeasured", "turns": [], "error": str(exc)})
                        status = aggregate_status(runs, args.reps)
                        report["cases"].append({"skill": f"{spec.plugin}:{spec.skill}", "id": query.id,
                                                "split": query.split, "family": query.family,
                                                "client": client, "status": status, "runs": runs})
                        print(f"{status.upper():<10} {client:<7} {spec.plugin}:{spec.skill} {query.id} "
                              f"{sum(r['status'] == 'pass' for r in runs)}/{args.reps}")
    auth_errors = {}
    for client, lease in leases.items():
        report["clients"][client]["auth_sync"] = lease.sync_status
        if lease.sync_status == "failed":
            auth_errors[client] = lease.error
            print(f"UNMEASURED {client:<7} {lease.error}")
    report["auth_sync_errors"] = auth_errors
    # 4. 全反復の証拠を保存してから合否を返し、部分的な成功を通過扱いにしない。
    report_path = Path(args.report).resolve() if args.report else base / "report.json"
    with report_path.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2, ensure_ascii=False)
        output.write("\n")
    print(f"\nreport: {report_path}")
    statuses = {case["status"] for case in report["cases"]}
    return 1 if "fail" in statuses else 2 if "unmeasured" in statuses or auth_errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO,
                        help="marketplace root (default: this repository)")
    parser.add_argument("--clients", default=",".join(cp.CLIENTS),
                        help="comma-separated subset of omp,codex,claude")
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="check dedicated test logins and print missing setup")
    prep.add_argument("--homes", type=Path, default=DEFAULT_HOMES,
                      help=f"directory for the test homes (default: {DEFAULT_HOMES})")
    runp = sub.add_parser("run", help="run cases in isolated client installations")
    runp.add_argument("--homes", type=Path, default=DEFAULT_HOMES,
                      help="directory used by prepare (default: same as prepare)")
    runp.add_argument("--profile", default="default",
                      help=f"model profile in {MODELS_FILE} (default: default)")
    runp.add_argument("--spec", action="append", default=[],
                      help="JSON spec file; repeat to select (default: evals/*/*.json)")
    runp.add_argument("--reps", type=int, default=3, help="runs per query and client")
    runp.add_argument("--jobs", type=int, default=4, help="parallel client runs")
    runp.add_argument("--split", help="comma-separated train,validation,fresh,behavior")
    runp.add_argument("--query", action="append", default=[], help="exact query ID; repeatable")
    runp.add_argument("--report", type=Path, help="JSON report destination")
    args = parser.parse_args()
    args.clients = [c.strip() for c in args.clients.split(",") if c.strip()]
    unknown = [c for c in args.clients if c not in cp.CLIENTS]
    if unknown or not args.clients:
        parser.error(f"unknown clients: {', '.join(unknown)}" if unknown
                     else "--clients needs at least one client")
    if len(set(args.clients)) != len(args.clients):
        parser.error("--clients cannot contain duplicates")
    if args.command == "run" and (args.reps < 1 or args.jobs < 1):
        parser.error("--reps and --jobs must be at least 1")
    return cmd_prepare(args) if args.command == "prepare" else cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
