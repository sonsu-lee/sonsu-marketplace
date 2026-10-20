# Require Markdown lint checks for all Markdown documents

- Date: 2026-10-19
- Status: accepted
- Decision-makers: sonsu-lee

## Context

Inconsistent Markdown formatting affects READMEs, decision records, and agent
instructions alike. Manual review does not reliably catch these errors, but a
marketplace should not need a package manifest just to run a formatting check.

## Decision

Run Markdown lint through `npx` with a pinned tool version. This provides a
repeatable formatting check without a global installation or a repository
package manifest. Require it before pushing for every added or modified
Markdown file, across all maintained document types, rather than reformatting
unrelated files. Do not add automatic formatting or a new CI integration.

The [README's documentation guidance](../../README.md#writing-documentation)
owns the Node.js prerequisite, pinned command, file selection, and separate
link and rendering checks. [AGENTS.md](../../AGENTS.md) makes those checks
mandatory for agents.

## Rejected alternatives

- **Manual formatting review only:** Does not reliably catch formatting errors
  or provide the repeatable check needed across maintained Markdown documents.

## Consequences

- Markdown formatting is checked consistently before review without requiring
  contributors to install a global linter. Adoption is incremental because only
  changed files need checking.
- Contributors need Node.js and npm, and the first run requires access to the
  npm registry.
- The check must pass, but lint does not verify link targets, rendered
  appearance, Standard Readme compliance, or plugin behavior. Those still need
  their separate checks. This complements [ADR-0003](0003-use-standard-readme.md),
  which governs document structure.
