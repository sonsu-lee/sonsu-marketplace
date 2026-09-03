# 스킬 라우팅 평가

`cases.json`은 Engineering, Quality Engineering, Workflow, Research, Prompting, Product와 Fluent
Languages를 함께 또는 각각 설치했을 때의 기대 라우팅을 정의합니다. 직접 산출물 요청,
비슷하지만 다른 요청, runtime 조합과 단독 설치 사례를 포함합니다.

`workflow:to-pr` 사례는 선택된 스킬뿐 아니라 원격 변경이 없는 준비 모드인지, publish payload의
`target_pr_state`가 무엇인지도 선언할 수 있습니다. 이 경우에도 평가는 원격 PR을 만들지 않고
모델이 제안한 계획과 payload만 확인합니다.

`workflow:to-ticket`과 `workflow:ticket-lifecycle` 사례는 생성과 기존 티켓 변경을 분리하고,
`expected_intent`, `expected_relation`, `expected_assignee_change`, canonical ticket·assignee 확인,
mutation 후 재조회와 native automation 중복 방지 같은 기대 효과를 선언할 수 있습니다. 이 필드는 모델이 제안한 작업과
결과 보고를 평가하기 위한 계약이며 실제 원격 ticket 생성·수정 권한을 부여하지 않습니다.
`expected_relation.target`도 fixture locator일 뿐 canonical ticket의 증거가 아니므로 실행 시 두
ticket을 각각 검증해야 합니다. `must_use_native_relation`은 provider의 native operation을 우선해
판단하라는 뜻이지, 사용자가 금지한 필수 부수 효과까지 무시하고 mutation하라는 권한은 아닙니다.
`must_report_conflict`와 `must_not_propose_mutation`이 함께 있으면 그 충돌을 명시하고 원격 호출을
제안하지 않아야 합니다. `expected_assignee_change.target`이 특정 사용자라면 해당 사용자를 현재
assignee에서 검증하고 다른 assignee를 유지해야 합니다. `all`은 사용자가 모든 담당자 해제를
명시한 사례에서만 허용합니다.

이 평가는 실제 skill selection 결과를 대상으로 합니다. JSON 파싱이나 description 문자열 비교는
평가 실행을 대신하지 않습니다. 모델 기반 실행은 격리된 읽기 전용 fixture에서 수행하고 원격
push, ticket 게시와 PR 생성은 허용하지 않습니다. 결과는 `pass`, `fail`, `not_run`,
`inconclusive`로 구분하며, 선택 attribution을 확인할 수 없으면 `pass`로 판정하지 않습니다.
