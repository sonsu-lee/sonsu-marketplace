---
name: select-design-patterns
description: 실제 코드나 설계에서 반복 문제, 충돌하는 forces와 필요한 보장이 확인되어 named design pattern 선택이 필요한 경우에 사용한다. 일반 구현, 사소한 분기, 단순 리팩터링과 원칙 설명에는 사용하지 않는다.
---

# Design pattern 선택

패턴 이름보다 현재 문제와 보장을 먼저 고정한다. 실제 코드·계약·운영 제약을 읽을 수 있으면 확인하고,
요청 문구만으로 반복성이나 분산 시스템 보장을 추측하지 않는다. 패턴 선택 자체는 파일 수정 권한이 아니다.

## 판단

1. [`../../references/pattern-vs-principle.md`](../../references/pattern-vs-principle.md)로 pattern,
   principle, idiom, framework 기능과 직접 해법을 구분한다.
2. [`../../catalog/index.json`](../../catalog/index.json)에서 관련 family만 고르고 해당 family 파일과
   [`../../catalog/decision-ready.json`](../../catalog/decision-ready.json)의 같은 ID를 읽는다.
3. 반복 문제, forces, 표준 기능, baseline 한계, 필요한 guarantee, 수용할 cost와 검증 방법을 확인한다.
4. 추천은 `decision-ready` 항목으로 제한한다. 최대 3개 후보에서 primary는 기본 1개이며 supporting은
   primary의 보장에 필요할 때만 선택한다. indexed 이름만 일치하면 `insufficient-evidence`다.
5. [`../../references/selection-contract.md`](../../references/selection-contract.md)의 형식으로 결과를 낸다.

외부 설명을 추가로 확인하거나 catalog 성숙도를 변경할 때에는
[`../../references/source-policy.md`](../../references/source-policy.md)를 읽는다.

직접 해법이나 플랫폼 기능이 충분하면 `no-pattern`이 정상 결과다. 패턴 이름을 class에 붙이는 것은
의도를 더 명확하게 할 때만 제안한다. 언어별 구현은 [`../../references/language-realization.md`](../../references/language-realization.md),
관계 해석은 [`../../references/relationship-types.md`](../../references/relationship-types.md)를 따른다.

분산·메시징 패턴은 delivery, ordering, consistency, idempotency, recovery를 모두 확인한다.
확인되지 않은 항목을 “기본 보장”으로 간주하지 않는다.
