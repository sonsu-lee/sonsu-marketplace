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

첫 검색 전에 **이번에 필요한 결과**로 경로를 고릅니다. 조사 깊이와 별개이므로 `lookup`에도 적용합니다.

- 로컬 자료 또는 이미 위치를 아는 공식 문서: 해당 자료 직접 확인
- Exa: 아직 이름을 모르는 자료·논문·구현·회사 등의 넓은 후보군 발견
- Perplexity: 정확한 사실·URL·현재 지원·변경 사항·정해진 대상의 비교·설명 근거. 애매한 일반 검색도 Perplexity 우선
- 사용자 지정 공급자·전용 스킬: 지정 범위에서 우선하며, 실제 사용 불가 시 조용히 대체하지 않음

기술·OSS·논문·회사라는 주제만으로 Exa를 선택하지 않습니다. 후보 발견에서 현재성 확인으로
목적이 바뀌거나, 중요한 증거 공백 또는 실제 도구 실패가 있으면 재판단합니다. Perplexity로
찾은 URL을 Exa fetch로 읽는 것은 허용하되 같은 기본 질문을 두 공급자에 중복 검색하지 않습니다.

자세한 공급자 자격과 generic fallback은
[`skills/research/references/tool-routing.md`](skills/research/references/tool-routing.md)에
정의되어 있습니다.

## 호스트의 기본 검색 지침

Research를 호출하지 않는 짧은 검색과 공급자 전용 스킬이 함께 설치된 환경에도 같은 선택을
적용하려면, 사용자 소유의 전역 `AGENTS.md`에서 기존 검색 공급자 규칙을 아래 내용으로
교체합니다. 플러그인 설치가 전역 파일을 자동으로 수정하지는 않습니다. 설치 캐시의 Exa
스킬을 직접 편집하지 않으며, 아래 호스트 지침이 일반 요청의 공급자 선택을 먼저 담당합니다.

```markdown
- 검색 공급자는 작업 주제가 아니라 이번 검색에서 필요한 결과로 고른다. 로컬·제공 자료로 충분하면 그 자료만 확인하고, 이미 위치를 아는 공식 문서는 직접 연다.
- 사용자가 공급자나 공급자 전용 스킬을 명시하면 해당 요청 범위에서 우선한다. 실제 사용 불가 시 조용히 다른 공급자로 대체하지 않는다.
- 아직 이름을 모르는 자료·논문·구현·회사 등의 넓은 후보군 발견은 Exa를 우선한다. 기술·OSS·논문·회사라는 주제 자체는 Exa 선택 근거가 아니다.
- 정확한 사실·URL·현재 지원·변경 사항·정해진 대상의 비교·설명 근거는 Perplexity를 우선한다. 목적이 애매한 일반 검색도 Perplexity로 시작한다.
- Perplexity 일반 검색과 URL 하나·사실 출처 lookup은 `perplexity_search`를 사용한다. `perplexity_ask`는 합성된 설명·요약이 목적일 때만 선택하고, 짧은 요청이라는 이유로 search를 대신하지 않는다. `perplexity_reason`은 단계적 분석, `perplexity_research`는 복잡성과 비용이 정당화되는 깊은 조사에만 사용한다. 실제 노출된 schema를 따른다.
- 공급자 전용 스킬은 공급자를 고른 뒤 사용법 참고로 적용한다. 전용 스킬의 넓은 research·latest·comparison trigger가 일반 요청의 공급자 선택을 먼저 결정하게 하지 않는다. 사용자의 명시적 전용 스킬 요청은 예외다.
- 목적 변경·중요한 증거 공백·실제 도구 실패 시 공급자를 재판단한다. 목적과 가용성이 그대로이고 근거가 충분하면 기존 경로를 유지한다. 두 공급자가 서로 다른 증거 목적을 맡거나 약한 첫 결과를 보완할 때만 검색을 함께 사용하며 같은 기본 질문을 반복하지 않는다.
- 검색과 원문 읽기는 별개다. Perplexity가 찾은 URL을 Exa fetch로 읽어도 되며, fetch 성공이 다음 검색의 Exa 선택 근거는 아니다.
- 외부 요청 전에 공급자 연결이 호스트·connector가 관리하는 도구인지 직접 API·CLI adapter인지 구분한다. 관리형 도구는 현재 노출된 읽기 전용 도구와 schema를 확인한 뒤 첫 필요한 최소 읽기 호출로 인증·가용성을 확인할 수 있으며 README marker나 환경변수를 요구하지 않는다.
- 직접 API·CLI adapter 또는 연결 유형이 불명확한 경우에는 외부 호출 전에 설치 manifest로 찾은 Research의 `skills/research/references/tool-routing.md`에 있는 직접 adapter 자격 규칙을 확인하고 적용한다. plugin-root README의 유효한 opt-in marker와 allowlist된 secret의 non-empty 여부를 값 노출 없는 boolean·종료 상태로 확인한 뒤에만 최소 읽기 호출을 한다. 규칙이나 자격 증거를 확인할 수 없으면 해당 adapter를 호출하지 않는다. 이 reference 확인은 Research 전체 workflow의 자동 실행을 뜻하지 않는다.
- 도구 미노출은 제공되는 discovery로 확인하고 실제 인증 실패·일시 제한과 구분한다. 일시 실패를 이후 작업까지 사용 불가로 일반화하지 않으며 이후 성공한 호출을 현재 근거로 삼는다. 기본 공급자가 자격을 충족하지 못하면 자격을 충족한 다른 공급자 또는 가용한 generic web·browser·connector로 진행하되, 사용자 지정 공급자를 조용히 대체하지 않는다.
```

이 기본값은 공급자 성능의 보편적 우열이 아니라 선택 정책입니다. 호스트의 더 높은 우선순위
도구·안전 지침은 계속 따릅니다. 평가에서는 Research 단독과 이 호스트 지침·Exa 스킬이 함께
있는 조건을 구분하고, 선택 비율 대신 실제 첫 호출·목적 전환·원문 읽기·실패 처리를 확인합니다.

## 선택적 코드 검색 cache

외부 코드 패턴 조사는 검색 결과를 그대로 좋은 사례로 간주하지 않고, full commit SHA로 고정한
호출부·설정·테스트·라이선스 근거를 검증합니다. 반복 조사에서는 사용자가 영속 저장과 절대 경로를
명시적으로 승인한 경우에만 표준 라이브러리 기반 SQLite helper를 사용할 수 있습니다.

```text
python3 skills/research/scripts/code_search_cache.py init --db /absolute/path/code-search.sqlite3
python3 skills/research/scripts/code_search_cache.py lookup --db /absolute/path/code-search.sqlite3 --input query.json
```

helper는 query metadata, immutable code locator, rubric 판정과 명시적으로 승격한 catalog 항목만
저장합니다. source code, snippet, diff, credential과 비공개 문서 본문은 저장하지 않습니다. cache를
요청하지 않은 조사의 기본값은 `off`이며 파일이나 데이터베이스를 만들지 않습니다. 검색 전략,
artifact identity와 freshness 규칙은
[`skills/research/references/code-search.md`](skills/research/references/code-search.md)에 정의되어
있습니다.

## 출처

가져온 정확한 commit, 포함 범위와 로컬 wrapper 경계는 [`UPSTREAM.md`](UPSTREAM.md)에
기록합니다.
