# 외부 코드 검색과 재사용

GitHub와 외부 공개 저장소에서 코드 패턴 후보를 넓게 찾거나, 이전 검색 결과를 재사용해야 할 때 읽는다. 검색 결과는 후보 발견 수단이며 [코드 조사](code-research.md)의 provenance·호출 경로·테스트·라이선스 gate를 통과하기 전에는 좋은 사례나 근거가 아니다.

## 검색 계약

검색 전에 다음 값을 비공개 작업 상태로 고정한다.

```text
behavior: 찾을 동작과 성공·실패 의미
language_and_version
framework_and_version
runtime_and_platform
required_context: 반드시 확인할 호출부·설정·테스트·라이선스
exclusions: 예제 전용, deprecated, generated, vendored 등
quality_rubric_version
query_strategy_version
persistence: off | cache | catalog
cache_path: persistence가 cache 또는 catalog일 때 사용자가 승인한 절대 경로
freshness_policy: immutable 사실과 다시 확인할 mutable 사실
```

`persistence`의 기본값은 `off`다. 사용자가 이전 결과 재사용이나 저장을 요청했더라도 저장 위치와 공개·비공개 범위가 명확하지 않으면 먼저 채팅 안에서만 중복을 제거한다. 파일이나 데이터베이스를 만들 권한으로 확대하지 않는다.

## 좋은 패턴의 판정

인기, star 수, 검색 순위와 코드 모양만으로 좋은 패턴을 판정하지 않는다. 먼저 다음 hard gate를 적용한다.

1. canonical repository와 full commit SHA가 고정됐다.
2. 정의, 실제 call site, feature·설정 조건과 정상 entry path가 같은 snapshot에서 연결됐다.
3. 테스트가 존재한다고 주장하려면 같은 snapshot의 assertion과 production 경로의 관계를 확인했다.
4. 오류, timeout, cancellation, retry, cleanup 같은 실패 의미가 요청한 동작과 일치한다.
5. 재사용이 목적이면 라이선스와 경로별 고지 범위를 확인했다.
6. mixed revision, generated·vendored copy, dead·deprecated code와 예제 전용 코드를 독립적인 production 사례로 세지 않았다.

hard gate를 통과한 사례만 같은 `quality_rubric_version` 안에서 비교한다. 점수와 설명에는 최소한 다음 축을 사용한다.

- 요청한 환경·버전과의 적합성
- 제어 흐름과 실패 처리의 정확성
- production reachability와 운영 근거
- assertion의 깊이와 회귀 방지 능력
- 단순성, 가독성과 불필요한 추상화의 정도
- 관측 가능성, 취소·정리와 경계 조건
- 유지보수 상태와 알려진 regression·반례
- 라이선스와 다른 코드베이스로 옮길 때 필요한 맥락

점수는 근거를 대체하지 않는다. hard gate 실패는 낮은 점수가 아니라 `rejected` 또는 `partial`이며, rubric이 바뀌면 기존 원문을 다시 내려받지 않고도 저장된 immutable locator를 새 rubric으로 재평가할 수 있다.

## 질의 묶음

표현만 바꾼 동일 질의를 반복하지 말고 서로 다른 증거 역할을 가진 query family를 만든다.

| family | 목적 | 예시 단서 |
| --- | --- | --- |
| `definition` | 구현 후보 발견 | 정확한 symbol, API, type, import |
| `usage` | 실제 호출부와 wiring 발견 | call expression, constructor, entry point |
| `behavior` | 의미가 같은 구현 발견 | 오류 문자열, config key, protocol token, 상태 전이 |
| `test` | assertion과 경계 조건 발견 | test name, fixture, expected error, timeout |
| `provenance` | 버전·수정 이유·릴리스 관계 확인 | commit, PR, issue, changelog, release |
| `counterexample` | 실패·폐기·regression 탐색 | deprecated, bug, race, leak, flaky, regression |

처음에는 의미 기반 탐색이나 일반 웹 검색으로 repository 후보를 만들 수 있다. 이름을 모르는 넓은 후보 발견에는 Exa, 이미 정해진 구현·라이브러리의 사실·현재 지원·비교에는 Perplexity를 우선하며, 기술 주제 자체를 Exa 선택 근거로 삼지 않는다. 후보를 고른 뒤에는 GitHub code search, repository 내부 검색과 git history처럼 정확한 식별자를 다루는 경로로 좁힌다. 검색 목적이 바뀌면 [도구 라우팅](tool-routing.md)을 재적용한다. 공급자별 현재 qualifier, pagination, query 길이, result cap과 default-branch 범위는 실행 시 도구 schema·공식 문서·help에서 확인하며 기억한 한도를 고정값으로 가정하지 않는다.

