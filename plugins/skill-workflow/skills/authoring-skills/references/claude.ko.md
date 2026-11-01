# Claude 작성 시 고려사항

> 영문 정본: [claude.md](claude.md) (`fe462ed` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

작성하는 스킬이 Claude를 대상으로 할 때 이 레퍼런스를 사용한다. 확장을 추가하기
전에 Claude Code, claude.ai 업로드, API 중 어느 쪽인지 정한다. 이들은 로딩과 실행
기능을 모두 공유하지는 않는다.

## 공통 내용과 클라이언트 기능 분리하기

의도한 배포 경로에 맞는 [Claude Code 스킬 레퍼런스][code]를 사용한다. Claude Code는
호출 제어, 포크 실행, 동적 명령 주입 같은 추가 프런트매터와 본문 기능을 지원한다.
이를 이식 가능한 스킬에 복사하거나 claude.ai, API에서도 동작한다고 가정하지 않는다.
각 경로가 받아들이는 필드는 [여러 환경 간 프런트매터 안내][portability]에서
확인한다.

[Claude 작성 가이드][authoring]는 기능과 트리거를 분명히 밝힌 3인칭 description을
권장한다. 이는 새 스키마가 아니라 작성 안내이며, 이미 잘 동작하는 description을
기계적으로 고쳐 쓸 이유도 아니다. 트리거는 메타데이터에 둔다. 본문 지침은 스킬이
선택된 뒤에 로드된다.

클라이언트별 동작은 요청한 워크플로에 필요하고 대상 환경이 지원할 때만 추가한다.
스킬의 자동 로딩과 부수 효과를 수행할 권한을 구분하고, 편의만을 위해 넓은 도구
접근 권한을 주지 않는다.

Claude Code는 플러그인 스킬을 `/<plugin>:<skill>`로 호출하고, 주입하는 본문 앞에
`Base directory for this skill:`을 붙인다. 공유 스킬은 번들 파일을 캐시 경로가
아니라 이 로드된 디렉터리를 기준으로 찾는다.

## 주장하는 지원 범위 검증하기

의도한 환경과 모델에서 탐색, 활성화, 작업 동작을 확인한다. Claude Code 플러그인은
`skills/` 디렉터리에 `claude plugin validate --strict`를 실행하면 스킬 파일을
검사하며, 마켓플레이스 실행은 스킬 파일을 열지 않는다.
`claude -p --output-format stream-json --verbose`의 `system` `init` 이벤트는 모델
요청 전에 탐색된 스킬을 나열한다. 완전한 로딩은 실제 요청에서 주입된 본문을
확인한다. 자체 평가 설정이 없는 프로젝트에서 출력 품질과 활성화를 보려면
[skill-creator 플러그인][creator]
(`/plugin install skill-creator@claude-plugins-official`)을 사용한다. 이 플러그인은
`evals/evals.json`에 대해 Agent Skills 평가 루프를 실행한다. `claude plugin eval`은
자체 케이스 형식을 가진 별개의 도구이며, 둘은 서로의 파일을 읽지 않는다. omp나
Codex 실행 또는 텍스트만의 리뷰로 Claude 호환성을 주장하지 않는다.

[code]: https://code.claude.com/docs/en/skills
[portability]: https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code
[authoring]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
