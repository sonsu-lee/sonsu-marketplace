---
name: simplify-code
description: 사용자가 코드 변경이나 구현을 가장 단순한 형태로 줄이거나 YAGNI, 삭제 우선, 최소 해법을 명시적으로 요청할 때 사용한다. 일반 구현을 가로채는 지속 모드, 읽기 전용 리뷰, repository 전체 audit에는 사용하지 않는다.
---

# simplify-code: 코드 단순화

현재 요구사항을 만족하는 가장 작은 변경을 구현한다. 단순성은 줄 수 경쟁이 아니라 동작,
개념, dependency와 미래 유지 비용을 줄이는 일이다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## 실행

1. 현재 동작, 요청 범위와 관련 검증을 확인한다.
2. 새 코드를 쓰기 전에 삭제, 기존 코드 재사용, 표준 library와 직접적인 제어 흐름으로 해결할
   수 있는지 본다.
3. 현재 호출자가 하나이고 도메인 의미를 주지 않는 wrapper, interface, factory와 helper는
   inline하거나 만들지 않는다.
4. 확인되지 않은 backend, variant, configuration, hook와 extension point를 추가하지 않는다.
5. 변경 전후의 외부 동작을 필요한 최소 검증으로 확인한다.

## 유지할 것

- 잘못된 상태를 막는 실제 invariant와 trust-boundary validation
- correctness, security, data integrity, accessibility와 compatibility에 필요한 분기
- 여러 곳에서 반복되는 domain rule을 한곳에 두는 abstraction
- 저장소가 이미 선택했고 현재 문제를 직접 해결하는 library와 convention

## 제거 후보

- 한 호출자만 감싸며 의미를 더하지 않는 forwarding layer
- 아직 존재하지 않는 요구사항을 위한 option, state와 callback
- 표준 library나 짧은 직접 코드가 이미 해결하는 자체 framework
- 실제 복구를 하지 않는 `try/catch`, 중복 guard와 log-and-rethrow
- 코드가 그대로 보여 주는 내용을 반복하는 comment

이 스킬은 활성화된 turn에만 적용한다. 다른 요청에 지속되는 persona나 고정 응답 형식을 만들지
않고, commit·push·PR 같은 Git 작업으로 범위를 넓히지 않는다.
