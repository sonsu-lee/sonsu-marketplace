---
name: review-overengineering
description: 사용자가 현재 diff, commit, branch 또는 지정한 코드 변경을 over-engineering, 불필요한 추상화, YAGNI 관점에서 검토해 달라고 명시적으로 요청할 때 사용한다. 코드를 수정하거나 repository 전체를 audit하지 않는다.
---

# Review over-engineering

선택된 변경을 읽기 전용으로 검토하고, 현재 요구사항을 만족하는 데 필요하지 않은 구조만 찾는다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## 범위

- 사용자가 지정한 diff, commit, branch 또는 파일과 그 판단에 필요한 인접 코드만 읽는다.
- 파일을 수정하거나 format, commit, push와 PR 작업을 하지 않는다.
- 일반 style, naming 선호나 줄 수 자체를 finding으로 만들지 않는다.
- correctness나 security 결함을 발견하면 숨기지 말되 over-engineering으로 가장하지 않는다. 깊은
  검증이 필요하면 해당 전문 검토의 범위를 제안한다.

## Finding 기준

다음 질문에 구체적인 코드 근거로 답할 수 있을 때만 보고한다.

- 현재 caller와 요구사항이 쓰지 않는 abstraction, option, variant 또는 extension point인가?
- 표준 library나 이미 존재하는 코드로 같은 계약을 더 직접적으로 표현할 수 있는가?
- forwarding layer, wrapper 또는 indirection이 정책·불변식·재사용을 제공하지 않는가?
- 같은 값에 validation, error wrapping 또는 logging이 중복되는가?
- 제거하면 현재 동작과 상위 우선순위를 유지하면서 이해 비용이 줄어드는가?

가능성만 있는 미래 요구, 개인 취향과 대규모 rewrite는 보고하지 않는다.

## 결과

finding마다 priority, `path:line`, 불필요한 구조, 현재 필요하지 않다는 근거, 가장 작은 제거
방법과 제거 위험을 적는다. 저장소의 priority convention이 없으면 P0은 즉시 차단해야 하는 문제,
P1은 현재 주요 경로의 높은 영향, P2는 일반적인 개선, P3는 낮은 영향으로 사용한다. 실행 가능한
finding이 없으면 없다고 명확히 말한다.
