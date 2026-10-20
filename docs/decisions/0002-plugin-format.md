# Package plugins as Agent Plugins with omp components alongside

- Date: 2026-10-19
- Status: accepted
- Decision-makers: sonsu-lee

## Context

This marketplace targets omp, but needs portable skills and MCP servers without
losing omp-specific commands, agents, rules, and extension modules. The packaging
choice should minimize migration if omp moves further toward the standard and
reject malformed plugins rather than load them silently.

At the inspected
[`can1357/oh-my-pi@ba85aef0b3`](https://github.com/can1357/oh-my-pi/tree/ba85aef0b3)
revision, [Agent Plugins](https://agent-plugins.org/) 1.0.0 covered skills and MCP
servers. omp loaded those through the standard provider and its own component
types alongside them, but did not yet consume the standard's client-specific
extension mechanism. That implementation included marketplace extension loading
from [#3245](https://github.com/can1357/oh-my-pi/pull/3245).

The initial evaluation used omp 18.12.1 with a temporary `HOME`. Standard skills
and MCP servers coexisted with omp commands, agents, rules, and extension
modules; invalid standard manifests and skill metadata were rejected. The
omp-only path loaded malformed skills without warnings. These observations
support the packaging tradeoff, not a claim about every later omp release.
The evaluation did not establish whether rule `globs` and `alwaysApply` took
effect, or confirm runtime handling of agent `model` fields in the legacy
manifest path.

## Decision

Package plugins as Agent Plugins for portable components, with omp's supported
conventions alongside for client-specific components. This preserves standard
portability and validation without giving up omp capabilities; the unavailable
omp-only skill and MCP options have workable alternatives. Keep the catalog in
omp's marketplace location.

If neither format can express a required capability, an individual plugin may
use the omp-only format and document that exception. The
[README's layout](../../README.md#layout) and
[plugin-authoring procedure](../../README.md#adding-a-plugin) own component
locations, manifest fields, supported substitutions, and alternatives for
omp-only features. Use the
[plugin test procedure](../../README.md#testing-a-plugin) for new packages.

## Rejected alternatives

- **omp conventions only:** The Claude Code compatible layout plus
  `omp.extensions`, without `plugin.json`, matches omp's marketplace guidance
  and supports options such as skill `hide`, `globs`, `alwaysApply`, and
  environment expansion in `.mcp.json`. However, a skill with no `description`
  or broken YAML loaded without a warning. The providers are marked legacy in
  omp's source, leaving the whole package exposed to a future standard-format
  migration.
- **Agent Plugins only:** Using only `plugin.json`, `skills/`, and `mcp.json`
  retains standard portability and validation, but cannot provide the required
  commands, agents, rules, and extension modules.

## Consequences

- Skills and MCP servers retain portable packaging and standard validation.
  At the evaluated version, the standard provider rejected malformed manifests
  and skill metadata rather than loading them silently.
- Installation does not report discovery warnings, so installed skills need
  a separate check.
- Standard skills cannot set omp's `hide`, `globs`, or `alwaysApply`, and
  `mcp.json` cannot expand environment variables. Standard MCP configuration
  also lacks some omp-specific credential options, so documented exceptions
  may remain necessary.
- omp components use existing conventions rather than the standard's extension
  mechanism. If omp adopts `extensions` or namespaced extension directories,
  those components may need to move.

Re-evaluate coexistence and validation when omp changes its loader or component
locations, supports its options through `plugin.json` `extensions` or `SKILL.md`
`metadata`, or a new Agent Plugins version adds component types. The proposed
omp namespace in [#8853](https://github.com/can1357/oh-my-pi/issues/8853) is a
relevant reference when revisiting standard extension support.

Create a superseding record only if the chosen approach changes. Re-evaluation
that confirms the existing choice does not require a new ADR.
