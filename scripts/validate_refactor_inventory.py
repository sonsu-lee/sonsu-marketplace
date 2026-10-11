#!/usr/bin/env python3
"""리팩터링 인벤토리가 저장소의 실제 단위를 빠짐없이 최신 상태로 기록하는지 검사한다."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ".agents/plugins/marketplace.json"
RENDER_OMP = "scripts/render-omp-compat.py"
DEFAULT_INVENTORY = "docs/research/refactor-inventory"
REPORT = "docs/research/refactor-assessment.md"
REPORT_START = "<!-- inventory-report:start -->"
REPORT_END = "<!-- inventory-report:end -->"
REPOSITORY = "repository"

# 다른 정본에서 생성되거나 캐시인 파일은 플러그인 스크립트 단위로 세지 않는다.
GENERATED_SCRIPTS = {"task-continuity.py", "validate_design_quality.py", "design_md.mjs", "review-package"}
# 플러그인 root의 omp/(render-omp-compat.py)와 claude/(render-claude-compat.py)는 생성된 호스트 미러다.
GENERATED_ROOTS = {"omp", "claude"}
# 실행 도구를 찾을 때 테스트·빌드 산출물·의존성·캐시 디렉터리는 내려가지 않는다.
SKIP_DIRS = {"tests", "dist", "node_modules", "__pycache__"}
TOOL_SUFFIXES = {".py", ".sh", ".js", ".mjs", ".cjs", ".ts"}
TEST_FILE = re.compile(r"^test_.+\.py$|_test\.py$|\.test\.[cm]?[jt]s$")

VERDICT = {"keep", "merge", "to-reference", "replace-with-existing", "new-tool", "delete"}
ASSET_VERDICT = VERDICT - {"new-tool"}
OMP = {"default", "opt-in", "not-distributed"}
PROPOSAL = {"none", "script", "validator", "existing-cli"}
KIND = ("negative-definition", "history", "duplicate-rule", "missing-example", "structure", "internal-detail")
EXAMPLE = {"present", "weak", "missing"}
TARGETED_VERDICTS = {"merge", "to-reference", "replace-with-existing"}
OMP_FEATURES = {"todo", "session", "memory", "subagents", "web-search", "review", "ask", "browser", "lsp"}
LOCATION = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")

NEGATIVE = re.compile(r"않는다|않습니다|않음|금지|하지 마|아니다|아닙니다|NEVER|MUST NOT|[Dd]o not|[Dd]on't")
DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
HISTORY = re.compile(r"이전 (이름|호출명|버전|구성|방식)|에서 이동|더 이상 사용|deprecated|[Mm]igrat")
EXAMPLE_HEADING = re.compile(r"^#+ .*(예시|Example|例)")


class AnalysisError(Exception):
    """분석을 끝낼 수 없는 입력 오류."""


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path, root):
    return path.relative_to(root).as_posix()


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AnalysisError(f"{path}: {error}") from error


# ---------------------------------------------------------------- 단위 열거


def load_catalog(root):
    data = read_json(root / CATALOG)
    try:
        return [entry["name"] for entry in data["plugins"]]
    except (KeyError, TypeError) as error:
        raise AnalysisError(f"{CATALOG}: plugins[].name is missing") from error


def omp_status(root):
    path = root / RENDER_OMP
    write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # 검사 대상 저장소에 __pycache__를 남기지 않는다.
    try:
        spec = importlib.util.spec_from_file_location("render_omp_compat", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        default, optin = set(module.OMP_PLUGINS), set(module.OMP_OPTIN_PLUGINS)
    except Exception as error:  # noqa: BLE001 - 어떤 import 실패든 분석 미완료다.
        raise AnalysisError(f"{RENDER_OMP}: {error}") from error
    finally:
        sys.dont_write_bytecode = write_bytecode

    def status(name):
        if name in default:
            return "default"
        if name in optin:
            return "opt-in"
        return "not-distributed"

    return status


def skill_roots(plugin_dir):
    manifest = read_json(plugin_dir / ".codex-plugin/plugin.json")
    roots = []
    value = manifest.get("skills")
    if isinstance(value, str):
        roots.append(value.removeprefix("./").rstrip("/") + "/")
    claude = plugin_dir / ".claude-plugin/plugin.json"
    if (claude.is_file() and "skills" not in read_json(claude) and
            (plugin_dir / "skills").is_dir() and "skills/" not in roots):
        roots.append("skills/")
    return [root for root in roots if root.split("/", 1)[0] not in GENERATED_ROOTS]


def is_tool(path):
    """scripts/ 안의 파일, 스크립트 확장자 파일, shebang 파일을 실행 도구로 본다."""
    if path.name in GENERATED_SCRIPTS or path.suffix == ".pyc" or TEST_FILE.search(path.name):
        return False
    if path.parent.name == "scripts" or path.suffix in TOOL_SUFFIXES:
        return True
    with path.open("rb") as file:
        return file.read(2) == b"#!"


def tool_files(plugin_dir, root):
    """생성 미러·테스트·빌드 산출물을 뺀 플러그인 정본 트리의 실행 도구를 열거한다."""
    found = []
    pending = [plugin_dir]
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            if path.name.startswith(".") or path.is_symlink():
                continue
            if path.is_dir():
                if path.name not in SKIP_DIRS and not (directory == plugin_dir and path.name in GENERATED_ROOTS):
                    pending.append(path)
            elif path.is_file() and is_tool(path):
                found.append(rel(path, root))
    return sorted(found)


def skill_metrics(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return {
        "lines": len(lines),
        "negative_lines": sum(bool(NEGATIVE.search(line)) for line in lines),
        "date_mentions": sum(bool(DATE.search(line)) for line in lines),
        "history_mentions": sum(bool(HISTORY.search(line)) for line in lines),
        "has_example": any(line.startswith("```") or EXAMPLE_HEADING.search(line) for line in lines),
    }


def enumerate_units(root):
    catalog = load_catalog(root)
    status = omp_status(root)
    plugins = []
    for name in catalog:
        plugin_dir = root / "plugins" / name
        skills = []
        scripts = tool_files(plugin_dir, root)
        for skill_root in skill_roots(plugin_dir):
            base = plugin_dir / skill_root
            if not base.is_dir():
                continue
            for skill in sorted(base.glob("*/SKILL.md")):
                skills.append({"path": rel(skill, root), "sha256": sha256(skill), **skill_metrics(skill)})
        plugins.append({
            "name": name,
            "manifest_sha256": sha256(plugin_dir / ".codex-plugin/plugin.json"),
            "omp_current": status(name),
            "skills": skills,
            "scripts": [{"path": path, "sha256": sha256(root / path)} for path in sorted(scripts)],
        })
    uncatalogued = sorted(
        path.parent.parent.name
        for path in (root / "plugins").glob("*/.codex-plugin/plugin.json")
        if path.parent.parent.name not in catalog
    )

    def children(name, want_dir):
        base = root / name
        if not base.is_dir():
            return []
        return [
            rel(path, root)
            for path in sorted(base.iterdir())
            if path.name != "__pycache__" and (path.is_dir() if want_dir else path.is_file())
        ]

    repository = {
        "scripts": [{"path": path, "sha256": sha256(root / path)} for path in children("scripts", False)],
        "shared": children("shared", True),
        "evals": children("evals", True),
    }
    return {"plugins": plugins, "repository": repository}, uncatalogued


# ---------------------------------------------------------------- 필드 검사


class Checker:
    def __init__(self, root, units):
        self.root = root
        self.units = units
        self.violations = []
        self.skill_names = {
            (plugin["name"], Path(skill["path"]).parent.name)
            for plugin in units["plugins"]
            for skill in plugin["skills"]
        }
        self.catalog = [plugin["name"] for plugin in units["plugins"]]
        self.line_counts = {}
        self.digests = {}

    def add(self, code, where, message):
        self.violations.append((code, where, message))

    def str_field(self, obj, key, where, allow_empty=False):
        value = obj.get(key)
        if not isinstance(value, str) or (not allow_empty and not value.strip()):
            kind = "str?" if allow_empty else "non-empty str"
            self.add("invalid-field", f"{where}.{key}", f"must be {kind}")
            return None
        return value

    def enum_field(self, obj, key, allowed, where):
        value = obj.get(key)
        if not isinstance(value, str) or value not in allowed:
            self.add("invalid-field", f"{where}.{key}", f"must be one of {', '.join(sorted(allowed))}")
            return None
        return value

    def list_field(self, obj, key, where):
        value = obj.get(key)
        if not isinstance(value, list):
            self.add("invalid-field", f"{where}.{key}", "must be an array")
            return []
        return value

    def object_keys(self, obj, keys, where):
        if not isinstance(obj, dict):
            self.add("invalid-field", where, "must be an object")
            return False
        missing = [key for key in keys if key not in obj]
        extra = sorted(set(obj) - set(keys))
        for key in missing:
            self.add("invalid-field", f"{where}.{key}", "is required")
        for key in extra:
            self.add("invalid-field", f"{where}.{key}", "is not a known key")
        return True

    def verdict_fields(self, obj, allowed, where):
        verdict = self.enum_field(obj, "verdict", allowed, where)
        target = self.str_field(obj, "verdict_target", where, allow_empty=True)
        if verdict in TARGETED_VERDICTS and target is not None and not target.strip():
            self.add("invalid-field", f"{where}.verdict_target", f"is required for verdict {verdict}")
        self.str_field(obj, "reason", where)
        return verdict

    def digest(self, value):
        if value not in self.digests:
            self.digests[value] = sha256(self.resolve(value))
        return self.digests[value]

    def line_count(self, path):
        if path not in self.line_counts:
            try:
                self.line_counts[path] = len(path.read_text(encoding="utf-8").splitlines())
            except (OSError, UnicodeDecodeError):
                self.line_counts[path] = None
        return self.line_counts[path]

    def resolve(self, value):
        path = Path(value)
        return path if path.is_absolute() else self.root / path

    def location(self, obj, key, where):
        """위치를 검사하고 읽을 수 있는 파일이면 그 경로 문자열을 돌려준다."""
        value = self.str_field(obj, key, where)
        if value is None:
            return None
        match = LOCATION.match(value)
        if not match:
            self.add("invalid-location", f"{where}.{key}", f"{value!r} is not <path>:<line>[-<line>]")
            return None
        path = self.resolve(match.group(1))
        start = int(match.group(2))
        end = int(match.group(3) or start)
        count = self.line_count(path) if path.is_file() else None
        if count is None:
            self.add("invalid-location", f"{where}.{key}", f"{match.group(1)} is not a readable file")
            return None
        if not 1 <= start <= end <= count:
            self.add("invalid-location", f"{where}.{key}", f"{value} is outside 1-{count}")
        return match.group(1)

    def sources(self, item, referenced, where):
        """항목 밖 파일을 가리키는 위치마다 기록한 sha256이 현재 파일과 같은지 검사한다."""
        if "sources" not in item:
            return  # object_keys가 이미 누락을 보고했다.
        value = item["sources"]
        if not isinstance(value, dict):
            self.add("invalid-field", f"{where}.sources", "must be an object of path to sha256")
            return
        for path in sorted(referenced - set(value)):
            self.add("invalid-field", f"{where}.sources", f"has no sha256 for location file {path}")
        for path in sorted(set(value) - referenced):
            self.add("invalid-field", f"{where}.sources.{path}", "is not a location file of this entry")
        for path in sorted(referenced & set(value)):
            recorded = value[path]
            if not isinstance(recorded, str):
                self.add("invalid-field", f"{where}.sources.{path}", "must be str")
            elif recorded != self.digest(path):
                self.add("stale", path, f"{where}.sources sha256 differs from the current file")

    def existing_tool(self, obj, where):
        value = obj.get("existing_tool")
        if value is None:
            return
        if not isinstance(value, str) or not value.strip() or value.strip() == "null":
            self.add("invalid-field", f"{where}.existing_tool", "must be null or a non-empty path")
        elif not self.resolve(value).exists():
            self.add("invalid-location", f"{where}.existing_tool", f"{value} does not exist")

    def overlap_target(self, value, where):
        prefix, separator, rest = value.partition(":") if isinstance(value, str) else ("", "", "")
        valid = bool(separator and rest.strip()) and (
            prefix == "external" or
            (prefix == "omp" and rest in OMP_FEATURES) or
            (prefix in self.catalog and (prefix, rest) in self.skill_names)
        )
        if not valid:
            self.add("invalid-target", where, f"{value!r} is not <plugin>:<skill>, omp:<feature> or external:<text>")

    def entries(self, items, expected, where, check):
        """항목 배열을 단위 목록과 대조하고 각 항목에 check를 적용한다."""
        seen = {}
        for index, item in enumerate(items):
            item_where = f"{where}[{index}]"
            path = item.get("path") if isinstance(item, dict) else None
            if isinstance(path, str) and path in seen:
                self.add("duplicate-entry", path, f"also recorded at {seen[path]}")
                continue
            if isinstance(path, str):
                seen[path] = item_where
                if path not in expected:
                    self.add("unknown-entry", path, f"{item_where} is not a current unit")
                    continue
            check(item, item_where, expected.get(path) if isinstance(path, str) else None)
        for path in expected:
            if path not in seen:
                self.add("missing-entry", path, f"no entry in {where}")
        return len(items)

    def own_digest(self, item, where, digest):
        """항목 경로를 검사하고, 경로가 유효하면 기록한 sha256을 현재 파일과 대조한다."""
        path = self.str_field(item, "path", where)
        recorded = self.str_field(item, "sha256", where)
        if path is not None and recorded is not None and recorded != digest:
            self.add("stale", path, "sha256 differs from the current file")
        return path

    def asset(self, item, where, digest, with_sha):
        keys = ["path", "role", "verdict", "verdict_target", "reason"] + (["sha256"] if with_sha else [])
        if not self.object_keys(item, keys, where):
            return
        if with_sha:
            self.own_digest(item, where, digest)
        else:
            self.str_field(item, "path", where)
        self.str_field(item, "role", where)
        self.verdict_fields(item, ASSET_VERDICT, where)

    def skill(self, item, where, digest):
        keys = ["path", "sha256", "sources", "problem", "outcome", "ai_judgment", "mechanical", "unique_value",
                "overlaps", "verdict", "verdict_target", "reason", "doc_findings", "example"]
        if not self.object_keys(item, keys, where):
            return None
        path = self.own_digest(item, where, digest)
        for key in ("problem", "outcome", "ai_judgment", "unique_value"):
            self.str_field(item, key, where)
        referenced = set()
        tool_proposals = 0
        for index, step in enumerate(self.list_field(item, "mechanical", where)):
            step_where = f"{where}.mechanical[{index}]"
            if not self.object_keys(step, ["step", "location", "existing_tool", "proposal"], step_where):
                continue
            self.str_field(step, "step", step_where)
            referenced.add(self.location(step, "location", step_where))
            self.existing_tool(step, step_where)
            tool_proposals += self.enum_field(step, "proposal", PROPOSAL, step_where) in {"script", "validator"}
        for index, overlap in enumerate(self.list_field(item, "overlaps", where)):
            overlap_where = f"{where}.overlaps[{index}]"
            if self.object_keys(overlap, ["target", "note"], overlap_where):
                self.overlap_target(overlap.get("target"), f"{overlap_where}.target")
                self.str_field(overlap, "note", overlap_where)
        for index, finding in enumerate(self.list_field(item, "doc_findings", where)):
            finding_where = f"{where}.doc_findings[{index}]"
            if self.object_keys(finding, ["kind", "location", "note"], finding_where):
                self.enum_field(finding, "kind", set(KIND), finding_where)
                referenced.add(self.location(finding, "location", finding_where))
                self.str_field(finding, "note", finding_where)
        self.sources(item, referenced - {None, path}, where)
        self.enum_field(item, "example", EXAMPLE, where)
        verdict = self.verdict_fields(item, VERDICT, where)
        if verdict == "new-tool" and not tool_proposals:
            self.add("invalid-field", f"{where}.verdict", "new-tool needs a script or validator proposal")
        return verdict

    def plugin(self, data, plugin, where):
        """플러그인 인벤토리 하나를 검사하고 기록된 항목 수를 돌려준다."""
        keys = ["schema_version", "plugin", "manifest_sha256", "problem", "outcome", "omp", "verdict",
                "verdict_target", "reason", "skills", "scripts"]
        if not self.object_keys(data, keys, where):
            return 0
        if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
            self.add("invalid-field", f"{where}.schema_version", "must be 1")
        if self.str_field(data, "plugin", where) is not None and data["plugin"] != plugin["name"]:
            self.add("invalid-field", f"{where}.plugin", f"must equal file stem {plugin['name']}")
        if (self.str_field(data, "manifest_sha256", where) is not None and
                data["manifest_sha256"] != plugin["manifest_sha256"]):
            self.add("stale", f"plugins/{plugin['name']}/.codex-plugin/plugin.json",
                     "manifest_sha256 differs from the current file")
        self.str_field(data, "problem", where)
        self.str_field(data, "outcome", where)
        omp = data.get("omp")
        if self.object_keys(omp, ["current", "proposal", "reason"], f"{where}.omp"):
            current = self.enum_field(omp, "current", OMP, f"{where}.omp")
            self.enum_field(omp, "proposal", OMP, f"{where}.omp")
            self.str_field(omp, "reason", f"{where}.omp")
            if current is not None and current != plugin["omp_current"]:
                self.add("omp-mismatch", f"{where}.omp.current",
                         f"recorded {current}, current state is {plugin['omp_current']}")
        verdict = self.verdict_fields(data, VERDICT, where)
        skill_verdicts = []
        count = 1
        count += self.entries(
            self.list_field(data, "skills", where),
            {skill["path"]: skill["sha256"] for skill in plugin["skills"]},
            f"{where}.skills",
            lambda item, item_where, digest: skill_verdicts.append(self.skill(item, item_where, digest)),
        )
        count += self.entries(
            self.list_field(data, "scripts", where),
            {script["path"]: script["sha256"] for script in plugin["scripts"]},
            f"{where}.scripts",
            lambda item, item_where, digest: self.asset(item, item_where, digest, True),
        )
        if verdict == "new-tool" and "new-tool" not in skill_verdicts:
            self.add("invalid-field", f"{where}.verdict", "new-tool needs at least one new-tool skill")
        return count

    def repository(self, data, where):
        if not self.object_keys(data, ["schema_version", "scripts", "shared", "evals"], where):
            return 0
        if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
            self.add("invalid-field", f"{where}.schema_version", "must be 1")
        units = self.units["repository"]
        count = self.entries(
            self.list_field(data, "scripts", where),
            {script["path"]: script["sha256"] for script in units["scripts"]},
            f"{where}.scripts",
            lambda item, item_where, digest: self.asset(item, item_where, digest, True),
        )
        count += self.entries(
            self.list_field(data, "shared", where),
            {path: None for path in units["shared"]},
            f"{where}.shared",
            lambda item, item_where, digest: self.asset(item, item_where, digest, False),
        )
        allowed = set(self.catalog) | {REPOSITORY}

        def eval_entry(item, item_where, _):
            if not self.object_keys(item, ["path", "covers", "role"], item_where):
                return
            self.str_field(item, "path", item_where)
            self.str_field(item, "role", item_where)
            covers = item.get("covers")
            if (not isinstance(covers, list) or not covers or
                    any(not isinstance(name, str) or name not in allowed for name in covers)):
                self.add("invalid-field", f"{item_where}.covers",
                         "must list one or more catalog plugin names or repository")

        count += self.entries(
            self.list_field(data, "evals", where),
            {path: None for path in units["evals"]},
            f"{where}.evals",
            eval_entry,
        )
        return count


# ---------------------------------------------------------------- 보고서


def cell(value):
    if value is None:
        return "-"
    return str(value).replace("|", "\\|").replace("\r\n", " ").replace("\n", " ")


def table(title, header, rows):
    lines = [f"### {title}", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(cell(value) for value in row) + " |" for row in rows]
    return "\n".join(lines)


def as_list(value):
    return value if isinstance(value, list) else []


def as_dict(value):
    return value if isinstance(value, dict) else {}


def by_path(items):
    return sorted((as_dict(item) for item in as_list(items)), key=lambda item: str(item.get("path", "")))


def render_report(catalog, inventories, repository):
    plugin_rows, other_rows, tool_rows, finding_rows = [], [], [], []
    for name in catalog:
        data = as_dict(inventories.get(name))
        if not data:
            continue
        skills = by_path(data.get("skills"))
        findings = [as_dict(finding) for skill in skills for finding in as_list(skill.get("doc_findings"))]
        omp = as_dict(data.get("omp"))
        plugin_rows.append([name, data.get("verdict", ""), data.get("verdict_target", ""), omp.get("current", ""),
                            omp.get("proposal", ""), len(skills), len(findings), data.get("reason", "")])
        for item in sorted(skills + by_path(data.get("scripts")), key=lambda item: str(item.get("path", ""))):
            if item.get("verdict") != "keep":
                other_rows.append([item.get("path", ""), item.get("verdict", ""), item.get("verdict_target", ""),
                                   item.get("reason", "")])
        for skill in skills:
            for step in (as_dict(step) for step in as_list(skill.get("mechanical"))):
                if step.get("proposal") in ("script", "validator"):
                    tool_rows.append([skill.get("path", ""), step.get("location", ""), step.get("step", ""),
                                      step.get("proposal"), step.get("existing_tool")])
        finding_rows.append([name] + [sum(finding.get("kind") == kind for finding in findings) for kind in KIND])
    repo = as_dict(repository)
    for item in sorted(by_path(repo.get("scripts")) + by_path(repo.get("shared")),
                       key=lambda item: str(item.get("path", ""))):
        if item.get("verdict") != "keep":
            other_rows.append([item.get("path", ""), item.get("verdict", ""), item.get("verdict_target", ""),
                               item.get("reason", "")])
    return "\n\n".join([
        table("플러그인 판정", ["플러그인", "판정", "대상", "omp 현재", "omp 제안", "스킬 수", "문서 지적 수", "근거"],
              plugin_rows),
        table("유지 외 판정", ["경로", "판정", "대상", "근거"], other_rows),
        table("도구 후보", ["스킬", "위치", "단계", "제안", "기존 도구"], tool_rows),
        table("문서 지적 집계", ["플러그인", *KIND], finding_rows),
    ]) + "\n"


def report_block(path):
    text = path.read_text(encoding="utf-8")
    if text.count(REPORT_START) != 1 or text.count(REPORT_END) != 1:
        return None
    start, end = text.index(REPORT_START), text.index(REPORT_END)
    if start > end:
        return None
    return text[start + len(REPORT_START):end].strip("\n")


# ---------------------------------------------------------------- 명령


def load_inventories(directory, catalog):
    """존재하는 인벤토리 파일을 읽는다. 구문 오류는 분석 미완료다."""
    inventories = {}
    for name in catalog + [REPOSITORY]:
        path = directory / f"{name}.json"
        if path.is_file():
            inventories[name] = read_json(path)
    return inventories


def command_scan(root, _args):
    units, _ = enumerate_units(root)
    print(json.dumps(units, ensure_ascii=False, indent=2))
    return 0


def command_report(root, args):
    units, _ = enumerate_units(root)
    catalog = [plugin["name"] for plugin in units["plugins"]]
    inventories = load_inventories(args.inventory, catalog)
    sys.stdout.write(render_report(catalog, inventories, inventories.get(REPOSITORY)))
    return 0


def command_check(root, args):
    units, uncatalogued = enumerate_units(root)
    catalog = [plugin["name"] for plugin in units["plugins"]]
    if args.plugin is not None and args.plugin not in catalog + [REPOSITORY]:
        raise AnalysisError(f"unknown plugin: {args.plugin}")
    checker = Checker(root, units)
    selected = catalog + [REPOSITORY] if args.plugin is None else [args.plugin]
    inventories = {}
    for name in selected:
        path = args.inventory / f"{name}.json"
        if path.is_file():
            inventories[name] = read_json(path)
    unit_count = entry_count = 0
    missing = []
    for plugin in units["plugins"]:
        if plugin["name"] not in selected:
            continue
        unit_count += 1 + len(plugin["skills"]) + len(plugin["scripts"])
        where = f"{plugin['name']}.json"
        if plugin["name"] not in inventories:
            # 아직 조사하지 않은 플러그인은 경고로 남기고 검사를 막지 않는다.
            missing.append(plugin["name"])
            continue
        entry_count += checker.plugin(inventories[plugin["name"]], plugin, where)
    if REPOSITORY in selected:
        repo = units["repository"]
        unit_count += len(repo["scripts"]) + len(repo["shared"]) + len(repo["evals"])
        if REPOSITORY not in inventories:
            checker.add("missing-entry", "repository.json", "inventory file does not exist")
        else:
            entry_count += checker.repository(inventories[REPOSITORY], "repository.json")
    warnings = [f"warning: missing-inventory {name}" for name in missing]
    if args.plugin is None:
        for name in uncatalogued:
            checker.add("uncatalogued-plugin", f"plugins/{name}", "has a Codex manifest but is not in the catalog")
        if args.inventory.is_dir():
            for path in sorted(args.inventory.glob("*.json")):
                if path.stem not in selected:
                    checker.add("unknown-entry", path.name, "is not a catalog plugin or repository")
        covered = {
            name
            for item in as_list(as_dict(inventories.get(REPOSITORY)).get("evals"))
            for name in as_list(as_dict(item).get("covers")) if isinstance(name, str)
        }
        warnings += [f"warning: uncovered-plugin {name}" for name in catalog if name not in covered]
        report = root / REPORT
        if report.is_file():
            expected = render_report(catalog, inventories, inventories.get(REPOSITORY)).rstrip("\n")
            block = report_block(report)
            if block is None:
                checker.add("stale-report", REPORT, "needs exactly one start marker before one end marker")
            elif block != expected:
                checker.add("stale-report", REPORT, "differs from validate_refactor_inventory.py report")
    for code, where, message in checker.violations:
        print(f"violation: {code} {where} {message}")
    for warning in warnings:
        print(warning)
    print(f"units: {unit_count}, entries: {entry_count}, violations: {len(checker.violations)}")
    return 1 if checker.violations else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("scan", "check", "report"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, default=ROOT)
        if name != "scan":
            command.add_argument("--inventory", type=Path, default=Path(DEFAULT_INVENTORY))
        if name == "check":
            command.add_argument("--plugin")
    args = parser.parse_args()
    root = args.root.resolve()
    if hasattr(args, "inventory"):
        args.inventory = args.inventory if args.inventory.is_absolute() else root / args.inventory
    handler = {"scan": command_scan, "check": command_check, "report": command_report}[args.command]
    try:
        return handler(root, args)
    except AnalysisError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
