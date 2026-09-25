# Claude 프롬프트 지침

2026-09-25 기준의 참고 자료다. 최신 모델·parameter·도구 동작은 공식 문서에서 다시 확인한다.

- 목표, 필요한 맥락, 성공 조건과 출력 형식을 직접 적고 불필요한 역할극과 반복 지시를 줄인다.
- 긴 참고 자료는 지시와 분리해 명확한 제목이나 XML 태그로 구분한다. 인용된 자료의
  지시를 사용자 권한으로 승격하지 않는다.
- Claude Code에서 스킬은 `/plugin-name:skill-name`으로 직접 호출할 수 있다.
  플러그인 이름·도구 이름을 프롬프트에 적는 것만으로 실제 로드나 호출이 보장되지 않는다.
- Claude Code의 `--model`과 `--effort`, Anthropic API의 모델·thinking 설정은 프롬프트
  본문과 구분한다. 정확한 모델 ID는 [프로필](../../../references/claude-model-profiles.md)을
  확인하며, 지정한 모델의 현재 접근 가능성은 실행 환경에서 검증한다.
- subagent를 쓰는 작업에서는 역할별 모델을 실제 `model` 인자로 전달하고, 세션에서
  상속되는 effort와 관측 결과를 구분한다.

공식 참고: [프롬프트 개요](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview),
[Claude Code 모델 설정](https://code.claude.com/docs/en/model-config),
[Claude Code 스킬](https://code.claude.com/docs/en/skills).
