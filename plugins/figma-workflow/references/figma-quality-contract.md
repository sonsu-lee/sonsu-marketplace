# Figma product-design quality contract

## Canvas structure

- 변경 전에 current page, selection, nearby screen, component, variable와 style을 읽는다.
- feature 또는 review state는 section, 제품 화면은 top-level frame으로 조직한다. semantic layer name을 쓰고
  layout·constraint·clipping·prototype behavior가 필요한 구조를 임시 group으로 끝내지 않는다.
- parent wrapper와 screen skeleton을 먼저 만들고 orphan fragment를 남기지 않는다. canonical handoff/prototype
  state와 exploration/archive를 분리한다.

## Layout model, Auto Layout과 responsive behavior

각 container는 사용자 작업에서 함께 읽거나 조작할 내용을 묶고, 읽는 순서와 resize intent에 따라 layout model을 선택한다.
같은 묶음의 제목·설명·control은 읽기 방향의 시작선을 맞추고, 관련 요소 사이의 gap을 다른 묶음 사이보다 작게
잡는다. 숫자 열의 끝선 정렬처럼 정보 해석에 필요한 정렬은 유지하며 모든 child를 같은 간격으로 펼치지 않는다.
이 관계를 기존 spacing token과 Auto Layout의 alignment·gap·padding으로 표현한다. 한 축의 순서·정렬·간격이
핵심이면 horizontal 또는 vertical Auto Layout을 사용하고, 같은 주축에서 반복 항목이 다음 줄로 reflow하면 wrap을
사용한다. row와 column track, cell 또는 span이 함께 의미를 가지는 2차원 구조에는 Grid Auto Layout을 사용한다.
각 nesting level이 독립적인 한 축 관계를 가질 때에는 nested Auto Layout을 유지하되, 2차원 관계를 의미 없는
wrapper나 absolute positioning으로 흉내 내지 않는다. Layout grid는 정렬을 위한 visual guide이며 responsive
behavior의 구조적 근거로 취급하지 않는다.

`HUG`는 content size, `FILL`은 Auto Layout parent의 available space, `FIXED`는 icon slot·touch target처럼
의도적으로 안정된 geometry에 쓴다. child를 Auto Layout parent에 넣은 뒤 `FILL`을 설정한다. non-Auto Layout
frame anchor에는 constraints, overlay·decorative overlap에는 scoped absolute positioning을 쓴다.

clipping으로 layout defect를 숨기지 않고 overflow를 명시한다. 의미·resize·alignment 역할이 없는 wrapper를
추가하지 않는다. component instance를 realistic screen parent에 넣어 narrow/wide container, short/long/multiline
text, empty/optional element, localized copy, 0/1/many item, icon-present/absent state를 확인한다. material section
마다 screenshot과 node sizing을 함께 읽는다.

같은 곡선 형태의 두 surface가 균일한 inset으로 중첩되면, 안쪽 radius는 `max(0, outer radius - inset)`을
출발점으로 검토한다. inset은 두 윤곽 사이의 실제 거리이며 stroke 위치·두께도 포함해 읽는다. 이 계산은
원호형 모서리의 관계를 확인하는 방법이다. corner smoothing, 비대칭 여백, pill 또는 독립된 내부 control에는
그대로 적용하지 않는다. 기존 component·radius token을 먼저 확인하고, 조정이 필요하면 해당 중첩 surface에
한정해 바인딩과 화면 결과를 다시 읽는다.

## Components, variants와 variables

Code Connected component, enabled library, local component, existing screen pattern, new component 순서로 찾는다.
visual match를 위해 instance를 detach하지 않는다. variants는 state/type/size axis, Boolean/Text/Instance swap은
controlled content change, Slot은 실제 free-form nested content가 필요한 경우에만 쓴다. library 변경은 API
변경으로 보고 property meaning, representative instance와 breaking change 여부를 검증한다.

semantic variable이 있으면 bind하고 새 variable에는 scope, alias, product reason을 둔다. primitive·semantic·
component token은 실제 context가 다를 때만 분리한다. variable로 모든 one-off value를 기계적으로 바꾸지 않으며
styles가 project convention이면 유지한다.

## Text, icons와 handoff

먼저 실제 화면의 제목, 본문, control label과 보조 정보가 어떤 역할과 읽는 순서를 가지는지 정하고 기존 Text Style에
매핑한다. 기존 체계가 없다면 현재 화면에서 반복되는 역할에 필요한 style만 만든다. `Display`, `Title`, `Body`,
`Label`, `Caption`은 역할을 찾는 예시이며 모든 프로젝트에 다섯 이름이나 새로운 크기 scale을 강제하지 않는다.
font size·weight·line height는 Text Style로, text color는 기존 semantic variable 또는 color style로 연결한다.
중요도 차이는 크기·굵기·간격으로 표현하고, 보조 정보를 연하게 만들 때도 실제 배경에서 읽을 수 있는 대비를 유지한다.

actual font를 확인하고 `font_load`가 제공되면 load한다. 불가능하면 다른 font로 조용히 대체하지 않는다.
wrapping intent에 맞는 text sizing과 realistic content, max-line/truncation을 유지한다. 같은 역할이 여러 화면과
긴 번역문에서도 일관되게 읽히는지 screenshot과 style binding으로 확인한다. icon은
[icon policy](icon-policy.md)의 exact component/provenance, accessible name, intended size와 state behavior를
따른다.

handoff에는 component description, external documentation link, development/interaction/accessibility/content
annotation, exact asset, Code Connect mapping을 보존한다. happy path와 empty/loading/error/permission state,
responsive behavior, content limit, focus/keyboard, scroll/sticky, interaction result와 token mapping을 노출한다.
웹 구현 대상이면 Figma node tree를 DOM과 기계적으로 일치시키지 않되, `flex` 또는 `grid` 의도를 복원할 수 있도록
해당 layout model의 속성을 기록한다. flex 계열에는 flow direction, wrap, alignment, gap, padding과 resize
behavior를, grid 계열에는 track sizing, gap, padding, span과 resize behavior를 남긴다. 웹이 아닌 대상에는 CSS
용어를 강제하지 않고 해당 platform의 layout primitive로 옮길 수 있는 구조적 의도를 기록한다.
최종 screenshot만으로 완료를 판단하지 않고 영향 component, consuming screen, connected prototype path를
재검토한다.
