---
name: select-design-patterns
description: 실제 코드나 설계에서 반복 문제, 충돌하는 forces와 필요한 보장을 확인해 named design pattern의 필요 여부와 형태를 결정할 때 사용한다. 일반 구현·단순 리팩터링이나 원칙 설명 요청은 대상이 아니다.
---

# Design pattern 선택

현재 코드·계약·운영 제약에서 문제와 필요한 보장을 확인하고 그 보장을 가장 작게 제공하는 해법을 고른다. 직접 해법이나 플랫폼 기능이 충분하면 `no-pattern`을 결과로 낸다.

## 절차

1. 읽을 수 있는 코드·계약·운영 제약을 확인한다. 요청 문구로만 주어진 반복성과 분산 보장은 미확인 사실로 기록한다. 사용자가 확인된 사실로 제공한 근거는 근거로 사용한다.
2. [`../../references/pattern-vs-principle.md`](../../references/pattern-vs-principle.md)로 문제의 종류를 구분하고 baseline 해법을 먼저 적는다.
3. [`../../catalog/index.json`](../../catalog/index.json)에서 관련 family를 고르고, family 파일과 [`../../catalog/decision-ready.json`](../../catalog/decision-ready.json)에서 같은 ID를 읽는다.
4. 다음 항목을 확인한다.
   - 반복 문제
   - forces
   - 표준 기능
   - baseline 한계
   - 필요한 guarantee
   - 수용할 cost
   - 검증 방법

   분산·메시징 문제는 delivery, ordering, consistency, idempotency, recovery를 각각 확인하고, 확인하지 못한 항목은 빠진 사실로 기록한다.
5. 패턴은 `decision-ready` 항목에서 고른다.
   - 후보는 최대 3개다.
   - primary는 0–1개다.
   - supporting은 primary의 보장에 필요할 때만 둔다.
   - indexed 이름만 일치하면 `insufficient-evidence`로 판정한다.
6. 패턴 이름을 identifier에 넣는 것은 의도가 더 분명해질 때만 제안한다.
   - 언어별 구현은 [`../../references/language-realization.md`](../../references/language-realization.md)를 따른다.
   - 관계는 [`../../references/relationship-types.md`](../../references/relationship-types.md)를 따른다.

## 결과

[`../../references/selection-contract.md`](../../references/selection-contract.md) 형식으로 쓴다.

## 예시

입력:

> 외부 결제 API 장애 때 요청마다 30초 timeout까지 대기해 worker가 고갈된다. 장애 중에는 즉시 실패하고, 복구되면 자동으로 다시 호출해야 한다.

결과:

```text
Decision: use
Scope: 결제 API를 호출하는 HTTP client 경계
Observed forces: 장애 중 요청마다 30초 대기로 worker 고갈, 복구 뒤 자동 재개 필요
Baseline: timeout 단축 — 장애가 이어지는 동안 호출 비용은 줄지 않음
Candidates: cloud-resilience-circuit-breaker — 장애 중 호출 차단, 상태 관리 비용; cloud-resilience-bulkhead — 다른 작업 보호, worker 고갈 자체는 남음
Selected: cloud-resilience-circuit-breaker
Rejected: cloud-resilience-bulkhead — 결제 호출의 대기 시간을 줄이지 않음; cloud-resilience-retry — 장애 중 호출을 늘림
Implementation shape: 사용 중인 HTTP client나 resilience 라이브러리의 breaker 정책
Verification: 연속 실패 후 즉시 실패, half-open 시험 호출 성공 후 정상 호출 복귀
Sources: 결제 client 호출 코드와 장애 기록; cloud-resilience-circuit-breaker
```

## 경계

- 선택 결과는 파일 수정 권한이 아니다.

## 참고 자료

- 외부 설명을 확인하거나 성숙도를 바꿀 때는 [`../../references/source-policy.md`](../../references/source-policy.md)를 읽는다.
