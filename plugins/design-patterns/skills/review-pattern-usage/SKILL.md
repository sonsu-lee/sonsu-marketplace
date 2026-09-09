---
name: review-pattern-usage
description: 사용자가 기존 코드, diff 또는 설계에서 named design pattern의 적용·오용·불필요한 복잡성을 읽기 전용으로 검토해 달라고 명시적으로 요청할 때 사용한다. 일반 코드 리뷰나 자동 수정에는 사용하지 않는다.
---

# Design pattern 사용 검토

현재 artifact를 수정하지 않는다. 선언된 패턴 이름뿐 아니라 실제 구조가 약속하는 guarantee와 비용을
검토하되, 이름이 없다는 이유로 패턴을 강요하지 않는다.

## 검토

1. 검토 범위와 기준 revision을 고정하고 실제 코드·diff·설계 계약을 읽는다.
2. 인식한 pattern ID의 family 파일과 [`../../catalog/decision-ready.json`](../../catalog/decision-ready.json)을
   읽는다. decision-ready가 아니면 이름 유사성만으로 정답 구조를 단정하지 않는다.
3. 발생 조건이 있는 문제만 보고한다: 필요한 forces 부재, guarantee 위반, 비용·실패 모드 미처리,
   scope 혼동, 언어·framework 기본 기능의 중복, 또는 baseline보다 복잡하지만 추가 보장이 없는 경우.
4. 각 finding에 severity, artifact 위치, trigger, actual behavior, required guarantee와 가장 작은 수정
   방향을 적는다. 유효한 finding이 없으면 없다고 보고한다.

`no-pattern`은 결함이 아니다. 단순성 취향만으로 구조를 바꾸거나, 다른 이름의 같은 구현을 중복
지적하거나, 도달하지 않는 가상 경로를 finding으로 만들지 않는다. 관계의 의미는
[`../../references/relationship-types.md`](../../references/relationship-types.md), 패턴과 원칙의 경계는
[`../../references/pattern-vs-principle.md`](../../references/pattern-vs-principle.md)를 따른다.
