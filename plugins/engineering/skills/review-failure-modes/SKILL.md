---
name: review-failure-modes
description: 사용자가 현재 diff나 지정한 코드의 도달 가능한 실패 경로, retry, 부분 성공, 동시성, cleanup과 복구 동작을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. penetration test나 repository-wide security scan에는 사용하지 않는다.
---

> Modified from OpenAI's `codex-plugin-cc` adversarial review prompt under Apache-2.0.
> See [`../../UPSTREAM.md`](../../UPSTREAM.md) and [`../../NOTICE`](../../NOTICE).

# review-failure-modes: 실패 모드 리뷰

현재 entry point, caller와 data flow에서 실제로 도달 가능한 실패만 검토한다.

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

## 절차

1. 사용자가 지정한 diff, commit, branch 또는 경로와 실제 entry point를 확인한다.
2. 정상 경로와 함께 입력 거부, dependency 실패, timeout, cancellation, retry, 부분 write,
   duplicate delivery, concurrent update와 cleanup 경로를 따라간다.
3. 실패가 사용자, 데이터 또는 다음 실행에 미치는 영향을 확인한다.
4. 기존 validation, transaction, idempotency, retry policy와 caller recovery가 위험을 이미 막는지
   확인한다.
5. 재현 조건과 코드 근거가 있는 항목만 보고한다.

단지 이론적으로 가능한 hardware failure, 현재 호출되지 않는 dead code와 근거 없는 공격
시나리오는 finding이 아니다. 명백한 security 위험은 숨기지 않지만 exploit 개발이나 광범위한
취약점 탐색으로 확장하지 않고 전문 security 검토가 필요한 범위를 밝힌다.

JavaScript·TypeScript 변경에서는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)를
읽고 nullish fallback이 계약 위반을 숨기는지, `forEach(async ...)`와 floating promise가 완료를
앞당기는지, `Promise.all` 이후 부분 write·retry가 실제로 도달하는지 확인한다.

## 결과

finding마다 priority, `path:line`, 도달 경로, trigger, 관찰 가능한 영향, 기존 방어가 부족한 이유와
가장 작은 수정 방향을 적는다. 실행이나 재현을 하지 않았다면 정적 추론임을 표시한다. 증거가
부족한 항목은 finding 대신 `inconclusive`로 구분한다. 파일을 수정하거나 Git 작업을 하지 않는다.
