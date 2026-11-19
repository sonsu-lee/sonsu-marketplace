# Choosing evaluation

Format, discovery, complete loading, output quality, and activation are
separate claims; evidence for one does not establish another. Pick checks for
the behavior the change affects.

## Match checks to the change

- **Metadata or packaging:** the official format validator and the client's
  discovery check, then invoke the installed skill and inspect the injected
  content for complete loading without warnings.
- **Task guidance:** exercise representative tasks and inspect transcripts as
  well as outcomes; follow the project's verification procedure.
- **Tool or configuration:** run the actual tool with valid and invalid
  inputs. Use deterministic checks, not model opinion.
- **Description or scope:** try relevant requests and near misses, observing
  whether the skill actually loads.
- **Formatting only:** no behavioral benchmark.

When moving content to a reference to fit a loader, exercise a task that needs
the moved content and check that the reference is read.

Use the project's existing verification setup and requirements.

## Feed results back

Revise from failures, feedback, and traces together. Prefer removing an
ineffective requirement over adding safeguards. Re-run affected cases, and
report smoke observations separately from repeated measurements.

## Gotchas

- Discovery may read only metadata and miss body truncation.
- A model saying it would use a skill is not evidence of activation.
- Run manual checks in isolated workspaces kept outside installed packages,
  and never publish test artifacts such as tickets, PRs, or messages to real
  projects.
- Results hold only for the client, model, and effort that ran.
- Keep evaluation out of the skill's everyday path; users of the skill do not
  run authoring benchmarks.
