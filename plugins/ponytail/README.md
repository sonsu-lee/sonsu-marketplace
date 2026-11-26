# ponytail

Choose the smallest complete change. Review a diff or repository, or list
shortcuts and their limits.

## Install

[Register the marketplace](../../README.md#install), then run the command for
your host:

```sh
omp plugin install ponytail@sonsu-marketplace
codex plugin add ponytail@sonsu-marketplace
claude plugin install ponytail@sonsu-marketplace
```

## Usage

```text
Use Ponytail lite on this change.
List the shortcuts we deferred.
```

Use `/ponytail:ponytail-review` in Claude Code or `$ponytail:ponytail-review`
in Codex to select a diff review. In omp, name the skill in your request.

| Skill | Result |
| --- | --- |
| [ponytail](skills/ponytail/SKILL.md) | Lite builds the request and names a smaller option; full chooses the smallest complete change; ultra questions unnecessary scope first. |
| [ponytail-review](skills/ponytail-review/SKILL.md) | A read-only review of a change and its callers. |
| [ponytail-audit](skills/ponytail-audit/SKILL.md) | A ranked, read-only report on a repository or package. |
| [ponytail-debt](skills/ponytail-debt/SKILL.md) | A ledger of shortcut comments, their ceilings, and when to revisit them. |
| [ponytail-gain](skills/ponytail-gain/SKILL.md) | The upstream benchmark and its baseline, not a prediction for your repository. |
| [ponytail-help](skills/ponytail-help/SKILL.md) | Level selection, invocation, and how to stop. |

Select a level for the conversation; say “stop ponytail” to turn it off. This
skills-only package installs no hooks, session tracker, status line, or
persistent settings. It does not authorize edits or tests that your project or
host restricts.

## Contributing

Pull requests are welcome. Follow the [contributor guide](../../CONTRIBUTING.md)
and ask questions in the
[issue tracker](https://github.com/sonsu-lee/sonsu-marketplace/issues).

## License

[MIT](../../LICENSE) © sonsu-lee. The six skills and benchmark are adapted from
[Ponytail][upstream]; see [sources](SOURCES.md) and the [upstream MIT
notice](THIRD-PARTY-LICENSES).

[upstream]: https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846
