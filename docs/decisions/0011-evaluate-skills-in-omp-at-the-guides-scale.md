# Evaluate skills in omp at the scale the Agent Skills guides recommend

- Date: 2026-11-01
- Status: accepted
- Decision-makers: sonsu-lee

## Context

[ADR-0009](0009-evaluate-skills-with-agent-skills-loops.md) adopted the Agent
Skills loops and ran them through each client's runner: skill-creator in
Claude Code and the `evaluating-skills` skill in omp and Codex. The README
procedure that implemented it added two rules the guides do not contain:
evaluate every behavioral change in all three clients, three runs per
configuration by default (`run_evals.py --runs` defaulted to 3).

The [output-quality guide][outputs] starts with two or three test cases,
treats early iterations as single runs judged by pass counts and the delta,
and expands the cases and repetitions later. The [description guide][descriptions]
runs each query about three times and holds out a validation split when
optimizing a description. Their examples use Claude Code, but neither
requires a particular client or model.

The first application of those rules re-evaluated the stacked pull requests
[#54](https://github.com/sonsu-lee/sonsu-marketplace/pull/54)–[#56](https://github.com/sonsu-lee/sonsu-marketplace/pull/56)
and [#63](https://github.com/sonsu-lee/sonsu-marketplace/pull/63) on
2026-11-01, one evaluation round, with results reported in those pull
requests:

- omp ran 288 sessions over about two hours and measured every run, with
  tokens and times. Most deltas were ±0.03–0.06, which one assertion in one
  of three runs accounts for.
- Codex hit the test account's usage limit on its first run, so none of its
  results were measured.
- In Claude Code, skill-creator reported grader output characters as tokens,
  hit a 20-subagent cap that refused and restarted reviewer runs, and its
  trigger script detected no skill load in any of 60 invocations. Part of the
  delay came from driving its interactive session, not from skill-creator.

## Decision

Evaluate skill changes in omp only, with the `evaluating-skills` scripts and
the model the README lists, and take case counts and repetitions from the
Agent Skills guides. omp is chosen because it runs unattended from the
repository scripts, recorded every measurement in the round above, and is not
bound by the Codex test account's usage limit.

- Output loop: start with two or three cases aimed at the changed behavior,
  one run per configuration. Keep earlier cases; add cases or runs when
  results are inconsistent or reveal a gap. `run_evals.py` now defaults to one
  run.
- Trigger loop: three runs per query as the guide suggests; the held-out
  split applies when optimizing a description, as before.
- The `evaluating-skills` Codex adapter stays, covered by the existing unit
  tests, for users who evaluate in Codex; the repository procedure does not
  require it. Codex and Claude Code runs are no longer required.
- Manual scenario checks keep their scope, behavior across plugins, client
  settings, or installation, in each client, once per scenario by default.

The current procedure is in the README's
[Evaluating skills](../../README.md#evaluating-skills) section.

## Rejected alternatives

- **Keep all three clients at three runs:** the most coverage, but the round
  above took hours, left Codex unmeasured, and produced Claude Code numbers
  that could not be used.
- **Keep all three clients at one run:** cheaper, but still depends on the
  Codex account limit and on driving skill-creator interactively.
- **Evaluate in Claude Code only:** keeps Anthropic's maintained runner, which
  ADR-0009 preferred over writing one runner for every client, but it cannot
  run unattended from the repository scripts, and its measurements were the
  least reliable in this round; whether that comes from the tool or from how it
  was driven is not established.

## Consequences

Results compare across pull requests and iterations within one client and
model, not across clients. A round should take far less time, which is
expected rather than measured. Client-specific skill behavior in Codex and
Claude Code is not measured by either loop; a difference shows up only in
manual scenarios or user reports. Single runs cannot separate flakiness from
skill effects, so a small delta needs repeated runs before it supports a claim.

Reconsider when a manual scenario or a user report shows a skill behaving
differently by client, or when Codex or Claude Code offer an unattended runner
with reliable measurements. This record supersedes ADR-0009's choice of one
runner per client; its loops, file formats, and workspace layout remain.

[outputs]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
