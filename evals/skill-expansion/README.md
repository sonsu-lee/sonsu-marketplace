# Retained capability behavior cases

[`cases.json`](cases.json)은 major cutover 뒤 남은 Workflow, Product, Interface Design, Operations UI,
Figma Workflow와 explicit `review-pr`의 산출물 경계를 평가합니다. continuity, 일반 Engineering
lifecycle, fixed model/reviewer policy와 retry-count 비교는 포함하지 않습니다.

평가 모델에는 opaque case ID, `prompt`, `installed_plugins`에 해당하는 native skill registry와 그
시점에 관찰 가능한 fixture만 제공합니다. `expected`와 과거 결과는 숨깁니다. 외부 PR/ticket/Figma와
repository source를 실제 수정하지 않습니다.

확인할 계약:

- Workflow: inspect/repair/create/lifecycle을 구분하고 target·permission·readback을 유지합니다.
- Product: discovery/evidence/domain/test/assessment/PRD를 구분하고 `to-prd`가 issue를 만들지 않습니다.
- UI: 일반 interface와 operations UI, proposal/redesign/audit 산출물 scope를 구분합니다.
- Figma: current host가 노출한 official capability만 사용하고 없으면 성공을 추정하지 않습니다.
- `review-pr`: explicit invocation에서만 선택하고 source를 수정하지 않으며 marker/readback이 있는
  COMMENT 하나만 게시합니다. 일반 review는 host-native path입니다.

Static registration, native loader discovery, model selection, behavior와 external mutation은 별도 증거입니다.
결과는 `pass | fail | blocked | not_run | inconclusive`로 기록하고 실행하지 않은 scope gate를 통과로
바꾸지 않습니다. 공통 DQ contract의 author/evaluator 관계와 minimum score 규칙은
[`../design-quality/`](../design-quality/)에서 별도 검증합니다.
