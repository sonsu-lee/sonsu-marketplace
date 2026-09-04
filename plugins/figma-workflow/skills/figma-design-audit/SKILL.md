---
name: figma-design-audit
description: 기존 Figma file, page, frame 또는 selection의 Auto Layout, responsive behavior, component·variable·icon 사용, prototype interaction과 developer handoff를 수정 없이 검토해야 할 때 사용한다. 화면 생성·수정, 클릭 동선 변경, FigJam 워크숍과 draw.io 구조도에는 사용하지 않는다.
---

# Figma design audit

현재 Figma artifact를 source of truth로 읽고 구조, 재사용, 상호작용과 handoff의 실제 evidence를 검토한다. 감사 요청은 mutation 권한이 아니다.

## 대상과 evidence

[tool routing](../../references/tool-routing.md), [capability and evidence](../../references/capability-and-evidence.md)를 읽는다. 정확한 file/page/frame이 주어지지 않았으면 현재 selection을 사용할 수 있는지 확인하고, 안전한 단일 target이 없을 때만 하나를 요청한다. 읽기 전용이라도 `use_figma`를 실제 호출한다면 먼저 `figma:figma-use`를 invoke하고 tool call의 `skillNames`에 `figma-use`를 포함한다. 설치·노출되지 않았으면 tool/API를 가정하지 않고 `blocked`, `not_run` 또는 `inconclusive`로 보고한다.

감사는 official Figma MCP의 read capability로 수행하고 write API를 호출하지 않는다. 수동 Desktop companion은 current selection을 대상으로 `inspect-selection`, `audit-auto-layout`, `audit-prototype-links`의 결정적 JSON evidence를 제공할 수 있지만, 미적·UX 판단이나 general canvas read/write 대체물이 아니다. schema, preview 결과와 failure 경계는 [deterministic execution](../../references/deterministic-execution.md) 및 [companion README](../../figma-plugin/README.md)를 따른다.

Screenshot과 metadata, hierarchy, components, variables, icon provenance, reactions와 annotations를 필요한 범위에서 읽는다. Screenshot에서 보이지 않는 구조를 추정해 확정하지 않는다.

## 감사 기준

[Figma quality contract](../../references/figma-quality-contract.md)를 기준으로 다음을 확인한다.

- section, frame와 semantic layer organization
- Auto Layout, `HUG`·`FILL`·`FIXED`, constraints와 absolute-position 예외
- content extreme과 resize에서 예상되는 failure
- component reuse, detached instances, variant와 property 책임
- semantic variable binding과 중복 hardcode
- font, text resize, clipping과 realistic content
- [icon policy](../../references/icon-policy.md)에 따른 exact component/provenance, accessible name과 size

prototype 또는 user flow가 범위에 있으면 [interaction specification](../../references/interaction-spec.md)을 읽고 starting point, executable reactions, destinations, overlay/back/dismiss, errors, recovery와 readable annotations를 분리해 확인한다.

## 결과

finding마다 target, 관찰 evidence, 사용자 영향, 확실성, 최소 수정 방향을 제시한다. 실제 resize, prototype playback 또는 Desktop companion 실행을 하지 못한 항목은 `needs-live-validation`, `inconclusive` 또는 `not_run`으로 표시한다. 수동 audit output은 finding의 근거이지 디자인 판정의 자동 결론이 아니다.

수정 요청으로 범위가 바뀌면 감사를 종료한다. 화면 구조 수정은 `figma-product-design`, prototype connection 수정은 `figma-prototype-flow`의 mutation workflow로 다시 시작한다.

## 예시

“현재 checkout selection의 Auto Layout과 끊긴 동선을 봐 줘”라는 요청에서는 화면을 고치지 않고 node sizing과 reaction destination을 읽는다. 시각적으로 정상이어도 `FILL` parent가 없거나 error state가 도달 불가능하면 각각 별도 finding으로 보고한다.
