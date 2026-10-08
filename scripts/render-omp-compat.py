#!/usr/bin/env python3
"""Codex のメタデータから omp 専用のカタログと独立パッケージを生成する。"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z][a-z0-9-]*\Z")
OMP_PLUGINS = {"workflow", "fluent-korean", "fluent-english", "fluent-japanese", "design", "career"}
ISOLATED = {"workflow", "design", "fluent-korean"}
MANIFEST_FIELDS = ("version", "description", "author", "homepage", "repository", "license", "keywords")
COPY_ROOTS = ("skills", "references", "assets", "scripts", "figma-plugin")
SKIP_PARTS = {"__pycache__", "node_modules", ".git"}
SKIP_FILES = {"scripts/task-continuity.py", "scripts/evidence-gates.py"}
INVENTORY = ".omp-plugin/generated.json"
GENERATOR = "scripts/render-omp-compat.py"
LEGACY_EXTENSION_SHA256 = "4cb66672a03fa27b6a67f7b4562e70f2c7f04d96fb3b9c23b22b88a5e1e092b2"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def has_symlink_component(path, root):
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def require_safe(path, root):
    if has_symlink_component(path, root) or not path.resolve().is_relative_to(root):
        raise ValueError(f"path escapes repository or contains a symlink: {path}")
    if path.exists() and not (path.is_file() or path.is_dir()):
        raise ValueError(f"unsupported file type: {path}")
    for parent in path.parents:
        if parent == root:
            break
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"parent is not a directory: {parent}")


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def owned_package(package):
    """旧生成器の完全な manifest だけを削除対象とする。"""
    try:
        data = read_json(package)
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and isinstance(data.get("version"), str) and data == {
        "name": f"sonsu-marketplace-{package.parent.name}",
        "version": data["version"], "private": True, "type": "module",
        "omp": {"extensions": ["./omp/extension.ts"]},
    }


def package_files(directory, root):
    require_safe(directory, root)
    for path in sorted(directory.iterdir()):
        if path.name in SKIP_PARTS or path.suffix == ".pyc":
            continue
        require_safe(path, root)
        if path.is_dir():
            yield from package_files(path, root)
        else:
            yield path


def omp_korean_skill(data):
    """Codex 단일 호출 경로의 품질 규칙은 유지하고 호스트 안내만 투영한다."""
    text = data.decode("utf-8")
    text = text.replace("# Fluent Korean — im-not-ai 기반 (Codex · GitHub Copilot CLI)",
                        "# Fluent Korean — im-not-ai 기반 (OMP)")
    text = text.replace("Codex와 GitHub Copilot CLI는 단일 호출 경로만 제공한다. 진단→겨냥 윤문→finalize로 이어지는 다중 호출 경로는 Claude Code 전용이다.",
                        "OMP는 현재 호스트 모델로 단일 호출 경로를 실행한다. 별도 task agent나 모델 고정을 요구하지 않는다. Claude Code의 다중 호출·strict 모드는 OMP에서는 제공하지 않는다.")
    text = text.replace('④ 등급 B 이하면 "정밀 검증은 Claude Code의 정밀 모드(3콜) 권장" 안내.',
                        '④ 등급 B 이하면 자체검증의 한계와 남은 문제를 안내한다. Claude Code의 정밀·strict 모드는 OMP에서는 제공하지 않는다.')
    text = text.replace("— Claude Code strict 모드 권고.",
                        "— 남은 문제와 자체검증 한계를 보고한다. Claude Code strict 모드는 OMP에서는 제공하지 않는다.")
    text = text.replace("변경률 30% 초과 = 경고, 50% 초과 = 작업 중단·롤백.",
                        "변경률 30% 이상 = 경고, 50% 이상 = 작업 중단·롤백. 확정 판정은 아래 결정적 검증기의 종료 코드에 따른다.")
    text = text.replace("2. **입력 확보**: ",
                        "2. **입력 확보**: 먼저 run_id를 `YYYY-MM-DD-NNN-TAG`로 만든다. 당일 기존 폴더가 있으면 NNN을 늘리고, TAG는 `python3 -c \"import secrets;print(secrets.token_hex(2))\"`로 한 번 생성해 재사용한다. `_workspace/{run_id}/01_input.txt`에 원문을 그대로 보존한 뒤 윤문을 시작한다. ")
    start = text.index("7. **출력**:")
    end = text.index("본문 끝에", start)
    text = (text[:start] + "7. **출력**: 입력 확보 때 만든 run_id를 사용해 cwd 기준 `_workspace/{run_id}/final.md`에 후보 윤문본을 작성한다. " + text[end:])
    verification = """8. **결정적 검증**: 출력 후 [변경률 검증기](../../scripts/verify_change_rate.py)를 실행한다. 현재 호스트의 `realpath skill://fluent-korean` 결과는 실제 SKILL.md 디렉터리다. 그 물리적 경로에서 `../../scripts/verify_change_rate.py`를 해석한 절대 경로를 `VALIDATOR`로 사용한다. `skill://` URL에 상위 경로를 붙이지 않는다. 생성한 run_id와 원문·후보 파일 경로를 사용해 다음 명령을 호출한다.

   ```sh
   python3 "$VALIDATOR" --before "_workspace/${run_id}/01_input.txt" --after "_workspace/${run_id}/final.md"
   ```

   - exit 0: 변경률 30% 미만. 변경률 검증 통과이며 나머지 의미·보호 규칙 자체검증도 확인한다.
   - exit 1: 변경률 30% 이상 50% 미만. 실제 측정값과 과윤문 경고를 사용자에게 고지한다.
   - exit 2: 변경률 50% 이상. 윤문본 채택 금지·롤백. 원문을 보존하며 완료본으로 반환하지 않는다.
   - exit 3: 실행 오류. 검증 미확인으로 기록하고 완료로 보고하지 않는다. 스크립트 실행 불가나 종료 코드를 얻지 못한 경우도 같게 처리한다.

   검증기 stdout의 실제 측정값을 요약에 반영하며 자가 계산을 확정 변경률로 쓰지 않는다. 이 도구는 문장 보존을 위한 도메인 검증기이며 Engineering evidence gate나 task/session 실행기를 요구하지 않는다.
