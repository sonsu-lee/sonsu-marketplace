# TypeScript policy

TypeScript에서는 compiler가 이미 정확히 추론하는 타입을 기본으로 사용한다. annotation과 별도
타입 이름은 계약, 제약 또는 재사용 경계를 더 명확하게 만들 때만 추가한다.

## Inference first

- 지역 변수, 명백한 반환값과 callback parameter의 타입은 추론에 맡긴다.
- public API, 재귀 함수, overload 경계, 생성된 선언의 안정성 또는 의도한 widening을 제어해야
  할 때는 annotation을 사용한다.
- `ReturnType`, 깊은 conditional type와 type-level program은 직접 타입보다 계약이 더 선명하고
  실제 중복을 줄일 때만 사용한다.
- 한 번만 쓰이며 구조 자체가 충분히 명확한 object shape에는 이름을 만들지 않는다.

## Variants and invalid states

- discriminated union은 현재 존재하는 variant별 동작이 다를 때 사용한다.
- exhaustive check는 모든 현재 variant를 반드시 처리해야 하고 누락이 실제 결함일 때 사용한다.
- optional field 여러 개로 불가능한 조합이 생기면 확인된 variant로 분리한다. 미래 variant를
  예상해 union member를 추가하지 않는다.
- branded type은 같은 primitive 값이 쉽게 뒤바뀌고 그 오류를 일반 구조 타입으로 막을 수 없을
  때만 사용한다. 생성과 검증 경계를 함께 제공하지 못하면 brand만 추가하지 않는다.

## Untrusted values

- `unknown`은 외부 입력이나 런타임 검증 전 값처럼 실제로 알 수 없는 경계에 사용한다.
- 내부의 이미 신뢰된 값을 습관적으로 `unknown`으로 되돌리지 않는다.
- type guard는 런타임 검사와 반환 타입이 같은 사실을 증명해야 한다. 타입만 만족시키는 guard를
  만들지 않는다.
- `as` assertion과 non-null assertion은 이미 성립한 불변식을 compiler가 표현하지 못하는 경우의
  마지막 수단이다. 가능한 경우 경계 검증이나 제어 흐름 narrowing으로 대체한다.
- `any`가 필요한 상호운용 경계는 좁게 격리하고 신뢰된 타입으로 즉시 변환한다.

## Reader cost

타입이 정확하더라도 독자가 값의 실제 shape와 흐름을 따라가기 어려워지면 비용이다. helper
type, generic parameter와 wrapper를 추가하기 전에 어떤 잘못된 사용이나 중복을 제거하는지
설명할 수 있어야 한다.
