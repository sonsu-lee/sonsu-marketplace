---
name: audit-overengineering
description: 사용자가 repository 전체 또는 명시한 큰 경로를 over-engineering과 삭제 가능성 관점에서 audit해 달라고 요청할 때 사용한다. 일부 diff review나 코드 수정에는 사용하지 않는다.
---

# Audit over-engineering

요청한 repository 또는 경로를 읽기 전용으로 조사해 삭제·축소 효과가 큰 구조를 순위화한다.

## 공통 우선순위

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

뒤 순위 때문에 앞 순위를 희생하지 않는다.

## 조사

1. 실제 조사 범위, 언어, package와 주요 entry point를 확인한다.
2. 사용처, import, configuration, tests와 runtime wiring을 따라 구조가 실제로 쓰이는지 검증한다.
3. dead layer, 중복 subsystem, 자체 framework, speculative extension surface와 반복 domain rule을
   찾는다.
4. 같은 root cause에서 나온 항목은 합치고, 삭제 효과와 변경 위험을 함께 평가한다.

일부만 읽고 repository 전체를 audit했다고 말하지 않는다. 생성물, vendored code와 외부 submodule은
범위에 포함한 이유가 없으면 제외하고 제외 사실을 밝힌다.

## 결과

우선순위가 높은 순으로 다음을 보고한다.

- priority와 대표 `path:line`
- 구조와 실제 사용 근거
- 제거하거나 단순화해 줄 개념, 코드와 dependency
- 현재 계약에 미치는 영향과 migration 난이도
- 가장 작은 안전한 시작점

줄 수만 많거나 낯선 pattern이라는 이유로 finding을 만들지 않는다. 확인되지 않은 사용처나 실행
경로는 결론이 아니라 `inconclusive`로 구분한다. 파일을 수정하거나 Git 상태를 바꾸지 않는다.
