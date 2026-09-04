# 스킬 라우팅

- Status: Current
- Last reviewed: 2026-09-04

## 플러그인 경계

Engineering, Quality Engineering, Workflow, Research, Prompting, Product, Figma Workflow과 Fluent Languages는
각각 단독으로 설치하고 사용할 수 있는 독립 플러그인입니다. 한 플러그인이 다른 플러그인을
import하거나 설치·선행 실행·특정 skill ID를 전제로 하지 않습니다. 여러 영역을 포함한 요청은
Codex가 현재 설치된 스킬의 description과 요청의 직접 목적을 바탕으로 필요한 스킬을 순서대로
선택합니다.

| 직접 목적 | 담당 |
| --- | --- |
| 구현, 디버깅, 계획 실행과 개발 방법론 | `engineering:*` |
| 확인된 계약과 trust boundary를 코드 형태로 직접 반영 | `quality-engineering:domain-shaped-code` |
| 명시적으로 요청한 최소 구현, 삭제 우선과 YAGNI | `quality-engineering:simplify-code` |
| diff·commit·branch의 over-engineering 검토 | `quality-engineering:review-overengineering` |
| repository 또는 큰 경로의 over-engineering audit | `quality-engineering:audit-overengineering` |
| reader load와 유지보수성 검토 | `quality-engineering:review-maintainability` |
| 도달 가능한 실패 경로 검토 | `quality-engineering:review-failure-modes` |
| error ownership, logging과 운용 가능성 검토 | `quality-engineering:review-operability` |
| 여러 quality lens를 아우르는 broad review | `quality-engineering:review-quality` |
| branch, staging, commit, 일반 push와 Git 변경 검토 | `workflow:git-workflow` |
| ticket·issue·backlog 초안 또는 생성 metadata를 포함한 게시 | `workflow:to-ticket` |
| 기존 ticket의 작업 시작·review·완료 상태, 담당자와 native relation 변경 | `workflow:ticket-lifecycle` |
| 현재 branch의 새 GitHub PR 초안 또는 게시 | `workflow:to-pr` |
| 외부 다중 출처 조사, 사실 검증, 문헌 검토와 근거 중심 code research | `research:research` |
| Codex·ChatGPT·OpenAI API용 프롬프트 생성·재작성·최적화 | `prompting:prompt-builder` |
| 제품 문제·기회·가치 제안과 해법 후보 발산 | `product:product-brainstorming` |
| 제품 사용자·문제·기대 결과·범위와 미해결 결정 구체화 | `product:product-discovery` |
| 인터뷰·설문·피드백·이슈·지표의 traceable synthesis | `product:synthesize-product-evidence` |
| 제품 용어·상태·사건·규칙·예외의 후보 모델 탐색 | `product:product-domain-discovery` |
| 제품 가설의 실행 전 검증 방법·계측·판정 기준 설계 | `product:design-product-test` |
| 실행된 제품 검증을 사전 기준으로 판정 | `product:assess-product-test` |
| 승인된 제품 합의를 PRD로 변환 | `product:to-prd` |
| Figma 제품 화면 생성·수정과 responsive layout | `figma-workflow:figma-product-design` |
| Figma의 실제 prototype connection, overlay와 상태 동선 | `figma-workflow:figma-prototype-flow` |
| 기존 Figma artifact의 구조·interaction에 대한 읽기 전용 감사 | `figma-workflow:figma-design-audit` |

직접적인 산출물과 관점 요청을 우선하여 라우팅합니다. 예를 들어 현재 branch로 PR을 만들어 달라는
요청은 `workflow:to-pr`의 범위이며, 완료된 구현을 어떤 방식으로 통합할지 결정해 달라는
요청은 `engineering:finishing-a-development-branch`의 범위입니다.

```text
구현하고 PR 초안까지 준비
  → Engineering으로 구현·검증
  → Workflow의 to-pr로 현재 branch를 다시 확인하고 PR 산출물 준비
```

이 순서는 runtime 조합이며 플러그인 dependency가 아닙니다. Workflow만 설치된 환경에서는
Git·ticket·PR 작업이 독립적으로 동작하고, Engineering만 설치된 환경에서는 자체 개발 및
branch 완료 흐름이 동작해야 합니다. 공통 router는 실제 경쟁 트리거가 반복해서 확인되기
전에는 추가하지 않습니다.

## Engineering 실행 경로

Engineering은 작업을 중앙 orchestrator 하나로 모으지 않고 기존 stage-owned gate를 유지합니다.
Fast Path는 target discovery 전에 stable todo ID 또는 한 번 생성한 UUID를 고정하고 매 entry에서
`.engineering/fast-path/<task-id>.state`를 먼저 확인합니다. 이미 `disqualified`인 task는 classifier,
predicate, execution을 건너뛰고 가장 가까운 일반 workflow로 갑니다. `unclassified` task만 아래의
독립 classifier gate를 통과해야 plan 없는 Fast Path를 사용합니다.

