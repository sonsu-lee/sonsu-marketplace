# omp authoring considerations

Read this when the authored skill targets omp.

1. **Check the loading path.** Read the project's contributor and install
   instructions, then [omp's skill documentation][skills]. Conventional skill
   directories and portable Agent Plugins packages validate metadata
   differently.
2. **Keep the portable layout.** In a package with a root `plugin.json`, keep
   skills at `skills/<name>/SKILL.md` with common Agent Skills frontmatter.
3. **Verify in a temporary `HOME`.** Follow the project's install procedure,
   then check `omp skill list` for the skill and for `warning:` lines.
   Exercise relevant requests separately to check loading and behavior.

## Gotchas

- Do not add omp's `hide`, `globs`, or `alwaysApply`, or another client's
  extensions, because a permissive scanner accepts them.
- Manual commands, file-scoped rules, and runtime enforcement need the
  matching omp component; skill text does not supply them.
- Support files stay inside the skill directory and are readable through
  `skill://<name>/<path>`. Never write installation cache paths into a skill.
- A readable file is not proof of discovery.
- Catalog fields, versioning, and publication belong to the owning project.
  Read the [marketplace guide][marketplaces] only when packaging is in scope.

[skills]: https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md
[marketplaces]: https://github.com/can1357/oh-my-pi/blob/main/docs/skills/authoring-marketplaces.md
