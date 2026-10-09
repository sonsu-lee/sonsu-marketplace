---
name: review-failure-modes
description: 사용자가 현재 diff나 지정한 코드의 도달 가능한 실패 경로, retry, 부분 성공, 동시성, cleanup과 복구 동작을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. penetration test나 repository-wide security scan에는 사용하지 않는다.
---

> Modified from OpenAI's `codex-plugin-cc` adversarial review prompt under Apache-2.0.
> See [`../../UPSTREAM.md`](../../UPSTREAM.md) and [`../../NOTICE`](../../NOTICE).

# review-failure-modes: 실패 모드 리뷰

현재 entry point, caller와 data flow에서 실제로 도달 가능한 실패만 검토한다.

## 절차

1. [공통 리뷰 기준](../../references/review-criteria.md)과
   [공통 우선순위](../../references/code-quality.md#공통-우선순위)를 적용한다. 근거의 적용 이유,
   실제 영향과 최소 수정으로 설명하고 선택적 개선을 새 필수 절차로 만들지 않는다.
2. 루트는 [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)에 따라
   위임·원결과 수집·판정·최종 보고를 마친다. 이미 이 관점의 검토자로 위임받았다면
   요청한 대상만 직접 검토하고 재위임하지 않는다.
3. 여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에
   진행과 근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

### 실패 경로 조사

1. 사용자가 지정한 diff, commit, branch 또는 경로와 실제 entry point를 확인한다.
2. 정상 경로와 함께 입력 거부, dependency 실패, timeout, cancellation, retry, 부분 write,
   duplicate delivery, concurrent update와 cleanup 경로를 따라간다.
3. 실패가 사용자, 데이터 또는 다음 실행에 미치는 영향을 확인한다.
4. 기존 validation, transaction, idempotency, retry policy와 caller recovery가 위험을 이미 막는지
   확인한다.
5. 재현 조건과 코드 근거가 있는 항목만 보고한다.

현재 도달 경로와 구체적 영향으로 판정한다. 이론적인 hardware failure, 호출되지 않는 dead
code와 근거 없는 공격 시나리오는 finding에서 제외한다.

JavaScript·TypeScript 변경에서는
[`../../references/javascript-typescript-review.md`](../../references/javascript-typescript-review.md)를
읽고 nullish fallback이 계약 위반을 숨기는지, `forEach(async ...)`와 floating promise가 완료를
앞당기는지, `Promise.all` 이후 부분 write·retry가 실제로 도달하는지 확인한다.

## 결과

finding마다 priority, `path:line`, 도달 경로, trigger, 관찰 가능한 영향, 기존 방어가 부족한 이유와
가장 작은 수정 방향을 적는다. 실행이나 재현을 하지 않았다면 정적 추론임을 표시한다. 증거가
부족한 항목은 finding 대신 `inconclusive`로 구분한다.

## 예시

입력: “보고서 다운로드 취소 때 임시 파일이 남는지 봐 줘.”
`src/export.ts:48`에서 취소 예외가 cleanup 이전에 빠져나가고 호출자도 파일을 지우지 않는
경로가 확인되면, 취소 trigger·디스크 잔류 영향·`finally`로 옮길 최소 수정 방향을 보고한다.
대조: 같은 임시 파일을 caller의 `finally`가 모든 종료 경로에서 제거한다면 중복 cleanup
추가를 요구하지 않는다. 실행하지 않았다면 두 판정 모두 정적 추론임을 표시한다.

## 경계

- 파일을 수정하거나 Git 작업을 하지 않는다.
- 명백한 security 위험은 보고하되 exploit 개발·광범위한 취약점 탐색 대신 전문 검토가 필요한 범위를 밝힌다.

## 참고 자료

- [공통 리뷰 기준](../../references/review-criteria.md), [공통 코드 품질](../../references/code-quality.md)
- [집중 리뷰 실행](../../references/independent-review.md#집중-리뷰-진입)
- [JavaScript·TypeScript 기준](../../references/javascript-typescript-review.md)
