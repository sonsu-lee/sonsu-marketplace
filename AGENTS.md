# AGENTS.md

This repository is an omp plugin marketplace. Plugins follow the format in
[docs/decisions/0002-plugin-format.md](docs/decisions/0002-plugin-format.md).

*   Add or change plugins as described in [README.md](README.md), "Adding a
    plugin".
*   Raise the plugin's `version` in `.omp-plugin/marketplace.json` with every
    change to it.
*   After changing a plugin, run the README's "Testing a plugin" procedure.
    Every skill must appear in `omp skill list` with no `warning:` lines.
*   Run omp only with a temporary `HOME`. Do not install plugins into, or add
    this marketplace to, the user's own omp.
*   Record decisions as described in
    [docs/decisions/0001-use-madr-for-decision-records.md](docs/decisions/0001-use-madr-for-decision-records.md).
    Do not edit an accepted record to change a decision; write a new record that
    supersedes it.
*   Write documentation in English.
