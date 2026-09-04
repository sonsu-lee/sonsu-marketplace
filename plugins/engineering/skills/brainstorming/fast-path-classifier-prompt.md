# Fast Path classifier prompt

Fast Path eligibility는 controller의 자기 판정으로 통과시키지 않는다. controller는 대상 탐색 전에
stable todo ID를 사용하거나, stable todo ID가 없으면 UUID를 **한 번만** 생성한다. 이 ID는 target에서
다시 유도하지 않으며 task 전체의 모든 handoff에 state-file path와 함께 전달한다. production state
root는 repository의 `.engineering/fast-path`다.

## Dispatch contract

classifier는 fresh context의 `gpt-5.6-luna` / `low` 한 슬롯이다. Fast Path 기본 경로에서 만들 수
있는 유일한 subagent이며 implementation 또는 reviewer subagent를 추가로 만들지 않는다.

classifier에게 주는 brief의 입력은 다음 다섯 항목뿐이다.

1. request
2. target
3. controller evidence
4. proposed deterministic oracle
5. unknowns

repository root는 한 번의 독립 표적 탐색을 실행할 working directory일 뿐, 이전 plan, implementer
report, rationale, self-review, classifier verdict, session history를 전달하는 입력이 아니다.

## Classifier instruction

```text
You are the independent Fast Path classifier.

Use fresh context and gpt-5.6-luna with low reasoning effort. You receive only:
- request
- target
- controller evidence
- proposed deterministic oracle
- unknowns

Run exactly one independent targeted repository search for the target's references or consumers.
Do not perform a code review, red-team review, implementation, retry, or a second search.
The controller search plus this search is the entire Fast Path search budget: two searches.

Return exactly one verdict: eligible | escalate | inconclusive | blocked.
Return a short evidence digest and the exact candidate revision. `eligible` is allowed only when every
Fast Path predicate is proven, the deterministic oracle is adequate, and no hidden-risk signal exists.
If a predicate is false or unknown, a consumer cannot be closed, the oracle is inadequate, the repository
cannot be searched, or execution is blocked, return a non-eligible verdict. Do not guess a pass.
```

## Controller routing

Before **every** Fast Path entry, capture the repository's exact current commit revision, then run the
revision-bound state check. The stable task ID is still created before target discovery and must never be
re-derived from the target.

```bash
STATE_ROOT="$REPOSITORY_ROOT/.engineering/fast-path"
TASK_ID=<stable-todo-id-or-uuid-created-once-before-target-discovery>
STATE_FILE="$STATE_ROOT/$TASK_ID.state"
CANDIDATE_REVISION=$(git -C "$REPOSITORY_ROOT" rev-parse --verify 'HEAD^{commit}')
plugins/engineering/skills/brainstorming/scripts/fast-path-state check "$STATE_ROOT" "$TASK_ID" "$CANDIDATE_REVISION"
```

`disqualified` rejects Fast Path without calling the classifier, predicate, or execution. `eligible` only
matches when its stored candidate revision is exactly `CANDIDATE_REVISION`; a missing expected revision or a
mismatch fails closed. For an
`unclassified` task, the controller performs its one targeted search, builds the five-field brief, and
dispatches the classifier once. Record an eligible verdict only with the exact candidate revision and
classifier evidence digest. The classifier's returned revision must match the controller-captured
`CANDIDATE_REVISION`, and `EVIDENCE_DIGEST` is a 64-character lowercase SHA-256 hex digest:

```bash
plugins/engineering/skills/brainstorming/scripts/fast-path-state record "$STATE_ROOT" "$TASK_ID" eligible "$CANDIDATE_REVISION" "$EVIDENCE_DIGEST"
```

For `escalate`, `inconclusive`, `blocked`, unavailable classifier capability, or any other non-eligible
outcome, record the irreversible latch before routing:

```bash
plugins/engineering/skills/brainstorming/scripts/fast-path-state record "$STATE_ROOT" "$TASK_ID" disqualified "$REASON" "$EVIDENCE_DIGEST"
```

Then route to the nearest normal workflow: unexplained failure to `engineering:systematic-debugging`,
multi-flow or interface work to `engineering:writing-plans`, and requirement or design change to
`engineering:brainstorming`. Every escalation handoff includes `TASK_ID` and `STATE_FILE`. A latched task
never re-enters Fast Path classification, predicates, or execution, including after context compaction.
