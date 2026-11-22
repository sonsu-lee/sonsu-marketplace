---
name: improving-codebase-architecture
description: >-
  Investigate architectural friction and compare concrete module-deepening
  opportunities when architecture improvement is requested. Not a general
  diff review and not permission to change code, documents, or glossary.
---

# Improving codebase architecture

Scope the exploration to the user's named area or, otherwise, recent change
hotspots. Read relevant glossary terms, ADRs, code and callers first. Use the
[design vocabulary](references/codebase-design.md): module, interface, depth,
seam, adapter, leverage and locality. Identify genuine friction, shallow
interfaces, scattered knowledge or coupled seams. Apply the deletion test:
would removing the module eliminate complexity or spread it to callers?

Compare concrete candidates with affected files, evidence, problem, possible
change, effects on locality, leverage and testability, and real tradeoffs. Mark
conflicts with an existing ADR only when there is evidence worth reconsidering.
Recommend a candidate without designing its full interface prematurely. Use the
[report guidance](references/html-report.md) if a visual report is requested;
creating a file or opening a browser requires the applicable authorization.
Otherwise present the comparison in the requested medium without creating files.

After the user selects a candidate, use `grilling` when available to explore
constraints, dependencies, interfaces and tests. Consult `domain-modeling` for
terminology if available. A discussion does not authorize editing the glossary,
writing an ADR, or implementing a candidate; report missing dependencies rather
than claiming an invocation. Respect the project's terms and decision lifecycle.

Assess purpose and scope, evidence, genuine alternatives, decided versus open
questions, and verifiability. Score applicable items 0, 1, or 2, record exclusions
and reasons, and normalize to 10. Require 8/10 and verified requirements,
authority, security, data safety, confirmed contracts, and stage evidence. Fix
failures and reevaluate up to three times, never without changes. If still
unsuccessful, report each score, mandatory conditions, evidence, and blockers.
Wait for required user decisions, permission, or access instead of retrying.
