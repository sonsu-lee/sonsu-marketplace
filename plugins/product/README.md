# product

Draft product requirements, decision records, and outcome-centered tickets.

## Install

Register the marketplace using the [root guide](../../README.md#install), then:

```sh
omp plugin install product@sonsu-marketplace
codex plugin add product@sonsu-marketplace
claude plugin install product@sonsu-marketplace
```

Tracker publication or private context needs authorized access to the relevant
GitHub repository or Linear workspace. This package supplies no credentials.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details product
```

Ask for a PRD draft, ADR assessment, or ticket. Use
`$product:writing-prd` in Codex or `/product:writing-prd` in Claude Code for
explicit invocation. Selection is model-dependent; listing is not execution.

- [writing-prd](skills/writing-prd/SKILL.md) synthesizes agreed requirements
  and preserves scope, defaults and prohibitions.
- [writing-adrs](skills/writing-adrs/SKILL.md) follows the target project's
  criteria and lifecycle before using its lightweight fallback.
- [writing-tickets](skills/writing-tickets/SKILL.md) uses applicable tracker
  templates and preserves observable outcomes and real blocking relationships.

Drafting does not authorize a file write, tracker publication, implementation,
or branch creation. Existing tracker synchronization is respected, not configured.
For downstream branch and pull-request tasks, install [git](../git/README.md).

## Contributing

Pull requests are welcome; ask questions in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
[the contributor guide](../../CONTRIBUTING.md), including plugin checks.

## License

[MIT](../../LICENSE) © sonsu-lee. Third-party notices are in
[THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES); source revisions are in
[SOURCES.md](SOURCES.md).
