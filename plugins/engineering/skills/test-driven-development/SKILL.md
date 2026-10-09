---
name: test-driven-development
description: 프로덕션 동작 변경·결함 수정·동작에 민감한 리팩터링 또는 자동 검사 추가·확장 전에 검증 방식을 정할 때 사용한다.
---

기대 동작과 검출할 결함을 먼저 정하고 적합한 검증 방식을 선택한다. TDD를 선택하면 의도한 실패를 확인한 뒤 통과하는 최소 구현을 만든다.

## 절차

1. 계획의 흐름 또는 직접 변경의 결과마다 [검증 방식 선택](verification-selection.md)을 읽고 `initial_state`, `action`, `observed_result`, `expected_source`, `fault_example`을 기록한다. 프로덕션 변경 없이 자동 검사를 추가·확장할 때도 적용한다.
2. 필드의 근거가 부족하면 `contract_unresolved`로 두고 기대 동작·재현 조건을 확인한다. 해당 구현과 검사 파일 작성은 확인 뒤 진행한다. 정적 변경에 기존 검사만 실행하면 소비 명령과 기대 결과를 기록한다.
3. 같은 참고 자료의 순서와 조건으로 `verification_mode`를 선택한다. 기존 검출력 확인 뒤 `existing_check`, 기존 경계 확장이 가능하면 `extend_existing_test`, 나머지는 명시된 세 조건에 따라 `one_time_reproduction` 또는 `new_test_file`을 선택한다. 환경 부재는 `blocked`로 기록하며 다른 모드로 우회하지 않는다.
4. 자동 검사 추가·확장은 [RED–GREEN–REFACTOR](test-cycle.md)를 따른다. 기존 검사 재사용은 변경 전후 실행하고 일회성 재현은 명령·구현 전 결과·수정 후 관찰·남은 검사 공백을 남긴다. 이미 작성한 구현의 테스트는 사후 검증으로 구분한다.
5. [좋은 테스트 기준](writing-good-tests.md)으로 독립 기대값·실제 동작·외부 경계 대체의 타당성을 확인한다. 준비가 과도하면 더 작은 소비 경계와 기존 도구를 찾는다. 현재 리비전의 필수 검사에 새 변경·실패가 없으면 검증을 마친다.
6. 여러 단계 작업의 조정자는 [작업 연속성](../../references/continuity.md)을 적용한다.

## 결과

선택한 `verification_mode`와 근거, 현재 리비전, RED의 실제 실패 이유, GREEN·관련 회귀 검사 결과를 보고한다. 실행하지 않은 검사는 `not_run`, 준비 환경 부재는 `blocked`로 구분한다. 일회성 재현에는 남은 자동 검사 공백을 포함한다.

## 예시

입력: “CSV 내보내기에서 쉼표가 있는 셀을 따옴표로 감싸도록 고쳐 줘. 기존 export 경계 테스트를 확장할 수 있어.”

결과: CSV 계약을 `expected_source`로 삼고 `a,b` 셀이 `"a,b"`로 출력되는지를 단언한다. `fault_example`은 따옴표 없는 `a,b`다. `extend_existing_test`를 선택하고 해당 단언의 실패를 확인한 뒤 수정·동일 검사·관련 회귀 결과를 기록한다. 이 예시는 실제 실행 증거가 아니다.

## 경계

- 테스트를 위해 공개 인터페이스나 승인된 설계를 바꿔야 하면 해당 결정을 확인한다. 기존 작업을 일괄 삭제하지 않는다.

## 참고 자료

- [검증 방식 선택](verification-selection.md): 필드·모드·정적 변경 기준의 정본이다.
- [RED–GREEN–REFACTOR](test-cycle.md): 실패 관찰·최소 구현·정리 절차다.
- [좋은 테스트 기준](writing-good-tests.md): 검출력과 외부 경계 대체를 판단한다.
