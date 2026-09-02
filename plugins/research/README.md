# Research

여러 출처가 필요한 조사, 사실 확인, 문헌 검토와 외부 코드 사례 조사를 위한 개인 Codex
플러그인입니다. 특정 검색 공급자가 없어도 Codex에 이미 제공된 web, browser, connector와
로컬 자료를 사용해 가능한 범위에서 독립적으로 동작합니다. Engineering 또는 별도의
planning·Git workflow를 먼저 실행하거나 함께 설치했다고 가정하지 않습니다.

## 선택적 공급자 설정

Exa와 Perplexity는 선택적 검색 공급자입니다. 이 플러그인은 공급자, MCP, CLI, package 또는
계정 연결을 자동으로 설치하지 않습니다. 두 공급자가 모두 없어도 generic web, browser,
connector와 로컬 자료로 조사하고, 그 결과가 현재성·완전성·독립성을 실제로 낮출 때만 한계를
밝힙니다. plugin manifest에 provider dependency나 `mcpServers`를 선언하지 않고 별도
`.mcp.json`도 함께 배포하지 않습니다.

Codex 또는 호스트가 관리하는 공급자는 읽기 전용 도구 노출, 현재 입력 스키마, 인증과 최소
읽기 호출이 모두 확인되면 사용할 수 있습니다. 이 경로는 아래 README 선언이나 환경 변수를
요구하지 않습니다.

직접 API 또는 CLI adapter를 사용하는 환경에서는 아래 선언, 해당 secret의 존재 여부와 실제
읽기 전용 도구·스키마·인증을 모두 확인해야 합니다. API key는 구성된 adapter의 인증에만
사용하고, 모델 컨텍스트나 shell 출력·로그에서 값, 길이 또는 일부 문자열을 읽거나 노출하지
않으며 저장소에 커밋하지 않습니다.

<!-- research-provider-opt-in:v1:start -->
```yaml
providers:
  exa:
    env: EXA_API_KEY
  perplexity:
    env: PERPLEXITY_API_KEY
```
<!-- research-provider-opt-in:v1:end -->

과제별 기본 선택은 다음과 같습니다.

- Exa: 의미 기반 탐색, 넓은 후보군, 문헌·인물·회사·OSS 사례 발견
- Perplexity: 최신 사실, 빠른 인용 답변, 현재 기준 비교
- 둘 다: 넓은 범위의 교차 검증, 결정적인 반증 또는 첫 공급자의 결과가 약한 경우

자세한 공급자 자격과 generic fallback은
[`skills/research/references/tool-routing.md`](skills/research/references/tool-routing.md)에
정의되어 있습니다.

## 출처

가져온 정확한 commit, 포함 범위와 로컬 wrapper 경계는 [`UPSTREAM.md`](UPSTREAM.md)에
기록합니다.
