# 0010 Add an Independent Design Plugin

- Status: Accepted
- Date: 2026-09-03
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-03 현재 대화에서 조사·설계안을 바탕으로 `design` 플러그인을 구현하고 branch, commit, push와 Draft PR을 만들도록 승인했습니다. plugin 설치, live Figma·Paper mutation과 유료 model 평가는 승인 범위에 포함되지 않습니다.

## Context

공식 Figma plugin은 canvas read/write, design-to-code, library generation, Code Connect, FigJam과
motion을 폭넓게 제공합니다. 그러나 제품 화면 작업에서 Auto Layout과 responsive behavior를 어떤
content 조건으로 검증할지, icon source를 어떻게 보존할지, prototype reaction과 annotation을
어떻게 구분할지는 여러 공식 skill과 실무 문서에 흩어져 있습니다. 같은 Figma 요청이라도 화면
생성·수정과 기존 artifact의 읽기 전용 감사에는 서로 다른 권한과 완료 근거가 필요합니다.

Paper Design은 DOM, flex, token, screenshot, JSX와 computed style을 읽고 쓸 수 있는 MCP를
제공하지만 공식 agent plugin에는 별도의 workflow skill이 없습니다. 현재 tool surface에는 Figma와
같은 native reaction 작성 기능이 없어 interaction을 실행 가능한 prototype으로 보고할 수 없습니다.

기존 draw.io skill은 architecture, AWS, UML, ERD와 data flow에 적합하고 trigger에 mockup과
wireframe도 포함합니다. 제품 UI와 clickable flow까지 draw.io로 라우팅하면 최종 artifact가 가져야
할 component, token, screen state와 executable interaction을 잃습니다. 반대로 architecture를
Figma에 두는 것도 정밀한 shape library와 `.drawio` artifact의 장점을 잃습니다.

## Decision

`plugins/design/`에 독립 `Design` 플러그인을 만들고 다음 스킬을 제공합니다.

- `figma-product-design`: Figma 제품 화면 생성·수정, responsive layout, reusable structure와 exact
  assets를 담당합니다.
- `figma-prototype-flow`: Figma control의 실제 reaction, overlay, 상태 분기와 prototype playback을
  담당합니다.
- `figma-design-audit`: 기존 Figma artifact의 Auto Layout, components, variables, icons, prototype와
  handoff를 수정 없이 감사합니다.
- `paper-product-design`: Paper의 flex·DOM·token 기반 생성·수정·감사와 code roundtrip을
  담당합니다.

공식 Figma skill, Paper MCP와 draw.io를 복제하거나 hard dependency로 포함하지 않습니다. 각 skill은
현재 environment의 provider capability와 permission을 확인하고, 필요한 공식 prerequisite가 있으면
runtime에서 조합합니다. Provider가 없으면 advisory specification을 제공하거나 `blocked`·`not_run`을
보고하며 실행했다고 주장하지 않습니다.

실제 Figma screen·composed view 생성은 공식 `figma-generate-design`과 `figma-use`, 개별 component와
library authoring은 공식 `figma-generate-library`가 담당합니다. 로컬 `figma-product-design`은 화면의
native craft와 검증 계약을 보완하며 공식 workflow를 대체하지 않습니다.

도구 선택은 final artifact의 source of truth로 결정합니다. 제품 UI와 clickable interaction은 Figma
Design, collaborative journey와 workshop은 FigJam, system architecture는 draw.io, HTML/CSS 구조와
code roundtrip은 Paper Design을 사용합니다. 반복된 실제 routing conflict가 확인되기 전에는 공통
router skill을 추가하지 않습니다.

Auto Layout은 구조적 sibling relationship에 적용하는 품질 계약으로 사용하지만 모든 frame에
강제하지 않습니다. Overlay와 decoration은 좌표 기반 예외가 될 수 있으며 unnecessary wrapper와
deep nesting도 finding입니다. Figma interaction은 executable reaction, annotation과 state topology의
세 evidence layer로 검증합니다. Paper interaction은 native capability가 생기기 전까지 state artboard와
comment를 사용한 `spec-only` 결과입니다.

동일한 live canvas의 mutation은 충돌 도메인별 single-writer로 제한합니다. 같은 page subtree,
component set, variable collection, prototype graph와 selection/current-page 의존 write는 직렬화합니다.
Provider가 허용하고 node·variable·prototype dependency가 없는 독립 page는 병렬화할 수 있지만,
writer는 적용 직전 target을 다시 읽고 다른 writer가 같은 충돌 도메인을 수정하면 직렬화하거나
중단합니다.

