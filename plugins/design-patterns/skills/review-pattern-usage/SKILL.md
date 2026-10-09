---
name: review-pattern-usage
description: 사용자가 기존 코드, diff 또는 설계에서 named design pattern의 적용·오용·불필요한 복잡성을 검토해 달라고 명시적으로 요청할 때 사용한다. 일반 코드 리뷰 요청은 대상이 아니다.
---

# Design pattern 사용 검토

현재 코드·diff·설계 계약에서 패턴이 제공하는 guarantee와 비용을 검토하고, 발생 조건이 확인되는 문제와 가장 작은 수정 방향을 보고한다.

## 절차

1. 검토 범위와 기준 revision을 고정하고 코드·diff·설계 계약을 읽는다.
2. 인식한 pattern ID의 family 파일과 [`decision-ready.json`](../../catalog/decision-ready.json)을 읽는다. decision-ready가 아닌 항목은 정답 구조의 근거로 쓰지 않는다.
3. 발생 조건이 있는 문제만 finding으로 보고한다.
   - forces 부재
   - guarantee 위반
   - 비용·실패 모드 미처리
   - scope 혼동
   - 언어·framework 기능 중복
   - baseline보다 복잡하지만 추가 보장이 없음
4. finding마다 다음 항목을 쓴다.
   - severity
   - 위치
   - trigger
   - actual behavior
   - required guarantee
   - 가장 작은 수정 방향

## 결과

- finding 목록을 쓴다.
- 같은 구현의 문제는 패턴 이름이 달라도 finding 하나로 묶는다.
- 구조 변경은 절차 3의 유형 중 하나에 해당할 때만 제안한다. 단순성 취향은 근거로 쓰지 않는다.
- 유효한 finding이 없으면 “finding 없음”이라고 쓴다.
- `no-pattern`은 결함이 아니다.

## 예시

```text
severity: high
위치: payments/client.ts `createCharge`
trigger: idempotency key 없는 결제 POST에 cloud-resilience-retry 적용, 응답 timeout 뒤 재시도
actual behavior: 첫 요청이 처리된 경우 중복 결제
required guarantee: 재시도 안전성(idempotency)
수정 방향: idempotency key를 추가하거나 POST를 재시도 대상에서 제외
```

## 경계

- 대상 artifact를 수정하지 않는다.

## 참고 자료

- [`relationship-types.md`](../../references/relationship-types.md)
- [`pattern-vs-principle.md`](../../references/pattern-vs-principle.md)
