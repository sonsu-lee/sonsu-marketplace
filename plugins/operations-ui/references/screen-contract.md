# Screen Contract

이 문서의 실행용 계약과 JSON/validator는 운영형 웹 구현·런타임 감사에 적용한다. 제안/Figma-only·일반 UI의 범위·결과는 [산출물별 작업 경계](delivery.md)를 따른다.

화면을 그리기 전에 `screen-contract.schema.json` 형식으로 작업 계약을 확정한다. 구현 중 새로 발견된 제품 결정은 추측해 숨기지 말고 계약으로 되돌린다.

## 필수 내용

- `actors`, `jobs`: 누가 어떤 운영 판단과 작업을 하는가
- `entities`, `lifecycle`: 무엇을 어떤 상태 전이로 관리하는가
- `primary_decision`: 이 화면에서 가장 먼저 내려야 하는 한 가지 판단
- `actions`, `permissions`, `risks`: 가능한 행동, 권한, 잘못됐을 때의 비용
- `view_states`: 현재 화면에서 도달 가능한 상태. loading, empty, error, permission-denied, zero, one, many, long-localized는 적용 여부를 검토할 예시이며 필수 상태 목록이 아니다. 제외 판단은 실제 타입·입력 경계·기존 동작에 근거하고, 미확인 상태는 `unresolved_decisions`로 남긴다.
- `viewports`: 실제 증거를 수집할 viewport. wide는 기본 `1440x900`이다.
- `requirements`: 검증 가능한 요구사항과 연결된 scenario ID
- `evidence_scenarios`: initial state, action sequence, expected outcome, required viewport와 `coverage`
- `exclusions`: 적용하지 않는 check와 구체적인 이유. `id`, `kind`, `check_ids`, `reason`을 사용하며 허용 kind는 `embedded-shell`, `desktop-only`, `capability-absent`다.
- `unresolved_decisions`: 모든 mode에서 확인하지 못한 항목을 `id`, `area`, `reason`, `evidence_needed`, 영향받는 `gate_ids`로 구조화한다. `area`에는 판단이 필요한 기능·권한·상태의 범위를 식별할 수 있게 쓴다. 조정자는 이 범위와 의존성을 대조해 관련 작업만 보류하고, 독립적으로 확정된 작업은 계속한다.

validator 성공은 필드·참조·coverage의 구조적 유효성이며 전체 구현 준비나 의미적 독립성을
증명하지 않는다. 미결정 항목이 남으면 전체 완료와 G0 및 지정된 gate의 통과는 금지된다.
영향이 없는 gate의 현재 근거는 보존할 수 있다. 미결정 항목은 해결 근거 없이 삭제하거나
영향 gate를 줄여 통과시키지 않는다.

## 완료 조건

- 모든 requirement가 하나 이상의 evidence scenario에 연결된다.
- 모든 scenario가 존재하는 requirement와 viewport만 참조한다.
- scenario의 `coverage.actions`, `coverage.permissions`, `coverage.risks`, `coverage.view_states`는 Screen Contract에 선언된 값만 참조한다. `coverage.actions`의 값은 같은 scenario의 `actions` 실행 순서에 실제로 포함한다. 모든 scenario의 coverage 합집합은 각 선언을 100% 포함해야 한다. 해당 scenario가 다루지 않는 차원은 빈 배열로 남긴다.
- `wide` viewport는 `1440x900`으로 고정한다. narrow가 없으면 양의 `minimum_viewport.width/height`와 구체적인 `operational_reason`을 `desktop-only` exclusion에 남기고 `narrow-or-excluded` check만 제외한다. minimum은 wide 증거 viewport보다 클 수 없다. overflow 관찰은 여전히 필요하다.
- permission 또는 destructive action이 없다는 사실도 계약에 나타낸다. 존재하지 않는 기능을 임의로 추가하지 않는다.

## 재설계 추가 계약

재설계는 먼저 Current Behavior Inventory를 만든다.

| 필드 | 의미 |
| --- | --- |
| `id` | 안정적인 추적 ID |
| `kind` | feature, state, action, permission, data-shape |
| `observed` | 코드 또는 브라우저에서 확인한 현재 동작 |
| `evidence` | 위치, screenshot 또는 실행 기록 |
| `decision` | preserve 또는 change |
| `reason` | 결정 근거 |
| `implementation_target` | 변경하거나 보존할 코드 위치 |
| `scenario_ids` | 재검증할 browser scenario |

decision, implementation target 또는 scenario mapping이 없는 항목과 의존 작업은 실행을 보류한다.
확정된 독립 범위는 기존 inventory와 미결정 항목을 보존한 채 별도 Screen Contract로 분리해
구조를 검증하고 진행할 수 있다. 부분 계약 통과는 전체 재설계 통과가 아니다. 전체 보존·변경 ID의
mapping coverage가 100%가 아니면 재설계를 완료로 판정하지 않는다.

`current_behavior_inventory`와 `change_contract`는 `mode: redesign`의 필수 필드다. Change Contract의 `inventory_ids` 합집합은 inventory ID 전체와 정확히 일치해야 하고, 각 inventory ID는 정확히 하나의 Change Contract에만 속해야 하며 각 항목은 존재하는 requirement와 browser scenario를 참조한다. 하나의 Change Contract 묶음에 들어간 모든 inventory와 requirement는 적어도 하나의 동일한 scenario를 공유해야 한다. 공유하지 않으면 서로 다른 묶음으로 나눈다.
