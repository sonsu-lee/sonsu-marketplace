# Repository guidance

## Code Review Rules

- Write the review summary and every inline review comment in Korean. Keep code identifiers,
  file paths, commands, log output, and quoted source text in their original form.

## Subagent Delegation

- For nontrivial work, the root agent identifies independently useful investigation,
  implementation, and review tasks. Assign eligible tasks to subagents in parallel when
  their results can be verified separately and the benefit exceeds coordination cost.
- Give each subagent a bounded goal, inputs, output, and read/write scope. Parallel writers
  use separate worktrees; the root agent integrates their results and verifies the final state.
- For recurring Engineering roles, select the matching project Codex agent in `.codex/agents/`
  only when that role is discoverable and selectable in the current project/session. Host support
  for named selection alone is insufficient because project configuration may not be loaded.
  Read `shared/agent-policy/profiles.json` and pass the role's model and reasoning effort at spawn
  unless the user specifies otherwise. Claude Code uses the matching packaged `engineering:<role>`
  agent. In both hosts, provide the concrete task brief at spawn time; a role name does not
  determine task count or file ownership. If the Codex role is unavailable or selection fails,
  read its definition and pass the role boundaries in the brief; report native role selection as
  unverified.
  A brief-only fallback does not apply the agent file's `sandbox_mode`; report the actual permission
  mode separately from the read-only instruction.
- Keep dependent work and shared writes sequential. When a task appears divisible but is
  handled directly, briefly state the concrete dependency or cost that prevented delegation.
- The root agent owns further assignments. A subagent returns requests for more workers to
  the root agent instead of delegating on its own.
