# 0010 Add Figma Workflow Plugin

- Status: Accepted
- Date: 2026-09-03
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-03 현재 대화에서 조사·설계안을 바탕으로 `figma-workflow` 플러그인 구현과 branch, commit, push 및 Draft PR 생성을 승인했습니다. plugin 설치, live Figma mutation, Figma Desktop import와 유료 model 평가는 승인 범위에 포함되지 않습니다.

## Context

공식 Figma plugin은 canvas read/write, design-to-code, library generation, Code Connect, FigJam과
motion을 폭넓게 제공합니다. 그러나 제품 화면 작업에서 Auto Layout과 responsive behavior를 어떤
content 조건으로 검증할지, icon source를 어떻게 보존할지, prototype reaction과 annotation을 어떻게
구분할지는 여러 공식 skill과 실무 문서에 흩어져 있습니다. 같은 Figma 요청이라도 화면 생성·수정과
기존 artifact의 읽기 전용 감사에는 서로 다른 권한과 완료 근거가 필요합니다.

기존 draw.io skill은 architecture, AWS, UML, ERD와 data flow에 적합합니다. 제품 UI와 clickable flow를
draw.io로 라우팅하면 최종 artifact가 가져야 할 component, token, screen state와 executable interaction을
잃습니다. 반대로 system architecture를 Figma에 두는 것도 정밀한 shape library와 `.drawio` artifact의
장점을 잃습니다. FigJam은 collaborative journey와 workshop board에 적합하지만 제품 prototype의 정본은
아닙니다.

반복적이고 결과가 명확한 일부 Figma 작업에는 versioned JSON plan, explicit target, preview와 readback
같은 결정적 실행 계약이 유용합니다. 다만 agent가 canvas를 쓰는 경로를 늘리면 같은 page subtree,
component set, variable collection, prototype graph와 editor state에 대한 writer 충돌과 권한 혼동이 생깁니다.

## Decision

`plugins/figma-workflow/`에 독립 `Figma Workflow` 플러그인을 만들고 다음 스킬을 제공합니다.

- `figma-product-design`: Figma 제품 화면의 Auto Layout, responsive structure, component·variable, exact
  asset과 handoff를 담당합니다.
- `figma-prototype-flow`: Figma control의 actual reaction, overlay/back/dismiss, state branch와 prototype
  evidence를 담당합니다.
- `figma-design-audit`: 기존 Figma artifact의 Auto Layout, components, variables, icons, prototype와
  handoff를 수정 없이 감사합니다.

`.codex-plugin/plugin.json`은 plugin-relative `.app.json`을 통해 registered official Figma connector를
참조합니다. Figma canvas의 agent mutation은 이 official MCP `use_figma` 경로만 수행합니다. 실제
`use_figma` 호출은 `figma:figma-use` prerequisite를 먼저 적용하고 해당 tool call의 `skillNames`에
`figma-use`를 포함합니다. 화면과 composed view에는 `figma:figma-generate-design`, component/library에는
`figma:figma-generate-library`, design-to-code에는 `figma:figma-design-to-code`를 current official contract에
따라 조합합니다. capability나 prerequisite가 없으면 다른 writer나 raw MCP로 우회하지 않고 `blocked`,
`inconclusive` 또는 `not_run`을 보고합니다.

Figma Workflow Companion은 Figma Desktop에서 사용자가 직접 실행하는 수동 companion입니다. Codex가
호출하는 bridge나 두 번째 canvas writer가 아니며 arbitrary JavaScript를 실행하지 않습니다. versioned
allowlist JSON의 read-only inspection/audit와 exact rename 또는 icon-instance swap만 처리합니다. mutation은
explicit node ID와 expected state, same-plan preview receipt, apply-time re-read와 readback을 요구합니다.
preview receipt는 plugin UI memory에만 유지하고, 입력 변경 또는 plugin 종료 시 폐기합니다.

도구 선택은 final artifact의 source of truth로 결정합니다. 제품 UI와 clickable interaction은 Figma
Design, collaborative journey와 workshop은 FigJam, system architecture는 draw.io를 사용합니다. 반복된 실제
routing conflict가 확인되기 전에는 공통 router skill을 추가하지 않습니다.

Auto Layout은 관찰 가능한 sibling relationship에 적용하는 품질 계약으로 사용하지만 모든 frame에
강제하지 않습니다. overlay와 decoration은 좌표 기반 예외가 될 수 있습니다. Figma interaction은
executable reaction, annotation과 state topology의 서로 다른 evidence layer로 검증합니다. screenshot,
native structure/readback과 prototype playback은 서로 대신할 수 없습니다.

