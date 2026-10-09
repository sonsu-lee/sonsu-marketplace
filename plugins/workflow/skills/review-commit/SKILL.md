---
name: review-commit
description: staged·unstaged commit 후보나 기존 Git commit의 범위, 원자성, 메시지와 검증 근거를 읽기 전용으로 검토할 때 사용한다. 코드 품질 일반 리뷰나 Git 쓰기는 담당하지 않는다.
---

# Git 커밋 검토

현재 대화와 실제 Git 상태에서 대상 revision과 비교 범위를 고정하고 커밋 전달 품질을 읽기 전용으로 검토한다.

## 절차

1. 후보 검토인지 기존 commit 검토인지 정한다. 후보는 staged·unstaged·untracked를 구분하고, 기존 commit은 revision·부모·비교 범위와 해당 tree·diff를 읽는다. worktree의 다른 변경은 별도 범위로 둔다.
2. 목적에 필요한 파일·hunk만 포함됐는지, 독립적으로 설명하고 되돌릴 단위인지 확인한다. 비밀·생성물·대용량 파일·의도하지 않은 삭제·binary를 살핀다.
3. validation과 문서가 변경 위험에 맞는지 확인한다. 실제 diff와 메시지를 대조하고 [커밋 메시지 기준](../../references/commit-message.md)의 언어·제목·본문·trailer 규칙을 적용한다.
4. 영향이 큰 문제부터 위치와 근거를 붙인다. 문제가 없으면 검토 범위·실제 검증 상태·남은 불확실성을 정리한다.

## 결과

범위와 revision, 문제별 파일·근거 위치·영향·수정 방향을 보고한다. 유효한 문제가 없으면 “문제 없음”과 검증 한계를 쓴다.

## 예시

입력: “staged 변경을 커밋 단위로 검토해 줘.” 후보에 캐시 TTL 수정과 독립적인 도움말 번역이 함께 있으면 두 목적의 경로·hunk를 근거로 분리를 제안한다. staging은 유지한다.

## 경계

- branch·index·worktree·commit·remote ref를 변경하지 않는다.
- Git 객체가 부족해도 요청 없이 fetch하지 않는다.

## 참고 자료

- [커밋 메시지 기준](../../references/commit-message.md)
- [Git 안전 규칙](../../references/git-safety.md)
