#!/usr/bin/env python3
"""Render Claude Code manifests from the canonical Codex marketplace metadata."""
import argparse
import json
from pathlib import Path, PurePosixPath


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
COMPAT_CONFIG = ".claude-plugin/compat.json"
COMPAT_FIELDS = {"schema_version", "include", "skill_frontmatter"}
SKILL_FRONTMATTER_FIELDS = {"disable-model-invocation"}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def load_json(path):
    return json.loads(path.read_text())


def load_compat_config(plugin_root):
    path = plugin_root / COMPAT_CONFIG
    if not path.is_file():
        return None
    config = load_json(path)
    if not isinstance(config, dict):
        raise ValueError(f"{plugin_root.name}: Claude compatibility config must be an object")
    unknown = set(config) - COMPAT_FIELDS
    if unknown:
        raise ValueError(
            f"{plugin_root.name}: unsupported Claude compatibility fields: "
            + ", ".join(sorted(unknown))
        )
    if config.get("schema_version") != 1:
        raise ValueError(f"{plugin_root.name}: Claude compatibility schema_version must be 1")

    includes = config.get("include", [])
    if not isinstance(includes, list) or not all(
        isinstance(value, str) and value for value in includes
    ):
        raise ValueError(f"{plugin_root.name}: Claude compatibility include must be a string array")
    for value in includes:
        path_value = PurePosixPath(value)
        if (
            path_value.is_absolute()
            or len(path_value.parts) != 1
            or path_value.parts[0] in (".", "..", "skills")
        ):
            raise ValueError(f"{plugin_root.name}: invalid Claude compatibility include: {value}")

    skill_frontmatter = config.get("skill_frontmatter", {})
    if not isinstance(skill_frontmatter, dict):
        raise ValueError(
            f"{plugin_root.name}: Claude compatibility skill_frontmatter must be an object"
        )
    for skill_name, overrides in skill_frontmatter.items():
        if (
            not isinstance(skill_name, str)
            or not skill_name
            or "/" in skill_name
            or "\\" in skill_name
            or skill_name in (".", "..")
            or not isinstance(overrides, dict)
        ):
            raise ValueError(f"{plugin_root.name}: invalid Claude skill override")
        unknown_overrides = set(overrides) - SKILL_FRONTMATTER_FIELDS
        if unknown_overrides:
            raise ValueError(
                f"{plugin_root.name}/{skill_name}: unsupported Claude skill fields: "
                + ", ".join(sorted(unknown_overrides))
            )
        if not all(isinstance(value, bool) for value in overrides.values()):
            raise ValueError(
                f"{plugin_root.name}/{skill_name}: Claude skill overrides must be booleans"
            )
    return config


def render_skill(source, overrides):
    text = source.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{source}: skill frontmatter is missing")
    frontmatter_end = text.find("\n---", 4)
    if frontmatter_end == -1:
        raise ValueError(f"{source}: skill frontmatter is not closed")
    frontmatter = text[4:frontmatter_end]
    for field in overrides:
        if any(line.split(":", 1)[0].strip() == field for line in frontmatter.splitlines()):
            raise ValueError(f"{source}: Claude override duplicates canonical field {field}")
    rendered = "".join(
        f"\n{field}: {str(value).lower()}"
        for field, value in sorted(overrides.items())
    )
    return (text[:frontmatter_end] + rendered + text[frontmatter_end:]).encode()


