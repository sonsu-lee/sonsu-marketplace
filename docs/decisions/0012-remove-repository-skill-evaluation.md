# Remove repository-owned skill evaluation

- Date: 2026-11-20
- Status: proposed

## Context

[ADR-0009](0009-evaluate-skills-with-agent-skills-loops.md) adopted stored
skill cases and output and activation evaluation loops. [ADR-0011](0011-evaluate-skills-in-omp-at-the-guides-scale.md)
kept those loops but limited the required model runs to omp. Maintaining the
repository's runner and per-skill data makes these evaluations part of the
marketplace's supported scope.

## Decision

Propose removing the repository-owned evaluation runner, per-skill evaluation
data, and mandatory output and trigger evaluation procedures without replacing
the automatic comparison or benchmark functions. Keep plugin format,
discovery, and loading checks, and retain manual scenarios for behavior across
plugins, client settings, or installation. The current procedures are in the
[contributor guide](../../CONTRIBUTING.md#testing-a-plugin).

## Rejected alternatives

- **Keep the repository runner and mandatory loops:** preserves standardized
  comparisons but retains the runner, data, and ongoing maintenance as part of
  the marketplace.

## Consequences

The marketplace no longer provides automatic baseline comparisons, trigger
measurements, or benchmark reports. Format and loading checks cannot establish
behavioral quality or activation; manual scenarios provide observations for
specific clients and runs, not an equivalent automated comparison. Model runs
remain local under [ADR-0006](0006-keep-model-evaluations-local.md).

This proposal would replace the remaining evaluation-loop and stored-case
choices in ADR-0009 and ADR-0011 if accepted. Those records retain their current
statuses while this decision is proposed. The operational instructions have
already changed as part of the authorized implementation; their divergence
from those accepted records remains unresolved until a separate decision.
