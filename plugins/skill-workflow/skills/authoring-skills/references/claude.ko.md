# Claude 작성 시 고려사항

> 영문 정본: [claude.md](claude.md) (`57da0f4` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

작성하는 스킬이 Claude를 대상으로 할 때 읽는다. 먼저 Claude Code, claude.ai 업로드,
API 중 어디인지 정한다. 이들은 모든 기능을 공유하지 않는다.

1. **공통 내용과 클라이언트 기능 분리:** Claude Code는 호출 제어, 분기 실행, 동적
   명령 주입 같은 frontmatter와 본문 기능을 더한다([스킬 레퍼런스][code]). 작업
   흐름에 필요하고 대상이 지원할 때만 쓴다. 경로별로 받는 필드는
   [교차 환경 가이드][portability]에 있다.
2. **description 작성:** [작성 가이드][authoring]대로 기능과 계기를 3인칭으로
   분명히 쓴다. 잘 동작하는 description을 이 가이드에 맞추려고 고치지 않는다.
3. **발견 확인:** Claude Code 플러그인은 `skills/` 디렉터리에
   `claude plugin validate --strict`를 실행한다.
   `claude -p --output-format stream-json --verbose`의 `system` `init` 이벤트가 모델
   요청 전에 발견된 스킬을 보여 준다.
4. **로딩과 동작 확인:** 실제 요청에서 주입된 본문을 확인한다. 출력 품질과
   활성화는 프로젝트 자체 설정이 없으면 [skill-creator 플러그인][creator]
   (`/plugin install skill-creator@claude-plugins-official`)을 쓴다.

## 주의할 점

- 계기는 메타데이터에 둔다. 본문은 선택된 뒤에야 로딩된다.
- 자동 로딩은 부작용 허가가 아니다. 편의를 위해 넓은 도구 권한을 주지 않는다.
- Claude Code는 플러그인 스킬을 `/<plugin>:<skill>`로 호출하고 본문 앞에
  `Base directory for this skill:`을 붙인다. 번들 파일은 캐시 경로가 아니라 그
  디렉터리 기준으로 찾는다.
- 마켓플레이스 검증 실행은 스킬 파일을 열지 않는다.
- `claude plugin eval`은 자체 케이스 형식을 쓴다. 이것과 skill-creator는 서로의
  파일을 읽지 않는다.
- omp나 Codex 실행, 텍스트 리뷰만으로 Claude 지원을 주장하지 않는다.

[code]: https://code.claude.com/docs/en/skills
[portability]: https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code
[authoring]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