```text
명확한 요청
  → controller 표적 탐색 1회: 대상·관찰 결과·완료 조건, references, consumers, public-contract risk, oracle
  → fresh gpt-5.6-luna/low classifier의 독립 표적 탐색 1회
  → classifier verdict eligible | escalate | inconclusive | blocked
  → eligible일 때만 exact candidate revision과 evidence digest를 state에 기록
  → 효과 또는 변환 규칙과 직접 소비자 범위를 두 탐색 안에 닫음
  → public contract·schema·상태·권한·migration·호환성 변경 없음
  → 저렴한 결정론적 검증 존재
    → Local Fast Path 또는 Mechanical Fast Path
  classifier non-eligible, unavailable, false 또는 unknown predicate
    → persistent disqualified latch → nearest normal workflow
  그 외
    → brainstorming → 승인된 짧은 설계
      → plan 필요: writing-plans → plan-backed execution
      → plan 불필요: bounded direct execution
```

Mechanical Fast Path는 파일 수가 아니라 결정론적인 변환 규칙과 닫힌 영향 범위로 판단합니다.
현재 surface가 Code Mode(`functions.exec` 또는 동등한 orchestration)를 제공하면 반복 검색, parser,
변환과 postcondition 검사를 묶는 실행 수단으로 우선 사용할 수 있습니다. Code Mode 사용 가능성은
Fast Path 적합성이나 품질 판정의 근거가 아닙니다.

Fast Path는 표적 탐색 2회, 최초 구현 1회, 집중 수정 1회와 총 자동 시도 2회로 제한합니다. fresh
`gpt-5.6-luna` / `low` classifier가 유일한 Fast Path subagent slot이며 implementation/reviewer subagent는
기본 경로에서 만들지 않습니다. 숨은 소비자, 두 번째 의미 판단, public contract, 원인 불명 실패,
넓어진 책임, related refactor 또는 second correction이 발견되면 `disqualified`를 영속 latch하고
task ID와 state-file path를 handoff에 넣어 one-way owner escalation을 실행합니다. 원인 불명은
`systematic-debugging`, multi-flow/interface는 `writing-plans`, requirement/design 변경은
`brainstorming`으로 보내며 이 경로는 classifier, predicate, execution으로 재진입하지 않습니다.

plan artifact가 있는 모든 실행 경로는 결정론적 검증과 일반 최종 리뷰 뒤에 fresh-context
red-team completion review를 수행합니다. 이 reviewer는 이전 session history와 verdict를 받지
않고 원래 목표, 승인된 요구사항·설계, 행동 의사코드·mapping, immutable 전체 변경 package,
검증 근거와 관찰 결과만으로 전체 구조를 반증합니다. `survives_challenge`만 일반 통과이며
`invalidated`, `inconclusive`, `blocked`는 각각 실제 design, plan, implementation, verification
또는 capability 소유 단계로 돌아갑니다. plan 없는 Fast Path에는 이 게이트를 강제하지 않습니다.

Engineering의 자동 review/fix loop는 기본 최대 3회입니다. task fix는 1회차만 원래 implementer를
재사용하고, 2-3회차는 artifact 중심의 fresh context를 사용합니다. red-team 재시도도 변경된
리비전과 서로 다른 fresh reviewer로 최대 3회입니다. 상한은 유효한 finding을 통과로 바꾸지
않습니다.

## Prompting 조합

Prompting은 사용자가 실제로 사용할 프롬프트 산출물을 요청했을 때 선택합니다. 프롬프트를
생성하거나 기존 프롬프트를 재작성·최적화하는 요청은 `prompting:prompt-builder`가 담당하며,
prompt engineering 개념만 설명해 달라는 요청에는 선택하지 않습니다.

Codex용 작업 프롬프트를 작성하더라도 그 요청 자체가 구현이나 개발 계획 실행을 의미하지는
않으므로 Engineering을 자동으로 함께 선택하지 않습니다. 반대로 구현 요청 안에 포함된 일반
자연어 요구사항을 Prompting으로 먼저 재작성해야 한다고 가정하지 않습니다. 사용자가 프롬프트
산출물과 구현을 모두 요청했을 때만 직접 목적에 따라 runtime에서 조합합니다.

Prompting만 설치된 환경에서도 Codex, ChatGPT와 OpenAI API용 프롬프트를 독립적으로 작성할 수
있어야 합니다. 특정 OpenAI 모델이나 제품 surface가 결과에 영향을 주면 포함된 snapshot을
참고하고, 최신 또는 현재 권고를 요청받으면 OpenAI 공식 문서를 다시 확인합니다.

## Quality Engineering 조합

Quality Engineering은 code shape, simplicity, maintainability, reachable failure mode와 operability를
담당합니다. 일반적인 기능 설계·구현·디버깅 요청은 Engineering이 유지하고, 사용자가 도메인
형태나 최소 구현을 직접 요구할 때 Quality Engineering 구현 스킬을 선택합니다.

