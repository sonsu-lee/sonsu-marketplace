#!/usr/bin/env python3
"""Run declared checks and bind successful results to Git trees."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DECLARATION = ".workflow-checks.json"
CHECK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def git(root: Path, *args: str, env: dict | None = None) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, env=env, stderr=subprocess.PIPE).strip()


def repository(cwd: str) -> Path:
    return Path(git(Path(cwd), "rev-parse", "--show-toplevel")).resolve()


def parse_declaration(raw: bytes) -> tuple[list[dict], str]:
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("checks"), list):
        raise ValueError("declaration must contain a checks array")
    checks = data["checks"]
    seen = set()
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("each check must be an object")
        name, argv, actions = check.get("id"), check.get("argv"), check.get("actions")
        if not isinstance(name, str) or not CHECK_ID.fullmatch(name) or name in seen:
            raise ValueError("check ids must be unique lowercase letters, digits, and hyphens")
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x for x in argv):
            raise ValueError(f"{name}: argv must be a nonempty string array")
        if not isinstance(actions, list) or not actions or any(not isinstance(x, str) or x not in {"commit", "push", "publish"} for x in actions):
            raise ValueError(f"{name}: actions must contain commit, push, or publish")
        seen.add(name)
    return checks, hashlib.sha256(raw).hexdigest()


def declaration(root: Path) -> tuple[list[dict], str] | None:
    path = root / DECLARATION
    return parse_declaration(path.read_bytes()) if path.exists() else None


def snapshot(root: Path) -> str:
    index_path = Path(git(root, "rev-parse", "--git-path", "index"))
    if not index_path.is_absolute():
        index_path = root / index_path
    with tempfile.TemporaryDirectory(prefix="development-index-") as tmp:
        index = Path(tmp) / "index"
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        if index_path.exists():
            shutil.copyfile(index_path, index)
        else:
            git(root, "read-tree", "--empty", env=env)
        git(root, "add", "-A", "--sparse", "--", ".", env=env)
        # stat キャッシュと skip-worktree の設定で変更を見逃さない。
        git(root, "add", "--renormalize", "-u", "--sparse", "--", ".", env=env)
        return git(root, "write-tree", env=env)


def store(root: Path) -> Path:
    path = Path(git(root, "rev-parse", "--git-path", "development-evidence"))
    return path if path.is_absolute() else root / path


def run_check(cwd: str, name: str) -> int:
    root = repository(cwd)
    declared = declaration(root)
    if declared is None:
        raise ValueError(f"no {DECLARATION} exists in {root}")
    checks, declaration_hash = declared
    check = next((item for item in checks if item["id"] == name), None)
    if check is None:
        raise ValueError(f"check {name!r} is not declared")
    directory = store(root)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = directory / f"{name}.lock"
    lock.mkdir(mode=0o700)
    receipt = directory / f"{name}.json"
    try:
        # 1. 古い結果を先に無効化し、失敗した再実行を成功として扱わない。
        receipt.unlink(missing_ok=True)
        before = snapshot(root)
        # 2. シェルを使わず承認済み argv を実行し、前後のツリーを比較する。
        result = subprocess.run(check["argv"], cwd=root, check=False)
        after = snapshot(root)
        if result.returncode != 0:
            print(f"check {name} failed with exit {result.returncode}; no receipt", file=sys.stderr)
            return result.returncode if result.returncode > 0 else 1
        if before != after:
            print(f"check {name} changed the worktree; no receipt", file=sys.stderr)
            return 1
        # 3. 成功かつ対象が不変の場合だけ結果を原子的に記録する。
        payload = {"id": name, "argv": check["argv"], "declaration": declaration_hash, "tree": before}
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as temp:
            json.dump(payload, temp)
            temp_path = Path(temp.name)
        try:
            os.replace(temp_path, receipt)
        finally:
            temp_path.unlink(missing_ok=True)
        print(f"Recorded {name} on tree {before}")
        return 0
    finally:
        lock.rmdir()


def strip_shell_comments(command: str) -> str:
    # 単語内の # を残し、明らかな単語境界のコメントを除く。
    if any(marker in command for marker in ("$(", "${", "$'", "`")):
        return command
    result = []
    quote = None
    escaped = False
    boundary = True
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            result.append(char)
            escaped = False
        elif char == "\\" and quote != "'":
            result.append(char)
            escaped = True
            boundary = False
        elif quote:
            result.append(char)
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            result.append(char)
            quote = char
            boundary = False
        elif char == "#" and boundary:
            end = command.find("\n", index)
            if end < 0:
                break
            index = end - 1
        else:
            result.append(char)
            boundary = char in " \t\n;&|<("
        index += 1
    return "".join(result)


def command_repository(cwd: str, command: str) -> Path:
    words = shlex.split(strip_shell_comments(command))
    if not words or Path(words[0]).name != "git":
        return repository(cwd)
    index = 1
    while index < len(words):
        if words[index] in {"-C", "-c", "--git-dir", "--work-tree"}:
            if index + 1 >= len(words):
                raise ValueError("incomplete Git option")
            index += 2
        elif words[index] == "--no-pager" or words[index].startswith(("--git-dir=", "--work-tree=")):
            index += 1
        else:
            break
    return Path(git(Path(cwd), *words[1:index], "rev-parse", "--show-toplevel")).resolve()


def command_target(cwd: str, command: str, action: str) -> tuple[Path, str]:
    if any(marker in command for marker in ("$", "`", "*", "?", "[", "{", "~")):
        raise ValueError("shell expansion is not bindable to a Git tree")
    lexer = shlex.shlex(strip_shell_comments(command), posix=True, punctuation_chars=";&|<>()")
    lexer.commenters = ""
    lexer.whitespace_split = True
    words = list(lexer)
    if not words or Path(words[0]).name != "git" or any(w and set(w) <= set(";&|<>()") for w in words):
        raise ValueError("use one direct Git command; chained or indirect actions are not bindable")
    index = 1
    root = Path(cwd)
    while index < len(words) and words[index] in {"-C", "-c", "--git-dir", "--work-tree", "--no-pager"}:
        option = words[index]
        if option == "--no-pager":
            index += 1
            continue
        if index + 1 >= len(words):
            raise ValueError("incomplete Git option")
        if option == "-C":
            root = (root / words[index + 1]).resolve()
        else:
            raise ValueError("per-command Git configuration or explicit Git directories are not bindable")
        index += 2
    if index >= len(words) or words[index] != action:
        raise ValueError("action cannot be bound to a Git target")
    args = words[index + 1:]
    root = repository(str(root))
    if action == "push":
        if args:
            raise ValueError("push with arguments or refspec is not bindable")
        mode = subprocess.run(["git", "-C", str(root), "config", "--get", "push.default"], text=True, capture_output=True)
        if mode.returncode not in {0, 1} or (mode.stdout.strip() or "simple") not in {"simple", "current"}:
            raise ValueError("configured push.default is not bindable to HEAD")
        refs = subprocess.run(["git", "-C", str(root), "config", "--get-regexp", r"^remote\..*\.(push|mirror)$"], text=True, capture_output=True)
        if refs.returncode not in {0, 1} or refs.stdout.strip():
            raise ValueError("configured remote push refspecs or mirrors are not bindable")
        tags = subprocess.run(["git", "-C", str(root), "config", "--bool", "--get", "push.followTags"], text=True, capture_output=True)
        if tags.returncode not in {0, 1} or tags.stdout.strip() == "true":
            raise ValueError("configured tag following is not bindable")
        return root, git(root, "rev-parse", "HEAD^{tree}")
    if action != "commit":
        raise ValueError("remote publication target is not bindable")
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in {"-m", "--message", "-F", "--file"}:
            i += 2
            if i > len(args):
                raise ValueError("missing commit option value")
        elif arg in {"--allow-empty", "--allow-empty-message", "--no-edit", "--amend", "-q", "--quiet"} or arg.startswith("--message="):
            i += 1
        else:
            raise ValueError("partial, staged-during-command, or unsupported commit form is not bindable")
    return root, git(root, "write-tree")


def gate(cwd: str, command: str, action: str, fallback_root: Path | None = None) -> dict:
    target_error = None
    target_root = None
    target_tree = None
    if action in {"commit", "push"}:
        try:
            target_root, target_tree = command_target(cwd, command, action)
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            target_error = error
    try:
        root = repository(cwd) if action == "publish" else target_root or fallback_root or command_repository(cwd, command)
    except ValueError as error:
        return {"state": "blocked", "reason": f"Evidence gate cannot determine the Git target: {error}"}
    except (OSError, subprocess.CalledProcessError):
        return {"state": "unverified", "reason": "Git target could not be determined; evidence gate is not enforced."}
    try:
        declared = declaration(root)
        prior = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{DECLARATION}"], capture_output=True)
        if prior.returncode == 0:
            previous, _ = parse_declaration(prior.stdout)
            versions = [{check["id"]: check for check in declared[0]} if declared else {}]
            if action == "commit":
                staged = subprocess.run(["git", "-C", str(root), "show", f":{DECLARATION}"], capture_output=True)
                staged_checks = parse_declaration(staged.stdout)[0] if staged.returncode == 0 else []
                versions.append({check["id"]: check for check in staged_checks})
            for check in previous:
                protected = set(check["actions"]) if action == "commit" else {action} & set(check["actions"])
                for current in versions:
                    replacement = current.get(check["id"])
                    if protected and (not replacement or replacement["argv"] != check["argv"] or not protected.issubset(replacement["actions"])):
                        raise ValueError(f"declared check {check['id']} was removed or changed")
        if declared is None:
            return {"state": "unverified", "reason": f"No {DECLARATION}; evidence gate is not enforced."}
        checks, declaration_hash = declared
        required = [check for check in checks if action in check["actions"]]
        if not required:
            return {"state": "unverified", "reason": f"No checks declared for {action}; evidence gate is not enforced."}
        if action == "publish":
            raise ValueError("remote publication target is not bindable")
        if target_error or target_root is None or target_tree is None:
            raise ValueError(f"Git target is not bindable: {target_error}")
        for check in required:
            path = store(root) / f"{check['id']}.json"
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                receipt = {}
            if not isinstance(receipt, dict) or receipt.get("tree") != target_tree or receipt.get("declaration") != declaration_hash or receipt.get("argv") != check["argv"]:
                runner = Path(__file__).resolve()
                return {"state": "blocked", "reason": f"Missing or stale evidence for {check['id']}; run: python3 {shlex.quote(str(runner))} run {shlex.quote(check['id'])} --root {shlex.quote(str(root))}"}
        return {"state": "pass", "tree": target_tree, "checks": [{"id": c["id"], "argv": c["argv"]} for c in required]}
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        return {"state": "blocked", "reason": f"Evidence gate cannot verify this action: {error}"}


def remote_publication(data: dict) -> bool:
    paths = [data.get("path")]
    if isinstance(data.get("paths"), list):
        paths.extend(data["paths"])
    if isinstance(data.get("edits"), list):
        paths.extend(edit.get("rename") for edit in data["edits"] if isinstance(edit, dict))
    patch = data.get("input")
    if isinstance(patch, str):
        paths.extend(re.findall(r"^\[(.+)#[0-9A-Fa-f]{4}\][^\S\n]*$", patch, re.MULTILINE))
        if not re.search(r"^\*\*\* (?:Add|Update|Delete|Edit) File: ", patch, re.MULTILINE):
            paths.extend(re.findall(r"^[ \t]*MV[ \t]+(.+?)[ \t]*$", patch, re.MULTILINE))
        paths.extend(re.findall(
            r"^\*\*\* (?:(?:Add|Update|Delete|Edit) File|Move to): (.+?)(?: all)?[ \t]*$",
            patch, re.MULTILINE,
        ))
    for path in paths:
        if not isinstance(path, str):
            continue
        path = path.rstrip()
        if path.startswith("[") and path.endswith("]"):
            path = re.sub(r"#[0-9A-Fa-f]{4}$", "", path[1:-1])
        if path.startswith('"'):
            try:
                decoded = json.loads(path)
                if isinstance(decoded, str):
                    path = decoded
            except json.JSONDecodeError:
                pass
        elif path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
        if path.lower().startswith(("xd://mcp__", "pr://", "issue://")):
            return True
    return False


def gate_event(event: dict) -> dict:
    name = str(event.get("tool_name", ""))
    data = event.get("tool_input")
    data = data if isinstance(data, dict) else {}
    command = data.get("command") if isinstance(data.get("command"), str) else ""
    cwd = str(event.get("cwd") or os.getcwd())
    actions = []
    if name.lower() in {"bash", "shell", "exec_command"}:
        if "$'" in command:
            return {"state": "blocked", "reason": "Evidence gate cannot parse ANSI-C shell quoting."}
        try:
            lexer = shlex.shlex(strip_shell_comments(command), posix=True, punctuation_chars=";&|<>()\n")
            lexer.commenters = ""
            lexer.whitespace = lexer.whitespace.replace("\n", "")
            lexer.whitespace_split = True
            words = list(lexer)
        except ValueError as error:
            return {"state": "blocked", "reason": f"Evidence gate cannot parse command: {error}"}
        start = 0
        while start < len(words) and words[start] and set(words[start]) == {"\n"}:
            start += 1
        if (start + 2 < len(words) and words[start] == "cd"
                and words[start + 2].replace("\n", "") in {"", "&&", ";"}
                and not any(c in words[start + 1] for c in "$`~")):
            try:
                directory = (Path(cwd) / words[start + 1]).resolve()
                if directory.is_dir():
                    cwd = str(directory)
            except (OSError, RuntimeError):
                pass
        segments = [[]]
        for word in words:
            if word and set(word) <= set(";&|<>()\n"):
                segments.append([])
            else:
                segments[-1].append(word)
        for segment in segments:
            for start, word in enumerate(segment):
                executable = Path(word).name
                if executable == "git":
                    index = start + 1
                    while index < len(segment):
                        option = segment[index]
                        if option in {"-C", "-c", "--git-dir", "--work-tree"}:
                            index += 2
                        elif option == "--no-pager" or option.startswith(("-C=", "-c=", "--git-dir=", "--work-tree=")):
                            index += 1
                        else:
                            break
                    if index < len(segment) and segment[index] in {"commit", "push"}:
                        target = None
                        try:
                            target = command_repository(cwd, shlex.join(segment[start:]))
                        except (OSError, ValueError, subprocess.CalledProcessError):
                            pass
                        action = (segment[index], target)
                        if action not in actions:
                            actions.append(action)
                    break
                if executable in {"gh", "curl", "kubectl", "helm", "terraform"}:
                    action = ("publish", None)
                    if action not in actions:
                        actions.append(action)
                    break
    elif name.startswith("mcp__") or remote_publication(data):
        actions.append(("publish", None))
    if not actions:
        return {"state": "not_applicable"}
    results = [gate(cwd, command, action, target) for action, target in actions]
    return next((result for result in results if result["state"] == "blocked"),
                next((result for result in results if result["state"] == "unverified"), results[0]))


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "run":
        return run_check(os.getcwd(), sys.argv[2])
    if len(sys.argv) == 5 and sys.argv[1] == "run" and sys.argv[3] == "--root":
        return run_check(sys.argv[4], sys.argv[2])
    if len(sys.argv) == 2 and sys.argv[1] == "gate":
        event = json.load(sys.stdin)
        print(json.dumps(gate_event(event)))
        return 0
    raise ValueError("usage: evidence.py run <check-id> [--root <path>] | gate")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Evidence error: {error}", file=sys.stderr)
        sys.exit(1)
