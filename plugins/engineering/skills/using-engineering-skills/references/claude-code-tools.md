# Claude Code 기본 하네스 대응

현재 Claude Code 세션의 도구 schema와 권한을 먼저 확인하고 [공통 실행 계약](agent-execution.md)을
적용한다. 플러그인은 작업·품질 계약을 소유하며 호스트의 세션·권한·에이전트 실행기를 재구현하지 않는다.

- 파일 탐색과 수정에는 현재 노출된 `Glob`·`Grep`·`Read`·`Edit`·`Write`·`Bash`를 사용한다.
  설치된 플러그인 내부 경로는 `${CLAUDE_PLUGIN_ROOT}` 또는 현재 스킬 파일의 위치에서 찾는다.
- 스킬은 실제 설치된 `/plugin-name:skill-name` ID로 호출한다. 사용자 결정이 필요한 때에만
  세션이 제공하는 질문 도구를 사용한다.
- 독립 검토가 필요한 작업은 현재 `Agent` 도구의 새 문맥 기능과 지원 schema를 확인한다.
  같은 고정 산출물에 일반 리뷰어 5명을 할당하고 고위험 정책이면 별도 red-team 1명을 할당한다.
  사용자 지정이 없으면 모델·effort override를 넣지 않고 호스트 설정을 상속한다. 요청 설정,
  실제 관측 설정과 완료 ID를 구분해 기록한다. 수·격리·완료를 확인할 수 없으면 필수 gate를
  `blocked` 또는 `not_run`으로 남기며 자기 리뷰를 독립 리뷰로 세지 않는다.
- 병렬 파일 쓰기는 별도 worktree에서 수행하고 root가 순차 통합한다. reviewer의 원본 작업
  공간은 읽기 전용으로 둔다. 현재 도구가 worktree 격리를 제공하지 않으면 공통 Git 절차를 따른다.
- `CLAUDE_CODE_SESSION_ID`는 일반 명령의 현재 세션 ID에, hook payload의 `session_id`는
  hook 복구에 사용한다. `--continue` 또는 ID 없는 `--resume`에서는 hook이 후속 Bash 환경에 기록한
  `SONSU_CLAUDE_SESSION_ID`를 우선한다. Codex와 Claude의 세션 ID가 둘 다 있으면 현재 호스트의
  ID를 CLI에 명시하고 managed review 준비에는 `--host claude-code`를 지정한다. 관측하지 않은 ID나 모델을 추측하지 않는다.
- Figma처럼 별도 plugin/MCP가 필요한 기능은 현재 연결과 도구 capability를 검사하고 해당
  제공자의 필수 스킬을 적용한다. 설치·인증을 스킬 실행 중 임의로 진행하지 않는다.

공식 참고: [Claude Code 도구](https://code.claude.com/docs/en/tools-reference),
[subagents](https://code.claude.com/docs/en/sub-agents),
[plugins](https://code.claude.com/docs/en/plugins-reference).
