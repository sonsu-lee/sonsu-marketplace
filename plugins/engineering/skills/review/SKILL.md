---
name: review
description: 현재 코드·diff·commit·branch·PR의 일반 리뷰, 명시적으로 요청한 독립 리뷰, 개발 중 필요한 전체 변경 리뷰에 사용한다. 같은 불변 입력을 받은 새 검토자 5명의 결과를 근거로 통합한다. PR 리뷰는 별도 세션·워크트리에서 병렬 검토 후 중복을 제거해 게시하며 로컬 전용·게시 금지는 우선한다. 한 관점만 지정한 집중 리뷰와 명시적인 PR 심층·다중 리뷰, 코드 수정에는 사용하지 않는다.
---

# review: 품질 리뷰

요청한 변경을 읽기 전용으로 검토하고 새 검토자들의 결과에서 근거가 확인된 지적을 통합한다.
대상이 생략됐으면 현재 코드·변경 맥락에서 정하고, 서로 다른 대상이 가능할 때만 확인한다.
직접 요청한 일반 리뷰와 개발 단계의 필수 독립 리뷰는 이 스킬로 완료한다. 개발 단계의
리뷰는 해당 작업에서 선언한 검사·근거와 연결하지만, 리뷰 전용 요청에는 구현 계획이나
작업 게이트를 추가하지 않는다.

리뷰를 시작할 때 [공통 리뷰 기준](../../references/review-criteria.md)을 읽고 해당 관점에 적용한다.
근거의 적용 이유, 실제 영향과 최소 수정으로 설명하며 선택적 개선을 새 필수 절차로 만들지 않는다.

## 작업 연속성

여러 단계의 작업이나 외부 쓰기를 맡은 주 조정자는 필요할 때 [연속성 참고 자료](../../references/continuity.md)를
읽어 진행과 근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

PR URL만으로 심층 리뷰를 선택하지 않는다. 사용자가 PR의 심층·다중 리뷰를 요청했거나 `review-pr`를 직접 지정하면 해당 스킬의 범위다.

PR 리뷰를 요청받으면 [PR 리뷰 실행과 게시](../../references/pr-review-execution.md)를 먼저 읽고
대상 SHA 고정, 리뷰어별 별도 워크트리·병렬 세션, 일시 실행 오류 재시도와 통합 `COMMENT` 게시를
수행한다. 일반 리뷰의 기본 Luna xhigh 5명은 유지한다. 로컬 전용·게시 금지 요청은 보고서로 완료한다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

고정 artifact를 받아 reviewer로 위임된 실행이면 직접 검토하고 결과를 반환한다. 아래 할당은
root 조정자만 수행하며 reviewer는 추가 agent를 생성하지 않는다. 실행·모델·관측 계약은
[독립 리뷰 실행 절차](../../references/independent-review.md)를 따른다.

## 기본 실행

1. 대상 코드·diff·commit·branch, 관련 caller·test·설정과 확인된 계약을 한 번 수집한다.
2. 대상 revision 또는 working-tree digest, 필요한 파일과 공통 리뷰 기준을 하나의 불변 artifact로
   고정한다. 모든 쓰기가 금지된 요청에서는 파일을 만들지 않고 동일한 frozen 내용을 각 호출
   입력에 그대로 전달한다.
3. 새 `gpt-5.6-luna` xhigh 검토자 5명을 기본값으로 호출한다. 이전 검토 대화를 전달하지 않고,
   모두에게 같은 artifact와 공통 기준을 주며 전체 변경에서 실제 문제가 있는 관점을 찾게 한다.
4. 각 후보를 현재 artifact의 코드와 계약에 다시 연결하고, 같은 root cause를 합쳐 최종 결과를
   작성한다. 다수결로 채택하거나 기각하지 않는다.

사용자가 검토자 수·모델·추론 수준을 지정하면 그 값을 따른다. Codex 일시 실행 오류에는
위 공통 문서의 재시도 규칙을 적용한다. 명시적으로 사용할 수 없는 검토자는 다른
설정으로 조용히 대체하지 않고 실제 실행 수와 `not_run`을 보고한다. 이 리뷰를 위해 구현 계획,
작업 DAG, 수정 agent나 완료 gate를 만들지 않는다. 소스 수정·commit·push는 하지 않는다.
PR 요청의 검토용 fetch·별도 워크트리와 결과 게시는 공통 PR 계약에 따른다.

## Lens 선택

먼저 diff와 관련 호출자·테스트·설정을 읽고 동작, 책임·의존 관계와 코드 패턴에서 어떤 문제가
실제로 존재하는지 판단한다. 아키텍처·패턴은 현재 비용과 필요한 보장으로 검토하고 다음 관점 중
해당하는 것을 선택한다.

- **Over-engineering:** 현재 요구사항이 쓰지 않는 abstraction, state, guard와 extension surface
- **Maintainability:** reader journey, 여러 변경 이유, 중복 domain knowledge와 과도한 public surface
- **Failure modes:** 도달 가능한 실패, retry, 부분 성공, concurrency, cleanup과 recovery
- **Operability:** error ownership, 원인 보존, 중복 logging, 실제 운영 질문과 민감정보

검토자에게 lens를 미리 나눠 주거나 모든 lens를 기계적으로 실행하지 않는다. 각 lens마다 finding을
만들어 수를 채우지 않는다. 한 가지
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
말하고, 남은 `inconclusive` 항목이 있으면 별도로 구분한다. 대상 파일은 수정하지 않는다.
PR 게시 대상이면 공통 게시 계약으로 원격 결과를 확인하고 URL을 반환한다.
