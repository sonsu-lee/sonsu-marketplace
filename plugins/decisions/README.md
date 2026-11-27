# decisions

Draft and maintain architecture decision records.

## Install

Register the marketplace using the [root guide](../../README.md#install), then:

```sh
omp plugin install decisions@sonsu-marketplace
codex plugin add decisions@sonsu-marketplace
claude plugin install decisions@sonsu-marketplace
```

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details decisions
```

Ask whether a design choice warrants an ADR, or request a draft.
[writing-adrs](skills/writing-adrs/SKILL.md) follows the target project's
criteria and lifecycle before using its short template. Use
`$decisions:writing-adrs` in Codex or `/decisions:writing-adrs` in Claude
Code for explicit invocation. A draft neither accepts a proposal nor
authorizes writing it to the repository.

## Contributing

Pull requests are welcome; ask questions in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
[the contributor guide](../../CONTRIBUTING.md), including plugin checks.

## License

[MIT](../../LICENSE) © sonsu-lee. Third-party notices are in
[THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES); source revisions are in
[SOURCES.md](SOURCES.md).
