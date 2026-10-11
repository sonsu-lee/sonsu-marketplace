# Logging 정책

log와 telemetry는 실제 운영 질문에 답하기 위해 만든다. 모든 endpoint, 함수 또는 예외를
기록하는 것이 목표가 아니다.

## 질문부터 시작한다

먼저 운영자가 물을 구체적인 질문을 적는다. 예:

- 어떤 요청 또는 job이 실패했고 사용자가 영향을 받았는가?
- retry가 진행 중인지, 최종 실패인지, 중복 처리가 있었는가?
- 외부 dependency의 지연이나 오류가 어느 제품 동작에 영향을 주었는가?

질문에 답하는 데 필요한 event, field와 level만 추가한다. dashboard나 alert가 실제로 소비하지
않는 high-cardinality field와 성공 log를 관성적으로 만들지 않는다.

## Event 소유권

- 오류를 최종 처리하거나 사용자 영향이 확정되는 경계에서 한 번 기록한다.
- log 후 같은 오류를 그대로 throw하여 중복 기록하지 않는다.
- 예외 object, stack과 원인 관계를 문자열로 평탄화하지 말고 runtime 또는 telemetry 표준이
  지원하는 구조화된 field로 보존한다.
- business event와 diagnostic log를 구분한다. metric이 더 직접적인 질문에는 log를 대신 쓰지
  않는다.
- correlation 또는 trace identifier는 여러 비동기 경계나 서비스에서 실제 요청을 연결해야 할
  때 사용한다. 단일 프로세스의 단순 흐름에 무조건 강제하지 않는다.

## 데이터 안전

- password, token, session secret, authorization header와 credential을 기록하지 않는다.
- 개인정보와 원문 payload는 질문에 반드시 필요하고 보존·접근 정책이 명확할 때만 기록한다.
- 민감한 식별자는 제거, 축약, hashing 또는 별도 접근 통제를 검토한다.
- logging 실패가 주 제품 흐름의 성공을 불필요하게 막지 않게 한다.

특정 logger, web framework, OpenTelemetry 또는 vendor는 저장소가 이미 선택했거나 요구사항이
있을 때만 사용한다.
