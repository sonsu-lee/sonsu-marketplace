---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Require Markdown lint checks for all Markdown documents

## Context and Problem Statement

README review found inconsistent list formatting, and Markdown lint caught
list-marker spacing errors. The same formatting issues can affect ADRs, skill
instructions, and other Markdown documents. How should contributors check
Markdown formatting consistently across the repository?

## Considered Options

- Manual formatting review only
- Markdown lint run through `npx`

## Decision Outcome

Chosen option: "Markdown lint run through `npx`", because it adds a repeatable
formatting check without a global installation or a repository package manifest.

This policy applies to all Markdown documents maintained in the repository,
including root and plugin READMEs, ADRs, contributor and agent instructions,
skills, commands, and rules.
It complements [ADR-0003](0003-use-standard-readme.md), which remains the decision
for README structure; it does not replace that decision.

Before pushing, run `markdownlint-cli` through `npx` on every Markdown file added
or modified by the change. Use version `0.49.1` and its default rules, and resolve
all reported errors. Node.js 22 or newer and npm (which provides `npx`) are
required. For example, a change to a README and this ADR is checked with:

```sh
npx --yes markdownlint-cli@0.49.1 \
  README.md docs/decisions/0004-require-markdown-lint.md
```

Pass every added or modified Markdown file, not just the example paths above.
The explicit version keeps the check repeatable; `npx` downloads and caches the
package when needed. The policy applies to every document type, but each change
only needs to check the files it touches. Untouched documents are checked when
they are next modified; this does not require a repository-wide reformat.
No automatic formatting or CI integration is introduced.

### Consequences

- Good, because all Markdown document types receive the same formatting checks
  before review.
- Good, because contributors need no global Markdown linter installation.
- Bad, because contributors need Node.js and npm, and the first run requires
  access to the npm registry.
- Bad, because lint does not verify Standard Readme compliance, link targets,
  or the rendered appearance. These still need separate review.

### Confirmation

Run the pinned command with all added or modified Markdown paths and require a
zero exit status with no lint errors. Check links and inspect the rendered
Markdown separately. README changes must also satisfy ADR-0003's structural
review, and lint does not replace plugin tests or checks of documented commands.
