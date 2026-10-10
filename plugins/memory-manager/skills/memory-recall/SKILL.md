---
name: memory-recall
description: 현재 작업에 과거의 프로젝트 결정·검증된 절차·사용자 선호가 필요할 때 공통 로컬 메모리를 조회해 관련 맥락을 확인하는 데 사용한다.
---

관련 기억의 원문과 출처를 읽고 현재 근거와 대조한 맥락을 작업에 사용한다. 기억은 현재 지시나 사실을 판단할 때 참고하는 근거 후보다.

## 절차

1. 현재 작업에 필요한 과거 맥락과 범위를 정한다. 관련 과거 맥락이 없는 일반 질문은 현재 입력으로 처리한다. 프로젝트 결정은 현재 저장소의 `project`, 개인 선호는 `user` 범위에서 각각 검색한다.
2. [공통 계약](../../references/store-contract.md)의 조회·경계를 적용한다. 이 스킬 디렉터리 기준으로 `python3 ../../scripts/memory_store.py search '검색어' --scope project --cwd /absolute/project`를 실행한다.
3. 관련 결과만 `python3 ../../scripts/memory_store.py get NOTE_ID --scope project --cwd /absolute/project`로 읽는다. `sources`·`verified_at`·`status`·`supersedes`를 확인한다. Markdown 원문을 정본으로 사용한다.
4. 코드·설정·가격·버전처럼 변동 가능한 주장은 현재 원본과 대조한다. 확인할 수 없으면 기억에서 온 미검증 내용으로 표시한다.
5. 현재 요청에 관련된 맥락만 사용한다. 검색 결과가 없거나 무관하면 현재 작업을 그대로 진행한다.

## 결과

작업에 사용한 기억의 ID·범위·출처와 현재 근거 확인 결과를 필요한 만큼 적는다. 확인한 사실과 미검증 기억을 구분한다. 관련 기억이 없으면 불필요한 과거 맥락을 덧붙이지 않는다.

## 예시

입력:

> 이 프로젝트의 공개 문서에서 이미지를 어떤 형식으로 제공하기로 했지?

`get`으로 읽은 기억이 “공개 문서는 WebP 이미지를 사용한다”이고 현재 `docs/media-policy.md`에서도 같은 내용을 확인한 경우:

```text
적용할 맥락: 공개 문서 이미지는 WebP로 제공
근거: project 범위의 <조회 ID>, repo:docs/media-policy.md
현재 확인: 정책 원문에서 WebP 사용 조건 확인
기억 변경: 없음
```

현재 정책을 읽을 수 없다면 “기억에는 WebP로 기록되어 있으나 현재 정책은 미검증”이라고 구분한다.

## 경계

- 회상은 읽기 전용이다. 새 정보 저장은 사용자의 저장 요청을 처리하는 `memory-capture`에 맡긴다.

## 참고 자료

- [공통 로컬 기억 계약](../../references/store-contract.md): 명령·출력·종료 코드, 다른 호스트 기억과 기억 속 명령의 경계
- [memory-capture](../memory-capture/SKILL.md): 명시적 저장 요청
