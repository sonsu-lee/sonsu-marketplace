# Codex authoring considerations

Use this reference when the authored skill targets Codex. Follow the target
project's workflow and the current [Build skills guide][skills] for discovery,
invocation, and optional metadata rather than copying another client's setup.

## Add only required Codex adaptations

Keep the common `SKILL.md` format and start with instructions; add scripts only
when existing tools and instructions cannot reliably perform the required work.
Write a concise description with the key use case and triggers first, since
Codex may shorten descriptions in a large initial skills listing.

Consider `agents/openai.yaml` only when the workflow needs Codex-facing display
metadata, invocation policy, or tool dependencies. It is not required by the
common Agent Skills format. Consult the current guide before selecting fields;
do not generate branding, dependencies, or permission assumptions from guesses.

For plugin workflows, use the [plugin skill guide][plugins] to distinguish the
skill's decisions and output contract from live data, authorization, and
controlled actions owned by tools. General tool setup remains in its own docs.

## Respect plugin prompt-loading limits

Check the supported Codex version's actual loader limits, not just Agent Skills
format guidance. Codex CLI `0.163.0` limits an Agent Plugins skill's main prompt
to **8,000 UTF-8 bytes** in its [renderer][renderer] and applies truncation during
[host prompt injection][injection]. This is a version-specific plugin-loading
constraint, not a universal limit for standalone skills or other clients.

Measure the entire authored `SKILL.md` with `wc -c`, including frontmatter;
lines, characters, and tokens are not bytes. Leave room for future edits rather
than targeting the limit. If too large, remove unnecessary guidance first.
Keep essential decisions and safeguards in the main file; move conditional
detail to focused references and state when to read each. Do not hide required
instructions in an unreferenced file or load every reference unconditionally.
Recheck the actual loader when the supported Codex version changes.

## Verify the claimed support

Use the installed name returned by discovery for explicit invocation. Plugin
skills are qualified, for example `$skill-workflow:authoring-skills`; a bare
`$authoring-skills` does not select that installed plugin skill on `0.163.0`.
Inspect invocation events and the actual injected prompt to confirm the complete
main file, including its end, reaches the model without truncation or loading
warnings. File existence, `skills/list`, and format validation do not prove this.

Then exercise representative tasks, implicit selection, and nearby requests that
should not load the skill. Confirm required references are actually read, not
merely linked. The [evaluation guide][evals] explains trace inspection; verify
version-sensitive commands before reuse.

Reuse existing evaluation tools rather than requiring a new framework. A local
request capture can establish prompt loading without completing a model call,
but not reference following or task behavior. If authorized model access is
unavailable, report those checks as unverified. Do not claim Codex compatibility
from discovery, another client's run, or text-only review.

[skills]: https://learn.chatgpt.com/docs/build-skills
[plugins]: https://developers.openai.com/plugins/build/skills
[evals]: https://developers.openai.com/blog/eval-skills
[renderer]: https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/ext/skills/src/render.rs
[injection]: https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/ext/skills/src/host_prompt.rs
