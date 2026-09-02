# Engineering

Engineering is a documentation-aware method for planning, implementing, debugging, verifying, and reviewing software changes. It packages composable Codex skills while keeping Git delivery, external research, and output-language guidance in separate plugins.

This local plugin is based on [obra/superpowers](https://github.com/obra/superpowers) v6.3.0 and is not an official Superpowers distribution. See [UPSTREAM.md](UPSTREAM.md) for the pinned source, imported files, local revisions, and retained compatibility names.

## Responsibilities

Engineering owns the development method:

- clarify a change and its documentation impact;
- reuse or create an isolated worktree when needed;
- write an implementation plan without automatically creating dated documents;
- apply TDD to production behavior changes and proportionate validation elsewhere;
- execute the plan inline or with subagents under the applicable commit boundary;
- debug systematically, request review, and verify completion;
- present integration choices after a development branch is complete.

The plugin does not require another plugin. Direct branch, commit, ticket, push, and pull request work belongs to the independent Workflow plugin when it is installed. Multi-source external research belongs to Research, and output-language guidance belongs to Fluent Languages. Codex can select these plugins together from their skill descriptions when a request spans more than one responsibility.

## Installation

Register this repository as the `sonsu-marketplace` marketplace, then install Engineering:

```sh
codex plugin marketplace add .
codex plugin add engineering@sonsu-marketplace
```

Repository changes and plugin installation are separate actions. Start a new Codex task after installing or updating the plugin so that the task receives the current skill catalog.
Remove an installed `superpowers` plugin before installing `engineering`; keeping both versions can expose duplicate copies of the same skills.

## Development flow

1. **brainstorming** clarifies the problem, alternatives, design, and documentation impact before implementation.
2. **using-git-worktrees** reuses an existing linked worktree or creates one when isolation is needed.
3. **writing-plans** writes an in-chat plan by default and records documentation, validation, and Git authorization boundaries.
4. **executing-plans** performs inline execution. **subagent-driven-development** is available when its file-backed plan and task commits are explicitly authorized.
5. **test-driven-development** applies RED–GREEN–REFACTOR to production behavior changes. Documentation, metadata, and simple configuration use checks appropriate to the change.
6. **requesting-code-review** and **receiving-code-review** handle review without treating unverified feedback as fact.
7. **verification-before-completion** requires current evidence before a success claim.
8. **finishing-a-development-branch** presents integration choices after applicable verification passes.

## Skills

| Area | Skills |
| --- | --- |
| Entry point | `using-engineering-skills` |
| Design and planning | `brainstorming`, `writing-plans` |
| Workspace and execution | `using-git-worktrees`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents` |
| Quality | `test-driven-development`, `systematic-debugging`, `verification-before-completion` |
| Review and completion | `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch` |
| Skill development | `writing-skills` |

Internal references use the `engineering:*` namespace, such as `engineering:brainstorming` and `engineering:systematic-debugging`.

## Local policy

- Inspect existing ADR, architecture, product, guide, reference, and runbook documents before proposing a new durable document.
- Keep implementation plans in the conversation by default. Use Git-ignored scratch files only when execution requires a file.
- Treat design approval, document writing, implementation, commit, push, pull request, merge, and deployment as separate authorization boundaries.
- Use TDD for production behavior changes and defects. Use proportionate structural or consuming-command validation for documentation, metadata, and simple configuration.
- Keep Engineering, Workflow, Research, and Fluent Languages independently installable.

The repository policies are recorded in the [documentation guide](../../docs/README.md), [skill-routing architecture](../../docs/architecture/skill-routing.md), and associated decision records.

## Compatibility and visual companion

Scratch plans, subagent ledgers, and persistent brainstorming sessions continue to use `.superpowers/`. This legacy path preserves existing local artifacts and script compatibility; it is not the current plugin name.

The optional brainstorming visual companion still uses the upstream Prime Radiant image when telemetry is enabled. Set `ENGINEERING_DISABLE_TELEMETRY` to a true value to prevent that request. The legacy `SUPERPOWERS_DISABLE_TELEMETRY`, `DISABLE_TELEMETRY`, and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` variables remain supported.

## Upstream and license

Engineering includes work derived from Superpowers v6.3.0. The original source, pinned commit, imported scope, and local changes are recorded in [UPSTREAM.md](UPSTREAM.md). The original MIT copyright notice remains in [LICENSE](LICENSE).
