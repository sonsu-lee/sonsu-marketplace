# Claude Code 기본 하네스 대응

현재 Claude Code 세션의 도구 schema와 권한을 확인하고 [실행 계약](agent-execution.md)을
적용한다. 플러그인은 작업·품질 계약을 소유하며 세션·권한·에이전트 실행기를 재구현하지 않는다.

- 설치된 스킬은 `/plugin-name:skill-name`으로 호출한다. 파일과 Git 작업에는 현재 노출된
  native 도구를 사용하고, 플러그인 내부 파일은 `${CLAUDE_PLUGIN_ROOT}` 또는 현재 스킬의
  경로에서 찾는다.
- 독립 검토에는 새 문맥의 native Agent를 사용한다. 역할 모델은
  [Claude 프로필](claude-model-profiles.md)의 정확한 ID로 `model` 인자에 전달한다.
  이 기본 정책에서 Claude subagent의 effort는 메인 세션에서 상속한다. Claude Code는
  subagent 정의의 개별 `effort` override도 지원한다. 요청 모델과 관측 모델·effort,
  생성 ID, 완료 이벤트와 결과를 구분해 기록한다. 호출에 모델을 지정할 수 없거나
  모델이 거부되거나 대체되면 필수 검토를 `blocked`/`not_run`으로 둔다. 실행 모델은
  `/tasks` 또는 CLI JSON의 `modelUsage` 등에서 확인한다.
- root가 리뷰어를 할당하고 결과를 수집한다. 병렬 writer는 별도 worktree를 쓰고
  reviewer의 원본 작업 공간은 읽기 전용으로 둔다. 현재 도구에 worktree 격리가 없으면
  공통 Git 절차를 적용한다.
- hook payload의 `session_id`가 복구의 정본이다. 일반 명령은 Claude 환경의 현재 ID를
  사용하고, ID가 충돌하거나 확인되지 않으면 `--session-id`를 명시한다.
  새 관리형 gate는 `init --host claude-code`로 등록한다.
- Figma 등 외부 기능은 현재 연결·도구 capability·권한을 확인한다. 별도 플러그인이나
  인증을 필요한 것처럼 추측하거나 스킬 실행 중 임의로 설치하지 않는다.

공식 참고: [subagents](https://code.claude.com/docs/en/sub-agents),
[plugins](https://code.claude.com/docs/en/plugins-reference),
[hooks](https://code.claude.com/docs/en/hooks).
