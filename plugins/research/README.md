# Research

공개 검색부터 여러 출처의 사실 검증·비교·문헌·외부 코드 조사까지 원문 근거를 확인하고, 주장별 근거와 미확인 사항을 구분한 답변을 만듭니다.

## 설치

```bash
codex plugin add research@sonsu-marketplace
claude plugin install research@sonsu-marketplace
omp plugin install research@sonsu-marketplace
```

omp에서는 기본 구성에 들지 않는 opt-in 패키지이므로 필요할 때 직접 설치합니다.

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `research` | 공개 정보·URL을 검색하거나 여러 출처로 사실을 검증·비교하고, 기존 보고서의 인용을 감사하거나 외부 코드 사례를 조사할 때 | 결론·신뢰도, 주장별 근거, 상충·한계·미확인 사항. 감사 요청에는 판정 요약과 수정 보고서 |

Exa·Perplexity 같은 공급자가 없어도 현재 host의 web·browser·connector와 로컬 자료로 조사합니다. 공급자 선택·자격·실패 처리는 [도구 라우팅](skills/research/references/tool-routing.md), 증거 원장과 인용 감사는 [증거 정책](skills/research/references/evidence-policy.md)이 정합니다.

## 사용 예시

요청: “사내 위키에 옮겨 둔 두 오픈소스 빌드 도구의 라이선스 표가 맞는지 각 공식 저장소로 확인해 줘.”

```text
결론: 도구 A 행은 맞고, 도구 B 행은 수정이 필요하다. 전체 신뢰도: high.
C1 [확인됨]: 도구 A는 MIT — 공식 저장소 기준 commit의 LICENSE 첫 줄.
C2 [상충]: 위키는 도구 B를 MIT로 적었으나 공식 저장소 기준 commit의 LICENSE는 Apache-2.0이다.
다음 행동: 위키 표의 도구 B 라이선스와 확인 commit을 갱신한다.
```

## 구성

### 선택적 공급자

플러그인은 공급자·MCP·CLI·package·계정 연결을 자동으로 설치하지 않으며, manifest에 provider dependency나 `mcpServers`를 선언하지 않습니다. host가 관리하는 공급자는 읽기 전용 도구, 현재 입력 스키마, 인증과 최소 읽기 호출이 확인되면 사용합니다.

직접 API·CLI adapter는 아래 선언, 해당 secret의 존재 여부와 실제 읽기 전용 도구·스키마·인증을 모두 확인한 뒤 사용합니다. API key는 구성된 adapter의 인증에만 쓰고 값·길이·일부 문자열을 모델 컨텍스트, shell 출력, 로그나 저장소에 남기지 않습니다.

<!-- research-provider-opt-in:v1:start -->
```yaml
providers:
  exa:
    env: EXA_API_KEY
  perplexity:
    env: PERPLEXITY_API_KEY
```
<!-- research-provider-opt-in:v1:end -->

### 코드 검색 cache

반복 코드 조사는 사용자가 영속 저장과 절대 경로를 승인한 경우에만 metadata-only SQLite helper를 사용합니다. 기본값은 `off`이며 source code, snippet, diff, credential과 비공개 문서 본문은 저장하지 않습니다. 검색 전략과 artifact 규칙은 [외부 코드 검색과 재사용](skills/research/references/code-search.md)에 있습니다.

```bash
python3 skills/research/scripts/code_search_cache.py init --db /absolute/path/code-search.sqlite3
python3 skills/research/scripts/code_search_cache.py lookup --db /absolute/path/code-search.sqlite3 --input query.json
```

### 작업 연속성

여러 단계 작업은 [작업 연속성 참고 자료](references/continuity.md)에 따라 `.sonsu/continuity/`에 진행과 근거 위치를 기록하고 컴팩션·재개 후 현재 상태와 대조합니다. 포함된 `SessionStart` hook은 CLI의 `/hooks`에서 검토·신뢰한 뒤 실행되며, 사용할 수 없으면 참고 자료의 `read` 단계부터 수동으로 재개합니다. helper는 Python 3.9+와 POSIX(macOS/Linux)를 사용합니다. [기록 형식](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고하세요.

출처와 로컬 변경 범위는 [`UPSTREAM.md`](UPSTREAM.md)에 있습니다.

## 검증

```bash
python3 -B -m unittest discover -s plugins/research/tests -p 'test_*.py' -v
python3 -B -m unittest plugins/research/skills/research/scripts/tests/test_code_search_cache.py -v
```
