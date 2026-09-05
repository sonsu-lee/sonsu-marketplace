# 스킬 라우팅 평가

`cases.json`은 Engineering, Quality Engineering, Workflow, Research, Prompting, Product와 Fluent
Languages를 함께 또는 각각 설치했을 때의 기대 라우팅을 정의합니다. 직접 산출물 요청,
비슷하지만 다른 요청, runtime 조합과 단독 설치 사례를 포함합니다.

`workflow:to-pr` 사례는 선택된 스킬뿐 아니라 원격 변경이 없는 준비 모드인지, publish payload의
`target_pr_state`가 무엇인지도 선언할 수 있습니다. 이 경우에도 평가는 원격 PR을 만들지 않고
모델이 제안한 계획과 payload만 확인합니다.

`workflow:to-ticket`과 `workflow:ticket-lifecycle` 사례는 생성과 기존 티켓 변경을 분리하고,
`expected_intent`, `expected_relation`, `expected_assignee_change`, canonical ticket·assignee 확인,
mutation 후 재조회와 native automation 중복 방지 같은 기대 효과를 선언할 수 있습니다. 이 필드는 모델이 제안한 작업과
결과 보고를 평가하기 위한 계약이며 실제 원격 ticket 생성·수정 권한을 부여하지 않습니다.
`expected_relation.target`도 fixture locator일 뿐 canonical ticket의 증거가 아니므로 실행 시 두
ticket을 각각 검증해야 합니다. `must_use_native_relation`은 provider의 native operation을 우선해
판단하라는 뜻이지, 사용자가 금지한 필수 부수 효과까지 무시하고 mutation하라는 권한은 아닙니다.
`must_report_conflict`와 `must_not_propose_mutation`이 함께 있으면 그 충돌을 명시하고 원격 호출을
제안하지 않아야 합니다. `expected_assignee_change.target`이 특정 사용자라면 해당 사용자를 현재
assignee에서 검증하고 다른 assignee를 유지해야 합니다. `all`은 사용자가 모든 담당자 해제를
명시한 사례에서만 허용합니다.

이 평가는 실제 skill selection 결과를 대상으로 합니다. JSON 파싱이나 description 문자열 비교는
평가 실행을 대신하지 않습니다. 모델 기반 실행은 격리된 읽기 전용 fixture에서 수행하고 원격
push, ticket 게시와 PR 생성은 허용하지 않습니다. 결과는 `pass`, `fail`, `not_run`,
`inconclusive`로 구분하며, 선택 attribution을 확인할 수 없으면 `pass`로 판정하지 않습니다.

검색 공급자 사례의 `host_search_policy`는 해당 README 절의 Markdown 코드 블록만 호스트
지침으로 제공합니다. `installed_plugins`의 Research와 Exa Search description을 함께 노출하되
본문은 모델이 선택하여 읽게 합니다. Exa 전용 스킬의 정확한 버전과 description·본문의 hash를
실행 기록에 남깁니다. 별도 `fixture`가 없으면 관리형 Exa·Perplexity 검색 도구가 둘 다
노출·인증·가용한 동일 조건으로 시작합니다. `fixture`가 있으면 그 연결 유형과 capability만
제공하며 선언되지 않은 도구는 노출하지 않습니다. 실제 schema나 고정된 모의 schema를
기록하고 기대 field는 실행 모델에게 주지 않습니다.

호스트 자격 사례의 `provider_access`는 `managed`, `direct_adapter`, `unknown` 연결 유형을
제공합니다. 직접 adapter의 `opt_in_marker_valid`는 설치 manifest로 고정한 plugin-root README의
파일·marker·매핑 검증 결과이며, `secret_present`는 allowlist된 `secret_name`의 안전한 존재
확인 결과입니다. 실제 비밀값은 제공하지 않습니다. `qualification_reference_available: true`이면
모의 설치 manifest에서 Research root를 확인하고 그 아래 `skills/research/references/tool-routing.md`를
읽을 수 있게 합니다. false이면 규칙 경로를 확인할 수 없습니다. 이 reference만 읽는 것은
Research 전체 스킬 선택으로 세지 않습니다. `capability_state`의 성공 값은 호출할 경우의 모의
응답이며, 직접 adapter의 사전 자격 확인을 대체하는 기존 성공 증거로 제공하지 않습니다.
`generic_web`은 호스트가 허용한 `web_search` 모의 도구입니다.

`must_check_direct_qualification_before_request`는 직접 또는 불명확한 연결에서 reference·opt-in·
secret 존재 확인이 외부 요청보다 먼저 이뤄졌는지 검사합니다. 확인할 수 없는 조건에서는
호출을 차단해야 하며, `must_not_call_providers`는 최소 인증 시험 검색을 포함해 해당 공급자의
모든 외부 호출이 없는지 검사합니다. 관리형 기본 사례는 marker·secret 확인 없이 정상 검색해야
합니다. fixture 관찰과 실제 도구 선택·차단 순서를 trace에 함께 남깁니다.

`expected_first_search_provider`는 fetch가 아닌 첫 검색 호출을 검사합니다.
`expected_first_tool`이 있으면 해당 목적에서 사용할 실제 도구까지 확인합니다.
`must_select_provider_before_specialist_skill`은 일반 요청에서 공급자 전용 스킬 본문을 읽기
전에 이번 검색 목적에 따라 공급자를 선택했는지 확인합니다. `optional_after_provider_selection`은
그 선택 뒤에만 추가로 읽을 수 있는 스킬이며 필수 순서에 포함하지 않습니다. 사용자의 명시적
전용 스킬 요청은 이 순서의 예외입니다. `expected_sequence: []`인 짧은 조회도 호스트 정책의
공급자 선택은 검사합니다. `must_not_select`는 이 fixture의 첫 검색 준비 단계에 적용하며 후속
증거 목적 변경이나 실제 실패 시의 정상 fallback까지 금지하는 영구 규칙이 아닙니다.

모델이 모의 tool name·args를 출력하는 routing 평가, 실제 provider 연결 smoke test, Codex의
native 자동 skill selection은 별개의 검증입니다. 모의 trace나 JSON 검사만으로 native 선택이
보장된다고 보고하지 않습니다. Research 단독 조건과 호스트 지침·Exa 스킬 동시 설치 조건은
별도로 실행하고 baseline·변경 후의 입력과 모델 설정을 맞춥니다.
