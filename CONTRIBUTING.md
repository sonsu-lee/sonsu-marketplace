# Contributing to sonsu-marketplace

Issues and pull requests are welcome. This page explains how to report a
problem, make a change, and add a plugin.

## Reporting a problem

Open a [GitHub issue](https://github.com/sonsu-lee/sonsu-marketplace/issues).
Include the plugin name, your omp version (`omp --version`), what you did, and
what happened.

## Making a change

1.  Create a branch named by
    [Conventional Branch](https://conventionalbranch.org/), for example
    `feature/add-login-skill`.
1.  Keep each pull request to one self-contained change.
1.  Write commit messages in
    [Conventional Commits](https://www.conventionalcommits.org/) with the
    `@commitlint/config-conventional` types.
1.  Run the [checks](#checking-your-changes).
1.  Open a pull request. Pull requests are squash merged, and the title and
    description become the commit message: write the title as a Conventional
    Commits header and the description as plain paragraphs that say what
    changed and why.

## Adding a plugin

*   Package the plugin as [Agent Plugins](https://agent-plugins.org/) 1.0.0: a
    root `plugin.json` with the 1.0.0 `$schema`, and each skill in
    `skills/<name>/SKILL.md` following the
    [Agent Skills specification](https://agentskills.io/specification).
*   Register it in `.omp-plugin/marketplace.json` with `name`,
    `source` (`./plugins/<name>`), `description`, and `version`. Raise the
    version with every change; omp upgrades a plugin only when its catalog
    version changes.
*   Target omp only; do not add a `.claude-plugin/` catalog.

## Checking your changes

```sh
node scripts/validate-marketplace.ts
```

This checks that omp accepts every catalog entry. It needs omp and Node.js
22.18 or later. CI runs it on every pull request.

## Documentation style

Write in English. The root `README.md` follows
[Standard Readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md),
plugin READMEs follow
[Google's README guide](https://google.github.io/styleguide/docguide/READMEs.html),
and all Markdown follows the
[Google Markdown style guide](https://google.github.io/styleguide/docguide/style.html).

## License

Contributions are licensed under the [MIT License](LICENSE).
