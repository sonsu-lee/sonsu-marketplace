# Operations design decision contract

화면을 만들기 전에 `design-decision-contract-v1`을 작성하고 잠근다. 형식은
`assets/design-quality/design-decision-contract.schema.json`, 의미는 [공통 계약](design-quality.md)을
따른다. 기존 `operations-ui-screen-contract-v1`은 사용하지 않는다.

## 공통 핵심

- `primary_question`: 사용자가 화면에서 가장 먼저 답해야 할 질문
- `intended_outcome`: 화면 사용 뒤 기대하는 관찰 가능한 결과
- `task_scenarios`: 시작 맥락, 올바른 결과, 오판과 비용, 필요한 정보·표현·환경
- `information_requirements`: `must_know`, `supporting`, `on_demand` 정보의 의미·출처·신선도·불확실성
- `representation_map`: 표현 이유, semantic role과 필수 `non_color_signals`
- `environments`: 실제 platform, 크기, input, locale, writing mode, accessibility profile
- `states`: 실제로 도달 가능한 상태와 근거. 체크리스트를 채우기 위해 가짜 상태를 만들지 않는다.
- `metric_targets`: 결과를 보기 전에 정한 primary·guardrail 지표. `critical-harm == 0`은 필수다.

## Operations 확장

`extensions.operations`에 `surface`, `jobs`, `entities`, `lifecycle`, `actions`, `permissions`,
`risks`, `requirements`를 기록한다. 각 task scenario는 다음을 추가한다.

- `requirement_ids`: 양방향으로 연결되는 요구사항 ID
- `actions`: 실제로 실행할 안정적인 action ID
- `coverage`: actions, permissions, risks, states의 선언값을 어떤 scenario가 검증하는지 표시

모든 선언값은 적어도 한 scenario가 다뤄야 한다. 대상 environment는 전역 기본값이 아니라 각
scenario의 `environment_ids`에서 파생한다.

## 재설계

`mode: redesign`은 `current_behavior_inventory`와 `change_contract`를 필수로 둔다. feature, state,
action, permission, data-shape마다 관찰 근거, preserve/change 결정, 구현 대상, scenario를 연결한다.
관찰 근거는 contract 파일을 기준으로 실제 존재하는 비어 있지 않은 상대 경로여야 한다.
모든 inventory ID는 정확히 한 change contract에 속해야 하며 연결 구성원은 공통 scenario를
가져야 한다. 확인되지 않은 기존 동작을 삭제해 계약을 통과시키지 않는다.

`unresolved_decisions`는 영향 gate와 필요한 근거를 유지한다. critical 미결정이 남은 필수 gate는
통과할 수 없으며, 다른 독립 범위의 작업과 유효한 증거는 그대로 보존한다.
