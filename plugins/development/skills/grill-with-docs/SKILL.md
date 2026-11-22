---
name: grill-with-docs
description: >-
  Interview the user about a plan or design while checking the repository's
  domain language and decisions. Use when repository domain documents matter;
  discussion alone does not authorize glossary or ADR changes.
---

# Grill with docs

Invoke `grilling` and `domain-modeling`; follow [client loading](references/clients.md)
for the current host. Treat a missing skill as a missing dependency, not as a
successful invocation. Research repository facts before asking and ask only
important unresolved decisions whose prerequisites are settled. Preserve the
user's scope: a design discussion or interview authorizes neither glossary nor
ADR writes. Provide a chat draft unless the user requested the file or its write
is authorized within implementation.

Assess purpose and scope, evidence, real alternatives, decided versus open
questions, and verifiability. Score applicable items 0, 1, or 2; record exclusions
and reasons and normalize to 10. Require 8/10 and verified requirements,
authorization, security, data safety, confirmed contracts, and stage evidence.
Fix supported failures and reevaluate no more than three times, not without a
change. If still unsuccessful, report each score, mandatory conditions, evidence,
and blockers. Wait for required user decisions, permission, or access.
