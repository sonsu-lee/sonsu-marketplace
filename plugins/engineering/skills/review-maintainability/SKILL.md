---
name: review-maintainability
description: 사용자가 현재 diff나 지정한 코드의 reader load, 변경 이유의 결합, 중복 지식, public surface와 장기 유지보수성을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. 파일 길이만으로 분할을 요구하거나 코드를 수정하지 않는다.
---

# review-maintainability: 유지보수성 리뷰

실제 변경 흐름을 따라가며 다음 수정자가 계약을 이해하고 안전하게 바꾸는 데 드는 비용을 검토한다.

리뷰를 시작할 때 [공통 리뷰 기준](../../references/review-criteria.md)을 읽고 해당 관점에 적용한다.
근거의 적용 이유, 실제 영향과 최소 수정으로 설명하며 선택적 개선을 새 필수 절차로 만들지 않는다.

루트가 이 요청을 받은 경우에는 [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)에
따라 위임·원결과 수집·판정·최종 보고를 마친다. 아래 관점은 요청한 대상에만 적용한다.
이 관점의 검토자로 이미 위임받았다면 직접 검토하고 재위임하지 않는다.

## 작업 연속성

여러 단계의 작업이나 외부 쓰기를 맡은 주 조정자는 필요할 때 [연속성 참고 자료](../../references/continuity.md)를
읽어 진행과 근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## 범위와 방법

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
없으면 없다고 말한다. 코드를 수정하거나 Git 작업을 하지 않는다.
