# Client execution

Read this only when coordinating delegation or independent review. The current
host's tool schema, permissions, and instructions are authoritative. Workers need
an explicit assignment and applicable constraints; do not assume they inherit
the conversation. Use available generic workers for implementation, testing,
or cleanup rather than inventing named agents. Never change persistent client
configuration to obtain delegation.

- **omp:** Use the exposed `task` interface and effective agent profiles.
  For a code-review controller, follow `reviewing-code`'s omp execution
  reference, including its native reviewer and skill-reviewer dispatch. For
  skill-only authoring without that controller, use `authoring-skills`' omp
  review procedure. Collect completed results, not spawn acknowledgments.
- **Codex:** Use the exposed subagent interface and its actual schema. For code
  review, the `reviewing-code` Codex reference describes fresh generic workers,
  independent context, and result collection. Skill-criteria review defaults to
  independent review for execution; explicitly assign it using
  `authoring-skills` criteria when the code-review controller does not already
  include it. Do not assume omp profile names or fields exist.
- **Claude Code:** Use the exposed Agent tool with appropriate generic workers.
  For code review, follow the `reviewing-code` Claude Code reference's independent
  general and focused workers. Skill-criteria review defaults to independent
  review for execution; explicitly assign it using `authoring-skills` criteria
  when the code-review controller does not already include it. Do not use a
  fork as an independent reviewer or assume omp profile names.

When a skill-criteria review is assigned in Codex or Claude Code, give the fresh
worker the installed `authoring-skills` SKILL.md absolute path, the change's
purpose, intended consumers, changed files, applicable requirements, and a
specific skill-guidance question. The integration owner owns this assignment if
there is no review controller; otherwise instruct the controller to include it
once. Reviewers do not edit or run authoring checks. If required delegation or
independence is unavailable, disclose the limitation; do not claim it happened.
