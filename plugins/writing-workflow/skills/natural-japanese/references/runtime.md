# Runner selection and failure handling

Read when a script run fails or prints warnings, when choosing `--genre` or the
runtime, or when asked about the upstream semantic experiment. Resource
resolution (`SKILL_DIR`, absolute filesystem paths, no guessed cache paths) is
defined in [the skill](../SKILL.md); all commands here use the same `SKILL_DIR`
and `TARGET`.

## Runner and genre

Choose `--genre tech`, `business`, or `essay` when known; omit it when
uncertain. Use the project's configured runtime when one exists; otherwise uv
uses the scripts' inline dependency declarations. Python imports resolve beside
the script, so no source checkout, development files, or corpus is needed.
Do not change project configuration, global installations, user settings, or
hooks to use this skill.

## Failures and manual review

If execution is unavailable, use [manual review](manual-checklist.md) and
disclose that no mechanical checks ran. A configured runner, dependency, input,
or script failure is not permission to silently switch to manual review or a
different runner. Report the failure and resolve its cause; if it remains
blocked, label any manual observations separately. Do not fabricate scores.

Findings return exit 0 even when numerous; input errors return nonzero. Read
stderr as well as JSON. A malformed baseline can produce an upstream warning
and omit comparison: do not claim convergence from such a result. Fix the
baseline rather than treating the warning as a successful comparison.

## No semantic experiment

The optional upstream semantic-model experiment is not shipped here. There is
no `exp` mode or automatic model download in this adaptation. A request for it
must explain that limitation, not silently relabel full review as experimental.
