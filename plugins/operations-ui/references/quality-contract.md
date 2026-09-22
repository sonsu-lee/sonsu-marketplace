# Operations UI quality contract

[공통 DQ0–DQ8 계약](design-quality.md)이 유일한 품질 게이트다. 평균 총점이나 기존 G0–G7을
사용하지 않는다.

Operations UI에서는 다음 근거를 특히 요구한다.

| Gate | Operations 적용 |
| --- | --- |
| DQ0 | requirement↔scenario와 inventory↔change mapping, 사전 등록 지표 |
| DQ1 | 운영자·맥락·primary question·오판 비용 |
| DQ2 | must-know 정보의 우선순위와 표현 이유 |
| DQ3 | 대상 제품 디자인 시스템의 semantic token/component 매핑; 색상 단독 금지 |
| DQ4 | 계약에서 실제 도달 가능한 상태, 긴 현지화 콘텐츠와 극단값 |
| DQ5 | 권한, 위험 행동, pending·부분 실패·취소·복구 |
| DQ6 | scenario별 environment와 접근성 프로필 |
| DQ7 | proposal/Figma/runtime에 맞는 provenance와 scenario×environment 증거 |
| DQ8 | 사전 등록 지표와 low/medium/high 위험에 맞는 사용자 증거 |

DQ1–DQ6의 `passed`, `failed`, `inconclusive`에는 같은 revision과 contract digest에 연결된
evaluator run이 최소 하나 필요하다. `relationship: author | independent`는 evidence metadata이며
independent reviewer spawn을 강제하지 않는다. 여러 run이 있으면 gate 점수는 최솟값이고 3 이상이
합격선이다. 점수 차이가 1보다 크면 `inconclusive`다. critical finding, hard check와 낮은 차원
점수는 다른 점수로 상쇄하지 않는다.

Operations report의 `extensions.operations.design_system_mapping`은 `system_id`, `token_source`,
contract `representation_ids`, semantic role→token ID와 근거를 가진다. 모든 적용 가능한
representation을 적어도 한 mapping이 덮어야 하며 literal 색상·길이를 token ID로 제출하지 않는다.
implementation/live에서 DQ7을 통과하려면 `browser_receipts`가 모든 task scenario×environment를
통과 상태로 덮어야 한다. Figma scope는 browser receipt 대신 native structure, readback, resize와
prototype 근거를 사용한다.
