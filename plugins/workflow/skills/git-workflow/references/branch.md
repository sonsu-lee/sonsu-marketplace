# Branch 규칙

branch 이름을 준비하거나 새 branch를 만들 때 읽는다.

## 이름을 정한다

다음 우선순위로 이름을 선택한다.

1. 사용자가 지정한 정확한 이름
2. repository의 문서·기존 branch·도구 설정에서 확인한 규칙
3. 실행 환경이 요구하는 prefix 규칙
4. 별도 규칙이 없을 때 `<type>/<short-kebab-description>`

실행 환경에 prefix가 필요하면 기본 형식 앞에 붙인다. 예를 들어 `codex/` prefix가 필요하면 `codex/feat/add-search-filter`처럼 구성한다. `type`은 실제 변경 목적에 맞는 `feat`, `fix`, `docs`, `refactor`, `test`, `chore` 중 하나를 우선하며 repository가 다른 taxonomy를 사용하면 이를 따른다.

이름은 현재 작업 범위만 표현한다. 존재하지 않는 티켓 ID, team key, 사용자명이나 변경 범위를 만들어 넣지 않는다.

## 티켓 ID를 후순위로 다룬다

branch 이름은 tracker 연결의 기본 채널로 사용하지 않는다. 다음 중 하나가 확인된 경우에만 티켓 ID를 새 branch 이름에 포함한다.

- 사용자가 정확한 이름이나 ID 포함을 요청했다.
- repository의 현재 branch 규칙이 이를 요구한다.
- 검증된 tracker integration이 branch ID를 요구하고 더 낮은 결합도의 metadata로 목적을 달성할 수 없다.

provider를 ID 문자열 모양만으로 추측하지 않는다. branch에 이미 ID가 있으면 보조 정보로만 취급하고 canonical ticket을 확인한다. ID가 없거나 다르다는 이유로 기존 branch를 자동 rename하지 않는다.

## 생성 전에 확인한다

- current branch, `HEAD`와 시작할 base revision
- 같은 이름의 local·remote branch 존재 여부
- detached HEAD와 진행 중인 Git 작업
- current checkout과 linked worktree에서 해당 branch가 이미 사용 중인지 여부
- dirty 변경이 새 branch로 함께 이동할 영향

사용자가 이름 제안이나 검사만 요청했다면 branch를 만들지 않는다. 생성이 명시된 경우에만 비대화형 명령으로 만들고 current branch와 `HEAD`가 예상과 같은지 다시 확인한다.

worktree를 새로 만들거나 기존 worktree를 이동하지 않는다. branch rename은 사용자가 정확한 대상과 새 이름을 명시한 경우에만 수행하며, 원격 branch 삭제나 강제 갱신은 하지 않는다.
