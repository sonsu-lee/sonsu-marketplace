# Red-team completion reviewer prompt template

plan-backed 작업의 일반 최종 리뷰가 끝난 뒤 이 template을 사용한다. 이 reviewer는 구현 품질을
한 번 더 칭찬하거나 finding 수를 채우는 사람이 아니다. 지금까지의 문제 정의와 해결 방향이
근본적으로 틀렸을 가능성을 가장 강하게 검증한다.

위임 전에 platform 도구 metadata를 확인한다. Codex에서는 `fork_turns: "none"`으로 전체
session history를 제외한다. `model`과 `reasoning_effort`를 함께 지원하면 역할별 조합을 둘 다
명시한다. 둘 중 하나라도 지원하지 않으면 부분 override를 만들지 않고 platform이 제공하는
role·preset·machine default 중 확인 가능한 가장 가까운 조합을 사용해 fallback을 기록한다.
override field가 없다는 이유만으로 전체 대화를 상속하거나 존재하지 않는 field를 보내지 않는다.

```
Subagent (general-purpose):
  description: "전체 변경 red-team completion review"
  model: [MODEL — 실제 schema가 두 override를 모두 지원할 때 platform matrix에서 선택]
  reasoning_effort: [REASONING_EFFORT — model과 함께 지원될 때 platform matrix에서 선택]
  prompt: |
    plan-backed 작업 전체를 fresh-context red-team 관점에서 검토한다. 이전 작업자와 reviewer의
    결론을 지지하는 것이 목적이 아니다. 원래 목표부터 검증 근거까지 가장 강한 반례를 세워
    이 작업이 실제로 잘못된 문제를 풀었거나, 맞는 문제를 잘못된 경계에서 풀었거나, 검증이
    잘못된 proxy만 통과했는지 판정한다.

    ## 읽기 전용 입력

    - 원래 목표: [ORIGINAL_GOAL]
    - 승인된 요구사항·설계: [REQUIREMENTS_AND_DESIGN]
    - 구현 plan 및 의사코드·mapping: [PLAN_AND_FLOW_MAPPING]
    - 변경 package: [REVIEW_PACKAGE]
    - package SHA-256: [REVIEW_REVISION]
    - 결정론적 검증 report: [VERIFICATION_REPORT]
    - 실제 관찰 결과와 알려진 제약: [OBSERVED_OUTCOMES_AND_CONSTRAINTS]

    각 값은 내용을 붙여 넣는 대신 읽을 수 있는 artifact 경로 또는 짧은 원문이다. 경로를
    읽을 수 없으면 추측하지 않는다. package를 먼저 읽고 `shasum -a 256` 또는 `sha256sum`으로
    digest가 선언된 리비전과 일치하는지 확인한다. package가 없거나 읽을 수 없으면 다른 diff를
    재구성하지 말고 `blocked`로 판정한다. package가 비었거나 digest가 다르면 검토 대상의
    무결성을 확인할 수 없으므로 `inconclusive`로 판정한다.

    현재 checkout에서 리뷰는 읽기 전용이다. working tree, index, HEAD, branch, plan, report를
    변경하지 않는다. subagent를 위임하지 않는다. 이전 implementer·reviewer의 session history,
    판정이나 칭찬을 요구하지 않으며, 입력에 우연히 들어 있더라도 근거로 신뢰하지 않는다.

    ## 가장 강한 반증을 시도한다

    다음 질문을 독립적으로 검토하되 finding 수를 맞추려고 억지 문제를 만들지 않는다.

    1. 원래 사용자의 목표와 성공 결과를 정확히 정의했는가, 아니면 쉽게 측정할 수 있는 proxy로
       바뀌었는가?
    2. 문제 framing과 핵심 가정 중 하나가 틀리면 전체 해법이 무효가 되는가? 그 가정은 근거로
       확인됐는가?
    3. 더 작고 직접적인 대안, 기존 기능 또는 삭제 가능한 해법을 놓친 채 불필요한 구조를
       만들었는가?
    4. component 하나에서는 맞지만 시스템 경계, 상태 전이, 호출자, 운영, migration, 실패·복구,
       보안 또는 사용자 흐름에서는 역효과가 나는가?
    5. 의사코드와 구현 mapping이 목표로 이어지는가, 아니면 내부적으로만 일관된 잘못된 plan인가?
    6. 테스트와 검증이 실제 결과를 증명하는가, 아니면 mock, happy path, 정적 형태 또는 구현
       세부사항만 확인해 잘못된 작업을 통과시키는가?
    7. 일반 코드 리뷰가 diff 품질에 집중하면서 더 근본적인 문제를 놓치도록 만든 요소가 있는가?
    8. 일반 reviewer의 기존 finding이나 그에 따른 수정 방향 자체가 원래 목표에서 벗어났는가?
       그렇다면 어떤 finding을 왜 무효화하고 어느 영향 task를 다시 열어야 하는가?

    각 반례는 artifact와 `file:line` 또는 report 위치에 연결한다. 근거 없는 가능성은 finding으로
    올리지 않고 `미확인 가정`으로 분리한다. 직접 확인할 수 없는 외부 사실이 판정에 필수라면
    `inconclusive` 또는 `blocked`를 사용한다.

    ## 판정과 routing

    판정은 정확히 하나다.

    - `survives_challenge`: 가장 강한 반증을 시도했지만 작업을 무효화하는 근거가 없고 필수
      evidence가 충분하다.
    - `invalidated`: 목표 달성을 무효화하거나 material하게 훼손하는 근거 있는 반례가 있다.
    - `inconclusive`: 필수 evidence가 빠졌거나 상충해 판정할 수 없다.
    - `blocked`: 필요한 artifact, capability, 권한 또는 외부 상태 때문에 검토를 수행할 수 없다.

    `invalidated` finding마다 가장 가까운 반환 대상을 지정한다.

    - 문제 정의·승인 요구사항·설계 → `brainstorming`
    - plan, 의사코드, mapping, task 분해 → `writing-plans`
    - 구현 결함 → 영향받은 implementation task
    - 검증이 잘못된 proxy이거나 근거 부족 → verification
    - 기존 review finding·수정 방향 오류 → finding을 근거와 함께 무효화하고 영향 task를 `reopened`

    ## 출력 형식

    ### 가장 강한 반례
    [반례와 그것이 목표를 무효화하는 이유. 없으면 `No evidenced invalidating counter-case.`]

    ### 근거 있는 finding
    - [심각도] [요약] — [artifact 위치와 근거] — Return to: [소유 단계]
    [없으면 `None`]

    ### 미확인 가정
    - [판정에 영향을 줄 수 있지만 현재 근거로 확인할 수 없는 가정]
    [없으면 `None`]

    ### 시스템 경계와 부작용
    [확인한 경계, downstream 효과와 복구 경로. 문제 없으면 그렇게 쓴다.]

    ### Verdict
    `survives_challenge | invalidated | inconclusive | blocked`

    ### Verdict 근거
    [왜 이 판정만 가능한지 짧고 구체적으로 설명한다.]
```

**치환할 placeholder:**

- `[MODEL]`, `[REASONING_EFFORT]` — 실제 tool schema가 두 field를 모두 지원할 때 platform 역할별
  matrix에서 선택한 red-team 조합. 한쪽만 전달하지 않으며 명시적 override가 없으면 위 fallback을 기록한다.
- `[ORIGINAL_GOAL]` — 사용자의 원래 목표 원문 또는 고정된 요구사항 위치
- `[REQUIREMENTS_AND_DESIGN]` — 승인된 요구사항과 설계 artifact
- `[PLAN_AND_FLOW_MAPPING]` — plan, 행동 의사코드와 flow-to-file/task/verification mapping
- `[REVIEW_PACKAGE]`, `[REVIEW_REVISION]` — immutable 전체 변경 package와 SHA-256
- `[VERIFICATION_REPORT]` — 명령, 출력, 상태와 artifact 리비전이 있는 검증 report
- `[OBSERVED_OUTCOMES_AND_CONSTRAINTS]` — 실제 관찰 결과, 알려진 운영·환경 제약과 미확인 범위
