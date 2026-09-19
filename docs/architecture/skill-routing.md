# 스킬 라우팅

## 컴팩션과 작업 연속성

작업 연속성을 제공하는 플러그인은 각각 자기 namespace의 `task-continuity`를 제공합니다. 현재 메인 controller가
여러 단계의 작업을 소유하거나 외부 쓰기 결과를 이어서 확인해야 할 때 기존 작업 스킬에서
같은 플러그인의 연속성 스킬을 사용합니다. 다른 플러그인의 연속성 스킬을 필수 호출하지 않습니다.
짧은 단발 산출물과 다른 작업의 출력 문체만 담당하는 Fluent Languages에는 별도 기록이 없습니다.

`SessionStart(compact|resume)` hook은 현재 session/worktree의 활성 checkpoint가 있을 때만
자기 스킬과 기록 경로를 전달합니다. 모델은 최신 사용자 지시·원장·실제 대상을 대조한 뒤 현재
작업 스킬로 돌아갑니다. hook은 중앙 router나 새 권한·정본이 아니며 종료 기록과 다른 session을
자동 선택하지 않습니다. fresh reviewer와 subagent는 controller의 checkpoint를 자동 상속하지 않습니다.
저장·예산·권한·외부 작업 중복 방지 규칙은 [작업 연속성 계약](../reference/task-continuity.md)에 있습니다.

Engineering의 선택적 [완료 근거 관찰 도구](../../plugins/engineering/skills/using-engineering-skills/references/evidence-gates.md)는
등록한 계획 기반 task의 검사·리뷰 근거를 연결합니다. `Stop`은 현재 근거의 누락·stale 상태만
관찰하며, 스킬 라우팅·실행 권한·다른 플러그인의 상태를 결정하지 않습니다.

- Status: Current
- Last reviewed: 2026-09-15

## 자동 트리거와 직접 호출

자연어 요청은 description의 목적·대상·산출물·제외 조건에 따라 선택하고 명시적인 이름 지정은
우선합니다. 사용자가 스킬 이름을 알아야만 실행되는 방식으로 만들지 않습니다. 선택 자체는
수정·게시 권한이 아니며 실제 요청과 기존 승인을 따릅니다. 별도의 만능 router는 없습니다.
혼합 요청은 주 작업 담당 하나가 명세·결과를 소유하고 필요한 전문 지침을 조합합니다.

## 플러그인 경계

Engineering, Workflow, Research, Prompting, Product, Interface Design, Figma Workflow, Operations UI, Design Patterns, Memory Manager, Writing과 Fluent Languages는
각각 단독으로 설치하고 사용할 수 있는 독립 플러그인입니다. 한 플러그인이 다른 플러그인을
import하거나 설치·선행 실행·특정 skill ID를 전제로 하지 않습니다. 여러 영역을 포함한 요청은
Codex가 현재 설치된 스킬의 description과 요청의 직접 목적을 바탕으로 필요한 스킬을 순서대로
선택합니다.

