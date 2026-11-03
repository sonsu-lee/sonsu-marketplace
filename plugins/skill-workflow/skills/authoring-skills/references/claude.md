# Claude authoring considerations

Read this when the authored skill targets Claude. First establish the surface:
Claude Code, a claude.ai upload, or the API. They do not share every feature.

1. **Separate common content from client features.** Claude Code adds
   frontmatter and body features such as invocation controls, forked
   execution, and dynamic command injection ([skills reference][code]). Use
   them only when the workflow needs them and the surface supports them; the
   [cross-surface guidance][portability] lists which fields each path accepts.
2. **Write the description** with clear capabilities and triggers, in the
   third person per the [authoring guide][authoring]. Do not rewrite working
   descriptions just to match it.
3. **Verify discovery.** For a Claude Code plugin, run
   `claude plugin validate --strict` on its `skills/` directory. The `system`
   `init` event of `claude -p --output-format stream-json --verbose` lists
   discovered skills before any model request.
4. **Verify loading and behavior.** Inspect the injected body in an actual
   request. For output quality and activation, use the
   [skill-creator plugin][creator]
   (`/plugin install skill-creator@claude-plugins-official`) unless the
   project has its own setup.

## Gotchas

- Triggers belong in the metadata; the body loads only after selection.
- Automatic loading is not permission for side effects. Do not grant broad
  tool access for convenience.
- Claude Code invokes plugin skills as `/<plugin>:<skill>` and prefixes the
  body with `Base directory for this skill:`. Resolve bundled files from that
  directory, not a cache path.
- A marketplace validation run does not open skill files.
- `claude plugin eval` uses its own case format; it and skill-creator do not
  read each other's files.
- Never claim Claude support from an omp or Codex run or a text-only review.

[code]: https://code.claude.com/docs/en/skills
[portability]: https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code
[authoring]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
