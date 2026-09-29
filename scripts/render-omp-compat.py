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
OMP_PLUGINS = {"workflow", "fluent-korean", "fluent-english", "fluent-japanese", "design"}
ISOLATED = {"workflow", "design"}
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


def isolated_outputs(root, plugin_root, manifest, outputs, modes):
    destination = plugin_root / "omp"
    sources = []
    for name in COPY_ROOTS:
        directory = plugin_root / name
        require_safe(directory, root)
        if directory.is_dir():
            sources.extend(package_files(directory, root))
    sources.extend(path for path in sorted(plugin_root.iterdir())
                   if path.name == ".app.json" or
                   path.name.startswith(("LICENSE", "NOTICE", "UPSTREAM")) or
                   "LICENSE" in path.name)
    for source in sources:
        relative = source.relative_to(plugin_root)
        if relative.as_posix() in SKIP_FILES:
            continue
        require_safe(source, root)
        outputs[destination / relative] = source.read_bytes()
        modes[destination / relative] = stat.S_IMODE(source.stat().st_mode)
    for name in ("continuity.md", "migration.md"):
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
