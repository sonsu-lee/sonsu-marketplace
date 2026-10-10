---
name: review-operability
description: 사용자가 현재 diff나 지정한 코드의 error ownership, logging, telemetry, 진단 가능성과 민감정보 노출을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. 특정 observability vendor나 모든 endpoint의 계측을 강제하지 않는다.
---

# review-operability: 운용 가능성 리뷰

운영자가 실제 장애 질문에 답하고 올바른 소유 경계에서 대응할 수 있는지 검토한다.

## 절차

1. [공통 리뷰 기준](../../references/review-criteria.md)과
   [공통 우선순위](../../references/code-quality.md#공통-우선순위)를 적용한다. 근거의 적용 이유,
   실제 영향과 최소 수정으로 설명하고 선택적 개선을 새 필수 절차로 만들지 않는다.
2. 루트는 [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)에 따라
   위임·원결과 수집·판정·최종 보고를 마친다. 이미 이 관점의 검토자로 위임받았다면
   요청한 대상만 직접 검토하고 재위임하지 않는다.
3. 여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에
   진행과 근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.
4. 아래 운영 질문에 기존 signal이 답하는지 확인하고 구체적인 공백만 finding으로 보고한다.

### 질문부터 시작

- 어떤 사용자 동작, request 또는 job이 실패했는가?
- dependency 실패와 제품 영향은 어디서 연결되는가?
- retry, timeout, cancellation, 부분 성공과 최종 실패를 구분할 수 있는가?
- 같은 오류가 여러 계층에서 중복 기록되거나 원래 cause가 사라지는가?
- log와 telemetry에 credential, secret, 개인정보 또는 불필요한 원문 payload가 포함되는가?

현재 운영 환경, 기존 logger·metric·trace와 소비되는 dashboard·alert를 확인한 뒤 필요한 signal을
판단한다. 실제 질문이 없으면 모든 endpoint, 함수와 성공 경로에 log를 요구하지 않는다. 분산
요청을 연결할 필요가 없는 코드에 correlation ID를 강제하지 않고, 특정 framework, logger,
OpenTelemetry 또는 vendor로 교체하라고 요구하지 않는다.

### Finding 기준

- 오류를 의미 있게 번역하거나 복구할 계층이 아닌 곳에서 삼키거나 반복 wrapping한다.
- log-and-rethrow 때문에 한 실패가 여러 번 기록되거나 final outcome을 구분할 수 없다.
- 원인, 영향 범위 또는 재시도 상태가 사라져 실제 장애 질문에 답할 수 없다.
- 민감정보가 log, exception message, event attribute에 노출된다.
- signal이 너무 많거나 cardinality가 높아 필요한 사건을 찾기 어렵고 비용 위험이 구체적이다.

## 결과

finding마다 priority, `path:line`, 답할 수 없는 운영 질문 또는 노출되는 데이터, 현재 error·signal
흐름, 가장 작은 수정 방향을 적는다. 실제 운영 질문과 연결되지 않는 telemetry 요구는 제외한다.

## 예시

입력: “백업 복구 작업의 오류 로그를 검토해 줘.”
`src/restore.ts:61`에서 인증 실패를 기록하며 서명된 다운로드 URL 전체가 로그에 남는다면
노출되는 credential, 로그 소비 경로와 URL에서 비밀 쿼리를 제거하는 최소 수정을 보고한다.
대조: 기존 작업 ID와 최종 실패 기록으로 어떤 복구가 실패했는지 이미 답할 수 있다면
모든 함수의 시작·종료 로그나 새 vendor 도입을 요구하지 않는다.

## 경계

- 파일을 수정하거나 Git 작업을 하지 않는다.

## 참고 자료

- [공통 리뷰 기준](../../references/review-criteria.md), [공통 코드 품질](../../references/code-quality.md)
- [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)