| 직접 목적 | 담당 |
| --- | --- |
| 구현, 디버깅, 계획 실행과 개발 방법론 | `engineering:*` |
| 확인된 계약과 trust boundary를 코드 형태로 직접 반영 | `engineering:domain-shaped-code` |
| 명시적으로 요청한 최소 구현, 삭제 우선과 YAGNI | `engineering:simplify-code` |
| diff·commit·branch의 over-engineering 검토 | `engineering:review-overengineering` |
| repository 또는 큰 경로의 over-engineering audit | `engineering:audit-overengineering` |
| reader load와 유지보수성 검토 | `engineering:review-maintainability` |
| 도달 가능한 실패 경로 검토 | `engineering:review-failure-modes` |
| error ownership, logging과 운용 가능성 검토 | `engineering:review-operability` |
| 코드·diff의 일반 직접 리뷰 또는 여러 품질 관점의 리뷰 | `engineering:review-quality` (Luna xhigh 5개 기본) |
| Engineering 절차의 검토·명시적 독립 리뷰 | `engineering:requesting-code-review` 워크플로우 분기 |
| branch, staging, commit, 일반 push와 Git 변경 검토 | `workflow:git-workflow` |
| ticket·issue·backlog 접수·초안·게시 또는 기존 제목·본문 보강 | `workflow:to-ticket` |
| 기존 ticket의 작업 시작·review·완료 상태, 담당자와 native relation 변경 | `workflow:ticket-lifecycle` |
| PR 상태·CI·리뷰·미해결 대화 조회 | `workflow:inspect-prs` |
| 지정 PR의 충돌·리뷰 지적·CI 실패 처리 | `workflow:repair-pr` |
| 독립된 PR 심층·다중 리뷰 또는 명시적 호출 | `engineering:review-pr` |
| 일반 웹·앱의 새 화면·흐름 설계 | `interface-design:design-interface` |
| 일반 웹·앱의 기존 화면 재설계 | `interface-design:redesign-interface` |
| 현재 branch의 새 GitHub PR 초안 또는 게시 | `workflow:to-pr` |
| 반복 문제와 설계 forces에 맞는 named pattern 선택 | `design-patterns:select-design-patterns` |
| 명시적으로 요청한 기존 pattern 적용·오용의 읽기 전용 검토 | `design-patterns:review-pattern-usage` |
| 명시적 호출에 따른 Codex 메모리 점검과 정리 | `memory-manager:memory-manager` |
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
| 신규 운영형 B2B·admin·back-office 화면의 제안·Figma·구현 | `operations-ui:design-operations-ui` |
| 기존 운영 화면의 동작을 보존하거나 명시적으로 변경하는 재설계 | `operations-ui:redesign-operations-ui` |
| 기존 운영 화면과 증거의 읽기 전용 품질 감사 | `operations-ui:audit-operations-ui` |
| 명시적으로 요청된 Figma 운영 화면을 Design Decision Contract와 구현 handoff에 연결 | `operations-ui:figma-operations-flow` |

Memory Manager는 Codex의 `policy.allow_implicit_invocation: false`로 명시적 호출만 허용합니다.
`$memory-manager`를 직접 요청할 때 실행하며 일반 작업에서 자동 선택하지 않습니다.
점검 요청은 읽기 전용이고 정리 요청은 대상 호스트가 허용하는 직접 편집 또는 수정 노트
방식으로 수행합니다. 수정 노트 생성과 원본 메모리 반영은 별도 결과로 보고합니다.

Operations UI는 WMS나 배송처럼 특정 산업명이 아니라 상태 판단, 반복 작업, 권한과 위험한
행동, 고밀도 데이터가 중심인 화면에 적용합니다. marketing·editorial·brand page는 대상이
아닙니다. Figma 자체 화면·component·prototype 생성과 수정은 Figma Workflow가 담당하며,
Operations UI의 Figma skill은 사용자가 명시했을 때 업무 명세를 native 산출물에 연결합니다.
코드 구현도 요청한 경우에만 implementation 범위의 Design Decision Contract와 DQ7 브라우저 증거까지 이어갑니다.
일반 UI의 과업·플랫폼·산출물 구조는 [Interface Design](interface-design.md)을 참고하세요.
PR URL만으로 심층 리뷰를 시작하지 않고, 일반 리뷰와 명시적인 심층·다중 리뷰를 구분합니다.
리뷰 의도는 요청과 기존 문맥에서 확인하며, 문맥 없는 URL 단독 입력에 리뷰·게시를 추가하지 않습니다.
두 PR 리뷰 경로 모두 리뷰어별 별도 세션·워크트리에서 병렬 검토한 뒤 원인별로 중복을 제거해
해당 PR에 `COMMENT` 리뷰를 게시합니다. 로컬 전용·게시 금지 요청은 우선합니다.
[PR 실행·게시 계약](../../plugins/engineering/references/pr-review-execution.md)이 SHA 고정,
Codex 일시 오류 재시도, 기존 댓글 중복과 게시 결과 재조회를 소유합니다.

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