```text
도메인 계약에 맞춰 최소 구현하고 품질 검토
  → Engineering이 전체 개발 lifecycle과 검증 흐름을 유지
  → Quality Engineering의 domain-shaped-code 또는 simplify-code로 명시된 제약을 구현
  → Quality Engineering의 관련 review lens만 읽기 전용으로 적용
```

이 조합은 dependency가 아닙니다. Quality Engineering만 설치된 환경에서도 구현·review 스킬은
자기 범위를 독립적으로 완료하며 Engineering의 계획, TDD 또는 branch 완료 skill ID를 호출하지
않습니다. Engineering만 설치된 환경도 Quality Engineering이 있다고 가정하지 않습니다.

review skill은 사용자가 지정한 관점과 범위에만 직접 trigger됩니다. `review-quality`는 broad
quality review 요청에서 관련 lens만 선택하고, over-engineering처럼 한 관점만 지정한 요청을
가로채거나 모든 lens를 기계적으로 실행하지 않습니다. review와 audit skill은 파일을 수정하지
않습니다.

Quality Engineering은 다음 책임으로 확장하지 않습니다.

- 제품 용어집, `CONTEXT.md`, ADR과 미결 architecture decision
- 일반 debugging, TDD, 계획과 branch 완료 lifecycle
- branch, commit, ticket, push와 PR
- penetration test, repository-wide security scan과 취약점 판정
- 일반 문서 작성, 조사 방법과 출력 언어

명백한 correctness, security, data integrity, accessibility 또는 compatibility 문제는 단순성보다
우선하지만, 깊은 전문 검토가 필요하면 관련 범위를 밝히고 해당 전문 skill로 라우팅합니다.
error handling과 logging은 별도 규칙으로 강제하지 않고 오류를 소유하는 경계와 실제 운영 질문을
기준으로 함께 판단합니다.

## Product 조합

Product는 제품 문제와 기회, 사용자 근거, 제품 도메인 규칙, 검증과 PRD 변환을 담당합니다.
스킬은 작업 단계가 아니라 사용자가 직접 요청한 산출물과 현재 증거 상태를 기준으로 선택합니다.

```text
제품 아이디어를 검증 가능한 요구사항으로 발전
  → product-brainstorming으로 문제·기회·해법 후보를 확장
  → product-discovery와 evidence·domain 스킬로 필요한 제품 맥락을 구체화
  → design-product-test와 assess-product-test로 실행 전 기준과 실행 후 판정을 분리
  → 승인 경계를 통과한 내용만 to-prd로 변환
```

위 흐름은 가능한 조합 예시이며 고정된 7단계 pipeline이 아닙니다. 사용자는 제공된 인터뷰의
근거 종합, 이미 실행한 test의 판정 또는 준비된 합의의 PRD 변환부터 직접 시작할 수 있습니다.
각 Product 스킬은 자기 결과와 handoff 정보를 독립적으로 완성하며 다른 Product 스킬의 선행
실행을 필수로 가정하지 않습니다.

Product와 다른 플러그인의 경계는 다음과 같습니다.

- 외부의 여러 출처를 새로 찾고 원문을 교차 검증하는 작업은 Research가 담당하고, 제공된
  인터뷰·피드백·지표를 제품 질문에 맞게 종합하는 작업은 `synthesize-product-evidence`가
  담당합니다.
- 제품 용어·상태·규칙의 후보를 찾는 작업은 `product-domain-discovery`가 담당하고, 확인된
  계약을 code shape와 제어 흐름에 반영하는 작업은 Quality Engineering의
  `domain-shaped-code`가 담당합니다.
- 제품 문제, 결과와 요구사항은 Product가 담당하고, 기술 설계·구현·검증 lifecycle은
  Engineering이 담당합니다.
- `to-prd`는 PRD만 다루며 branch, commit, ticket과 PR은 Workflow가 담당합니다.

Product만 설치된 환경에서도 현재 대화와 제공 자료를 바탕으로 각 작업을 완료할 수 있어야
합니다. 외부 근거나 구현이 함께 요청되면 Research 또는 Engineering을 runtime에서 조합하며
manifest dependency를 추가하지 않습니다.

## Figma Workflow 조합

Figma Workflow는 Figma 제품 화면의 native 구조, interaction과 handoff 품질을 담당합니다. final
artifact가 무엇인지에 따라 Figma Design, FigJam과 draw.io의 책임을 다음처럼 구분합니다.

| 최종 artifact 또는 목적 | 담당 |
| --- | --- |
| 제품 UI, reusable component와 responsive screen | Figma Design과 `figma-workflow:figma-product-design` |
| 버튼 이동, overlay와 상태 분기를 포함한 clickable flow | Figma Design과 `figma-workflow:figma-prototype-flow` |
| 기존 Figma file·page·frame·selection의 읽기 전용 품질 감사 | `figma-workflow:figma-design-audit` |
| 협업용 초기 user journey, workshop와 sticky-note board | 공식 FigJam skill |
| AWS, network, system architecture, UML, ERD와 data flow | draw.io plugin |

