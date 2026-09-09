# Language와 framework realization

카탈로그의 구조를 class diagram으로 직역하지 않습니다. 먼저 필요한 guarantee를 고정하고 해당
언어와 framework가 이미 제공하는 가장 작은 표현을 선택합니다.

## 판단 순서

1. 표준 타입, 함수, iterator, algebraic data type, middleware 또는 transaction API가 guarantee를
   직접 제공하는지 확인합니다.
2. framework가 lifecycle을 소유하면 별도 pattern infrastructure를 중복 구현하지 않습니다.
3. nominal class는 runtime 교체, 독립 state, lifecycle 또는 팀 경계를 표현할 때만 추가합니다.
4. pattern role 이름은 reader가 의도와 비용을 더 빨리 이해할 때만 identifier에 넣습니다.

예를 들어 Strategy는 Java에서 interface와 구현 class일 수 있지만 Python에서는 callable 하나,
TypeScript에서는 function type이나 discriminated union이 더 명확할 수 있습니다. State도 닫힌 상태
집합이면 state class 계층보다 exhaustive union transition이 더 강한 guarantee를 줄 수 있습니다.

분산 패턴은 라이브러리 이름으로 구현 완료를 주장하지 않습니다. 설정된 delivery, ordering,
consistency, idempotency와 recovery 동작을 실제 provider·runtime 경계에서 확인합니다.
