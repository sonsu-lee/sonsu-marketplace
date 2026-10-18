# AGENTS.md

This repository is an omp plugin marketplace. The current plugin format and
authoring procedure are in [README.md](README.md#adding-a-plugin); the rationale
is in [ADR-0002](docs/decisions/0002-plugin-format.md).

* Add or change plugins as described in [README.md](README.md), "Adding a
  plugin".
* Raise the plugin's `version` in `.omp-plugin/marketplace.json` with every
  change to it.
* After changing a plugin, run the README's "Testing a plugin" procedure.
  Every skill must appear in `omp skill list` with no `warning:` lines.
* Run omp only with a temporary `HOME`. Do not install plugins into, or add
  this marketplace to, the user's own omp.
* Record significant decisions, not implementation steps or a work log, using
  [MADR](docs/decisions/0001-use-madr-for-decision-records.md) and the
  [README's decision-record guidance](README.md#decision-records).
  Keep records under review `proposed` and consolidate revisions of the same
  decision in the same record. Mark them `accepted` only after decision review.
  Do not edit an accepted record to change a decision; write a new record that
  supersedes it.
* Keep current procedures in the README and relevant skills, and executable
  rules in configuration files. Update those sources when behavior changes;
  link to them from ADRs instead of duplicating commands or rule values.
* Write documentation in English.
* When creating or updating a README, follow the
  [README's documentation checklist](README.md#writing-documentation) and its
  linked Standard Readme specification, as adopted in
  [ADR-0003](docs/decisions/0003-use-standard-readme.md).
* Before pushing Markdown changes, run the README's pinned Markdown lint
  command on every added or modified Markdown file, including agent
  instructions and skills, and fix all reported errors. Check links and
  rendered Markdown separately; lint does not replace those checks. See
  [ADR-0004](docs/decisions/0004-require-markdown-lint.md) for the rationale.
