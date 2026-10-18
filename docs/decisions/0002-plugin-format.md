---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Package plugins as Agent Plugins with omp components alongside

## Context and Problem Statement

This marketplace targets omp, but its plugin format should preserve portable
skills and MCP servers without losing omp-specific commands, agents, rules,
and extension modules. A standard-only package cannot provide all of these
components, while an omp-conventions-only package gives up standard validation.

At the inspected
[`can1357/oh-my-pi@ba85aef0b3`](https://github.com/can1357/oh-my-pi/tree/ba85aef0b3)
revision, [Agent Plugins](https://agent-plugins.org/) 1.0.0 covered skills and MCP
servers. omp loaded those through the standard provider while continuing to
load its own component types alongside them. It did not yet consume the
standard's client-specific extension mechanism.

Which packaging approach preserves both capabilities with the least migration
risk?

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

Use the standard for portable components and omp's supported conventions for
client-specific components. Keep the catalog in omp's marketplace location.
If neither can express a required capability, an individual plugin may use the
omp-only format and document that exception.

### Current instructions

The [README's layout](../../README.md#layout) and
[plugin-authoring procedure](../../README.md#adding-a-plugin) define component
locations, manifest fields, supported substitutions, and alternatives for
omp-only features. The
[plugin test procedure](../../README.md#testing-a-plugin) defines how to verify
the installed package. Keep those operational details there.

### Consequences

* Good, because skills and MCP servers are portable and should not need
  migration if omp moves further toward the standard.
* Good, because the standard provider rejects malformed manifests and skill
  metadata instead of loading them silently.
* Bad, because discovery warnings are not reported by the installation command;
  the installed skills must be checked separately.
* Bad, because standard MCP configuration lacks some omp-specific expansion and
  credential options, so some plugins may require a documented exception.
* Bad, because the omp components use omp's existing conventions, not the
  standard's extension mechanism. If omp adopts `extensions` or namespaced
  extension directories, these components may need to move.

### Confirmation

The initial evaluation used omp 18.12.1 with a temporary `HOME`. It recorded
that standard skills and MCP servers coexisted with omp commands, agents,
rules, and extension modules; invalid standard manifests and skill metadata
were rejected. The omp-only path loaded malformed skills without warnings.
These observations support the portability and validation tradeoff above;
they are not a claim about every later omp release.

The evaluation did not establish whether rule `globs` and `alwaysApply` took
effect, or confirm runtime handling of agent `model` fields in the legacy
manifest path.

Use the README's plugin test procedure for new packages. Re-evaluate coexistence
and validation when the loader or supported standard changes.

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

* omp supports its options through `plugin.json` `extensions` or `SKILL.md`
  `metadata`, making the current component split unnecessary.
* omp deprecates or changes its conventional component locations.
* A new Agent Plugins version adds component types.
* A major omp release changes the loader assumptions.

The inspected implementation included marketplace extension loading from
[#3245](https://github.com/can1357/oh-my-pi/pull/3245). The proposed omp namespace
in [#8853](https://github.com/can1357/oh-my-pi/issues/8853) is a relevant point
to check when revisiting native support for the standard's extension mechanism.
