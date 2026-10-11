---
name: audit-overengineering
description: 사용자가 repository 전체 또는 명시한 큰 경로를 over-engineering과 삭제 가능성 관점에서 audit해 달라고 요청할 때 사용한다. 일부 diff review나 코드 수정에는 사용하지 않는다.
---

# audit-overengineering: 과도한 설계 감사

요청한 repository 또는 경로를 읽기 전용으로 조사해 삭제·축소 효과가 큰 구조를 순위화한다.

## 절차

조사를 시작할 때 [공통 리뷰 기준](../../references/review-criteria.md)과
[공통 우선순위](../../references/code-quality.md#공통-우선순위)를 적용한다.
근거의 적용 이유, 실제 영향과 최소 수정으로 설명하며 선택적 개선을 새 필수 절차로 만들지 않는다.

1. 실제 조사 범위, 언어, package와 주요 entry point를 확인한다.
2. 사용처, import, configuration, tests와 runtime wiring을 따라 구조가 실제로 쓰이는지 검증한다.
3. dead layer, 중복 subsystem, 자체 framework, speculative extension surface와 반복 domain rule을
   찾는다.
4. 같은 root cause에서 나온 항목은 합치고, 삭제 효과와 변경 위험을 함께 평가한다.
5. 여러 단계의 주 조정자는 필요할 때 [작업 연속성](../../references/continuity.md)에 진행과
   근거를 기록한다. 단발 작업과 위임된 작업자는 별도 기록을 만들지 않는다.

실제 조사 범위와 제외 범위를 밝힌다. 생성물, vendored code와 외부 submodule은
범위에 포함할 이유가 있을 때 조사한다.

## 결과

우선순위가 높은 순으로 다음을 보고한다.

- priority와 대표 `path:line`
- 구조와 실제 사용 근거
- 제거하거나 단순화해 줄 개념, 코드와 dependency
- 현재 계약에 미치는 영향과 migration 난이도
- 가장 작은 안전한 시작점

구조의 실제 사용과 비용으로 판정한다. 줄 수나 낯선 pattern만으로 finding을 만들지 않는다.
확인되지 않은 사용처나 실행 경로는 결론 대신 `inconclusive`로 구분한다.

지적은 [코멘트 라벨](../../references/review-criteria.md#코멘트-라벨) 형식으로 쓴다.

## 예시

입력: “문서 변환 패키지 전체에서 없앨 수 있는 구조를 찾아 줘.”
export 목록·설정·테스트·runtime wiring에서 미사용임을 확인한 `LegacyRendererRegistry`는
삭제 후보로 보고하고, 먼저 끊을 등록 경로와 제거할 의존성을 적는다.
반면 실제 고객 확장 모듈을 로드하는 registry는 호환 계약을 지키므로 유지한다.
외부 확장 사용 여부를 확인하지 못했다면 삭제 후보로 확정하지 않고 `inconclusive`로 남긴다.

## 경계

- 읽기 전용 조사로 범위를 지키며 파일과 Git 상태를 바꾸지 않는다.
- 일부만 조사했다면 전체 저장소를 조사했다고 보고하지 않는다.

## 참고 자료

- [공통 리뷰 기준](../../references/review-criteria.md)
- [공통 코드 품질](../../references/code-quality.md)
- [작업 연속성](../../references/continuity.md)
- [호스트별 도구](../../references/hosts.md)
