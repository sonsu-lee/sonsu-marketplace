# 기존 디자인 플러그인 작업 기록 이전

`interface-design`, `operations-ui`, `figma-workflow`의 진행 중인 작업 기록은 같은 worktree와
session의 `<old-plugin>.json`에 남아 있습니다. `design`의 `SessionStart` hook은 현재
`design.json`이 없으면 세 이전 파일의 활성 기록 위치만 읽기 전용으로 알립니다. 기록 내용은
hook 출력에 싣지 않으며 기존 파일을 자동 이전하거나 삭제하지 않습니다.

현재 설치된 `design`의 `scripts/task-continuity.py` 절대 경로로 해당 기록을 읽고, 최신 사용자
지시·원본 산출물·외부 작업 상태와 대조합니다. 정확한 `--session-id`와 `--cwd`를 쓰며 다른
세션이나 worktree를 검색하지 않습니다.

```sh
python3 /absolute/design/scripts/task-continuity.py read \
  --from-plugin figma-workflow --session-id <session-id> --cwd <worktree>
python3 /absolute/design/scripts/task-continuity.py migrate --mode write \
  --from-plugin figma-workflow --session-id <session-id> --cwd <worktree> \
  --task-id <record-task-id> --skill design-interface --expected-revision <record-revision>
python3 /absolute/design/scripts/task-continuity.py read \
  --session-id <session-id> --cwd <worktree>
```

`--from-plugin`에는 실제 이전 패키지 이름을, `--skill`에는 현재 `design`의 작업 스킬을
넣습니다. `migrate`는 쓰기 권한이 있을 때만 실행하고, 기존 기록의 task ID·revision과 현재
상태를 다시 확인한 뒤 `design.json`을 새로 만듭니다. `summary`와 task ID를 보존하고 revision을
하나 올리며 이전 파일은 그대로 둡니다. 현재 `design.json`이 있거나 이전 패키지의 활성 기록이
여러 개이면 자동으로 합치지 않고 실패합니다. 작업별 원본과 현재 상태를 수동으로 대조합니다.

이전한 작업은 기존 플러그인으로 다시 진행하지 않습니다. 새 기록의 내용과 실제 결과를 확인한
뒤 설치된 이전 패키지만 제거합니다. 저장된 디자인 품질 contract/report의 `profile` 값은
작업 연속성 기록과 별개이며 변경하지 않습니다.
