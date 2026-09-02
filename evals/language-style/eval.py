#!/usr/bin/env python3
"""Reproducible A/B evaluation runner for Korean language-style prompts.

The runner deliberately uses only the Python 3.9 standard library.  Repository
files contain fixtures and candidate instructions; generated manifests, model
outputs, traces, review bundles, and analysis files always live outside the
repository.
"""

import argparse
import concurrent.futures
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import secrets
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_CANDIDATE_DIR = SCRIPT_DIR / "candidates"
DEFAULT_SCREEN_CASES = SCRIPT_DIR / "cases-screen.json"
DEFAULT_CONFIRM_CASES = SCRIPT_DIR / "cases-confirm.json"
DEFAULT_ARTIFACT_ROOT = (
    Path.home() / ".codex" / "evals" / "sonsu-marketplace" / "language-style"
)

SCHEMA_VERSION = "language-style-cases-v1"
MANIFEST_VERSION = "language-style-manifest-v1"
RUN_RESULT_VERSION = "language-style-run-result-v1"
CHECK_VERSION = "language-style-check-v1"
REVIEW_VERSION = "language-style-review-v1"
REVIEW_KEY_VERSION = "language-style-review-key-v1"
ANALYSIS_VERSION = "language-style-analysis-v1"

MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "xhigh"
SERVICE_TIER = "priority"
REPETITIONS = 2

CANDIDATE_FILES = {
    "C": ("baseline", "c-baseline.md"),
    "A": ("im-only", "a-im-only.md"),
    "B": ("hybrid", "b-hybrid.md"),
}
STAGE_CANDIDATES = {"screen": ("C", "A", "B"), "confirm": ("A", "B")}
STAGE_CASE_COUNTS = {"screen": 12, "confirm": 18}
STAGE_CATEGORY_COUNTS = {"screen": 2, "confirm": 3}

CASE_FIELDS = {
    "id",
    "category",
    "prompt",
    "evidence",
    "required_substrings",
    "protected_literals",
    "forbidden_substrings",
    "allowed_numbers",
    "required_headings",
    "ordered_markers",
    "exact_code_blocks",
    "min_chars",
    "max_chars",
}
LIST_FIELDS = {
    "required_substrings",
    "protected_literals",
    "forbidden_substrings",
    "allowed_numbers",
    "required_headings",
    "ordered_markers",
    "exact_code_blocks",
}

ISOLATION_OVERRIDE = """## 평가 격리 규칙

이 실행에서는 위의 공통 보존 계약과 이 후보 지침만 사용합니다. 설치된 Fluent Languages,
fluent-korean, humanize, humanizer, im-not-ai 또는 다른 언어·문체 스킬을 읽거나 호출하거나
그 지침을 적용하지 마세요. AGENTS.md, 메모리, 플러그인과 외부 문체 설정도 사용하지 마세요.
도구로 스킬 파일이나 문체 지침을 탐색하지 마세요. 제공된 사용자 요청과 evidence packet만
근거로 답하고, 평가 지침이나 후보 이름은 답변에서 언급하지 마세요."""

# These overrides narrow the executable environment as well as documenting it.
# `codex debug prompt-input` still renders task-level skill metadata on some CLI
# builds, so the saved debug prompt is a sentinel check rather than proof of a
# clean room.  Actual command/tool payloads are checked fail-closed below.
ISOLATION_CONFIG = {
    "model_reasoning_effort": REASONING_EFFORT,
    "service_tier": SERVICE_TIER,
    "approval_policy": "never",
    "features.apps": False,
    "features.plugins": False,
    "features.memories": False,
    "features.multi_agent": False,
    "features.hooks": False,
    "features.remote_plugin": False,
    "features.tool_suggest": False,
    "web_search": "disabled",
    "shell_environment_policy.inherit": "none",
    "project_doc_max_bytes": 0,
    "orchestrator.mcp.enabled": False,
    "orchestrator.skills.enabled": False,
}

THRESHOLDS = {
    "preference_min_fraction": 2.0 / 3.0,
    "sign_test_p_max_exclusive": 0.05,
    "clarity_min_delta": 0.25,
    "naturalness_min_delta": 0.25,
    "technical_accuracy_min_delta": -0.20,
    "category_mean_min_delta": -0.30,
    "equivalence_abs_delta": 0.20,
}

RATING_AXES = (
    "technical_accuracy",
    "clarity",
    "naturalness",
    "concision",
    "structure_fit",
)

CRITICAL_GATES = {
    "required_substring",
    "protected_literal",
    "forbidden_substring",
    "unexpected_number",
    "required_heading",
    "heading_order",
    "ordered_marker",
    "exact_code_block",
    "fenced_code_block_count",
}

CONTAMINATION_RE = re.compile(
    r"(?i)(?:fluent[-_/\\ ]?(?:languages?|korean)|"
    r"humaniz(?:e|er)|im[-_ ]?not[-_ ]?ai).{0,180}SKILL\.md|"
    r"SKILL\.md.{0,180}(?:fluent[-_/\\ ]?(?:languages?|korean)|"
    r"humaniz(?:e|er)|im[-_ ]?not[-_ ]?ai)|"
    r"(?:/|\\)(?:fluent[^/\\]*|humaniz[^/\\]*|im-not-ai)(?:/|\\)|"
    r"(?:/|\\)SKILL\.md(?:\"|$)|SKILL\.md"
)
PROMPT_CONTAMINATION_RE = re.compile(
    r"(?i)(?:fluent[-_ ]?(?:languages?|korean)|"
    r"humaniz(?:e|er)|im[-_ ]?not[-_ ]?ai)"
)
EXTERNAL_SKILL_PATH_RE = re.compile(
    r"(?i)(?:/|\\)\.agents(?:/|\\)skills(?:/|\\)|"
    r"(?:/|\\)\.codex(?:/|\\)plugins(?:/|\\).{0,240}(?:/|\\)SKILL\.md"
)


class ValidationError(ValueError):
    """Raised when a fixture, candidate, manifest, or rating is invalid."""


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(_canonical_bytes(value))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValidationError("missing file: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValidationError("invalid JSON in %s: %s" % (path, exc)) from exc


def _read_utf8_exact(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def _ensure_private_dir(path: Path) -> None:
    missing = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    for directory in reversed(missing):
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass


def _write_json(path: Path, value: Any) -> None:
    _ensure_private_dir(path.parent)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), delete=False
    ) as handle:
        handle.write(payload)
        temp_name = handle.name
    os.replace(temp_name, str(path))


