#!/usr/bin/env python3
"""Render the omp catalog and plugin extension packages from Codex metadata."""

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z][a-z0-9-]*\Z")
OMP_EXCLUDED = {"memory-manager"}


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


def rendered_outputs(root):
    codex = read_json(root / ".agents/plugins/marketplace.json")
    entries = codex.get("plugins")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Codex marketplace has no plugins")
    continuity = set(read_json(root / "shared/task-continuity/profiles.json"))
    extension = (root / "shared/omp-runtime/extension.ts").read_bytes()

    outputs = {}
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
        if name in OMP_EXCLUDED:
            continue
        plugin_root = root / "plugins" / name
        if plugin_root.is_symlink() or not plugin_root.is_dir() or not plugin_root.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"{name}: plugin root is missing or escapes the repository")
        codex_manifest_path = plugin_root / ".codex-plugin/plugin.json"
        if codex_manifest_path.is_symlink() or not codex_manifest_path.resolve().is_relative_to(plugin_root.resolve()):
            raise ValueError(f"{name}: Codex manifest escapes plugin root")
        codex_manifest = read_json(codex_manifest_path)
        if codex_manifest.get("name") != name:
            raise ValueError(f"{name}: Codex manifest name differs")
        version = codex_manifest.get("version")
        if not isinstance(version, str) or not version:
            raise ValueError(f"{name}: missing plugin version")
        omp_entries.append({
            "name": name,
            "source": source_path,
            "description": codex_manifest.get("description", ""),
            "version": version,
            "category": entry.get("category", "Productivity"),
        })
        if name in continuity:
            outputs[plugin_root / "package.json"] = encode({
                "name": f"sonsu-marketplace-{name}",
                "version": version,
                "private": True,
                "type": "module",
                "omp": {"extensions": ["./omp/extension.ts"]},
            })
            outputs[plugin_root / "omp/extension.ts"] = extension
    outputs[root / ".omp-plugin/marketplace.json"] = encode({
        "name": codex["name"],
        "owner": {"name": "sonsu-lee", "url": "https://github.com/sonsu-lee"},
        "description": "omp에서 사용하는 Sonsu 플러그인 모음",
        "plugins": omp_entries,
    })
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale output without writing")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        outputs = rendered_outputs(root)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    managed = set(root.glob("plugins/*/package.json")) | set(root.glob("plugins/*/omp/extension.ts"))
    obsolete = sorted(managed - set(outputs))
    if obsolete and not args.check:
        for path in obsolete:
            if has_symlink_component(path, root):
                parser.error(f"generated path contains a symlink: {path}")
            path.unlink()
            print(f"removed: {path.relative_to(root)}")
        for directory in sorted(root.glob("plugins/*/omp")):
            if directory.is_dir() and not directory.is_symlink() and not any(directory.iterdir()):
                directory.rmdir()
    stale = []
    for path, data in outputs.items():
        if has_symlink_component(path, root) or not path.resolve().is_relative_to(root):
            parser.error(f"generated path escapes repository or contains a symlink: {path}")
        if path.is_file() and path.read_bytes() == data:
            continue
        stale.append(path.relative_to(root))
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    for path in stale:
        print(f"{'stale' if args.check else 'rendered'}: {path}")
    for path in obsolete:
        if args.check:
            print(f"obsolete: {path.relative_to(root)}")
    return int(args.check and bool(stale or obsolete))


if __name__ == "__main__":
    raise SystemExit(main())
