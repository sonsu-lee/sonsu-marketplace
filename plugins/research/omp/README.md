# Research

단일 공개 웹 검색부터 여러 출처의 조사, 사실 확인, 문헌 검토와 외부 코드 사례 조사까지
담당하는 개인 Codex·Claude Code 플러그인입니다. 특정 검색 공급자가 없어도 현재 host에 이미 제공된 web, browser, connector와
로컬 자료를 사용해 가능한 범위에서 독립적으로 동작합니다. Engineering 또는 별도의
planning·Git workflow를 먼저 실행하거나 함께 설치했다고 가정하지 않습니다.

```sh
codex plugin add research@sonsu-marketplace
```

## 선택적 공급자 설정

Exa와 Perplexity는 선택적 검색 공급자입니다. 이 플러그인은 공급자, MCP, CLI, package 또는
계정 연결을 자동으로 설치하지 않습니다. 두 공급자가 모두 없어도 generic web, browser,
connector와 로컬 자료로 조사하고, 그 결과가 현재성·완전성·독립성을 실제로 낮출 때만 한계를
밝힙니다. plugin manifest에 provider dependency나 `mcpServers`를 선언하지 않고 별도
`.mcp.json`도 함께 배포하지 않습니다.

Codex가 관리하는 공급자는 읽기 전용 도구 노출, 현재 입력 스키마, 인증과 최소
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

## 플러그인 내부의 공급자 선택

일반 검색과 단일 사실·URL 검색도 `research`에서 공급자를 선택한 뒤 `lookup`으로 짧게
완료합니다. 이 동작에 전역 `AGENTS.md`, 머신별 설정이나 공급자 전용 스킬은 필요하지 않습니다.
플러그인 설치는 전역 지침과 설치된 다른 플러그인의 캐시를 수정하지 않습니다. 제공 자료·로컬
조회, 이미 위치를 아는 공식 페이지 읽기와 전용 날씨·스포츠 도구 조회는 바로 처리합니다.

| 필요한 결과 | 기본 경로와 활용할 장점 |
| --- | --- |
| 자연어로 의미·특징을 설명하며 아직 모르는 자료·논문·구현·회사 후보 발견 | Exa 검색: 관련 페이지·본문을 찾아 후보군 확장 |
| 정해진 대상의 사실·공식 URL·현재 지원·최근 변경 또는 도메인·기간·지역 조건이 있는 검색 | Perplexity Search: 순위 있는 제목·URL·날짜·스니펫과 구조화 필터 |
| 알려진 URL의 본문 읽기 | 원문 직접 열기 또는 Exa fetch로 본문 추출 |
| 생성 설명·분석이 실제 필요한 중간 자료 | 노출된 Perplexity answer·reason·research 계열 검토; 원문과 인용 별도 검증 |
| 목적이 애매한 일반 검색 | Perplexity Search로 시작하고 필요한 결과에 따라 재판단 |

이는 공식 문서에 확인된 기능과 실제 노출된 도구를 연결한 기본 정책입니다. 두 API의 기능은
겹치며 보편적인 검색 품질 우열이나 한 공급자의 독점 기능을 뜻하지 않습니다. 노출된 schema에
필요한 필터·본문·출력 기능이 없으면 사용자가 공급자를 지정하지 않은 범위에서 자격을 충족한 다른 경로를 사용합니다. 지정한 공급자 결과에 필요한 기능이 없으면 한계를 알리고 허용 없이 대체하지 않습니다.

예를 들어 Exa로 Rust retry 구현 후보를 발견하고, 선택한 구현의 현재 지원·릴리스를 Perplexity로
확인한 뒤, 찾은 URL의 원문을 Exa fetch로 읽을 수 있습니다. 같은 기본 질문을 양쪽에 반복하거나
사용 비율을 맞추기 위해 검색을 추가하지 않습니다. 사용자 지정 공급자·전용 스킬은 지정 범위에서
우선하고, 실제 사용 불가 시 조용히 대체하지 않습니다. 공급자 전용 스킬은 일반 요청에서 이
선택을 대신하지 않으며 선택 후 사용법 참고로 적용합니다.

기능 근거, 공급자 자격, 도구별 비용과 실패 처리, generic fallback은
[`skills/research/references/tool-routing.md`](skills/research/references/tool-routing.md)에 있습니다.
스킬이 선택되기 전의 자동 호출은 호스트의 description 판단에 달려 있으므로, 플러그인 단독과
Exa 전용 스킬 동시 설치를 전역 지침 없는 새 문맥에서 별도로 평가합니다. 설치·스키마 확인과
모델의 실제 스킬·도구 선택을 구분하며, 호스트 전체의 자동 선택을 강제한다고 주장하지 않습니다.

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

## 컴팩션 후 작업 재개

[작업 연속성 참고 자료](references/continuity.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 참고 자료·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 참고 자료를
읽고 수동으로 재개할 수 있습니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고하세요.
