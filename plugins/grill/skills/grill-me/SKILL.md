---
name: grill-me
description: >-
  Interview the user to sharpen a plan, idea, or draft when important questions
  about its audience, purpose, or central claim remain. Do not use for a clear
  request for spelling or routine wording corrections.
---

# Grill me

Load `grilling` and run a file-free interview. In Claude Code, call the Skill
tool with `grill:grilling`; in Codex, use `$grill:grilling`; in omp, read
`skill://grilling`. If nested invocation isn't available, read the installed
`grilling/SKILL.md` through the client's exposed path. Report an inaccessible
skill rather than claiming it ran.

For a draft, start with unresolved questions about its audience, purpose, or
central claim. An interview does not require a repository or authorize writes.