동일한 live canvas의 mutation은 conflict domain별 single-writer로 제한합니다. 같은 page subtree,
component set, variable collection, prototype graph와 selection/current-page 의존 write는 직렬화합니다.
official MCP가 허용하는 bounded code도 이 writer 규칙과 explicit target·unchanged-area boundary를
따릅니다. writer는 적용 직전 target을 다시 읽고 다른 writer가 같은 conflict domain을 수정하면
직렬화하거나 중단합니다.

Skill은 session model을 자동으로 변경하지 않습니다. 현재 runtime catalog와 공식 model 역할을
확인한 뒤 `gpt-5.6-sol` + `medium`을 품질 우선 잠정 기준으로 사용하고, 반복·결정론적 작업에는
`gpt-5.6-terra` 또는 `gpt-5.6-luna`를 별도 평가합니다. Custom agent와 Codex profile은 대표 evaluation에서
역할 분리가 이득으로 확인되기 전에는 추가하지 않습니다. 이미 만들어진 결정론적 companion 실행에는
불필요한 model 호출을 요구하지 않습니다.

외부 skill이나 문서 파일은 복사하지 않고 독자 작성합니다. 검토한 공식·community·practitioner source와
비복사 범위는 `UPSTREAM.md`에 기록합니다. 플러그인 라이선스는 공개 배포 전에 별도 결정하며 현재
manifest에는 선언하지 않습니다.

## Alternatives Considered

- 공식 Figma plugin을 fork해 local rule을 직접 추가: Figma upstream 갱신과 Developer Terms 범위를
  함께 관리해야 하며 local quality contract와 companion boundary를 독립적으로 관리하기 어렵습니다.
- raw MCP 또는 agent-callable local bridge를 추가: connector registration, OAuth와 live canvas 권한을
  중복하고 official MCP와 두 번째 writer 경쟁을 만듭니다.
- Figma와 FigJam 또는 draw.io를 하나의 local router로 묶기: 도구 선택은 쉬워 보이지만 repository의
  plugin independence 원칙과 충돌하며 모든 요청에 추가 절차를 만듭니다.
- `user-flow-diagram`을 별도 skill로 import: flow semantics는 유용하지만 실제 Figma reaction을
  보장하지 않고 FigJam·draw.io와 trigger 경쟁을 늘립니다. 필요한 semantics는 독자 작성한
  `figma-prototype-flow`, interaction reference와 evaluation에 반영합니다.
- 초기에 역할별 custom agent와 model profile을 함께 추가: 비교 평가 없이 model을 고정하고 같은
  canvas의 writer를 늘릴 위험이 있어 reference의 잠정 추천과 평가 계약만 둡니다.
- local Figma companion을 agent writer로 만들기: deterministic operation에 유용하지만 selection 의존
  mutation과 live write 권한을 agent에 중복 부여합니다. 사용자가 Desktop에서 직접 실행하는 구조를
  유지합니다.

## Consequences

사용자는 제품 화면을 Figma 안에서 완료하고 버튼·modal·navigation 동선을 실제 prototype으로
검증하는 workflow를 발견할 수 있습니다. Existing Figma는 별도의 read-only audit로 안전하게
검토합니다. 수동 companion은 JSON-safe 구조 evidence와 좁은 mutation을 제공하지만 디자인 판단이나
agent orchestration을 대체하지 않습니다. FigJam과 draw.io는 각각 workshop 및 architecture artifact를
계속 독립적으로 담당합니다.

Plugin 자체가 connector를 설치하거나 권한을 부여하지 않으므로 환경마다 실행 가능한 범위가 다릅니다.
Static skill, manifest, fixture, TypeScript test와 bundle 검증은 가능하지만 actual Figma MCP exposure,
live canvas mutation, Figma Desktop import와 companion execution은 별도 승인된 evaluation이 필요합니다.
실행하지 않은 검증은 `not_run`으로 남겨야 합니다. 공식 provider tool과 skill이 바뀌면 current capability를
다시 읽고 reference와 evaluation을 갱신해야 합니다.

## Revisit When

Figma, FigJam과 draw.io가 같은 요청에서 반복적으로 잘못 선택될 때, official Figma skill이 이
플러그인의 품질 계약을 직접 제공할 때, Codex가 plugin dependency와 composition을 명시적으로 지원할
때, 또는 companion의 반복 작업이 manual correction 비용을 넘는 유지보수 비용을 유발할 때 재검토합니다.
역할별 custom agent는 대표 scenario에서 독립 reviewer 또는 비용 이점이 측정될 때 재검토합니다.
