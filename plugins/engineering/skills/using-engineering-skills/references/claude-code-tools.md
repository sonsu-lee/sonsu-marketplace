# Claude Code 도구 참고

현재 세션에 노출된 도구와 입력 스키마를 확인하고 [공통 실행 계약](agent-execution.md)을
적용한다. Codex 전용 도구·모델 이름을 Claude Code 입력으로 대체하지 않는다.

## 파일·명령·스킬

- 탐색은 제공되는 `Glob`·`Grep`·`Read`, 반복 가능한 파서·테스트·빌드는 `Bash`, 편집은
  `Edit`·`Write`에 대응한다.
- 설치된 스크립트·훅은 `${CLAUDE_PLUGIN_ROOT}`를 기준으로 찾는다. 저장소 밖 형제 경로가
  설치 환경에도 존재하는지는 별도로 확인한다.
- 플러그인 스킬은 `/plugin-name:skill-name`으로 명시적으로 호출할 수 있다. 자연어 요청의
  선택은 설치된 설명과 현재 `Skill` 기능을 따른다.
- 필요한 사용자 결정에는 제공되는 `AskUserQuestion`, 작업 공간 격리에는 지원되는 기본
  worktree 기능을 사용한다. 해당 기능이 없으면 `using-git-worktrees`의 Git 방식을 검토한다.

## 에이전트·리뷰

위임이 승인되거나 적용되는 지침에서 요청된 경우 현재 `Agent` 기능을 사용한다. 별도 문맥의
실제 이력 전달 방식과 재위임 제한을 확인한다. 생성 입력은 공통 실행 계약의 사실 중심
인계를 사용한다.

현재 스키마가 재개를 지원하면 같은 세션을 이어 가고, 지원하지 않으면 새 문맥에서 현재
작업·게이트와 누적 예산을 유지한다. 모델 설정이 필요하면 지원되는 Claude Code 값만 사용하며,
지정이나 역할상 필요가 없으면 `inherit` 또는 호스트 기본값을 유지한다.

독립 리뷰가 필수인데 기능이나 권한이 없으면 `blocked` 또는 `not_run`으로 기록한다. 자체
검토와 독립 검토를 구분한다. Codex goal과 같은 기능이 있다고 가정하지 않으며 현재 도구의
호출 조건을 따른다.

## 설치·검증

현재 리비전의 실제 테스트·빌드·검증기·로더 결과로 보고한다. 플러그인·훅 설치처럼 호스트가
소비하는 계약은 사용 가능한 `claude plugin validate --strict`와 격리 설치로 확인한다.
정적 검사와 실제 설치·로딩·동작 근거를 구분한다.

공식 참고: [Tools reference](https://code.claude.com/docs/en/tools-reference),
[Subagents](https://code.claude.com/docs/en/sub-agents),
[Plugins reference](https://code.claude.com/docs/en/plugins-reference).
