# 스킬 라우팅 평가

`cases.json`은 Engineering, Workflow, Research, Prompting, Product, Writing과 언어별 Fluent
플러그인을 함께 또는 각각 설치했을 때의 기대 라우팅을 정의합니다. 직접 산출물 요청,
비슷하지만 다른 요청, runtime 조합과 단독 설치 사례를 포함합니다.

`workflow:to-pr` 사례는 선택된 스킬뿐 아니라 원격 변경이 없는 준비 모드인지, publish payload의
`target_pr_state`가 무엇인지도 선언할 수 있습니다. 이 경우에도 평가는 원격 PR을 만들지 않고
모델이 제안한 계획과 payload만 확인합니다.

`workflow:to-ticket`과 `workflow:ticket-lifecycle` 사례는 생성·내용 수정과 lifecycle 변경을 분리하고,
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

Writing은 공통 구성을 담당합니다. 영어 Fluent는 일상·기술 문장의 작성·윤문·검토에, 일본어 Fluent는 작성·윤문과 문서 진단에 적용합니다. 한국어 Fluent는
기존 글의 AI 티·번역투 윤문이나 진단 요청에 적용합니다. Workflow는 자체 양식과
운영 절차에 적합한 지침을 적용합니다. 분리·조합 사례의 기대값은 실제 native 라우팅 결과와
구분하며, [명시적 지침 적용 검사](../writing/README.md)만으로 자동 선택을 통과했다고 하지 않습니다.
일상 메시지와 기술 설명의 선택 경계를 각 언어별로 확인하는 사례도 포함합니다.
일본어 기술 문서의 Markdown 구조만 바꾸는 요청은 Writing으로 보내고 Fluent를 선택하지 않는
사례로 범위를 확인합니다.

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

## 티켓 양식·내용 수정 사례

`expected_action`은 create/revise, `expected_mode`는 draft/publish를 구분합니다.
`expected_template`은 적용할 양식을, `expected_structure`는 상하위 구성을 나타내며 native
label·type·status 값이 아닙니다. 기본 양식은 변경·추가·정리 요청의 `default`, 잘못된 동작 수정의
`bug`, 답변·판단 근거 마련의 `investigation`입니다. 버그 수정 과정에 원인 조사가 포함돼도 `bug`를 사용합니다.
`must_include_reproduction_section`은 증상 설명에 재현 정보를 포함하는지,
`must_not_classify_readiness`는 준비 상태 분류를 강제하지 않는지 확인합니다.
`must_ask_for_problem_context`는 문제 자체를 특정할 수 없을 때 핵심 질문을 반환하는지 검사합니다.
`must_preserve_preference_vs_agreement`와 `must_not_invent_implementation`은 선호·합의의 강도를
보존하고 요청에 없는 구현을 만들지 않는지, `must_not_add_completion_checklist`와
`must_not_add_empty_optional_sections`는 불필요한 항목을 붙이지 않는지 확인합니다. `expected_template_source`는 team과 temporary-fallback 등의
출처 확인을 검사합니다. `must_preserve_*`는 실제 초안·수정 payload에서 해당 내용이 유지되는지,
`expected_child_count`와 `must_map_parent_and_child_keys`는 사용자가 지정한 분해 경계와 게시 전
부모·자식 참조를 실제 초안에서 확인합니다. `must_limit_update_to_content`는 식별자 이외의 변경 field가 요청한 제목·본문에 한정되는지 검사합니다.

