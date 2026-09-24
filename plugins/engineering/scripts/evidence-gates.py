#!/usr/bin/env python3
"""Manage registered v2 evidence DAGs; retain explicit v1 observer history.

Python 3.9+, Git and POSIX only. Receipts bind observations to content; they do
not prove review honesty, model identity, or authorization. The passive Stop
hook never executes checks, blocks, or continues a turn.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import selectors
import time
import stat
import subprocess
import sys
import tempfile


STATE_DIR = ".engineering/gates"
REVIEWS = ("final-review", "red-team")
LIMIT = 5
MAX_JSON = 256 * 1024
MAX_REPORT = 1024 * 1024
MAX_LOG = 8 * 1024 * 1024
HOOK_SECONDS = 6
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
DIGEST = re.compile(r"sha256:[a-f0-9]{64}\Z")


class GateError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value), "invalid identifier")
    return value


def session_identity(explicit):
    if explicit:
        return identifier(explicit)
    claude = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("SONSU_CLAUDE_SESSION_ID")
    codex = os.environ.get("CODEX_THREAD_ID")
    require(not (claude and codex and claude != codex), "ambiguous host session; pass --session-id")
    return identifier(claude or codex)


def host_identity(explicit):
    if explicit:
        return explicit
    claude = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    codex = os.environ.get("CODEX_THREAD_ID")
    require(not (claude and codex), "ambiguous host; pass --host codex or --host claude-code")
    return "claude-code" if claude else "codex"


def encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode()


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON field")
        result[key] = value
    return result


def parse_json(data):
    require(len(data) <= MAX_JSON, "JSON input is too large")
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as error:
        raise GateError("invalid JSON") from error


def safe_path(path):
    """Reject symlinks in a protected path and its ancestors."""
    for part in (path, *path.parents):
        require(not part.is_symlink(), "symlink path is not supported")
    return path


def read_file(path, limit=None):
    safe_path(path)
    require(path.is_file(), "required file is unavailable")
    if limit is not None:
        require(path.stat().st_size <= limit, "file is too large")
    return path.read_bytes()


def file_digest(path):
    safe_path(path)
    require(path.is_file(), "required file is unavailable")
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            value.update(chunk)
    return "sha256:" + value.hexdigest()


def read_json(path):
    return parse_json(read_file(path, MAX_JSON))


def atomic_write(path, data):
    atomic_chunks(path, (data,))


def atomic_chunks(path, chunks):
    safe_path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as stream:
            for chunk in chunks:
                stream.write(chunk)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def workspace_env():
    local = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX",
             "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE"}
    return {key: value for key, value in os.environ.items() if key not in local}


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], env=workspace_env(),
                            capture_output=True, timeout=15)
    require(result.returncode == 0, "Git workspace query failed")
    return result.stdout


def workspace(cwd):
    return Path(os.fsdecode(git(Path(cwd).resolve(), "rev-parse", "--show-toplevel")).strip()).resolve()


def relative_input(value):
    require(isinstance(value, str) and value and "\x00" not in value, "invalid input path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and
            not any(p in (".", "..", ".git") for p in path.parts), "input path must be relative and canonical")
    require(value != STATE_DIR and not value.startswith(STATE_DIR + "/"), "state cannot be an artifact")
    return value


def config_validate(config, root):
    require(isinstance(config, dict) and set(config) == {"inputs", "checks"}, "invalid task configuration")
    inputs = config["inputs"]
    require(isinstance(inputs, list) and 0 < len(inputs) <= 32, "declare plan/contract inputs")
    for name in inputs:
        relative_input(name)
    require(len(set(inputs)) == len(inputs), "duplicate input path")
    checks = config["checks"]
    require(isinstance(checks, list) and 0 < len(checks) <= 32, "declare required checks")
    ids = []
    for check in checks:
        require(isinstance(check, dict) and set(check) == {"id", "argv"}, "invalid check definition")
        ids.append(identifier(check["id"]))
        argv = check["argv"]
        require(isinstance(argv, list) and 0 < len(argv) <= 128 and
                all(isinstance(x, str) and x and "\x00" not in x and len(x) <= 16384 for x in argv), "invalid check argv")
    require(len(set(ids)) == len(ids), "duplicate check identifier")
    return config


def snapshot(root, config):
    names = set(os.fsdecode(x) for x in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if x)
    names.update(config["inputs"])
    entries = []
    for name in sorted(names):
        if name == STATE_DIR or name.startswith(STATE_DIR + "/"):
            continue
        path = root / name
        safe_path(path.parent)
        if name in config["inputs"]:
            require(path.is_file(), "declared input is missing or not a file")
        if path.is_symlink():
            entries.append([name, "symlink", os.readlink(path)])
        elif not path.exists():
            entries.append([name, "deleted"])
        else:
            require(path.is_file(), "submodules and directory artifacts are not supported")
            entries.append([name, bool(path.stat().st_mode & stat.S_IXUSR), digest(path.read_bytes())])
    package = Path(__file__).resolve().parents[1]
    policies = ("references/quality-gates.md",
                "references/code-quality.md",
                "references/review-criteria.md",
                "references/javascript-typescript-review.md",
                "references/review/code-reviewer.md",
                "references/review/red-team-reviewer.md")
    return digest(encode({"files": entries, "config": config,
                          "index": digest(git(root, "ls-files", "--stage", "-v", "-z")),
                          "staged_diff": digest(git(root, "diff", "--cached", "--raw", "--no-renames",
                                                    "--no-ext-diff", "--no-abbrev", "-z")),
                          "head": digest(git(root, "rev-parse", "--revs-only", "HEAD")),
                          "runtime": digest(Path(__file__).read_bytes()),
                          "policy": {name: file_digest(package / name) for name in policies}}))


def exclude_state(root):
    path = Path(os.fsdecode(git(root, "rev-parse", "--git-path", "info/exclude")).strip())
    if not path.is_absolute():
        path = root / path
    safe_path(path)
    rule = b"/" + STATE_DIR.encode() + b"/"
    if path.is_file() and rule in path.read_bytes().splitlines():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        original = stream.read()
        if rule not in original.splitlines():
            stream.write((b"\n" if original and not original.endswith(b"\n") else b"") + rule + b"\n")


@contextmanager
def lock(root, wait=False):
    directory = safe_path(root / STATE_DIR)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = safe_path(directory / ".lock")
    with path.open("a+b") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | (0 if wait else fcntl.LOCK_NB))
        except BlockingIOError as error:
            raise GateError("gate state is busy; retry after the current write") from error
        yield


def task_path(root, task):
    return safe_path(root / STATE_DIR / "tasks" / identifier(task) / "state.json")


def session_path(root, session):
    return safe_path(root / STATE_DIR / "sessions" / (identifier(session) + ".json"))


def save(root, state):
    data = encode(state)
    require(len(data) <= MAX_JSON, "task state is too large")
    atomic_write(task_path(root, state["task_id"]), data)


def load(root, task):
    state = read_json(task_path(root, task))
    require(isinstance(state, dict) and set(state) == {"schema_version", "workspace_root", "task_id", "config", "config_history", "sessions", "closed", "checks", "reviews"}, "invalid task state")
    require(type(state["schema_version"]) is int and state["schema_version"] == 1 and
            state["workspace_root"] == str(root) and state["task_id"] == task, "task identity or schema mismatch")
    require(state["closed"] in (False, "complete", "superseded"), "invalid task lifecycle")
    require(isinstance(state["sessions"], list) and 0 < len(state["sessions"]) <= 128, "invalid session history")
    for session in state["sessions"]:
        identifier(session)
    config_validate(state["config"], root)
    require(isinstance(state["config_history"], list) and len(state["config_history"]) <= 32, "invalid configuration history")
    for config in state["config_history"]:
        config_validate(config, root)
    require(isinstance(state["checks"], dict) and set(state["checks"]) == {x["id"] for x in state["config"]["checks"]}, "check definitions do not match receipts")
    require(isinstance(state["reviews"], dict) and set(state["reviews"]) == set(REVIEWS), "review gates are missing")
    for name, attempts in list(state["checks"].items()) + list(state["reviews"].items()):
        require(isinstance(attempts, list) and len(attempts) <= LIMIT, "invalid attempt history")
        for index, receipt in enumerate(attempts, 1):
            require(isinstance(receipt, dict) and type(receipt.get("attempt")) is int and receipt["attempt"] == index and
                    receipt.get("outcome") in ("pending", "passed", "failed", "blocked", "inconclusive"), "invalid receipt")
            require(receipt.get("execution") in ("complete", "incomplete"), "invalid execution state")
            require(isinstance(receipt.get("artifact_digest"), str) and DIGEST.fullmatch(receipt["artifact_digest"]), "invalid artifact digest")
            require(isinstance(receipt.get("dependencies"), str) and DIGEST.fullmatch(receipt["dependencies"]), "invalid dependency digest")
            require(isinstance(receipt.get("files"), dict), "invalid receipt evidence")
            for filename, fingerprint in receipt["files"].items():
                require(isinstance(filename, str) and re.fullmatch(r"[A-Za-z0-9_-]+\.(?:log|md)", filename), "invalid evidence path")
                require(isinstance(fingerprint, str) and DIGEST.fullmatch(fingerprint), "invalid evidence digest")
            if receipt["outcome"] == "passed":
                require(bool(receipt["files"]), "passing receipt has no evidence")
                if name in REVIEWS and attempts is state["reviews"].get(name):
                    require(receipt.get("verdict") == ("passed" if name == "final-review" else "survives_challenge"), "invalid review verdict")
                    identifier(receipt.get("reviewer_id"))
                else:
                    require(type(receipt.get("exit_code")) is int and receipt["exit_code"] == 0, "check did not pass")
    return state


def dependency_digest(state, gate):
    if gate == "final-review":
        value = {name: rows[-1] if rows else None for name, rows in state["checks"].items()}
    elif gate == "red-team":
        value = state["reviews"]["final-review"][-1:]  # includes its verification dependency
    else:
        value = None
    return digest(encode(value))


def receipt_status(root, state, rows, artifact, dependencies, dependency_ready=True):
    if not rows:
        return "not_run"
    receipt = rows[-1]
    if receipt["outcome"] == "pending" or receipt["artifact_digest"] != artifact or receipt["dependencies"] != dependencies or not dependency_ready:
        return "inconclusive"
    directory = task_path(root, state["task_id"]).parent
    try:
        if any(file_digest(directory / name) != expected for name, expected in receipt["files"].items()):
            return "inconclusive"
    except (GateError, OSError):
        return "inconclusive"
    return receipt["outcome"]


def inspect(root, state):
    artifact = snapshot(root, state["config"])
    checks = {name: {"status": receipt_status(root, state, rows, artifact, dependency_digest(state, "check")),
                     "attempts": len(rows), "execution": rows[-1]["execution"] if rows else "not_run"}
              for name, rows in state["checks"].items()}
    values = [item["status"] for item in checks.values()]
    verification = next((value for value in ("failed", "blocked", "inconclusive", "not_run") if value in values), "passed")
    gates = {"verification": verification}
    for gate, dependency in (("final-review", "verification"), ("red-team", "final-review")):
        gates[gate] = receipt_status(root, state, state["reviews"][gate], artifact,
                                    dependency_digest(state, gate), gates[dependency] == "passed")
    return {"mode": "observe", "task_id": state["task_id"], "artifact_digest": artifact,
            "ready": all(value == "passed" for value in gates.values()), "gates": gates,
            "checks": checks, "attempts": {name: len(rows) for name, rows in state["reviews"].items()}}


def initialize(root, args, supplied=None):
    config = config_validate(supplied if supplied is not None else parse_json(sys.stdin.buffer.read(MAX_JSON + 1)), root)
    snapshot(root, config)  # reject unreadable inputs before any persistent write
    session = session_identity(args.session_id)
    path = task_path(root, args.task_id)
    pointer = session_path(root, session)
    with lock(root):
        if pointer.exists():
            current = read_json(pointer)
            require(isinstance(current, dict) and set(current) == {"task_id"}, "invalid session pointer")
            if current["task_id"] != args.task_id:
                require(load(root, current["task_id"])["closed"], "session already has an active task")
        if path.exists():
            state = load(root, args.task_id)
            require(state["config"] == config, "task configuration changed; reconcile the existing task instead of resetting its budget")
            if session not in state["sessions"]:
                require(not any(row.get("reviewer_id") == session for rows in state["reviews"].values() for row in rows),
                        "session conflicts with an existing reviewer")
                require(len(state["sessions"]) < 128, "session history is full")
                state["sessions"].append(session)
            state["closed"] = False
        else:
            state = {"schema_version": 1, "workspace_root": str(root), "task_id": identifier(args.task_id),
                     "config": config, "config_history": [], "sessions": [session], "closed": False,
                     "checks": {x["id"]: [] for x in config["checks"]}, "reviews": {gate: [] for gate in REVIEWS}}
        exclude_state(root)
        save(root, state)
        atomic_write(pointer, encode({"task_id": args.task_id}))
    return inspect(root, state)


def revise(root, args, supplied=None):
    config = config_validate(supplied if supplied is not None else parse_json(sys.stdin.buffer.read(MAX_JSON + 1)), root)
    snapshot(root, config)
    with lock(root):
        state = load(root, args.task_id)
        require(not state["closed"], "task is closed")
        require({x["id"] for x in config["checks"]} == set(state["checks"]), "revise must preserve check IDs and their budgets")
        require(all(not rows or rows[-1]["outcome"] != "pending" for rows in
                    list(state["checks"].values()) + list(state["reviews"].values())), "record or abandon pending attempts before revising")
        if config != state["config"]:
            require(len(state["config_history"]) < 32, "configuration history is full")
            state["config_history"].append(state["config"])
            state["config"] = config
            save(root, state)
        return inspect(root, state)


def reserve(root, state, rows, gate):
    require(not state["closed"], "task is closed; explicitly resume it with init")
    require(not rows or rows[-1]["outcome"] != "pending", "attempt is pending; record or abandon it first")
    require(len(rows) < LIMIT, "attempt budget exhausted")
    status = inspect(root, state)
    if gate in REVIEWS:
        dependency = "verification" if gate == "final-review" else "final-review"
        require(status["gates"][dependency] == "passed", "review dependency is not currently passed")
    receipt = {"attempt": len(rows) + 1, "outcome": "pending", "execution": "incomplete", "artifact_digest": status["artifact_digest"],
               "dependencies": dependency_digest(state, gate), "files": {}}
    rows.append(receipt)
    return receipt


def pending(rows, attempt):
    require(rows and rows[-1]["attempt"] == attempt and rows[-1]["outcome"] == "pending", "attempt is not the current pending reservation")
    return rows[-1]


def run_check(root, args):
    with lock(root):
        state = load(root, args.task_id)
        require(args.check in state["checks"], "unknown check")
        receipt = reserve(root, state, state["checks"][args.check], "check")
        argv = next(x["argv"] for x in state["config"]["checks"] if x["id"] == args.check)
        save(root, state)  # a crash must consume the reserved attempt
    name = "check-" + args.check + "-" + str(receipt["attempt"]) + ".log"
    path = safe_path(task_path(root, args.task_id).parent / name)
    outcome, exit_code = "inconclusive", None
    with path.open("xb") as output:
        process = None
        try:
            process = subprocess.Popen(argv, cwd=root, env=workspace_env(), stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            deadline = time.monotonic() + args.timeout
            written = 0
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(argv, args.timeout)
                    for key, _ in selector.select(remaining):
                        chunk = os.read(key.fd, 64 * 1024)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        available = MAX_LOG - written
                        output.write(chunk[:available])
                        written += min(len(chunk), available)
                        if len(chunk) > available:
                            raise GateError("check output exceeded log limit")
            exit_code = process.wait(timeout=max(0, deadline - time.monotonic()))
            outcome = "passed" if exit_code == 0 else "failed"
        except GateError:
            outcome = "inconclusive"
            marker = b"\ncheck output exceeded log limit; execution interrupted\n"
            output.seek(MAX_LOG - len(marker))
            output.write(marker)
        except subprocess.TimeoutExpired:
            outcome = "inconclusive"
            marker = b"\ncheck timed out before completion\n"
            output.seek(min(output.tell(), MAX_LOG - len(marker)))
            output.write(marker)
        except OSError as error:
            outcome = "blocked"
            output.write(("process could not start (errno " + str(error.errno) + ")\n").encode())
        finally:
            if process is not None:
                # Descendants may retain the pipe after the direct child exits.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                process.stdout.close()
    with lock(root, wait=True):
        state = load(root, args.task_id)
        current = pending(state["checks"][args.check], receipt["attempt"])
        current.update(outcome="inconclusive", execution="complete" if exit_code is not None else "incomplete",
                       exit_code=exit_code)
        try:
            current["files"] = {name: file_digest(path)}
            if snapshot(root, state["config"]) == current["artifact_digest"]:
                current["outcome"] = outcome
        finally:
            save(root, state)  # retain completed execution facts even if evidence cannot be inspected
        return inspect(root, state)


def prepare_review(root, args):
    source = safe_path(Path(args.package).absolute())
    require(source.is_file(), "required file is unavailable")
    # Freeze the input before reserving an attempt; package size is independent of reports.
    with tempfile.TemporaryFile() as frozen:
        value, nonempty = hashlib.sha256(), False
        with source.open("rb") as stream:
            for chunk in iter(lambda: stream.read(64 * 1024), b""):
                nonempty = nonempty or bool(chunk.strip())
                value.update(chunk)
                frozen.write(chunk)
        require(nonempty, "review package is empty")
        fingerprint = "sha256:" + value.hexdigest()
        frozen.seek(0)
        with lock(root):
            state = load(root, args.task_id)
            receipt = reserve(root, state, state["reviews"][args.gate], args.gate)
            name = args.gate + "-" + str(receipt["attempt"]) + "-input.md"
            path = task_path(root, args.task_id).parent / name
            require(not path.exists(), "review package already exists")
            receipt["files"][name] = fingerprint
            save(root, state)
            atomic_chunks(path, iter(lambda: frozen.read(64 * 1024), b""))
            return {"gate": args.gate, "attempt": receipt["attempt"], "artifact_digest": receipt["artifact_digest"],
                    "package": str(path), "package_digest": fingerprint}


def record_review(root, args):
    verdicts = ({"passed": "passed", "failed": "failed"} if args.gate == "final-review"
                else {"survives_challenge": "passed", "invalidated": "failed"})
    verdicts.update(inconclusive="inconclusive", blocked="blocked")
    require(args.verdict in verdicts, "invalid verdict for this review stage")
    reviewer = identifier(args.reviewer_id)
    content = read_file(Path(args.report).absolute(), MAX_REPORT)
    require(content.strip(), "review report is empty")
    with lock(root):
        state = load(root, args.task_id)
        require(not state["closed"], "task is closed")
        receipt = pending(state["reviews"][args.gate], args.attempt)
        require(reviewer not in state["sessions"], "reviewer must differ from the controller")
        if args.gate == "red-team":
            require(reviewer != state["reviews"]["final-review"][-1].get("reviewer_id"), "red-team requires a different reviewer")
        status = inspect(root, state)
        dependency = "verification" if args.gate == "final-review" else "final-review"
        require(receipt["artifact_digest"] == status["artifact_digest"] and
                receipt["dependencies"] == dependency_digest(state, args.gate) and
                status["gates"][dependency] == "passed", "review reservation is stale")
        directory = task_path(root, args.task_id).parent
        require(all(file_digest(directory / name) == expected for name, expected in receipt["files"].items()), "review package is stale")
        name = args.gate + "-" + str(args.attempt) + "-report.md"
        path = directory / name
        if path.exists():
            require(read_file(path, MAX_REPORT) == content, "different report already exists for this reservation")
        else:
            atomic_write(path, content)
        receipt["files"][name] = digest(content)
        receipt.update(outcome=verdicts[args.verdict], execution="complete", verdict=args.verdict, reviewer_id=reviewer)
        save(root, state)
        return inspect(root, state)


def finish(root, args):
    with lock(root):
        state = load(root, args.task_id)
        require(not state["closed"], "task is closed; explicitly resume it with init")
        if args.command == "abandon":
            rows = state["reviews"].get(args.gate)
            if args.gate.startswith("check:"):
                rows = state["checks"].get(args.gate[6:])
            require(rows is not None, "unknown gate")
            pending(rows, args.attempt)["outcome"] = "inconclusive"
        else:
            require(args.outcome == "superseded" or inspect(root, state)["ready"], "completion evidence is missing or stale")
            state["closed"] = args.outcome
        save(root, state)
        return inspect(root, state)


class ObservationTimeout(Exception):
    pass


def observation_timeout(signum, frame):
    raise ObservationTimeout("observation time budget exceeded")


def hook():
    previous = signal.signal(signal.SIGALRM, observation_timeout)
    signal.setitimer(signal.ITIMER_REAL, HOOK_SECONDS)
    try:
        return observe_hook()
    except ObservationTimeout:
        return {"systemMessage": "Engineering 관찰: 실행 시간을 초과해 완료 근거를 확인하지 못했습니다. evidence-gates의 status로 확인하세요."}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def observe_hook():
    event = parse_json(sys.stdin.buffer.read(MAX_JSON + 1))
    require(isinstance(event, dict), "invalid hook event")
    if event.get("hook_event_name") != "Stop" or event.get("agent_id") is not None or event.get("parent_session_id") is not None or event.get("permission_mode") == "plan":
        return None
    require(isinstance(event.get("cwd"), str) and Path(event["cwd"]).is_absolute(), "invalid hook cwd")
    cwd = Path(event["cwd"]).resolve()
    if not any((path / ".git").exists() or (path / ".git").is_symlink()
               for path in (cwd, *cwd.parents)):
        return None
    root = workspace(cwd)
    pointer = session_path(root, event.get("session_id"))
    if not pointer.exists():
        return None
    current = read_json(pointer)
    require(isinstance(current, dict) and set(current) == {"task_id"}, "invalid session pointer")
    # Only registered tasks write observations; status never mutates receipts.
    with lock(root):
        raw = read_json(task_path(root, identifier(current["task_id"])))
        managed = raw.get("schema_version") == 2
        if managed:
            import evidence_gates_v2
            evidence_gates_v2.G = sys.modules[__name__]
            state = evidence_gates_v2.load(root, current["task_id"])
        else:
            state = load(root, current["task_id"])
        require(event["session_id"] in state["sessions"], "session is not registered for this task")
        if state["closed"]:
            return None
        try:
            status = evidence_gates_v2.inspect(root, state) if managed else inspect(root, state)
        except ObservationTimeout:
            status = {"mode": "observe", "task_id": state["task_id"], "ready": False,
                      "observation": "inconclusive", "reason": "time_budget_exceeded"}
        path = task_path(root, state["task_id"]).parent / "observation.json"
        previous = read_json(path) if path.exists() else None
        if previous == status:
            return None
        atomic_write(path, encode(status))
        if status.get("reason") == "time_budget_exceeded":
            return {"systemMessage": "Engineering 관찰: 실행 시간을 초과해 완료 근거를 확인하지 못했습니다. evidence-gates의 status로 확인하세요."}
        if not status["ready"]:
            return {"systemMessage": "Engineering 관찰: 현재 변경의 완료 근거가 누락되었거나 오래되었습니다. evidence-gates의 status로 확인하세요. 이 알림은 작업을 차단하거나 실행 권한을 부여하지 않습니다."}
    return None


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cwd", default=os.getcwd())
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("hook")
    for command in ("init", "revise", "status", "check", "run", "prepare-review", "record-review", "abandon", "close", "ready", "enter", "complete-unit", "adjudicate"):
        item = sub.add_parser(command)
        item.add_argument("--task-id", required=True)
        item.add_argument("--unit")
        if command in ("enter", "complete-unit"):
            item.add_argument("--request-id", required=True)
        if command == "init":
            item.add_argument("--session-id")
            item.add_argument("--host", choices=("codex", "claude-code"))
        elif command == "run":
            item.add_argument("--check", required=True)
            item.add_argument("--timeout", type=float, default=300)
        elif command in ("prepare-review", "record-review", "abandon", "adjudicate"):
            item.add_argument("--gate", required=command != "abandon", **({"choices": REVIEWS} if command != "abandon" else {}))
            if command == "prepare-review":
                item.add_argument("--package", required=True)
            else:
                item.add_argument("--attempt", required=command != "abandon", type=int)
            if command == "record-review":
                item.add_argument("--verdict")
                item.add_argument("--reviewer-id", required=True)
                item.add_argument("--report", required=True)
        elif command == "close":
            item.add_argument("--outcome", choices=("complete", "superseded", "accepted_risk"), default="complete")
    return p


def main():
    args = parser().parse_args()
    try:
        if args.command == "hook":
            result = hook()
        else:
            identifier(args.task_id)
            root = workspace(args.cwd)
            supplied = parse_json(sys.stdin.buffer.read(MAX_JSON + 1)) if args.command in ("init", "revise") else None
            if args.command in ("init", "revise"):
                require(isinstance(supplied, dict), "configuration must be a JSON object")
            managed = supplied.get("schema_version") == 2 if supplied is not None else (
                read_json(task_path(root, args.task_id)).get("schema_version") == 2)
            if managed:
                import evidence_gates_v2
                result = evidence_gates_v2.dispatch(sys.modules[__name__], root, args, supplied)
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
                if args.command == "check":
                    return 0 if result["ready"] else 1
                if args.command == "run":
                    return 0 if result["outcome"] == "passed" else 1
                return 0
            if args.command == "close" and args.outcome == "accepted_risk":
                raise GateError("accepted_risk requires a v2 task")
            if args.command == "abandon":
                require(args.gate is not None and args.attempt is not None, "legacy abandon requires gate and attempt")
            if args.command in ("ready", "enter", "complete-unit", "adjudicate") or args.unit:
                raise GateError("managed commands require a v2 task; legacy receipts cannot pass v2")
            if args.command == "init":
                result = initialize(root, args, supplied)
            elif args.command == "revise":
                result = revise(root, args, supplied)
            elif args.command in ("status", "check"):
                result = inspect(root, load(root, args.task_id))
            elif args.command == "run":
                require(0 < args.timeout <= 3600, "timeout must be between 0 and 3600 seconds")
                result = run_check(root, args)
            elif args.command == "prepare-review":
                result = prepare_review(root, args)
            elif args.command == "record-review":
                result = record_review(root, args)
            else:
                result = finish(root, args)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        if args.command == "check":
            return 0 if result["ready"] else 1
        if args.command == "run":
            return 0 if result["checks"][args.check]["status"] == "passed" else 1
        return 0
    except (GateError, OSError, ValueError, TypeError, subprocess.SubprocessError) as error:
        if args.command == "hook":
            print("Engineering gate observation unavailable; existing evidence was preserved.", file=sys.stderr)
            return 0
        print("evidence-gates: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