## Engineering 실행과 모델 선택

일반 리뷰의 진입점은 Engineering 안에 통합됐습니다. 일반 리뷰는 Luna xhigh 5개의 같은 고정
입력·같은 기준, focused 리뷰는 1개가 기본입니다. 직접 리뷰 요청은 전체 개발 계획·소스 수정으로
확장하지 않습니다. root가 작업자 할당을 소유하고 worker는 추가 할당을 root로 요청합니다.

정확한 역할 모델·추론 수준은 [공유 프로필](../../plugins/engineering/references/model-profiles.md),
실행은 [공통 수명주기](../../plugins/engineering/skills/executing-plans/SKILL.md),
현재 근거와 진행 조건은 [관리형 게이트](../../plugins/engineering/skills/using-engineering-skills/references/evidence-gates.md)를
따릅니다. 이 링크는 저장소 문서의 탐색이며 전문 플러그인이 Engineering 설치를 요구하는 계약이 아닙니다.

기계적 작업은 결정론적 검사, 동작 변경은 independent, 고위험 경계는 별도 red-team을 선택합니다.
계획 파일 존재·재개·고정 탐색 횟수로 위험을 결정하지 않습니다. 직접/위임은 같은 절차이고
파일 계획·커밋 승인은 위임의 선행 조건이 아닙니다. 모델보다 실제 도구·환경 가용성을 먼저
확인하며 사용자 권한과 gate 통과를 구분합니다.

공통 구성은 Writing, 언어 표현은 Fluent, 개발 단계와 코드 품질은 Engineering이 소유합니다.
공유 원본에서 필요한 패키지 참조만 생성해 단독 설치를 유지합니다.

## Writing·Fluent·Workflow 조합

Writing은 독자·목적·편집 범위에 따라 내용을 선별하고 문서 위치와 문장·문단 구성을 정합니다.
Fluent는 요청된 언어의 어순·표현·어조를 다듬고, Workflow는 티켓·PR 양식과 필수 항목,
사실·검증 근거 확인, 연결 문법·게시·재조회를 담당합니다. 각 플러그인은 단독으로 사용할 수 있습니다.

함께 사용할 때는 현재 제공되는 지침을 같은 초안에 한 번씩 적용합니다. 독자·목적·선별한 사실,
출력 언어·편집 범위·정해진 구성을 전달하고, 영속 문서는 이미 정한 목적·경로·갱신 범위도 이어받습니다.
Fluent는 구성 단계에서 제외한 참고 내용을 다시 추가하지 않습니다. Workflow가 확인한 양식과
필수 정보는 Writing·Fluent가 유지하며, 표현 개선이 양식 확인이나 게시 조건을 대신하지 않습니다.

공통 작성 규칙의 정본은 Writing, 언어별 표현과 독립적인 보존 기준은 Fluent, 티켓·PR 양식과
운영 지침은 Workflow에 있습니다. Fluent 내부 생성기는 공통 원본을 세 언어 스킬에 반영하지만
Writing과 Workflow 사이에서 지침을 생성·복사하는 단계는 없습니다. 상세 조합 계약은
[Workflow의 작성 지침 함께 적용하기](../../plugins/workflow/references/writing-composition.md)를 참고합니다.

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

## 코드 품질과 리뷰

일반 리뷰, 도메인 타입·상태, 단순화, 유지보수·실패·운영성은 Engineering 내부의 전문 스킬입니다.
일반 리뷰는 `review-quality`, 특정 관점은 해당 focused 스킬, 개발 단계·PR 이외의 독립 실행은
`requesting-code-review`, 독립 PR 심층·다중 리뷰는 `review-pr`가 맡습니다.
판단 기준은 패키지의 공통 references를 재사용합니다.

