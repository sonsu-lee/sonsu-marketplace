# decision-workflow

English | [한국어](README.ko.md)

Select consequential design decisions and write lightweight ADRs using
repository conventions first.

## Install

Register the marketplace as described in the
[root installation guide](../../README.md#install), then run the command for
your client:

```sh
omp plugin install decision-workflow@sonsu-marketplace
codex plugin add decision-workflow@sonsu-marketplace
claude plugin install decision-workflow@sonsu-marketplace
```

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details decision-workflow
```

In any supported client, ask for the task naturally:

```text
Does moving our job queue from Redis to Postgres warrant an ADR?

Draft an ADR for that decision and leave it proposed.
```

Natural-language requests usually select the matching skill, but selection is
a model decision, not a guaranteed hook. To select a skill explicitly, use
`$decision-workflow:writing-adrs` in Codex or `/decision-workflow:writing-adrs`
in Claude Code. Listing a plugin does not prove that its skills run.

### Skills

- **`writing-adrs`** selects decisions worth recording and writes short ADRs
  with context, a decision and its rationale, rejected alternatives, and
  consequences. It follows the target project's scope, template, and lifecycle
  first; without those, it uses direction-setting and consequential design
  choices as its boundary. See the
  [ADR writing procedure](skills/writing-adrs/SKILL.md)
  and [default template](skills/writing-adrs/assets/adr.md).

Ask whether a design choice warrants an ADR, or ask to draft, review, or
supersede one, to use `writing-adrs`. It does not create a decision record for
every implementation change.

The principles follow Martin Fowler's ADR guidance, and the default template
is adapted from Evolu. Drafts remain proposed until the decision-maker accepts
them; changing an accepted decision requires a linked replacement. This plugin
does not install hooks, impose a format on existing repositories, or turn
routine work into ADRs.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
the repository's [contributor guide](../../CONTRIBUTING.md), including its
[plugin](../../CONTRIBUTING.md#adding-a-plugin) and
[testing](../../CONTRIBUTING.md#testing-a-plugin) procedures.

## License

[MIT](../../LICENSE) © sonsu-lee
