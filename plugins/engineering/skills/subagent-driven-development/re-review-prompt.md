# 범위가 제한된 재리뷰 prompt template

수정 회차 뒤 재리뷰를 위임할 때 이 template을 사용한다. 재리뷰어는 finding이 해결됐는지
검증하고 수정 diff에 새 문제가 생겼는지 확인한다. 전체 리뷰는 이미 끝났으므로 새로운 리뷰가 아니다.

**목적:** 이전 리뷰의 각 finding을 해결했고 수정 자체가 다른 동작을 깨뜨리지 않았는지 검증한다.

```
Subagent (general-purpose):
  description: "Task N 수정 회차 R 재리뷰"
  model: [MODEL — 필수: SKILL.md의 Model Selection에 따라 선택한다. 생략하면
         session에서 가장 비싼 모델을 조용히 상속한다.]
  prompt: |
    한 task의 수정 회차를 재리뷰한다. 이전 리뷰에서 finding이 나왔고 implementer가 수정을
    시도했다. 각 finding을 판정하고 수정 diff만 검사한다. 다른 작업은 하지 않는다.

    ## Task

    task brief를 읽는다: [BRIEF_FILE]

    ## 검증할 finding

    [FINDINGS]

    ## 수정 내용

    implementer의 report를 읽는다(수정 보고는 끝에 추가된다).
    [REPORT_FILE]

    **수정 base:** [FIX_BASE_SHA] (이전 리뷰에서 확인한 head)
    **Head:** [HEAD_SHA]
    **Diff 파일:** [DIFF_FILE]

    diff 파일을 한 번 읽는다. 이 파일에는 수정 commit, stat 요약과 주변 context를 포함한
    수정 diff가 들어 있다. git 명령을 다시 실행하지 않는다. diff 파일이 없으면 직접 가져온다.
    `git diff --stat [FIX_BASE_SHA]..[HEAD_SHA]` and
    `git diff [FIX_BASE_SHA]..[HEAD_SHA]`.

    현재 checkout에서 리뷰는 읽기 전용이다. working tree, index, HEAD 또는 브랜치 상태를
    어떤 방식으로도 변경하지 않는다.

    ## Subagent를 위임하지 않는다

    이 리뷰는 모두 직접 수행한다. diff 일부를 리뷰하도록 subagent를 생성하지 않고, 두 번째
    의견을 위해 다른 reviewer도 생성하지 않는다. 이 process에는 이 작업에 필요한 모든 리뷰
    자리가 이미 포함되어 있다. 직접 생성한 reviewer는 전체 비용으로 기존 자리를 중복하며 그
    판정은 반영되지 않는다. diff가 한 번에 리뷰하기에 너무 크다면 직접 여러 차례로 나누어
    리뷰하고 report에 그 사실을 밝힌다.

    ## 범위

    범위는 finding 목록과 수정 diff다. 모든 finding을 판정한다. 수정 자체가 만든 새 문제가
    있는지 수정 diff를 검사한다. 수정에서 건드리지 않은 코드를 다시 리뷰하지 않는다. 수정
    diff 밖의 문제를 발견하면 범위 밖 관찰에 보고한다. 이 항목은 task를 막거나 loop를
    확장하지 않는다. 모든 task가 완료된 뒤 전체 브랜치를 대상으로 넓은 리뷰를 수행한다.

    ## 검증

    implementer는 변경된 작업을 다루는 집중 검증을 다시 실행하고 결과를 report 파일에
    추가했다. report는 검증되지 않은 주장으로 취급한다. 수정 보고에 검사 이름과 출력이 있는지
    확인하고 주장을 diff와 대조한다. report를 확인하려고 같은 검증을 반복하지 않는다. diff를
    읽다가 기존 근거로 답할 수 없는 구체적인 의문이 생긴 경우에만 명령을 실행하며, 관련 없는
    package 전체 suite가 아니라 집중된 검사를 사용한다.

    ## 출력 형식

    final message가 report 자체다. 첫 finding의 판정부터 바로 시작한다. 모든 줄은 판정,
    `file:line`이 있는 finding 또는 실행한 검사여야 한다. 서문이나 process 설명은 쓰지 않는다.

    ### Finding 판정

    검증할 finding의 각 항목을 순서대로 판정한다.
    - **[finding 한 줄 요약]** — ADDRESSED | NOT ADDRESSED와 `file:line` 근거.
      "Attempted"는 해결이 아니다. 해당 결함이 더 이상 존재하지 않아야 한다.

    ### 수정 diff의 새 문제

    수정 자체가 깨뜨리거나 새로 만든 문제를 심각도(Critical/Important/Minor), `file:line`과
    함께 적는다. 문제가 없으면 "None"이라고 쓴다.

    ### 범위 밖 관찰

    수정 diff 밖에서 발견한 문제다. task를 막지 않으며 controller가 최종 리뷰를 위해 ledger에
    기록한다. 없으면 "None"이라고 쓴다.

    ### 판정

    **수정 회차:** [All findings addressed, no new Critical/Important
    breakage | Findings remain open] — 남은 항목을 나열한다.
```

**치환할 placeholder:**
- `[MODEL]` — 필수: SKILL.md의 Model Selection에 따른 reviewer 모델. 작은 수정 diff의 범위가 제한된 재리뷰에는 저가에서 중간 tier를 사용한다.
- `[BRIEF_FILE]` — task brief 파일(implementer가 작업한 파일과 동일)
- `[FINDINGS]` — 이전 리뷰의 Critical/Important finding과 spec 공백을 불릿마다 하나씩 그대로 복사
- `[REPORT_FILE]` — implementer의 report 파일(수정 보고가 추가됨)
- `[FIX_BASE_SHA]` — 이전 리뷰에서 확인한 head
- `[HEAD_SHA]` — 현재 commit
- `[DIFF_FILE]` — `scripts/review-package PLAN_FILE FIX_BASE HEAD`가 출력한 경로

**Re-reviewer 반환값:** finding별 판정(ADDRESSED / NOT ADDRESSED), 수정 diff의 새 문제,
범위 밖 관찰과 회차 판정.
