# Codex authoring considerations

Read this when the authored skill targets Codex. Follow the project's workflow
and the current [Build skills guide][skills].

1. **Keep the common format.** Start with instructions; add scripts only when
   tools and instructions cannot do the work. Put the key use case first in
   the description, since Codex may shorten long skill listings.
2. **Add Codex metadata only when needed.** Use `agents/openai.yaml` only for
   display metadata, invocation policy, or tool dependencies, choosing fields
   from the current guide. For plugin workflows, use the
   [plugin skill guide][plugins] to separate the skill's decisions from data,
   authorization, and actions owned by tools.
3. **Check the size.** Measure the whole `SKILL.md`, frontmatter included,
   with `wc -c`. Leave room below the limit; remove guidance before moving it.
4. **Verify loading.** Invoke the skill by its installed name and inspect the
   events and injected prompt to confirm the whole file, including its end,
   arrives without truncation or warnings.
5. **Verify behavior.** Exercise representative tasks, implicit selection,
   and nearby requests that should not load the skill. Confirm required
   references are actually read ([evaluation guide][evals]).

## Gotchas

- Codex CLI `0.163.0` limits a plugin skill's main prompt to **8,000 UTF-8
  bytes** ([renderer][renderer], [injection][injection]). This is a
  version-specific plugin limit; recheck it when the supported version changes.
- Bytes are not lines, characters, or tokens.
- Plugin skills are invoked qualified, such as
  `$skill-workflow:authoring-skills`; a bare `$authoring-skills` does not
  select the plugin skill on `0.163.0`.
- File existence, `skills/list`, and format validation do not prove loading.
- Codex ships no evaluation runner; use `evaluating-skills` or project tools.
  A local request capture proves loading, not behavior.
- Without authorized model access, report behavior as unverified. Never claim
  Codex support from another client's run or a text-only review.

[skills]: https://learn.chatgpt.com/docs/build-skills
[plugins]: https://developers.openai.com/plugins/build/skills
[evals]: https://developers.openai.com/blog/eval-skills
[renderer]: https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/ext/skills/src/render.rs
[injection]: https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/ext/skills/src/host_prompt.rs
