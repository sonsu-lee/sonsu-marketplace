---
name: review-commit
description: staged·unstaged commit 후보나 기존 Git commit의 범위, 원자성, 메시지와 검증 근거를 읽기 전용으로 검토할 때 사용한다. 코드 품질 일반 리뷰나 Git 쓰기는 담당하지 않는다.
---

# Git 커밋 검토

현재 대화와 실제 Git 상태를 바탕으로 단독 검토한다. 다른 플러그인이나 스킬의 설치·선행
실행을 요구하지 않는다. 검토 대상과 revision을 고정하고 읽기 전용으로 완료한다.

Git 객체가 없어도 요청 없이 fetch하지 않으며 현재 index·worktree·remote ref를 변경하지 않는다.

## Commit 후보를 검토한다

- staged, unstaged와 untracked 변경을 구분한다.
- 변경 목적에 필요한 파일과 hunk만 포함되었는지 확인한다.
- 비밀, 생성물, 대용량 파일, 의도하지 않은 삭제와 binary를 확인한다.
- validation과 문서가 변경 위험에 맞는지 확인한다.
- 제안한 Conventional Commit 메시지가 실제 diff와 일치하는지 확인한다.

## 기존 commit을 검토한다

- 대상 revision, 부모와 비교 범위를 명시적으로 확인한다.
- commit의 tree와 diff를 기준으로 원자성, 메시지와 검증 근거를 살핀다.
- 현재 worktree의 관계없는 변경을 해당 commit의 일부로 오인하지 않는다.

영향이 큰 문제부터 파일과 근거 위치를 포함하여 보고한다. 문제가 없으면 검토한 범위, 실제 검증 상태와 남은 불확실성을 알린다. 검토 모드에서는 branch, index, commit과 remote ref를 변경하지 않는다.
