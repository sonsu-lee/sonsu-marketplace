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

## Verify the claimed support

Check both explicit and implicit invocation in the intended Codex environment,
including nearby requests that should not load the skill. Exercise the task,
not just description matching. The [official evaluation guide][evals] explains
how to inspect execution traces and outputs; check current CLI documentation
before reusing version-sensitive example commands or installation paths.

Reuse a suitable existing evaluation setup. Treat the official skill-creator's
scaffolding scripts as implementation tools, not required parts of every skill.
Do not claim Codex compatibility from another client's run or a text-only review.

[skills]: https://learn.chatgpt.com/docs/build-skills
[plugins]: https://developers.openai.com/plugins/build/skills
[evals]: https://developers.openai.com/blog/eval-skills
