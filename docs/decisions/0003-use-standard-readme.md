# Use Standard Readme for README files

- Date: 2026-10-19
- Status: accepted
- Decision-makers: sonsu-lee

## Context

The marketplace README must explain installation, usage, and plugin development
without making readers learn a different structure for each plugin. As the
catalog grows, the documents need a predictable structure without unnecessary
sections.

## Decision

Use [Standard Readme](https://github.com/RichardLitt/standard-readme) for the root
and plugin READMEs. Its recognizable section names and ordering provide familiar
navigation while leaving room for marketplace-specific instructions. Omit
optional sections that add no value, and keep decision rationale in ADRs.

The [README's documentation guidance](../../README.md#writing-documentation)
owns the authoring and review checklist, including language, required sections,
navigation, examples, and license information. It uses the
[Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
as the structural source.

## Rejected alternatives

- **Keep the repository-specific structure:** Retains the current outline but
  does not provide the recognizable section names and ordering that motivated
  adopting Standard Readme.

## Consequences

- Readers can find installation, usage, and contribution guidance without
  learning a repository-specific outline. Existing plugin instructions fit
  without a separate handbook.
- Section changes require keeping the table of contents and links in sync,
  and descriptions must stay aligned with external metadata.
- Rendered navigation and examples still need review, and changed CLI examples
  need to be exercised using the plugin test procedure when applicable.
  Markdown lint, covered in [ADR-0004](0004-require-markdown-lint.md), does not
  establish structural compliance with Standard Readme.
