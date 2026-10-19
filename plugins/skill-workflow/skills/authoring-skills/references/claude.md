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

## Verify the claimed support

Check discovery, activation, and task behavior on the intended surface and
models. When evaluating a Claude Code plugin, consider its
[official plugin evaluation tool][evals] before building a runner. Its case
format differs from the skill-creator plugin's format; use the documentation
for the tool actually selected. Do not claim Claude compatibility from an omp
run or a text-only review.

[code]: https://code.claude.com/docs/en/skills
[portability]: https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code
[authoring]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[evals]: https://code.claude.com/docs/en/plugin-evals
