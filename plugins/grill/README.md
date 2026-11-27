# grill

Stress-test an idea in rounds, with or without repository domain documents.

## Install

Register the marketplace using the [root guide](../../README.md#install), then
install the plugin in your client:

```sh
omp plugin install grill@sonsu-marketplace
codex plugin add grill@sonsu-marketplace
claude plugin install grill@sonsu-marketplace
```

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details grill
```

- [grill-me](skills/grill-me/SKILL.md): a file-free interview about a plan,
  idea, or draft. No repository is needed.
- [grill-with-docs](skills/grill-with-docs/SKILL.md): check proposed terms and
  decisions against the repository. With [development](../development/README.md)
  installed, it also loads [domain-modeling](../development/skills/domain-modeling/SKILL.md).
  Without it, the skill still reads project vocabulary and decisions. It only
  writes a glossary entry or ADR when you authorize that file.
- [grilling](skills/grilling/SKILL.md): the interview used by both skills.

Ask “Stress-test my plan” in omp, use `$grill:grill-me` in Codex, or type
`/grill:grill-me` in Claude Code. Confirming a decision does not authorize
implementation.

## Contributing

See the [contributor guide](../../CONTRIBUTING.md) for plugin checks.

## License

[MIT](../../LICENSE) © sonsu-lee. See [sources](SOURCES.md) and the
[third-party license](THIRD-PARTY-LICENSES) for Matt Pocock’s interview skills.
