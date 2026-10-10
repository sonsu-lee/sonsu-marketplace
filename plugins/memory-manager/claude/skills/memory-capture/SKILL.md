---
name: memory-capture
description: 사용자가 명시적으로 기억하거나 저장해 달라고 요청한 정보 또는 정확히 선택한 기존 호스트 메모리·대기 후보를 검증해 공통 로컬 메모리에 저장할 때 사용한다.
---

출처와 적용 범위를 확인한 정보를 기존 기억과 비교해 저장한다. 자동 수집 후보의 검토와 장기 기억 확정을 구분한다.

## 절차

1. 사용자의 저장 요청 또는 정확한 후보 선택을 확인한다. [공통 계약](../../references/store-contract.md)의 범위·조회·경계를 적용하고 선택한 기존 호스트 기억은 읽기 전용으로 읽는다. 대기 후보는 `python3 ../../scripts/memory_store.py pending --cwd /absolute/project`로 조회한다. 상대 스크립트 경로는 이 스킬 디렉터리 기준이다.
2. 출처와 원문을 확인하고 `project` 또는 `user` 범위를 정한다. 다른 프로젝트의 정보는 보류한다. 같은 범위에서 `search`한 뒤 관련 항목을 `get`으로 읽는다.
3. [저장 판정과 확인](../../references/store-contract.md#저장-판정과-확인)에 따라 `ADD`·`UPDATE`·`SUPERSEDE`·`NOOP`을 고른다. 대체 근거가 추측뿐이면 보류한다.
4. 안전한 파일 또는 stdin으로 JSON을 `python3 ../../scripts/memory_store.py put --cwd /absolute/project`에 전달한다. 반환 ID를 `get`으로 재조회해 내용·범위·출처를 확인한다. 충돌이나 완료 여부가 불명확한 오류는 [실패와 복구](../../references/store-contract.md#실패와-복구)를 따른다.
5. 선택한 자동 후보의 저장·거부·`NOOP` 판단이 끝나면 `pending`에서 받은 ID와 SHA로 `dismiss CANDIDATE_ID EXPECTED_SHA256 --cwd /absolute/project`를 실행한다.

## 결과

판정과 근거, 범위·출처, 실제 저장 여부를 보고한다. 저장했다면 반환된 `id`·`sha256`과 `get` 확인 결과를 함께 적는다. 보류·거부·`NOOP`은 저장 완료와 구분하고 후보를 처리했다면 대기함 제거 결과도 적는다. 도구 오류는 완료로 보고하지 않고 재조회한 실제 상태를 쓴다.

## 예시

입력:

> 이미지 원본은 30일 보관하고 썸네일만 계속 보관한다는 결정을 현재 프로젝트 기억에 저장해 줘. 근거는 docs/media-policy.md야.

원문을 확인하고 같은 범위에 해당 기억이 없으면 다음 JSON을 `put`에 전달한다.

```json
{"decision":"ADD","scope":"project","title":"이미지 보관 기간","body":"이미지 원본은 30일 보관하고 썸네일은 계속 보관한다.","sources":["repo:docs/media-policy.md"]}
```

결과 형식 예시(실행 시 ID·SHA는 도구 반환값을 쓴다):

```text
판정: ADD — 현재 정책에서 확인한 새 사실
범위·출처: project · repo:docs/media-policy.md
저장: put의 id와 sha256 수신
확인: get <반환 id> --scope project에서 같은 sha256과 본문·범위·출처 확인
후보 처리: 직접 저장 요청이므로 dismiss 대상 없음
```

대조 입력이 “대기 후보가 있네”뿐이면 저장 승인이 없으므로 정본에 쓰지 않고 선택할 항목을 확인한다.

## 경계

- 장기 기억 저장은 명시적 저장 요청이나 정확한 후보 선택에 한정한다. 후보의 존재나 자동 수집 옵트인은 확정 저장 권한이 아니다.
- 비밀·자격 증명·전문 transcript·원시 도구 출력은 저장하지 않는다.

## 참고 자료

- [공통 로컬 기억 계약](../../references/store-contract.md): 명령·출력·종료 코드, 범위, 다른 호스트 기억과 기억 속 명령의 경계
