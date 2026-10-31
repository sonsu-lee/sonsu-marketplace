# Enforce design evidence at the omp runtime boundary

- Date: 2026-10-29
- Status: proposed

## Context

The design plugin needs reusable visual judgment and stronger control over what
an agent may call verified. A skill can teach typography, hierarchy, interaction
and evidence limits, but the same model writes both its work and its completion
claim. Instructions alone cannot establish that a capture happened, that a
check passed, or that evidence still describes the current files.

The marketplace shares packages across clients, while their execution hooks
and tools differ. omp's extension lifecycle can mediate tools and session
completion. It does not turn arbitrary shell commands, browser bridges or other
in-process extensions into a filesystem sandbox. Treating every tool result as
proof or treating an assistant's approval field as operator consent would keep
the trust decision inside the actor being checked.

## Decision

Keep design judgment in portable, narrowly scoped skills. Put optional stronger
verification in an omp extension that starts only after an operator approves an
explicit scope. The extension owns controlled writes, capture/check execution,
revision-bound evidence and the official outcome. Operator acceptance remains
separate from evidence production and from the model's completion request.

During an active run, reject broad execution and delegation paths that the
extension cannot mediate instead of trying to infer their effects after the
fact. Completion requires current declared evidence and operator acceptance;
interruption, unavailable capabilities and stalled verification remain visible
non-success outcomes. Preserve an operator exit and wait for human review
without an unbounded model retry loop.

Make the official result a report the extension owns, not the agent's chat.
Observed model answers kept inventing approval states even after the skills
said not to, and omp, Codex and Claude Code hooks all run after text has
already been shown. So the operator confirms the project facts in the plan, an
operator command writes the report without streaming it, a fresh tool-less
model process checks its statements against those facts, and the operator
accepts the exact checked bytes, which are then published unchanged. A failed
or unreadable check blocks publication. Ordinary chat stays unchecked.

Preserve the host's existing tool selection and presentation. Hiding schemas is
not an execution boundary, and the supported extension interface cannot
round-trip the distinction between top-level and mounted tools. Expose the
controlled tools directly and enforce the allowlist before execution rather than
reconfiguring unrelated tools.

This is a cooperation boundary within omp, not hostile-code isolation. Approving
a process check grants real process access. A screenshot and successful
assertions establish an observed state, not general visual quality or usability.
Codex and Claude Code receive the shared skills without a claim of equivalent
runtime enforcement. Current commands, supported targets, limitations and checks
belong in the [plugin guide](../../plugins/design-workflow/README.md), not here.

## Rejected alternatives

- **Enforce the workflow only in SKILL.md:** portable and simple, but leaves
  permission, evidence and completion under model control. Keep it as guidance
  where runtime enforcement is unavailable, without relabeling it as a harness.
- **Allow every existing tool and inspect results afterward:** accommodates
  more workflows but cannot reliably constrain broad execution or establish
  trusted evidence provenance. Exclude unsupported paths rather than certify
  them from self-reported tool output.
- **Promise identical hooks in every client now:** would either misrepresent
  unsupported capabilities or require separate adapters whose behavior has not
  been implemented and verified. Share criteria, not an unearned guarantee.
- **Check every chat answer with Stop or display hooks:** these hooks run after
  the text is visible and either continue the turn or fail open, so they cannot
  hold back an unchecked answer. Withholding all chat would need host changes.
- **Rely on JSON schemas or stricter skill wording alone:** a schema constrains
  shape, not whether a stated approval is true, and wording changes did not stop
  the observed errors.

## Consequences

Portable skill guidance remains useful without activating the harness. omp can
make the distinction between completed, stopped, blocked and limited runs
observable, and stale file evidence cannot silently retain approval. These
controls intentionally narrow strict-mode workflows and require operator
participation; remote/native-editor work may require a non-success exit or a
separately designed adapter. Reports cost two extra model calls, and the fact
check is a model judgment that can miss errors or reject correct text; it is
measured, not assumed.

The extension depends on supported omp lifecycle behavior and local browser and
process capabilities. Other trusted extensions, external writers and approved
checks remain outside its isolation guarantee. Revisit this boundary if hostile
code isolation or equivalent enforcement on another client becomes a supported
requirement. Implementation and verification do not accept this proposed record
on the decision-maker's behalf.
