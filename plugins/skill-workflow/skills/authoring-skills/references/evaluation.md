# Choosing evaluation

Choose checks for the changed behavior. Format, discovery, complete prompt
loading, activation, output quality, and enforcement are different claims;
evidence for one does not establish the others. Follow the project's existing
validation setup rather than introducing a new evaluation framework.

## Start with the changed behavior

- **Metadata or packaging:** use the official format validator and the target
  client's discovery check. Separately invoke the installed skill and inspect
  events and injected content for complete main-file loading without warnings.
  Use the client's actual invocation identity and version-specific limits;
  discovery may inspect only metadata and miss body truncation.
- **Task guidance:** exercise a representative request and a relevant boundary
  case. Inspect actions and outputs, not just the final answer. Use isolated
  workspaces and avoid publishing test artifacts to real projects.
- **Tool or configuration behavior:** run the actual tool with representative
  valid and invalid inputs. Use deterministic checks for mechanical rules;
  an LLM opinion is not a substitute for a validator result.
- **Description or scope:** check relevant prompts and near-misses, observing
  whether the client actually loads the skill. A model saying it would use the
  skill is not evidence of activation.

When splitting content to fit a loader, retain essential workflow and safety
instructions in the main file and give moved detail explicit loading conditions.
Exercise a task that needs the moved content and check that the reference is
read. A size check or prompt capture proves neither reference use nor task
success. With model access unavailable, report loading evidence separately from
unverified reference following and behavior.

Start small. For a new workflow, two or three realistic cases can reveal useful
failures before investing in a larger evaluation. For a formatting-only edit,
do not manufacture a behavioral benchmark. Report what was exercised and what
remains unverified; a smoke check does not establish a reliable success rate.

## Compare when effectiveness is the question

When deciding whether instructions add value, whether deleting them is safe,
or whether a revision improves results, use the
[output evaluation guide][outputs]. Compare with and without the skill, or the
old and new versions, using the same tasks and inputs in fresh contexts.
Keep unrelated instructions, tools, model settings, and workspace state
consistent so they do not explain the difference.

Judge observable outcomes and important boundaries, not exact wording or the
presence of headings. Use code for objectively checkable properties and human
review for qualities such as clarity or visual usefulness. Require evidence
for each claimed pass and review the criteria themselves: checks that always
pass in both conditions may not measure the skill's contribution.

Read execution traces to explain the results. A correct answer reached through
unnecessary checks or unrelated changes may still indicate a poor instruction.
Compare time and token cost when available, without claiming small samples
establish statistical reliability. Inspect failures in the evaluation setup
before treating them as skill failures.

## Optimize activation only when needed

For missed or excessive activation, use the
[description optimization guide][descriptions]. Include realistic positive
queries and nearby negative queries with overlapping vocabulary. Observe
actual skill loading, repeat runs to account for variation, and keep a fixed
train/validation split. Revise from training failures; use validation results
to select a version, not to add query-specific keywords. Check new prompts
before claiming the revision generalizes.

Full trigger optimization is not a prerequisite for every skill edit. Choose
it when activation is uncertain or is the behavior the change intends to fix.

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
