---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Use Standard Readme for README files

## Context and Problem Statement

The marketplace README explains installation and plugin development, but has no
table of contents or dedicated usage and contribution sections. As the catalog
grows, readers need predictable places to find these instructions. Which
convention should the repository's README files follow?

## Considered Options

* [Standard Readme](https://github.com/RichardLitt/standard-readme)
* Keep the current, repository-specific structure

## Decision Outcome

Chosen option: "Standard Readme", because it defines recognizable section names
and ordering while leaving room for marketplace-specific instructions.

The root README and any plugin README files follow the
[Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md).
Documentation remains in English. Apply these rules when creating or updating a
README:

* Use the project name as the title and a short description of fewer than 120
  characters. Keep the description consistent with GitHub and package metadata
  where applicable.
* Use the specification's section names and order. Include `Install`, `Usage`,
  `Contributing`, and a final `License` section. Include a table of contents for
  READMEs of 100 lines or more; it may be omitted for shorter files.
* Show installation and common usage in code blocks. Document manually installed
  prerequisites under `Install` / `Dependencies` and CLI usage under `Usage` /
  `CLI` where applicable.
* Put marketplace-specific sections, such as available plugins and layout,
  after `Usage`. Keep plugin authoring and testing under `Contributing`, along
  with where to ask questions and whether pull requests are accepted.
* Omit optional sections that add no useful information. Keep decision rationale
  in ADRs and link to it rather than duplicating it in README files.

### Consequences

* Good, because readers can find installation, usage, and contribution guidance
  without learning a repository-specific outline.
* Good, because existing plugin instructions fit without a separate handbook.
* Bad, because section changes require keeping the table of contents and links
  in sync, and descriptions must stay aligned with external metadata.

### Confirmation

Review README changes against the linked specification. Check required sections
and their order, table-of-contents targets, local and external links, and the
license identifier and owner. Render the Markdown to check navigation and code
blocks. Exercise changed CLI examples with a temporary `HOME`; plugin changes
also require the README's "Testing a plugin" procedure. No README linter or CI
requirement is introduced by this decision.
