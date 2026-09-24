# Claude Code 메모리 접근

Claude Code의 auto memory를 대상으로 할 때 적용한다. 사용자가 명시한 경로나 현재 호스트가
보여 주는 memory directory를 우선한다. 기본 형태는 `~/.claude/projects/<project>/memory/`지만
`<project>`를 현재 디렉터리 이름만으로 추정하지 않는다. `CLAUDE_CONFIG_DIR`, 프로젝트 범위와
`autoMemoryDirectory` 설정을 확인하고 실제 디렉터리가 요청한 프로젝트와 일치하는지 대조한다.
같은 저장소의 worktree가 메모리를 공유할 수 있으므로 다른 worktree의 진행 기록도 범위 안에서만 다룬다.

`MEMORY.md`는 인덱스이고 나머지 주제 파일은 필요할 때 읽는다. 인덱스의 첫 200줄 또는 25KB만
시작 시 로드되는 현재 계약을 점검하되 다른 호스트의 제한을 적용하지 않는다. 기존 frontmatter,
날짜와 주제 파일의 고유 정보를 보존한다. `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/`는
지시 파일이므로 메모리 정리 요청만으로 수정하지 않는다.

점검은 읽기 전용이다. 정리 요청이 직접 편집을 허용하면 본문 스킬의 백업·변경 직전 재확인·
적용 후 readback 절차를 따른다. 공유 메모리를 다른 Claude 세션이 수정 중일 수 있으므로
변경 직전 내용이 달라졌다면 재검토한다. 경로·권한을 확인할 수 없으면 수정하지 않고
`blocked` 또는 `inconclusive`로 보고한다. 자동 메모리 기능의 활성화·설정 변경과 plugin
설치는 이 스킬의 정리 범위에 포함하지 않는다.

현재 경로와 한도는 [Claude Code 공식 메모리 문서](https://code.claude.com/docs/en/memory)를
확인한다. 설치된 호스트의 관찰 결과와 다르면 그 차이를 보고한다.
