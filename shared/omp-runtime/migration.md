# 기존 디자인 작업에서 재개하기

`interface-design`, `operations-ui`, `figma-workflow`, `design`의 기존 기록은 그대로 보존한다. omp 버전은 이전 기록을 자동으로 찾거나 이전·삭제하지 않으며, 이전용 helper나 SessionStart hook을 실행하지 않는다.

현재 사용자가 지정한 작업과 기록만 읽기 전용으로 확인한다. 다른 세션이나 worktree를 검색하지 않는다. 과거 요약을 현재 승인으로 보지 않고 최신 지시, 원본 산출물, 외부 작업 결과와 대조한다. 여러 기록이 충돌하거나 작업 결과가 불분명하면 대상과 실제 상태를 확인하기 전까지 다시 실행하지 않는다.

재개에 필요한 확인된 상태와 다음 작업은 [omp의 작업 연속성](continuity.md)에 따라 순정 todo와 세션 기록으로 다룬다. `.sonsu` 기록이나 Git exclude를 고치지 않고 새 독자 checkpoint도 만들지 않는다.

저장된 디자인 품질 contract/report의 `profile` 값(`interface-design`, `operations-ui`, `figma-workflow`)은 호환성을 위해 바꾸지 않는다. 이전 플러그인 삭제는 설치된 패키지만 대상으로 하며 사용자가 요청한 경우로 한정한다. 작업 산출물과 과거 기록은 남긴다.
