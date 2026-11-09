# ticket-workflow

English | [한국어](README.ko.md)

Write small, outcome-centered GitHub and Linear tickets while leaving
implementation to the assignee.

## Install

Register the marketplace as described in the
[root installation guide](../../README.md#install), then run the command for
your client:

```sh
omp plugin install ticket-workflow@sonsu-marketplace
codex plugin add ticket-workflow@sonsu-marketplace
claude plugin install ticket-workflow@sonsu-marketplace
```

### Dependencies

Publishing tickets needs authenticated tooling for the selected GitHub repository
or Linear workspace. `ticket-workflow` does not bundle credentials or configure
tracker integrations.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details ticket-workflow
```

In any supported client, ask for the task naturally:

```text
Draft a GitHub issue from these bug notes without publishing it.

Split this oversized Linear ticket into smaller drafts without publishing them.
```

Natural-language requests usually select the matching skill, but selection is
a model decision, not a guaranteed hook. To select a skill explicitly, use
`$ticket-workflow:writing-tickets` in Codex or
`/ticket-workflow:writing-tickets` in Claude Code. Listing a plugin does not
prove that its skills run.

### Skills

- **`writing-tickets`** writes plain, outcome-centered GitHub and Linear tickets.
  It follows project templates first; otherwise a clear title or one or two
  sentences can be the entire ticket. Bodies hold the current agreement, not
  accumulated investigation or progress logs, while retaining essential
  constraints. It also reviews labels,
  assignment, priority, estimates, and milestones, proposing grounded metadata
  separately from the body using the tracker's actual fields and conventions.
  Optional unknowns remain unset rather than guessed. Bug reports and parent
  tickets add kind-specific guidance, and suspected vulnerabilities follow the
  project's private reporting path instead of a public ticket. See the
  [ticket-writing procedure](skills/writing-tickets/SKILL.md)
  and [fallback template](skills/writing-tickets/assets/ticket-body.md).

Ask to draft, create, update, or split GitHub Issues or Linear tickets to use
`writing-tickets`. Draft requests do not publish issues.

Use ticket, then work, then PR as the normal development flow. Tickets and PRs
need not be one-to-one; partial work should not close the whole ticket.
Install `git-workflow` for downstream branch naming and PR preparation; it is not
needed to draft tickets. The ticket plugin respects existing tracker sync and
templates but does not configure them, publish duplicate issues to both trackers,
or enforce ticket-first work through hooks.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
the repository's [contributor guide](../../CONTRIBUTING.md), including its
[plugin](../../CONTRIBUTING.md#adding-a-plugin) and
[testing](../../CONTRIBUTING.md#testing-a-plugin) procedures.

## License

[MIT](../../LICENSE) © sonsu-lee