root는 일반 리뷰에 같은 고정 입력·기준을 받은 Luna xhigh 5개를 할당합니다. 각 지적을 실제
계약·도달 경로·영향으로 검증하고 중복 원인을 합칩니다. 다수결로 판정하지 않습니다. 리뷰 전용
요청은 구현 계획·DAG·소스 수정을 요구하지 않으며 쓰기 금지 시 inline 고정 입력을 사용합니다.
기본 Codex `/review`나 GitHub 자동 리뷰의 hook을 설치하는 기능은 별도 제공하지 않습니다.

도메인 타입은 확인된 규칙으로 불가능한 상태를 제외하고, 실제 외부·가변 경계는 검증합니다.
이미 보장한 내부 경로에 중복 guard를 추가하거나 확인되지 않은 미래 요구의 fallback·추상화를
만들지 않습니다. 전문 보안 감사·제품 규칙 발견·Git 전달·조사·언어 정책은 해당 책임에 남깁니다.

## Design Patterns 조합

Design Patterns는 pattern catalog 자체보다 현재 문제의 반복성, forces, baseline 한계와 필요한
guarantee를 먼저 판단합니다. 일반 기능 구현이나 사소한 리팩터링을 가로채지 않으며, framework나
직접 해법이 충분하면 `no-pattern`을 정상 결과로 반환합니다.

```text
구현 중 pattern 판단이 실제로 필요한 경우
  → Design Patterns가 pattern 필요 여부와 최소 implementation shape를 결정
  → Engineering이 승인된 선택을 전체 구현·TDD·검증 lifecycle에 반영
  → 명시적인 pattern review 요청이면 review-pattern-usage가 수정 없이 guarantee를 검토
```

이 조합은 runtime 책임 분담이며 manifest dependency가 아닙니다. Design Patterns만 설치된 환경에서도
선택과 읽기 전용 검토를 완성하고 Engineering의 skill ID나 계획 절차를 호출하지 않습니다.
Engineering도 Design Patterns가 없으면 일반 설계·구현을 독립적으로 수행합니다. Engineering의 품질 스킬은
broad code shape와 실패·운용 문제를 검토하고, Design Patterns review는 named pattern이 약속한
guarantee, cost와 scope에만 집중합니다.

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
  계약을 code shape와 제어 흐름에 반영하는 작업은 Engineering의
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

## Ticket 작성·수정과 lifecycle

Workflow는 ticket 접수·작성·내용 수정, 기존 ticket의 lifecycle 변경과 PR 연동을 서로 다른 책임으로 나눕니다.

| 이벤트 | 담당 | 책임 |
| --- | --- | --- |
| ticket 접수·초안·생성 | `workflow:to-ticket` | 적용 양식으로 제목·본문과 생성 필드를 준비하고 허가된 게시·첨부 결과를 검증 |
| 기존 title·body 보강 | `workflow:to-ticket` | canonical 원문을 읽고 요청한 내용만 수정·재조회; 기존 결정·기록과 요청 밖 field 보존 |
| 작업 시작·상태 변경 | `workflow:ticket-lifecycle` | canonical ticket의 현재 상태를 읽고 허용된 transition, 담당자와 native relation을 변경 |
| branch 생성 | `workflow:git-workflow` | Git branch만 관리하고 ticket mutation은 runtime에서 `ticket-lifecycle`과 조합 |
| PR 초안·게시 | `workflow:to-pr` | canonical ticket의 연결 의도와 provider 문법을 PR에 표현하고 status effect를 검증 |
| PR·merge·release event | tracker의 native integration | 구성된 workflow automation을 적용하고, Workflow skill은 직접 중복 전이하지 않음 |

### 작업 전달과 내용 수정을 담당한다

`to-ticket`은 외부 논의의 핵심 결론과 작업에 필요한 맥락을 본문에 담습니다.
[양식 선택 기준](../../plugins/workflow/skills/to-ticket/references/ticket-selection.md)에 따라
사용자·대상 공간의 양식을 우선하고, 없으면 일반 작업·버그·조사 작업 양식을 사용합니다.
이 구분은 본문 작성 방식이며 tracker의 type·label·status가 아닙니다. 항목·순서·필수 여부는
각 템플릿, 내용과 언어는 [작성 기준](../../plugins/workflow/skills/to-ticket/references/ticket-quality-bar.md)이 담당합니다.

