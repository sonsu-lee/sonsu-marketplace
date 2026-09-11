---
name: review-quality
description: 현재 코드·diff·commit·branch를 리뷰해 달라는 일반 요청이나 여러 품질 관점을 아우르는 리뷰에 사용한다. 실제 동작, 구조와 코드 패턴을 읽기 전용으로 검토한다. 한 관점만 지정한 요청, 개발 절차가 선언한 리뷰, 명시적 독립 리뷰어 요청이나 코드 수정에는 사용하지 않는다.
---

# review-quality: 품질 리뷰

요청한 변경을 읽기 전용으로 검토하고 관련 있는 관점만 선택해 같은 원인의 지적은 하나로 합친다.
대상이 생략됐으면 현재 코드·변경 맥락에서 정하고, 서로 다른 대상이 가능할 때만 확인한다.
일반 직접 리뷰는 이 스킬로 완료하며 개발 절차의 리뷰나 명시적인 독립 리뷰어 요청을 대신하지 않는다.

리뷰를 시작할 때 [공통 리뷰 기준](../../references/review-criteria.md)을 읽고 해당 관점에 적용한다.
근거의 적용 이유, 실제 영향과 최소 수정으로 설명하며 선택적 개선을 새 필수 절차로 만들지 않는다.

## 작업 연속성

현재 메인 controller가 여러 단계의 작업을 소유하거나 외부 쓰기를 수행할 때에는 같은 플러그인의
[task-continuity](../task-continuity/SKILL.md)를 적용해 시작·중요한 진행 변화·외부 쓰기 전후를 기록한다.
컴팩션·재개 후에는 그 기록과 현재 근거를 대조한다. 짧은 단발 작업, 위임된 subagent와 fresh reviewer는
별도 기록을 만들지 않으며, 파일 쓰기가 금지되면 checkpoint와 Git exclude도 변경하지 않는다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## Lens 선택

먼저 diff와 관련 호출자·테스트·설정을 읽고 동작, 책임·의존 관계와 코드 패턴에서 어떤 문제가
실제로 존재하는지 판단한다. 아키텍처·패턴은 현재 비용과 필요한 보장으로 검토하고 다음 관점 중
해당하는 것을 선택한다.

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

JavaScript·TypeScript 변경에서는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)를
읽고 현재 diff에 관련된 항목만 적용한다. 특히 nullish 의미, `satisfies`의 compile-time 한계,
trust boundary와 중복 guard, async 실패 경로를 서로 다른 취향 규칙으로 쪼개지 않는다.

## 결과

finding을 priority 순으로 제시한다. 각 finding에는 다음을 포함한다.

- 짧고 구체적인 제목. 적용 관점은 이해에 도움이 될 때 덧붙인다.
- 정확한 `path:line`
- 현재 entry point와 흐름에 근거한 영향
- 문제가 되는 계약, 구조 또는 실패 경로
- 가장 작은 실행 가능한 수정 방향

같은 root cause에서 나온 복잡성, 실패와 logging 증상은 하나의 finding으로 합친다. 실행하지 않은
테스트나 runtime 동작은 확인했다고 말하지 않는다. 실행 가능한 finding이 없으면 없다고 명확히
말하고, 남은 `inconclusive` 항목이 있으면 별도로 구분한다. 파일을 수정하거나 Git 작업을 하지
않는다.
