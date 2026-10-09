---
name: memory-maintain
description: 공통 로컬 메모리의 중복·충돌·오래된 주장·깨진 출처를 사용자가 명시적으로 점검하거나 정리해 달라고 요청할 때 사용한다.
---

요청 범위의 기억을 현재 근거와 대조해 점검하고 허가된 정리만 반영한다. 구조적 이상 후보와 의미상 필요한 변경을 구분한다.

## 절차

1. 요청 범위를 정한다. 지정이 없으면 현재 프로젝트, 개인 기억이면 `user`로 둔다. [공통 계약](../../references/store-contract.md)의 조회·경계를 적용한다.
2. 이 스킬 디렉터리 기준으로 `python3 ../../scripts/memory_store.py audit --scope project --cwd /absolute/project`를 실행한다. `items` 전체를 열거하고 `get`으로 원문·출처·현재 SHA를 읽는다. `duplicates`·`broken_sources`·`invalid_files`는 점검 후보로 다룬다.
3. 중복 후보의 고유 조건과 출처를 비교한다. 충돌·오래된 주장은 현재 코드·문서·사용자 결정으로 검증하고 깨진 참조는 경로 이동 가능성을 확인한다. 불확실한 항목은 보류한다.
4. 점검 요청은 읽기 전용으로 보고한다. 정리 요청에서 확인한 보정·대체는 [memory-capture](../memory-capture/SKILL.md)의 `UPDATE`·`SUPERSEDE` 흐름으로 반영하거나 `archive ID HASH --scope SCOPE`로 보관한다. 사용자가 정확한 항목의 삭제를 명시했으면 `forget ID HASH --scope SCOPE`를 사용한다.
5. 변경마다 현재 SHA를 조회해 전달하고 [명령별 확인 방법](../../references/store-contract.md#실행과-결과)으로 실제 반영을 재조회한다. 오류는 [실패와 복구](../../references/store-contract.md#실패와-복구)에 따라 처리한다.

## 결과

항목별 ID, 점검 근거, 조치 또는 보류 이유를 보고한다. 점검에서는 제안과 읽기 전용 상태를, 정리에서는 실제 변경·보관·삭제와 재조회 결과를 구분한다.

## 예시

입력:

> 현재 프로젝트 기억의 출처 링크를 점검해 줘.

`audit.broken_sources`가 가리키는 `repo:docs/image-policy.md`의 원문이 `docs/media/policy.md`로 이동했고 같은 보관 조건을 유지하는지 확인한 경우:

```text
후보: 이미지 보관 기억의 repo:docs/image-policy.md 경로 없음
확인: docs/media/policy.md에 같은 보관 조건과 이동 근거가 있음
제안: 같은 주장이므로 UPDATE로 현재 출처 추가
실제 조치: 점검만 요청했으므로 읽기 전용 유지
주의: UPDATE는 출처를 합치므로 예전 경로의 broken_sources가 남을 수 있음
```

현재 출처를 찾을 수 없다면 삭제 대신 “현재 근거 미확인”으로 보류한다.

## 경계

- 실제 파일 삭제는 사용자가 정확한 항목의 삭제를 명시한 경우에만 수행한다. 오래됐거나 검색되지 않는다는 사실만으로 삭제하지 않는다.

## 참고 자료

- [공통 로컬 기억 계약](../../references/store-contract.md): 명령·출력·종료 코드, 다른 호스트·Engineering 기록과 기억 속 명령의 경계
- [memory-capture](../memory-capture/SKILL.md): 보정·대체 저장
