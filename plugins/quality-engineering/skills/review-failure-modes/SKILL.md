---
name: review-failure-modes
description: 사용자가 현재 diff나 지정한 코드의 도달 가능한 실패 경로, retry, 부분 성공, 동시성, cleanup과 복구 동작을 읽기 전용으로 검토해 달라고 요청할 때 사용한다. penetration test나 repository-wide security scan에는 사용하지 않는다.
---

> Modified from OpenAI's `codex-plugin-cc` adversarial review prompt under Apache-2.0.
> See [`../../UPSTREAM.md`](../../UPSTREAM.md) and [`../../NOTICE`](../../NOTICE).

# Review failure modes

현재 entry point, caller와 data flow에서 실제로 도달 가능한 실패만 검토한다.

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

## 결과

finding마다 priority, `path:line`, 도달 경로, trigger, 관찰 가능한 영향, 기존 방어가 부족한 이유와
가장 작은 수정 방향을 적는다. 실행이나 재현을 하지 않았다면 정적 추론임을 표시한다. 증거가
부족한 항목은 finding 대신 `inconclusive`로 구분한다. 파일을 수정하거나 Git 작업을 하지 않는다.
