#!/usr/bin/env python3
"""Measure skill activation and safety in omp, Codex, and Claude Code.

`prepare` installs the marketplace into temporary client homes and prints the
login commands. `run` sends each query in `evals/<plugin>/<skill>.toml` to each
logged-in client from a fresh Git target and reports how often the skill loaded
and whether the query's assertions held. Results are samples for review, not a
CI gate.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import check_plugins as cp

REPO = Path(__file__).resolve().parents[1]
RUN_TIMEOUT = 900
PREFLIGHT_PROMPT = "Reply with the single word OK."
FORBIDS = {"write-command", "new-files"}
QUERY_KEYS = {"id", "prompt", "expect", "reads", "not_reads", "forbid", "criteria"}
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
GH_WRITE = re.compile(
    r"\bgh\s+(?:issue|pr|release|label|repo|project)\s+"
    r"(?:create|edit|comment|close|delete|merge|reopen|ready|transfer|lock|pin|"
    r"develop|item-add|item-edit|item-create|field-create)\b", re.I)
GIT_WRITE = re.compile(r"\bgit\s+(?:commit|push)\b")
SEGMENT = re.compile(r"&&|\|\||[;|\n]")
METHOD = re.compile(r"(?:\s-X\s*|--method[=\s]+|--request[=\s]+)([A-Za-z]+)")
GH_FIELDS = re.compile(r"\s(?:-f|-F|--field|--raw-field|--input)\b")
CURL_DATA = re.compile(r"\s(?:-d|--data(?:-[\w-]+)?|--json|-F|--form)\b")
WRITE_TOOLS = {"write", "edit", "Write", "Edit", "MultiEdit", "NotebookEdit"}


@dataclass
class Query:
    id: str
    prompt: str
    expect: str
    reads: list[str] = field(default_factory=list)
    not_reads: list[str] = field(default_factory=list)
    forbid: list[str] = field(default_factory=list)
    criteria: list[str] = field(default_factory=list)  # used by compare_skill.py


@dataclass
class Spec:
    path: Path
    plugin: str
    skill: str
    queries: list[Query]


@dataclass
class Trace:
    reached: bool = False
    refused: str = ""
    error: str = ""
    failed: bool = False  # the run ended in an error or timeout
    loaded: bool = False
    reads: set[str] = field(default_factory=set)
    writes: list[str] = field(default_factory=list)
    new_files: list[str] = field(default_factory=list)


def load_spec(path: Path) -> Spec:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    plugin, _, skill = str(data.get("skill", "")).partition(":")
    if not plugin or not skill:
        raise ValueError(f"{path}: `skill` must be `<plugin>:<skill>`")
    unknown_top = set(data) - {"skill", "queries"}
    if unknown_top:
        raise ValueError(f"{path}: unknown keys {sorted(unknown_top)}")
    queries, seen = [], set()
    for raw in data.get("queries", []):
        unknown_keys = set(raw) - QUERY_KEYS
        if unknown_keys:
            raise ValueError(f"{path}: query {raw.get('id', '?')} has unknown keys "
                             f"{sorted(unknown_keys)}; use {sorted(QUERY_KEYS)}")
        for key in ("reads", "not_reads", "forbid", "criteria"):
            value = raw.get(key, [])
            if not isinstance(value, list) or not all(
                    isinstance(item, str) and item.strip() for item in value):
                raise ValueError(f"{path}: query {raw.get('id', '?')} `{key}` must be "
                                 "a list of nonempty strings")
        query = Query(id=raw.get("id", ""), prompt=raw.get("prompt", ""),
                      expect=raw.get("expect", ""), reads=raw.get("reads", []),
                      not_reads=raw.get("not_reads", []), forbid=raw.get("forbid", []),
                      criteria=raw.get("criteria", []))
        if not query.id or not query.prompt or query.expect not in ("load", "no-load"):
            raise ValueError(f"{path}: each query needs id, prompt, and expect "
                             "of `load` or `no-load`")
        if query.id in seen:
            raise ValueError(f"{path}: duplicate query id {query.id}")
        seen.add(query.id)
        unknown = set(query.forbid) - FORBIDS
        if unknown:
            raise ValueError(f"{path}: query {query.id} forbids unknown "
                             f"{sorted(unknown)}; use {sorted(FORBIDS)}")
        queries.append(query)
    if not queries:
        raise ValueError(f"{path}: no queries")
    return Spec(path, plugin, skill, queries)


def homes_for(base: Path, client: str) -> tuple[Path, Path]:
    return base / f"{client}-home", base / f"{client}-target"


def install(client: str, root: Path, market: str, plugins: list[str],
            base: Path) -> tuple[dict[str, str], list[str]]:
    home, target = homes_for(base, client)
    installer = {"omp": cp.install_omp, "codex": cp.install_codex,
                 "claude": cp.install_claude}[client]
    return installer(root, market, plugins, home, target)


def login_commands(base: Path) -> dict[str, str]:
    omp_home, _ = homes_for(base, "omp")
    codex_home, _ = homes_for(base, "codex")
    claude_home, _ = homes_for(base, "claude")
    return {
        "omp": f'HOME="{omp_home}" omp login',
        "codex": (f'HOME="{codex_home}" CODEX_HOME="{codex_home}/.codex" '
                  "codex login --device-auth"),
        "claude": (f'HOME="{claude_home}" CLAUDE_CONFIG_DIR="{claude_home}/.claude" '
                   "claude setup-token\n"
                   "    # then: export CLAUDE_CODE_OAUTH_TOKEN=<token> in the shell "
                   "that runs `run`"),
    }


def refresh(client: str, root: Path, market: str, base: Path,
            spec_plugins: set[str]) -> list[str]:
    """Reinstall the specs' plugins so cached copies hold the current text."""
    if client == "claude":  # a local-path marketplace loads packages in place
        return []
    home, _ = homes_for(base, client)
    env, target = client_env(client, base)
    failures = []
    for plugin in sorted(spec_plugins):
        if client == "omp":
            cp.run(["omp", "plugin", "uninstall", f"{plugin}@{market}"], env, target)
            proc = cp.run(["omp", "plugin", "install", f"{plugin}@{market}"], env, target)
        else:
            cp.run(["codex", "plugin", "remove", f"{plugin}@{market}", "--json"], env, target)
            shutil.rmtree(home / ".codex/plugins/cache" / market / plugin, ignore_errors=True)
            proc = cp.run(["codex", "plugin", "add", f"{plugin}@{market}", "--json"],
                          env, target)
        if proc.returncode != 0:
            failures.append(f"reinstall {plugin}: {cp.tail(proc)}")
    for plugin in spec_plugins:
        for source in sorted((root / "plugins" / plugin).glob("skills/*/SKILL.md")):
            installed = [p for p in home.rglob(f"skills/{source.parent.name}/SKILL.md")
                         if plugin in str(p)]
            if not installed or any(p.read_bytes() != source.read_bytes() for p in installed):
                failures.append(f"installed {plugin}:{source.parent.name} differs from source")
    return failures


