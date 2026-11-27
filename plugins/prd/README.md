# prd

Draft product requirements from an agreed discussion or specification.

## Install

Register the marketplace using the [root guide](../../README.md#install), then:

```sh
omp plugin install prd@sonsu-marketplace
codex plugin add prd@sonsu-marketplace
claude plugin install prd@sonsu-marketplace
```

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details prd
```

Ask for a PRD draft. [writing-prd](skills/writing-prd/SKILL.md) preserves
agreed requirements, scope, defaults, and prohibitions without reopening the
interview. To invoke it explicitly, use `$prd:writing-prd` in Codex or
`/prd:writing-prd` in Claude Code. Drafting does not authorize a file write,
tracker publication, or implementation. To turn the PRD into tickets, install
[tickets](../tickets/README.md).

## Contributing

Pull requests are welcome; ask questions in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
[the contributor guide](../../CONTRIBUTING.md), including plugin checks.

## License

[MIT](../../LICENSE) © sonsu-lee. Third-party notices are in
[THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES); source revisions are in
[SOURCES.md](SOURCES.md).