Skill은 session model을 자동으로 변경하지 않습니다. 현재 runtime catalog와 공식 model 역할을
확인한 뒤 `gpt-5.6-sol` + `medium`을 품질 우선 잠정 기준으로 사용하고, 반복·결정론적 작업에는
`gpt-5.6-terra` 또는 `gpt-5.6-luna`를 별도 평가합니다. Custom agent와 Codex profile은 대표
evaluation에서 역할 분리가 이득으로 확인되기 전에는 추가하지 않습니다. 반복 작업이 안정된
input/output 계약, preview, idempotency와 rollback을 요구하면 별도 승인 아래 local Figma plugin을
구현할 수 있으며, 이미 만들어진 결정론적 plugin 실행에는 불필요한 model 호출을 요구하지 않습니다.

외부 skill이나 문서 파일은 복사하지 않고 독자 작성합니다. 검토한 공식·community·practitioner
source와 비복사 범위는 `UPSTREAM.md`에 기록합니다. 플러그인 라이선스는 공개 배포 전에 별도
결정하며 현재 manifest에는 선언하지 않습니다.

## Alternatives Considered

- 공식 Figma plugin을 fork해 local rule을 직접 추가: Figma upstream 갱신과 Developer Terms 범위를
  함께 관리해야 하고 Paper의 독립적인 DOM workflow를 해결하지 못합니다.
- Figma와 Paper를 각각 별도 local plugin으로 분리: provider별 경계는 선명하지만 interaction,
  icon, evidence와 routing 계약이 작은 초기 버전에서 중복됩니다. 실제 update cadence가 달라질 때
  다시 검토합니다.
- 하나의 `design-router` skill을 추가: 도구 선택은 쉬워 보이지만 repository의 plugin independence
  원칙과 충돌하며 모든 디자인 요청에 추가 절차를 만들 수 있습니다.
- `user-flow-diagram`을 별도 skill로 import: flow semantics는 유용하지만 실제 Figma reaction을
  보장하지 않고 FigJam·draw.io와 trigger 경쟁을 늘립니다. 필요한 semantics는 독자 작성한
  `figma-prototype-flow`, interaction reference와 evaluation에 반영합니다.
- 초기에 역할별 custom agent와 model profile을 함께 추가: 비교 평가 없이 model을 고정하고 같은
  canvas의 writer를 늘릴 위험이 있어 reference의 잠정 추천과 평가 계약만 둡니다.
- 지금 local Figma plugin까지 구현: 반복 빈도와 결정론적 계약이 아직 검증되지 않아 도입 조건만
  기록하고 생성은 보류합니다.
- Paper를 Figma workflow의 fallback으로 취급: DOM/code roundtrip이라는 Paper의 장점을 잃고
  unsupported Figma semantics를 성공처럼 표현할 위험이 있습니다.

## Consequences

사용자는 제품 화면을 Figma 안에서 완료하고 버튼·modal·navigation 동선을 실제 prototype으로
검증하는 workflow를 발견할 수 있습니다. Existing Figma는 별도의 read-only audit로 안전하게
검토합니다. Paper에서는 web-native layout과 code handoff를 활용하면서 현재 지원하지 않는
prototype을 명확히 분리합니다. draw.io는 architecture artifact를 계속 독립적으로 담당합니다.

Plugin 자체가 provider를 설치하지 않으므로 환경마다 실행 가능한 범위가 다릅니다. Static skill,
manifest와 fixture 검증은 가능하지만 실제 routing, model 비교와 live canvas behavior는 별도 승인된
evaluation이 필요합니다. 공식 provider tool과 skill이 바뀌면 현재 capability를 다시 읽고 reference와
evaluation을 갱신해야 합니다.

## Revisit When

Figma·Paper·draw.io가 같은 요청에서 반복적으로 잘못 선택될 때, Paper가 native prototype이나
component slots·token modes를 안정적으로 제공할 때, official Figma skill이 이 플러그인의 품질
계약을 직접 제공할 때, Figma와 Paper의 update cadence가 독립 배포를 요구할 때, 또는 Codex가
plugin dependency와 composition을 명시적으로 지원할 때 재검토합니다. 역할별 custom agent는 대표
scenario에서 독립 reviewer 또는 비용 이점이 측정될 때, local Figma plugin은 같은 결정론적 작업이
반복되고 manual correction 비용이 유지보수 비용을 넘을 때 재검토합니다.
