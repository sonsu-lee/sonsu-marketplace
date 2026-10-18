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

Validate the complete proposed message before creating or amending a commit,
or presenting the message as ready. Re-run validation after any message edit.
Follow the [validation procedure](references/validation.md) to select the
runner and configuration independently:

1. Use the repository's existing validation command, tool, and version first,
   including a validator other than commitlint. Follow its documented setup
   if dependencies are missing; an unavailable or failing configured tool is
   not permission to switch validators.
2. Only if no execution setup is established, run the pinned commitlint CLI via
   `npx`. Preserve repository configuration if present.
3. Only if no configuration is established, use the
   [bundled ESM defaults](assets/commitlint.config.mjs) with commitlint.
   Do not replace another validator's configuration with this file.

Respect repository acceptance criteria, including intentional warning levels.
Do not bypass a failed check or install hooks, CI jobs, or project dependencies
just to introduce the fallback. Report blockers rather than claim validation
passed. An existing hook does not validate a draft before it runs.

The bundled defaults check types, lowercase scopes, subject style, blank-line
separators, and 72-character limits. Review accuracy, rationale, imperative
wording, the initial lowercase letter, and breaking-change explanations
separately. The body-length rule exempts URL-containing lines; check those
manually. Also review any skill defaults the repository validator leaves
unchecked, without overriding an explicit repository rule.

## Example

```text
feat(api)!: return timestamps in UTC

Responses used server-local time without an offset, so clients could
interpret the same timestamp differently. Return ISO 8601 timestamps
with an explicit UTC offset instead.

BREAKING-CHANGE: created_at and updated_at now include a UTC offset.
Replace parsers that expect the previous offset-free format.
```
