---
name: writing-prd
description: >-
  Synthesize an agreed discussion or specification into a product requirements
  draft, preserving decisions, constraints, scope, and observable outcomes.
  Drafting does not authorize publishing or changing a tracker.
---

# Writing a PRD

Distinguish a chat draft from an authorized file write or tracker publication.
Read the discussion, project context, relevant code, glossary, ADRs, and any
required template. Synthesize what is already established without conducting a
new interview; identify missing information as open rather than inventing it.
Use project vocabulary and distinguish facts from assumptions.

Describe the user problem, target users, desired solution and outcomes,
constraints and decisions, scope and exclusions, open questions, and observable
acceptance behavior. Preserve exact defaults, prohibitions, and original
requirements. Quote quantified constraints exactly when paraphrasing could
change their scope; check every restatement, including the problem and summary.
Do not strengthen a collective prohibition into a per-item requirement or
present an inferred interpretation as a decision. For example, forbidding all
sessions from merging into one does not by itself require unchanged session
counts or exact membership; leave additional constraints open unless agreed.
Record agreed implementation decisions where they affect the outcome, not
speculative paths or code.
Identify the highest useful
existing verification seam and relevant test precedents; propose a new seam only
when necessary. Do not invent metrics or a long list of formulaic stories.

Review the PRD and any derived ticket drafts against the source discussion:
requirements, defaults, prohibitions, decisions, and scope must remain intact.
Use `writing-tickets` for ticket format and tracker work if installed and
requested; absent that package, report the dependency rather than claiming it
was invoked. Neither a PRD request nor a skill invocation authorizes publishing.

Before a PRD becomes the input to an implementation plan, apply the
[plan readiness](references/plan-readiness.md) gate. A standalone draft may
list open questions; it is not plan input until that gate passes.

Assess user problem, requirements accuracy, scope, open questions and evidence,
and acceptance. Score applicable items 0, 1, or 2; record exclusions and reasons
and normalize to 10. Require 8/10 and verified requirements, authorization,
security, data safety, confirmed contracts, and stage evidence. Correct failures
and reevaluate up to three times, never without changes. If still unsuccessful,
report each score, mandatory conditions, evidence, and blockers. Wait rather
than retry when user decisions, permission, or access are required.