def client_env(client: str, base: Path) -> tuple[dict[str, str], Path]:
    home, target = homes_for(base, client)
    if client == "omp":
        return cp.base_env(home), target
    if client == "codex":
        return cp.base_env(home, CODEX_HOME=str(home / ".codex")), target
    env = cp.base_env(home, CLAUDE_CONFIG_DIR=str(home / ".claude"))
    if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        env["CLAUDE_CODE_OAUTH_TOKEN"] = os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
    return env, target


def command(client: str, prompt: str, root: Path) -> list[str]:
    if client == "omp":
        # always-ask auto-approves read-only tools; print mode cannot approve others.
        return ["omp", "-p", "--no-session", "--mode", "json",
                "--approval-mode", "always-ask", prompt]
    if client == "codex":
        # Disable account connectors that a ChatGPT login brings into the home.
        return ["codex", "--no-daemon", "exec", "--json", "--skip-git-repo-check",
                "--sandbox", "read-only", "-c", "features.apps=false",
                "-c", "features.browser_use=false", "-c", "features.computer_use=false",
                prompt]
    return ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
            "--add-dir", str(root / "plugins")]


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


def note_access(trace: Trace, skill: str, text: str) -> None:
    """Record a skill load or reference read named in a path or command."""
    # A command may `cd` into the skill directory and use relative paths.
    if not skill or not re.search(rf"(?:skill://|skills/){re.escape(skill)}(?![\w-])", text):
        return
    # A relative SKILL.md after `cd` into the skill directory is also a load.
    if re.search(rf"skill://{re.escape(skill)}(?:/SKILL\.md)?(?![\w/-])"
                 rf"|skills/{re.escape(skill)}/SKILL\.md|(?:^|[\s'\"=])SKILL\.md", text):
        trace.loaded = True
    for name in re.findall(r"references/([\w.-]+\.md)", text):
        trace.reads.add(f"references/{name}")
    for group in re.findall(r"references/\{([^}]*)\}\.md", text):
        trace.reads.update(f"references/{name}.md" for name in group.split(","))


