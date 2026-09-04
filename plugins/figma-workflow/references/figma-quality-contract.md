# Figma product-design quality contract

## Canvas structure

- 변경 전에 current page, selection, nearby screen, component, variable와 style을 읽는다.
- feature 또는 review state는 section, 제품 화면은 top-level frame으로 조직한다. semantic layer name을 쓰고
  layout·constraint·clipping·prototype behavior가 필요한 구조를 임시 group으로 끝내지 않는다.
- parent wrapper와 screen skeleton을 먼저 만들고 orphan fragment를 남기지 않는다. canonical handoff/prototype
  state와 exploration/archive를 분리한다.

## Auto Layout과 responsive behavior

Auto Layout은 sibling order, content size, spacing 또는 alignment가 관계를 결정할 때 사용한다. `HUG`는 content
size, `FILL`은 Auto Layout parent의 available space, `FIXED`는 icon slot·touch target처럼 의도적으로 안정된
geometry에 쓴다. child를 Auto Layout parent에 넣은 뒤 `FILL`을 설정한다. non-Auto Layout frame anchor에는
constraints, overlay·decorative overlap에는 scoped absolute positioning을 쓴다.

clipping으로 layout defect를 숨기지 않고 overflow를 명시한다. 의미·resize·alignment 역할이 없는 wrapper를
추가하지 않는다. component instance를 realistic screen parent에 넣어 narrow/wide container, short/long/multiline
text, empty/optional element, localized copy, 0/1/many item, icon-present/absent state를 확인한다. material section
마다 screenshot과 node sizing을 함께 읽는다.

## Components, variants와 variables

Code Connected component, enabled library, local component, existing screen pattern, new component 순서로 찾는다.
visual match를 위해 instance를 detach하지 않는다. variants는 state/type/size axis, Boolean/Text/Instance swap은
controlled content change, Slot은 실제 free-form nested content가 필요한 경우에만 쓴다. library 변경은 API
변경으로 보고 property meaning, representative instance와 breaking change 여부를 검증한다.

semantic variable이 있으면 bind하고 새 variable에는 scope, alias, product reason을 둔다. primitive·semantic·
component token은 실제 context가 다를 때만 분리한다. variable로 모든 one-off value를 기계적으로 바꾸지 않으며
styles가 project convention이면 유지한다.

## Text, icons와 handoff

actual font를 확인하고 `font_load`가 제공되면 load한다. 불가능하면 다른 font로 조용히 대체하지 않는다.
wrapping intent에 맞는 text sizing과 realistic content, max-line/truncation을 유지한다. icon은
[icon policy](icon-policy.md)의 exact component/provenance, accessible name, intended size와 state behavior를
따른다.

handoff에는 component description, external documentation link, development/interaction/accessibility/content
annotation, exact asset, Code Connect mapping을 보존한다. happy path와 empty/loading/error/permission state,
responsive behavior, content limit, focus/keyboard, scroll/sticky, interaction result와 token mapping을 노출한다.
최종 screenshot만으로 완료를 판단하지 않고 영향 component, consuming screen, connected prototype path를
재검토한다.
