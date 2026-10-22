# AGENTS.md

This repository is a shared omp, Codex, and Claude Code plugin marketplace.
Use the current procedures in the README and skills below. Identify which
requirements apply to the task and read their linked procedures before making
changes.

* Add or change plugins, including support for another client, using the
  [plugin-authoring procedure](README.md#adding-a-plugin). Keep shared sources
  and client-specific execution separate, and verify each added client.
* When creating, revising, or reviewing skills, follow the
  [skill-authoring procedure](plugins/skill-workflow/skills/authoring-skills/SKILL.md),
  including its independent review step. In omp, reviews of changes that touch
  skills also dispatch `skill-workflow-reviewer` as described in the
  [omp review execution reference](plugins/review-workflow/skills/reviewing-code/references/omp.md).
* Raise the plugin's root `plugin.json` version and matching
  `.omp-plugin/marketplace.json` version together with every plugin change,
  along with its Claude Code catalog entry or `.claude-plugin/plugin.json`.
  Keep all client catalogs pointed at the same package directories.
* After changing a plugin, run the
  [plugin test procedure](README.md#testing-a-plugin) for every client.
  Require every expected skill exactly once without loading errors; omp
  discovery must have no `warning:` lines. Exercise representative tasks
  separately; listing is not proof of execution.
* Use separate temporary client homes: `HOME` for omp, both `HOME` and
  `CODEX_HOME` for Codex, and both `HOME` and `CLAUDE_CONFIG_DIR` for Claude
  Code. Do not install into live clients or copy real settings or credentials.
  Use `--no-daemon` for Codex model smoke runs and report unavailable
  authorized authentication as an execution blocker.
* Follow the [commit skill](plugins/git-workflow/skills/writing-commits/SKILL.md)
  when writing commit messages and the
  [branch skill](plugins/git-workflow/skills/naming-branches/SKILL.md)
  when choosing branch names, including their required validation procedures.
  Reuse repository tools and versions first; use the documented fallback only
  when no execution setup exists, never to bypass a broken setup.
* Follow the
  [PR skill](plugins/git-workflow/skills/writing-pull-requests/SKILL.md)
  when drafting, creating, updating, or marking a pull request ready, including
  title validation, repository templates, author checks, and UI evidence.
  Create new PRs as Draft by default; mark ready only on an explicit request.
* Follow the
  [ticket-writing procedure](plugins/ticket-workflow/skills/writing-tickets/SKILL.md)
  when drafting, creating, updating, or splitting GitHub Issues or Linear
  tickets. Use ticket, work, then PR as the normal development flow; follow the
  branch and PR skills for downstream work.
* When reviewing code, a diff, or a PR, or responding to feedback, follow the
  [review procedure](README.md#code-review) and the Code Review Rules below.
  Requested omp, Codex, and Claude Code plugin reviews use the linked common
  skill and the corresponding client execution reference; explicit native-only
  requests retain the native procedure and output. Results stay local unless
  publication is explicitly requested.
* When deciding whether to write an ADR, or drafting, reviewing, or replacing
  one, follow the [decision-record procedure](README.md#decision-records) and
  its [ADR skill](plugins/decision-workflow/skills/writing-adrs/SKILL.md).
  Record direction-setting or consequential design choices, not every shared
  rule, implementation step, or operational change. Keep proposals together
  until the decision-maker accepts them; implementation completion is not
  acceptance. Preserve accepted records and link a new record when the
  decision changes, not merely when it is reconsidered.
  The procedure documents the one-time ADR-0001 consolidation and ADR-0002
  through ADR-0004 format migration; do not infer permission for further resets.
* Keep current procedures in the README and relevant skills, and executable
  rules in configuration files. When adding or changing a requirement, update
  its operational source and ensure this file identifies when it applies and
  which procedure to follow. Add or adjust that routing in the same change if
  needed. Never leave an active requirement only in an ADR; ADRs link to current
  instructions rather than duplicate commands or values.
* Write documentation in English.
* When creating or updating a README, follow the
  [documentation checklist](README.md#writing-documentation) and its linked
  Standard Readme specification.
* Before pushing Markdown changes, run the pinned Markdown lint command in
  the [documentation procedure](README.md#writing-documentation) on every added
  or modified Markdown file, including agent instructions and skills. Fix all
  reported errors and check links and rendered Markdown separately.
* Before delivery, confirm that every applicable check above was completed.
  Report any verification blockers explicitly; do not describe unchecked work
  as verified.

## Code Review Rules

### Scope and evidence

* Review against the PR's coherent purpose, supported use cases, and repository
  requirements. Problems introduced or worsened by the change are in scope,
  even when fixing them is substantial. Do not invent new requirements.
* Before reporting a problem, inspect relevant surrounding code, callers,
  tests, and guidance. Explain the triggering conditions and concrete failure,
  requirement violation, or maintenance cost. Distinguish evidence from
  speculation; ask for clarification only when an important uncertainty
  cannot be resolved from available context.
* Skills are not exhaustive tool manuals. Missing examples, repeated
  safeguards, or explanations of ordinary tool usage are not defects by
  themselves. Flag omissions that lead to an incorrect action or consequential
  ambiguity, not merely information the reviewer did not know.
* Do not demand a broad architectural migration when a change follows an
  established pattern without violating an applicable requirement. Report
  consequential existing issues directly related to the changed path only as
  non-blocking warnings, explaining why resolution belongs in separate work.
  Omit unrelated debt and preference-only observations.
* Prefer the smallest sufficient correction, including simplification or
  deletion. Describe the required outcome rather than mandate one
  implementation. Justify additional tests by the important behavior or
  regression not covered; leave formatting and lint checks to automation.

### Comment intent

For native Codex reviews, preserve Codex's native priority and output format.
Custom plugin controllers use their own report contract, not native JSON.
These are local intent labels, not severity levels or settings that expand
which findings Codex posts:

* **Fix:** a concrete problem introduced or worsened by this PR, to address
  here.
* **Warning (non-blocking):** a consequential, directly related existing
  issue whose resolution belongs in separate work.
* **Suggestion (non-blocking):** an optional alternative with a concrete
  benefit; acknowledge that the current approach is valid.
* **Nit (non-blocking):** minor polish; omit unless explicitly requested.

Make the intent clear in comments that merit reporting; do not fill categories.
Non-blocking labels do not excuse low-value feedback. No findings is a valid
outcome.

### Review iterations

* Consolidate repeated manifestations of one actionable root cause into one
  finding, identifying the affected scope. Keep independently actionable
  problems separate.
* When prior discussion is available, read it before commenting. Do not
  duplicate findings or reopen settled decisions without new evidence, a
  regression, or a newly discovered consequential defect. Explain what changed.
  In subsequent rounds, prioritize the agreed fixes and their effects rather
  than restarting an open-ended search for improvements.
