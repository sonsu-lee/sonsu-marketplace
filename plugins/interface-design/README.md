# Interface Design

웹·모바일 UI의 정보 구조와 표현을 설계·재설계하는 `1.0.0` capability pack이다.
`design-interface`, `redesign-interface`와 domain reference, validator, schema, example을 유지한다.
일반 구현 lifecycle과 session continuity를 소유하지 않는다.

모든 작업은 `사용자·맥락 → 판단/과업 → 필요한 정보 → 표현 → 상태/interaction → 관찰 결과`를
연결하는 Design Decision Contract를 사용한다. Proposal은 DQ0–DQ6, Figma/implementation은
DQ0–DQ7, live는 DQ0–DQ8을 평가한다.

DQ1–DQ6의 `passed`, `failed`, `inconclusive`에는 같은 artifact revision과 contract digest에 연결된
evaluator run이 최소 하나 필요하다. `relationship: author | independent`는 evidence metadata이며
pack이 independent reviewer 수를 정하거나 spawn하지 않는다. 여러 run이 있으면 최솟값을 gate
score로 쓰고 `maximum_score_divergence`를 넘으면 `inconclusive`다.

```sh
python3 scripts/validate_design_quality.py contract <contract.json>
python3 scripts/validate_design_quality.py report <report.json> <contract.json>
```
