"""Load and validate a skill's Agent Skills evaluation files."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from scripts.utils import parse_skill_md

EVAL_KEYS = {"id", "prompt", "expected_output", "files", "assertions"}
REQUIRED_EVAL_KEYS = {"id", "prompt", "expected_output"}


class EvalSetError(ValueError):
    """An evaluation file does not follow the Agent Skills format."""


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise EvalSetError(f"{path} does not exist") from None
    except json.JSONDecodeError as error:
        raise EvalSetError(f"{path} is not valid JSON: {error}") from None


def _check_files(skill_dir: Path, where: str, files) -> None:
    if not isinstance(files, list) or not all(isinstance(f, str) and f for f in files):
        raise EvalSetError(f"{where}: files must be a list of non-empty strings")
    root = (skill_dir / "evals" / "files").resolve()
    for entry in files:
        parts = Path(entry).parts
        if Path(entry).is_absolute() or ".." in parts:
            raise EvalSetError(f"{where}: {entry!r} must be a relative path without '..'")
        target = (skill_dir / entry).resolve()
        if root not in target.parents:
            raise EvalSetError(f"{where}: {entry!r} must be under evals/files/")
        if entry.endswith("/"):
            if not target.is_dir():
                raise EvalSetError(f"{where}: directory {entry!r} does not exist")
        elif not target.is_file():
            raise EvalSetError(f"{where}: file {entry!r} does not exist (end directories with '/')")


def load_evals(skill_dir: Path) -> dict:
    """Return evals/evals.json after checking it against the format rules."""
    skill_dir = Path(skill_dir)
    path = skill_dir / "evals" / "evals.json"
    data = _read_json(path)
    if not isinstance(data, dict) or set(data) != {"skill_name", "evals"}:
        raise EvalSetError(f"{path}: top-level keys must be exactly skill_name and evals")
    name, _, _ = parse_skill_md(skill_dir)
    if data["skill_name"] != name:
        raise EvalSetError(f"{path}: skill_name {data['skill_name']!r} does not match SKILL.md name {name!r}")
    evals = data["evals"]
    if not isinstance(evals, list) or not evals:
        raise EvalSetError(f"{path}: evals must be a non-empty list")
    seen: set[int] = set()
    for index, case in enumerate(evals):
        where = f"{path}: evals[{index}]"
        if not isinstance(case, dict):
            raise EvalSetError(f"{where} must be an object")
        if "expectations" in case:
            raise EvalSetError(f"{where}: use `assertions` (Agent Skills format), not `expectations`")
        unknown = set(case) - EVAL_KEYS
        if unknown:
            raise EvalSetError(f"{where}: unknown keys {sorted(unknown)}")
        missing = REQUIRED_EVAL_KEYS - set(case)
        if missing:
            raise EvalSetError(f"{where}: missing keys {sorted(missing)}")
        case_id = case["id"]
        if not isinstance(case_id, int) or isinstance(case_id, bool):
            raise EvalSetError(f"{where}: id must be an integer")
        if case_id in seen:
            raise EvalSetError(f"{where}: duplicate id {case_id}")
        seen.add(case_id)
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise EvalSetError(f"{where}: prompt must be a non-empty string")
        if not isinstance(case["expected_output"], str):
            raise EvalSetError(f"{where}: expected_output must be a string")
        if "assertions" in case:
            assertions = case["assertions"]
            if not isinstance(assertions, list) or not all(
                isinstance(a, str) and a.strip() for a in assertions
            ):
                raise EvalSetError(f"{where}: assertions must be a list of non-empty strings")
        if "files" in case:
            _check_files(skill_dir, where, case["files"])
    nested = sorted(str(p.relative_to(skill_dir)) for p in (skill_dir / "evals").rglob("SKILL.md"))
    if nested:
        raise EvalSetError(
            f"{skill_dir}: files named SKILL.md under evals/ may be registered as skills: {nested}"
        )
    return data


def load_queries(path: Path) -> list[dict]:
    """Return a trigger query set after checking its format."""
    path = Path(path)
    data = _read_json(path)
    if not isinstance(data, list) or not data:
        raise EvalSetError(f"{path}: must be a non-empty array")
    seen: set[str] = set()
    for index, item in enumerate(data):
        where = f"{path}: [{index}]"
        if not isinstance(item, dict) or set(item) != {"query", "should_trigger"}:
            raise EvalSetError(f"{where}: keys must be exactly query and should_trigger")
        if not isinstance(item["query"], str) or not item["query"].strip():
            raise EvalSetError(f"{where}: query must be a non-empty string")
        if not isinstance(item["should_trigger"], bool):
            raise EvalSetError(f"{where}: should_trigger must be true or false")
        # run_loop matches train and test results by query text.
        if item["query"] in seen:
            raise EvalSetError(f"{where}: duplicate query")
        seen.add(item["query"])
    return data


def copy_inputs(skill_dir: Path, files: list[str], workdir: Path) -> list[str]:
    """Copy an eval's input files into workdir and return their relative paths."""
    skill_dir, workdir = Path(skill_dir), Path(workdir)
    sources: dict[Path, Path] = {}

    def add(key: Path, item: Path) -> None:
        if sources.setdefault(key, item) != item:
            raise EvalSetError(f"input files collide at {key}")

    for entry in files:
        source = skill_dir / entry
        if entry.endswith("/"):
            for item in sorted(source.rglob("*")):
                if item.is_file():
                    add(item.relative_to(source), item)
        else:
            add(Path(source.name), source)
    for relative, source in sources.items():
        target = workdir / relative
        if target.exists():
            raise EvalSetError(f"input file {relative} collides with an existing path")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return sorted(str(relative) for relative in sources)


def default_workspace(name: str) -> Path:
    """Return the per-user workspace for a skill, outside any installed package."""
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "skill-evals" / f"{name}-workspace"
