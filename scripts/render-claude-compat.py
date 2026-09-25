#!/usr/bin/env python3
"""Render Claude Code catalog and plugin manifests from Codex metadata."""

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z][a-z0-9-]*\Z")
PLUGIN_SCHEMA = "https://json.schemastore.org/claude-code-plugin-manifest.json"
MANIFEST_FIELDS = ("version", "description", "author", "homepage", "repository", "license", "keywords")
CLAUDE_PACKAGE_OVERRIDES = {"memory-manager": "memory-manager-claude"}


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

    outputs = {}
    claude_entries = []
    names = set()
    for entry in entries:
        name = entry.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name) or name in names:
            raise ValueError(f"invalid or duplicate plugin name: {name!r}")
        names.add(name)
        source = entry.get("source")
        codex_source_path = f"./plugins/{name}"
        if source != {"source": "local", "path": codex_source_path}:
            raise ValueError(f"{name}: invalid local plugin path")
        plugin_root = root / "plugins" / name
        claude_root = root / "plugins" / CLAUDE_PACKAGE_OVERRIDES.get(name, name)
        source_path = f"./plugins/{claude_root.name}"
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
        manifest = {"$schema": PLUGIN_SCHEMA, "name": name}
        display_name = codex_manifest.get("interface", {}).get("displayName")
        if display_name:
            manifest["displayName"] = display_name
        for field in MANIFEST_FIELDS:
            if field in codex_manifest:
                manifest[field] = codex_manifest[field]
        outputs[claude_root / ".claude-plugin/plugin.json"] = encode(manifest)
        if name == "memory-manager":
            skill_root = plugin_root / "skills" / name
            skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            frontmatter_end = skill.find("\n---\n", 4)
            if not skill.startswith("---\n") or frontmatter_end == -1 or "disable-model-invocation" in skill[4:frontmatter_end]:
                raise ValueError("memory-manager: invalid Codex skill frontmatter")
            claude_skill_root = claude_root / "skills" / name
            outputs[claude_skill_root / "SKILL.md"] = (skill[:frontmatter_end] + "\ndisable-model-invocation: true" + skill[frontmatter_end:]).encode("utf-8")
            for reference in sorted((skill_root / "references").glob("*.md")):
                outputs[claude_skill_root / "references" / reference.name] = reference.read_bytes()
        claude_entries.append({
            "name": name,
            "source": source_path,
            "description": codex_manifest.get("description", ""),
            "version": version,
            "category": entry.get("category", "Productivity"),
        })
    outputs[root / ".claude-plugin/marketplace.json"] = encode({
        "name": codex["name"],
        "owner": {"name": "sonsu-lee", "url": "https://github.com/sonsu-lee"},
        "description": "Codex와 Claude Code에서 사용하는 Sonsu 플러그인 모음",
        "plugins": claude_entries,
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

    stale = []
    unexpected = set(root.glob("plugins/*/.claude-plugin/plugin.json")) - set(outputs)
    if unexpected:
        parser.error("unexpected Claude manifests: " + ", ".join(str(path.relative_to(root)) for path in sorted(unexpected)))
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
    return int(args.check and bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