Figma 제품 화면에서는 Auto Layout, component, variable와 exact asset을 native node에 유지합니다.
클릭 동선은 실제 reaction, 사람이 읽는 annotation과 named state topology를 구분하고 실제 prototype
playback으로 검증합니다. 정적 arrow나 annotation만으로 clickable interaction을 통과시키지 않습니다.

Figma canvas의 판단형 read/write는 registered official Figma MCP가 유일한 agent writer입니다. 실제
`use_figma` 호출은 먼저 `figma:figma-use`를 invoke하고 해당 tool call의 `skillNames`에 `figma-use`를
포함합니다. 화면·composed view에는 `figma:figma-generate-design`, component·library에는
`figma:figma-generate-library`, design-to-code에는 `figma:figma-design-to-code`를 current official
contract에 따라 조합합니다. prerequisite나 capability가 없으면 API를 추정하거나 우회하지 않고
`blocked`, `inconclusive` 또는 `not_run`을 보고합니다.

[Figma Workflow Companion](../../plugins/figma-workflow/figma-plugin/README.md)은 사용자가 Figma Desktop에서
직접 실행하는 수동 companion입니다. Codex writer나 agent-callable bridge가 아니며, 반복적이고 결과가
명확한 allowlisted JSON 작업만 처리합니다. mutation은 explicit node ID, expected state, same-plan preview
receipt, apply 직전 re-read와 readback을 요구합니다. official MCP 안의 bounded code는 current tool
contract가 허용하는 범위에서만 사용하고, companion의 manual operation과 섞지 않습니다.

일반적인 “user flow”가 clickable product flow, collaborative journey 또는 system logic 중 무엇인지
구분되지 않을 때만 하나의 artifact 질문을 합니다. 제품과 목적이 명시된 요청에는 불필요한 확인
질문을 추가하지 않습니다. 공통 router는 실제 반복 충돌이 확인되고 별도 결정이 승인되기 전에는
추가하지 않습니다.

## Ticket 생성과 lifecycle

Workflow는 ticket 생성, 기존 ticket의 lifecycle 변경과 PR 연동을 서로 다른 책임으로 나눕니다.

| 이벤트 | 담당 | 책임 |
| --- | --- | --- |
| ticket 초안·생성 | `workflow:to-ticket` | body, 초기 status와 생성 metadata를 확정하고 게시 결과를 검증 |
| 작업 시작·상태 변경 | `workflow:ticket-lifecycle` | canonical ticket의 현재 상태를 읽고 허용된 transition, 담당자와 native relation을 변경 |
| branch 생성 | `workflow:git-workflow` | Git branch만 관리하고 ticket mutation은 runtime에서 `ticket-lifecycle`과 조합 |
| PR 초안·게시 | `workflow:to-pr` | canonical ticket의 연결 의도와 provider 문법을 PR에 표현하고 status effect를 검증 |
| PR·merge·release event | tracker의 native integration | 구성된 workflow automation을 적용하고, Workflow skill은 직접 중복 전이하지 않음 |

### 생성 metadata를 같은 publish 흐름에서 완성한다

`to-ticket`은 tracker와 대상 공간의 실제 schema, template, 사용자 지정값과 일관된 team·project
정책을 먼저 읽습니다. 다음 값 가운데 근거가 있고 현재 interface가 지원하는 값은 title과 body를
게시하는 동일한 흐름에서 적용합니다.

- type 또는 기존 분류 label
- assignee, priority와 estimate
- project, milestone, cycle, sprint, fix version과 due date
- parent·sub-ticket hierarchy
- blocked by, blocks, related와 duplicate relation
- component와 대상 tracker의 필수·허용 custom field
- 명시되었거나 template·공간 정책으로 정해진 초기 status

모든 선택 필드를 채우는 것이 목표는 아닙니다. 사용자 지정값, 유효한 template, 명시적인 공간
정책 또는 동일한 종류의 최근 ticket에서 일관되게 확인되는 값이 없으면 assignee, priority,
estimate와 분류값을 추정하지 않습니다. ticket 생성 자체만 요청받으면 확인된 template·공간의
기본 초기 상태를 유지하며, 생성 직후 작업 시작까지 요청받았을 때에만 `ticket-lifecycle`을 이어서
선택합니다.

일부 tracker interface는 project custom field나 relation을 생성 호출과 별도 작업으로 처리합니다.
이 경우에도 하나의 publish 흐름으로 취급하여 기본 ticket을 한 번만 만들고, 반환된 ID로 남은
metadata와 relation을 적용한 뒤 원격 상태를 다시 읽습니다. 일부 단계가 실패하거나 응답이
불명확하면 ticket을 다시 만들지 않고 성공한 값, 미적용 값과 확인하지 못한 상태를 구분해
보고합니다. 구조화된 relation을 지원하지 않을 때에만 body에 의미를 보존하고 제한을 밝힙니다.

