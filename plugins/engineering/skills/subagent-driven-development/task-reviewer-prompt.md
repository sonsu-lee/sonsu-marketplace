# Task reviewer prompt template: task 리뷰어 프롬프트 템플릿

task reviewer subagent를 위임할 때 이 template을 사용한다. reviewer는 task의 diff를 한 번
읽고 spec 준수 여부와 코드 품질의 두 가지 판정을 반환한다.

**목적:** 한 task의 구현이 요구사항과 정확히 일치하고 과하거나 부족한 부분이 없으며, 깔끔하고
적절히 검증되고 유지보수 가능하게 구현됐는지 확인한다.

```
Subagent (general-purpose):
  description: "Task N 리뷰(spec + quality)"
  model: [MODEL — 필수: SKILL.md의 Model Selection에 따라 선택한다. 생략하면
         session에서 가장 비싼 모델을 조용히 상속한다.]
  prompt: |
    한 task의 구현을 리뷰한다. 먼저 요구사항과 일치하는지, 그다음 적절하게 구현됐는지
    확인한다. 이것은 task 범위의 게이트이며 merge 리뷰가 아니다. 모든 task가 완료된 뒤
    전체 브랜치를 대상으로 하는 넓은 리뷰를 별도로 수행한다.

    ## 요청 내용

    task brief를 읽는다: [BRIEF_FILE]

    이 task에 적용되는 spec/design의 전역 제약:
    [GLOBAL_CONSTRAINTS]

    ## Implementer가 구현했다고 주장하는 내용

    implementer의 report를 읽는다: [REPORT_FILE]

    ## 리뷰할 diff

    **Base:** [BASE_SHA]
    **Head:** [HEAD_SHA]
    **Diff 파일:** [DIFF_FILE]

    diff 파일을 한 번 읽는다. 이 파일에는 commit 목록, stat 요약과 주변 context를 포함한 전체
    diff가 들어 있으며, 이것이 변경을 보는 기준이다. diff의 context line이 곧 변경된 파일이다.
    판정해야 할 hunk가 함수 중간에서 잘린 경우가 아니라면 변경 파일을 별도로 읽지 않는다.
    별도로 읽었다면 report에 그 사실을 밝힌다. git 명령을 다시 실행하지 않는다. diff 파일이
    없으면 직접 가져온다.
    `git diff --stat [BASE_SHA]..[HEAD_SHA]` and `git diff [BASE_SHA]..[HEAD_SHA]`.
    더 넓은 codebase를 탐색하지 않는다. 이름을 붙일 수 있는 구체적인 위험을 평가할 때에만
    diff 밖의 코드를 검사한다. 위험마다 집중된 검사를 하나씩 수행하고 report에 위험과 확인한
    내용을 모두 적는다. cross-cutting 변경은 유효한 명시적 위험이다. diff가 lock 순서, 함수나
    API 계약 또는 공유 mutable state를 바꾼다면 call site를 확인하는 것이 올바른 방법이다.

    현재 checkout에서 리뷰는 읽기 전용이다. working tree, index, HEAD 또는 브랜치 상태를
    어떤 방식으로도 변경하지 않는다.

    ## Subagent를 위임하지 않는다

    이 리뷰는 모두 직접 수행한다. diff 일부를 리뷰하도록 subagent를 생성하지 않고, 두 번째
    의견을 위해 다른 reviewer도 생성하지 않는다. 이 process에는 이 작업에 필요한 모든 리뷰
    자리가 이미 포함되어 있다. 직접 생성한 reviewer는 전체 비용으로 기존 자리를 중복하며 그
    판정은 반영되지 않는다. diff가 한 번에 리뷰하기에 너무 크다면 직접 여러 차례로 나누어
    리뷰하고 report에 그 사실을 밝힌다.

    ## Report를 신뢰하지 않는다

    implementer의 report를 코드에 대한 검증되지 않은 주장으로 취급한다. 불완전하거나 부정확하거나
    낙관적일 수 있다. 주장을 diff와 대조해 검증한다. report의 설계 근거도 주장이다. "left it
    per YAGNI", "kept it simple deliberately" 또는 다른 정당화는 implementer가 자신의 작업을
    스스로 채점하는 것이다. 코드는 자체 품질을 기준으로 판정하며, 명시된 근거가 finding의
    심각도를 낮추지는 않는다.

    ## 검증

    implementer는 task에 지정된 검증을 이미 실행하고 결과를 보고했다. TDD 근거는 task가
    production 동작을 바꾸고 plan에서 TDD를 선택한 경우에만 필요하다. report를 확인하기 위해
    같은 검사를 반복하지 않는다. diff를 읽다가 기존 근거로 답할 수 없는 구체적인 의문이 생긴
    경우에만 명령을 실행한다. 이때 관련 없는 package 전체 suite, race detector 실행 또는 높은
    횟수의 반복 loop가 아니라 집중된 검사를 사용한다. 더 무거운 검증이 필요해 보이면 직접
    실행하지 말고 report에서 권고한다. 현재 환경에서 명령을 실행할 수 없다면 실행할 검사를 밝힌다.

    보고된 출력에 관련 오류, warning 또는 설명되지 않은 noise가 있으면 finding이다.

    보이지 않는 근거가 존재하지 않는 것은 아니다. report 또는 검증 근거가 잘린 것으로 보이거나
    주장한 결과를 찾을 수 없다면 명시된 경로의 파일을 다시 읽는다. 실제로 없거나 깨져 있다면
    controller에게 공백으로 보고한다. 읽지 못한 내용을 다시 만들려고 suite를 재실행하는 것은
    검증이 아니다. 근거를 읽을 수 없다고 그 근거가 무효가 되지는 않는다.

    ## 1부: Spec 준수

    diff를 요청 내용과 비교한다.

    - **Missing:** 건너뛰거나 빠뜨렸거나 구현하지 않고 구현했다고 주장한 요구사항
    - **Extra:** 요청하지 않은 기능, over-engineering, 필요하지 않은 "nice to haves"
    - **Misunderstood:** 올바른 기능을 잘못된 방식으로 구현했거나 다른 문제를 해결함

    brief에 각자 변경 사항이 있는 여러 파일이 나열됐다면(batched dispatch) 파일별로 목록과
    diff를 대조한다. 나열된 모든 파일에 해당 hunk가 있어야 한다. 나머지 batch가 아무리
    깔끔해도 diff에서 건드리지 않은 나열된 파일은 Missing finding이다.

    이 diff만으로 요구사항을 검증할 수 없다면(변경되지 않은 코드에 있거나 여러 task에 걸친
    경우) 검색 범위를 넓히지 말고 ⚠️ 항목으로 보고한다.

    ## 2부: 코드 품질

    **코드 품질:**
    - 관심사가 명확히 분리되어 있는가?
    - 오류 처리가 적절한가?
    - 성급한 abstraction 없이 DRY를 지키는가?
    - edge case를 처리하는가?

    **검증:**
    - 근거가 task의 변경 유형과 지정된 검증 방법에 맞는가?
    - 테스트가 바뀌었다면 mock이 아니라 실제 동작을 검증하는가?
    - task의 중요한 사례나 invariant를 다루는가?

    **구조:**
    - 각 파일이 잘 정의된 interface와 하나의 명확한 책임을 가지는가?
    - 각 단위를 독립적으로 이해하고 테스트할 수 있도록 분해했는가?
    - 구현이 plan의 파일 구조를 따르는가?
    - 이 변경에서 이미 큰 새 파일을 만들었거나 기존 파일을 크게 키웠는가? 기존 파일 크기를
      finding으로 삼지 말고 이 변경이 추가한 내용에 집중한다.

    report는 근거를 가리켜야 한다. 모든 finding과 단순히 "yes"라고 답할 수 있는 검사에도
    `file:line`을 넣는다. 줄을 인용하는 간결한 report는 controller에게 필요한 모든 정보를 제공한다.

    final message가 report 자체다. spec 준수 판정부터 바로 시작한다. 모든 줄은 판정,
    `file:line`이 있는 finding 또는 실행한 검사여야 한다. 서문, process 설명 또는 맺음말은 쓰지 않는다.

    ## 판정 보정

    실제 심각도에 따라 문제를 분류한다. 모든 문제가 Critical은 아니다. Important는 수정하기
    전까지 이 task를 신뢰할 수 없다는 뜻이다. 잘못됐거나 깨지기 쉬운 동작, 빠진 요구사항,
    merge를 막을 만한 유지보수성 손상, 즉 logic block의 verbatim duplication, 삼킨 오류,
    아무것도 assert하지 않는 테스트 등이 해당한다. "Coverage could be broader"와 다듬기 제안은 Minor다.
    plan 또는 brief가 이 rubric에서 결함으로 보는 내용을 명시적으로 요구하더라도(아무것도
    assert하지 않는 테스트, logic block의 verbatim duplication) finding이다. plan-mandated라고
    표시해 Important로 보고한다. plan 작성자가 자신의 작업을 채점하지 않으며 사람이 결정한다.
    문제를 나열하기 전에 잘된 부분을 인정한다. 정확한 긍정적 평가는 implementer가 나머지
    피드백을 신뢰하는 데 도움이 된다.

    ## 출력 형식

    ### Spec 준수

    - ✅ Spec compliant | ❌ Issues found: [빠졌거나 추가됐거나 잘못 이해한 내용과 `file:line` 참조]
    - ⚠️ Cannot verify from diff: [diff만으로 검증할 수 없었던 요구사항과 controller가 확인할 내용.
      검증할 수 있었던 모든 내용의 ✅/❌ 판정과 함께 보고한다.]

    ### 잘된 점
    [잘된 부분을 구체적으로 작성한다.]

    ### 문제

    #### Critical (반드시 수정)
    #### Important (수정 권고)
    #### Minor (선택적 개선)

    각 문제에 `file:line`, 잘못된 내용, 중요한 이유와 명백하지 않은 경우 수정 방법을 포함한다.

    ### 판정

    **Task 품질:** [Approved | Needs fixes]

    **근거:** [1-2문장의 기술적 판정]
```

**치환할 placeholder:**
- `[MODEL]` — 필수: SKILL.md의 Model Selection에 따른 reviewer 모델
- `[BRIEF_FILE]` — 필수: task brief 파일(`scripts/task-brief PLAN N`이 경로를 출력하며 implementer가 작업한 파일과 동일)
- `[GLOBAL_CONSTRAINTS]` — plan의 Global Constraints 섹션 또는 spec에서 그대로 복사한 필수 요구사항. 정확한 값, 형식과 component 사이의 명시된 관계를 포함한다. process 규칙은 이미 이 template에 있으므로 제외한다.
- `[REPORT_FILE]` — 필수: implementer가 상세 report를 작성한 파일
- `[BASE_SHA]` — 현재 task 전의 commit
- `[HEAD_SHA]` — 현재 commit
- `[DIFF_FILE]` — 필수: controller가 review package를 작성한 경로(`scripts/review-package PLAN_FILE BASE HEAD`가 고유 경로를 출력하며 package는 controller context에 들어가지 않는다.)

**Reviewer 반환값:** Spec 준수 판정(✅/❌/⚠️), 잘된 점, 문제(Critical/Important/Minor),
Task 품질 판정
