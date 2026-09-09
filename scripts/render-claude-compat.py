#!/usr/bin/env python3
"""Render Claude Code manifests from the canonical Codex marketplace metadata."""
import argparse
import json
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SCHEMA = "https://json.schemastore.org/claude-code-plugin-manifest.json"
MARKETPLACE_OWNER = {
    "name": "sonsu-lee",
    "url": "https://github.com/sonsu-lee",
}
MARKETPLACE_DESCRIPTION = (
    "Codex와 Claude Code에서 사용하는 재사용 가능한 에이전트 플러그인 모음입니다."
)
CLAUDE_FIELDS = (
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "commands",
    "agents",
    "mcpServers",
    "outputStyles",
    "lspServers",
    "experimental",
    "dependencies",
    "userConfig",
    "channels",
)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def load_json(path):
    return json.loads(path.read_text())


def outputs(root):
    codex_marketplace = load_json(root / ".agents/plugins/marketplace.json")
    claude_plugins = []

    for entry in codex_marketplace["plugins"]:
        entry_name = entry.get("name")
        source = entry.get("source")
        if not isinstance(source, dict) or source.get("source") != "local":
            raise ValueError(f"{entry_name or '<unknown>'}: expected a local plugin source")
        source_path = source.get("path")
        if (not isinstance(entry_name, str) or entry_name in ("", ".", "..")
                or "/" in entry_name or "\\" in entry_name
                or source_path != f"./plugins/{entry_name}"):
            raise ValueError(f"{entry_name or '<unknown>'}: invalid local plugin path")

        plugin_root = (root / source_path.removeprefix("./")).resolve()
        if not plugin_root.is_relative_to(root / "plugins"):
            raise ValueError(f"{entry_name}: plugin path resolves outside plugins directory")
        codex_manifest = load_json(plugin_root / ".codex-plugin/plugin.json")
        if codex_manifest.get("name") != entry_name:
            raise ValueError(f"{entry_name}: marketplace and manifest names differ")

        claude_manifest = {
            "$schema": PLUGIN_SCHEMA,
            "name": codex_manifest["name"],
        }
        display_name = codex_manifest.get("interface", {}).get("displayName")
        if display_name:
            claude_manifest["displayName"] = display_name
        for field in CLAUDE_FIELDS:
            if field in codex_manifest:
                claude_manifest[field] = codex_manifest[field]

        yield plugin_root / ".claude-plugin/plugin.json", encode(claude_manifest)

        claude_entry = {
            "name": entry["name"],
            "source": source_path,
        }
        for field in ("description", "version"):
            if field in codex_manifest:
                claude_entry[field] = codex_manifest[field]
        if "category" in entry:
            claude_entry["category"] = entry["category"]
        claude_plugins.append(claude_entry)

    claude_marketplace = {
        "name": codex_marketplace["name"],
        "owner": MARKETPLACE_OWNER,
        "description": MARKETPLACE_DESCRIPTION,
        "plugins": claude_plugins,
    }
    yield root / ".claude-plugin/marketplace.json", encode(claude_marketplace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true", help="report stale outputs without writing")
    args = parser.parse_args()
    root = args.root.resolve()

    stale = []
    try:
        rendered = list(outputs(root))
        for target, _ in rendered:
            if not target.resolve().is_relative_to(root):
                raise ValueError(f"output path resolves outside repository: {target}")
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    for target, data in rendered:
        if target.exists() and target.read_bytes() == data:
            continue
        stale.append(str(target.relative_to(root)))
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    for target in stale:
        print(("stale: " if args.check else "rendered: ") + target)
    return int(args.check and bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
