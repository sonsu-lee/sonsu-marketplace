---
name: domain-modeling
description: >-
  Sharpen a project's domain model while discussing terminology or preparing
  a glossary or architecture decision record. Do not create or change files
  unless the user requested them or authorized them within implementation.
---

# Domain modeling

Read the project's glossary, glossary map, ADR conventions, and relevant code
when available. Identify the context involved, challenge terms that conflict
with the glossary, suggest precise terms for ambiguous concepts, and use
concrete scenarios to clarify relationships. Compare claims about behavior to
actual code and surface contradictions. Use the project's existing terminology
and conventions; ask when the right context or a consequential decision is
unclear.

A glossary holds domain language, not implementation details or a specification.
If no project convention applies, see [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md)
for single- and multi-context layouts. Write or update a glossary only when
explicitly requested or authorized within the implementation scope; otherwise
provide a draft in chat. Create files lazily, never merely because a term was
resolved. Apply the same authorization boundary to ADRs.

Absent project-specific criteria, offer an ADR only when a decision is hard
to reverse, surprising without context, and involves real alternatives and a
tradeoff. See [ADR-FORMAT.md](ADR-FORMAT.md); the project's location, format,
threshold, and lifecycle take precedence. When available, use `writing-adrs`
for a requested record. Do not claim another package is installed if it is not.

Assess purpose and scope, evidence, real alternatives, decided versus open
questions, and verifiability. Score each applicable item 0, 1, or 2; exclude
with reasons and normalize to 10. Require 8/10 and verified requirements,
authority, security, data safety, confirmed contracts, and stage evidence.
Fix failures and reevaluate up to three times, never without changes. If still
unsuccessful, report each score, mandatory conditions, evidence, and blockers.
Wait for a required user decision, access, or permission instead of retrying.
