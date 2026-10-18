---
name: writing-commits
description: Use this skill when writing or revising a git commit message, including when creating or amending a commit.
---

# Writing commits

Check and follow the repository's commit-message rules, including its
commitlint configuration. Use the defaults below where the repository
specifies no rule.

## Message rules

Base the message on the actual changes. Use Conventional Commits:

```text
<type>(<scope>): <subject>

<body>

<footers>
```

* **Type:** one of `feat`, `fix`, `docs`, `refactor`, `perf`, `test`,
  `build`, `ci`, `chore`, `style`, `revert`.
* **Scope:** optional; a lowercase name of the part that changes.
* **Subject:** describe the specific change in the imperative, starting
  with a lowercase letter and without a final period. Keep the entire
  first line within 72 characters and meaningful on its own.
* **Body:** explain why the change is needed and any important context or
  limitations not apparent from the diff. Omit it when the subject is
  sufficient. Do not invent a rationale the change does not establish.
* **Body and footers:** separate them from the preceding section with a
  blank line and wrap at 72 columns.
* **Breaking changes:** add `!` before the colon or a `BREAKING-CHANGE:`
  footer, or both. Explain what breaks and how callers should adapt.

## Required validation

After writing or revising a message, you MUST validate the complete message
(header, body, and footers) with commitlint through `npx`. Do not create or
amend a commit, or present a message as ready to use, until validation passes.
Re-run validation after any message change.

Use Node.js 22.12.0 or newer and npm. From the target repository's root,
save the exact proposed message in a temporary UTF-8 file and set
`message_file` to its absolute path. Read the file back to confirm it contains
the intended nonempty header and complete message; commitlint can skip empty
files. If the repository has a commitlint configuration, run:

```sh
npx --yes --package @commitlint/cli@21.2.4 commitlint \
  --strict --verbose --edit "$message_file"
```

Respect the repository's configuration, including any explicitly selected
config path (`--config`) and required presets or plugins. Install those
dependencies using the repository's documented setup; do not replace its
rules to make validation pass.

Only when the repository has no commitlint configuration, use the bundled
[ESM configuration](assets/commitlint.config.mjs). Set `skill_dir` to the
absolute directory containing this loaded `SKILL.md`, not the target
repository or a guessed plugin-cache path. Resolve the asset relative to
that directory; do not copy it into the repository.

```sh
npx --yes --package @commitlint/cli@21.2.4 commitlint \
  --config "$skill_dir/assets/commitlint.config.mjs" \
  --strict --verbose --edit "$message_file"
```

Fix all errors and warnings and require exit status zero. If Node.js, npm,
network access, or configuration dependencies are unavailable, report the
blocker and stop before committing; manual review is not a substitute.
Do not add a package manifest, commitlint config, Git hook, or CI job to the
target repository just to run this check. Remove the temporary message file
afterward.

The bundled config checks allowed types, lowercase scopes, subject style,
blank-line separators, and 72-character header, body, and footer limits.
It has no external imports or presets. It accepts breaking changes marked
with `!`, a `BREAKING-CHANGE:` footer, or both.

Lint does not replace review of accuracy, rationale, imperative wording,
the subject's initial lowercase letter, or breaking-change explanations.
The body line-length rule exempts lines containing URLs; check those
manually against the 72-column rule. When repository configuration is used,
also review any skill defaults it leaves unchecked.

## Example

```text
feat(api)!: return timestamps in UTC

Responses used server-local time without an offset, so clients could
interpret the same timestamp differently. Return ISO 8601 timestamps
with an explicit UTC offset instead.

BREAKING-CHANGE: created_at and updated_at now include a UTC offset.
Replace parsers that expect the previous offset-free format.
```
