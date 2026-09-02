# Research

여러 출처가 필요한 조사, 사실 확인, 문헌 검토와 외부 코드 사례 조사를 위한 개인 Codex
플러그인입니다. 특정 검색 공급자가 없어도 Codex에 이미 제공된 web, browser, connector와
로컬 자료를 사용해 가능한 범위에서 독립적으로 동작합니다.

## 선택적 공급자 설정

Exa와 Perplexity는 선택적 검색 공급자입니다. 이 플러그인은 공급자, MCP, CLI, package 또는
계정 연결을 자동으로 설치하지 않습니다. 직접 API 또는 CLI adapter를 사용하는 환경에서는
아래 선언과 해당 환경 변수 설정이 모두 있어야 합니다. API key 값은 출력하거나 저장소에
커밋하지 않습니다.

<!-- research-provider-opt-in:v1:start -->
```yaml
providers:
  exa:
    env: EXA_API_KEY
  perplexity:
    env: PERPLEXITY_API_KEY
```
<!-- research-provider-opt-in:v1:end -->

현재 baseline의 자세한 공급자 자격과 fallback은
[`skills/research/references/tool-routing.md`](skills/research/references/tool-routing.md)에
정의되어 있습니다.

## 출처

가져온 정확한 commit, 포함 범위와 로컬 wrapper 경계는 [`UPSTREAM.md`](UPSTREAM.md)에
기록합니다.
