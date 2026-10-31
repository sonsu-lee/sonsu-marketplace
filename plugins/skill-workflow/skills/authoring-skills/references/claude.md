# Claude authoring considerations

Use this reference when the authored skill targets Claude. Establish whether
it is for Claude Code, a claude.ai upload, or the API before adding extensions;
these surfaces do not share every loading and execution feature.

## Separate common content from client features

Use the [Claude Code skills reference][code] for the intended deployment path.
Claude Code supports additional frontmatter and body features, such as
invocation controls, forked execution, and dynamic command injection. Do not
copy them into a portable skill or assume they work in claude.ai or the API.
The [cross-surface frontmatter guidance][portability] identifies which fields
those paths accept.

The [Claude authoring guide][authoring] recommends third-person descriptions
with clear capabilities and triggers. Treat this as authoring guidance, not a
new schema or a reason to mechanically rewrite descriptions that already work.
Keep the trigger in the metadata; body instructions load after selection.

Add client-specific behavior only when the requested workflow needs it and the
target surface supports it. Distinguish automatic skill loading from permission
to perform side effects; do not grant broad tool access merely for convenience.

Claude Code invokes plugin skills as `/<plugin>:<skill>` and prefixes the
injected body with `Base directory for this skill:`. A shared skill resolves
bundled files from that loaded directory, not a cache path.

## Verify the claimed support

Check discovery, activation, and task behavior on the intended surface and
models. For a Claude Code plugin, `claude plugin validate --strict` on its
`skills/` directory checks skill files; a marketplace run does not open them.
The `system` `init` event of `claude -p --output-format stream-json --verbose`
lists discovered skills before any model request. For complete loading, inspect
the injected body in an actual request. For output quality and activation in a
project without its own evaluation setup, use the
[skill-creator plugin][creator]
(`/plugin install skill-creator@claude-plugins-official`), which runs the Agent
Skills evaluation loops on `evals/evals.json`; `claude plugin eval` is a
separate tool with its own case format, and neither reads the other's files.
Do not claim Claude compatibility from an omp or Codex run or a text-only
review.

[code]: https://code.claude.com/docs/en/skills
[portability]: https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code
[authoring]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
