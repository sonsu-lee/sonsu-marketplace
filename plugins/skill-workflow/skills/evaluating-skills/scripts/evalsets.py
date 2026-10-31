"""Load and check a skill's Agent Skills evaluation files."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from scripts.utils import parse_skill_md

EVAL_KEYS = {"id", "prompt", "expected_output", "files", "assertions"}


class EvalSetError(ValueError):
    """An evaluation file does not follow the format in references/formats.md."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvalSetError(message)


def _strings(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value)


def load_evals(skill_dir: Path) -> dict:
    """Return evals/evals.json after checking it."""
    skill_dir = Path(skill_dir)
    path = skill_dir / "evals" / "evals.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(data, dict) and set(data) == {"skill_name", "evals"},
             f"{path}: keys must be exactly skill_name and evals")
    _require(data["skill_name"] == parse_skill_md(skill_dir)[0],
             f"{path}: skill_name must equal the name in SKILL.md")
    _require(isinstance(data["evals"], list) and data["evals"], f"{path}: evals must not be empty")
    ids = [case.get("id") for case in data["evals"]]
    _require(len(set(ids)) == len(ids), f"{path}: ids must be unique")
    files_root = (skill_dir / "evals" / "files").resolve()
    for case in data["evals"]:
        where = f"{path}: eval {case.get('id')}"
        _require("expectations" not in case, f"{where}: use `assertions`, not `expectations`")
        _require(set(case) <= EVAL_KEYS and {"id", "prompt", "expected_output"} <= set(case),
                 f"{where}: keys must be id, prompt, expected_output, and optionally files "
                 "and assertions")
        _require(isinstance(case["id"], int) and isinstance(case["prompt"], str)
                 and case["prompt"].strip() and isinstance(case["expected_output"], str),
                 f"{where}: id must be an integer, prompt and expected_output strings")
        _require(_strings(case.get("assertions", [])), f"{where}: assertions must be strings")
        _require(_strings(case.get("files", [])), f"{where}: files must be strings")
        for entry in case.get("files", []):
            target = (skill_dir / entry).resolve()
            exists = target.is_dir() if entry.endswith("/") else target.is_file()
            _require(files_root in target.parents and exists,
                     f"{where}: {entry} must exist under evals/files/ "
                     "(end directories with /)")
    # Codex registers every SKILL.md it finds under a skill directory.
    nested = list((skill_dir / "evals").rglob("SKILL.md"))
    _require(not nested, f"{skill_dir}: rename files named SKILL.md under evals/: {nested}")
    return data


def load_queries(path: Path) -> list:
    """Return a trigger query set after checking it."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(isinstance(data, list) and data, f"{path}: must be a non-empty array")
    for item in data:
        _require(isinstance(item, dict) and set(item) == {"query", "should_trigger"}
                 and isinstance(item["query"], str) and item["query"].strip()
                 and isinstance(item["should_trigger"], bool),
                 f"{path}: each item is {{query: string, should_trigger: boolean}}")
    queries = [item["query"] for item in data]
    # run_loop matches train and test results by query text.
    _require(len(set(queries)) == len(queries), f"{path}: queries must be unique")
    return data


def copy_inputs(skill_dir: Path, files: list, workdir: Path) -> list:
    """Copy input files into workdir and return their paths relative to it.

    A file keeps its base name; a directory entry ending in / copies its
    contents to the top of workdir.
    """
    for entry in files:
        source = Path(skill_dir) / entry
        if entry.endswith("/"):
            shutil.copytree(source, workdir, dirs_exist_ok=True)
        else:
            shutil.copy2(source, Path(workdir) / source.name)
    return sorted(p.relative_to(workdir).as_posix() for p in Path(workdir).rglob("*")
                  if p.is_file() and ".git" not in p.relative_to(workdir).parts)


def default_workspace(name: str) -> Path:
    """Per-user workspace outside any installed package."""
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "skill-evals" / f"{name}-workspace"
