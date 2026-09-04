---
name: figma-product-design
description: Figma Design에서 제품 화면이나 composed view를 생성 또는 수정하고, Auto Layout, responsive behavior, component, variable, exact icon과 handoff 품질을 함께 다뤄야 할 때 사용한다. 클릭 가능한 prototype 연결, 읽기 전용 감사, FigJam 워크숍, draw.io 시스템 구조도와 코드 구현에는 사용하지 않는다.
---

# Figma product design

Figma Design이 최종 제품 화면의 source of truth일 때 native frame, Auto Layout, component, variable과 검증된 exact asset으로 화면을 만든다. 시각적 유사성만으로 완료를 판단하지 않고 resize, 상태와 handoff evidence까지 유지한다.

## 시작과 실행 선택

1. [tool routing](../../references/tool-routing.md)으로 최종 artifact가 Figma Design인지 확인한다. 제품 화면, 상태, overlay와 interaction 동선은 Figma 안에서 완결한다. FigJam은 탐색·워크숍, draw.io는 AWS·시스템 구조도에만 사용한다.
2. [capability and evidence](../../references/capability-and-evidence.md)를 읽어 target, edit permission, connected Figma capability와 provider가 요구하는 prerequisite skill을 확인한다. 환경에 해당 prerequisite가 설치되어 있다면 현재 계약을 먼저 따르며, 없는 tool/API 이름을 추정하지 않는다.
3. 실행 방식은 [deterministic execution](../../references/deterministic-execution.md)의 분류를 따른다. 판단을 요하는 canvas read/write는 registered official Figma MCP가 유일한 agent writer다. `use_figma`를 호출할 때마다 먼저 `figma:figma-use`를 invoke하고 tool call의 `skillNames`에 `figma-use`를 포함한다. 직접 MCP 작업 또는 explicit target을 가진 bounded code 모두 이 경로 안에서만 수행한다.
4. 기존 page, selection, nearby screens, components, variables, styles와 Code Connect 정보를 읽는다. 기존 system을 읽지 않은 채 primitives부터 만들지 않는다.

composed screen/view는 `figma:figma-use`와 `figma:figma-generate-design`을 함께 invoke한 뒤 `use_figma`를 호출한다. 개별 component·library authoring은 `figma:figma-use`와 `figma:figma-generate-library`를 함께 invoke한다. motion 등 추가 official prerequisite가 현재 설치된 contract에 적용되면 그것도 함께 따른다. 실제 canvas I/O는 현재 연결된 official Figma MCP schema가 정한 경로만 사용하며, 이 skill은 native craft와 evidence 계약을 보완한다. design-to-code는 `figma:figma-design-to-code`의 범위다.

필수 prerequisite 또는 capability가 설치·노출되지 않으면 screen/layout specification만 제공하고 mutation을 `blocked`, `not_run` 또는 `inconclusive`로 보고한다. tool/API를 추정하거나 raw MCP 설치, agent-callable local bridge 또는 두 번째 agent writer를 제안하지 않는다.

## 생성과 수정

[Figma quality contract](../../references/figma-quality-contract.md)를 적용한다. 화면과 wrapper를 먼저 만들고 한 visual section씩 작은 write와 readback으로 진행한다. 같은 page subtree, component set, variable collection, prototype graph 또는 selection/current-page state에 의존하는 mutation은 official MCP writer 하나가 직렬화한다.

각 material container를 만들기 전에 한 축 flow, wrap 또는 2차원 track 중 content relationship과 resize intent에 맞는 layout model을 정한다. 웹 handoff에서는 Figma structure를 DOM과 일대일로 복제하지 않으면서 `flex`·`grid` 구현 의도를 복원할 수 있는 속성과 annotation을 남긴다.

기존 component와 semantic variable을 우선한다. 새로운 reusable pattern만 component로 만들고 variant와 component property의 역할을 나눈다. icon 또는 vector는 [icon policy](../../references/icon-policy.md)에 따라 exact component/provenance, accessible name과 intended size를 확인한다.

반복적이고 결과가 명확한 allowlisted 작업만 사용자가 Figma Desktop에서 [Figma Workflow Companion](../../figma-plugin/README.md)을 수동 실행할 수 있다. companion은 `inspect-selection`, `audit-auto-layout`, `audit-prototype-links`, `rename-exact`, `replace-icon-instance-exact`만 받으며 arbitrary JavaScript를 실행하지 않는다. 판단형 layout·UX 결정이나 general canvas write를 companion에 넘기지 않는다.

화면 생성에 interaction이 포함되면 `figma-prototype-flow`를 함께 사용한다. actual reaction, annotation과 named state topology는 그 skill이 소유하며 이 skill은 필요한 visual state와 component structure를 제공한다.

## 검증과 결과

각 section과 전체 화면의 screenshot, node hierarchy, Auto Layout sizing, component/variable binding과 icon provenance를 다시 읽는다. short/long/localized text, absent/extra content, 0/1/many item, narrow/wide resize를 위험에 맞게 확인한다. interaction이 있으면 reaction readback과 playback evidence를 별도로 기록한다.

결과에는 변경한 frame, 재사용한 component·variable·asset, accessible icon name/size, interaction handoff와 각 evidence 상태를 기록한다. write가 성공해도 screenshot·structure·reaction readback 중 필요한 근거가 없으면 해당 claim은 `inconclusive` 또는 `not_run`이다. 실제 Desktop companion 실행과 live Figma 실행을 이 문서 작업에서 했다고 주장하지 않는다.

## 예시

“결제 화면에서 Pay를 누르면 확인 modal이 열리고 성공하면 주문 상세로 이동하게 해 줘”라는 요청에서는 이 skill로 confirmation, submitting, success와 error의 visual state를 만들고 `figma-prototype-flow`로 reaction, annotation과 starting point를 연결·검증한다. 화면 사이에 화살표만 그린 결과는 완료가 아니다.
