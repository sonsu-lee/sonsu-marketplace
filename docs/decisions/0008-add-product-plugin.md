# 0008 Add an Independent Product Plugin

- Status: Accepted
- Date: 2026-09-02
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-02 현재 대화에서 독립 `Product` 플러그인과 제안된 7개 스킬 구조의 구현과 PR 게시를 명시적으로 승인했습니다.

## Context

기존 standalone `product-discovery`와 `to-prd`는 제품 맥락의 탐색과 승인된 제품 합의의 문서화를
각각 담당합니다. 그러나 초기 아이디어 발산, 여러 제품 근거의 traceable synthesis, 제품
도메인 후보 발견, 실행 전 검증 설계와 실행 후 판정은 서로 다른 입력, 성공 기준과 실패 형태를
가집니다. 이 책임을 `product-discovery` 하나에 추가하면 description의 직접 trigger가 넓어지고,
탐색 후보와 근거, 계획과 결과, 제안과 승인이 한 작업 상태에 섞일 수 있습니다.

OpenAI의 skill authoring guidance는 trigger, 입력 또는 성공 기준이 다른 workflow를 분리하고
서로 관련된 스킬을 하나의 plugin으로 배포하는 방식을 권고합니다. Anthropic의 Product
Management plugin도 research synthesis, specification, roadmap와 metrics를 여러 workflow로
구분합니다. 제품 문제를 가설과 test로 연결하는 연구는 실행 전 기준과 결과 기반 판단을
분리하는 구조를 지지하지만, 하나의 고정된 제품 방법이나 customer interview·MVP를 모든
상황에 적용할 근거는 제공하지 않습니다.

관련 근거는 다음 원문에서 검토했습니다.

- [OpenAI Skills 작성 가이드](https://developers.openai.com/plugins/build/skills)
- [Claude Product Management plugin](https://claude.com/plugins/product-management)
- [A scientific approach to entrepreneurial decision-making](https://doi.org/10.1002/smj.3580)
- [The RIGHT model for Continuous Experimentation](https://doi.org/10.1016/j.jss.2016.03.034)
- [Sample Size in Qualitative Interview Studies](https://doi.org/10.1177/1049732315617444)

## Decision

제품 탐색과 검증 workflow를 `Product`라는 독립 플러그인으로 배포합니다. 플러그인 ID와
디렉터리는 `product`와 `plugins/product/`를 사용하고 다음 스킬을 포함합니다.

- `product-brainstorming`: 제품 문제, 기회, 가치 제안과 해법 후보를 확장합니다.
- `product-discovery`: 사용자, 문제, 기대 결과, 범위와 미해결 결정을 구체화합니다.
- `synthesize-product-evidence`: 제품 자료를 출처에 연결된 theme, 반례와 불확실성으로
  종합합니다.
- `product-domain-discovery`: 제품의 용어, 행위자, 상태, 사건, 규칙과 예외를 후보 모델로
  정리합니다.
- `design-product-test`: 가설, 반증 조건, 방법, 계측과 판정 기준을 실행 전에 정합니다.
- `assess-product-test`: 실제 실행과 관찰을 사전 기준에 대조하여 결과를 판정합니다.
- `to-prd`: 승인된 제품 결정만 추적 가능한 PRD로 변환합니다.

이 스킬들을 고정된 7단계 pipeline으로 만들지 않습니다. 요청의 직접 목적에 따라 어느
스킬에서든 시작할 수 있고, 검증 결과에 따라 탐색으로 돌아갈 수 있습니다. Product는 다른
플러그인의 설치나 특정 skill ID를 필수로 가정하지 않습니다. 여러 외부 출처가 필요하면
Research, 승인된 요구사항의 구현이 필요하면 Engineering과 runtime에서 조합합니다.

제품 도메인 탐색 결과는 정본이나 코드 설계가 아닌 후보로 유지합니다. 제품 test의 설계와
판정을 분리하여 결과를 본 뒤 성공 기준을 소급해서 변경하는 일을 방지합니다. PRD는 현재
리비전에 대해 확인된 승인 범위를 넘어 누락된 결정을 만들지 않습니다.

## Alternatives Considered

- 기존 `product-discovery`에 모든 책임을 추가: 설치 항목은 적지만 서로 다른 trigger와 성공
  기준이 한 스킬에 섞이고, 열린 탐색에서 PRD까지 고정 순서로 진행할 위험이 있습니다.
- 각 스킬을 standalone으로 유지: 개별 설치는 가능하지만 관련 workflow의 version, 문서와
  discovery 경계를 함께 관리하기 어렵습니다.
- Engineering에 포함: 구현 전 설계와 연결되지만 제품 근거·수요·도메인 규칙의 탐색을 개발
  lifecycle에 종속시킵니다.
- Research에 포함: 근거 종합과 일부 겹치지만 제품 결정·검증·PRD 책임이 외부 다중 출처 조사와
  다른 업데이트 경계를 가집니다.
- JTBD, Opportunity Solution Tree, EventStorming과 scoring framework를 별도 스킬로 추가:
  현재 핵심 작업보다 특정 방법론을 먼저 선택하게 만들 수 있어 이번 범위에는 포함하지 않습니다.

## Consequences

Product는 단독으로 설치해 제품 탐색부터 PRD 변환까지 필요한 스킬을 직접 선택할 수 있습니다.
열린 brainstorming에는 높은 자유도를 주고, 근거 종합, test 판정과 PRD 승인에는 추적 가능한
입력과 엄격한 상태 경계를 적용할 수 있습니다.

스킬 수가 늘어나므로 description이 겹치면 잘못된 동시 선택과 절차 비용이 생길 수 있습니다.
직접 trigger, near-miss, 단독 설치와 Research·Engineering 조합을 repository-level routing
fixture와 실제 격리 실행으로 계속 확인해야 합니다. 기존 standalone `product-discovery`와
`to-prd`를 함께 노출하면 이름이 같은 스킬이 경쟁하므로 플러그인판 검증 후 discovery 경로에서
기존 복사본을 제외해야 합니다.

## Revisit When

같은 요청에서 Product 스킬이 반복적으로 경쟁하거나 고정 pipeline처럼 선택될 때, Product와
Research·Engineering의 경계가 실제 사용에서 구분되지 않을 때, 특정 방법론이 반복적으로
필요하고 독립 trigger와 성공 기준을 가질 때, 또는 Codex가 공식 plugin dependency나 workflow
composition 계약을 제공할 때 재검토합니다.
