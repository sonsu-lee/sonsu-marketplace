# skill-workflow

Create, refine, evaluate, and independently review focused agent skills,
delegating mechanical work to existing tools.

## Install

Register the marketplace as described in the
[root installation guide](../../README.md#install), then run the command for
your client:

```sh
omp plugin install skill-workflow@sonsu-marketplace
codex plugin add skill-workflow@sonsu-marketplace
claude plugin install skill-workflow@sonsu-marketplace
```

### Dependencies

The `skill-workflow` plugin's `evaluating-skills` scripts need Python 3.11 or
newer, Git, and the omp or Codex CLI being evaluated; with an older `python3`,
they exit and print the equivalent `uv run --no-project --python 3.12`
command. Claude Code evaluations use Anthropic's `skill-creator` plugin from
`claude-plugins-official`.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details skill-workflow
```

In any supported client, ask for the task naturally:

```text
Revise the skill in skills/report-writer so it triggers only for report
drafting.

Evaluate skills/report-writer against its previous version.
```

Natural-language requests usually select the matching skill, but selection is
a model decision, not a guaranteed hook. To select a skill explicitly, use
`$skill-workflow:authoring-skills` in Codex or
`/skill-workflow:authoring-skills` in Claude Code. Listing a plugin does not
prove that its skills run.

### Skills

- **`authoring-skills`** creates, revises, and reviews focused agent skills
  using common Agent Skills principles, without a default client. It identifies
  the intended consumer from the request and project context, then loads only
  the relevant omp, Claude, or Codex considerations. It keeps judgment in the
  skill and delegates mechanical work to existing tools. Its checks distinguish
  discovery from complete prompt loading and task behavior; version-specific
  limits belong in client references, not common format rules. It routes
  behavior and activation evaluation to `skill-creator` in Claude Code or
  `evaluating-skills` for omp and Codex. See the
  [skill-authoring procedure](skills/authoring-skills/SKILL.md).
- **`evaluating-skills`** runs the Agent Skills evaluation loops against omp
  and Codex from any client with a shell: each skill's `evals/evals.json`
  prompts with and without the skill or against its previous version, graded
  assertions, a pass-rate, time, and token benchmark, a review viewer for human
  feedback, and description tuning against `evals/eval_queries.json`. It ports
  the client-independent parts of Anthropic's skill-creator under the Apache
  License 2.0 and adds omp and Codex adapters; Claude Code results come from
  the skill-creator plugin itself. See the
  [skill evaluation procedure](skills/evaluating-skills/SKILL.md).
- **`skill-workflow-reviewer`** is an omp agent that autoloads
  `authoring-skills` and reviews a fixed skill change read-only, without
  running checks. In omp, `authoring-skills` dispatches it after creating a
  skill or changing its behavior, and `reviewing-code` adds it when a reviewed
  change touches a skill. Codex and Claude Code use a fresh generic worker for
  behavioral skill authoring too. One controller owns each review assignment;
  authoring and execution do not launch duplicate skill reviewers.

Ask to create, revise, or simplify an agent skill to use `authoring-skills`.

This plugin does not install skills or configure projects. Plugin packaging
and marketplace checks remain in the repository's
[contributor guide](../../CONTRIBUTING.md#testing-a-plugin).

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
the repository's [contributor guide](../../CONTRIBUTING.md), including its
[plugin](../../CONTRIBUTING.md#adding-a-plugin) and
[testing](../../CONTRIBUTING.md#testing-a-plugin) procedures.

## License

[MIT](../../LICENSE) © sonsu-lee, except `skills/evaluating-skills/`, which is
under the [Apache License 2.0](skills/evaluating-skills/LICENSE.txt) and
includes material from Anthropic's
[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator).
