# Plan 문서 reviewer prompt template

plan 문서 reviewer subagent를 위임할 때 이 template을 사용한다.

**목적:** plan이 완전하고 승인된 요구사항 출처와 일치하며 task 분해와 권한 경계가 적절한지 검증한다.

**위임 시점:** 전체 plan을 작성했고 독립 리뷰가 구현 위험을 실질적으로 줄일 수 있을 때.

```
Subagent (general-purpose):
  description: "Plan 문서 리뷰"
  model: [MODEL — 필수: architecture/plan 역할에 맞게 선택한다.]
  reasoning_effort: [REASONING_EFFORT — 필수: architecture/plan 역할에 맞게 선택한다.]
  prompt: |
    당신은 plan 문서 reviewer다. 이 plan이 완전하고 구현할 준비가 됐는지 검증한다.

    **리뷰할 plan:** [PLAN_FILE_PATH]
    **요구사항 출처:** [REQUIREMENTS_SOURCE]

    ## 확인할 내용

    | 분류 | 확인할 내용 |
    |----------|------------------|
    | 완전성 | TODO, placeholder, 불완전한 task, 빠진 단계 |
    | 요구사항 정합성 | 큰 scope creep 없이 승인된 요구사항을 plan이 다루는가 |
    | 순서 | 구현 세부사항, 파일별 단계와 검증 선택보다 의사코드가 먼저 작성됐는가 |
    | 의사코드 | 필요한 입력, 결과, 처리 흐름, 상태 변화, 분기·반복, 오류·경계, 책임 경계와 미확인 가정을 검토 가능한 수준으로 설명하는가 |
    | 추적성 | 각 의사코드 flow가 변경 파일, task, dependency와 검증에 연결되고 각 task에서 flow ID를 추적할 수 있는가 |
    | Task 분해 | task 경계가 명확하고 의사코드 흐름에서 실행 단계를 도출했는가 |
    | 구현 가능성 | engineer가 막히지 않고 이 plan을 따를 수 있는가 |
    | 검증 | 의사코드 뒤에 TDD 또는 다른 검증 방법을 선택했고, 각 task에 선택 이유가 있는가 |
    | 승인 | 승인된 요구사항·설계·관찰 가능한 계약을 바꾼 plan 리비전에 사용자의 명시적인 재승인 근거가 있는가. plan-readiness gate를 승인으로 취급하지 않았는가 |
    | 기존 작업 | plan 리비전이 영향을 받는 완료 task를 식별하고 reopened 및 재검증 대상으로 표시했는가 |
    | 완료 게이트 | plan-backed 작업의 일반 최종 리뷰 뒤 fresh-context red-team completion gate와 반환 경로가 있는가 |
    | 문서 | plan이 승인된 문서 영향과 일치하는가 |
    | 권한 | commit과 외부 작업이 현재 permission을 넘지 않는가 |

    ## 판정 보정

    **구현 중 실제 문제를 일으킬 항목만 보고한다.**
    implementer가 잘못된 대상을 만들거나 막히게 하는 내용은 문제다.
    사소한 문구, style 선호와 "nice to have" 제안은 문제가 아니다.

    승인된 요구사항 누락, 서로 모순되는 단계, placeholder 내용 또는 실행할 수 없을 만큼
    모호한 task처럼 심각한 공백이 없다면 승인한다.

    ## 출력 형식

    ## Plan 리뷰

    **Status:** Approved | Issues Found

    **Issues(있는 경우):**
    - [Task X, Step Y]: [구체적인 문제] - [구현에 중요한 이유]

    **Recommendations(권고 사항이며 승인을 막지 않음):**
    - [개선 제안]
```

**Reviewer 반환값:** Status, Issues(있는 경우), Recommendations
