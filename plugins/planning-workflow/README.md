# planning-workflow

English | [한국어](README.ko.md)

Plan non-trivial work and coordinate authorized execution through independent
review and final validation.

## Table of Contents

- [Install](#install)
  - [Dependencies](#dependencies)
- [Usage](#usage)
  - [CLI](#cli)
  - [Skills](#skills)
- [Contributing](#contributing)
- [License](#license)

## Install

Register the marketplace as described in the
[root installation guide](../../README.md#install), then run the command for
your client:

```sh
omp plugin install planning-workflow@sonsu-marketplace
codex plugin add planning-workflow@sonsu-marketplace
claude plugin install planning-workflow@sonsu-marketplace
```

### Dependencies

`executing-work` requires independent review of code and behavioral skill
changes. It loads `reviewing-code` from
[review-workflow](../review-workflow/README.md) for code review and follows
`authoring-skills` from [skill-workflow](../skill-workflow/README.md) for a
skill-only change without a code-review controller. Install those plugins when
your work needs that review; otherwise the missing review is reported as a
limitation, not as a pass.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details planning-workflow
```

In any supported client, ask for the task naturally:

```text
Plan adding CSV export to the reports page. Do not change any files yet.

Implement the approved plan, then review and validate the final revision.
Do not commit or push.
```

Natural-language requests usually select the matching skill, but selection is
a model decision, not a guaranteed hook. To select a skill explicitly, use
`$planning-workflow:planning-work` in Codex or
`/planning-workflow:planning-work` in Claude Code. Listing a plugin does not
prove that its skills run.

### Skills

- **`planning-work`** plans non-trivial work, such as a feature, a change
  spanning several pull requests, or product and UI planning, as a design to
  approve before implementation. It distinguishes the requested deliverable
  from the intended outcome without expanding scope, reads available context,
  and asks only about unknowns that would change the plan. Where consequential
  assumptions are uncertain, it seeks direct evidence, concrete methods, and
  external checks that could disprove them. It traces requirements through the
  design, considers reachable edge cases, plans verification and delivery,
  and marks the plan Draft or Decided. It uses an independent reader where
  available (otherwise disclosing self-review), which is not proof the plan works,
  and waits for explicit approval. Research and experiments stop once they can
  no longer change a decision and stay read-only for plan-only requests; the
  plan follows a required output format and stays resumable from the latest
  agreement. See the
  [planning procedure](skills/planning-work/SKILL.md).
- **`executing-work`** coordinates authorized work through implementation,
  independent review, scoped cleanup, and final-revision validation. It reuses
  a valid plan, keeps commit, push, publication, merge, and deployment permissions
  separate, and delegates testing or cleanup only when useful. One controller
  owns review dispatch, including skill-criteria review when applicable. A
  change that repeats one rule across many sites uses a rerunnable query for
  scope and coverage, the least machinery that applies it consistently, and
  incremental updates instead of a fresh survey. See the
  [execution procedure](skills/executing-work/SKILL.md).

Planning and execution apply [Ponytail's smallest-complete-change principle][ponytail]:
reuse suitable capabilities without dropping requested behavior or safeguards.
For README and guide edits, `executing-work` favors the owning document over
duplicate procedures. These instructions travel with the skills; consumers do
not need this repository's README, but the relevant skill must be loaded.

Small, clear changes need no plan. The skills guide agent behavior; they do not
install hooks or grant permissions. Use the relevant ticket, ADR, and Git skills
for those specialized artifacts.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
the repository's [contributor guide](../../CONTRIBUTING.md), including its
[plugin](../../CONTRIBUTING.md#adding-a-plugin) and
[testing](../../CONTRIBUTING.md#testing-a-plugin) procedures.

## License

[MIT](../../LICENSE) © sonsu-lee

[ponytail]: https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md
