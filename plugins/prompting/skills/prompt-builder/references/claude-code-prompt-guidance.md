# Claude Code 프롬프트 지침

Claude Code에서 현재 대화에 보낼 한 번의 작업 요청을 기본 산출물로 둔다. 사용자가 재사용 가능한
스킬이나 `CLAUDE.md`를 요청했을 때에만 해당 파일 형식으로 작성한다. 설치된 도구·플러그인,
작업 디렉터리, 수정·외부 게시 권한과 관찰 가능한 완료 조건을 요청에 필요한 만큼 명시한다.
Claude Code의 내장 도구와 현재 세션이 이미 제공하는 정보는 길게 반복하지 않는다.

복잡한 입력에서는 목표, 현재 자료, 지켜야 할 제약과 기대 결과를 분리하고, 외부 문서·로그·
사용자 제공 자료를 지시와 혼동하지 않도록 구획한다. XML 태그는 여러 종류의 자료가 섞여
구분이 필요할 때만 사용한다. 출력 예시는 원하는 형식이 말로 모호할 때 추가한다. 모델의 내부
추론을 강제로 출력하도록 요구하지 않고, 검증할 수 있는 결과와 실패 시 보고할 정보를 지정한다.

Claude Code의 `/plugin-name:skill-name`은 해당 플러그인이 실제 설치된 경우에만 넣는다.
Codex 전용 `functions.exec`, `spawn_agent`, 모델명·effort, OpenAI API 설정을 Claude Code의
명령이나 파라미터처럼 쓰지 않는다. 현재 모델에 맞춘 조정을 요청받으면
[Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)를
다시 확인하고 확인 시점과 대상 surface를 구분한다.
