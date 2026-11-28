# Client execution

Read this only when coordinating delegation or independent review. The current
host's tool schema, permissions, and instructions are authoritative. Workers need
an explicit assignment and applicable constraints; do not assume they inherit
the conversation. Use available generic workers for implementation, testing,
or cleanup rather than inventing named agents. Never change persistent client
configuration to obtain delegation.

Assign a role by its work, not by a fictional persona or model name. Include
its scope, decision perspective, allowed actions, required context, output,
and limitations in the brief:

- Exploration traces actual entry points and callers and returns evidence and
  unknowns without editing.
- Implementation owns the authorized slice and reports changes and observed
  validation. Verify isolation preserves the required work and that its side
  effects are authorized before using it.
- General and focused reviewers independently assess the fixed target and
  report concrete impact and evidence without editing or publishing.
- Skill review applies authoring criteria to the assigned guidance question;
  runtime verification is a separate role that runs authorized scenarios in a
  disposable environment and reports observed results.

These are assignment contracts, not new always-on agents or permission
boundaries. A prompt cannot create a sandbox. Do not infer model identity,
review independence, or a successful run from the requested role.

- **omp:** Read installed skills using `skill://<name>`. Use exposed native
  task, todo and session facilities; an extension gate is not evidence of
  skill loading, verification or approval. Isolated workers may automatically
  apply changes, and branch merge mode may
  create commits; use them only when those effects and the baseline are
  authorized. For code and skill changes, follow `reviewing-code`'s omp
  execution reference: use its native reviewer with a focused worker. For a
  skill change add the skill reviewer, which is the focused worker when only
  skills changed. Collect completed results, not spawn acknowledgments.
- **Codex:** Select installed qualified plugin skills (`$<plugin>:<skill>`).
  Use the exposed subagent interface and its actual schema. For code
  review, the `reviewing-code` Codex reference describes fresh generic workers,
  independent context, and result collection. For skill changes, assign
  `authoring-skills` criteria through that controller. Do not assume omp
  profile names or fields exist.
- **Claude Code:** Invoke the Skill tool with the qualified plugin skill
  name. Use the exposed Agent tool with appropriate generic workers.
  Subagent worktrees normally start from the default branch and omit uncommitted
  files; their branch creation and cleanup need applicable authority. Verify
  baseline and effects before using them. For code review, follow the
  `reviewing-code` Claude Code reference's independent general and focused
  workers. For skill changes, assign `authoring-skills` criteria through that
  controller. Do not use a fork as an independent reviewer or assume omp
  profile names.

When a skill-criteria review is assigned in Codex or Claude Code, give the fresh
worker the installed `authoring-skills` SKILL.md absolute path, the change's
purpose, intended consumers, changed files, applicable requirements, and a
specific skill-guidance question. In authorized execution, instruct the review
controller to include it once; a separate assignment cannot replace a missing
required controller. Reviewers do not edit or run authoring checks. If required
delegation or independence is unavailable, report the review as incomplete.

If nested invocation is unsupported, read the installed skill file before
its materials; distinguish reading from invocation. If the file cannot be
loaded or a required worker cannot run, report that stage as incomplete.
Native-only means the requested native procedure and output, without plugin
workers, criteria, or claims that an integrated skill ran.