9. **응답**:"""
    text = text.replace("8. **응답**:", verification)
    text = text.replace("① 한 줄 상태(`완료. 변경률 X% / 등급 Y / 자체검증 N/6 통과`)",
                        "① 종료 코드에 맞는 한 줄 상태(`검증 통과` 또는 `과윤문 경고`와 실제 변경률·등급·자체검증 결과). exit 2·3이면 채택 중단·미검증 상태와 복구 조치만 보고하고 완료로 보고하지 않는다.")
    text = text.replace("\n---\n", "\n---\n\n<!-- Generated by scripts/render-omp-compat.py from the Codex single-call skill. -->\n", 1)
    return text.encode("utf-8")


def omp_korean_quick_rules(data):
    """패턴·보호 규칙은 유지하며 Claude 실행 안내만 OMP 단일 호출로 바꾼다."""
    text = data.decode("utf-8")
    text = text.replace("Monolith Fast Path 전용", "OMP 단일 호출")
    text = text.replace("`humanize-monolith` 에이전트가 한 콜에서", "OMP 현재 호스트 모델이 단일 호출에서")
    text = text.replace("(monolith 윤문 후 자가 점검)", "(OMP 단일 호출 후 자가 점검)")
    text = text.replace("변경률 30% 초과 = 경고, 50% 초과 = 강제 중단·롤백.",
                        "변경률 30% 이상 = 경고, 50% 이상 = 강제 중단·롤백.")
    text = text.replace("`scripts/verify_change_rate.py`가 한다(오케스트레이터 Phase 2.5).",
                        "[변경률 검증기](../../../scripts/verify_change_rate.py)가 한다. 물리적 설치 경로를 사용하며 실행·종료 코드 처리는 SKILL.md의 단일 호출 절차를 따른다.")
    text = text.replace("30% 이하인가. 확정 판정은 오케스트레이터 Phase 2.5(`verify_change_rate.py`)",
                        "30% 미만인가. 확정 판정은 [변경률 검증기](../../../scripts/verify_change_rate.py)")
    text = text.replace("— 사용자에게 strict 모드 권고", "— 남은 문제와 자체검증 한계를 사용자에게 보고")
    text = text.replace("변경률 50% 초과 — 작업 중단 권고", "변경률 50% 이상 — 윤문본 채택 금지·롤백")
    return text.encode("utf-8")


def isolated_outputs(root, plugin_root, manifest, outputs, modes):
    destination = plugin_root / "omp"
    sources = []
    for name in (("codex/skills",) if manifest["name"] == "fluent-korean" else COPY_ROOTS):
        directory = plugin_root / name
        require_safe(directory, root)
        if directory.is_dir():
            sources.extend(package_files(directory, root))
    if manifest["name"] == "fluent-korean":
        sources.extend(plugin_root / "scripts" / name for name in ("verify_change_rate.py", "console.py"))
    sources.extend(path for path in sorted(plugin_root.iterdir())
                   if path.name in (".app.json", "THIRD_PARTY_NOTICES.md") or
                   path.name.startswith(("LICENSE", "NOTICE", "UPSTREAM")) or
                   "LICENSE" in path.name)
    for source in sources:
        relative = source.relative_to(plugin_root)
        if relative.as_posix() in SKIP_FILES:
            continue
        require_safe(source, root)
        data = source.read_bytes()
        if manifest["name"] == "fluent-korean" and relative.parts[0] == "codex":
            relative = Path(*relative.parts[1:])
            if relative == Path("skills/fluent-korean/SKILL.md"):
                data = omp_korean_skill(data)
            elif relative.name in ("quick-rules.md", "quick-rules.header.md", "quick-rules.footer.md"):
                data = omp_korean_quick_rules(data)
        if manifest["name"] == "fluent-korean" and relative == Path("UPSTREAM.md"):
            text = data.decode("utf-8").rsplit("\n\n", 1)[0]
            data = (text + "\n\nFor omp, scripts/render-omp-compat.py projects the Codex single-call skill and its references into an independent package. Only host guidance in the skill and quick-rules files is adapted; language patterns and preservation rules remain intact. The existing verify_change_rate.py and console.py domain validator scripts are copied without modification, with their metrics dependencies from the Codex references. The package uses the current host model and provides no Claude multistep or strict execution path.\n").encode("utf-8")
        outputs[destination / relative] = data
        modes[destination / relative] = stat.S_IMODE(source.stat().st_mode)
    for name in (() if manifest["name"] == "fluent-korean" else ("continuity.md", "migration.md")):
        if name == "migration.md" and manifest["name"] != "design":
            continue
        source = root / "shared/omp-runtime" / name
        require_safe(source, root)
        outputs[destination / "references" / name] = source.read_bytes()
        modes[destination / "references" / name] = 0o644
    native_manifest = {"name": manifest["name"]}
    for field in MANIFEST_FIELDS:
        if field in manifest:
            native_manifest[field] = manifest[field]
    outputs[destination / ".claude-plugin/plugin.json"] = encode(native_manifest)


def rendered_outputs(root):
    require_safe(root / ".agents/plugins/marketplace.json", root)
    codex = read_json(root / ".agents/plugins/marketplace.json")
    entries = codex.get("plugins")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Codex marketplace has no plugins")

    outputs = {}
    modes = {}
    omp_entries = []
    names = set()
    for entry in entries:
        name = entry.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name) or name in names:
            raise ValueError(f"invalid or duplicate plugin name: {name!r}")
        names.add(name)
        source_path = f"./plugins/{name}"
        if entry.get("source") != {"source": "local", "path": source_path}:
            raise ValueError(f"{name}: invalid local plugin path")
        if name not in OMP_PLUGINS:
            continue
        plugin_root = root / "plugins" / name
        require_safe(plugin_root, root)
        if not plugin_root.is_dir():
            raise ValueError(f"{name}: plugin root is missing")
        codex_manifest_path = plugin_root / ".codex-plugin/plugin.json"
        require_safe(codex_manifest_path, root)
        codex_manifest = read_json(codex_manifest_path)
        if codex_manifest.get("name") != name:
            raise ValueError(f"{name}: Codex manifest name differs")
        version = codex_manifest.get("version")
        if not isinstance(version, str) or not version:
            raise ValueError(f"{name}: missing plugin version")
        omp_entries.append({
            "name": name,
            "source": source_path + ("/omp" if name in ISOLATED else ""),
            "description": codex_manifest.get("description", ""),
            "version": version,
            "category": entry.get("category", "Productivity"),
        })
        if name in ISOLATED:
            isolated_outputs(root, plugin_root, codex_manifest, outputs, modes)
    if not OMP_PLUGINS.issubset(names):
        raise ValueError("missing omp plugins: " + ", ".join(sorted(OMP_PLUGINS - names)))
    outputs[root / ".omp-plugin/marketplace.json"] = encode({
        "name": codex["name"],
        "owner": {"name": "sonsu-lee", "url": "https://github.com/sonsu-lee"},
        "description": "omp 用の Sonsu プラグイン",
        "plugins": omp_entries,
    })
    for path in outputs:
        modes.setdefault(path, 0o644)
    return outputs, modes


def previous_outputs(root):
    path = root / INVENTORY
    require_safe(path, root)
    if not path.exists():
        return {}
    data = read_json(path)
    if not isinstance(data, dict) or data.get("generator") != GENERATOR or not isinstance(data.get("files"), dict):
        raise ValueError(f"unmanaged inventory: {path}")
    previous = {}
    for relative, digest in data["files"].items():
        target = root / relative
        parts = Path(relative).parts
        if (len(parts) < 4 or parts[0] != "plugins" or parts[1] not in ISOLATED or
                parts[2] != "omp" or ".." in parts or Path(relative).is_absolute() or
                not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest)):
            raise ValueError(f"invalid owned path: {relative}")
        require_safe(target, root)
        previous[target] = digest
    return previous


def obsolete_extensions(root):
    obsolete = set()
    for package in sorted(root.glob("plugins/*/package.json")):
        require_safe(package, root)
        if not owned_package(package):
            continue
        extension = package.parent / "omp/extension.ts"
        require_safe(extension, root)
        if extension.exists() and fingerprint(extension.read_bytes()) != LEGACY_EXTENSION_SHA256:
            raise ValueError(f"modified legacy extension: {extension}")
        obsolete.add(package)
        if extension.exists():
            obsolete.add(extension)
    return obsolete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale output without writing")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        outputs, modes = rendered_outputs(root)
        previous = previous_outputs(root)
        obsolete = obsolete_extensions(root)
        for path, digest in previous.items():
            if path.exists() and fingerprint(path.read_bytes()) != digest:
                raise ValueError(f"modified generated file: {path}")
        obsolete.update(path for path in previous if path not in outputs and path.exists())
        for name in sorted(ISOLATED):
            for relative in ("hooks", "package.json", "extension.ts", "omp",
                             "scripts/task-continuity.py", "scripts/evidence-gates.py"):
                path = root / "plugins" / name / "omp" / relative
                require_safe(path, root)
                if path.exists() and path not in obsolete:
                    raise ValueError(f"unmanaged runtime in isolated package: {path}")
        catalog = root / ".omp-plugin/marketplace.json"
        for path in outputs:
            require_safe(path, root)
            if path.exists() and path not in previous and path != catalog:
                raise ValueError(f"unmanaged file at generated path: {path}")
        inventory = root / INVENTORY
        outputs[inventory] = encode({
            "generator": GENERATOR,
            "files": {path.relative_to(root).as_posix(): fingerprint(data)
                      for path, data in sorted(outputs.items()) if path != catalog},
        })
        modes[inventory] = 0o644
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.error(str(error))

    for path in sorted(obsolete):
        if not args.check:
            path.unlink()
            print(f"removed: {path.relative_to(root)}")
    stale = []
    for path, data in outputs.items():
        if (path.is_file() and path.read_bytes() == data and
                stat.S_IMODE(path.stat().st_mode) == modes[path]):
            continue
        stale.append(path.relative_to(root))
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(modes[path])
    for path in stale:
        print(f"{'stale' if args.check else 'rendered'}: {path}")
    for path in sorted(obsolete):
        if args.check:
            print(f"obsolete: {path.relative_to(root)}")
    return int(args.check and bool(stale or obsolete))


if __name__ == "__main__":
    raise SystemExit(main())
