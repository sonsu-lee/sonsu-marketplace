# 영속 설계 문서 reviewer prompt template

spec 문서 reviewer subagent를 위임할 때 이 template을 사용한다.

**목적:** 승인된 영속 설계 문서가 완전하고 일관되며 구현 계획을 작성할 준비가 됐는지 검증한다.

**위임 시점:** 영속 설계 문서를 만들거나 크게 갱신했고 독립 리뷰가 계획 위험을 실질적으로 줄일 수 있을 때.

```
Subagent (general-purpose):
  description: "Spec 문서 리뷰"
  model: [MODEL — 실제 schema가 두 override를 모두 지원할 때 architecture/design 역할에 맞게 선택한다.]
  reasoning_effort: [REASONING_EFFORT — model과 함께 지원될 때 역할에 맞게 선택한다.]
  prompt: |
    당신은 설계 문서 reviewer다. 이 문서가 완전하고 plan을 작성할 준비가 됐는지 검증한다.

    **리뷰할 문서:** [DOCUMENT_FILE_PATH]

    ## 확인할 내용

    | 분류 | 확인할 내용 |
    |----------|------------------|
    | 완전성 | TODO, placeholder, "TBD", 불완전한 섹션 |
    | 일관성 | 내부 모순, 충돌하는 요구사항 |
    | 명확성 | 잘못된 구현을 만들 수 있을 만큼 모호한 요구사항 |
    | 범위 | 서로 독립적인 여러 subsystem을 다루지 않고 하나의 plan에 집중됐는가 |
    | YAGNI | 요청하지 않은 기능, over-engineering |

    ## 판정 보정

    **구현 계획을 작성할 때 실제 문제를 일으킬 항목만 보고한다.**
    빠진 섹션, 모순 또는 두 가지 방식으로 해석될 만큼 모호한 요구사항은 문제다. 사소한 표현
    개선, style 선호와 "다른 섹션보다 덜 상세함"은 문제가 아니다.

    잘못된 plan으로 이어질 심각한 공백이 없다면 승인한다.

    ## 출력 형식

    ## Spec 리뷰

    **Status:** Approved | Issues Found

    **Issues(있는 경우):**
    - [Section X]: [구체적인 문제] - [plan에 중요한 이유]

    **Recommendations(권고 사항이며 승인을 막지 않음):**
    - [개선 제안]
```

**Reviewer 반환값:** Status, Issues(있는 경우), Recommendations
