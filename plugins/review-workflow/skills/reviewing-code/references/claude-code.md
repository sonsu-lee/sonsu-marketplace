# Claude Code execution

Read this reference only when controlling an ordinary plugin review in Claude
Code. Assigned custom reviewers read the common skill and their assignment
instead.

## Keep entry paths separate

Do not invoke `/code-review`, its `/review` alias, `/security-review`, or
ultrareview as an internal worker, and do not launch another Claude Code CLI.
An explicit native-only request keeps the native workflow without plugin
orchestration.

## Prepare the target and brief

Freeze the target and prepare the shared brief as the common skill requires,
using ordinary absolute paths. Workers start without this conversation or its
invoked skills: give them the loaded `SKILL.md` by absolute path, from the
`Base directory for this skill:` line, and state applicable constraints.

## Dispatch and collect the reviewers

Start the general reviewer and at least one focused reviewer with Agent calls
in one message, each with `subagent_type: "general-purpose"`. Never use
`"fork"`: a fork inherits this conversation, so the reviewer is not independent.
Do not use the omp `review-workflow-focused` profile. A small change does not
exempt an ordinary plugin review from these workers.

For standalone reviews, add a skill-criteria worker only on the user's explicit
request. An authorized implementation controller may also assign it to satisfy
`executing-work` or `authoring-skills`, without a second user opt-in. The review
controller dispatches it once in the same message with the shared brief, the
installed `authoring-skills` `SKILL.md` absolute path, and one skill-guidance
question. It uses that skill as criteria, not authoring checks. Report an
unavailable skill as unmet coverage rather than omit the required review.

Use each worker's full final result, not a launch acknowledgment. Do not sleep,
poll, or schedule a wakeup while waiting; a wakeup replays the request in a
later turn.

A denied Agent tool, denied permissions, a concurrency limit, or a stopped or
truncated worker makes the review incomplete. Report that rather than
substituting a single-agent or native review.

Reference: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents).
