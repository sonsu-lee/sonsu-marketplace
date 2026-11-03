# Claude Code execution

Read this reference only when controlling an ordinary plugin review in Claude
Code. Assigned custom reviewers read the common skill and their assignment
instead.

## Workflow

1. **Select the entry path.** An explicit native-only request keeps the native
   workflow without plugin orchestration. Never invoke `/code-review`, its
   `/review` alias, `/security-review`, or ultrareview as an internal worker,
   or launch another Claude Code CLI.
2. **Prepare the brief.** Freeze the target and prepare the shared brief as
   the common skill requires, using ordinary absolute paths. Workers start
   without this conversation or its invoked skills: give them the loaded
   `SKILL.md` by absolute path from the `Base directory for this skill:` line
   and state applicable constraints.
3. **Dispatch reviewers.** Start the general reviewer and at least one
   focused reviewer in Agent calls in one message, each with
   `subagent_type: "general-purpose"`. Small changes are not exempt.
   Never use `"fork"`, which inherits this conversation and is not independent,
   or the omp `review-workflow-focused` profile.
4. **Add skill-criteria coverage when required.** For standalone reviews,
   add a skill-criteria worker only on the user's explicit request. An
   authorized implementation controller may also assign it to satisfy
   `executing-work` or `authoring-skills` without a second user opt-in. The
   review controller dispatches it once in the same message with the shared
   brief, the installed `authoring-skills` `SKILL.md` absolute path, and one
   skill-guidance question. The worker uses that skill as criteria, not
   authoring checks. Report an unavailable skill as unmet coverage.
5. **Collect results.** Use each worker's full final result, not a launch
   acknowledgment. Do not sleep, poll, or schedule a wakeup while waiting;
   a wakeup replays the request in a later turn. A denied Agent tool or
   permission, concurrency limit, or stopped or truncated worker makes the
   review incomplete: report it instead of substituting a single-agent or
   native review.

Reference: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents).
