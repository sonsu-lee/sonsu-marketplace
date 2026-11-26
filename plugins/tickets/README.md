# tickets

Draft and manage outcome-centered GitHub Issues and Linear tickets.

## Install

Register the marketplace using the [root guide](../../README.md#install), then:

```sh
omp plugin install tickets@sonsu-marketplace
codex plugin add tickets@sonsu-marketplace
claude plugin install tickets@sonsu-marketplace
```

### Dependencies

Tracker publication or private context needs authorized access to the relevant
GitHub repository or Linear workspace. This package supplies no credentials.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details tickets
```

Ask for a ticket draft or a split of an existing issue.
[writing-tickets](skills/writing-tickets/SKILL.md) uses applicable tracker
templates and preserves observable outcomes and real blocking relationships.
Use `$tickets:writing-tickets` in Codex or `/tickets:writing-tickets` in
Claude Code for explicit invocation. Drafting does not authorize publishing,
changing metadata, implementing a ticket, or creating a branch. Existing
tracker synchronization is respected, not configured. For downstream branch
and pull-request tasks, install [git](../git/README.md).

## Contributing

Pull requests are welcome; ask questions in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
[the contributor guide](../../CONTRIBUTING.md), including plugin checks.

## License

[MIT](../../LICENSE) © sonsu-lee. Third-party notices are in
[THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES); source revisions are in
[SOURCES.md](SOURCES.md).
