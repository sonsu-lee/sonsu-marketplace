# Client skill loading

Use the installed client's skill interface. Codex plugin skills are
`$development:grilling` and `$development:domain-modeling`; Claude Code skills
are `/development:grilling` and `/development:domain-modeling`. In omp use the
exposed skill interface, such as `skill://grilling` and
`skill://domain-modeling`. For `grill-me`, use the same method for `grilling`.

If the client cannot invoke a nested skill, read the installed skill's actual
`SKILL.md` using its exposed path and apply it; identify that as reading, not an
invocation. If it is inaccessible, report the missing dependency. Metadata and
discovery do not prove automatic selection or full prompt loading.
