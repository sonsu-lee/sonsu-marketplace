---
name: figma-product-design
description: Figma Design 제품 화면의 Auto Layout, responsive behavior, exact assets와 handoff 품질 계약을 적용하거나 화면 생성·수정 작업을 그 기준으로 보완해 달라는 요청에 사용한다. Prototype connection이 주목적인 작업, 개별 component·library authoring, Figma-to-code 구현, FigJam workshop, system diagram과 읽기 전용 Figma 감사에는 사용하지 않는다.
---

# Figma product design

Figma가 최종 제품 UI의 source of truth일 때 native frame, Auto Layout, component, variable와 exact
asset을 사용한다. 시각적 유사성뿐 아니라 resizing, state와 handoff를 검증한다.

## 시작 전

1. [tool routing](../../references/tool-routing.md)으로 최종 artifact가 Figma Design인지 확인한다.
2. [capability and evidence](../../references/capability-and-evidence.md)를 읽고 현재 Figma tool, provider가
   요구하는 prerequisite skill, identity, target와 edit permission을 확인한다.
   Model, custom agent 또는 local plugin 선택이 필요한 요청은
   [execution architecture](../../references/execution-architecture.md)를 함께 읽는다.
3. 기존 page, selection, nearby screens, components, variables, styles와 Code Connect 정보를 읽는다.
   create 요청은 허용하지만 기존 system을 읽지 않은 채 primitives부터 만들지 않는다.

화면이나 composed view를 실제 canvas에 생성·수정할 때 공식 `figma:figma-generate-design`과 mandatory
prerequisite인 `figma:figma-use`를 함께 사용한다. 이 스킬은 native craft와 검증 계약을 보완하며
공식 canvas workflow를 대체하지 않는다. 개별 component 생성·library 작업은 공식
`figma:figma-generate-library`가 담당한다.

Write capability가 없으면 screen/layout specification을 제공하고 mutation을 `not_run`으로 보고한다.
사용자가 지정한 Figma 요청을 다른 제품에 조용히 옮기지 않는다.

## 생성과 수정

[Figma quality contract](../../references/figma-quality-contract.md)를 적용한다. 화면과 wrapper를 먼저
만들고 한 visual section씩 작은 tool call로 작성한다. 같은 page subtree, component set, variable
collection, prototype graph 또는 selection/current-page state에 의존하는 mutation은 하나의 writer로
직렬화한다. 독립 영역을 병렬화하더라도 writer는 적용 직전 target을 다시 읽는다.

기존 component와 semantic variable을 우선한다. 새로운 reusable pattern만 component로 만들고,
variant와 component property의 역할을 나눈다. icon 또는 vector가 필요하면
[icon policy](../../references/icon-policy.md)를 따른다.

화면 생성에 interaction이 포함되면 `figma-prototype-flow`를 함께 사용한다. 실제 control의 reaction,
annotation과 named state topology는 그 스킬이 소유하며 제품 화면 작업은 필요한 visual state와
component structure를 제공한다.

사용자가 Figma의 선택, 반복 편집, 정리 방법이나 수동 cleanup 절차를 함께 요청하면
[Figma editing practice](../../references/figma-editing-practice.md)를 읽는다. Keyboard shortcut 암기를
artifact 품질로 평가하거나 UI-only 조작을 MCP/API capability처럼 보고하지 않는다.

## 검증과 결과

각 section과 전체 화면의 screenshot, node hierarchy, sizing과 binding을 다시 읽는다. short/long/localized
text, absent/extra content, 0/1/many item과 narrow/wide resize를 위험에 맞게 시험한다. Interaction이
포함됐으면 `figma-prototype-flow`가 보고한 reaction readback과 playback 상태를 handoff에 포함한다.

변경한 frame, 재사용한 component·variable·asset, interaction handoff와 실제 검증 상태를 보고한다.
성공한 write와 검증되지 않은 structure가 섞였으면 `inconclusive`로 구분하고 영향받은 범위만 다시
검증한다.

## 예시

“결제 화면에서 Pay를 누르면 확인 modal이 열리고 성공하면 주문 상세로 이동하게 해 줘”라는 요청은
이 스킬로 confirmation, submitting, success와 error의 visual state를 만들고 `figma-prototype-flow`로
actual reaction, annotation과 starting point를 연결·검증한다. 화면 사이에 화살표만 그린 결과는
완료가 아니다.
