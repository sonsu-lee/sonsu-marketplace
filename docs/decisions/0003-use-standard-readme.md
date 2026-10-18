---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Use Standard Readme for README files

## Context and Problem Statement

The marketplace README must explain installation, usage, and plugin development
without making readers learn a different structure for each plugin. As the
catalog grows, which convention keeps these documents predictable without
adding unnecessary sections?

## Considered Options

* [Standard Readme](https://github.com/RichardLitt/standard-readme)
* Keep the current, repository-specific structure

## Decision Outcome

Chosen option: "Standard Readme", because it defines recognizable section names
and ordering while leaving room for marketplace-specific instructions.

Apply the same structure to root and plugin READMEs, while keeping decision
rationale in ADRs. Standard Readme provides familiar navigation without forcing
optional content that adds no value to a particular plugin.

### Current instructions

The [README's documentation guidance](../../README.md#writing-documentation)
contains the authoring and review checklist, including language, required
sections, navigation, examples, and license information. It references the
[Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
as the structural source.

### Consequences

* Good, because readers can find installation, usage, and contribution guidance
  without learning a repository-specific outline.
* Good, because existing plugin instructions fit without a separate handbook.
* Bad, because section changes require keeping the table of contents and links
  in sync, and descriptions must stay aligned with external metadata.

### Confirmation

Review README changes using the documentation checklist and inspect their
rendered navigation and examples. Exercise changed CLI examples using the
plugin test procedure when applicable. Markdown lint, covered separately in
[ADR-0004](0004-require-markdown-lint.md), does not establish structural
compliance with Standard Readme.
