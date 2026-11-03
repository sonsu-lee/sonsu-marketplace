# Choosing evaluation

Format, discovery, complete loading, output quality, and activation are
separate claims; evidence for one does not establish another. Pick checks for
the behavior the change affects.

## Match checks to the change

- **Metadata or packaging:** the official format validator and the client's
  discovery check, then invoke the installed skill and inspect the injected
  content for complete loading without warnings.
- **Task guidance:** the output-quality loop on `evals/evals.json`, with and
  without the skill or against its previous version. Read transcripts, not
  just answers.
- **Tool or configuration:** run the actual tool with valid and invalid
  inputs. Use deterministic checks, not model opinion.
- **Description or scope:** a trigger eval on `evals/eval_queries.json` for
  the old and new descriptions, and observe actual loading.
- **Formatting only:** no behavioral benchmark.

When moving content to a reference to fit a loader, add an eval whose task
needs the moved content and assert that the reference is read.

## Pick the runner

Use the project's existing setup first; otherwise:

- **Claude Code:** Anthropic's [skill-creator plugin][creator].
- **omp and Codex:** the `evaluating-skills` skill.
- **Other clients:** the [output][outputs] and [description][descriptions]
  guides with the client's own tools.

## Feed results back

Revise from failures, feedback, and traces together. Prefer removing an
ineffective requirement over adding safeguards. Re-run affected cases, and
report smoke observations separately from repeated measurements.

## Gotchas

- Discovery may read only metadata and miss body truncation.
- A model saying it would use a skill is not evidence of activation.
- Never name a file `SKILL.md` under `evals/`; some clients register it.
- Keep workspaces outside installed packages, and never publish test
  artifacts such as tickets, PRs, or messages to real projects.
- Results hold only for the client, model, and effort that ran. A shared
  description must not lose passing trigger queries in any client.
- Keep evaluation out of the skill's everyday path; users of the skill do not
  run authoring benchmarks.

[outputs]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