`expected_required_headings`와 `expected_omitted_headings`는 완성된 기본형에서 필요한 항목과 생략할
항목을 검사하며, 고정된 팀 양식에는 적용하지 않습니다. `must_preserve_actual_and_expected`,
`must_preserve_request_response`, `must_include_reproduction_media`는 버그의 동작·요청·응답·제공 자료
보존을 확인합니다. `must_not_repeat_expected_behavior`는 같은 기대 동작을 현상과 고려 사항에 반복하지 않는지,
`must_report_unavailable_reproduction_media`는 자료가 없는 버그의 미확보 표시를 확인합니다.
`must_not_require_visual_media`, `must_not_split_investigation`,
`must_not_invent_deliverable_format`은 자료 유형·티켓 분리·조사 산출물을 임의로 강제하지 않는지,
`must_summarize_external_decisions`는 링크와 함께 필요한 외부 합의를 본문에 담는지 확인합니다.

PR의 `must_preserve_manual_verification`과 `must_not_claim_ci_success`는 수동 확인과 CI 근거를
구분합니다. `must_not_repeat_ci_checks`는 CI가 다루는 자동 검사를 본문에 반복하지 않는지,
`must_keep_publication_procedure_outside_body`는 게시·첨부 준비 절차를 본문 밖에서 보고하는지 확인합니다.
`must_only_state_missing_media_in_body`는 자료가 없을 때 본문에는 짧은 미확보 사실만 남기는지 확인합니다.
`must_report_missing_required_media`, `must_not_claim_media_uploaded`, `must_keep_draft`는
필수 미디어 미준비·업로드 불명 상태를 성공으로 바꾸거나 Ready로 전환하지 않는지 확인합니다.

`fixture`는 정확히 그 시점에 확인 가능한 모의 응답만 제공합니다. `before_write_body`는 쓰기 직전
재조회 결과이며 첫 읽기에 제공하지 않습니다. `update_response`·`readback_response`도 해당 모의
operation 뒤에만 노출합니다. 기대 field는 실행 모델에게 제공하지 않습니다. 응답 불명확·ADF 손실·
동시 수정 충돌에서 제안한 쓰기 횟수와 보존 결과를 읽어 판정하며, 원격 mutation은 수행하지 않습니다.

Linear branch 사례는 repository 관례·integration 추천이 있어도 ID를 자동 삽입하지 않는지와
사용자 지정 정확한 이름의 예외를 함께 검사합니다. branch 제안 사례는 생성 권한을 부여하지 않습니다.
새 사례의 정적 등록과 모의 모델 실행, 실제 host의 native skill selection, 실제 tracker read/write는
각각 별개의 검증으로 보고합니다.

## 내용 수정 후 lifecycle 인계

`fixture.continuation_observation`은 내용 수정 이후 시점까지 이미 관찰한 요청·쓰기 응답·readback과
현재 인계 정보를 제공합니다. 미래 도구 응답이 아닙니다. `content_write_response`가 success여도
`content_readback`이 unavailable이면 실제 반영은 확인되지 않은 상태이며, timeout이어도 readback이
목표 내용과 보존할 내용을 담으면 실제 반영을 판정할 수 있습니다. no-op은 쓰지 않았다는 사실만으로
성립하지 않고 최신 내용이 목표와 같다는 근거가 필요합니다.

이 continuation 사례는 첫 skill 선택 순서를 고정하지 않습니다. `expected_lifecycle_mutation_allowed`는
후속 상태·담당자·관계 mutation이 허용되는지, `expected_content_result`는 field별 결과와 전체 선행
조건의 판정을 검사합니다. partial은 새 원격 상태가 아니라 field별 성공·실패가 섞였다는 평가 요약입니다.
`must_check_content_prerequisite`는 요청한 내용 성공이 선행 조건인지 확인하고,
`must_reread_lifecycle_state`는 허용된 후속 작업도 최신 상태·권한으로 진행하는지 검사합니다.
명시적으로 독립된 담당자 해제와 lifecycle 단독 요청에는 무관한 본문 성공 조건을 붙이지 않습니다.

모델에는 기대 field와 판정을 암시하는 case 이름을 제외하고 opaque ID, 요청과 관찰 이력만 줍니다.
원격 mutation 없이 다음에 제안한 operation과 인계 근거를 읽어 판정하며 native 실행과 구분합니다.