def projected_outputs(plugin_root, output_root, config):
    source_paths = [plugin_root / "skills"] + [
        plugin_root / value for value in config.get("include", [])
    ]
    overrides_by_skill = config.get("skill_frontmatter", {})
    observed_skills = set()
    for source_path in source_paths:
        if source_path.is_symlink():
            raise ValueError(
                f"{plugin_root.name}: Claude projection source cannot be a symlink: "
                f"{source_path.relative_to(plugin_root)}"
            )
        if source_path.is_file():
            sources = [source_path]
        elif source_path.is_dir():
            sources = sorted(source_path.rglob("*"))
        else:
            raise ValueError(
                f"{plugin_root.name}: Claude projection source is missing: "
                f"{source_path.relative_to(plugin_root)}"
            )
        for source in sources:
            if source.is_symlink():
                raise ValueError(
                    f"{plugin_root.name}: Claude projection source cannot be a symlink: "
                    f"{source.relative_to(plugin_root)}"
                )
            if not source.is_file():
                continue
            relative = source.relative_to(plugin_root)
            data = source.read_bytes()
            if (
                len(relative.parts) == 3
                and relative.parts[0] == "skills"
                and relative.name == "SKILL.md"
            ):
                skill_name = relative.parts[1]
                observed_skills.add(skill_name)
                overrides = overrides_by_skill.get(skill_name, {})
                if overrides:
                    data = render_skill(source, overrides)
            yield output_root / relative, data

    missing = set(overrides_by_skill) - observed_skills
    if missing:
        raise ValueError(
            f"{plugin_root.name}: Claude skill override target is missing: "
            + ", ".join(sorted(missing))
        )


def extra_projection_files(root, rendered):
    expected = {target for target, _ in rendered}
    projection_roots = {
        root / relative.parts[0] / relative.parts[1]
        for target in expected
        for relative in [target.relative_to(root)]
        if len(relative.parts) >= 2 and relative.parts[0] == ".claude-plugins"
    }
    extras = []
    for projection_root in sorted(projection_roots):
        if projection_root.is_symlink():
            raise ValueError(
                f"Claude projection root cannot be a symlink: "
                f"{projection_root.relative_to(root)}"
            )
        if not projection_root.exists():
            continue
        for candidate in sorted(projection_root.rglob("*")):
            if (candidate.is_file() or candidate.is_symlink()) and candidate not in expected:
                extras.append(candidate)
    return projection_roots, extras


def remove_empty_projection_directories(projection_roots):
    for projection_root in projection_roots:
        directories = [
            path
            for path in projection_root.rglob("*")
            if path.is_dir() and not path.is_symlink()
        ]
        for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass


def claude_manifest(codex_manifest):
    manifest = {
        "$schema": PLUGIN_SCHEMA,
        "name": codex_manifest["name"],
    }
    display_name = codex_manifest.get("interface", {}).get("displayName")
    if display_name:
        manifest["displayName"] = display_name
    for field in CLAUDE_FIELDS:
        if field in codex_manifest:
            manifest[field] = codex_manifest[field]
    return manifest


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

        manifest = claude_manifest(codex_manifest)
        compat_config = load_compat_config(plugin_root)
        if compat_config is None:
            claude_source_path = source_path
            yield plugin_root / ".claude-plugin/plugin.json", encode(manifest)
        else:
            claude_source_path = f"./.claude-plugins/{entry_name}"
            output_root = root / claude_source_path.removeprefix("./")
            yield output_root / ".claude-plugin/plugin.json", encode(manifest)
            yield from projected_outputs(plugin_root, output_root, compat_config)

        claude_entry = {
            "name": entry["name"],
            "source": claude_source_path,
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

    changed = []
    removed = []
    try:
        rendered = list(outputs(root))
        for target, _ in rendered:
            if not target.resolve().is_relative_to(root):
                raise ValueError(f"output path resolves outside repository: {target}")
        projection_roots, extras = extra_projection_files(root, rendered)
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    for target, data in rendered:
        if target.exists() and target.read_bytes() == data:
            continue
        changed.append(str(target.relative_to(root)))
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    for target in extras:
        removed.append(str(target.relative_to(root)))
        if not args.check:
            target.unlink()
    if not args.check:
        remove_empty_projection_directories(projection_roots)

    for target in changed:
        print(("stale: " if args.check else "rendered: ") + target)
    for target in removed:
        print(("stale: " if args.check else "removed: ") + target)
    return int(args.check and bool(changed or removed))


if __name__ == "__main__":
    raise SystemExit(main())
