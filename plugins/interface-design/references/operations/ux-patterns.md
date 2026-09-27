# UX patterns

## Status summary와 filter

summary를 선택하면 table filter가 변경되고 active 상태, 결과 수와 reset 경로가 보인다. dashboard KPI처럼 읽기 전용이면 click affordance를 주지 않는다.

## Filter bar

자주 쓰는 필터만 노출하고 advanced filters는 별도 surface로 확장한다. 적용된 조건, 결과 수, reset 범위와 URL/state persistence를 일관되게 처리한다.

## Data table

식별자와 primary state를 왼쪽, 수치와 날짜를 정렬 가능한 열에 둔다. row action과 selection action을 구분한다. long/localized value, zero/one/many rows, horizontal overflow와 column priority를 실제 데이터로 확인한다.

## Selection과 bulk action

선택 범위가 현재 page인지 전체 결과인지 표시한다. 필터·페이지 변경 시 selection 유지/해제 규칙을 명시한다. partial success는 성공·실패 수와 재시도 대상을 분리한다.

## Detail surface

빠른 확인은 drawer, 독립 URL·복잡한 이력·깊은 작업은 detail page를 사용한다. close/back 후 list context, filter, scroll과 selection 복원 규칙을 정한다.

## Destructive action

위험도를 색만으로 표현하지 않는다. 대상, 영향, 되돌릴 수 있는지와 권한을 보여준다. confirmation은 모든 클릭에 붙이지 않고 실제 손실 가능성이 있는 행동에만 사용한다.

## 상태와 피드백

- loading: layout shift를 줄이고 무엇을 기다리는지 표현한다.
- empty: `아직 없음`과 `필터 결과 없음`을 구분한다.
- error: 실패 범위, 보존된 작업과 재시도 방법을 보여준다.
- permission-denied: 숨김과 disabled의 제품 규칙을 따르고, 이유와 요청 경로가 있다면 제공한다.
- pending/success/failure: action owner와 중복 실행 방지, 결과 반영 시점을 분명히 한다.

## Keyboard와 focus

navigation, filter, table action, drawer/modal 순서가 시각적 작업 흐름과 일치해야 한다. overlay가 열리면 focus를 이동·가두고 닫은 뒤 호출 지점으로 복귀시킨다.
