# AGENTS.md

This repository is an omp plugin marketplace. Plugins follow the format in
[docs/decisions/0002-plugin-format.md](docs/decisions/0002-plugin-format.md).

* Add or change plugins as described in [README.md](README.md), "Adding a
  plugin".
* Raise the plugin's `version` in `.omp-plugin/marketplace.json` with every
  change to it.
* After changing a plugin, run the README's "Testing a plugin" procedure.
  Every skill must appear in `omp skill list` with no `warning:` lines.
* Run omp only with a temporary `HOME`. Do not install plugins into, or add
  this marketplace to, the user's own omp.
* Record decisions as described in
  [docs/decisions/0001-use-madr-for-decision-records.md](docs/decisions/0001-use-madr-for-decision-records.md).
  Do not edit an accepted record to change a decision; write a new record that
  supersedes it.
* Write documentation in English.
* When creating or updating a README, follow the
  [Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
  as adopted in [ADR-0003](docs/decisions/0003-use-standard-readme.md).
* Before pushing Markdown changes, run
  `npx --yes markdownlint-cli@0.49.1` with every added or modified Markdown file
  as an argument, including agent instructions and skills. Use Node.js 22 or
  newer and npm, and fix all reported errors. Check links and rendered Markdown
  separately; lint does not replace those checks. See
  [ADR-0004](docs/decisions/0004-require-markdown-lint.md) for the policy.
