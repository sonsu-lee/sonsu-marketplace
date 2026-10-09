---
name: domain-shaped-code
description: 사용자가 확인된 제품·도메인 계약이나 trust boundary를 타입, 상태, 경계와 제어 흐름에 직접 반영해 구현하거나 리팩터링해 달라고 명시적으로 요청할 때 사용한다. 도메인 용어 결정, ADR 작성, 일반 기능 구현·디버깅, 읽기 전용 리뷰와 Git 전달에는 사용하지 않는다.
---

# domain-shaped-code: 도메인 구조를 반영한 코드

현재 확인된 계약을 가장 직접적인 코드로 표현한다. 도메인 모델은 목표가 아니라 잘못된 상태,
반복 규칙 또는 분기를 실제로 줄이는 수단이다.

## 절차

구현 전에 [공통 우선순위](../../references/code-quality.md#공통-우선순위)와
[신뢰 경계 기준](../../references/code-quality.md#신뢰-경계에서-보증을-만든다)을 읽고,
확인된 타입·상태와 경계가 금지된 경로를 실제로 제거하는지 대조한다.

여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에 진행과
근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

1. 요청, 기존 동작, 테스트와 인접 코드를 읽고 확정된 계약과 추정 사항을 분리한다.
2. 외부 입력이 신뢰되는 값으로 바뀌는 trust boundary를 찾는다.
3. 실제로 금지해야 하는 상태, 반복되는 규칙과 필요한 variant만 적는다.
4. 현재 흐름을 보존하는 가장 작은 변경을 선택한다. 새 타입이나 추상화는 제거되는 오류나
   중복보다 유지 비용이 낮을 때만 도입한다.
5. 변경 성격에 비례해 검증하고, 실행하지 못한 검증은 실행한 것처럼 보고하지 않는다.

### 도메인 형태

- union과 상태 variant는 현재 계약에 존재하는 경우만 만든다. "나중에 필요할 수 있는" 상태를
  미리 추가하지 않는다.
- primitive wrapper, value object와 branded type은 서로 바뀌면 실제 결함이 되는 같은 형태의
  값을 구분하거나, 생성 시 한 번의 검증으로 반복 검사를 없앨 때만 사용한다.
- 한 번만 쓰이는 구조에 이름을 붙이면 독자가 얻는 도메인 의미가 있는지 확인한다.
- 기존 자료구조와 제어 흐름이 계약을 명확히 표현하면 별도 계층이나 pattern을 추가하지 않는다.

JavaScript·TypeScript를 변경할 때는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)를 읽고,
TypeScript 구현에는 [`references/typescript.md`](references/typescript.md)도 적용한다.
오류 제어 흐름을 변경할 때는 [`references/error-handling.md`](references/error-handling.md)를,
주석을 추가·수정할 때는 [`references/comments.md`](references/comments.md)를 읽는다. logging이나
telemetry가 범위에 포함되면 [`references/logging.md`](references/logging.md)도 적용한다.

## 결과

- 새 상태, 타입, guard와 abstraction 각각이 현재 계약의 구체적인 필요에 연결된다.
- 입력 검증과 내부 guard의 유지·제거 이유를 공통 신뢰 경계 기준에 연결한다.
- 오류는 복구할 수 있는 계층에서 처리되거나 의미를 소유하는 경계에서 번역된다.
- 주석은 코드가 말하는 내용을 반복하지 않고 이유, 불변식 또는 외부 제약을 설명한다.
- 검증 결과는 실제 실행, 정적 확인과 미실행 항목을 구분한다.

## 예시

입력: “파일 복사 옵션에서 덮어쓰기 정책과 확인 여부가 엇갈리지 않게 바꿔 줘.”
외부 설정의 `mode`를 소유 경계에서 해석해
`{ kind: 'skip' } | { kind: 'replace'; confirmed: true }`로 전달한다.
확인되지 않은 `replace` 입력은 경계에서 거부하고, 내부 복사 흐름은 두 상태만 처리한다.
현재 계약에 없는 `merge` 상태나 별도 전략 계층은 추가하지 않는다. 결과에는 제거한 불가능 상태와
실제 실행한 계약 검사·정적 확인·미실행 항목을 구분해 적는다.

## 경계

- 구현과 국소 리팩터링을 담당한다. 계획·TDD·디버깅·branch 완료는 해당 Engineering 흐름을 따른다.
- domain glossary, `CONTEXT.md`, ADR 또는 미결 설계 결정을 새로 만들지 않는다.
- commit·push·ticket·PR을 만들지 않는다.
- 깊은 보안 감사로 확장하지 않는다. 명백한 위험은 보고하고 별도 보안 검토가 필요한 이유와 범위를 밝힌다.

## 참고 자료

- [공통 코드 품질](../../references/code-quality.md)
- [JavaScript·TypeScript 기준](../../references/javascript-typescript-review.md), [TypeScript 구현](references/typescript.md)
- [오류 처리](references/error-handling.md), [주석](references/comments.md), [로깅](references/logging.md)
