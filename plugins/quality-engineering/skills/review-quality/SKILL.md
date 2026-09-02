---
name: review-quality
description: 사용자가 현재 diff, commit, branch 또는 지정한 코드에 대해 단순성, 유지보수성, 실패 모드와 운용 가능성을 아우르는 broad quality review를 명시적으로 요청할 때 사용한다. 한 관점만 지정한 요청이나 코드 수정에는 사용하지 않는다.
---

# review-quality: 품질 리뷰

요청한 변경을 읽기 전용으로 검토하되, 관련 있는 quality lens만 선택하고 같은 원인의 finding은
하나로 합친다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## Lens 선택

먼저 diff와 관련 caller·test를 읽고 어떤 질문이 실제로 존재하는지 판단한다.

- **Over-engineering:** 현재 요구사항이 쓰지 않는 abstraction, state, guard와 extension surface
- **Maintainability:** reader journey, 여러 변경 이유, 중복 domain knowledge와 과도한 public surface
- **Failure modes:** 도달 가능한 실패, retry, 부분 성공, concurrency, cleanup과 recovery
- **Operability:** error ownership, 원인 보존, 중복 logging, 실제 운영 질문과 민감정보

모든 lens를 기계적으로 실행하거나 각 lens마다 finding을 만들어 수를 채우지 않는다. 한 가지
관점만 명시한 요청은 해당 전용 review skill의 범위다. 별도 skill이 설치되어 있다고 가정하지
않고 이 기준으로 독립적으로 완료한다.

명백한 correctness, security, data integrity, accessibility 또는 compatibility 문제는 quality
shape보다 먼저 보고한다. 다만 깊은 보안 감사, 제품 결정, 디버깅과 Git 전달 작업으로 범위를
확장하지 않는다.

## 결과

finding을 priority 순으로 제시한다. 각 finding에는 다음을 포함한다.

- 짧고 구체적인 제목과 적용한 lens
- 정확한 `path:line`
- 현재 entry point와 흐름에 근거한 영향
- 문제가 되는 계약, 구조 또는 실패 경로
- 가장 작은 실행 가능한 수정 방향

같은 root cause에서 나온 복잡성, 실패와 logging 증상은 하나의 finding으로 합친다. 실행하지 않은
테스트나 runtime 동작은 확인했다고 말하지 않는다. 실행 가능한 finding이 없으면 없다고 명확히
말하고, 남은 `inconclusive` 항목이 있으면 별도로 구분한다. 파일을 수정하거나 Git 작업을 하지
않는다.
