---
name: branch
description: 브랜치 이름을 제안·검토하거나 명시적으로 요청된 새 Git branch를 만들 때 사용한다. commit, push, PR, worktree 생성은 담당하지 않는다.
---

# 브랜치 준비

이 스킬은 현재 대화와 실제 Git 상태를 바탕으로 단독 실행한다. 다른 플러그인이나
스킬의 설치·선행 실행을 요구하지 않는다. [전달 권한](../../references/delivery-authority.md)을
따르며, 사용자 요청에 없는 Git 쓰기나 원격 작업은 수행하지 않는다. 여러 단계의 작업이나
외부 쓰기는 필요할 때 [연속성 기록](../../references/continuity.md)을 사용한다.

이름 제안은 읽기 전용으로 완료한다. 생성·전환을 요청받으면 [Git 안전 규칙](../../references/git-safety.md)을 읽고 현재 checkout과 기존 변경을 확인한 뒤 결과를 다시 읽는다.

## 이름을 정한다

[새 브랜치 이름 규칙](../../references/branch-naming.md)을 읽고 적용한다.

## 티켓 ID를 후순위로 다룬다

branch 이름은 tracker 연결의 기본 채널로 사용하지 않는다.

Linear 티켓 작업의 새 branch는 위의 이름 규칙에 따라 type·작업 설명으로 구성하고 티켓 ID를 자동으로 넣지 않는다. repository의 ID 포함 관례나 integration이 제공하는 branch 이름도 Linear ID를 추가할 근거로 사용하지 않는다. 예를 들어 `ENG-123`의 검색 필터 작업은 별도 접두사 요구가 없다면 `feat/add-search-filter`로 표현하고, 티켓 연결은 PR metadata에서 처리한다. 사용자가 정확한 이름이나 ID 포함을 직접 지정한 경우에는 그 명시적 요청을 따른다.

Linear 이외의 tracker는 다음 중 하나가 확인된 경우에만 티켓 ID를 새 branch 이름에 포함한다.

- 사용자가 정확한 이름이나 ID 포함을 요청했다.
- repository의 현재 branch 규칙이 이를 요구한다.
- 검증된 tracker integration이 branch ID를 요구하고 더 낮은 결합도의 metadata로 목적을 달성할 수 없다.

provider를 ID 문자열 모양만으로 추측하지 않는다. branch에 이미 ID가 있으면 보조 정보로만 취급하고 canonical ticket을 확인한다. ID가 없거나 다르다는 이유로 기존 branch를 자동 rename하지 않는다.

## 생성 전에 확인한다

- 현재 브랜치, `HEAD`와 시작할 base revision
- 같은 이름의 local·remote branch 존재 여부
- detached HEAD와 진행 중인 Git 작업
- current checkout과 linked worktree에서 해당 branch가 이미 사용 중인지 여부
- dirty 변경이 새 branch로 함께 이동할 영향

사용자가 이름 제안이나 검사만 요청했다면 branch를 만들지 않는다. 생성이 명시된 경우에만 비대화형 명령으로 만들고 current branch와 `HEAD`가 예상과 같은지 다시 확인한다.

worktree를 새로 만들거나 기존 worktree를 이동하지 않는다. branch rename은 사용자가 정확한 대상과 새 이름을 명시한 경우에만 수행하며, 원격 branch 삭제나 강제 갱신은 하지 않는다.
