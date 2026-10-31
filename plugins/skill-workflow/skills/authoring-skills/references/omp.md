# omp authoring considerations

Use this reference when the authored skill is intended for omp. Adapt only the
parts the target project needs; omp is not the default for other skill work.

## Check the loading path

Read the target project's contributor and installation instructions, then use
[omp's skill documentation][skills] to check its discovery path. A skill loaded
from a conventional directory and one shipped in a portable Agent Plugins
package do not have identical metadata validation.

For a portable package with a standard root `plugin.json`, keep skills at
`skills/<name>/SKILL.md` and use the common Agent Skills frontmatter. Do not add
omp's `hide`, `globs`, or `alwaysApply`, or another client's extensions, merely
because a permissive scanner accepts them elsewhere. If the workflow needs a
manual command, file-scoped rule, or runtime enforcement, use the appropriate
omp component rather than assuming skill text or metadata supplies it.

Keep support files within the skill directory. omp can read them through
`skill://<name>/<relative-path>`; do not bake installation cache paths into the
skill. Retain ordinary relative references when no omp-specific URI is needed.

## Verify in the intended environment

Follow the target project's validation and installation procedure. For local
checks, use a temporary `HOME`, not the user's live installation. Inspect
`omp skill list` for the intended skill and warning lines; a readable file is
not proof of discovery. Exercise relevant requests separately to check actual
loading and behavior, and report any unverified behavior. Use the
`evaluating-skills` skill for output and trigger evaluations.

Marketplace catalog fields, versioning, and publication remain in the owning
project's procedures. Consult the [official marketplace guide][marketplaces]
only when that packaging work is in scope; do not copy it into every skill.

[skills]: https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md
[marketplaces]: https://github.com/can1357/oh-my-pi/blob/main/docs/skills/authoring-marketplaces.md