## 수집과 검증

1. query family마다 목적, query, filters, 예상 증거 역할을 기록한다.
2. 검색 결과를 `canonical_repository + full_commit_sha + file_path + symbol 또는 line range` 후보로 정규화한다.
3. fork, mirror, 동일 blob, vendored copy와 같은 계보 중복을 제거한다.
4. 높은 recall이 필요한 후보 수집과 비용이 큰 원문 검증을 분리한다. 검색 snippet이나 match count에는 점수를 주지 않는다.
5. 상위 후보를 full SHA로 고정하고 정의, 호출부, 설정, 테스트, 라이선스를 같은 snapshot에서 hydrate한다.
6. hard gate를 통과한 후보만 평가하고, 실패한 후보도 재검색 방지를 위해 거부 이유와 rubric version을 남길 수 있다.
7. 마지막 query family 또는 shard가 새 canonical artifact나 결론을 바꿀 근거를 더 이상 만들지 않으면 포화 이유를 기록한다.

## `bounded` brute force(범위를 제한한 완전 탐색)

브루트포스는 모집단 경계와 중복 키가 있을 때만 사용한다. result cap에 걸린 동일 질의를 페이지로만 반복하지 말고 language, organization, repository, path, extension, version 또는 다른 상호 배타적인 qualifier로 shard한다. 각 shard에는 다음 정보를 남긴다.

```text
shard_key
query_fingerprint
pages_or_cursors_examined
reported_result_count
unique_artifacts_added
duplicate_artifacts
incomplete_or_capped
failure_kind
```

cap이나 `incomplete` 상태가 있으면 전수 조사라고 표현하지 않는다. 새 shard가 기존 artifact만 반복하고 핵심 공백을 줄이지 못하면 확장을 중단한다. repository를 먼저 선별한 뒤 내부에서 병렬 검색하는 편이 전체 GitHub를 무차별 순회하는 것보다 검증 비용을 통제하기 쉽다.

## 영속 상태와 재사용

영속 상태는 raw 검색 결과 덤프가 아니라 다음 세 층으로 나눈다.

| 층 | 목적 | 기본 보존 내용 |
| --- | --- | --- |
| search cache | 같은 질의와 pagination의 반복 방지 | query contract, fingerprint, 실행 시각, cursor, artifact ID |
| evidence store | 검증을 다시 수행할 위치 보존 | canonical repository, full SHA, path, symbol/range, blob SHA, immutable locator |
| curated catalog | 좋은 사례만 재사용 | accepted artifact, rubric version, 판정과 짧은 적용 메모 |

query fingerprint는 `provider + normalized query + filters + language/framework/version + query_strategy_version`의 canonical JSON SHA-256이다. query와 filter 문자열은 바깥쪽 공백만 제거하고 정규식·문자열 리터럴의 의미가 달라질 수 있는 내부 공백은 보존한다. artifact ID는 정규화한 `canonical repository + full commit SHA + file path + symbol 또는 line range`의 canonical JSON SHA-256이다. GitHub의 `owner/repository`, HTTP(S) URL과 `.git` suffix는 같은 canonical HTTPS repository로 합친다. commit과 blob object ID는 정확히 40자 또는 64자 hex만 허용한다. blob SHA는 snapshot 무결성과 copy 계보 확인에 사용하되, 나중에 blob SHA를 확보했다는 이유만으로 같은 artifact를 새 사례로 만들지 않는다.

immutable commit의 코드, path와 blob은 재사용할 수 있다. 현재 default branch·HEAD, 최신 release 포함 여부, 저장소 archived 상태, 현재 라이선스 정책, 열려 있는 issue와 유지보수 상태처럼 mutable한 주장은 매번 다시 확인한다.

재실행할 때는 다음 순서를 사용한다.

1. 현재 계약으로 fingerprint를 계산하고 cache를 조회한다.
2. 기존 artifact를 `reused`, mutable 사실을 다시 확인한 항목을 `revalidated`, 새 후보를 `new`, 더 이상 맞지 않는 항목을 `stale`, hard gate 실패를 `rejected`로 구분한다.
3. 기존 검색 전체를 반복하지 않고 누락된 query family, 미완료 shard, stale한 mutable fact와 열린 evidence gap만 검색한다.
4. `quality_rubric_version`이 바뀌었으면 immutable artifact를 다시 fetch하기 전에 저장된 locator로 재평가 가능한지 확인한다.
5. 최종 결과에는 새로 찾은 근거와 재사용한 근거를 구분하되, 내부 cache 상세는 감사 자료를 요청받은 경우에만 노출한다.

