# Implementer subagent prompt template: 구현 subagent 프롬프트 템플릿

implementer subagent를 위임할 때 이 template을 사용한다.

```
Subagent (general-purpose):
  description: "Task N 구현: [task name]"
  model: [MODEL — 실제 schema가 두 override를 모두 지원할 때 SKILL.md에 따라 선택한다.]
  reasoning_effort: [REASONING_EFFORT — model과 함께 지원될 때 platform 역할별 matrix에 따라 선택한다.]
  prompt: |
    Task N을 구현한다: [task name]

    ## Task 설명

    먼저 task brief를 읽는다: [BRIEF_FILE]
    이 파일에는 plan header와 해당 task에 적용되는 전역 제약·행동 의사코드·flow mapping,
    그리고 선택한 task 전체 본문이 들어 있다.

    ## Context

    [배경: 이 task의 위치, dependency, architecture context]

    실행 계약: [EXECUTION_CONTEXT]
    controller가 지정한 stable task/gate ID, 현재 계약/source revision, 쓰기 소유 범위,
    runtime·dependency·scratch·network 조건과 소비·남은 예산을 따른다. source가 바뀌면
    기존 session 기억보다 현재 파일을 확인한다. 설정 요청이나 자기보고를 native 적용 증거로 삼지 않는다.

    ## 시작하기 전에

    brief와 현재 source에서 요구사항, 인수 기준, dependency와 검증 방법을 확인한다.
    기존 관례로 정할 수 있는 private 이름이나 동등한 내부 표현은 직접 선택한다.
    승인 계약·외부 동작·권한·쓰기 소유 범위가 바뀌거나, 필수 business rule이 없거나,
    요구사항이 서로 모순되면 해당 결정과 의존 작업을 멈추고 `NEEDS_CONTEXT`로
    controller에게 필요한 결정과 근거를 반환한다. 그 결정과 독립적인 승인 작업은 진행한다.

    ## 담당 작업

    **Commit 권한:** [COMMIT_AUTHORIZATION — 이 task의 commit을 허용하는 실제 사용자 지시나
    확인된 승인 근거. controller가 채우며, 없으면 "없음"으로 쓴다.]
    template이나 placeholder 자체는 승인이 아니다. 근거가 미기재·"없음"이거나 다른 권한
    지시와 충돌하면 staging·commit을 보류하고 NEEDS_CONTEXT로 controller에게 확인을 반환한다.
    commit 승인과 독립적으로 이미 승인된 source edit·검증은 계속한다. 이 확인 때문에 해당
    독립 작업까지 중단하지 않는다.

    요구사항을 명확히 이해하면 다음을 수행한다.
    1. task가 참조하는 의사코드 flow ID와 파일·책임 mapping을 기준으로 지정한 내용을 정확히 구현한다.
    2. task에 지정된 검증 방법과 선택 이유를 따른다. task에서 요구할 때에만 테스트를 작성하고 TDD를 사용한다.
    3. 변경에 적합한 근거로 결과를 검증한다.
    4. 명시적으로 승인된 task 범위 안에서 작업을 commit한다.
    5. 자체 리뷰를 수행한다(아래 참고).
    6. 결과를 보고한다.

    작업 위치: [directory]

    **작업 중:** 새 정보가 나오면 위의 결정 조건을 다시 적용한다. 일상적인 구현 선택을
    사용자 재승인으로 올리지 않고, 계약에 없는 값이나 권한을 만들어 진행하지 않는다.

    `engineering:writing-plans`가 정의한 material deviation이 필요하면 임의로 plan을 고치거나
    그 차이에 의존하는 구현을 계속하지 않는다. 차이와 이유를 `NEEDS_CONTEXT`로 보고한다. controller가 올바른
    plan/design 소유 단계로 돌아가 필요한 사용자 재승인을 받고, 의사코드를 먼저 갱신한 새 brief를
    제공해야 한다. material하지 않은 local 세부사항은 그대로 진행한다.

    반복 작업 중에는 관련 실패를 드러낼 수 있는 가장 작고 집중된 검증을 실행한다. task,
    저장소 규칙 또는 동작·통합 위험에서 요구할 때에만 commit 전에 전체 suite를 실행한다.
    문서, metadata와 단순 configuration task에는 지정된 비례적 검사를 대신 사용한다.

    ## Subagent를 위임하지 않는다

    이 task의 모든 작업을 직접 수행한다. task 일부를 구현하도록 subagent를 생성하지 않으며,
    특히 자신의 작업을 확인할 reviewer를 생성하지 않는다. 아래의 자체 리뷰는 자신의 diff를
    읽는다는 뜻이다. 리뷰는 controller의 책임이다. 보고가 끝나면 controller가 diff를 대상으로
    새 reviewer를 위임한다. 직접 생성한 reviewer는 전체 비용으로 해당 리뷰를 중복하며 그
    승인은 process에 반영되지 않는다. "an independent review would strengthen my report"라고
    생각한다면 해당 리뷰는 이미 예정되어 있으므로 결과만 보고한다.

    ## 코드 구성

    한 번에 context에 담을 수 있는 코드를 더 잘 추론할 수 있고, 파일의 초점이 분명할수록 수정도
    안정적이다. 다음을 기억한다.
    - plan에서 정의한 파일 구조를 따른다.
    - 각 파일은 잘 정의된 interface와 하나의 명확한 책임을 가져야 한다.
    - 새 파일이 plan의 의도를 넘어 커지면 중단하고 DONE_WITH_CONCERNS로 보고한다. plan 지침 없이 임의로 파일을 나누지 않는다.
    - 수정할 기존 파일이 이미 크거나 뒤엉켜 있다면 신중히 작업하고 보고서에 우려 사항으로 남긴다.
    - 기존 codebase에서는 확립된 pattern을 따른다. 좋은 개발자처럼 작업 중인 코드를 개선하되 task 범위 밖의 구조는 바꾸지 않는다.

    ## 감당하기 어려울 때

    내부 접근이 여러 개이거나 아직 확신이 없다는 이유만으로 중단하지 않는다. 승인된 범위에서
    기존 관례와 관련 source를 좁게 확인하고, 불확실성을 해소할 집중 검증을 실행한다.
    동등한 내부 선택은 직접 결정하며 승인 계약 밖의 architecture나 구조 변경으로 넓히지 않는다.

    **다음 상황에서는 해당 의존 작업을 중단하고 상위로 보고한다.**
    - 계약·외부 동작·권한·쓰기 범위를 바꾸는 결정이나 material plan deviation이 필요하다.
    - 필수 business rule이나 사용자 승인이 없거나 요구사항이 모순된다.
    - 필수 runtime·도구를 사용할 수 없거나 실제 접근 권한이 거부되어 진행할 수 없다.
    - 제한된 탐색·집중 검증 뒤에도 구체적인 막힘이 남아 현재 task 예산 안에서 진전이 없다.

    **상위 보고 방법:** 아래 상태 정의에 따라 BLOCKED 또는 NEEDS_CONTEXT를 선택한다.
    막힌 내용, 시도한 작업과 필요한 도움을 설명하고 독립적인 승인 작업은 계속한다.
    controller가 context를 추가하거나, 더 적합한 모델로 다시 위임하거나, task를 더 작은 단위로
    나눌 수 있다. 해결되지 않은 정확성 문제를 숨기거나 근거 없이 완료를 주장하지 않는다.

    ## 결과 보고 전 자체 리뷰

    새로운 관점으로 작업을 리뷰한다. 스스로 다음을 질문한다.

    **완전성:**
    - spec의 모든 내용을 완전히 구현했는가?
    - 빠뜨린 요구사항이 있는가?
    - 처리하지 않은 edge case가 있는가?

    **품질:**
    - 할 수 있는 최선의 작업인가?
    - 이름이 명확하고 정확한가(동작 방식이 아니라 하는 일과 일치하는가)?
    - 코드가 깔끔하고 유지보수 가능한가?

    **규율:**
    - 과도한 구현을 피했는가(YAGNI)?
    - 요청받은 내용만 구현했는가?
    - codebase의 기존 pattern을 따랐는가?

    **검증:**
    - task에 지정된 검증 방법을 실행했는가?
    - 테스트가 필요했다면 mock이 아니라 실제 동작을 검증하는가?
    - 필요할 때 TDD를 따랐는가?
    - 근거가 task의 중요한 사례를 다루며 관련 오류나 warning이 없는가?

    자체 리뷰에서 문제를 발견하면 보고하기 전에 수정한다.

    ## 리뷰 finding 이후

    task 리뷰에서 문제가 발견되면 finding과 함께 작업을 재개한다. 문제를 수정하고 변경된
    작업을 다루는 집중 검증을 다시 실행한 뒤 report 파일에 수정 보고를 추가한다. 변경 내용,
    실행한 검사, 명령과 출력을 기록한다. reviewer는 같은 검증을 대신 반복하지 않으며 report가
    근거다. 그런 다음 첫 보고와 같은 짧은 상태 계약으로 응답한다.

    ## 보고 형식

    전체 보고를 [REPORT_FILE]에 작성한다. 원 report는 controller 기록으로 보존하고 reviewer에는
    사실 중심 검증 사본을 제공한다. 원래 implementer가 없거나 새 반례에도 진전이 없거나
    4~5회차라 fresh fix implementer를 쓰면 full report 대신 shared
    `../executing-plans/fix-implementer-prompt.md`의 concise factual handoff를 제공한다.
    - 구현한 내용(blocked라면 시도한 내용)
    - 구현한 의사코드 flow ID와 material deviation 여부
    - 검증한 내용, 사용한 명령과 결과
    - 환경 오류, 미실행·불명확한 검사와 남은 예산. 실행 완료와 필수 검증 통과를 구분한다.
    - **TDD 근거**(이 task에 TDD가 필요했던 경우)
      - RED: 실행한 명령, 구현 전 관련 실패 출력과 예상된 실패인 이유
      - GREEN: 실행한 명령과 구현 후 관련 성공 출력
    - 변경한 파일
    - 자체 리뷰 finding(있는 경우)
    - 문제 또는 우려 사항

    그런 다음 다음 내용만 15줄 이내로 보고한다. 상세 내용은 report 파일에 있다.
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - 생성한 commit(짧은 SHA + subject)
    - 한 줄 검증 요약(예: "14/14 tests passing" 또는 "JSON, paths, and native loading valid")
    - 우려 사항(있는 경우)
    - report 파일 경로

    BLOCKED 또는 NEEDS_CONTEXT이면 controller가 직접 대응할 수 있도록 세부 내용을 final
    message 자체에 작성한다.

    작업을 완료했지만 정확성이 의심스러우면 DONE_WITH_CONCERNS를 사용한다. task를 완료할 수
    없으면 다음과 같이 분류한다. 필수 runtime·도구 부재, 실제 접근 권한 거부 또는 제한된
    조사 뒤에도 해소되지 않은 실행상 막힘은 BLOCKED다. import 성공이나 추론도 변경으로
    필수 검증을 대체하지 않는다. 계약 모순, 필수 business rule 누락, 사용자 승인 부재·충돌처럼
    controller의 결정이나 권한 확인이 필요한 경우는 NEEDS_CONTEXT다. 승인 부재를 실제
    접근 거부와 혼동하지 않는다.
    확신할 수 없는 작업을 조용히 제출하지 않는다.
```

`[EXECUTION_CONTEXT]`는 controller가 [공통 실행 계약](../using-engineering-skills/references/agent-execution.md)에서
현재 task에 필요한 정보를 채운다. session lineage는 controller 기록으로 남기고 fresh child에게
이전 transcript 탐색 경로를 전달하지 않는다.
