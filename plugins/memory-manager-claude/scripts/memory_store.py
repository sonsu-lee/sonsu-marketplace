#!/usr/bin/env python3
"""Local, host-neutral memory store. Markdown is authoritative; SQLite is disposable."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
import tempfile
import uuid


META_OPEN = "<!-- sonsu-memory-meta\n"
META_CLOSE = "\n-->\n"
ID_RE = re.compile(r"[0-9a-f]{32}\Z")
PROJECT_RE = re.compile(r"[0-9a-f]{20}\Z")
SECRET_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----|"
    r"\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|access[_-]?token|password|secret|token|"
    r"client[_-]?secret|aws[_-]?secret[_-]?access[_-]?key|private[_-]?key)"
    r"(?:\\*[\"'])?\s*[:=]\s*\S+|"
    r"\b(?:password|passphrase|api[ _-]?key|access[ _-]?token|secret|token)"
    r"\s+(?:is|was|are)\s+\S+|"
    r"(?:비밀번호|암호|비밀[ _-]?키|API[ _-]?키|토큰)"
    r"\s*(?:은|는|이|가|:|=)\s*\S+|"
    r"\bauthorization\s*:\s*(?:bearer|basic)\s+\S+|"
    r"\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}|"
    r"\bAKIA[0-9A-Z]{16}\b", re.I
)
SIGNAL_RE = re.compile(r"기억해|기억해 줘|기억하|결정했|확정했|원인은|해결했|remember|decided|resolved|root cause", re.I)
SKIP_RE = re.compile(
    r"기억(?:하지|해\s*주지)\s*(?:마|말|않)|저장하지\s*(?:마|말|않)|"
    r"(?:do not|don['’]t|never)\s+(?:remember|save|store)", re.I
)


class StoreError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def root_path():
    override = os.environ.get("SONSU_MEMORY_HOME")
    root = Path(override).expanduser() if override else Path.home() / ".sonsu" / "memory-manager"
    if not root.is_absolute():
        raise StoreError("unsafe_path")
    for component in (root, *root.parents):
        if component.is_symlink():
            raise StoreError("unsafe_path")
    return root


def project_key(cwd):
    location = Path(cwd).expanduser().resolve(strict=True)
    if not location.is_dir():
        raise StoreError("invalid_project")
    result = subprocess.run(
        ["git", "-C", str(location), "rev-parse", "--git-common-dir"],
        capture_output=True, text=True, check=False,
    )
    common_dir = result.stdout.strip()
    identity = (location / common_dir).resolve() if result.returncode == 0 and common_dir else location
    return digest(str(identity).encode("utf-8"))[:20]


def checked_path(root, path):
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise StoreError("unsafe_path")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise StoreError("unsafe_path")
    return path


def ensure_private_dir(root, path):
    checked_path(root, path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.is_dir() or path.is_symlink():
        raise StoreError("unsafe_path")
    os.chmod(path, 0o700)


def safe_read(root, path):
    checked_path(root, path)
    if not path.exists():
        raise StoreError("not_found")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise StoreError("unsafe_path")
        with os.fdopen(fd, "rb", closefd=False) as source:
            return source.read()
    finally:
        os.close(fd)


def atomic_write(root, path, data):
    checked_path(root, path)
    ensure_private_dir(root, path.parent)
    if path.exists() and not path.is_file():
        raise StoreError("unsafe_path")
    fd, name = tempfile.mkstemp(prefix=".memory-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        checked_path(root, path)
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(root):
    ensure_private_dir(root, root)
    lock_file = checked_path(root, root / ".lock")
    fd = os.open(lock_file, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise StoreError("unsafe_path")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def note_dir(root, scope, key):
    if scope == "user":
        return root / "notes" / "user"
    if scope == "project":
        return root / "notes" / "projects" / key
    raise StoreError("invalid_scope")


def note_path(root, scope, key, note_id):
    if not isinstance(note_id, str) or not ID_RE.fullmatch(note_id):
        raise StoreError("invalid_id")
    return note_dir(root, scope, key) / (note_id + ".md")


def encode_note(meta, body):
    metadata = json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2)
    return (META_OPEN + metadata + META_CLOSE + "# " + meta["title"] + "\n\n" + body.rstrip() + "\n").encode("utf-8")


def decode_note(data):
    try:
        text = data.decode("utf-8")
        if not text.startswith(META_OPEN):
            raise ValueError("missing metadata")
        metadata_text, content = text[len(META_OPEN):].split(META_CLOSE, 1)
        meta = json.loads(metadata_text)
        if not isinstance(meta, dict):
            raise ValueError("invalid metadata")
        if not isinstance(meta.get("id"), str) or not ID_RE.fullmatch(meta["id"]):
            raise ValueError("invalid id")
        if meta.get("scope") not in ("user", "project") or not isinstance(meta.get("project"), str):
            raise ValueError("invalid scope")
        if meta["scope"] == "user" and meta["project"] != "":
            raise ValueError("invalid user project")
        if meta["scope"] == "project" and not PROJECT_RE.fullmatch(meta["project"]):
            raise ValueError("invalid project key")
        if meta.get("status") not in ("active", "archived", "superseded"):
            raise ValueError("invalid status")
        if not isinstance(meta.get("title"), str) or not meta["title"] or "\n" in meta["title"]:
            raise ValueError("invalid title")
        for field in ("created_at", "verified_at"):
            if not isinstance(meta.get(field), str) or not meta[field]:
                raise ValueError("invalid timestamp")
        if not isinstance(meta.get("sources"), list) or not all(isinstance(x, str) for x in meta["sources"]):
            raise ValueError("invalid sources")
        if not isinstance(meta.get("supersedes"), list) or not all(
            isinstance(x, str) and ID_RE.fullmatch(x) for x in meta["supersedes"]
        ) or meta["id"] in meta["supersedes"]:
            raise ValueError("invalid supersedes")
        heading = "# " + meta["title"] + "\n\n"
        if not content.startswith(heading):
            raise ValueError("invalid heading")
        meta["body"] = content[len(heading):].rstrip("\n")
        meta["sha256"] = digest(data)
        return meta
    except (UnicodeError, ValueError, KeyError, TypeError):
        raise StoreError("invalid_note")


def read_note(root, scope, key, note_id):
    path = note_path(root, scope, key, note_id)
    note = decode_note(safe_read(root, path))
    validate_note_location(root, path, note)
    return note


def validate_note_location(root, path, note):
    expected = note_path(root, note["scope"], note["project"], note["id"])
    if path != expected:
        raise StoreError("invalid_note")


def iter_notes(root):
    base = root / "notes"
    if not base.exists():
        return
    checked_path(root, base)
    for path in sorted(base.glob("**/*.md")):
        try:
            checked_path(root, path)
            if path.is_file():
                note = decode_note(safe_read(root, path))
                validate_note_location(root, path, note)
                yield note, path
        except (StoreError, OSError):
            continue


def active_notes(root):
    notes = list(iter_notes(root))
    superseded = {(note["scope"], note["project"], old) for note, _ in notes
                  if note["status"] == "active" for old in note["supersedes"]}
    return [(note, path) for note, path in notes if note["status"] == "active" and
            (note["scope"], note["project"], note["id"]) not in superseded]


def finalize_superseded_parents(root, note):
    """Finish an interrupted supersede before deactivating its successor."""
    for old_id in note["supersedes"]:
        try:
            old = read_note(root, note["scope"], note["project"], old_id)
        except StoreError as error:
            if error.code == "not_found":
                continue
            raise
        if old["status"] == "active":
            meta = {k: v for k, v in old.items() if k not in ("body", "sha256")}
            meta["status"] = "superseded"
            atomic_write(root, note_path(root, old["scope"], old["project"], old_id),
                         encode_note(meta, old["body"]))


def rebuild_index(root):
    ensure_private_dir(root, root)
    fd, name = tempfile.mkstemp(prefix=".index-", suffix=".sqlite3", dir=root)
    os.close(fd)
    try:
        connection = sqlite3.connect(name)
        try:
            connection.execute("CREATE VIRTUAL TABLE memories USING fts5(id UNINDEXED, scope UNINDEXED, project UNINDEXED, title, body)")
            for note, _ in active_notes(root):
                connection.execute("INSERT INTO memories (id, scope, project, title, body) VALUES (?, ?, ?, ?, ?)",
                                   (note["id"], note["scope"], note.get("project", ""), note["title"], note["body"]))
            connection.commit()
        finally:
            connection.close()
        os.chmod(name, 0o600)
        target = checked_path(root, root / "index.sqlite3")
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def refresh_index(root):
    try:
        rebuild_index(root)
        return True
    except (sqlite3.DatabaseError, OSError, StoreError):
        return False


def index_is_stale(root):
    index = root / "index.sqlite3"
    if not index.exists():
        return True
    indexed_at = index.stat().st_mtime_ns
    base = root / "notes"
    if not base.exists():
        return False
    for path in base.glob("**/*.md"):
        try:
            checked_path(root, path)
            if path.stat().st_mtime_ns > indexed_at:
                return True
        except (StoreError, OSError):
            continue
    return False


def validate_content(title, body, sources):
    if not isinstance(title, str) or not title.strip() or "\n" in title or len(title) > 180:
        raise StoreError("invalid_content")
    if not isinstance(body, str) or not body.strip() or len(body) > 20000:
        raise StoreError("invalid_content")
    if not isinstance(sources, list) or not sources or not all(isinstance(x, str) and x.strip() and len(x) < 1000 for x in sources):
        raise StoreError("invalid_sources")
    if SECRET_RE.search("\n".join([title, body, *sources])):
        raise StoreError("sensitive_content")


def put(root, key, request):
    if not isinstance(request, dict):
        raise StoreError("invalid_request")
    decision = request.get("decision")
    if decision == "NOOP":
        return {"decision": "NOOP"}
    if decision not in ("ADD", "UPDATE", "SUPERSEDE"):
        raise StoreError("invalid_decision")
    scope = request.get("scope")
    title, body, sources = request.get("title"), request.get("body"), request.get("sources")
    validate_content(title, body, sources)
    directory = note_dir(root, scope, key)
    with locked(root):
        target = None
        if decision != "ADD":
            target = read_note(root, scope, key, request.get("target_id"))
            if target["sha256"] != request.get("expected_sha256"):
                raise StoreError("conflict")
            if target["status"] != "active" or target["id"] not in {note["id"] for note, _ in active_notes(root)}:
                raise StoreError("inactive_target")
            if decision == "SUPERSEDE":
                finalize_superseded_parents(root, target)
        timestamp = now()
        if decision == "UPDATE":
            meta = {k: v for k, v in target.items() if k not in ("body", "sha256")}
            meta.update(title=title, verified_at=timestamp,
                        sources=list(dict.fromkeys(target["sources"] + sources)))
            path = note_path(root, scope, key, target["id"])
        else:
            note_id = uuid.uuid4().hex
            meta = {"id": note_id, "scope": scope, "project": key if scope == "project" else "",
                    "status": "active", "title": title, "created_at": timestamp,
                    "verified_at": timestamp, "sources": list(dict.fromkeys(sources)),
                    "supersedes": [target["id"]] if target else []}
            path = note_path(root, scope, key, note_id)
        if decision == "ADD" and path.exists():
            raise StoreError("conflict")
        data = encode_note(meta, body)
        atomic_write(root, path, data)
        if target and decision == "SUPERSEDE":
            old_meta = {k: v for k, v in target.items() if k not in ("body", "sha256")}
            old_meta["status"] = "superseded"
            try:
                atomic_write(root, note_path(root, scope, key, target["id"]), encode_note(old_meta, target["body"]))
            except (OSError, StoreError):
                try:
                    current = read_note(root, scope, key, target["id"])
                except (OSError, StoreError):
                    current = None
                if current is not None and current["status"] == "active":
                    checked_path(root, path)
                    path.unlink()
                raise
        indexed = refresh_index(root)
        saved = read_note(root, scope, key, meta["id"])
        return {"decision": decision, "id": saved["id"], "sha256": saved["sha256"], "path": str(path),
                "index_degraded": not indexed}


def change_status(root, key, scope, note_id, expected, action):
    with locked(root):
        note = read_note(root, scope, key, note_id)
        if note["sha256"] != expected:
            raise StoreError("conflict")
        finalize_superseded_parents(root, note)
        path = note_path(root, scope, key, note_id)
        if action == "forget":
            checked_path(root, path)
            path.unlink()
        else:
            meta = {k: v for k, v in note.items() if k not in ("body", "sha256")}
            meta["status"] = "archived"
            atomic_write(root, path, encode_note(meta, note["body"]))
        indexed = refresh_index(root)
    return {"status": "forgotten" if action == "forget" else "archived", "id": note_id,
            "index_degraded": not indexed}


def search(root, key, scope, query):
    tokens = re.findall(r"\w+", query, re.UNICODE)[:12]
    if not tokens or not root.exists():
        return {"results": []}
    patterns = [re.compile(r"(?<![a-z0-9])" + re.escape(token.casefold()) + r"(?![a-z0-9])")
                for token in tokens]
    degraded = False
    try:
        checked_path(root, root / "index.sqlite3")
        if index_is_stale(root):
            with locked(root):
                degraded = not refresh_index(root)
    except StoreError:
        degraded = True
    expression = " OR ".join('"' + item.replace('"', '') + '"' for item in tokens)
    for attempt in range(0 if degraded else 2):
        try:
            connection = sqlite3.connect("file:" + str(root / "index.sqlite3") + "?mode=ro", uri=True)
            try:
                rows = connection.execute(
                    "SELECT id, title FROM memories WHERE memories MATCH ? AND scope = ? AND project = ? ORDER BY bm25(memories) LIMIT 5",
                    (expression, scope, key if scope == "project" else ""),
                ).fetchall()
            finally:
                connection.close()
            results = []
            stale_row = False
            for note_id, _ in rows:
                try:
                    note = read_note(root, scope, key, note_id)
                    haystack = (note["title"] + " " + note["body"]).casefold()
                    if note["status"] == "active" and any(pattern.search(haystack) for pattern in patterns):
                        results.append({"id": note_id, "title": note["title"], "sources": note["sources"]})
                    else:
                        stale_row = True
                except StoreError:
                    stale_row = True
            if results and not stale_row:
                return {"results": results}
            break
        except sqlite3.DatabaseError:
            if attempt:
                break
            with locked(root):
                if not refresh_index(root):
                    break
    ranked = []
    for note, _ in active_notes(root):
        if note["scope"] == scope and note.get("project", "") == (key if scope == "project" else ""):
            haystack = (note["title"] + " " + note["body"]).casefold()
            score = sum(len(pattern.findall(haystack)) for pattern in patterns)
            if score:
                ranked.append((score, note))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    return {"results": [{"id": note["id"], "title": note["title"], "sources": note["sources"]} for _, note in ranked[:5]],
            "degraded": True}


def capture_config(root, key, setting=None):
    path = root / "settings" / (key + ".json")
    if setting is None:
        if not path.exists():
            return {"enabled": False}
        config = json.loads(safe_read(root, path))
        if not isinstance(config, dict) or type(config.get("enabled")) is not bool:
            raise StoreError("invalid_config")
        return {"enabled": config["enabled"]}
    with locked(root):
        atomic_write(root, path, json.dumps({"enabled": setting}).encode("utf-8"))
    return {"enabled": setting}


def stage_hook(root, key, event):
    if not isinstance(event, dict):
        raise StoreError("invalid_event")
    if event.get("permission_mode") == "plan":
        return {"status": "disabled"}
    if capture_config(root, key)["enabled"] is not True:
        return {"status": "disabled"}
    kind = event.get("hook_event_name")
    if kind not in ("UserPromptSubmit", "Stop"):
        return {"status": "ignored"}
    excerpt = event.get("prompt") if kind == "UserPromptSubmit" else event.get("last_assistant_message")
    match = SIGNAL_RE.search(excerpt) if isinstance(excerpt, str) else None
    if match is None or SKIP_RE.search(excerpt):
        return {"status": "ignored"}
    if SECRET_RE.search(excerpt):
        return {"status": "sensitive_content"}
    excerpt = excerpt[max(0, match.start() - 120):match.end() + 600]
    session = event.get("session_id", "unknown")
    if not isinstance(session, str):
        session = "unknown"
    candidate_id = digest((session + "\0" + kind + "\0" + excerpt).encode("utf-8"))[:32]
    path = root / "inbox" / key / (candidate_id + ".json")
    candidate = {"id": candidate_id, "event": kind, "excerpt": excerpt,
                 "session_id": session, "created_at": now(), "project": key}
    with locked(root):
        if capture_config(root, key)["enabled"] is not True:
            return {"status": "disabled"}
        if path.exists():
            return {"status": "duplicate", "id": candidate_id}
        atomic_write(root, path, json.dumps(candidate, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"status": "staged", "id": candidate_id}


def pending(root, key):
    directory = root / "inbox" / key
    if not directory.exists():
        return {"results": []}
    checked_path(root, directory)
    results = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = safe_read(root, path)
            candidate = json.loads(data)
            if not isinstance(candidate, dict) or candidate.get("id") != path.stem or candidate.get("project") != key:
                continue
            candidate["sha256"] = digest(data)
            results.append(candidate)
        except (StoreError, OSError, ValueError):
            continue
    return {"results": results}


def dismiss(root, key, candidate_id, expected):
    if not isinstance(candidate_id, str) or not ID_RE.fullmatch(candidate_id):
        raise StoreError("invalid_id")
    path = root / "inbox" / key / (candidate_id + ".json")
    with locked(root):
        if digest(safe_read(root, path)) != expected:
            raise StoreError("conflict")
        path.unlink()
    return {"status": "dismissed", "id": candidate_id}


def project_root(cwd):
    location = Path(cwd).expanduser().resolve(strict=True)
    result = subprocess.run(["git", "-C", str(location), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True, check=False)
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else location


def audit(root, key, scope, cwd):
    chosen = [(note, path) for note, path in iter_notes(root) if note.get("scope") == scope and note.get("project", "") == (key if scope == "project" else "")]
    active_ids = {note["id"] for note, _ in active_notes(root)}
    groups = {}
    broken = []
    repo_root = project_root(cwd)
    for note, _ in chosen:
        if note["id"] in active_ids:
            groups.setdefault(note["body"].strip().casefold(), []).append(note["id"])
        else:
            continue
        for source in note.get("sources", []):
            if source.startswith("file:") and not Path(source[5:]).exists():
                broken.append({"id": note["id"], "source": source})
            if source.startswith("repo:"):
                try:
                    relative = Path(source[5:])
                    resolved = (repo_root / relative).resolve()
                    broken_source = relative.is_absolute() or not resolved.is_relative_to(repo_root) or not resolved.exists()
                except (OSError, RuntimeError):
                    broken_source = True
                if broken_source:
                    broken.append({"id": note["id"], "source": source})
    directory = note_dir(root, scope, key)
    invalid = []
    if directory.exists():
        for path in sorted(directory.glob("*.md")):
            try:
                if path.is_symlink():
                    raise StoreError("unsafe_path")
                read_note(root, scope, key, path.stem)
            except (StoreError, OSError):
                invalid.append(path.name)
    return {"notes": len(chosen), "duplicates": [ids for ids in groups.values() if len(ids) > 1],
            "broken_sources": broken, "invalid_files": invalid,
            "items": [{"id": note["id"], "title": note["title"], "status": note["status"],
                       "verified_at": note["verified_at"]} for note, _ in chosen]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("put", "get", "search", "archive", "forget", "capture", "hook", "pending", "dismiss", "audit", "rebuild"):
        sub = actions.add_parser(name)
        sub.add_argument("--cwd", default=os.getcwd())
        if name in ("get", "archive", "forget"):
            sub.add_argument("id")
        if name == "dismiss":
            sub.add_argument("id")
            sub.add_argument("expected_sha256")
        if name in ("archive", "forget"):
            sub.add_argument("expected_sha256")
        if name == "search":
            sub.add_argument("query")
        if name == "capture":
            sub.add_argument("setting", choices=("on", "off", "show"))
        if name in ("get", "search", "archive", "forget", "audit"):
            sub.add_argument("--scope", choices=("project", "user"), default="project")
    args = parser.parse_args()
    try:
        root = root_path()
        event = json.load(sys.stdin) if args.action == "hook" else None
        cwd = event.get("cwd", args.cwd) if isinstance(event, dict) else args.cwd
        key = project_key(cwd)
        if args.action == "put":
            result = put(root, key, json.load(sys.stdin))
        elif args.action == "get":
            result = read_note(root, args.scope, key, args.id)
        elif args.action == "search":
            result = search(root, key, args.scope, args.query)
        elif args.action in ("archive", "forget"):
            result = change_status(root, key, args.scope, args.id, args.expected_sha256, args.action)
        elif args.action == "capture":
            result = capture_config(root, key, None if args.setting == "show" else args.setting == "on")
        elif args.action == "hook":
            result = stage_hook(root, key, event)
        elif args.action == "pending":
            result = pending(root, key)
        elif args.action == "dismiss":
            result = dismiss(root, key, args.id, args.expected_sha256)
        elif args.action == "audit":
            result = audit(root, key, args.scope, cwd)
        else:
            with locked(root):
                rebuild_index(root)
            result = {"status": "rebuilt"}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except StoreError as error:
        print(json.dumps({"error": error.code}))
        return 2
    except (OSError, ValueError, sqlite3.DatabaseError, subprocess.SubprocessError):
        print(json.dumps({"error": "store_unavailable"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
