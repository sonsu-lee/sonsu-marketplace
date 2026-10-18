---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Use Standard Readme and require Markdown lint checks

## Context and Problem Statement

[ADR-0003](0003-use-standard-readme.md) adopted Standard Readme without a linter
requirement. Subsequent README review found inconsistent list formatting, and
Markdown lint caught list-marker spacing errors. How should contributors check
Markdown formatting as well as the README's structure?

## Considered Options

- Standard Readme with manual formatting review only
- Standard Readme with Markdown lint run through `npx`

## Decision Outcome

Chosen option: "Standard Readme with Markdown lint run through `npx`", because it
adds a repeatable formatting check without a global installation or a repository
package manifest. This decision supersedes ADR-0003 and retains its Standard
Readme policy:

- Write documentation in English. The root README and any plugin README files
  follow the [Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md).
- Use the project name as the title and a short description of fewer than 120
  characters, consistent with GitHub and package metadata where applicable.
- Follow the specification's section names and ordering. Include `Install`,
  `Usage`, `Contributing`, and a final `License`. Include a table of contents for
  READMEs of 100 lines or more.
- Include installation and usage examples, `Dependencies` and `CLI` subsections
  where applicable, and project-specific sections after `Usage`. Keep authoring,
  testing, and contribution guidance under `Contributing`.
- Omit optional sections that add no useful information. Keep decision rationale
  in ADRs and link to it rather than duplicating it in README files.

Before pushing, run `markdownlint-cli` through `npx` on every Markdown file added
or modified by the change, including README files and ADRs. Use version `0.49.1`
and its default rules, and resolve all reported errors. Node.js 22 or newer and
npm (which provides `npx`) are required. For a README-only change, run:

```sh
npx --yes markdownlint-cli@0.49.1 README.md
```

Append the paths of any other changed Markdown files to the same command. The
explicit version keeps the check repeatable; `npx` downloads and caches the
package when needed. This decision does not add automatic formatting, CI
integration, or a requirement to reformat untouched documents.

### Consequences

- Good, because README structure stays predictable and formatting errors are
  checked consistently before review.
- Good, because contributors need no global Markdown linter installation.
- Bad, because contributors need Node.js and npm, and the first run requires
  access to the npm registry.
- Bad, because lint does not verify Standard Readme compliance, link targets,
  or the rendered appearance. These still need separate review.

### Confirmation

Run the pinned command with all changed Markdown paths and require a zero exit
status with no lint errors. Review README sections against Standard Readme,
check table-of-contents targets and local and external links, confirm the license
identifier and owner, and inspect the rendered Markdown. Exercise changed CLI
examples with a temporary `HOME` when running omp; plugin changes also require
the README's "Testing a plugin" procedure.
