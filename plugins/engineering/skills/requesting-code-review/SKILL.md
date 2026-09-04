---
name: requesting-code-review
description: task를 완료할 때, 주요 기능을 구현한 뒤 또는 merge 전에 작업이 요구사항을 충족하는지 검증하기 위해 사용한다
---

# requesting-code-review: 코드 리뷰 요청

문제가 다음 작업으로 번지기 전에 발견하도록 code reviewer subagent를 위임한다. reviewer에게는 평가에 맞춰 정확히 구성한 context만 제공하고 session history는 전달하지 않는다.

**핵심 원칙:** 일찍, 자주 리뷰한다.

공통 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 읽는다.
리뷰는 선언한 하나의 artifact 리비전에 대한 근거이며 이후 수정까지 포괄적으로 승인하지 않는다.

## 리뷰 요청 시점

**필수:**
- subagent-driven development의 각 task 이후
- 주요 기능 완료 이후
- main merge 이전

**선택 사항이지만 유용한 경우:**
- 막혔을 때(새로운 관점)
- refactoring 전(baseline 확인)
- 복잡한 버그 수정 후

## 요청 방법

**1. 리뷰 artifact와 리비전을 고정한다.**
```bash
BASE_SHA=<the task base or verified merge base>
HEAD_SHA=$(git rev-parse HEAD)
./scripts/review-package range "$BASE_SHA" "$HEAD_SHA"
```

여러 commit으로 구성된 task에 `HEAD~1`을 기본값으로 사용하지 않는다. task 전에 기록한 base
또는 검증한 브랜치 merge base를 사용한다. 스크립트는 package 경로와 SHA-256 리비전을
출력하므로 둘 다 기록해 reviewer에게 전달한다. 이 스킬 디렉터리에서
`./scripts/review-package`를 실행한다.

승인된 artifact가 아직 commit되지 않았다면 전체 working tree를 대신 고정한다.

```bash
./scripts/review-package working-tree
```

이 mode는 tracked, staged, untracked 변경을 포함하며 빈 working tree는 거부한다. package는
저장소 밖에 생성되어 자신을 `diff`에 추가하지 않는다. digest만으로 artifact를 식별할 수는
있지만 reviewer가 내용을 검사할 수 없으므로 읽을 수 있는 package 경로도 항상 전달한다.

**2. Code reviewer subagent를 위임한다.**

[code-reviewer.md](code-reviewer.md)의 template을 채워 `general-purpose` subagent를 위임한다.

**치환할 placeholder:**
- `{MODEL}` - 역할과 위험에 맞는 모델
- `{REASONING_EFFORT}` - 역할과 위험에 맞는 추론도
- `{DESCRIPTION}` - 구현한 내용의 짧은 요약
- `{PLAN_OR_REQUIREMENTS}` - 기대 동작
- `{REVIEW_PACKAGE}` - `scripts/review-package`가 출력한 변경할 수 없는 package 경로
- `{REVIEW_REVISION}` - 해당 package에 대해 출력된 SHA-256 리비전

**3. 피드백에 대응한다.**
- Critical 문제를 즉시 수정한다.
- 진행하기 전에 Important 문제를 수정한다.
- Minor 문제는 나중에 처리하도록 기록한다.
- reviewer가 틀렸다면 근거를 들어 반박한다.
- 변경된 리비전에서 집중 수정 부분을 다시 리뷰한다.

리뷰 게이트의 artifact, 리비전, 근거, finding, 상태, 반환 대상, 시도 횟수와 decision owner를 기록한다. 필수 판정이 빠진 reviewer 보고서는 `inconclusive`다. 필수 reviewer를 사용할 수 없으면 `blocked` 또는 `not_run`을 사용하며 implementer의 자체 리뷰나 변경 없는 재시도로 대신하지 않는다. 기술적으로 반증된 finding은 근거와 함께 닫을 수 있다. 유효한 미해결 필수 finding은 workflow가 진행되기 전에 artifact 변경 또는 사람의 명시적인 `accepted_risk`가 필요하다.

## Plan-backed red-team completion review

일반 코드 리뷰가 끝난 plan-backed 작업에는 [red-team-reviewer.md](red-team-reviewer.md)를 사용해
별도의 completion gate를 수행한다. Fast Path처럼 plan이 없는 작업에는 적용하지 않는다.

- reviewer는 이전 implementer·reviewer와 다른 fresh context에서 시작하며 이전 session history,
  판정, 칭찬 또는 finding을 전달받지 않는다.
- 원래 목표, 승인된 요구사항·설계, plan 의사코드·mapping, immutable review package와 digest,
  결정론적 검증 report, 실제 관찰 결과와 알려진 제약의 읽기 전용 경로만 전달한다.
- 일반 리뷰를 반복하지 않고 문제 정의부터 검증까지 전체 연결을 부정하는 가장 강한 반례를 찾는다.
- 판정은 정확히 `survives_challenge`, `invalidated`, `inconclusive`, `blocked` 중 하나다.
  `survives_challenge`만 일반 통과로 취급한다.
- `invalidated` finding은 design, plan, implementation 또는 verification의 실제 소유 단계로
  돌려보낸다. 새 artifact를 다시 검토할 때에는 새 fresh-context reviewer를 사용하며 변경 없는
  재시도는 하지 않는다. 자동 시도는 최대 3회다.
- reviewer를 사용할 수 없거나 필요한 evidence가 없으면 `not_run`, `blocked` 또는
  `inconclusive`를 그대로 기록한다. 일반 reviewer의 승인을 red-team 통과로 대체하지 않는다.

## 예시

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=<recorded Task 2 base>
HEAD_SHA=$(git rev-parse HEAD)
./scripts/review-package range "$BASE_SHA" "$HEAD_SHA"

[Script returns]:
  Package: /tmp/engineering-review.ABC123.diff
  Revision: sha256:012345...

[Dispatch code reviewer subagent]
  MODEL: <role-appropriate model>
  REASONING_EFFORT: <role-appropriate effort>
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from .superpowers/plans/deployment-plan.md
  REVIEW_PACKAGE: /tmp/engineering-review.ABC123.diff
  REVIEW_REVISION: sha256:012345...

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## 자주 하는 합리화

| 변명 | 실제 |
|--------|---------|
| "I'll just review the diff myself instead of dispatching a reviewer" | 자신은 coordinator다. `diff`를 직접 리뷰하면 작업을 계속 이끄는 데 필요한 context window를 소모한다. reviewer subagent를 위임하면 `diff`와 평가는 해당 context에 남고 finding만 돌아온다. |
| "The reviewer needs my whole session history to understand the change" | session history가 아니라 정확히 구성한 context를 전달한다. 그러면 reviewer가 사고 과정이 아닌 작업 산출물에 집중한다. |

## 위험 신호

**다음 행동은 하지 않는다.**
- "it's simple"이라는 이유로 리뷰를 생략한다.
- Critical 문제를 무시한다.
- Important 문제를 수정하지 않고 진행한다.
- 유효한 기술 피드백을 부정한다.

**reviewer가 틀렸다면 다음과 같이 대응한다.**
- 기술적 근거를 들어 반박한다.
- 동작을 증명하는 코드와 테스트를 제시한다.
- 명확화를 요청한다.

template은 [code-reviewer.md](code-reviewer.md)를 참고한다.