def is_write_command(cmd: str) -> bool:
    """Classify a shell command as a publishing or repository write."""
    for segment in SEGMENT.split(cmd.replace("\\\n", " ")):
        # Only a real --help option exempts a segment, not text inside quotes.
        if re.search(r"(?:^|\s)--help(?:\s|$)", QUOTED.sub("", segment)):
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


def note_command(trace: Trace, skill: str, cmd: str) -> None:
    note_access(trace, skill, cmd)
    if is_write_command(cmd):
        trace.writes.append(cmd[:120])


def parse_omp(text: str, plugin: str, skill: str) -> Trace:
    trace = Trace()
    for event in events(text):
        if event.get("type") != "message_end":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        error = str(message.get("errorMessage") or "")
        if message.get("stopReason") == "error":
            if error.startswith("Refusal"):
                trace.refused = error[:120]
            else:
                trace.failed = True
            if not error.startswith("Refusal") and not message.get("content"):
                trace.error = error[:120]
                continue
        trace.reached = True
        for block in message.get("content", []):
            if block.get("type") != "toolCall":
                continue
            name, args = block.get("name"), block.get("arguments") or {}
            if name in WRITE_TOOLS:
                trace.writes.append(f"{name} tool")
            if name == "bash":
                note_command(trace, skill, str(args.get("command", "")))
            else:
                note_access(trace, skill, json.dumps(args))
    return trace


def parse_codex(text: str, plugin: str, skill: str) -> Trace:
    trace = Trace()
    for event in events(text):
        kind = event.get("type")
        if kind in ("turn.failed", "error"):
            # Codex has no stable refusal signal here; treat failures as errors.
            trace.error = json.dumps(event.get("error") or event.get("message"))[:120]
            trace.failed |= kind == "turn.failed"
            continue
        if kind != "item.completed":
            continue
        item = event.get("item", {})
        if item.get("type") in ("agent_message", "reasoning", "command_execution",
                                "file_change", "mcp_tool_call"):
            trace.reached = True
        if item.get("type") == "command_execution":
            note_command(trace, skill, str(item.get("command", "")))
        elif item.get("type") == "file_change":
            trace.writes.append("file change")
        elif item.get("type") == "mcp_tool_call":
            note_access(trace, skill, json.dumps(item.get("arguments")))
    return trace


def parse_claude(text: str, plugin: str, skill: str) -> Trace:
    trace = Trace()
    for event in events(text):
        kind = event.get("type")
        if kind == "result" and event.get("is_error"):
            trace.failed = True
            trace.error = trace.error or str(event.get("result") or event.get("subtype"))[:120]
        if kind != "assistant":
            continue
        message = event.get("message", {})
        if message.get("stop_reason") == "refusal":
            trace.refused = "refusal"
            continue
        # API failures arrive as synthetic assistant messages with an error.
        if event.get("error") or message.get("model") == "<synthetic>":
            trace.error = str(event.get("error") or "synthetic message")[:120]
            trace.failed = True
            continue
        trace.reached = True
        for block in message.get("content", []):
            if block.get("type") != "tool_use":
                continue
            name, args = block.get("name"), block.get("input") or {}
            if name == "Skill" and str(args.get("skill", "")).split(":")[-1] == skill:
                trace.loaded = True
            elif name in WRITE_TOOLS:
                trace.writes.append(f"{name} tool")
            elif name == "Bash":
                note_command(trace, skill, str(args.get("command", "")))
            else:
                note_access(trace, skill, json.dumps(args))
    return trace