## 로컬 SQLite helper

`scripts/code_search_cache.py`는 표준 라이브러리만 사용하는 선택적 metadata cache다. 자동으로 실행하지 않는다.

- 사용자가 승인한, 이미 존재하는 디렉터리 아래의 절대 `--db` 경로만 받는다.
- 새 DB는 mode `0600`으로 만든다.
- 기본 권고 위치는 조사 대상 Git repository 밖의 사용자 소유 상태 디렉터리다. DB, journal과 lock 파일을 자동으로 commit하거나 `.gitignore`에 추가하지 않는다.
- query contract, run 상태, immutable locator, 평가와 catalog 승격만 저장한다.
- source code, snippet, diff, 검색 원문, credential과 비공개 문서 본문은 입력 schema에서 허용하지 않는다.
- `record-run`, `evaluate`, `promote`는 쓰기 작업이므로 각 조사에서 승인된 persistence 범위 안에서만 호출한다.
- `lookup`과 `catalog`은 외부 검색을 수행하지 않으며 DB의 기존 metadata만 읽는다.
- `init`과 모든 DB 명령은 schema version만 보지 않고 필수 table, column, foreign key, unique constraint와 catalog invariant trigger를 검증한다. 일부만 만들어진 파일을 cache로 간주하지 않는다.
- 기존 artifact의 `blob_sha`, `immutable_locator`, `role` 또는 `license`가 보강·변경되면 그 metadata에 기대던 평가와 catalog 항목을 같은 transaction에서 무효화하고 재평가를 요구한다. 충돌하는 non-null `blob_sha`는 갱신하지 않고 거부한다.
- `lookup`은 실제 `searched_at` 기준의 최신 run을 반환하고 `complete`를 JSON boolean으로 직렬화한다. 최신 complete run에서 사라진 artifact는 `stale`로, 선택한 rubric의 hard gate가 실패한 artifact는 `partial` 또는 `rejected`로 표시한다.

대표적인 흐름은 다음과 같다.

```text
init --db <absolute-path>
fingerprint --input <query-contract.json>
lookup --db <absolute-path> --input <query-contract.json> [--rubric-version <version>]
record-run --db <absolute-path> --input <verified-run.json>
evaluate --db <absolute-path> --input <evaluation.json>
promote --db <absolute-path> --input <promotion.json>
catalog --db <absolute-path> [--rubric-version <version>]
```

`record-run` 입력은 검증된 metadata만 포함한다.

```json
{
  "query_contract": {
    "provider": "github",
    "query": "retry_with_backoff lang:rust",
    "filters": {"path": "src"},
    "language": "Rust",
    "framework": "Tokio",
    "version": "1.x",
    "strategy_version": "code-search-v1"
  },
  "run": {
    "searched_at": "2026-09-02T10:00:00Z",
    "status": "complete",
    "complete": true,
    "result_count": 1
  },
  "artifacts": [{
    "canonical_repository": "https://github.com/owner/repository",
    "full_commit_sha": "<full-sha>",
    "file_path": "src/retry.rs",
    "symbol": "retry_with_backoff",
    "line_start": 20,
    "line_end": 54,
    "blob_sha": "<full-blob-sha>",
    "immutable_locator": "<commit-permalink>",
    "role": "release_path",
    "license": "MIT",
    "verified_at": "2026-09-02T10:00:00Z"
  }]
}
```

`evaluate`는 `artifact_id`, `rubric_version`, `accepted | partial | rejected`, 숫자형 `scores`, 짧은 `rationale`와 `evaluated_at`을 받는다. `promote`는 같은 `artifact_id`와 `rubric_version`, 적용 맥락을 설명하는 `note`, `promoted_at`을 받으며 `accepted` 평가만 catalog에 넣는다. 이 조건은 승격 SQL과 DB trigger가 함께 강제하므로 평가가 동시에 바뀌어도 rejected 결과가 catalog에 남지 않는다. 재평가가 `partial`이나 `rejected`로 바뀌면 기존 catalog 항목을 제거한다. 여러 rubric의 평가가 함께 저장된 경우 `lookup --rubric-version`으로 이번 조사에서 사용할 판정을 지정한다.

메모리 저장을 별도로 요청받았더라도 raw 결과나 전체 catalog를 넣지 않는다. 장기 정책, 사용자가 선택한 cache locator와 대표 artifact ID처럼 작은 pointer만 남기고, 실제 검색·검증 상태는 이 구조화된 저장소에서 조회한다.
