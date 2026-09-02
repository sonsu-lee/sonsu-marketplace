---
name: review-operability
description: 사용자가 현재 diff나 지정한 코드의 error ownership, logging, telemetry, 진단 가능성과 민감정보 노출을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. 특정 observability vendor나 모든 endpoint의 계측을 강제하지 않는다.
---

# Review operability

운영자가 실제 장애 질문에 답하고 올바른 소유 경계에서 대응할 수 있는지 검토한다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## 질문부터 시작

- 어떤 사용자 동작, request 또는 job이 실패했는가?
- dependency 실패와 제품 영향은 어디서 연결되는가?
- retry, timeout, cancellation, 부분 성공과 최종 실패를 구분할 수 있는가?
- 같은 오류가 여러 계층에서 중복 기록되거나 원래 cause가 사라지는가?
- log와 telemetry에 credential, secret, 개인정보 또는 불필요한 원문 payload가 포함되는가?

현재 운영 환경, 기존 logger·metric·trace와 소비되는 dashboard·alert를 확인한 뒤 필요한 signal을
판단한다. 실제 질문이 없으면 모든 endpoint, 함수와 성공 경로에 log를 요구하지 않는다. 분산
요청을 연결할 필요가 없는 코드에 correlation ID를 강제하지 않고, 특정 framework, logger,
OpenTelemetry 또는 vendor로 교체하라고 요구하지 않는다.

## Finding 기준

- 오류를 의미 있게 번역하거나 복구할 계층이 아닌 곳에서 삼키거나 반복 wrapping한다.
- log-and-rethrow 때문에 한 실패가 여러 번 기록되거나 final outcome을 구분할 수 없다.
- 원인, 영향 범위 또는 재시도 상태가 사라져 실제 장애 질문에 답할 수 없다.
- 민감정보가 log, exception message, event attribute에 노출된다.
- signal이 너무 많거나 cardinality가 높아 필요한 사건을 찾기 어렵고 비용 위험이 구체적이다.

## 결과

finding마다 priority, `path:line`, 답할 수 없는 운영 질문 또는 노출되는 데이터, 현재 error·signal
흐름, 가장 작은 수정 방향을 적는다. 추측만 있는 telemetry 요구는 보고하지 않는다. 파일을
수정하거나 Git 작업을 하지 않는다.
