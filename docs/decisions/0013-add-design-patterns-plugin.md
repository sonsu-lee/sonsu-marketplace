# 0013 Add an Independent Design Patterns Plugin

- Status: Accepted
- Date: 2026-09-08
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 현재 대화에서 전체 pattern 조사 결과를 개발 시 선택 가능한 marketplace plugin으로 만드는 설계를 승인하고 Draft PR 게시를 요청했습니다.

## Context

소프트웨어 pattern은 GoF 23개처럼 닫힌 단일 목록이 아닙니다. object design, architecture, DDD,
enterprise application, integration, microservices, cloud, distributed systems, concurrency, workflow,
testing과 security catalog가 서로 다른 scope와 같은 이름을 사용합니다. 이름을 한 목록으로 합치면
`Repository`, `Adapter`, `Saga`, `Idempotent Receiver`처럼 intent와 guarantee가 다른 항목을 혼동합니다.

반대로 모든 구현 요청에 pattern catalog를 적용하면 직접 함수, 언어 idiom과 framework 기능으로
충분한 문제에도 불필요한 class와 abstraction을 만들 수 있습니다. catalog의 이름만 존재하는 것과
현재 context에서 선택할 수 있을 만큼 problem, forces, cost와 verification이 정리된 상태도 구분해야
합니다.

## Decision

1. `design-patterns`를 Engineering과 Quality Engineering에서 분리된 독립 플러그인으로 추가합니다.
   manifest dependency나 공통 router를 추가하지 않고 runtime이 요청 목적에 따라 조합합니다.
2. `select-design-patterns`는 실제 반복 문제, forces, baseline 한계, 필요한 guarantee, 비용 수용과
   검증 방법이 확인될 때만 named pattern을 선택합니다. 직접 해법이 충분한 `no-pattern`과 근거가
   부족한 `insufficient-evidence`를 동등한 정상 결과로 둡니다.
3. `review-pattern-usage`는 명시적으로 호출하는 읽기 전용 skill입니다. 기존 pattern이 약속한
   guarantee, scope와 cost를 실제 artifact가 지키는지만 검토하고 일반 code review를 대체하지 않습니다.
4. 12개 원천 family의 named entry를 family-prefixed ID로 보관합니다. 2026-09-08 snapshot은 553개이며
   source 설명·코드·diagram을 복사하지 않습니다. 같은 이름의 다른 scope는 relation으로 연결합니다.
5. maturity는 `indexed`, `normalized`, `decision-ready`, `contextual`, `superseded`로 구분합니다.
   selector는 problem, forces, preconditions, contraindications, solution, guarantees, costs, failure modes와
   language realizations가 있는 `decision-ready` 항목만 추천합니다.
6. source family file은 discovery를 위해 compact하게 유지하고, 추천 metadata는 stable ID를 대상으로
   `decision-ready.json` overlay에 둡니다. overlay는 base identity와 source를 덮어쓸 수 없고 모든
   판단 필드를 항목마다 직접 선언합니다. validator가 count drift, duplicate ID, dangling relation,
   cross-family 동일 이름 관계와 decision-ready 필수 필드를 검사합니다.
7. `source-manifest.json`에 553개 원천 이름과 정규화 결과·locator를 별도로 고정하고 catalog mapping과
   manifest digest를 validator에서 대조합니다.
8. 후보는 최대 3개, 기본 primary는 1개입니다. distributed·messaging 선택은 delivery, ordering,
   consistency, idempotency와 recovery를 명시적으로 확인합니다.

## Alternatives Considered

- Engineering에 pattern skill 포함: 구현 lifecycle과 pattern 지식의 업데이트 경계를 결합하고 pattern
  선택만 필요한 요청에서도 무거운 개발 workflow를 요구합니다.
- Quality Engineering에 포함: broad maintainability review와 named pattern guarantee review의 trigger가
  겹치고, 단순성 검토가 특정 pattern catalog를 전제하게 됩니다.
- 모든 entry를 즉시 추천 가능하게 작성: 넓은 이름 목록을 빠르게 제공하지만 얕은 설명을 확정적 추천
  근거로 오인하게 됩니다.
- 일반 구현마다 자동으로 pattern을 제안: discovery는 늘지만 speculative abstraction과 trigger 충돌이
  커집니다.

## Consequences

사용자는 패턴 이름을 미리 알지 않아도 실제 설계 문제에서 조건부로 선택 도움을 받을 수 있고,
패턴이 불필요한 경우도 구조화된 결과로 남길 수 있습니다. 플러그인은 독립 설치 가능하며 Engineering과
함께 사용할 때도 pattern 판단과 구현 lifecycle의 책임이 분리됩니다.

전체 raw index와 추천 가능한 subset의 완성도가 다르므로 현재 553개 중 36개만 decision-ready입니다.
나머지 이름은 누락 방지와 discovery에는 유용하지만 추천 범위가 넓어지려면 source 확인, 자체 정규화와
행동 평가가 추가로 필요합니다. 원천 catalog 변경 시 observed date와 count를 갱신해야 합니다.

## Revisit When

실제 routing 평가에서 일반 구현을 반복해서 가로채거나 pattern이 필요한 요청을 놓칠 때, 같은 이름의
scope 관계가 선택 오류를 만들 때, decision-ready 승격 기준이 너무 느슨하거나 엄격할 때 다시 검토합니다.
원천 catalog가 변경되거나 실사용에서 새 family가 반복적으로 필요할 때 inclusion policy와 count를
갱신합니다.
