# Review comments

Read this reference when drafting review comments or explicitly asked to post
reviews. Ordinary local findings do not require loading it.

## Preserve the finding while improving the wording

Write to the developer about the code, not about the reviewer or the review
process. Name the relevant condition, its consequence, and the smallest
sufficient correction or required outcome. Include the precise location and
supporting evidence, with enough surrounding context to understand the issue.
For design concerns, explain a current responsibility or maintenance cost,
not a hypothetical future preference. Follow the repository's comment format
and disclosure rules; otherwise use plain, short prose.

Make intent legible without requiring stock labels or phrase templates:

- A **bug** states an evidenced defect and what needs to change. Do not soften
  a required fix into an optional suggestion or hide it in a rhetorical
  question. Keep any uncertainty about the trigger explicit.
- A **question** identifies a consequential uncertainty that source, callers,
  requirements, and existing discussion could not settle. Say which intent or
  behavior needs confirmation. Do not present an unverified bug as established.
- An **optional suggestion** acknowledges that the current approach is valid
  and names a concrete benefit. Mark it non-blocking; omit preference-only
  advice and unsolicited nits. A related existing issue is also non-blocking
  and belongs separately, not among defects introduced by this change.

Avoid vague adjectives such as "safe" or "cleaner" when the code condition is
more informative. Skip boilerplate headings, stock praise, and long preludes
unless the repository requires that structure. Do not add confidence scores to
comment prose or use them as evidence; preserve any required confidence and
correctness fields in the native review report. Do not fill finding quotas or
rewrite evidence to sound more certain or more polite.
Natural tone does not mean pretending to be human: never invent personal
runtime experience, identity, or independent verification. Preserve required
AI disclosure. When drafting or editing comment prose, also read the matching
language skill if listed; retain these review rules. Language guidance must
not change obligation, scope, uncertainty, technical facts, or evidence.

## Examples, not findings

These examples are invented. They illustrate wording, not findings in the
linked projects, mandatory phrases, or a claim that any check ran.

**Bug, with a confirmed requirement and traced call path:**

> With `readOnly` enabled, this branch still calls `saveSettings()`, so opening
> the preview overwrites the settings file. Skip the save on the read-only path;
> the preview needs to leave the file unchanged.

**Question, with intent still unresolved:**

> Is this frame selection meant to find the first user-authored frame? It now
> stops at the generated wrapper, which would change which location we show.

**Optional suggestion, when a current maintenance benefit is established:**

> Non-blocking: both branches build the same error message. Building it once
> after the branch would leave one place to update the wording. The current
> behavior is correct.

The first example asserts a traced side effect, not an executed reproduction.
If a runtime check actually ran, name the check and observed result separately.
Do not turn a merely suspected call path into that assertion.

## Local draft or explicit publication

Keep the result local unless the user explicitly authorizes remote posting.
A draft request authorizes local text only, not a remote pending review. Do
not modify source, apply suggestions, commit, push, approve, or submit
`REQUEST_CHANGES`. Publication uses `COMMENT` and only the requested scope;
permission to post one finding is not permission to post the entire report.

For an authorized GitHub review:

1. Re-read the PR head SHA and compare it with the frozen reviewed SHA. Read
   prior reviews and threads; deduplicate root causes and do not reopen settled
   decisions without new evidence. A moved head requires reconciliation with
   the new target before posting; do not attach stale findings to new lines.
2. Use the repository-required authenticated GitHub tool and inspect its schema.
   With GitHub MCP, use `pull_request_review_write` to create a pending review,
   `add_comment_to_pending_review` for inline comments, then
   `pull_request_review_write` to `submit_pending` with event `COMMENT`.
   Keep all authorized findings in one consolidated review, anchored to the
   reviewed revision. Do not reuse or submit an unrelated pending review.
   If the required tool is unavailable, retain the local draft and report the
   blocker rather than silently changing tools or claiming publication.
3. Check the head SHA again before submission. If it changed, stop submission
   and report any remote pending state already created. Do not automatically
   restart a review cycle or delete unrelated drafts.
4. Read back the resulting review and comments; report their links, submitted
   state, and any missing items. A timeout or ambiguous write response is not
   proof of failure: inspect remote state before any retry. Never blindly
   repeat a write, submit a partial review as complete, or claim success from
   an unconfirmed response. If remote state remains unknown, stop and say so.

## Public examples behind the guidance

These excerpts illustrate communication choices, not proof of a defect in a
new target or authority to impose the same implementation there:

- [toss/slash #21](https://github.com/toss/slash/pull/21#discussion_r991756463)
  replaces "안전하다" with specific environments where Web Storage is
  unavailable. Name the supported condition instead of a vague assurance.
- [vite #23744](https://github.com/vitejs/vite/pull/23744#discussion_r4268202745)
  explains that detection "starts eagerly on import instead of when we call
  it" and suggests retaining a function call. Tie the API choice to its
  timing effect, preserving the original comment's uncertainty.
- [vite #23741](https://github.com/vitejs/vite/pull/23741#discussion_r4269403491)
  asks whether the intent is "to find out the first user (authored) code".
  Confirm the specific purpose rather than asking a generic "why?" or
  asserting an unsupported defect.
