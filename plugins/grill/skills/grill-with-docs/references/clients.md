# Client skill loading

| Client | Interview (required) | Domain modeling (optional) |
| --- | --- | --- |
| Claude Code Skill tool | `grill:grilling` | `development:domain-modeling` |
| Codex | `$grill:grilling` | `$development:domain-modeling` |
| omp read | `skill://grilling` | `skill://domain-modeling` |

If the client cannot invoke a nested skill, read its installed `SKILL.md` using
the exposed path. Distinguish reading from invocation. If `grilling` cannot be
loaded, report the missing interview dependency. If `domain-modeling` cannot
be loaded, follow the standalone procedure in the calling skill.
