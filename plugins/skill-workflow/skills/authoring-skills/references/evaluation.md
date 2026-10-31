# Choosing evaluation

Format, discovery, complete prompt loading, output quality, and activation are
separate claims; evidence for one does not establish another. Choose checks
for the behavior the change affects.

## Match checks to the change

- **Metadata or packaging:** use the official format validator and the target
  client's discovery check. Separately invoke the installed skill and inspect
  events and injected content for complete main-file loading without warnings.
  Use the client's actual invocation identity and version-specific limits;
  discovery may inspect only metadata and miss body truncation.
- **Task guidance:** run the output-quality loop on the skill's
  `evals/evals.json`, with and without the skill or against its previous
  version. Inspect actions and transcripts, not just final answers.
- **Tool or configuration behavior:** run the actual tool with representative
  valid and invalid inputs. Use deterministic checks for mechanical rules; an
  LLM opinion is not a substitute for a validator result.
- **Description or scope:** measure triggering on `evals/eval_queries.json`
  for the old and new descriptions, and observe whether the client actually
  loads the skill. A model saying it would use the skill is not evidence of
  activation.
- **Formatting-only edits:** do not manufacture a behavioral benchmark.

Run manual checks in isolated workspaces, and never publish test artifacts,
such as tickets, pull requests, or messages, to real projects.

When splitting content to fit a loader, keep essential workflow and safety
instructions in the main file and give moved detail an explicit loading
condition. Add an eval whose task needs the moved content, with an assertion
that the reference is read. A size check or prompt capture proves neither
reference use nor task success.

## Pick the runner for the client

Use the project's existing evaluation setup when it has one; otherwise:

- **Claude Code:** Anthropic's [skill-creator plugin][creator].
- **omp and Codex:** the `evaluating-skills` skill.
- **Other clients:** follow the [output][outputs] and
  [description][descriptions] guides with the client's own tools.

Every runner reads `evals/evals.json`, `evals/eval_queries.json`, and
`evals/files/` in the skill directory. Never name a file `SKILL.md` under
`evals/`, because some clients register nested skill files. Keep workspaces
outside installed packages. Results hold only for the client, model, and
effort that ran; a description shared by several clients must not lose
passing trigger queries in any of them.

## Feed findings back into authoring

Use output failures, human feedback, and traces together. Resolve the root
cause with clearer decisions, a useful example, simpler instructions, or a
reusable tool where warranted. Prefer removing ineffective requirements over
accumulating safeguards. Re-exercise affected cases after changes and report
smoke observations separately from comparative or repeated measurements.
Keep evaluation fixtures and reports outside the skill's everyday execution
path; do not make downstream users run authoring benchmarks.

[outputs]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