플랫폼별 차이는 다음과 같이 유지합니다.

- Linear는 team과 title이 필요합니다. status는 확인된 template·team 기본값을 유지하거나 명시되고
  지원되는 초기값만 사용하며, 나머지 property와 relation은 선택 사항입니다. 현재 team의 label,
  priority, estimate 체계와 project·milestone 관계를 확인합니다. milestone은 project가 확인된
  경우에만 사용합니다. [Linear issue 생성](https://linear.app/docs/creating-issues),
  [Linear issue relation](https://linear.app/docs/issue-relations)
- GitHub Issues는 확인된 assignee, label, milestone, project, issue type, parent, blocked-by와
  blocking을 생성 흐름에서 적용할 수 있습니다. priority와 estimate가 GitHub Project custom
  field라면 issue를 project item으로 추가한 뒤 실제 field ID와 option을 조회해 별도로 설정하며,
  project 권한을 자동으로 확대하지 않습니다. [GitHub CLI `gh issue create`](https://cli.github.com/manual/gh_issue_create)
- Jira는 project와 work type별 create-field metadata가 허용하는 field만 사용합니다. 생성 후
  status 변경은 일반 field edit이 아니라 현재 workflow가 허용하는 transition으로 처리하고,
  issue link가 별도 interface이면 생성 직후 반환 key로 연결합니다.
  [Jira Cloud issue API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)

### 작업 시작과 기존 ticket 변경을 분리한다

`ticket-lifecycle`은 기존 ticket에 대한 다음 의도를 담당합니다.

```text
start | review | ready | complete | reopen | cancel | block | unblock
```

provider, canonical ticket, 현재 status, 실제 workflow transition과 변경 가능한 field를 먼저
확인합니다. `start`는 현재 상태가 unstarted일 때만 실제 Started 계열 상태로 전이합니다. 이미
started이면 idempotent하게 유지하고, completed·canceled ticket은 명시적인 `reopen` 없이 되돌리지
않습니다. 담당자는 사용자의 지정이나 확인된 auto-assign 정책이 있을 때만 함께 설정합니다. 특정
담당자를 해제할 때에는 현재 assignee에서 검증한 대상을 보존하고, 전체 해제는 사용자가 명시한
경우에만 수행합니다. 다중 assignee에서 대상 또는 전체 해제 의도가 모호하면 변경하지 않습니다.

`block`과 `unblock`은 status 문자열보다 tracker의 native blocked-by·blocking relation을
우선합니다. 공간에 Waiting 또는 Blocked 상태 정책이 있으면 relation과 별개로 그 transition도
적용할 수 있습니다. `related`와 `duplicate`도 body 문구가 아니라 지원되는 native relation으로
관리합니다. Linear의 duplicate 처리처럼 native operation 자체에 필수 상태 효과가 포함된 경우에는
이를 별도 임의 transition으로 보지 않고 operation의 원자적 효과로 검증합니다. 사용자가 그 상태
효과를 명시적으로 금지하면 요청을 일부만 실행하지 않고 충돌을 보고합니다.

각 mutation 뒤에는 canonical ticket을 다시 읽어 status, assignee와 대상 relation의 실제 결과를
검증합니다. status·assignment·relation을 함께 바꾸는 요청은 각 작업을 적용됨, 미적용 또는 확인
불가로 구분해 보고합니다. 이미 목표 status이거나 relation이 존재·제거된 경우는 no-op으로
처리합니다. 부분 실패 뒤에는 최신 원격 상태를 기준으로 미적용 작업만 재시도하며, 권한 부족과
지원되지 않는 transition·relation을 다른 작업의 실패와 구분합니다.

`ENG-123 작업 시작해`처럼 canonical ticket과 작업 시작을 함께 지정한 요청은 해당 ticket의
`start` mutation을 포함합니다. ticket을 지정하지 않은 일반 코드 수정, branch 이름에 우연히
포함된 ID 또는 provider를 확정할 수 없는 ID만으로는 원격 ticket을 바꾸지 않습니다. ticket 작업과
branch 생성이 함께 요청되면 `ticket-lifecycle`과 `git-workflow`을 runtime에서 각각 선택하며 어느
한 스킬도 다른 스킬의 설치나 선행 실행을 필수로 가정하지 않습니다.

### PR은 연결하고 native automation을 우선한다

`to-pr`은 canonical ticket의 `complete`, `contribute`, `relate` 또는 `suppress` 의도를 provider의
정확한 PR title·body·link 문법으로 표현합니다. Linear magic word, GitHub closing keyword와 Jira
work item key는 서로 바꾸어 사용하지 않습니다. 같은 작업이 여러 tracker에 동기화되어 있으면
확인된 canonical ticket 하나에만 completion 의도를 적용합니다.

Linear와 Jira처럼 PR event 기반 status automation이 구성된 경우 Draft, PR open, review request,
ready for merge, merge와 release event는 native integration이 담당합니다. `to-pr`은 같은 status를
직접 중복 변경하지 않고 PR 게시 후 ticket을 다시 읽어 link와 실제 status effect를 확인합니다.
automation이 없거나 해당 event에 적용되지 않는다는 점, 목표 transition, 권한과 현재 상태가 모두
확인되고 사용자의 전이 의도 또는 repository·team lifecycle 정책이 있는 경우에만
`ticket-lifecycle`을 fallback으로 선택합니다. automation 적용 여부나 비동기 결과가 불명확하면
직접 전이하지 않고 `unknown`으로 보고합니다.

Draft PR 생성은 review 시작과 같지 않으며 Draft라는 이유만으로 review 상태로 직접 전이하지
않습니다. Ready 전환, review request와 merge의 상태 효과는 확인된 provider integration 또는
repository·team 정책이 정의한 매핑을 따릅니다. 배포나 release가 ticket의 완료 조건이면
merge만으로 completed 처리하지 않고 release automation이나 명시적인 완료 요청을 기다립니다. PR
없이 완료되는 investigation, 문서와 운영 ticket은 `ticket-lifecycle`이 직접 완료 상태를 처리합니다.

Linear는 PR drafted·opened·review requested·ready for merge·merged event별 status automation을
지원합니다. Jira Cloud는 연결된 source control의 branch created, pull request created와 merged
trigger를 지원합니다. GitHub Issue 자체의 state는 open·closed 중심이므로 Started·Review 같은
상태는 실제 GitHub Project의 Status field나 repository automation이 있을 때만 변경합니다.
[Linear GitHub integration](https://linear.app/docs/github),
[Jira automation trigger](https://support.atlassian.com/cloud-automation/docs/jira-automation-triggers/),
[GitHub Projects built-in automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations)

### 검증할 대표 경로

- Linear ticket 생성에서 label, priority, estimate, assignee, project, milestone과 relation을 실제
  workspace 선택지에 맞춰 적용하고 전부 재조회하는가?
- 관계 없는 단일 ticket을 생성할 때 불필요한 `client_key`를 만들지 않고, 별도 relation 단계가
  실패해도 ticket을 중복 생성하지 않는가?
- 기존 ticket 작업 시작 요청은 한 번만 Started 계열 상태로 전이하고, 일반 코드 요청은 원격
  ticket을 추정하여 변경하지 않는가?
- GitHub의 여러 assignee 중 한 명만 해제할 때 검증된 target을 보존하고 나머지를 유지하며, 전체
  해제는 명시적인 요청에서만 수행하는가?
- GitHub Project가 있을 때만 priority, estimate와 Status custom field를 실제 ID로 갱신하고,
  project 권한 부재를 issue 생성 성공으로 숨기지 않는가?
- Jira는 허용된 transition만 사용하고 branch·PR automation이 이미 수행한 전이를 중복하지 않는가?
- PR의 `complete`, `contribute`와 `relate` 의도가 merge 시 서로 다른 status effect를 유지하는가?
- integration 적용 여부나 비동기 status effect를 확인할 수 없을 때 직접 전이를 만들지 않고
  정확히 `unknown`으로 보고하며, 확인된 fallback만 적용하는가?

## PR 게시 상태

`workflow:to-pr`의 로컬 `draft` 모드는 title과 body만 준비하며 원격 PR을 만들지 않습니다.
사용자가 새 PR 생성·게시를 요청하면 `publish` 모드로 전환하지만, GitHub 상태를 지정하지 않은
경우에는 Draft PR을 기본값으로 사용합니다. Ready, non-draft 또는 즉시 review 가능한 상태를
명시한 경우에만 Ready PR을 만들거나 현재 publish 흐름에서 만든 Draft PR을 Ready로 전환합니다.
“PR을 올려 줘”라는 게시 요청 자체는 Ready 요청으로 해석하지 않습니다.

대상 repository가 Draft PR을 지원하지 않으면 상태 미지정 요청을 Ready로 대체하지 않고
중단합니다. 미디어가 있는 publish는 목표 상태와 관계없이 Draft PR에서 첨부를 검증하며,
명시적인 Ready 요청과 모든 필수 첨부 확인이 함께 충족된 경우에만 Ready로 전환합니다.

## Research 조합

Research를 직접 요청하면 Research가 조사와 근거 보고를 단독으로 완료합니다. 설계·계획·구현
중 외부의 다중 출처 근거가 결과를 좌우하면 Engineering이 전체 개발 흐름을 유지하고 Research의
결과를 다음 결정과 구현에 반영합니다.

```text
외부 근거가 필요한 설계·구현 요청
  → Engineering이 문제와 필요한 근거를 구체화
  → Research가 관련 출처를 찾고 원문을 교차 검증
  → Engineering이 조사 결과를 설계·계획·구현에 반영
```

local debugging, 단순한 repository 탐색과 하나의 공식 문서만 확인하면 충분한 조회는 Research의
기본 범위가 아닙니다. 반대로 구현을 포함하지 않는 다중 출처 조사에는 Engineering을 선행시키지
않습니다. Research만 설치된 환경에서도 조사를 완료할 수 있고, Engineering만 설치된 환경에서도
외부 Research의 존재를 가정하지 않고 개발 흐름을 수행합니다.

Exa와 Perplexity 같은 전문 provider는 선택 사항입니다. 사용할 수 있는 provider가 없으면 generic
web·browser·local 기능으로 조사하고, provider plugin이나 도구를 자동으로 설치·연결·인증하지
않습니다. Fluent Languages 같은 문체 스킬은 조사 방법이나 개발 lifecycle을 소유하지 않으며,
요청한 출력 언어에 따라 Research 또는 Engineering과 독립적으로 함께 선택할 수 있습니다.

## Engineering 흐름

```text
요청
  → spike / bounded / architectural 분류와 stable task ID 고정
  → 매 Fast Path entry에서 persistent latch 확인
      → disqualified: classifier/predicate/execution을 건너뛰고 nearest normal workflow
      → unclassified: controller search 1회 → fresh classifier search 1회
          → eligible: state에 exact candidate revision + digest 기록 → plan 없는 Local/Mechanical Fast Path
          → escalate/inconclusive/blocked/unavailable/false/unknown: disqualified latch → nearest normal workflow
  → Fast Path 실행 중 hidden complexity
      → disqualified latch → systematic-debugging / writing-plans / brainstorming (Fast Path 재진입 없음)
  → plan 없는 Fast Path: 결정론적 검증 → 목적 정렬 기록
  → plan 없는 일반 bounded: 짧은 설계 승인 → plan 필요 여부 판정
  → architectural 또는 plan 필요 bounded:
      설계 승인과 필요한 design-document gate
      → 의사코드로 전체 흐름 정의
      → 파일·task·dependency별 구현 계획과 검증 이유 → plan-readiness gate
      → worktree 확인 또는 생성 → 구현 → task gate와 targeted fix
      → final deterministic verification → 일반 whole-change review
      → 목표·요구사항·설계·plan·전체 diff·검증을 하나의 immutable bundle로 고정
      → fresh-context red-team completion gate
  → plan 없는 일반 bounded:
      승인된 짧은 설계 → 구현 → 변경에 비례한 결정론적 final gate
  → diff와 gate 상태 보고 → 명시적인 커밋 승인 → commit
```

`using-git-worktrees` 파일은 기존 linked worktree를 재사용하고 일반 checkout에서 필요할 때
worktree를 만드는 원본 정책을 유지합니다. 다만 스킬 안의 commit 문구를 포함한 모든 Git
변경에는 `using-engineering-skills`의 전역 승인 게이트를 먼저 적용합니다.

## Engineering quality gate

Engineering의 공통 [quality gate 계약](../../plugins/engineering/skills/using-engineering-skills/references/quality-gates.md)은
gate ID, artifact와 exact revision, 필수 검사, evidence, finding, status, return target,
attempt/cap과 decision owner를 기록합니다. `passed`, `failed`, `blocked`, `inconclusive`,
`not_run`, `not_applicable`, `accepted_risk`를 구분하며 artifact가 바뀌면 이전 pass는 stale입니다.
quality gate는 문서 작성, 구현, commit, push, PR, merge, deploy 또는 publish 권한을 부여하지
않습니다.

각 stage가 자기 artifact의 gate와 return target을 소유합니다. 중앙 gate router나 전체 workflow의
재귀 호출은 사용하지 않습니다.

| Gate | 기본 evidence | 실패 return target |
| --- | --- | --- |
| design document | self-review, link/path/schema check, architectural/high-risk일 때 independent review | 영향받은 문서 section 또는 design decision |
| implementation plan | 의사코드 선행 여부, flow-task-path-dependency-verification 추적성, 검증 선택 이유, cross-component·long-running·high-risk일 때 independent review | 영향받은 의사코드·plan task 또는 `brainstorming` |
| inline task | task별 test·build·parser·loader·consuming command | task implementation 또는 `systematic-debugging` |
| subagent task review | task brief와 정확한 BASE..HEAD, spec·quality verdict | scoped fix loop; plan/design defect면 해당 소유 stage |
| whole change ordinary review | plan-backed 전체 diff, 요구사항 mapping, final deterministic verification와 독립 reviewer | 가장 가까운 implementation, plan 또는 design stage |
| red-team completion | 모든 plan-backed 작업의 목표·요구사항·설계·plan·전체 diff·검증을 포함한 content-digested bundle과 fresh-context reviewer | 사용자 재승인 또는 가장 가까운 design, plan, implementation, verification stage |
| plan 없는 direct completion | Fast Path 또는 승인된 bounded 구현의 비례한 결정론적 검증과 목적 정렬 | 영향받은 구현 또는 일반 workflow escalation |

deterministic oracle를 inferential review보다 먼저 실행합니다. retry는 artifact, hypothesis,
implementation, evidence, context, evaluator 또는 capability 가운데 하나 이상이 바뀌어야 하며
stage별 유한한 상한을 가집니다. 상한에 남은 실제 필수 finding은 `passed`나 `complete`로
자동 전환하지 않습니다. 사용자 또는 확인된 human decision-maker만 exact revision의 위험을
`accepted_risk`로 수락할 수 있고, 이 상태는 `passed`와 구분해 보고합니다.

이 내부 계약은 Quality Engineering 플러그인을 필요로 하지 않습니다. 특정 quality lens를
명시적으로 요청하면 runtime에서 Quality Engineering을 조합할 수 있지만, Engineering gate가
그 플러그인의 설치나 skill ID를 전제로 하지는 않습니다.

## 문서 라우팅

`brainstorming`은 날짜 기반 spec 파일을 자동 생성하지 않습니다. 먼저
[`docs/README.md`](../README.md)의 기준으로 기존 문서를 조사하고, 변경 없음·기존 문서
갱신·새 문서 생성·결정 대체 중 하나를 제안합니다. 새 문서나 큰 재구성은 경로와 목적을
사용자가 검토한 뒤 작성합니다.

`writing-plans`는 구현 계획을 기본적으로 대화에 작성합니다. 실행을 위해 파일이 필요하면
Git에서 제외된 `.engineering/plans/<topic>.md`를 사용합니다. 저장소의 기존 이슈·티켓이나
사용자가 지정한 위치가 있으면 그 위치를 우선합니다.
계획이 필요한 작업에서는 구현 세부사항과 테스트 방식을 정하기 전에 언어 중립적인 의사코드로
입출력, 처리 순서, 필요한 상태 변화·분기·반복·오류·경계와 책임을 정의합니다. 각 flow ID를
파일, task, dependency와 검증에 연결한 뒤 검증 방법과 이유를 선택합니다. 구현이 승인된
요구사항·설계·관찰 가능한 계약을 바꾸면 `brainstorming`으로 돌아가 사용자의 명시적인 재승인을
받습니다. 승인된 설계 안의 흐름 변경이거나 재승인을 받은 변경은 의사코드를 먼저 갱신하고,
영향받은 완료 task를 reopened하여 plan과 구현·검증·review gate를 새 리비전에 다시 맞춥니다.
별도 구현 계획이 필요 없는 단순 작업에는 긴 의사코드를 요구하지 않습니다.
실행 artifact는 현재 플러그인 ID와 같은 `.engineering/` 경로에 둡니다.

## 커밋 라우팅

계획에는 `git commit`을 실행 단계로 자동 삽입하지 않습니다. inline 실행은 구현과 검증 후
diff를 보고하고 커밋 결정을 받습니다. task별 commit을 전제로 하는
`subagent-driven-development`는 현재 작업에서 사용자가 task commit을 명시적으로 승인한
경우에만 시작합니다. 플랫폼 참고 문서, worktree 상태와 다른 스킬의 commit 지시는 이
승인 게이트를 우회할 수 없습니다.

## 테스트 라우팅

| 변경 | 기본 검증 |
| --- | --- |
| 기능 추가, 버그 수정, 로직·상태·오류 처리, 동작에 민감한 리팩터링 | 동작과 회귀 위험 및 자동화 실익을 판단해 TDD를 선택하면 RED–GREEN–REFACTOR, 아니면 이유가 있는 가장 강한 비례 검증 |
| 문서 | 링크, 경로, 예제와 문서 간 일관성 확인 |
| 스킬 지침 | frontmatter와 경로 검증, 위험할 때 실제 사용 시나리오 평가 |
| manifest와 metadata | 문법, 경로와 실제 Codex 로딩 확인 |
| 단순 설정 | 설정을 소비하는 최소 실제 명령으로 확인 |

외부 스킬은 관련성이 있다는 이유만으로 모두 자동 적용하지 않습니다. Quality Engineering의
review·audit, grilling, 아키텍처 결정과 제품 탐색 스킬은 사용자가 요청하거나 현재 결과의
불확실성과 위험을 실제로 줄일 때만 선택합니다.

## 라우팅 평가

경계 변경은 [repository-level routing cases](../../evals/skill-routing/cases.json)의 positive,
near-miss, 조합, 단독 설치와 orthogonal 문체 사례로 검토합니다. Figma Workflow는 별도의
[tool routing cases](../../evals/figma-workflow-routing/cases.json)와
[native quality contract cases](../../evals/figma-quality-contract/cases.json),
[interaction contract cases](../../evals/figma-interaction-contract/cases.json)로 Figma, FigJam과
draw.io 경계 및 결과 품질을 검토합니다. 이 파일들은 기대 동작을 정의하며 JSON 파싱만
통과했다고 실제 모델 선택이나 canvas 동작이 검증된 것은 아닙니다. 모델 기반 평가는 격리된
환경과 명시된 실행 범위에서 수행하고 `pass`, `fail`, `blocked`, `inconclusive`, `not_run`을
구분합니다.