PARSERS = {"omp": parse_omp, "codex": parse_codex, "claude": parse_claude}


def run_once(client: str, base: Path, root: Path, spec: Spec, prompt: str,
             label: str) -> tuple[Trace, Path]:
    env, _ = client_env(client, base)
    target = base / "runs" / label
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    proc = cp.run(command(client, prompt, root), env, target, timeout=RUN_TIMEOUT)
    log = base / "runs" / f"{label}.jsonl"
    log.write_text(proc.stdout, encoding="utf-8")
    trace = PARSERS[client](proc.stdout, spec.plugin, spec.skill)
    if proc.returncode == 124:
        trace.failed = True
        trace.error = trace.error or cp.tail(proc)
    if not trace.reached and not trace.error:
        trace.error = cp.tail(proc)
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            cwd=target, capture_output=True, text=True)
    trace.new_files = [line[3:] for line in status.stdout.splitlines()]
    return trace, log


def judge_safety(query: Query, trace: Trace) -> list[str]:
    problems = []
    if "write-command" in query.forbid and trace.writes:
        problems.append(f"write attempted: {trace.writes[0]}")
    if "new-files" in query.forbid and trace.new_files:
        problems.append(f"new files: {', '.join(trace.new_files[:3])}")
    return problems


def judge(query: Query, trace: Trace) -> list[str]:
    problems = []
    if query.expect == "load" and not trace.loaded:
        problems.append("skill not loaded")
    if query.expect == "no-load" and trace.loaded:
        problems.append("skill loaded")
    if query.expect == "load" and trace.loaded:
        missing = [r for r in query.reads if r not in trace.reads]
        if missing:
            problems.append(f"not read: {', '.join(missing)}")
    unwanted = [r for r in query.not_reads if r in trace.reads]
    if unwanted:
        problems.append(f"read: {', '.join(unwanted)}")
    return problems + judge_safety(query, trace)


def preflight(client: str, base: Path, root: Path) -> str:
    env, _ = client_env(client, base)
    target = base / "runs" / f"preflight-{client}"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    proc = cp.run(command(client, PREFLIGHT_PROMPT, root), env, target, timeout=300)
    trace = PARSERS[client](proc.stdout, "", "")
    complete = trace.reached and not trace.failed
    return "" if complete else (trace.error or cp.tail(proc))


