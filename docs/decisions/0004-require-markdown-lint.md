---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Require Markdown lint checks for all Markdown documents

## Context and Problem Statement

Inconsistent Markdown formatting affects READMEs, decision records, and agent
instructions alike. Manual review does not reliably catch these errors, but a
marketplace should not need a package manifest just to run a formatting check.
How should contributors validate Markdown consistently?

## Considered Options

- Manual formatting review only
- Markdown lint run through `npx`

## Decision Outcome

Chosen option: "Markdown lint run through `npx`", because it adds a repeatable
formatting check without a global installation or a repository package manifest.

Apply the check to every maintained Markdown document type, but only require
each change to check the files it adds or modifies. This keeps adoption
incremental rather than forcing unrelated reformatting.

Pin the tool version to make checks repeatable. Use a pre-push validation step,
not automatic formatting or a new CI integration. This complements
[ADR-0003](0003-use-standard-readme.md): lint checks Markdown formatting, while
Standard Readme defines document structure.

### Current instructions

The [README's documentation guidance](../../README.md#writing-documentation)
defines the current Node.js prerequisite, pinned `npx` command, file selection,
and separate link and rendering checks.
[AGENTS.md](../../AGENTS.md) makes those checks mandatory for agents.

### Consequences

- Good, because all Markdown document types receive the same formatting checks
  before review.
- Good, because contributors need no global Markdown linter installation.
- Bad, because contributors need Node.js and npm, and the first run requires
  access to the npm registry.
- Bad, because lint does not verify Standard Readme compliance, link targets,
  or the rendered appearance. These still need separate review.

### Confirmation

Run the README's pinned command on every added or modified Markdown file and
require a zero exit status. Review links, rendering, and README structure
separately; successful lint does not replace those checks or plugin validation.
