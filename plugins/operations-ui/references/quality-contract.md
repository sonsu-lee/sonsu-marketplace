# Quality contract

이 문서의 실행용 계약과 JSON/validator는 운영형 웹 구현·런타임 감사에 적용한다. 제안/Figma-only·일반 UI의 범위·결과는 [산출물별 작업 경계](delivery.md)를 따른다.

## 상태

gate status는 `passed`, `failed`, `blocked`, `inconclusive`, `not_run` 중 하나다. G0–G7은 모두 `required: true`이고 gate 자체에는 `not_applicable`을 사용할 수 없다.

개별 check만 Screen Contract의 exclusion ID, 일치하는 `check_ids`와 구체적인 reason이 있을 때 `not_applicable`이 될 수 있다. `embedded-shell`은 `shell-and-navigation`, `desktop-only`는 `narrow-or-excluded`, `capability-absent`는 `bulk-destructive-actions`만 제외할 수 있다. 다른 필수 check는 N/A가 될 수 없다. 해당 check를 제외한 gate의 책임이 모두 실제 증거로 확인돼야 gate가 `passed`다. `accepted_risk`는 사람이 명시적으로 결정하는 별도 기록이며 자동으로 pass를 만들지 않는다.

## 고정 gate

gate별 check ID도 아래 순서로 고정한다. `status: passed`인 gate의 check는 모두 `passed` 또는 유효한 `not_applicable`이어야 한다.

| Gate | Required check IDs |
| --- | --- |
| G0 | `contract-artifact`, `requirement-scenario-coverage` |
| G1 | `pattern-decision`, `information-hierarchy`, `actual-wide-render` |
| G2 | `token-mapping`, `shell-and-navigation`, `semantic-color`, `density-and-components` |
| G3 | `state-matrix`, `loading-empty-error-permission`, `zero-one-many`, `long-localized-overflow` |
| G4 | `primary-secondary-actions`, `bulk-destructive-actions`, `feedback-and-selection` |
| G5 | `wide-viewport`, `narrow-or-excluded`, `overflow-and-detail-access` |
| G6 | `keyboard-focus`, `names-roles-states`, `non-color-status`, `contrast` |
| G7 | `actual-app-provenance`, `required-scenario-coverage`, `screenshots`, `console-runtime` |

### G0 Contract Integrity

Screen Contract 필수 필드가 완성되고 unresolved decision이 없으며 requirement와 action, permission, risk, view state의 scenario coverage가 100%다.

필수 증거: screen contract artifact, coverage matrix.

### G1 Task & Information Architecture

primary decision/action, 선택한 screen pattern, entity/lifecycle/status/filter hierarchy가 일치한다.

필수 증거: pattern decision record, scenario mapping, wide actual-render screenshot.

### G2 Precision Operations Console Visual System

[design.md](design.md)의 light workspace, dark persistent navigation, blue primary/selection, semantic colors, density, spacing과 component hierarchy가 actual UI에 일관되게 적용된다. standalone console에는 dark persistent navigation check가 필수다. embedded view만 exclusion으로 그 check를 제외할 수 있다.

필수 증거: token mapping/audit, wide actual-render screenshot, table/form/component sample.

### G3 Data & State Resilience

contract상 applicable한 loading, empty, error, permission-denied, zero, one, many, long-localized와 overflow 상태가 구현되고 관찰된다.

필수 증거: state matrix, scenario별 actual-render capture 또는 observation.

### G4 Interaction Safety

primary, secondary, bulk, destructive action과 disabled, pending, success, failure, partial-success feedback가 계약과 일치한다. selection과 cancel/rollback 의미가 분명하다.

필수 증거: browser action trace, 결과 UI capture. 존재하지 않는 action check는 exclusion이 필요하다.

### G5 Responsive & Spatial Integrity

wide `1440x900`와 contract narrow viewport에서 navigation, content, table overflow, reflow, truncation과 detail access가 유실되지 않는다. desktop-only는 minimum viewport와 운영상 이유가 있을 때 narrow check만 제외할 수 있고 horizontal behavior evidence는 필수다.

필수 증거: viewport-tagged captures, overflow observation.

### G6 Accessibility

keyboard reach/order, visible focus, accessible names/roles/states, non-color-only status와 contrast를 applicable interactive scenario에서 확인한다.

필수 증거: keyboard trace, semantics output 또는 수동 inspection, contrast result.

### G7 Browser Runtime Evidence

실제 target app의 command, build 또는 revision, URL, scenario ID, viewport, action, expected/observed, screenshot path와 console/runtime error result가 연결돼 있다. screenshot 단독, 정적 mock 또는 Figma는 증거가 아니다.

필수 증거: [evidence-contract.md](evidence-contract.md)의 Browser Evidence Receipt와 모든 required scenario×viewport coverage.

## 전체 판정

`overall: passed`는 G0–G7이 정확한 순서로 모두 `passed`이고, 모든 필수 evidence와 required browser receipt가 있을 때만 허용한다. 하나라도 `failed`, `blocked`, `inconclusive`, `not_run`이면 가장 가까운 책임 단계로 반환하고 수정·재실행한다.
