---
name: branch
description: 브랜치 이름을 제안·검토하거나 명시적으로 요청된 새 Git branch를 만들 때 사용한다. commit, push, PR, worktree 생성은 담당하지 않는다.
---

# 브랜치 준비

현재 대화와 실제 Git 상태에서 작업 목적에 맞는 이름을 고르고, 생성 요청이 있으면 기존 변경을 보존하며 브랜치를 만든다. 이름 제안은 읽기 전용으로 완료한다.

## 절차

1. [전달 권한](../../references/delivery-authority.md)에서 승인 범위를 확인하고 [새 브랜치 이름 규칙](../../references/branch-naming.md)으로 이름을 정한다. `git check-ref-format --branch <이름>`으로 문법을 확인한다.
2. 티켓 ID는 이름에 넣지 않는다. 이름에 ID가 없으면 Linear의 branch 기반 연결이 일어나지 않으므로, PR 전 상태 변경 요청은 `tickets` 플러그인의 `update-ticket`으로 처리한다.
3. 생성·전환 요청에는 [Git 안전 규칙](../../references/git-safety.md)을 적용한다. current branch·HEAD·base revision, 동명 local·remote ref, detached HEAD·진행 중 작업, current checkout·linked worktree의 점유와 dirty 변경의 이동 영향을 확인한다.
4. 명시적으로 승인된 생성만 비대화형 명령으로 수행한다. current branch와 HEAD가 예상과 같은지 다시 읽고 기존 변경이 보존됐는지 확인한다. 여러 단계 작업은 [연속성 기록](../../references/continuity.md)에 남긴다.

## 결과

이름 제안에는 이름과 적용한 규칙을, 생성 결과에는 branch·base·확인된 HEAD와 남은 변경을 보고한다. 생성하지 않았다면 제안만 완료했다고 쓴다.

## 예시

- 입력: “캐시 키 정규화 작업의 이름만 추천해 줘.” 별도 명명 규칙이 없으면 `fix/normalize-cache-keys`를 제안하고 Git 상태는 유지한다.
- 입력: “확인한 현재 HEAD에서 `test/cache-key-unicode` 브랜치를 만들어 줘.” 동명 ref·점유·변경 영향을 확인한 뒤 생성하고 새 branch와 같은 HEAD를 보고한다.

## 경계

- 이름 제안·검사 요청만으로 branch를 만들지 않는다.
- worktree 생성·이동, commit·push·PR, 원격 branch 삭제·강제 갱신은 이 작업에 포함하지 않는다.
- branch rename은 사용자가 정확한 대상과 새 이름을 명시한 경우에만 수행한다.

## 참고 자료

- [새 브랜치 이름 규칙](../../references/branch-naming.md)
- [Git 안전 규칙](../../references/git-safety.md)
- [전달 권한](../../references/delivery-authority.md)
- [작업 연속성](../../references/continuity.md)
- [호스트별 도구](../../references/hosts.md)
