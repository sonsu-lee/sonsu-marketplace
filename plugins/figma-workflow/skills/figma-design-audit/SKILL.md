---
name: figma-design-audit
description: 기존 Figma file, page, frame 또는 selection의 Auto Layout, responsive behavior, component·variable·icon 사용, prototype interaction과 developer handoff를 수정 없이 검토해 달라는 요청에 사용한다. 화면 생성·수정, 코드 구현, FigJam과 architecture diagram에는 사용하지 않는다.
---

# Figma design audit

현재 Figma artifact를 source of truth로 읽고 구조, 재사용, 상호작용과 handoff의 실제 evidence를
검토한다. 감사 요청은 mutation 권한이 아니다.

## 대상과 evidence

[tool routing](../../references/tool-routing.md)과
[capability and evidence](../../references/capability-and-evidence.md)를 읽는다. 정확한 file/page/frame이
주어지지 않았으면 현재 selection을 사용할 수 있는지 확인하고, 안전한 단일 target이 없을 때만
하나를 요청한다. Provider가 요구하는 Figma prerequisite skill을 불러오되 write API는 호출하지 않는다.
Model, auditor 역할 또는 평가 구성이 범위에 있으면
[execution architecture](../../references/execution-architecture.md)를 함께 읽는다.

Screenshot과 metadata, hierarchy, components, variables, reactions와 annotations를 필요한 범위에서
읽는다. Screenshot에서 보이지 않는 구조를 추정해 확정하지 않는다.

## 감사 기준

[Figma quality contract](../../references/figma-quality-contract.md)를 기준으로 다음을 확인한다.

- section, frame와 semantic layer organization
- Auto Layout, `HUG`·`FILL`·`FIXED`, constraints와 absolute-position 예외
- content extreme과 resize에서 예상되는 failure
- component reuse, detached instances, variant와 property 책임
- semantic variable binding과 중복 hardcode
- font, text resize, clipping과 realistic content
- [icon policy](../../references/icon-policy.md)에 따른 provenance와 consistency

Prototype 또는 user flow가 범위에 있으면
[interaction specification](../../references/interaction-spec.md)을 읽고 starting point, executable reactions,
destinations, errors, cancel/back, recovery와 annotations를 분리해 확인한다.

## 결과

Finding마다 target, 관찰 evidence, 사용자 영향, 확실성, 최소 수정 방향을 제시한다. 실제 resize나
prototype playback을 실행하지 못한 항목은 `needs-live-validation` 또는 `inconclusive`로 표시한다.
수정 요청으로 범위가 바뀌면 감사를 종료한다. 화면 구조 수정은 `figma-product-design`, prototype
connection 수정은 `figma-prototype-flow`의 mutation workflow로 다시 시작한다.

## 예시

“현재 checkout selection의 Auto Layout과 끊긴 동선을 봐 줘”라는 요청에서는 화면을 고치지 않고
node sizing과 reaction destination을 읽는다. 시각적으로 정상이어도 `FILL` parent가 없거나 error
state가 도달 불가능하면 각각 별도 finding으로 보고한다.