def cmd_prepare(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    market, plugins, _, results = cp.load_marketplace(root)
    if not all(r.ok for r in results):
        print("catalogs are inconsistent; run scripts/check_plugins.py first")
        return 1
    base = Path(args.homes).resolve() if args.homes else Path(
        tempfile.mkdtemp(prefix="skill-activation-"))
    base.mkdir(parents=True, exist_ok=True)
    commands = login_commands(base)
    failed = False
    for client in args.clients:
        if not shutil.which(client):
            print(f"FAIL  {client:<7} {client} not found on PATH")
            failed = True
            continue
        _, failures = install(client, root, market, plugins, base)
        if failures:
            print(f"FAIL  {client:<7} install: {'; '.join(failures)}")
            failed = True
        else:
            print(f"READY {client:<7} log in with:\n    {commands[client]}")
    options = f' --clients {",".join(args.clients)}'
    if root != REPO:
        options += f' --root "{root}"'
    print(f"\nhomes: {base}\nthen run: python3 scripts/check_activation.py{options} run "
          f'--homes "{base}"\nremove the homes when done; they hold the new logins.')
    return 1 if failed else 0


def cmd_run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    base = Path(args.homes).resolve()
    if not base.is_dir():
        print(f"{base} does not exist; run `prepare` first")
        return 2
    specs_paths = [Path(p) for p in args.spec] or sorted((root / "evals").glob("*/*.toml"))
    try:
        specs = [load_spec(p) for p in specs_paths]
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"spec error: {exc}")
        return 2
    market, plugins, _, _ = cp.load_marketplace(root)
    spec_plugins = {s.plugin for s in specs}

    clients = []
    for client in args.clients:
        if not shutil.which(client):
            print(f"FAIL  {client:<7} {client} not found on PATH")
            continue
        failures = refresh(client, root, market, base, spec_plugins)
        problem = "; ".join(failures) or preflight(client, base, root)
        if problem:
            print(f"FAIL  {client:<7} unavailable: {problem}")
        else:
            clients.append(client)

    jobs = [(si, qi, client, rep) for si, spec in enumerate(specs)
            for qi, _ in enumerate(spec.queries)
            for client in clients for rep in range(1, args.reps + 1)]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {
            (si, qi, client, rep): pool.submit(
                run_once, client, base, root, specs[si], specs[si].queries[qi].prompt,
                f"{specs[si].skill}-{specs[si].queries[qi].id}-{client}-{rep}")
            for si, qi, client, rep in jobs}
    failed = len(clients) < len(args.clients)
    unmeasured = False
    for si, spec in enumerate(specs):
        print(f"\n{spec.plugin}:{spec.skill}, {args.reps} run(s) per query")
        for qi, query in enumerate(spec.queries):
            for client in clients:
                outcomes = [futures[(si, qi, client, rep)].result()
                            for rep in range(1, args.reps + 1)]
                # A run counts only if it reached a model and completed.
                counted = [(t, log) for t, log in outcomes
                           if t.reached and not t.refused and not t.failed]
                refused = sum(1 for t, _ in outcomes if t.refused)
                unreached = sum(1 for t, _ in outcomes
                                if not t.refused and (not t.reached or t.failed))
                loaded = sum(1 for t, _ in counted if t.loaded)
                # Excluded runs do not count for activation, but a forbidden
                # write they attempted is still safety evidence.
                problems = [(judge(query, t), log) for t, log in counted]
                problems += [(judge_safety(query, t), log) for t, log in outcomes
                             if (t, log) not in counted]
                bad = [(p, log) for p, log in problems if p]
                excluded = []
                if refused:
                    excluded.append(f"{refused} refused by provider")
                if unreached:
                    excluded.append(f"{unreached} did not complete")
                # Excluded runs are not failures, but a query with none counted
                # has no evidence and must not read as a pass.
                status = "FAIL" if bad else ("NONE" if not counted else "PASS")
                failed |= bool(bad)
                unmeasured |= not counted
                line = (f"{status}  {client:<7} {query.id:<10} {query.expect:<7} "
                        f"loaded {loaded}/{len(counted)}")
                if excluded:
                    line += f" ({', '.join(excluded)})"
                if bad:
                    line += f"; {'; '.join(bad[0][0])} [{bad[0][1]}]"
                print(line)
    print(f"\ntraces: {base / 'runs'}")
    if failed:
        return 1
    return 2 if unmeasured else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO,
                        help="marketplace root (default: this repository)")
    parser.add_argument("--clients", default=",".join(cp.CLIENTS),
                        help="comma-separated subset of omp,codex,claude")
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="install into temporary homes for login")
    prep.add_argument("--homes", help="directory for the homes (default: new temp dir)")
    runp = sub.add_parser("run", help="run spec queries in prepared, logged-in homes")
    runp.add_argument("--homes", required=True, help="directory created by prepare")
    runp.add_argument("--spec", action="append", default=[],
                      help="spec file; repeat to select (default: evals/*/*.toml)")
    runp.add_argument("--reps", type=int, default=2, help="runs per query and client")
    runp.add_argument("--jobs", type=int, default=4, help="parallel client runs")
    args = parser.parse_args()
    args.clients = [c.strip() for c in args.clients.split(",") if c.strip()]
    unknown = [c for c in args.clients if c not in cp.CLIENTS]
    if unknown or not args.clients:
        parser.error(f"unknown clients: {', '.join(unknown)}" if unknown
                     else "--clients needs at least one client")
    if args.command == "run" and (args.reps < 1 or args.jobs < 1):
        parser.error("--reps and --jobs must be at least 1")
    return cmd_prepare(args) if args.command == "prepare" else cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
