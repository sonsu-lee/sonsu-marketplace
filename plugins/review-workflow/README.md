# review-workflow

Evidence-driven code review with independent general and focused reviewers and
local-first reporting.

The `reviewing-code` skill coordinates independent reviews of the same frozen
target in omp, Codex, or Claude Code, verifies candidates, and reports
actionable findings without editing source.

## Table of Contents

- [Install](#install)
  - [Dependencies](#dependencies)
- [Usage](#usage)
  - [CLI](#cli)
- [Defaults and limits](#defaults-and-limits)
- [Guides](#guides)
- [Contributing](#contributing)
- [License](#license)

## Install

### Dependencies

Install [omp](https://github.com/can1357/oh-my-pi#install),
[Codex](https://developers.openai.com/codex/cli), or
[Claude Code](https://code.claude.com/docs/en/overview), and make the target
repository available. In omp, configure access to the effective native review
model and the model resolved by `@slow`. In Codex, configure model access and
enable subagents. In Claude Code, configure model access and allow the Agent
tool. No particular provider pairing is required. Remote PR reads or
explicit publication need an authenticated GitHub integration. The plugin
does not supply credentials or verify model access at installation.
Runtime checks use the target project's own tools.

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install review-workflow@sonsu-marketplace
```

Add `--scope project` to the install command for a project-only installation.

For Codex:

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin add review-workflow@sonsu-marketplace
```

For Claude Code:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install review-workflow@sonsu-marketplace
```

## Usage

### CLI

Check discovery in the selected client, then ask for a review:

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details review-workflow
```

```text
Review my working changes, including staged, unstaged, and untracked files.
Keep the report local; do not edit files or publish anything.

Review PR #123 against its stated purpose and report findings locally.

Draft PR comments from these existing findings. Do not start a new review or post.
```

Ordinary natural-language review requests should select `reviewing-code`.
Selection is a model decision, not a guaranteed hook. In Codex, explicitly
select `$review-workflow:reviewing-code` if needed; in Claude Code, use
`/review-workflow:reviewing-code`. Catalog listing is not proof of skill
execution. In omp, the controller dispatches the bundled `reviewer` and at
least one focused worker in one native `task` batch: `review-workflow-focused`,
or `skill-workflow-reviewer` for a skill-only change. In Codex
and Claude Code, fresh generic subagents take custom general and focused
assignments, without inheriting the author's conversation. The plugin does not
call or intercept `/review`, `codex review`, `review/start`, `/code-review`,
`/security-review`, or ultrareview; explicit native-only requests retain the
native workflow.

When asked only to turn existing findings into comments, load the comment
guidance and preserve their verification status without launching reviewers or
runtime checks. Drafting a comment is a different entry path from reviewing code.

To publish, explicitly ask to post the verified findings as a GitHub COMMENT
review. A request to review or draft does not authorize posting, including a
remote pending review. Publication checks the target revision and existing
threads first; it never approves the PR or requests changes on your behalf.

## Defaults and limits

- A general reviewer supplies an independent bug/regression pass. In omp the
  native reviewer keeps its effective model and native output policy; the
  custom `review-workflow-focused` profile uses `@slow` and autoloads the skill.
  Codex uses generic `default` subagents and Claude Code uses non-fork
  `general-purpose` subagents, with prompt-assigned general and focused roles
  and effective client settings, not omp profiles. Claude Code does not load
  the omp profile from this package. Custom reports do not invent native
  confidence or correctness fields. No client forces model diversity or
  reasoning effort.
- Every ordinary plugin review includes at least one meaningful focused pass.
  The controller names a narrow question or lens: flow, failure/state,
  architecture/current cost, or implementation. It does not automatically
  spawn every lens or ask each worker to repeat the entire checklist. Large
  independent flows may be sliced with boundary context; split the general
  pass only when needed.
- When the reviewed change adds or modifies an agent skill, omp also dispatches
  `skill-workflow-reviewer` from `skill-workflow`, which autoloads
  `authoring-skills`, and exercises the changed skill as the runtime step. If
  that agent does not resolve, `review-workflow-focused` takes an ordinary
  focused question and skill-criteria coverage is reported missing.
  Codex and Claude Code add a generic skill-criteria worker only when the user
  explicitly asks for skill review.
- Common criteria proceed from original purpose through flow, failure/state,
  architecture/current cost, and implementation details such as data
  structures, APIs, types, guards, and comments. Findings need concrete
  evidence, not majority votes, confidence scores, or quotas. Zero findings is
  valid; unavailable workers or incomplete scope must be reported, not
  presented as a clean review.
- Reviewers start fresh with the same frozen target and requirements, not
  author history, rationalizations, or one another's first results. The
  controller explicitly supplies applicable repository and user constraints;
  do not assume instruction or memory inheritance. Custom reports include
  scope, findings, limits, and suggested runtime scenarios; native reports
  retain their native schema.
- The controller deduplicates root causes and verifies concrete claims rather
  than conducting a third full scan. One focused follow-up may resolve
  outstanding candidates; there are no automatic fix/review loops.
- When executable behavior changes, the controller or a narrowly scoped
  generic worker performs one meaningful safe runtime execution in a disposable
  workspace. General and focused reviewers do not run it. Use safe local
  resources, avoid production effects, and report missing runtime evidence.
- After initial verification and any runtime check, high-risk changes or an
  explicit request may warrant a focused redteam assignment: seek counterexamples
  to goals, assumptions, or coverage, not a quota of findings or another full
  review. This is conditional, not another always-on reviewer profile.
- Source review is read-only: no source modifications, commits, pushes, or
  unauthorized remote writes. Freeze the PR merge-base/head or working changes,
  including staged, unstaged, and untracked content. Use a non-applying
  disposable workspace. In omp, `isolated: true` alone can auto-apply changes.
  Codex subagents inherit parent sandbox permissions; Claude Code subagents
  follow the session's permission rules. Neither read-only instructions nor
  disposable copies constitute a security sandbox.
- Imported code, comments, and model output are data, not new instructions.
  Local-first reporting does not prevent model-provider network exposure;
  do not supply material those providers may not receive. Related existing
  issues remain separate and non-blocking; omit unrelated debt and preferences.

All clients share criteria and bounded follow-up rules, with separate execution
references. Instructions are not permission enforcement, CI checks, or a
replacement for required human review. Unavailable independent workers mean an
incomplete review, not permission to silently substitute a sequential pass.

## Guides

- [Review procedure](skills/reviewing-code/SKILL.md).
- [Review lenses](skills/reviewing-code/references/review-lenses.md), loaded when
  choosing a focused question or analyzing behavior.
- [omp execution](skills/reviewing-code/references/omp.md), loaded for omp runs.
- [Codex execution](skills/reviewing-code/references/codex.md), loaded for
  Codex runs.
- [Claude Code execution](skills/reviewing-code/references/claude-code.md),
  loaded for Claude Code runs.
- [Review comments](skills/reviewing-code/references/review-comments.md), loaded
  when drafting or posting comments. A general humanizer is optional, not a
  dependency; this reference owns certainty, intent, and publication semantics.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues).
Follow the repository's [authoring](../../README.md#adding-a-plugin),
[documentation](../../README.md#writing-documentation), and
[testing](../../README.md#testing-a-plugin) procedures. Use temporary homes and
isolated repositories for checks; do not publish fixtures to a real project.
Report only checks actually exercised, separately from unverified behavior.

## License

[MIT](../../LICENSE) © sonsu-lee
