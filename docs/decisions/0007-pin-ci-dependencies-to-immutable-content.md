# Pin CI dependencies to immutable content

- Date: 2026-10-23
- Status: accepted
- Decision-makers: sonsu-lee

## Context

The `checks` workflow runs third-party code on every pull request: GitHub
Actions, the omp, Codex, and Claude Code CLIs, and tools fetched through `npx`
and `uvx`. Action tags can be moved to other commits, and an exact package
version still lets its dependencies resolve within version ranges. omp 18.12.6
declares 13 of its 27 direct dependencies as ranges, so an exact
`npm install -g` or `bun install -g` reinstalled a different dependency tree
whenever one of them published a new release, which is how recent npm supply
chain attacks spread.

[OpenSSF Scorecard's Pinned-Dependencies check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies)
treats a dependency as pinned only when it is fixed to a hash, recommends
committing lockfiles because they hold hashes for the whole tree, and treats
`npm install` in a workflow as unpinned even with an exact version.
[PyO3](https://github.com/PyO3/pyo3/tree/main/.github/tools/netlify) installs
a CI-only CLI the same way, from a manifest and lockfile under `.github/tools`
with `npm ci --ignore-scripts`.

## Decision

Pin everything CI executes to immutable content. Reference each action by its
full commit SHA, with the release tag in a comment. Install CLI tools from a
CI-only manifest and committed lockfile with a frozen install that skips
dependency install scripts, rather than by name and version. Pin the package
manager's version as well. Keep these files under `.github`, not at the
repository root, because the marketplace itself is not a Node project.

Runtime patch releases are the one deliberate exception: CI takes the latest
patch of the pinned Node.js major so security fixes arrive without a change.
The [README's CI section](../../README.md#running-checks-in-ci) owns the
current files, versions, and update steps.

## Rejected alternatives

- **Exact versions with global installs:** fixes only the top-level package;
  ranged dependencies still float, and Scorecard counts the install as
  unpinned.
- **Version tags for actions:** shorter to read, but a tag can be moved to a
  different commit after review.
- **Vendor binary installers with checksums:** remove the package manager, but
  omp's installer fetches the expected hash from the same origin as the
  binary, so it detects corruption, not a compromised origin.
- **A lockfile at the repository root:** works with default tooling, but makes
  the marketplace look like a Node package and mixes CI tools with plugin
  packaging.

## Consequences

CI runs the same reviewed code until a change updates a pin, and a modified or
republished dependency fails the frozen install instead of running. Updates
are deliberate work: an action, CLI, or package manager upgrade needs a new SHA
or a regenerated lockfile, and stale pins delay security fixes unless someone
updates them. Dependabot supports both GitHub Actions and Bun's `bun.lock` for
version updates, so automated update pull requests are an option. Scorecard
recognizes `npm ci` but not `bun install --frozen-lockfile`, so a Scorecard run
may still report the Bun install as unpinned even though it follows the same
principle.
