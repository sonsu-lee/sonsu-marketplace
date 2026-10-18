# sonsu-marketplace

Personal plugin marketplace for [omp](https://github.com/can1357/oh-my-pi).

omp reads the catalog at `.omp-plugin/marketplace.json` and installs plugins
from the `plugins/` directory.

## Install

Add the marketplace:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

List its plugins and install one:

```sh
omp plugin discover sonsu-marketplace
omp plugin install <plugin>@sonsu-marketplace
```

Add `--scope project` to install a plugin for the current project only. In an
omp session, `/marketplace` opens the same catalog in the plugin browser.

Fetch catalog changes, then upgrade installed plugins:

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

## Layout

```text
.omp-plugin/
  marketplace.json            # catalog: name, owner, plugins[]
plugins/
  <name>/
    plugin.json               # Agent Plugins manifest (required)
    skills/<skill>/SKILL.md   # Agent Plugins: skills
    mcp.json                  # Agent Plugins: MCP servers
    commands/<command>.md     # omp: slash commands, run as /<name>:<command>
    agents/<agent>.md         # omp: task subagents
    rules/<rule>.md           # omp: rules
    package.json              # omp: extension modules under "omp.extensions"
```

Each plugin is an [Agent Plugins](https://agent-plugins.org/) 1.0.0 package.
Skills and MCP servers follow the standard. omp-specific components sit next to
them in omp's conventional locations, and omp loads both from the same plugin.
omp does not read the standard's `extensions` field or namespaced extension
directories yet, so omp-specific components use these locations for now.
Everything except `plugin.json` is optional. The reasons for this format are in
[docs/decisions/0002-plugin-format.md](docs/decisions/0002-plugin-format.md).

## Adding a plugin

1.  Create `plugins/<name>/plugin.json`:

    ```json
    {
      "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
      "name": "<name>"
    }
    ```

    Use only the fields the standard defines: `$schema`, `name`, `version`,
    `description`, `author`, `homepage`, `repository`, `license`, `keywords`,
    and `extensions`. omp rejects the whole plugin if a defined field is
    invalid, for example an uppercase `name`.

1.  Add the standard components:

    *   **Skills**: `skills/<skill>/SKILL.md` following the
        [Agent Skills specification](https://agentskills.io/specification).
        The frontmatter may contain only `name`, `description`, `license`,
        `compatibility`, `metadata`, and `allowed-tools`, and `name` must match
        the directory name. omp skips a skill with any other field, such as
        omp's `hide` or Claude Code's `argument-hint`.
    *   **MCP servers**: `mcp.json` with the
        `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json` `$schema`
        and an `mcpServers` object. Each server sets `type` (`stdio`,
        `streamable-http`, or `sse`). A `stdio` `command` is a bare executable
        name or a `./` path. Use `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in
        `args`, `env`, and `cwd`; omp expands nothing else. Keep secrets out of
        `mcp.json`. A `stdio` server receives omp's environment and can read
        credentials from it.

    Do not add `.mcp.json` or `.claude-plugin/plugin.json`. omp loads the
    skills and MCP servers of a standard plugin only from `skills/` and
    `mcp.json`.

1.  Add omp-specific components:

    *   **Commands**: `commands/<command>.md` with a `description`. Use a
        command for a workflow that runs only when the user asks for it,
        since a standard skill cannot set `hide`.
    *   **Agents**: `agents/<agent>.md` with `name` and `description`.
    *   **Rules**: `rules/<rule>.md` with a `description`. Use a rule for
        guidance tied to file patterns (`globs`) or that always applies
        (`alwaysApply`), since a standard skill cannot set these fields.
    *   **Code** (tools, event handlers, commands with logic): extension
        modules listed in `package.json` under `omp.extensions`. See
        [Extensions](https://github.com/can1357/oh-my-pi/blob/main/docs/extensions.md).

1.  Register the plugin in `.omp-plugin/marketplace.json`:

    ```json
    {
      "name": "<name>",
      "source": "./plugins/<name>",
      "description": "What the plugin does.",
      "version": "0.1.0"
    }
    ```

    Raise `version` with every change. `omp plugin upgrade` only reinstalls
    plugins whose catalog version changed.

Use the same name in `plugin.json`, the catalog entry, and the directory. It
must be lowercase ASCII letters, digits, `-`, and `.`, start and end with a
letter or digit, contain no `--` or `..`, and be at most 64 characters.

If a plugin needs something neither the standard nor these locations provide,
such as a remote MCP server that sends a credential header, leave out
`plugin.json` for that plugin and say why in the plugin's README. omp then loads
it with its own conventions (`.mcp.json`, omp skill frontmatter) instead of the
standard.

## Testing a plugin

omp reports skipped skills and rejected plugins only in `omp skill list`, so
install into a temporary home and check its output before pushing:

```sh
(
  export HOME="$(mktemp -d)"
  omp plugin marketplace add ./
  omp plugin install <name>@sonsu-marketplace
  omp skill list
)
```

Every skill should appear, with no `warning:` lines.

## License

[MIT](LICENSE) © sonsu-lee
