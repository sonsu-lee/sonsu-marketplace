---
status: accepted
date: 2026-10-18
decision-makers: sonsu-lee
---

# Package plugins as Agent Plugins with omp components alongside

## Context and Problem Statement

omp loads plugin content in three ways:

1. **Claude Code compatible layout.** Conventional directories (`skills/`,
   `commands/`, `agents/`, `rules/`, `hooks/`, `tools/`, `.mcp.json`) and an
   optional `.claude-plugin/plugin.json`. Every marketplace install is read
   through this path (`discovery/claude-plugins.ts`). The marketplace catalog
   uses the same format.
2. **omp extension modules.** `package.json` `omp.extensions`, inherited from
   pi. Marketplace installs load them since
   [#3245](https://github.com/can1357/oh-my-pi/pull/3245).
3. **[Agent Plugins](https://agent-plugins.org/) 1.0.0.** A plugin whose root
   `plugin.json` declares the Agent Plugins `$schema` has its skills and MCP
   servers loaded only by the standard provider. Other components still load
   through ways 1 and 2 (`discovery/agent-plugin-format.ts:546`,
   `legacyProviderAllowed`).

The standard covers skills and MCP servers only. For client-specific data it
defines `extensions` in `plugin.json` and `metadata` in `SKILL.md`, but omp
reads neither: it stores `extensions` without using it
(`discovery/agent-plugin-format.ts:231`) and decides `hide` from top-level
frontmatter only (`extensibility/skills.ts:265`).
[#8853](https://github.com/can1357/oh-my-pi/issues/8853) proposes an omp
namespace under `extensions`; it is open and not implemented.

Which format should plugins in this marketplace use?

Source paths are relative to `packages/coding-agent/src/` in
[`can1357/oh-my-pi@ba85aef0b3`](https://github.com/can1357/oh-my-pi/tree/ba85aef0b3).

## Decision Drivers

* The marketplace targets omp only.
* Plugins should not need rework if omp moves further toward the standard.
* omp-specific components (commands, agents, rules, extension modules) must
  stay available.
* omp should reject malformed plugins rather than load them silently.

## Considered Options

* omp conventions only
* Agent Plugins only
* Agent Plugins with omp components alongside

## Decision Outcome

Chosen option: "Agent Plugins with omp components alongside", because it is the
only option that keeps both the standard's portability and validation and omp's
components. Its cost, the omp-only skill and MCP options, has workable
replacements.

Each plugin is laid out as follows:

| Component | Format | Location |
|---|---|---|
| Manifest | Agent Plugins | `plugin.json` |
| Skills | Agent Plugins | `skills/<skill>/SKILL.md` |
| MCP servers | Agent Plugins | `mcp.json` |
| Commands, agents, rules | omp | `commands/`, `agents/`, `rules/` |
| Code | omp | `package.json` `omp.extensions` |

The catalog stays at `.omp-plugin/marketplace.json`, the location omp docs
prefer when omp is the only consumer. Plugins do not use
`.claude-plugin/plugin.json` or `.mcp.json`.

When the standard lacks an omp feature, use an omp component instead:

| Need | Instead of | Use |
|---|---|---|
| Workflow that runs only when the user asks | skill with `hide` | command |
| Guidance tied to file patterns or always on | skill with `globs` or `alwaysApply` | rule |
| Code, tools, event handlers | `hooks/`, `tools/` | `omp.extensions` (omp docs prefer extensions over hooks) |

A plugin that needs something none of these provide, such as a remote MCP server
that sends a credential header, leaves out `plugin.json` and uses omp's
conventions. That plugin's README states why.

### Consequences

* Good, because skills and MCP servers are portable and should not need
  migration if omp moves further toward the standard.
* Good, because omp rejects an invalid `plugin.json` field, such as an
  uppercase `name`, and skips a `SKILL.md` with any field outside `name`,
  `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`
  (`discovery/agent-plugin-format.ts:90`).
* Bad, because omp shows those warnings only in `omp skill list`, not in
  `omp read`. The source has no TUI or `/status` consumer for them.
* Bad, because `mcp.json` values are literal apart from `${PLUGIN_ROOT}` and
  `${PLUGIN_DATA}`: no environment lookup and no `!command`
  (`mcp/manager.ts:2089`). A `stdio` server inherits omp's environment
  (`mcp/transports/stdio.ts:582`) and reads credentials from it.
* Bad, because the omp components use omp's existing conventions, not the
  standard's extension mechanism. If omp adopts `extensions` or namespaced
  extension directories, these components may need to move.

### Confirmation

Each case below was installed from a local checkout of this marketplace into a
temporary `HOME` with omp 18.12.1, then inspected with `omp skill list` and an
RPC session.

| Case | Result |
|---|---|
| Standard plugin with a skill, two commands, an agent, a rule, and an extension module | All loaded: the skill and rule in the system prompt, `/demo:<command>`, the agent in the task tool, and the extension's `session_start` ran |
| `mcp.json` `stdio` server with `${PLUGIN_ROOT}` in `args` | Connected and registered its tool. `${PLUGIN_ROOT}` expanded to the install cache, `PLUGIN_DATA` was set, and ambient environment variables were inherited |
| `.mcp.json` next to `mcp.json` in a standard plugin | Server not started |
| `plugin.json` `name: "Hello"` | Plugin installed, then rejected: `invalid plugin name "Hello"` |
| Skill with `hide`, or with `argument-hint` | Skill skipped: `unexpected frontmatter field` |
| Plugin without `plugin.json`, skill missing `description` or with broken YAML | Loaded without a warning |

Not confirmed at runtime:

* Whether rule `globs` and `alwaysApply` take effect.
* That `.claude-plugin/plugin.json` makes omp ignore agent `model` fields in a
  plugin without a standard `plugin.json`. The source says it does
  (`discovery/agent-plugin-format.ts:566`).

New plugins are confirmed with the README's "Testing a plugin" procedure.

## Pros and Cons of the Options

### omp conventions only

No `plugin.json`; the Claude Code compatible layout plus `omp.extensions`.

* Good, because every omp option is available, including skill `hide`,
  `globs`, and `alwaysApply`, and environment expansion in `.mcp.json`.
* Good, because it matches the plugin structure in omp's marketplace docs.
* Bad, because omp does not validate it: a skill with no `description` or with
  broken YAML loads without a warning.
* Bad, because omp's source calls these providers legacy, and the whole plugin
  would need migration if omp moves to the standard.

### Agent Plugins only

Only `plugin.json`, `skills/`, and `mcp.json`.

* Good, because the plugin is fully portable and fully validated.
* Bad, because commands, agents, rules, and extension modules are not available.

### Agent Plugins with omp components alongside

* Good, because skills and MCP servers are portable and validated.
* Good, because commands, agents, rules, and extension modules still load.
* Bad, because skills cannot set `hide`, `globs`, or `alwaysApply`, and
  `mcp.json` cannot expand environment variables.
* Bad, because the omp components may need to move when omp adopts the
  standard's extension mechanism.

## More Information

Revisit this decision, with a new record that supersedes this one, when:

* omp reads `plugin.json` `extensions` or `SKILL.md` `metadata` for omp
  options. Move the replacements above back into skills or MCP config, and move
  any non-standard plugins to the standard.
* omp deprecates or changes the conventional locations for commands, agents,
  rules, or extension modules.
* A new Agent Plugins version adds component types.
* omp's major version changes. Rerun the confirmation above.
