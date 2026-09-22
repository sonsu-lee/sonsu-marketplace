# Operations UI

운영형 B2B 화면을 설계, 재설계, 감사하고 Figma flow로 연결하는 `1.0.0` capability pack이다.
업무의 사용자·과업·정보·표현·상태·권한·환경을 추적 가능한 contract로 만들고 실제 browser/user
evidence를 artifact scope와 구분한다.

- `design-operations-ui`
- `redesign-operations-ui`
- `audit-operations-ui`
- `figma-operations-flow`

Proposal은 DQ0–DQ6, Figma/implementation은 DQ0–DQ7, live는 DQ0–DQ8을 평가한다. DQ1–DQ6의
판정에는 같은 artifact/contract evaluator run이 최소 하나 필요하다. relationship은 evidence
metadata이며 pack이 independent reviewer를 필수 spawn하지 않는다. 여러 run이면 최솟값과
`maximum_score_divergence`를 보존한다.

Operations 확장은 requirement↔scenario, current behavior inventory↔change contract,
scenario×environment browser receipt를 보존한다. 정적 mock, Figma와 screenshot을 runtime evidence로
승격하지 않는다.
