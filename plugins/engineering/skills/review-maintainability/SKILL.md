---
name: review-maintainability
description: 사용자가 현재 diff나 지정한 코드의 reader load, 변경 이유의 결합, 중복 지식, public surface와 장기 유지보수성을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. 파일 길이만으로 분할을 요구하거나 코드를 수정하지 않는다.
---

# review-maintainability: 유지보수성 리뷰

실제 변경 흐름을 따라가며 다음 수정자가 계약을 이해하고 안전하게 바꾸는 데 드는 비용을 검토한다.

## 절차

1. [공통 리뷰 기준](../../references/review-criteria.md)과
   [공통 우선순위](../../references/code-quality.md#공통-우선순위)를 적용한다. 근거의 적용 이유,
   실제 영향과 최소 수정으로 설명하고 선택적 개선을 새 필수 절차로 만들지 않는다.
2. 루트는 [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)에 따라
   위임·원결과 수집·판정·최종 보고를 마친다. 이미 이 관점의 검토자로 위임받았다면
   요청한 대상만 직접 검토하고 재위임하지 않는다.
3. 여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에
   진행과 근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

### 범위와 방법

- 사용자가 지정한 diff, commit, branch 또는 경로와 판단에 필요한 caller·test를 읽는다.
- entry point에서 주요 data와 control flow를 따라 실제 reader journey를 확인한다.
- 하나의 변경이 서로 독립적인 여러 이유로 같은 module을 흔드는지, domain knowledge가 여러 곳에
  복제됐는지, public surface가 실제 caller보다 넓은지 본다.
- 이름과 구조가 현재 domain contract를 숨기거나, indirection을 여러 번 건너야 동작을 이해할 수
  있는지 확인한다.
- test가 구현 세부사항에 결합되어 안전한 구조 변경을 방해하는지도 실제 사례로 판단한다.

고정 line-count, 함수 길이, nesting 수치만으로 finding을 만들지 않는다. 긴 파일도 한 가지 이유로
함께 바뀌고 흐름이 직접적이면 유지할 수 있다. 작은 파일도 지식이 흩어져 있으면 문제가 될 수
있다.

JavaScript·TypeScript 변경에서는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)를
읽고 반복 guard, optional·boolean soup, DTO 누수, assertion 연쇄와 의미 없는 wrapper가 실제
reader load나 변경 비용을 만드는지 확인한다.

## 결과

finding마다 priority, `path:line`, 독자가 따라야 하는 실제 흐름, 변경 비용이나 결함 가능성,
가장 작은 개선 방향을 적는다. 같은 root cause의 증상은 하나로 합친다. 실행 가능한 finding이
없으면 없다고 말한다.

## 예시

입력: “문서 내보내기 옵션을 바꿀 때 수정 지점이 왜 많은지 검토해 줘.”
`src/export-options.ts:24`의 옵션을 바꾸려면 의미를 더하지 않는 세 forwarding 모듈을
같이 수정해야 한다면 실제 호출 순서와 변경 비용을 적고 불필요한 전달 단계를 줄이도록 제안한다.
대조: 같은 모듈 수라도 각 단계가 파일 형식별 호환 계약을 번역한다면 단순히 파일이 많다는
이유로 합치지 않는다. 확인한 계약과 유지 이유를 보고한다.

## 경계

- 코드를 수정하거나 Git 작업을 하지 않는다.

## 참고 자료

- [공통 리뷰 기준](../../references/review-criteria.md), [공통 코드 품질](../../references/code-quality.md)
- [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)
- [JavaScript·TypeScript 기준](../../references/javascript-typescript-review.md)
