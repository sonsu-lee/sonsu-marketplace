# Engineering Quality Gate Contract

Use this contract when an Engineering lifecycle skill declares a quality gate. The
stage that creates an artifact owns its gate and its return path. Do not create a
central gate dispatcher or recursively invoke the whole workflow.

## Quality Is Not Authorization

A quality gate decides whether the current artifact has enough evidence to advance.
It never grants permission to write a durable document, implement, stage, commit,
push, create a PR, merge, deploy, publish, or perform another external action.
Apply the relevant authorization gate separately.

## Define the Gate Before Running It

Record these fields in the conversation, plan, progress ledger, or review package:

```text
Gate: <stable gate id>
Artifact: <path, task, diff, or other exact scope>
Revision: <commit SHA, content digest, or saved review-package identity>
Required checks: <checks that must produce evidence>
Pass condition: <observable result>
Evidence: <commands, outputs, review result, or human decision>
Findings: <none or unresolved findings>
Status: <status below>
Return target: <nearest stage that can change the failing input>
Attempt: <current>/<cap>
Decision owner: <stage owner or named human decision-maker>
```

Set the required checks, pass condition, return target, and finite attempt cap before
the first run. Use a content digest or immutable review package when a file is not
committed. If the artifact changes, the previous result is stale; run the required
checks against the new revision before advancing.

## Statuses

| Status | Meaning | May advance a required gate? |
| --- | --- | --- |
| `passed` | All required checks produced evidence meeting the pass condition for this revision | Yes |
| `failed` | Evidence shows a required condition is not met | No |
| `blocked` | A missing capability, permission, dependency, or external state prevents a required check or repair | No |
| `inconclusive` | Evidence exists but cannot support either pass or fail | No |
| `not_run` | A required or proposed check was not executed | No |
| `not_applicable` | The check was excluded before execution because it does not apply to this artifact | Only if every required check is otherwise satisfied |
| `accepted_risk` | A named human decision-maker explicitly accepts a stated unresolved risk for this revision | Yes, but never report it as `passed` |

Only the user or another identified, authorized human decision-maker may set
`accepted_risk`. A controller, implementer, reviewer, retry cap, schedule, or token
budget cannot create it. Preserve the finding, consequence, scope, revision, and
decision evidence whenever work advances under accepted risk.

## Run Cheap Oracles Before Judgment

Run deterministic checks that can decide the question before an inferential review:
tests, type checks, builds, parsers, native loaders, link/path checks, and consuming
commands. Use an independent reviewer where judgment materially reduces risk, not as
a substitute for an available oracle.

Independent review is normally worth its cost at these boundaries:

- an architectural or high-risk durable design document;
- a cross-component, long-running, or high-risk implementation plan;
- each subagent implementation task;
- a major or high-risk inline change and the final whole change.

Documentation, metadata, and simple configuration usually need proportionate
deterministic checks. If a review is optional and deliberately excluded, record it as
`not_applicable`; if it was required but unavailable, record `blocked` or
`not_run` rather than silently weakening the gate.

## Return to the Nearest Owner

| Failure | Return target |
| --- | --- |
| Failing behavior check or test | The task implementation; use systematic debugging when the cause is not known |
| Valid task-review finding | The task's focused fix loop, followed by a scoped re-review |
| Incomplete or contradictory plan | `writing-plans` at the affected task or interface |
| Requirement or design contradiction | `brainstorming` at the disputed decision |
| Integration-only failure | The integration step or affected implementation, not the whole project |
| Missing tool, permission, service, or external state | `blocked`; wait for changed capability or human action |
| Reviewer disagreement | Gather decisive evidence, clarify the requirement, or request human adjudication |

Preserve the last green checkpoint and already verified work. Backtracking is a
targeted state transition, not a restart and not recursive self-invocation.

## Retry With Changed Information

Every retry must change at least one of: the artifact, hypothesis, implementation,
evidence, context, evaluator, or available capability. Do not repeat an identical
deterministic command against an unchanged artifact, and do not tell the same
evaluator to “try harder” with unchanged inputs.

At the attempt cap:

1. Close a finding only when evidence demonstrates that it is invalid or outside the
   declared gate scope.
2. Route a valid unresolved finding to the nearest owner and record
   `decision_required` in prose alongside the gate's `failed` or `blocked` status.
3. Advance only after a new revision passes or a human explicitly records
   `accepted_risk` for the current revision.

Minor advisory observations may be deferred when they were never part of the pass
condition. A valid required finding never becomes `passed` merely because the retry
cap was reached.