첨부는 [미디어 규칙](../../plugins/workflow/skills/to-ticket/references/media-attachments.md)과
프로바이더 문서로 처리합니다. 기존 본문의 부분 수정·동시 변경 보존·결과 재조회는
[`to-ticket`](../../plugins/workflow/skills/to-ticket/SKILL.md)의 책임이며, 본문 수정 권한을
상태·담당자·관계 변경으로 확대하지 않습니다.

내용 반영 후 시작처럼 후속 lifecycle이 수정 성공에 의존하면 필요한 content field 전체의
`applied` 또는 검증된 `no-op`을 확인한 뒤 `ticket-lifecycle`에 인계합니다. 부분 성공·`unknown`이면
의존하는 후속 변경을 보류합니다. 본문 성공과 무관하게 수행하라는 명시적 요청은 현재 상태와
권한을 새로 확인해 처리합니다.

제품·기술 의사결정은 Product·Engineering의 책임이며 필수 의존성이 아닙니다. 출력 언어의
Fluent Languages 스킬이 있으면 함께 적용하되 설치를 가정하거나 자동 설치하지 않습니다.

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

Linear 티켓의 새 branch에는 ID를 자동으로 넣지 않습니다. repository의 ID 관례나 integration의 추천
branch도 예외가 아니며, 사용자가 정확한 이름이나 ID 포함을 직접 지정했을 때만 따릅니다. 기존 branch를
자동 rename하지 않고 PR metadata를 연결 채널로 사용합니다.

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

- 미승인 기능 요청·원인 미상 버그를 접수하고, 실행 준비와 실제 tracker status를 구분하는가?
- 기존 내용 수정에서 요청 밖 기록·형식과 동시 변경을 보존하고 불명확한 쓰기를 반복하지 않는가?
- 내용 수정과 lifecycle을 함께 요청했을 때 선행 내용의 실패·불명확·부분 성공은 의존 상태 변경을 막고,
  검증된 `no-op`·timeout 후 실제 적용 확인과 명시적으로 독립된 요청은 구분하는가?
- 팀 양식·부모 전체 완료 조건·Fluent 미설치 경계를 보존하는가?

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

## 개발·문서·검증 경계

Writing은 영속 문서 작업에서 이후에도 찾아볼 내용인지 판단하고, 해당 주제를 담당하는 기존
문서를 우선 갱신합니다. 독립된 읽기 목적이 있고 기존 문서에 적합한 자리가 없을 때 새 문서를
만듭니다. README는 주요 이해·첫 사용·중요한 제약·탐색 경로에 영향이 있을 때 갱신하며,
일회성 작업·검사 기록만 있다면 작업 보고에 남깁니다. 문서 배치의 판단은
[Writing](../../plugins/writing/skills/writing/SKILL.md)이, 이 저장소의 구체적인 분류·경로는
[`docs/README.md`](../README.md)가 설명합니다.

구현 요청은 Engineering에서 범위·위험·의존성·검사를 정하고 실행합니다. 확인된 승인 안의
내부 선택은 진행하며 새 목표·미결정 제품 규칙에 의존하는 작업만 보류합니다. 문서 생성은
승인된 작업에 필요한 만큼 수행하고 형식적인 추가 승인이나 날짜 기반 명세를 요구하지 않습니다.
계획은 대화가 기본이며 큰 brief의 임시 파일은 선택적입니다.

의미 있는 동작·결함은 재현/회귀 테스트로 보호하고 문서·메타데이터는 파서·경로·실제 loader로
확인합니다. 관련 필수 검사가 통과하면 새 변경·실패·미해결 우려가 있을 때만 검사를 확대합니다.
Git·외부 전달은 [공유 권한](../../plugins/workflow/references/delivery-authority.md)을 따릅니다.

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
