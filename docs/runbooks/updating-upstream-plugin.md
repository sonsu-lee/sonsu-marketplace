# 업스트림 플러그인 업데이트

## 실행 조건

업스트림의 새 tag 또는 commit을 가져와야 하고, 현재 로컬 커스텀과의 차이를 검토할 준비가
되었을 때 실행합니다. 업데이트 대상과 기준 commit이 불명확하면 시작하지 않습니다.

## 사전 확인

1. 작업 디렉터리, branch, `HEAD`, staged·unstaged·untracked 파일을 확인합니다.
2. 기존 linked worktree이면 재사용하고, 일반 checkout이면 `using-git-worktrees` 정책을 따릅니다.
3. 현재 `UPSTREAM.md`의 저장소, 기준 commit, 버전과 포함 범위를 읽습니다.
4. 현재 로컬 커스텀 diff와 관련 결정 문서를 확인합니다.
5. commit, push와 PR 권한이 각각 어디까지 승인되었는지 확인합니다.

## 업데이트

1. 새 업스트림 소스를 임시 위치에 가져옵니다.
2. 업스트림 Codex 패키징 범위에 해당하는 파일만 식별합니다.
3. 새 원본의 파일 내용, symlink 처리와 실행 권한을 검증합니다.
4. 기존 로컬 커스텀과 충돌하는 변경을 분리해 검토합니다.
5. 업스트림 변경을 적용하고 `UPSTREAM.md`의 기준 commit, 버전, 날짜와 호환성 메모를 갱신합니다.
6. 원본 파일만 포함한 diff와 검증 결과를 사용자에게 보고합니다. 현재 작업에서 upstream
   baseline commit이 승인된 경우에만 이 범위를 첫 번째 commit으로 기록합니다. 승인되지
   않았으면 로컬 정책을 섞지 않고 여기서 멈춥니다.
7. 확정된 새 baseline 위에 로컬 정책을 다시 적용하고 매니페스트의 `-sonsu.<revision>`을 갱신합니다.
8. 관련 아키텍처, 결정, 참조 문서를 현재 상태에 맞춥니다.
9. 로컬 변경 diff와 검증 결과를 별도로 보고합니다. customization commit도 현재 작업에서
   별도로 승인된 경우에만 기록합니다.

## 검증

- marketplace와 plugin JSON을 파싱합니다.
- 매니페스트가 가리키는 파일과 스킬 경로가 존재하는지 확인합니다.
- 업스트림으로 분류한 파일의 내용과 실행 권한을 선택한 기준 commit과 비교합니다.
- 로컬 커스텀 diff에 의도하지 않은 업스트림 변경이나 누락이 없는지 확인합니다.
- 가능한 경우 Codex `plugin/read`로 플러그인 이름, 버전, source와 스킬 목록을 확인합니다.
- 전체 diff와 `git diff --check` 결과를 검토합니다.

## 실패와 복구

검증이 실패하면 commit하지 않습니다. 원본 가져오기와 로컬 정책 적용을 구분할 수 없거나
충돌의 의도를 판단할 수 없으면 현재 worktree를 보존하고 실패 지점과 필요한 결정을
보고합니다. `reset`, `clean`, 강제 checkout이나 force-push로 기존 작업을 없애지 않습니다.

각 검증 단계가 끝나면 upstream baseline과 로컬 customization diff를 따로 보고합니다. 한쪽
commit 승인으로 다른 쪽 commit까지 승인된 것으로 간주하지 않습니다. 승인된 단계만 정확히
stage해 commit하며, push와 PR은 별도 요청이 있을 때만 수행합니다.
