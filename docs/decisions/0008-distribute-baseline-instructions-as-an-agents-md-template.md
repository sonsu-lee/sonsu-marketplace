# Distribute baseline instructions as an AGENTS.md template

- Date: 2026-10-24
- Status: proposed

## Context

The marketplace has so far distributed only plugins, whose skills hold
task-specific procedures. Some guidance should apply to almost every task:
write no speculative code, cite evidence before claiming completion, and stop
to ask when something is unclear. Skill bodies load on demand, through
selection or explicit invocation, rather than as session-opening instructions.

This repository has not verified one shared plugin mechanism for loading such
instructions across its supported clients:

- [ADR-0002](0002-plugin-format.md) did not establish whether omp rules with
  `alwaysApply` take effect.
- A Claude Code report that plugin `SessionStart` hooks do not pass
  `additionalContext` to the model was
  [closed for inactivity](https://github.com/anthropics/claude-code/issues/16538)
  without a recorded fix.
- Codex supports plugin lifecycle hooks only for
  [manually installed desktop plugins](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks),
  and skips them until the user trusts them.

All three clients read `AGENTS.md`: [omp](https://github.com/can1357/oh-my-pi/blob/main/docs/context-files.md),
[Codex](https://developers.openai.com/codex/guides/agents-md), and
[Claude Code](https://code.claude.com/docs/en/claude-md#agents-md), which reads
it directly when no `CLAUDE.md` applies and otherwise through an import.
Always-loaded instructions have a cost: one
[evaluation of context files](https://arxiv.org/abs/2602.11988) found no
general gain in task success and over 20% higher inference cost.

## Decision

Distribute always-applicable guidance as one template file outside the plugin
packages. Users copy it into their own instruction file or import it where
their client supports imports. The template holds only short criteria that
apply to almost every task; task procedures stay in skills, and each skill
must work without the template.

This uses a path the three clients already share instead of depending on
client-specific plugin capabilities. It extends the shared-source direction
proposed in [ADR-0005](0005-share-plugins-across-clients.md) beyond plugin
packages and does not replace it.

## Rejected alternatives

- **Client-specific always-on components** (omp rules, Claude Code and Codex
  hooks): could automate loading, but their support and trust requirements
  differ by client and a shared installation contract is not established.
  Hook-based paths also add executable code to maintain.
- **Skills only:** need no new distribution path, but are activated on demand,
  so they do not establish session-wide baseline guidance.

## Consequences

Users can adopt one source of guidance through their clients' instruction-file
mechanisms. The marketplace's scope grows from plugins to plugins plus an
instruction template. Users' copies do not update automatically and can drift
from the source. Plugin checks do not cover the template, so its effect needs
separate model runs. Every line adds cost to every session, so a line belongs
in the template only if omitting it would cause mistakes.

Moving later to client-specific components would require users to remove
their copies, or the guidance would load twice. Revisit this decision if the
clients gain a common, working way for plugins to add instructions to every
session.
