---
name: simplify-code
description: 사용자가 코드 변경이나 구현을 가장 단순한 형태로 줄이거나 YAGNI, 삭제 우선, 최소 해법을 명시적으로 요청할 때 사용한다. 일반 구현을 가로채는 지속 모드, 읽기 전용 리뷰, repository 전체 audit에는 사용하지 않는다.
---

# simplify-code: 코드 단순화

현재 요구사항을 만족하는 가장 작은 변경을 구현한다. 단순성은 줄 수 경쟁이 아니라 동작,
개념, dependency와 미래 유지 비용을 줄이는 일이다.

## 절차

단순화 전에 [공통 우선순위](../../references/code-quality.md#공통-우선순위)와
[공통 코드 품질 원칙](../../references/code-quality.md)을 읽는다. 확인된 도메인 상태와 실제
trust boundary의 보증은 유지하고, 그 보증을 반복하는 내부 guard와 추측성 abstraction을 구분한다.

여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에 진행과
근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

1. 현재 동작, 요청 범위와 관련 검증을 확인한다.
2. 새 코드를 쓰기 전에 삭제, 기존 코드 재사용, 표준 library와 직접적인 제어 흐름으로 해결할
   수 있는지 본다.
3. 현재 호출자가 하나이고 도메인 의미를 주지 않는 wrapper, interface, factory와 helper는
   inline하거나 만들지 않는다.
4. 확인되지 않은 backend, variant, configuration, hook와 extension point를 추가하지 않는다.
5. 변경 전후의 외부 동작을 필요한 최소 검증으로 확인한다.

### 유지할 것

- 잘못된 상태를 막는 실제 invariant와 trust-boundary validation
- correctness, security, data integrity, accessibility와 compatibility에 필요한 분기
- 여러 곳에서 반복되는 domain rule을 한곳에 두는 abstraction
- 저장소가 이미 선택했고 현재 문제를 직접 해결하는 library와 convention

### 제거 후보

- 한 호출자만 감싸며 의미를 더하지 않는 forwarding layer
- 아직 존재하지 않는 요구사항을 위한 option, state와 callback
- 표준 library나 짧은 직접 코드가 이미 해결하는 자체 framework
- 실제 복구를 하지 않는 `try/catch`, 중복 guard와 log-and-rethrow
- 코드가 그대로 보여 주는 내용을 반복하는 comment

JavaScript·TypeScript를 단순화할 때는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)를
읽는다. 외부 검증을 제거하거나 assertion으로 덮지 말고, 이미 검증된 내부 값의 반복 guard,
optional·boolean soup와 의미 없는 type wrapper를 우선 줄인다.

## 결과

줄인 개념·의존성·중복, 유지한 계약과 보장, 변경 전후의 관찰 결과를 보고한다.
실제 실행한 검증과 미실행 항목을 구분하며 요청하지 않은 고정 응답 양식을 추가하지 않는다.

## 예시

입력: “아카이브 파일명 처리의 wrapper를 줄이되 경로 탈출 방지는 유지해 줘.”
변경 전에는 `extract → NameService → NameFactory → validateArchivePath`를 거친다.
두 중간 계층이 전달만 한다는 근거를 확인하면 `extract → validateArchivePath`로 줄인다.
외부 아카이브 항목의 `../`·절대 경로를 거부하는 검증과 회귀 검사는 그대로 남긴다.
검증까지 없애거나 타입 assertion으로 대체하는 변경은 같은 동작을 보존한 단순화가 아니다.

## 경계

- 활성화된 turn의 요청에만 적용하며 다른 요청에 지속되는 persona로 만들지 않는다.
- commit·push·PR 같은 Git 작업으로 범위를 넓히지 않는다.

## 참고 자료

- [공통 코드 품질](../../references/code-quality.md)
- [JavaScript·TypeScript 기준](../../references/javascript-typescript-review.md)
- [작업 연속성](../../references/continuity.md)
