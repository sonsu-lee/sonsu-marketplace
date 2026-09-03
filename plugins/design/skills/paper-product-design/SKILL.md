---
name: paper-product-design
description: Paper Design에서 웹 제품 화면을 생성·수정·감사하거나 HTML/CSS·JSX code roundtrip과 interaction state를 다뤄 달라는 요청에 사용한다. Figma-native component library, FigJam workshop과 system architecture diagram에는 사용하지 않는다.
---

# Paper product design

Paper가 최종 artifact이거나 web layout과 code roundtrip을 탐색하는 환경일 때 DOM, flex, tokens와
정확한 JSX/style evidence를 사용한다. Paper를 Figma의 축소판으로 가정하지 않는다.

## 시작 전

1. [tool routing](../../references/tool-routing.md)으로 Paper가 요청된 artifact인지 확인한다.
2. [capability and evidence](../../references/capability-and-evidence.md)를 읽고 Paper Desktop, MCP,
   target와 mutation 범위를 확인한다.
3. 현재 Paper MCP guide를 불러오고 basic info, selection, tree, fonts와 tokens를 읽는다.

Model 또는 역할별 평가가 범위에 있으면
[execution architecture](../../references/execution-architecture.md)를 읽고 Figma 결과를 Paper에 그대로
적용하지 않는다.

Paper capability가 없으면 다른 design product로 전환하지 않는다. 요청된 결과와 현재 blocker를
보고하고 실행하지 않은 mutation을 `not_run` 또는 `blocked`로 남긴다.

## 생성, 수정과 감사

[Paper quality contract](../../references/paper-quality-contract.md)를 읽고 한 visual group씩 작성한다.
Flex, padding과 gap을 기본 구조로 사용하고 반복 요소는 duplicate 후 좁게 수정한다. Existing token과
실제 font를 우선하며 unrelated sibling을 보존한다. Icon과 vector는
[icon policy](../../references/icon-policy.md)를 따른다.

Read-only 감사 요청에는 write tool을 사용하지 않는다. 생성·수정에서는 각 group 뒤 screenshot과
tree/computed-style readback을 수행하고 clipping, typography, alignment, repetition과 artboard fit을
확인한다.

Interaction이 요청되면 [interaction specification](../../references/interaction-spec.md)을 읽는다.
현재 tool surface에 native reaction API가 없으면 before/after state artboard와 comment로 명세하고
`spec-only`로 보고한다. Clickable prototype을 만들었다고 주장하지 않는다.

Code handoff에는 exact JSX와 computed styles를 사용하고 target repository의 component·token convention에
맞춰 적응한다. Screenshot만으로 production code를 만들지 않는다.

수정한 node의 owning artboard를 추적하고 중복 제거한 artboard ID를 성공, partial success와 failure의
finalization 단계에서 `finish_working_on_nodes`에 전달한다. Cleanup 실패를 별도 evidence로 남기고 전체
상태를 최소 `inconclusive`로 낮춘다. 결과에는 변경한 artboard, token·asset, readback evidence,
unresolved comments와 unsupported behavior를 구분한다.

## 예시

“Paper에서 dashboard를 flex로 정리하고 React handoff를 준비해 줘”라는 요청은 현재 DOM을 읽고 section
단위로 수정한 뒤 screenshot, computed styles와 JSX를 확인한다. Modal click 요청이 포함돼도 현재
reaction API가 없다면 state artboard와 comment까지만 만들고 prototype은 `not_run`으로 남긴다.
