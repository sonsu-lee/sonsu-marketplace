# Capability, permission and evidence

## Capability preflight

mutation 전에 current provider tool, required prerequisite skill, target document, authenticated identity,
permission과 requested scope를 확인한다. plugin 설치는 tool, editable file, Desktop application 또는 full
seat의 존재를 증명하지 않는다.

`structure_read`, `screenshot`, `reaction_write`, `reaction_readback`, `prototype_playback`, `font_load`,
`asset_import`, `export`를 각각 `supported`, `unsupported`, `unavailable`로 기록한다. provider가 tool 전에
prerequisite skill을 요구하고 설치되어 있으면 현재 contract를 따른다. unavailable skill의 내용을 복제하거나
tool name을 발명하지 않는다.

판단형 Figma canvas read/write는 registered official Figma MCP가 유일한 agent writer다. explicit target의
bounded code도 그 MCP 안에서만 허용한다. [deterministic execution](deterministic-execution.md)에 적힌
Desktop companion은 사용자가 수동 실행하는 allowlisted JSON 도구이며 raw MCP, local bridge 또는 second
writer가 아니다.

## Authorization boundary

read나 audit은 mutation을 승인하지 않는다. Figma artifact 생성·수정은 사용자의 external change 요청과
정확한 target 또는 승인된 new file이 필요하다. asset 생성, library publish, Code Connect 변경, export는
요청 결과를 넘는 별도 side effect일 수 있다.

## Evidence layers

| claim | 필요한 근거 |
| --- | --- |
| visual layout | 영향 section과 필요한 경우 전체 view의 current screenshot |
| structural layout | node tree, Auto Layout/resizing metadata와 readback |
| reuse | component instance/property, variable binding, icon provenance |
| clickable interaction | current reaction readback, named state/annotation, prototype playback |
| companion audit | exact node ID와 observed field를 포함한 JSON output |
| cleanup | provider working-state readback 또는 finalization 결과 |

결과는 `passed`, `failed`, `blocked`, `inconclusive`, `not_run`, `not_applicable`, `accepted_risk`로 구분한다.
screenshot은 structure를, annotation은 reaction을, write response는 final appearance를 각각 단독으로 증명하지
못한다. font나 exact asset을 불러올 수 없으면 대체하지 말고 영향 범위만 `blocked` 또는 `inconclusive`로
보고한다.

reaction write/readback이 성공했지만 playback이 unsupported이면 전자는 `passed`, playback은 `not_run`,
clickable-interaction claim은 `inconclusive`다. successful partial work는 보존하되 최신 state를 읽고 영향
범위만 재검증한다.

## Conflict-domain single writer

같은 page subtree, component set, variable collection/mode/alias graph, prototype graph/starting point,
selection/current-page state에 의존하는 write는 직렬화한다. read-only inspection과 provider가 명시적으로
허용한 완전히 독립적인 file/page만 병렬화할 수 있다. writer는 mutation 직전에 exact target을 다시 읽고
다른 writer가 conflict domain을 바꿨으면 refresh하거나 중단한다.
