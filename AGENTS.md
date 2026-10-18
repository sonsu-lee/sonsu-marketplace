# AGENTS.md

This repository is an omp plugin marketplace. Use the current procedures in
the README and skills below. Identify which requirements apply to the task and
read their linked procedures before making changes.

* Add or change plugins using the
  [plugin-authoring procedure](README.md#adding-a-plugin).
* Raise the plugin's `version` in `.omp-plugin/marketplace.json` with every
  change to it.
* After changing a plugin, run the
  [plugin test procedure](README.md#testing-a-plugin).
  Every skill must appear in `omp skill list` with no `warning:` lines.
* Run omp only with a temporary `HOME`. Do not install plugins into, or add
  this marketplace to, the user's own omp.
* Follow the [commit skill](plugins/git-workflow/skills/writing-commits/SKILL.md)
  when writing commit messages and the
  [branch skill](plugins/git-workflow/skills/naming-branches/SKILL.md)
  when choosing branch names, including their required validation procedures.
  Reuse repository tools and versions first; use the documented fallback only
  when no execution setup exists, never to bypass a broken setup.
* Record significant decisions, not implementation steps or a work log,
  following the [decision-record procedure](README.md#decision-records).
  Keep records under review `proposed` and consolidate revisions of the same
  decision in the same record. Mark them `accepted` only after decision review.
  Do not edit an accepted record to change a decision; write a new record that
  supersedes it.
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
