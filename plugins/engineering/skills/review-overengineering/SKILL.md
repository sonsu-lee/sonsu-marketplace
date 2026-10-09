---
name: review-overengineering
description: 사용자가 현재 diff, commit, branch 또는 지정한 코드 변경을 over-engineering, 불필요한 추상화, YAGNI 관점에서 검토해 달라고 명시적으로 요청할 때 사용한다. 코드를 수정하거나 repository 전체를 audit하지 않는다.
---

# review-overengineering: 과도한 설계 리뷰

선택된 변경을 읽기 전용으로 검토하고, 현재 요구사항을 만족하는 데 필요하지 않은 구조만 찾는다.

## 절차

1. [공통 리뷰 기준](../../references/review-criteria.md)과
   [공통 우선순위](../../references/code-quality.md#공통-우선순위)를 적용한다. 근거의 적용 이유,
   실제 영향과 최소 수정으로 설명하고 선택적 개선을 새 필수 절차로 만들지 않는다.
2. 루트는 [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)에 따라
   위임·원결과 수집·판정·최종 보고를 마친다. 이미 이 관점의 검토자로 위임받았다면
   요청한 대상만 직접 검토하고 재위임하지 않는다.
3. 여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에
   진행과 근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.
4. 아래 범위의 구조를 현재 caller·요구사항과 대조해 제거 효과와 위험을 판정한다.

### 범위

- 사용자가 지정한 diff, commit, branch 또는 파일과 그 판단에 필요한 인접 코드만 읽는다.
- 일반 style, naming 선호나 줄 수 자체를 finding으로 만들지 않는다.
- correctness나 security 결함을 발견하면 숨기지 말되 over-engineering으로 가장하지 않는다. 깊은
  검증이 필요하면 해당 전문 검토의 범위를 제안한다.

### Finding 기준

다음 질문에 구체적인 코드 근거로 답할 수 있을 때만 보고한다.

- 현재 caller와 요구사항이 쓰지 않는 abstraction, option, variant 또는 extension point인가?
- 표준 library나 이미 존재하는 코드로 같은 계약을 더 직접적으로 표현할 수 있는가?
- forwarding layer, wrapper 또는 indirection이 정책·불변식·재사용을 제공하지 않는가?
- 같은 값에 validation, error wrapping 또는 logging이 중복되는가?
- 제거하면 현재 동작과 상위 우선순위를 유지하면서 이해 비용이 줄어드는가?

가능성만 있는 미래 요구, 개인 취향과 대규모 rewrite는 보고하지 않는다.

JavaScript·TypeScript의 타입 생성자 추상화를 검토할 때는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)의
HKT 판단 기준을 적용한다.

## 결과

finding마다 priority, `path:line`, 불필요한 구조, 현재 필요하지 않다는 근거, 가장 작은 제거
방법과 제거 위험을 적는다. 저장소의 priority convention이 없으면 P0은 즉시 차단해야 하는 문제,
P1은 현재 주요 경로의 높은 영향, P2는 일반적인 개선, P3는 낮은 영향으로 사용한다. 실행 가능한
finding이 없으면 없다고 명확히 말한다.

## 예시

입력: “썸네일 변환 변경에 넣은 전략 계층이 필요한지 검토해 줘.”
`src/thumbnail.ts:18`의 factory가 단일 구현만 반환하고 옵션·정책·불변식을 더하지 않으며
현재 caller도 고정되어 있다면 직접 호출로 바꿀 최소 제거 방향과 영향을 보고한다.
대조: 이미지 해상도 제한을 강제하는 같은 형태의 wrapper라면 실제 보장을 제공하므로 유지한다.
미래 변환 엔진의 가능성만으로 전략 계층을 남기거나 대규모 rewrite를 제안하지 않는다.

## 경계

- 파일 수정·format·commit·push·PR 작업을 하지 않는다. 저장소 전체 감사로 범위를 넓히지 않는다.

## 참고 자료

- [공통 리뷰 기준](../../references/review-criteria.md), [공통 코드 품질](../../references/code-quality.md)
- [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)
- [JavaScript·TypeScript 기준](../../references/javascript-typescript-review.md)