def _write_text(path: Path, value: str) -> None:
    _ensure_private_dir(path.parent)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), delete=False
    ) as handle:
        handle.write(value)
        temp_name = handle.name
    os.replace(temp_name, str(path))


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _require_external(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if _is_within(resolved, REPO_ROOT):
        raise ValidationError("%s must be outside the repository: %s" % (label, resolved))
    return resolved


def _source_name(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        # JSON basic strings are valid TOML basic strings for these values.
        return json.dumps(value, ensure_ascii=False)
    raise TypeError("unsupported TOML config value: %r" % (value,))


def _config_args(config: Mapping[str, Any]) -> List[str]:
    args: List[str] = []
    for key in sorted(config):
        args.extend(["-c", "%s=%s" % (key, _toml_value(config[key]))])
    return args


def _isolated_codex_environment(root: Path) -> Tuple[Dict[str, str], Path]:
    codex_home = root / "codex-home"
    user_home = root / "home"
    codex_home.mkdir(parents=True, exist_ok=True)
    user_home.mkdir(parents=True, exist_ok=True)
    configured_home = os.environ.get("CODEX_HOME")
    source_home = Path(configured_home).expanduser() if configured_home else Path.home() / ".codex"
    auth_source = source_home / "auth.json"
    auth_link = codex_home / "auth.json"
    if auth_source.is_file() and not auth_link.exists():
        auth_link.symlink_to(auth_source.resolve())
    env = dict(os.environ)
    env["HOME"] = str(user_home)
    env["CODEX_HOME"] = str(codex_home)
    env["XDG_CONFIG_HOME"] = str(user_home / ".config")
    return env, codex_home


def load_candidates(candidate_dir: Path = DEFAULT_CANDIDATE_DIR) -> Dict[str, Any]:
    candidate_dir = Path(candidate_dir)
    common_path = candidate_dir / "common.md"
    errors: List[str] = []
    try:
        common = common_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        common = ""
        errors.append("missing candidate file: %s" % common_path)
    if not common.strip():
        errors.append("common.md must not be empty")
    if "\x00" in common:
        errors.append("common.md contains a NUL byte")

    candidates: Dict[str, Any] = {}
    source_hashes: Dict[str, str] = {}
    if common_path.is_file():
        source_hashes[_source_name(common_path)] = _sha256_file(common_path)

    for candidate_id, (name, filename) in CANDIDATE_FILES.items():
        path = candidate_dir / filename
        try:
            body = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            body = ""
            errors.append("missing candidate file: %s" % path)
        if not body.strip():
            errors.append("%s must not be empty" % filename)
        if "\x00" in body:
            errors.append("%s contains a NUL byte" % filename)
        if path.is_file():
            source_hashes[_source_name(path)] = _sha256_file(path)
        developer = "\n\n".join(
            (common.strip(), body.strip(), ISOLATION_OVERRIDE.strip())
        )
        candidates[candidate_id] = {
            "id": candidate_id,
            "name": name,
            "source": _source_name(path),
            "source_sha256": _sha256_file(path) if path.is_file() else None,
            "developer_instructions": developer,
            "developer_sha256": _sha256_bytes(developer.encode("utf-8")),
        }

    a_path = candidate_dir / CANDIDATE_FILES["A"][1]
    b_path = candidate_dir / CANDIDATE_FILES["B"][1]
    if a_path.is_file() and b_path.is_file() and not b_path.read_bytes().startswith(
        a_path.read_bytes()
    ):
        errors.append("b-hybrid.md must contain a-im-only.md as a byte-for-byte prefix")

    if errors:
        raise ValidationError("\n".join(errors))
    candidate_fingerprint = {
        key: {
            "source_sha256": value["source_sha256"],
            "developer_sha256": value["developer_sha256"],
        }
        for key, value in sorted(candidates.items())
    }
    return {
        "common": {
            "source": _source_name(common_path),
            "source_sha256": _sha256_file(common_path),
        },
        "sources": source_hashes,
        "candidates": candidates,
        "candidate_set_sha256": _sha256_json(candidate_fingerprint),
    }


def _validate_case(case: Any, source: str, index: int) -> Dict[str, Any]:
    where = "%s cases[%d]" % (source, index)
    if not isinstance(case, dict):
        raise ValidationError("%s must be an object" % where)
    keys = set(case)
    if keys != CASE_FIELDS:
        missing = sorted(CASE_FIELDS - keys)
        extra = sorted(keys - CASE_FIELDS)
        raise ValidationError(
            "%s has wrong fields (missing=%s, extra=%s)" % (where, missing, extra)
        )
    for field in ("id", "category", "prompt", "evidence"):
        if not isinstance(case[field], str) or not case[field].strip():
            raise ValidationError("%s.%s must be a non-empty string" % (where, field))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}", case["id"]):
        raise ValidationError("%s.id must be a 3-80 character lowercase slug" % where)
    if len(case["category"]) > 80:
        raise ValidationError("%s.category is too long" % where)

    for field in sorted(LIST_FIELDS):
        values = case[field]
        if not isinstance(values, list):
            raise ValidationError("%s.%s must be an array" % (where, field))
        if any(not isinstance(value, str) or not value for value in values):
            raise ValidationError(
                "%s.%s must contain only non-empty strings" % (where, field)
            )
        if len(values) != len(set(values)):
            raise ValidationError("%s.%s contains duplicates" % (where, field))
    for block in case["exact_code_blocks"]:
        parsed = _extract_code_blocks(block)
        if len(parsed) != 1 or parsed[0]["raw"] != block:
            raise ValidationError(
                "%s.exact_code_blocks entries must be full fenced blocks" % where
            )
    if any(not re.fullmatch(r"\d+", value) for value in case["allowed_numbers"]):
        raise ValidationError(
            "%s.allowed_numbers entries must be consecutive ASCII digits" % where
        )
    if any(
        not re.fullmatch(r"#{1,6}\s+\S(?:.*\S)?", value)
        for value in case["required_headings"]
    ):
        raise ValidationError(
            "%s.required_headings entries must be full Markdown ATX headings" % where
        )

    for field in ("min_chars", "max_chars"):
        value = case[field]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("%s.%s must be an integer" % (where, field))
    if not 1 <= case["min_chars"] <= 100000:
        raise ValidationError("%s.min_chars must be in 1..100000" % where)
    if not case["min_chars"] <= case["max_chars"] <= 100000:
        raise ValidationError(
            "%s.max_chars must be in min_chars..100000" % where
        )

    forbidden = set(case["forbidden_substrings"])
    overlap = forbidden.intersection(
        case["required_substrings"] + case["protected_literals"]
    )
    if overlap:
        raise ValidationError(
            "%s requires and forbids the same text: %s" % (where, sorted(overlap))
        )
    return dict(case)


def load_case_file(path: Path, expected_stage: Optional[str] = None) -> Dict[str, Any]:
    path = Path(path)
    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValidationError("%s must contain an object" % path)
    expected_keys = {"schema_version", "stage", "cases"}
    if set(data) != expected_keys:
        raise ValidationError(
            "%s top-level fields must be exactly %s" % (path, sorted(expected_keys))
        )
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValidationError(
            "%s schema_version must be %s" % (path, SCHEMA_VERSION)
        )
    stage = data["stage"]
    if stage not in STAGE_CASE_COUNTS:
        raise ValidationError("%s stage must be screen or confirm" % path)
    if expected_stage is not None and stage != expected_stage:
        raise ValidationError("%s stage must be %s" % (path, expected_stage))
    if not isinstance(data["cases"], list):
        raise ValidationError("%s.cases must be an array" % path)
    cases = [
        _validate_case(case, str(path), index)
        for index, case in enumerate(data["cases"])
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "stage": stage,
        "cases": cases,
        "source": _source_name(path),
        "source_sha256": _sha256_file(path),
    }


def validate_inputs(
    candidate_dir: Path = DEFAULT_CANDIDATE_DIR,
    screen_cases: Path = DEFAULT_SCREEN_CASES,
    confirm_cases: Path = DEFAULT_CONFIRM_CASES,
) -> Dict[str, Any]:
    candidates = load_candidates(Path(candidate_dir))
    screen = load_case_file(Path(screen_cases), "screen")
    confirm = load_case_file(Path(confirm_cases), "confirm")

    for envelope in (screen, confirm):
        expected = STAGE_CASE_COUNTS[envelope["stage"]]
        if len(envelope["cases"]) != expected:
            raise ValidationError(
                "%s must contain %d cases, found %d"
                % (envelope["stage"], expected, len(envelope["cases"]))
            )

    all_cases = screen["cases"] + confirm["cases"]
    ids = [case["id"] for case in all_cases]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValidationError("case IDs must be globally unique: %s" % duplicates)

    screen_counts = Counter(case["category"] for case in screen["cases"])
    confirm_counts = Counter(case["category"] for case in confirm["cases"])
    if set(screen_counts) != set(confirm_counts) or len(screen_counts) != 6:
        raise ValidationError(
            "screen and confirm must use the same six categories"
        )
    for stage, counts in (("screen", screen_counts), ("confirm", confirm_counts)):
        expected = STAGE_CATEGORY_COUNTS[stage]
        wrong = {key: value for key, value in counts.items() if value != expected}
        if wrong:
            raise ValidationError(
                "%s must have %d cases per category: %s" % (stage, expected, wrong)
            )
    total_counts = Counter(case["category"] for case in all_cases)
    if any(value != 5 for value in total_counts.values()):
        raise ValidationError("combined fixtures must have five cases per category")

    return {
        "candidates": candidates,
        "screen": screen,
        "confirm": confirm,
        "summary": {
            "candidate_ids": sorted(candidates["candidates"]),
            "screen_cases": len(screen["cases"]),
            "confirm_cases": len(confirm["cases"]),
            "categories": dict(sorted(total_counts.items())),
        },
    }


def render_user_prompt(case: Mapping[str, Any]) -> str:
    return (
        "%s\n\n"
        "<evidence_packet>\n%s\n</evidence_packet>\n\n"
        "evidence packet의 사실과 불확실성 범위를 유지해서 답하세요. "
        "packet에 없는 사실을 새로 만들지 마세요."
    ) % (case["prompt"].rstrip(), case["evidence"].rstrip())


def _plan_config() -> Dict[str, Any]:
    return {
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "service_tier": SERVICE_TIER,
        "sandbox": "read-only",
        "approval_policy": "never",
        "ephemeral": True,
        "ignore_user_config": True,
        "ignore_rules": True,
        "json_trace": True,
        "repetitions": REPETITIONS,
        "isolation_config": dict(ISOLATION_CONFIG),
    }


def _manifest_digest(value: Mapping[str, Any]) -> str:
    identity = {
        key: item
        for key, item in value.items()
        if key not in {"manifest_id", "manifest_sha256", "artifact_dir"}
    }
    return _sha256_json(identity)


def create_manifest(
    stage: str,
    seed: Optional[int] = None,
    output: Optional[Path] = None,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
    candidate_dir: Path = DEFAULT_CANDIDATE_DIR,
    screen_cases: Path = DEFAULT_SCREEN_CASES,
    confirm_cases: Path = DEFAULT_CONFIRM_CASES,
    screen_manifest: Optional[Path] = None,
) -> Tuple[Path, Dict[str, Any]]:
    if stage not in STAGE_CANDIDATES:
        raise ValidationError("stage must be screen or confirm")
    if stage == "confirm" and screen_manifest is None:
        raise ValidationError(
            "confirm planning requires --screen-manifest to prove frozen inputs"
        )
    validated = validate_inputs(candidate_dir, screen_cases, confirm_cases)
    if seed is None:
        seed = secrets.randbits(63)
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**63:
        raise ValidationError("seed must be an integer in 0..2^63-1")

    selected_ids = STAGE_CANDIDATES[stage]
    selected_candidates = {
        key: validated["candidates"]["candidates"][key] for key in selected_ids
    }
    cases = list(validated[stage]["cases"])
    rng = random.Random(seed)
    rng.shuffle(cases)
    runs: List[Dict[str, Any]] = []
    order = 0
    for case in cases:
        prompt = render_user_prompt(case)
        for repetition in range(1, REPETITIONS + 1):
            condition_order = list(selected_ids)
            rng.shuffle(condition_order)
            for candidate_id in condition_order:
                order += 1
                runs.append(
                    {
                        "run_id": "%s-r%d-%s" % (
                            case["id"],
                            repetition,
                            candidate_id.lower(),
                        ),
                        "case_id": case["id"],
                        "candidate_id": candidate_id,
                        "repetition": repetition,
                        "order": order,
                        "prompt_sha256": _sha256_bytes(prompt.encode("utf-8")),
                    }
                )

    config = _plan_config()
    hashes = {
        "runner_sha256": _sha256_file(Path(__file__).resolve()),
        "candidate_set_sha256": validated["candidates"]["candidate_set_sha256"],
        "candidate_sources": validated["candidates"]["sources"],
        "case_files": {
            validated["screen"]["source"]: validated["screen"]["source_sha256"],
            validated["confirm"]["source"]: validated["confirm"]["source_sha256"],
        },
        "cases_sha256": _sha256_json(cases),
        "config_sha256": _sha256_json(config),
    }
    payload = {
        "schema_version": MANIFEST_VERSION,
        "created_at": _utc_now(),
        "stage": stage,
        "seed": seed,
        "config": config,
        "thresholds": dict(THRESHOLDS),
        "hashes": hashes,
        "common": validated["candidates"]["common"],
        "candidates": selected_candidates,
        "cases": cases,
        "runs": runs,
    }
    if screen_manifest is not None:
        prior = load_manifest(Path(screen_manifest), check_sources=False)
        if prior["stage"] != "screen":
            raise ValidationError("--screen-manifest must point to a screen manifest")
        for key in (
            "runner_sha256",
            "candidate_set_sha256",
            "case_files",
            "config_sha256",
        ):
            if prior["hashes"].get(key) != hashes.get(key):
                raise ValidationError(
                    "confirm inputs changed since screen manifest (%s mismatch)" % key
                )
        payload["frozen_against_screen_manifest_id"] = prior["manifest_id"]

    payload["manifest_sha256"] = _manifest_digest(payload)
    payload["manifest_id"] = payload["manifest_sha256"][:16]

    if output is None:
        root = _require_external(Path(artifact_root), "artifact root")
        output = root / (
            "%s-%s-%s" % (stage, _timestamp(), payload["manifest_id"])
        ) / "manifest.json"
    output = _require_external(Path(output), "manifest output")
    if output.exists():
        raise ValidationError("refusing to overwrite frozen manifest: %s" % output)
    payload["artifact_dir"] = str(output.parent)
    _write_json(output, payload)
    return output, payload


def _verify_current_sources(manifest: Mapping[str, Any]) -> None:
    if _sha256_file(Path(__file__).resolve()) != manifest["hashes"].get(
        "runner_sha256"
    ):
        raise ValidationError("eval.py changed after planning")
    for name, expected in manifest["hashes"]["candidate_sources"].items():
        path = REPO_ROOT / name
        if not path.is_file() or _sha256_file(path) != expected:
            raise ValidationError("candidate source changed after planning: %s" % name)
    for name, expected in manifest["hashes"]["case_files"].items():
        path = REPO_ROOT / name
        if not path.is_file() or _sha256_file(path) != expected:
            raise ValidationError("case source changed after planning: %s" % name)


def load_manifest(path: Path, check_sources: bool = True) -> Dict[str, Any]:
    path = _require_external(Path(path), "manifest")
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != MANIFEST_VERSION:
        raise ValidationError("invalid manifest schema: %s" % path)
    digest = _manifest_digest(data)
    if data.get("manifest_sha256") != digest or data.get("manifest_id") != digest[:16]:
        raise ValidationError("manifest_id integrity check failed")
    stage = data.get("stage")
    if stage not in STAGE_CANDIDATES:
        raise ValidationError("invalid manifest stage")
    required = {
        "schema_version",
        "created_at",
        "stage",
        "seed",
        "manifest_id",
        "manifest_sha256",
        "config",
        "thresholds",
        "hashes",
        "common",
        "candidates",
        "cases",
        "runs",
        "artifact_dir",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValidationError("manifest is missing fields: %s" % missing)
    extra = set(data) - required - {"frozen_against_screen_manifest_id"}
    if extra:
        raise ValidationError("manifest has unexpected fields: %s" % sorted(extra))
    seed = data["seed"]
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**63:
        raise ValidationError("manifest seed is invalid")
    if set(data["candidates"]) != set(STAGE_CANDIDATES[stage]):
        raise ValidationError("manifest has wrong candidates for %s" % stage)
    if data["config"] != _plan_config():
        raise ValidationError("manifest execution config is not the fixed evaluation config")
    if data["hashes"].get("config_sha256") != _sha256_json(data["config"]):
        raise ValidationError("manifest config hash mismatch")
    if not isinstance(data["hashes"].get("runner_sha256"), str):
        raise ValidationError("manifest runner hash is missing")
    if data["hashes"].get("cases_sha256") != _sha256_json(data["cases"]):
        raise ValidationError("manifest cases hash mismatch")
    if data["thresholds"] != THRESHOLDS:
        raise ValidationError("manifest thresholds differ from the preregistration")
    for candidate_id, candidate in data["candidates"].items():
        developer = candidate.get("developer_instructions")
        if not isinstance(developer, str) or not developer:
            raise ValidationError("manifest candidate instructions are missing")
        expected = _sha256_bytes(developer.encode("utf-8"))
        if candidate.get("developer_sha256") != expected:
            raise ValidationError("manifest candidate hash mismatch: %s" % candidate_id)
    # A stage contains a subset of the global candidate set.  Source hashes are
    # the authoritative global fingerprint; embedded candidate hashes protect
    # the instructions used by this stage.
    if not isinstance(data["hashes"].get("candidate_set_sha256"), str):
        raise ValidationError("manifest candidate-set hash is missing")

    if len(data["cases"]) != STAGE_CASE_COUNTS[stage]:
        raise ValidationError("manifest has wrong case count")
    case_map: Dict[str, Dict[str, Any]] = {}
    for index, case in enumerate(data["cases"]):
        checked = _validate_case(case, "manifest", index)
        if checked["id"] in case_map:
            raise ValidationError("manifest contains duplicate case ID")
        case_map[checked["id"]] = checked
    category_counts = Counter(case["category"] for case in case_map.values())
    if len(category_counts) != 6 or any(
        count != STAGE_CATEGORY_COUNTS[stage] for count in category_counts.values()
    ):
        raise ValidationError("manifest has wrong category counts")
    expected_runs = len(case_map) * len(STAGE_CANDIDATES[stage]) * REPETITIONS
    if not isinstance(data["runs"], list) or len(data["runs"]) != expected_runs:
        raise ValidationError("manifest has wrong run count")
    run_ids = set()
    combinations = set()
    orders = []
    for run in data["runs"]:
        if not isinstance(run, dict):
            raise ValidationError("manifest run must be an object")
        expected_run_fields = {
            "run_id",
            "case_id",
            "candidate_id",
            "repetition",
            "order",
            "prompt_sha256",
        }
        if set(run) != expected_run_fields:
            raise ValidationError("manifest run has wrong fields")
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9-]+", run_id):
            raise ValidationError("manifest run_id is invalid")
        if run_id in run_ids:
            raise ValidationError("manifest contains duplicate run_id")
        run_ids.add(run_id)
        case_id = run.get("case_id")
        candidate_id = run.get("candidate_id")
        repetition = run.get("repetition")
        if case_id not in case_map or candidate_id not in data["candidates"]:
            raise ValidationError("manifest run has an unknown reference")
        if repetition not in (1, 2):
            raise ValidationError("manifest repetition must be 1 or 2")
        order = run.get("order")
        if isinstance(order, bool) or not isinstance(order, int):
            raise ValidationError("manifest run order must be an integer")
        orders.append(order)
        combination = (case_id, candidate_id, repetition)
        if combination in combinations:
            raise ValidationError("manifest contains duplicate run combination")
        combinations.add(combination)
        prompt = render_user_prompt(case_map[case_id])
        if run.get("prompt_sha256") != _sha256_bytes(prompt.encode("utf-8")):
            raise ValidationError("manifest prompt hash mismatch: %s" % run_id)
    if sorted(orders) != list(range(1, expected_runs + 1)):
        raise ValidationError("manifest run order must be a 1..N permutation")
    artifact_dir = _require_external(Path(data["artifact_dir"]), "artifact directory")
    if artifact_dir != path.parent.resolve():
        raise ValidationError("manifest artifact_dir must match its parent directory")
    if check_sources:
        _verify_current_sources(data)
    return data


def _text_contents(messages: Any, role: str) -> List[str]:
    found: List[str] = []
    if not isinstance(messages, list):
        return found
    for message in messages:
        if not isinstance(message, dict) or message.get("role") != role:
            continue
        content = message.get("content", [])
        if isinstance(content, str):
            found.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    found.append(item["text"])
    return found


def _all_text_contents(messages: Any) -> List[str]:
    found: List[str] = []
    if not isinstance(messages, list):
        return found
    for message in messages:
        if not isinstance(message, dict):
            continue
        content = message.get("content", [])
        if isinstance(content, str):
            found.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    found.append(item["text"])
    return found


def _capture_with_timeout(
    argv: Sequence[str], cwd: Path, env: Mapping[str, str], timeout: int
) -> Tuple[int, str, str, bool]:
    """Capture a subprocess and kill its whole process group on timeout."""
    process = subprocess.Popen(
        list(argv),
        cwd=str(cwd),
        env=dict(env),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=(os.name == "posix"),
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr, timed_out


def _debug_preflight(manifest: Mapping[str, Any], artifact_dir: Path) -> None:
    case = manifest["cases"][0]
    prompt = render_user_prompt(case)
    preflight_dir = artifact_dir / "preflight"
    _ensure_private_dir(preflight_dir)
    for candidate_id in manifest["candidates"]:
        candidate = manifest["candidates"][candidate_id]
        developer = candidate["developer_instructions"]
        output_path = preflight_dir / (candidate_id.lower() + ".prompt-input.json")
        stderr_path = preflight_dir / (candidate_id.lower() + ".stderr.txt")
        config = dict(ISOLATION_CONFIG)
        config["model"] = MODEL
        config["developer_instructions"] = developer
        argv = ["codex", "debug", "prompt-input"] + _config_args(config) + [prompt]
        with tempfile.TemporaryDirectory(prefix="language-style-preflight-") as temp_root:
            root = Path(temp_root)
            cwd = root / "workspace"
            cwd.mkdir()
            env, _ = _isolated_codex_environment(root)
            returncode, stdout, stderr, timed_out = _capture_with_timeout(
                argv, cwd, env, 60
            )
        _write_text(output_path, stdout)
        _write_text(stderr_path, stderr)
        if timed_out:
            raise ValidationError(
                "codex debug prompt-input timed out for %s; see %s"
                % (candidate_id, stderr_path)
            )
        if returncode != 0:
            raise ValidationError(
                "codex debug prompt-input failed for %s; see %s"
                % (candidate_id, stderr_path)
            )
        try:
            messages = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise ValidationError("prompt-input did not return JSON") from exc
        developer_texts = _text_contents(messages, "developer")
        user_texts = _text_contents(messages, "user")
        if developer_texts.count(developer) != 1:
            raise ValidationError(
                "model-visible prompt must contain exact developer instructions once for %s"
                % candidate_id
            )
        if user_texts.count(prompt) != 1:
            raise ValidationError(
                "model-visible prompt must contain exact user prompt once for %s" % candidate_id
            )
        remaining = list(_all_text_contents(messages))
        remaining.remove(developer)
        contaminated = [
            text
            for text in remaining
            if PROMPT_CONTAMINATION_RE.search(text) or EXTERNAL_SKILL_PATH_RE.search(text)
        ]
        if contaminated:
            raise ValidationError(
                "model-visible prompt contains external language-style instructions for %s"
                % candidate_id
            )
    _write_json(
        preflight_dir / "result.json",
        {
            "status": "pass",
            "checked_at": _utc_now(),
            "candidate_ids": list(manifest["candidates"]),
            "isolation": "temporary CODEX_HOME with auth.json symlink only",
            "contamination_check": "pass",
        },
    )


def _parse_jsonl(path: Path) -> Tuple[List[Any], List[str]]:
    events: List[Any] = []
    errors: List[str] = []
    try:
        lines = _read_utf8_exact(path).splitlines()
    except FileNotFoundError:
        return [], ["trace file is missing"]
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append("line %d: %s" % (number, exc))
    if not events:
        errors.append("trace contains no JSON events")
    return events, errors


def _walk_objects(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_objects(child)


def _tool_payloads(events: Sequence[Any]) -> Iterable[str]:
    tool_types = {
        "command_execution",
        "function_call",
        "tool_call",
        "mcp_tool_call",
        "dynamic_tool_call",
        "computer_tool_call",
    }
    for event in events:
        for obj in _walk_objects(event):
            item_type = str(obj.get("type", "")).lower()
            if item_type in tool_types:
                yield json.dumps(obj, ensure_ascii=False, sort_keys=True)


def trace_contamination(events: Sequence[Any]) -> List[str]:
    matches: List[str] = []
    for payload in _tool_payloads(events):
        match = CONTAMINATION_RE.search(payload)
        if match:
            excerpt = payload[max(0, match.start() - 80) : match.end() + 80]
            matches.append(excerpt)
    return matches


def _trace_completed(events: Sequence[Any]) -> bool:
    for event in events:
        if isinstance(event, dict) and event.get("type") == "turn.completed":
            return True
    return False


def _trace_usage(events: Sequence[Any]) -> Optional[Dict[str, Any]]:
    last: Optional[Dict[str, Any]] = None
    for event in events:
        for obj in _walk_objects(event):
            usage = obj.get("usage")
            if isinstance(usage, dict) and any(
                key in usage for key in ("input_tokens", "output_tokens", "total_tokens")
            ):
                last = dict(usage)
    return last


def _classify_attempt(
    case: Mapping[str, Any],
    output: str,
    events: Sequence[Any],
    trace_errors: Sequence[str],
    contamination: Sequence[str],
    returncode: Optional[int],
    timed_out: bool,
    spawn_error: Optional[str],
) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """Derive an attempt outcome only from immutable artifacts and process facts."""
    check = hard_check(case, output) if output.strip() else None
    if timed_out:
        return "not_run", "timeout", check
    if spawn_error:
        return "not_run", "spawn_error", check
    if returncode != 0:
        return "not_run", "codex_exit_%s" % returncode, check
    if not output.strip():
        return "not_run", "empty_output", check
    if trace_errors:
        return "inconclusive", "invalid_or_truncated_trace", check
    if not _trace_completed(events):
        return "inconclusive", "trace_missing_turn_completed", check
    if contamination:
        return "inconclusive", "external_language_skill_contamination", check
    assert check is not None
    return check["status"], "hard_checks_" + check["status"], check


def _numeric_literals(text: str) -> List[str]:
    # Treat each consecutive digit run as one literal.  This intentionally
    # sees list markers and the numeric parts of `p99`, `v1.2`, dates, times,
    # IDs, and units.  Fixtures explicitly allow required procedure numbers.
    pattern = re.compile(r"\d+")
    return [match.group(0) for match in pattern.finditer(text)]


def _normalize_number(value: str) -> str:
    return value


def _extract_code_blocks(text: str) -> List[Dict[str, str]]:
    pattern = re.compile(
        r"^```([^\n]*)\n(.*?)\n^```[ \t]*$", re.MULTILINE | re.DOTALL
    )
    blocks = []
    for match in pattern.finditer(text):
        blocks.append(
            {
                "raw": match.group(0),
                "info": match.group(1),
                "content": match.group(2),
            }
        )
    return blocks


def _ordered_marker_position(output: str, marker: str, cursor: int) -> int:
    structural = marker.startswith(("#", "|")) or re.match(r"^\d+[.)]\s", marker)
    if structural:
        match = re.compile(r"^ {0,3}" + re.escape(marker), re.MULTILINE).search(
            output, cursor
        )
        return match.start() if match else -1
    return output.find(marker, cursor)


def hard_check(case: Mapping[str, Any], output: str) -> Dict[str, Any]:
    failures: List[Dict[str, Any]] = []

    def fail(gate: str, detail: Any) -> None:
        failures.append({"gate": gate, "detail": detail})

    if not output.strip():
        fail("nonempty", "output is empty")
    length = len(output)
    if length < case["min_chars"] or length > case["max_chars"]:
        fail(
            "length",
            {
                "actual": length,
                "min": case["min_chars"],
                "max": case["max_chars"],
            },
        )
    for value in case["required_substrings"]:
        if value not in output:
            fail("required_substring", value)
    for value in case["protected_literals"]:
        if value not in output:
            fail("protected_literal", value)
    for value in case["forbidden_substrings"]:
        if value in output:
            fail("forbidden_substring", value)

    allowed = {_normalize_number(value) for value in case["allowed_numbers"]}
    unexpected = sorted(
        {
            value
            for value in _numeric_literals(output)
            if _normalize_number(value) not in allowed
        }
    )
    for value in unexpected:
        fail("unexpected_number", value)

    headings = []
    for line in output.splitlines():
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
        if match:
            heading_text = re.sub(r"\s+#+\s*$", "", match.group(2))
            headings.append(match.group(1) + " " + heading_text)
    positions: List[int] = []
    for expected in case["required_headings"]:
        try:
            positions.append(headings.index(expected))
        except ValueError:
            fail("required_heading", expected)
    if len(positions) == len(case["required_headings"]) and positions != sorted(positions):
        fail("heading_order", case["required_headings"])

    cursor = 0
    for marker in case["ordered_markers"]:
        position = _ordered_marker_position(output, marker, cursor)
        if position < 0:
            fail("ordered_marker", marker)
        else:
            cursor = position + len(marker)

    blocks = _extract_code_blocks(output)
    if case["exact_code_blocks"] and len(blocks) != len(case["exact_code_blocks"]):
        fail(
            "fenced_code_block_count",
            {"expected": len(case["exact_code_blocks"]), "actual": len(blocks)},
        )
    for expected in case["exact_code_blocks"]:
        matches = sum(block["raw"] == expected for block in blocks)
        if matches != 1:
            fail("exact_code_block", {"block": expected, "matches": matches})

    return {
        "schema_version": CHECK_VERSION,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "metrics": {
            "chars": length,
            "numeric_literals": _numeric_literals(output),
            "fenced_code_blocks": len(blocks),
        },
    }


def _run_result_path(artifact_dir: Path, run_id: str) -> Path:
    return artifact_dir / "runs" / run_id / "result.json"


def _case_index(manifest: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {case["id"]: case for case in manifest["cases"]}


def _load_existing_result(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != RUN_RESULT_VERSION:
        raise ValidationError("invalid run result: %s" % path)
    return data


def _validate_run_result(
    manifest: Mapping[str, Any],
    run: Mapping[str, Any],
    case: Mapping[str, Any],
    result: Mapping[str, Any],
    verify_check: bool = True,
) -> None:
    identity = {
        "manifest_id": manifest["manifest_id"],
        "run_id": run["run_id"],
        "case_id": run["case_id"],
        "candidate_id": run["candidate_id"],
        "repetition": run["repetition"],
    }
    for key, expected in identity.items():
        if result.get(key) != expected:
            raise ValidationError("run result identity mismatch for %s" % run["run_id"])
    if result.get("status") not in {"pass", "fail", "not_run", "inconclusive"}:
        raise ValidationError("run result has invalid status: %s" % run["run_id"])
    attempts = result.get("attempts")
    latest = result.get("latest")
    if not isinstance(attempts, list) or not attempts or not isinstance(latest, dict):
        raise ValidationError("run result attempts are incomplete: %s" % run["run_id"])
    if [attempt.get("attempt") for attempt in attempts] != list(
        range(1, len(attempts) + 1)
    ):
        raise ValidationError("run result attempt order is invalid: %s" % run["run_id"])
    if any(
        attempt.get("status") not in {"pass", "fail", "not_run", "inconclusive"}
        for attempt in attempts
    ):
        raise ValidationError("run result attempt status is invalid: %s" % run["run_id"])
    if latest != attempts[-1]:
        raise ValidationError("run result latest attempt is stale: %s" % run["run_id"])
    if latest.get("status") != result.get("status"):
        raise ValidationError("run result status is stale: %s" % run["run_id"])
    if latest.get("reason") != result.get("reason"):
        raise ValidationError("run result reason is stale: %s" % run["run_id"])

    run_dir = Path(manifest["artifact_dir"]) / "runs" / run["run_id"]
    for attempt in attempts:
        for path_field, hash_field, required in (
            (
                "output_path",
                "output_sha256",
                attempt.get("status") in {"pass", "fail"},
            ),
            ("trace_path", "trace_sha256", True),
            ("stderr_path", "stderr_sha256", True),
            ("command_path", "command_sha256", True),
        ):
            raw_path = attempt.get(path_field)
            path = Path(raw_path) if isinstance(raw_path, str) and raw_path else None
            if path is None or not _is_within(path, run_dir):
                raise ValidationError("run artifact path escaped its run directory")
            if required and not path.is_file():
                raise ValidationError("run artifact is missing: %s" % path)
            expected_hash = attempt.get(hash_field)
            if path.is_file():
                if not isinstance(expected_hash, str) or _sha256_file(path) != expected_hash:
                    raise ValidationError("run artifact hash mismatch: %s" % path)
            elif expected_hash is not None:
                raise ValidationError("missing artifact has a hash: %s" % path)

        timed_out = attempt.get("timed_out")
        returncode = attempt.get("returncode")
        spawn_error = attempt.get("spawn_error")
        if not isinstance(timed_out, bool):
            raise ValidationError("run attempt timed_out is invalid: %s" % run["run_id"])
        if isinstance(returncode, bool) or not (
            returncode is None or isinstance(returncode, int)
        ):
            raise ValidationError("run attempt returncode is invalid: %s" % run["run_id"])
        if spawn_error is not None and (
            not isinstance(spawn_error, str) or not spawn_error
        ):
            raise ValidationError("run attempt spawn_error is invalid: %s" % run["run_id"])

        output_path = Path(attempt["output_path"])
        output = _read_utf8_exact(output_path) if output_path.is_file() else ""
        trace_path = Path(attempt["trace_path"])
        events, trace_errors = _parse_jsonl(trace_path)
        contamination = trace_contamination(events)
        usage = _trace_usage(events)
        status, reason, check = _classify_attempt(
            case,
            output,
            events,
            trace_errors,
            contamination,
            returncode,
            timed_out,
            spawn_error,
        )
        derived = {
            "status": status,
            "reason": reason,
            "trace_errors": trace_errors,
            "contamination": contamination,
            "usage": usage,
            "check": check,
        }
        for field, expected in derived.items():
            if attempt.get(field) != expected:
                raise ValidationError(
                    "run attempt %s is stale for %s" % (field, run["run_id"])
                )

        command = _read_json(Path(attempt["command_path"]))
        if not isinstance(command, dict) or set(command) != {
            "argv",
            "cwd",
            "codex_home_isolated",
            "stdin_sha256",
        }:
            raise ValidationError("run command metadata is invalid: %s" % run["run_id"])
        cwd = command.get("cwd")
        if not isinstance(cwd, str) or not cwd or not Path(cwd).is_absolute():
            raise ValidationError("run command cwd is invalid: %s" % run["run_id"])
        expected_argv = _codex_exec_argv(
            manifest["candidates"][run["candidate_id"]]["developer_instructions"],
            output_path,
            cwd,
        )
        if command.get("argv") != expected_argv:
            raise ValidationError("run command argv is stale: %s" % run["run_id"])
        if command.get("codex_home_isolated") is not True:
            raise ValidationError("run command was not isolated: %s" % run["run_id"])
        expected_stdin = _sha256_bytes(render_user_prompt(case).encode("utf-8"))
        if command.get("stdin_sha256") != expected_stdin:
            raise ValidationError("run command prompt is stale: %s" % run["run_id"])

    # `verify_check` is retained for the public helper signature.  Attempt
    # status is always re-derived so pass/fail can never bypass trace gates.
    del verify_check


def _codex_exec_argv(developer: str, output_path: Path, cwd: str) -> List[str]:
    config = dict(ISOLATION_CONFIG)
    config["developer_instructions"] = developer
    return [
        "codex",
        "exec",
        "--ignore-user-config",
        "--strict-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--ephemeral",
        "--model",
        MODEL,
        "--sandbox",
        "read-only",
        "--color",
        "never",
        "--json",
        "--output-last-message",
        str(output_path),
        "-C",
        cwd,
    ] + _config_args(config) + ["-"]


def _execute_attempt(
    manifest: Mapping[str, Any],
    run: Mapping[str, Any],
    case: Mapping[str, Any],
    attempt_number: int,
    timeout: int,
) -> Dict[str, Any]:
    artifact_dir = Path(manifest["artifact_dir"])
    run_dir = artifact_dir / "runs" / run["run_id"]
    _ensure_private_dir(run_dir)
    stem = "attempt-%02d" % attempt_number
    output_path = run_dir / (stem + ".md")
    trace_path = run_dir / (stem + ".trace.jsonl")
    stderr_path = run_dir / (stem + ".stderr.txt")
    command_path = run_dir / (stem + ".command.json")
    prompt = render_user_prompt(case)
    developer = manifest["candidates"][run["candidate_id"]][
        "developer_instructions"
    ]
    started_at = _utc_now()
    started = time.monotonic()
    returncode: Optional[int] = None
    timed_out = False
    spawn_error: Optional[str] = None
    with tempfile.TemporaryDirectory(prefix="language-style-run-") as temp_root:
        root = Path(temp_root)
        cwd = root / "workspace"
        cwd.mkdir()
        env, _ = _isolated_codex_environment(root)
        argv = _codex_exec_argv(developer, output_path, str(cwd))
        _write_json(
            command_path,
            {
                "argv": argv,
                "cwd": str(cwd),
                "codex_home_isolated": True,
                "stdin_sha256": _sha256_bytes(prompt.encode("utf-8")),
            },
        )
        try:
            with trace_path.open("w", encoding="utf-8") as trace_handle, stderr_path.open(
                "w", encoding="utf-8"
            ) as stderr_handle:
                process = subprocess.Popen(
                    argv,
                    cwd=str(cwd),
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=trace_handle,
                    stderr=stderr_handle,
                    text=True,
                    start_new_session=(os.name == "posix"),
                )
                try:
                    process.communicate(prompt, timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    if os.name == "posix":
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    else:
                        process.kill()
                    process.communicate()
                returncode = process.returncode
        except OSError as exc:
            spawn_error = "%s: %s" % (type(exc).__name__, exc)
            if not trace_path.exists():
                _write_text(trace_path, "")
            _write_text(stderr_path, spawn_error + "\n")
    latency = time.monotonic() - started

    output = _read_utf8_exact(output_path) if output_path.is_file() else ""
    for artifact in (output_path, trace_path, stderr_path, command_path):
        if artifact.is_file():
            artifact.chmod(0o600)
    events, trace_errors = _parse_jsonl(trace_path)
    contamination = trace_contamination(events)
    usage = _trace_usage(events)
    status, reason, check_result = _classify_attempt(
        case,
        output,
        events,
        trace_errors,
        contamination,
        returncode,
        timed_out,
        spawn_error,
    )
    return {
        "attempt": attempt_number,
        "status": status,
        "reason": reason,
        "started_at": started_at,
        "latency_seconds": round(latency, 6),
        "returncode": returncode,
        "timed_out": timed_out,
        "spawn_error": spawn_error,
        "output_path": str(output_path),
        "output_sha256": _sha256_file(output_path) if output_path.is_file() else None,
        "trace_path": str(trace_path),
        "trace_sha256": _sha256_file(trace_path) if trace_path.is_file() else None,
        "stderr_path": str(stderr_path),
        "stderr_sha256": _sha256_file(stderr_path) if stderr_path.is_file() else None,
        "command_path": str(command_path),
        "command_sha256": _sha256_file(command_path),
        "trace_errors": trace_errors,
        "contamination": contamination,
        "usage": usage,
        "check": check_result,
    }


@contextlib.contextmanager
def _exclusive_run_lock(run_dir: Path) -> Iterable[None]:
    """Serialize one run across concurrent runner processes."""
    _ensure_private_dir(run_dir)
    lock_path = run_dir / ".run.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        lock_path.chmod(0o600)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _run_one_locked(
    manifest: Mapping[str, Any],
    run: Mapping[str, Any],
    case: Mapping[str, Any],
    retries: int,
    timeout: int,
) -> Dict[str, Any]:
    artifact_dir = Path(manifest["artifact_dir"])
    result_path = _run_result_path(artifact_dir, run["run_id"])
    existing = _load_existing_result(result_path)
    if existing is not None:
        _validate_run_result(manifest, run, case, existing, verify_check=True)
    if existing and existing.get("status") in {"pass", "fail"}:
        return existing
    attempts = list(existing.get("attempts", [])) if existing else []
    # A fresh invocation may retry a prior inconclusive result, but within one
    # invocation only infrastructure-level `not_run` results are retried.
    max_attempts = len(attempts) + retries + 1
    while len(attempts) < max_attempts:
        attempt = _execute_attempt(
            manifest, run, case, len(attempts) + 1, timeout
        )
        attempts.append(attempt)
        result = {
            "schema_version": RUN_RESULT_VERSION,
            "manifest_id": manifest["manifest_id"],
            "run_id": run["run_id"],
            "case_id": run["case_id"],
            "candidate_id": run["candidate_id"],
            "repetition": run["repetition"],
            "status": attempt["status"],
            "reason": attempt["reason"],
            "attempts": attempts,
            "latest": attempt,
            "updated_at": _utc_now(),
        }
        _write_json(result_path, result)
        if attempt["status"] != "not_run":
            return result
    return _load_existing_result(result_path) or result


def _run_one(
    manifest: Mapping[str, Any],
    run: Mapping[str, Any],
    case: Mapping[str, Any],
    retries: int,
    timeout: int,
) -> Dict[str, Any]:
    run_dir = Path(manifest["artifact_dir"]) / "runs" / run["run_id"]
    with _exclusive_run_lock(run_dir):
        return _run_one_locked(manifest, run, case, retries, timeout)


def run_manifest(
    manifest_path: Path,
    workers: int = 1,
    retries: int = 1,
    timeout: int = 600,
) -> Dict[str, Any]:
    if workers < 1 or workers > 32:
        raise ValidationError("workers must be in 1..32")
    if retries < 0 or retries > 5:
        raise ValidationError("retries must be in 0..5")
    if timeout < 30 or timeout > 3600:
        raise ValidationError("timeout must be in 30..3600 seconds")
    manifest = load_manifest(Path(manifest_path), check_sources=True)
    artifact_dir = Path(manifest["artifact_dir"])
    _debug_preflight(manifest, artifact_dir)
    cases = _case_index(manifest)
    ordered_runs = sorted(manifest["runs"], key=lambda item: item["order"])
    results: List[Dict[str, Any]] = []
    lock = threading.Lock()

    def work(run: Mapping[str, Any]) -> Dict[str, Any]:
        result = _run_one(
            manifest, run, cases[run["case_id"]], retries, timeout
        )
        with lock:
            results.append(result)
        return result

    if workers == 1:
        for run in ordered_runs:
            work(run)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(work, run) for run in ordered_runs]
            for future in concurrent.futures.as_completed(futures):
                future.result()
    counts = Counter(result["status"] for result in results)
    summary = {
        "manifest_id": manifest["manifest_id"],
        "stage": manifest["stage"],
        "total": len(results),
        "status_counts": dict(sorted(counts.items())),
        "successful_model_calls": sum(
            1 for result in results if result["status"] in {"pass", "fail"}
        ),
        "attempts": sum(len(result.get("attempts", [])) for result in results),
        "completed_at": _utc_now(),
    }
    attempt_statuses: Counter = Counter()
    retry_causes: Counter = Counter()
    for result in results:
        for attempt in result.get("attempts", []):
            attempt_statuses[attempt.get("status", "unknown")] += 1
            if attempt.get("status") in {"not_run", "inconclusive"}:
                retry_causes[attempt.get("reason", "unknown")] += 1
    summary["attempt_status_counts"] = dict(sorted(attempt_statuses.items()))
    summary["retry_causes"] = dict(sorted(retry_causes.items()))
    summary["target_successful_model_calls"] = len(ordered_runs)
    summary["complete"] = summary["successful_model_calls"] == len(ordered_runs)
    _write_json(artifact_dir / "run-summary.json", summary)
    return summary


def check_manifest(manifest_path: Path) -> Dict[str, Any]:
    manifest = load_manifest(Path(manifest_path), check_sources=True)
    artifact_dir = Path(manifest["artifact_dir"])
    cases = _case_index(manifest)
    counts: Counter = Counter()
    details = []
    for run in manifest["runs"]:
        result_path = _run_result_path(artifact_dir, run["run_id"])
        result = _load_existing_result(result_path)
        if result is None:
            counts["not_run"] += 1
            details.append({"run_id": run["run_id"], "status": "not_run"})
            continue
        _validate_run_result(
            manifest, run, cases[run["case_id"]], result, verify_check=False
        )
        latest = result.get("latest", {})
        output_path = Path(latest.get("output_path", ""))
        if result["status"] in {"not_run", "inconclusive"} or not output_path.is_file():
            counts[result["status"]] += 1
            details.append(
                {
                    "run_id": run["run_id"],
                    "status": result["status"],
                    "reason": result.get("reason"),
                }
            )
            continue
        output = _read_utf8_exact(output_path)
        check = hard_check(cases[run["case_id"]], output)
        result["status"] = check["status"]
        result["reason"] = "hard_checks_" + check["status"]
        result["latest"]["check"] = check
        result["latest"]["status"] = check["status"]
        result["latest"]["reason"] = "hard_checks_" + check["status"]
        result["attempts"][-1] = dict(result["latest"])
        result["updated_at"] = _utc_now()
        _write_json(result_path, result)
        counts[check["status"]] += 1
        details.append(
            {
                "run_id": run["run_id"],
                "status": check["status"],
                "failures": check["failures"],
            }
        )
    report = {
        "schema_version": CHECK_VERSION,
        "manifest_id": manifest["manifest_id"],
        "checked_at": _utc_now(),
        "status_counts": dict(sorted(counts.items())),
        "details": details,
    }
    _write_json(artifact_dir / "checks.json", report)
    return report


def _collect_manifests(paths: Sequence[Path]) -> List[Dict[str, Any]]:
    # Review and analysis semantics are part of the frozen runner.  Requiring
    # current sources prevents a newer analyzer from silently reinterpreting
    # results planned with another revision.
    manifests = [load_manifest(Path(path), check_sources=True) for path in paths]
    stages = [manifest["stage"] for manifest in manifests]
    if len(stages) != len(set(stages)):
        raise ValidationError("only one manifest per stage may be combined")
    if len(manifests) > 1:
        first = manifests[0]
        for manifest in manifests[1:]:
            for key in (
                "runner_sha256",
                "candidate_set_sha256",
                "case_files",
                "config_sha256",
            ):
                if manifest["hashes"].get(key) != first["hashes"].get(key):
                    raise ValidationError("manifest mismatch for %s" % key)
        by_stage = {manifest["stage"]: manifest for manifest in manifests}
        if set(by_stage) == {"screen", "confirm"} and by_stage["confirm"].get(
            "frozen_against_screen_manifest_id"
        ) != by_stage["screen"]["manifest_id"]:
            raise ValidationError("confirm manifest is not frozen against this screen manifest")
    return manifests


def _result_index(
    manifests: Sequence[Mapping[str, Any]],
) -> Dict[Tuple[str, str, int], Dict[str, Any]]:
    result: Dict[Tuple[str, str, int], Dict[str, Any]] = {}
    for manifest in manifests:
        artifact_dir = Path(manifest["artifact_dir"])
        cases = _case_index(manifest)
        for run in manifest["runs"]:
            loaded = _load_existing_result(
                _run_result_path(artifact_dir, run["run_id"])
            )
            if loaded is not None:
                _validate_run_result(
                    manifest, run, cases[run["case_id"]], loaded, verify_check=True
                )
                result[(run["case_id"], run["candidate_id"], run["repetition"])] = loaded
    return result


def _result_output(result: Mapping[str, Any]) -> Optional[str]:
    if result.get("status") not in {"pass", "fail"}:
        return None
    path = Path(result.get("latest", {}).get("output_path", ""))
    if not path.is_file():
        return None
    text = _read_utf8_exact(path)
    return text if text.strip() else None


def _review_html(review_id: str, pairs: List[Dict[str, Any]]) -> str:
    public_bundle_sha256 = _sha256_json(
        {"pairs": pairs, "axes": list(RATING_AXES)}
    )
    data_json = json.dumps(
        {
            "review_id": review_id,
            "public_bundle_sha256": public_bundle_sha256,
            "pairs": pairs,
            "axes": list(RATING_AXES),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    template = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>한국어 문체 블라인드 평가</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;max-width:1500px;margin:0 auto;padding:24px;background:#f6f7f9;color:#17202a}
h1{font-size:1.6rem}.toolbar{position:sticky;top:0;background:#f6f7f9;padding:10px 0;z-index:3}.task{background:white;border:1px solid #d9dee5;border-radius:12px;margin:20px 0;padding:20px}.context{white-space:pre-wrap;background:#eef2f6;padding:12px;border-radius:8px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}.side{min-width:0}.output{white-space:pre-wrap;overflow-wrap:anywhere;background:#111827;color:#f3f4f6;padding:14px;border-radius:8px;min-height:160px}.rep{border-top:1px solid #e5e7eb;padding-top:12px;margin-top:12px}.scores{border-collapse:collapse;width:100%;margin-top:14px}.scores th,.scores td{border:1px solid #d9dee5;padding:8px;text-align:center}.scores th:first-child{text-align:left}.pref{display:flex;gap:20px;margin-top:14px}.missing{color:#a33}button{padding:9px 14px;margin-right:8px}@media(max-width:850px){.pair{grid-template-columns:1fr}}
</style>
</head>
<body>
<h1>한국어 문체 블라인드 평가</h1>
<p>같은 과제의 두 반복 결과를 함께 읽고, 각 축의 왼쪽·오른쪽 점수와 전체 선호를 기록하세요.</p>
<div class="toolbar"><button id="save">브라우저에 저장</button><button id="download">JSON 다운로드</button><span id="status"></span></div>
<main id="tasks"></main>
<script>
const bundle=__REVIEW_DATA__;
const storageKey="language-style-review:"+bundle.review_id;
const labels={technical_accuracy:"기술적 정확성과 완전성",clarity:"명료성",naturalness:"자연스러운 한국어",concision:"불필요한 반복과 장황함이 적음",structure_fit:"구조와 어조 적합성"};
let state={};try{state=JSON.parse(localStorage.getItem(storageKey)||"{}")}catch(e){state={}}
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
function scoreSelect(pairId,axis,side){const s=document.createElement("select");s.dataset.pair=pairId;s.dataset.axis=axis;s.dataset.side=side;const blank=document.createElement("option");blank.value="";blank.textContent="-";s.appendChild(blank);for(let i=1;i<=5;i++){const o=document.createElement("option");o.value=String(i);o.textContent=String(i);s.appendChild(o)}const old=state[pairId]?.scores?.[axis]?.[side];if(old)s.value=String(old);s.onchange=save;return s}
function save(){for(const p of bundle.pairs){const entry=state[p.pair_id]||{scores:{},preference:""};for(const axis of bundle.axes){entry.scores[axis]=entry.scores[axis]||{};for(const side of ["left","right"]){const n=document.querySelector(`select[data-pair="${p.pair_id}"][data-axis="${axis}"][data-side="${side}"]`);entry.scores[axis][side]=n&&n.value?Number(n.value):null}}const checked=document.querySelector(`input[name="pref-${p.pair_id}"]:checked`);entry.preference=checked?checked.value:"";state[p.pair_id]=entry}localStorage.setItem(storageKey,JSON.stringify(state));document.getElementById("status").textContent=" 저장됨"}
function render(){const root=document.getElementById("tasks");bundle.pairs.forEach((p,index)=>{const card=el("section","task");card.appendChild(el("h2",null,`${index+1}. ${p.task_id} · ${p.category}`));card.appendChild(el("div","context",p.prompt+"\n\n[근거]\n"+p.evidence));for(const rep of p.repetitions){card.appendChild(el("h3","rep",`반복 ${rep.repetition}`));const grid=el("div","pair");for(const side of ["left","right"]){const col=el("div","side");col.appendChild(el("h4",null,side==="left"?"왼쪽":"오른쪽"));col.appendChild(el("pre","output",rep[side]));grid.appendChild(col)}card.appendChild(grid)}const table=el("table","scores");const head=document.createElement("tr");for(const text of ["평가 축","왼쪽","오른쪽"]){head.appendChild(el("th",null,text))}table.appendChild(head);for(const axis of bundle.axes){const row=document.createElement("tr");row.appendChild(el("th",null,labels[axis]));for(const side of ["left","right"]){const td=document.createElement("td");td.appendChild(scoreSelect(p.pair_id,axis,side));row.appendChild(td)}table.appendChild(row)}card.appendChild(table);const pref=el("div","pref");for(const option of [["left","왼쪽"],["tie","동률"],["right","오른쪽"]]){const label=document.createElement("label");const input=document.createElement("input");input.type="radio";input.name=`pref-${p.pair_id}`;input.value=option[0];input.checked=state[p.pair_id]?.preference===option[0];input.onchange=save;label.appendChild(input);label.appendChild(document.createTextNode(" "+option[1]));pref.appendChild(label)}card.appendChild(pref);root.appendChild(card)})}
document.getElementById("save").onclick=save;
document.getElementById("download").onclick=()=>{save();const payload={schema_version:"language-style-review-v1",review_id:bundle.review_id,public_bundle_sha256:bundle.public_bundle_sha256,saved_at:new Date().toISOString(),ratings:state};const blob=new Blob([JSON.stringify(payload,null,2)+"\n"],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`ratings-${bundle.review_id}.json`;a.click();URL.revokeObjectURL(a.href)};
render();
</script>
</body>
</html>
"""
    return template.replace("__REVIEW_DATA__", data_json, 1)


def create_review_bundle(
    manifest_paths: Sequence[Path],
    output: Optional[Path] = None,
    key_output: Optional[Path] = None,
    seed: Optional[int] = None,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
) -> Tuple[Path, Path, Dict[str, Any]]:
    manifests = _collect_manifests(manifest_paths)
    if seed is None:
        seed = secrets.randbits(63)
    rng = random.Random(seed)
    results = _result_index(manifests)
    cases = []
    for manifest in manifests:
        cases.extend(manifest["cases"])
    case_ids = [case["id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValidationError("review manifests contain duplicate task IDs")
    rng.shuffle(cases)
    public_pairs: List[Dict[str, Any]] = []
    key_pairs: Dict[str, Any] = {}
    omitted: List[Dict[str, Any]] = []
    for case in cases:
        orientation = ("A", "B") if rng.randrange(2) == 0 else ("B", "A")
        repetitions = []
        repetition_lineage = []
        missing = []
        for repetition in range(1, REPETITIONS + 1):
            left_result = results.get((case["id"], orientation[0], repetition))
            right_result = results.get((case["id"], orientation[1], repetition))
            left = _result_output(left_result or {})
            right = _result_output(right_result or {})
            if left is None or right is None:
                missing.append(repetition)
            else:
                repetitions.append(
                    {"repetition": repetition, "left": left, "right": right}
                )
                repetition_lineage.append(
                    {
                        "repetition": repetition,
                        "left": {
                            "run_id": left_result["run_id"],
                            "output_sha256": left_result["latest"]["output_sha256"],
                        },
                        "right": {
                            "run_id": right_result["run_id"],
                            "output_sha256": right_result["latest"]["output_sha256"],
                        },
                    }
                )
        if missing:
            omitted.append({"task_id": case["id"], "missing_repetitions": missing})
            continue
        pair_id = "pair-" + _sha256_bytes(
            ("%s:%s:%d" % (case["id"], seed, len(public_pairs))).encode("utf-8")
        )[:12]
        public_pairs.append(
            {
                "pair_id": pair_id,
                "task_id": case["id"],
                "category": case["category"],
                "prompt": case["prompt"],
                "evidence": case["evidence"],
                "repetitions": repetitions,
            }
        )
        key_pairs[pair_id] = {
            "task_id": case["id"],
            "category": case["category"],
            "left": orientation[0],
            "right": orientation[1],
            "repetitions": repetition_lineage,
        }
    manifest_ids = [manifest["manifest_id"] for manifest in manifests]
    public_bundle_sha256 = _sha256_json(
        {"pairs": public_pairs, "axes": list(RATING_AXES)}
    )
    html_template_sha256 = _sha256_bytes(
        _review_html("__REVIEW_ID__", public_pairs).encode("utf-8")
    )
    review_material = {
        "manifest_ids": manifest_ids,
        "seed": seed,
        "pairs": key_pairs,
        "public_bundle_sha256": public_bundle_sha256,
        "html_template_sha256": html_template_sha256,
    }
    review_id = _sha256_json(review_material)[:16]
    if output is None:
        root = _require_external(Path(artifact_root), "artifact root")
        output = root / ("review-%s-%s" % (_timestamp(), review_id)) / "review.html"
    output = _require_external(Path(output), "review output")
    if key_output is None:
        key_output = output.parent / "private" / "review-key.json"
    key_output = _require_external(Path(key_output), "review key output")
    if output.resolve() == key_output.resolve():
        raise ValidationError("review HTML and key must be separate files")
    html = _review_html(review_id, public_pairs)
    _write_text(output, html)
    key = {
        "schema_version": REVIEW_KEY_VERSION,
        "review_id": review_id,
        "created_at": _utc_now(),
        "seed": seed,
        "manifest_ids": manifest_ids,
        "pairs": key_pairs,
        "omitted": omitted,
        "public_bundle_sha256": public_bundle_sha256,
        "html_template_sha256": html_template_sha256,
        "html_path": str(output.resolve()),
        "html_sha256": _sha256_file(output),
    }
    _write_json(key_output, key)
    return output, key_output, key


def exact_sign_test_p(wins: int, losses: int) -> float:
    if isinstance(wins, bool) or isinstance(losses, bool):
        raise ValidationError("wins and losses must be non-negative integers")
    if not isinstance(wins, int) or not isinstance(losses, int):
        raise ValidationError("wins and losses must be non-negative integers")
    if wins < 0 or losses < 0:
        raise ValidationError("wins and losses must be non-negative integers")
    n = wins + losses
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(wins, n + 1)) / float(2**n)


def _automatic_summary(
    manifests: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    by_candidate: Dict[str, Dict[str, Any]] = {}
    gate_counts: Dict[str, Counter] = defaultdict(Counter)
    violation_counts: Dict[str, Counter] = defaultdict(Counter)
    result_index = _result_index(manifests)
    expected_total_runs = sum(len(manifest["runs"]) for manifest in manifests)
    result_statuses = Counter(result["status"] for result in result_index.values())
    all_candidate_ids = sorted(
        {candidate for manifest in manifests for candidate in manifest["candidates"]}
    )
    for candidate_id in all_candidate_ids:
        expected_runs = sum(
            len(manifest["cases"]) * REPETITIONS
            for manifest in manifests
            if candidate_id in manifest["candidates"]
        )
        rows = [
            result
            for (_, candidate, _), result in result_index.items()
            if candidate == candidate_id
        ]
        statuses = Counter(result["status"] for result in rows)
        latencies = [
            result.get("latest", {}).get("latency_seconds")
            for result in rows
            if isinstance(result.get("latest", {}).get("latency_seconds"), (int, float))
        ]
        input_tokens = []
        output_tokens = []
        for result in rows:
            check = result.get("latest", {}).get("check")
            if isinstance(check, dict):
                for failure in check.get("failures", []):
                    gate = failure.get("gate", "unknown")
                    gate_counts[candidate_id][gate] += 1
                    detail = json.dumps(
                        failure.get("detail"), ensure_ascii=False, sort_keys=True
                    )
                    violation_counts[candidate_id][(gate, detail)] += 1
            usage = result.get("latest", {}).get("usage")
            if isinstance(usage, dict):
                if isinstance(usage.get("input_tokens"), int):
                    input_tokens.append(usage["input_tokens"])
                if isinstance(usage.get("output_tokens"), int):
                    output_tokens.append(usage["output_tokens"])
        by_candidate[candidate_id] = {
            "runs_expected": expected_runs,
            "runs_present": len(rows),
            "runs_missing": expected_runs - len(rows),
            "status_counts": dict(sorted(statuses.items())),
            "hard_failures": statuses.get("fail", 0),
            "critical_gate_failures": sum(
                count
                for gate, count in gate_counts[candidate_id].items()
                if gate in CRITICAL_GATES
            ),
            "gate_failures": dict(sorted(gate_counts[candidate_id].items())),
            "mean_latency_seconds": (
                sum(latencies) / len(latencies) if latencies else None
            ),
            "total_input_tokens": sum(input_tokens) if input_tokens else None,
            "total_output_tokens": sum(output_tokens) if output_tokens else None,
        }
    repeated_critical = {
        candidate_id: [
            {"gate": gate, "detail": json.loads(detail), "count": count}
            for (gate, detail), count in sorted(
                violation_counts.get(candidate_id, {}).items()
            )
            if gate in CRITICAL_GATES and count >= 2
        ]
        for candidate_id in ("A", "B")
    }
    repeated_b = repeated_critical["B"]
    a_failures = by_candidate.get("A", {}).get("critical_gate_failures", 0)
    b_failures = by_candidate.get("B", {}).get("critical_gate_failures", 0)
    preservation_ok = b_failures <= a_failures and not repeated_b

    # A baseline alert requires a material and repeated difference.  It is an
    # automatic safety stop, not a style-quality finding.
    baseline_alert = False
    if "C" in by_candidate:
        def rate(candidate_id: str) -> float:
            row = by_candidate[candidate_id]
            total = row["runs_expected"]
            return row["status_counts"].get("pass", 0) / total if total else 0.0

        if (
            by_candidate["C"]["critical_gate_failures"] == 0
            and by_candidate.get("A", {}).get("critical_gate_failures", 0) >= 2
            and by_candidate.get("B", {}).get("critical_gate_failures", 0) >= 2
            and rate("C") >= max(rate("A"), rate("B")) + 0.10
        ):
            baseline_alert = True
    return {
        "runs_expected": expected_total_runs,
        "runs_present": len(result_index),
        "run_status_counts": dict(sorted(result_statuses.items())),
        "execution_complete": (
            len(result_index) == expected_total_runs
            and set(result_statuses).issubset({"pass", "fail"})
        ),
        "by_candidate": by_candidate,
        "hybrid_preservation_not_worse": preservation_ok,
        "hybrid_repeated_critical_failures": repeated_b,
        "baseline_safety_alert": baseline_alert,
        "both_style_candidates_repeat_critical_failures": bool(
            repeated_critical["A"] and repeated_critical["B"]
        ),
    }


def _review_bundle_from_html(html: str) -> Dict[str, Any]:
    prefix = "const bundle="
    suffix = ";\nconst storageKey="
    start = html.find(prefix)
    if start < 0:
        raise ValidationError("review HTML does not contain its public bundle")
    start += len(prefix)
    end = html.find(suffix, start)
    if end < 0:
        raise ValidationError("review HTML public bundle is truncated")
    try:
        bundle = json.loads(html[start:end])
    except json.JSONDecodeError as exc:
        raise ValidationError("review HTML public bundle is invalid") from exc
    if not isinstance(bundle, dict):
        raise ValidationError("review HTML public bundle must be an object")
    return bundle


def _load_review_key(path: Path) -> Dict[str, Any]:
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != REVIEW_KEY_VERSION:
        raise ValidationError("invalid review key: %s" % path)
    if not isinstance(data.get("pairs"), dict):
        raise ValidationError("review key pairs must be an object")
    if not isinstance(data.get("review_id"), str) or not data["review_id"]:
        raise ValidationError("review key review_id is invalid")
    if not isinstance(data.get("manifest_ids"), list) or any(
        not isinstance(value, str) for value in data["manifest_ids"]
    ):
        raise ValidationError("review key manifest_ids are invalid")
    task_ids = []
    for pair_id, mapping in data["pairs"].items():
        if not isinstance(pair_id, str) or not isinstance(mapping, dict):
            raise ValidationError("review key pair is invalid")
        if {mapping.get("left"), mapping.get("right")} != {"A", "B"}:
            raise ValidationError("review key pair must blind A and B")
        if not isinstance(mapping.get("task_id"), str) or not isinstance(
            mapping.get("category"), str
        ):
            raise ValidationError("review key task identity is invalid")
        repetitions = mapping.get("repetitions")
        if not isinstance(repetitions, list) or [
            row.get("repetition") if isinstance(row, dict) else None
            for row in repetitions
        ] != list(range(1, REPETITIONS + 1)):
            raise ValidationError("review key repetitions are invalid")
        for repetition in repetitions:
            for side in ("left", "right"):
                lineage = repetition.get(side)
                if (
                    not isinstance(lineage, dict)
                    or not isinstance(lineage.get("run_id"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", str(lineage.get("output_sha256", "")))
                ):
                    raise ValidationError("review key output lineage is invalid")
        task_ids.append(mapping["task_id"])
    if len(task_ids) != len(set(task_ids)):
        raise ValidationError("review key contains duplicate tasks")
    public_digest = data.get("public_bundle_sha256")
    template_digest = data.get("html_template_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", str(public_digest or "")) or not re.fullmatch(
        r"[0-9a-f]{64}", str(template_digest or "")
    ):
        raise ValidationError("review key bundle hashes are invalid")
    expected_review_id = _sha256_json(
        {
            "manifest_ids": data["manifest_ids"],
            "seed": data.get("seed"),
            "pairs": data["pairs"],
            "public_bundle_sha256": public_digest,
            "html_template_sha256": template_digest,
        }
    )[:16]
    if data["review_id"] != expected_review_id:
        raise ValidationError("review key integrity check failed")
    html_path_raw = data.get("html_path")
    html_sha256 = data.get("html_sha256")
    if not isinstance(html_path_raw, str) or not Path(html_path_raw).is_absolute():
        raise ValidationError("review key HTML path is invalid")
    html_path = Path(html_path_raw)
    if not html_path.is_file() or _sha256_file(html_path) != html_sha256:
        raise ValidationError("review HTML hash mismatch")
    html = _read_utf8_exact(html_path)
    bundle = _review_bundle_from_html(html)
    if bundle.get("review_id") != data["review_id"]:
        raise ValidationError("review HTML review_id does not match key")
    public_pairs = bundle.get("pairs")
    if not isinstance(public_pairs, list) or bundle.get("axes") != list(RATING_AXES):
        raise ValidationError("review HTML public bundle is invalid")
    if bundle.get("public_bundle_sha256") != public_digest:
        raise ValidationError("review HTML declared bundle hash mismatch")
    if _sha256_json({"pairs": public_pairs, "axes": list(RATING_AXES)}) != public_digest:
        raise ValidationError("review HTML public bundle hash mismatch")
    if _sha256_bytes(
        _review_html("__REVIEW_ID__", public_pairs).encode("utf-8")
    ) != template_digest:
        raise ValidationError("review HTML template hash mismatch")
    if html != _review_html(data["review_id"], public_pairs):
        raise ValidationError("review HTML is not the frozen review bundle")
    return data


def _load_ratings(
    path: Path, expected_review_id: str, expected_public_bundle_sha256: str
) -> Dict[str, Any]:
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != REVIEW_VERSION:
        raise ValidationError("invalid ratings file: %s" % path)
    if data.get("review_id") != expected_review_id:
        raise ValidationError("ratings review_id does not match review key")
    if data.get("public_bundle_sha256") != expected_public_bundle_sha256:
        raise ValidationError("ratings public bundle does not match review key")
    if not isinstance(data.get("ratings"), dict):
        raise ValidationError("ratings must be an object")
    return data


def _validate_review_lineage(
    key: Mapping[str, Any], manifests: Sequence[Mapping[str, Any]]
) -> None:
    """Bind a rating key to the currently validated run outputs."""
    results = _result_index(manifests)
    for pair_id, mapping in key["pairs"].items():
        for repetition in mapping["repetitions"]:
            number = repetition["repetition"]
            for side in ("left", "right"):
                candidate_id = mapping[side]
                result = results.get((mapping["task_id"], candidate_id, number))
                if result is None:
                    raise ValidationError(
                        "review key result is missing for %s" % pair_id
                    )
                expected = repetition[side]
                current = {
                    "run_id": result["run_id"],
                    "output_sha256": result["latest"].get("output_sha256"),
                }
                if current != expected:
                    raise ValidationError(
                        "review key output lineage is stale for %s" % pair_id
                    )


def _human_summary(
    rating_paths: Sequence[Path], key_path: Path
) -> Dict[str, Any]:
    key = _load_review_key(key_path)
    resolved_rating_paths = [Path(path).resolve() for path in rating_paths]
    if len(resolved_rating_paths) != len(set(resolved_rating_paths)):
        raise ValidationError("ratings paths must be unique")
    rating_hashes = [_sha256_file(path) for path in resolved_rating_paths]
    if len(rating_hashes) != len(set(rating_hashes)):
        raise ValidationError("ratings files must have unique content")
    rating_files = [
        _load_ratings(path, key["review_id"], key["public_bundle_sha256"])
        for path in resolved_rating_paths
    ]
    task_rows: Dict[str, Dict[str, Any]] = {}
    invalid: List[str] = []
    for pair_id, mapping in key["pairs"].items():
        axis_diffs: Dict[str, List[float]] = defaultdict(list)
        preferences: List[str] = []
        valid_reviewers = 0
        for reviewer, ratings_file in enumerate(rating_files, 1):
            entry = ratings_file["ratings"].get(pair_id)
            if not isinstance(entry, dict):
                invalid.append("reviewer %d missing %s" % (reviewer, pair_id))
                continue
            scores = entry.get("scores")
            if not isinstance(scores, dict):
                invalid.append("reviewer %d has invalid scores for %s" % (reviewer, pair_id))
                continue
            complete = True
            for axis in RATING_AXES:
                row = scores.get(axis)
                if not isinstance(row, dict):
                    complete = False
                    break
                left, right = row.get("left"), row.get("right")
                if (
                    isinstance(left, bool)
                    or isinstance(right, bool)
                    or not isinstance(left, (int, float))
                    or not isinstance(right, (int, float))
                    or not 1 <= left <= 5
                    or not 1 <= right <= 5
                ):
                    complete = False
                    break
                diff = left - right if mapping["left"] == "B" else right - left
                axis_diffs[axis].append(float(diff))
            preference = entry.get("preference")
            if preference not in {"left", "tie", "right"}:
                complete = False
            if not complete:
                invalid.append("reviewer %d has incomplete %s" % (reviewer, pair_id))
                continue
            valid_reviewers += 1
            if preference == "tie":
                preferences.append("tie")
            elif mapping[preference] == "B":
                preferences.append("B")
            else:
                preferences.append("A")
        if valid_reviewers != len(rating_files) or not all(
            len(axis_diffs[axis]) == len(rating_files) for axis in RATING_AXES
        ):
            continue
        b_votes = preferences.count("B")
        a_votes = preferences.count("A")
        majority = len(rating_files) / 2.0
        winner = "B" if b_votes > majority else "A" if a_votes > majority else "tie"
        task_rows[mapping["task_id"]] = {
            "category": mapping["category"],
            "axis_deltas_b_minus_a": {
                axis: sum(axis_diffs[axis]) / len(axis_diffs[axis])
                for axis in RATING_AXES
            },
            "preference": winner,
        }
    wins = sum(row["preference"] == "B" for row in task_rows.values())
    losses = sum(row["preference"] == "A" for row in task_rows.values())
    ties = sum(row["preference"] == "tie" for row in task_rows.values())
    axis_means = {
        axis: (
            sum(row["axis_deltas_b_minus_a"][axis] for row in task_rows.values())
            / len(task_rows)
            if task_rows
            else None
        )
        for axis in RATING_AXES
    }
    category_axes: Dict[str, Dict[str, float]] = {}
    category_means: Dict[str, float] = {}
    categories = sorted({row["category"] for row in task_rows.values()})
    for category in categories:
        rows = [row for row in task_rows.values() if row["category"] == category]
        category_axes[category] = {
            axis: sum(row["axis_deltas_b_minus_a"][axis] for row in rows) / len(rows)
            for axis in RATING_AXES
        }
        category_means[category] = sum(category_axes[category].values()) / len(
            RATING_AXES
        )
    return {
        "review_id": key["review_id"],
        "manifest_ids": key["manifest_ids"],
        "reviewers": len(rating_files),
        "expected_tasks": len(key["pairs"]),
        "complete_tasks": len(task_rows),
        "invalid": invalid,
        "task_results": task_rows,
        "preference": {
            "hybrid_wins": wins,
            "im_only_wins": losses,
            "ties": ties,
            "non_ties": wins + losses,
            "hybrid_fraction": wins / (wins + losses) if wins + losses else None,
            "one_sided_exact_sign_p": exact_sign_test_p(wins, losses),
        },
        "axis_mean_deltas_b_minus_a": axis_means,
        "category_axis_deltas_b_minus_a": category_axes,
        "category_mean_deltas_b_minus_a": category_means,
    }


def analyze(
    manifest_paths: Sequence[Path],
    rating_paths: Sequence[Path] = (),
    key_path: Optional[Path] = None,
) -> Dict[str, Any]:
    manifests = _collect_manifests(manifest_paths)
    automatic = _automatic_summary(manifests)
    human = None
    if rating_paths:
        if key_path is None:
            raise ValidationError("--key is required when --ratings is used")
        review_key = _load_review_key(Path(key_path))
        _validate_review_lineage(review_key, manifests)
        human = _human_summary(rating_paths, Path(key_path))
        if set(human["manifest_ids"]) != {
            manifest["manifest_id"] for manifest in manifests
        }:
            raise ValidationError("review key does not match analyzed manifests")

    expected_ab_tasks = sum(len(manifest["cases"]) for manifest in manifests)
    full_experiment = (
        {manifest["stage"] for manifest in manifests} == {"screen", "confirm"}
        and expected_ab_tasks == 30
    )
    reasons: List[str] = []
    if not full_experiment:
        recommendation = None
        decision_status = "inconclusive"
        reasons.append("both frozen screen and confirm stages are required")
    elif not automatic["execution_complete"]:
        recommendation = None
        decision_status = "inconclusive"
        reasons.append("all 144 runs must finish as pass or fail before analysis")
    elif automatic["baseline_safety_alert"] or automatic[
        "both_style_candidates_repeat_critical_failures"
    ]:
        recommendation = "reduce-im-rules"
        decision_status = "safety_stop"
        if automatic["baseline_safety_alert"]:
            reasons.append(
                "screen baseline has materially fewer repeated preservation failures"
            )
        if automatic["both_style_candidates_repeat_critical_failures"]:
            reasons.append("both style candidates repeat critical preservation failures")
    elif human is None:
        recommendation = None
        decision_status = "awaiting_human_review"
        reasons.append("human blind ratings are not available")
    elif human["complete_tasks"] != expected_ab_tasks or human["invalid"]:
        recommendation = None
        decision_status = "inconclusive"
        reasons.append("human ratings are incomplete")
    else:
        pref = human["preference"]
        axes = human["axis_mean_deltas_b_minus_a"]
        category_values = list(
            human["category_mean_deltas_b_minus_a"].values()
        )
        gates = {
            "preservation": automatic["hybrid_preservation_not_worse"],
            "preference_fraction": (
                pref["hybrid_fraction"] is not None
                and pref["hybrid_fraction"] >= THRESHOLDS["preference_min_fraction"]
            ),
            "sign_test": pref["one_sided_exact_sign_p"]
            < THRESHOLDS["sign_test_p_max_exclusive"],
            "clarity": axes["clarity"] >= THRESHOLDS["clarity_min_delta"],
            "naturalness": axes["naturalness"]
            >= THRESHOLDS["naturalness_min_delta"],
            "technical_accuracy": axes["technical_accuracy"]
            >= THRESHOLDS["technical_accuracy_min_delta"],
            "category_regression": bool(category_values)
            and min(category_values) >= THRESHOLDS["category_mean_min_delta"],
        }
        human["adoption_gates"] = gates
        if all(gates.values()):
            recommendation = "hybrid"
            decision_status = "criteria_met"
            reasons.append("all preregistered hybrid adoption thresholds are met")
        else:
            recommendation = "im-only"
            relevant = [axes["clarity"], axes["naturalness"], axes["technical_accuracy"]]
            if all(abs(value) <= THRESHOLDS["equivalence_abs_delta"] for value in relevant):
                decision_status = "practical_equivalence"
                reasons.append("main rating deltas are inside the practical-equivalence band")
            else:
                decision_status = "criteria_not_met"
                reasons.append("one or more hybrid adoption thresholds are not met")

    return {
        "schema_version": ANALYSIS_VERSION,
        "created_at": _utc_now(),
        "manifest_ids": [manifest["manifest_id"] for manifest in manifests],
        "automatic": automatic,
        "human": human,
        "thresholds": dict(THRESHOLDS),
        "decision": {
            "recommendation": recommendation,
            "status": decision_status,
            "reasons": reasons,
            "requires_user_approval": True,
        },
    }


def _path(value: str) -> Path:
    return Path(value).expanduser()


def _add_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--candidate-dir", type=_path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--screen-cases", type=_path, default=DEFAULT_SCREEN_CASES)
    parser.add_argument("--confirm-cases", type=_path, default=DEFAULT_CONFIRM_CASES)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate fixtures")
    _add_input_args(validate_parser)

    plan_parser = subparsers.add_parser("plan", help="create a frozen manifest")
    plan_parser.add_argument("--stage", choices=("screen", "confirm"), required=True)
    plan_parser.add_argument("--seed", type=int)
    plan_parser.add_argument("--output", type=_path)
    plan_parser.add_argument("--artifact-root", type=_path, default=DEFAULT_ARTIFACT_ROOT)
    plan_parser.add_argument("--screen-manifest", type=_path)
    _add_input_args(plan_parser)

    run_parser = subparsers.add_parser("run", help="execute a frozen manifest")
    run_parser.add_argument("--manifest", type=_path, required=True)
    run_parser.add_argument("--workers", type=int, default=1)
    run_parser.add_argument("--retries", type=int, default=1)
    run_parser.add_argument("--timeout", type=int, default=600)

    check_parser = subparsers.add_parser("check", help="recompute hard gates")
    check_parser.add_argument("--manifest", type=_path, required=True)

    review_parser = subparsers.add_parser("review", help="build blind review HTML")
    review_parser.add_argument("--manifest", type=_path, action="append", required=True)
    review_parser.add_argument("--output", type=_path)
    review_parser.add_argument("--key-output", type=_path)
    review_parser.add_argument("--seed", type=int)
    review_parser.add_argument("--artifact-root", type=_path, default=DEFAULT_ARTIFACT_ROOT)

    analyze_parser = subparsers.add_parser("analyze", help="analyze checks and ratings")
    analyze_parser.add_argument("--manifest", type=_path, action="append", required=True)
    analyze_parser.add_argument("--ratings", type=_path, action="append", default=[])
    analyze_parser.add_argument("--key", type=_path)
    analyze_parser.add_argument("--output", type=_path)
    analyze_parser.add_argument("--artifact-root", type=_path, default=DEFAULT_ARTIFACT_ROOT)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_inputs(
                args.candidate_dir, args.screen_cases, args.confirm_cases
            )["summary"]
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "plan":
            path, manifest = create_manifest(
                args.stage,
                seed=args.seed,
                output=args.output,
                artifact_root=args.artifact_root,
                candidate_dir=args.candidate_dir,
                screen_cases=args.screen_cases,
                confirm_cases=args.confirm_cases,
                screen_manifest=args.screen_manifest,
            )
            print(
                json.dumps(
                    {
                        "manifest": str(path),
                        "manifest_id": manifest["manifest_id"],
                        "stage": manifest["stage"],
                        "runs": len(manifest["runs"]),
                        "seed": manifest["seed"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        if args.command == "run":
            summary = run_manifest(
                args.manifest, args.workers, args.retries, args.timeout
            )
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0 if summary["complete"] else 2
        if args.command == "check":
            report = check_manifest(args.manifest)
            print(json.dumps(report["status_counts"], ensure_ascii=False, indent=2))
            return 0 if set(report["status_counts"]) <= {"pass"} else 1
        if args.command == "review":
            output, key, metadata = create_review_bundle(
                args.manifest,
                output=args.output,
                key_output=args.key_output,
                seed=args.seed,
                artifact_root=args.artifact_root,
            )
            print(
                json.dumps(
                    {
                        "html": str(output),
                        "key": str(key),
                        "review_id": metadata["review_id"],
                        "pairs": len(metadata["pairs"]),
                        "omitted": metadata["omitted"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0 if not metadata["omitted"] else 2
        if args.command == "analyze":
            report = analyze(args.manifest, args.ratings, args.key)
            if args.output is None:
                root = _require_external(args.artifact_root, "artifact root")
                output = root / ("analysis-%s.json" % _timestamp())
            else:
                output = _require_external(args.output, "analysis output")
            _write_json(output, report)
            print(
                json.dumps(
                    {"output": str(output), "decision": report["decision"]},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
    except (ValidationError, OSError, subprocess.SubprocessError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
