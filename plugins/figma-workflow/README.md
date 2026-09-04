# Figma Workflow

Figma Design에서 제품 화면, responsive Auto Layout, component·variant·variable, exact icon과 clickable prototype을 생성·수정·감사할 때 native 구조와 evidence 기준을 제공하는 Codex plugin입니다. 판단이 필요한 canvas read/write의 agent writer는 이 plugin이 등록한 official Figma MCP connection 하나입니다.

## 스킬

| 스킬 | 책임 |
| --- | --- |
| `figma-product-design` | Figma 제품 화면의 Auto Layout, responsive structure, component·variable, exact asset과 handoff |
| `figma-prototype-flow` | actual control의 reaction, overlay/back/dismiss, state branch와 prototype evidence |
| `figma-design-audit` | Figma artifact의 구조, system reuse, icon provenance, interaction과 handoff를 수정 없이 감사 |

## 도구 경계

- 제품 화면, visual state, overlay와 interaction 동선은 Figma Design에서 완결합니다.
- FigJam은 초기 journey 탐색과 workshop board에 사용하며 제품 prototype의 정본이 아닙니다.
- AWS, network, UML, ERD와 system architecture는 draw.io에서 native `.drawio`로 만듭니다.
- 판단형 Figma canvas read/write는 registered official Figma MCP만 수행합니다. raw MCP 설치, agent-callable local bridge, second writer는 제공하거나 제안하지 않습니다.

`use_figma`를 실제 호출할 때마다 먼저 `figma:figma-use`를 invoke하고 해당 tool call의 `skillNames`에 `figma-use`를 포함합니다. composed screen/view는 `figma:figma-use`와 `figma:figma-generate-design`, component/library는 `figma:figma-use`와 `figma:figma-generate-library`를 함께 invoke합니다. motion 등 추가 official prerequisite는 current installed contract가 요구할 때 함께 적용합니다. 읽기 전용 audit도 `use_figma`를 호출하면 같은 규칙을 따릅니다. prerequisite 또는 capability가 설치·노출되지 않으면 tool/API를 가정하거나 우회하지 않고 `blocked`, `not_run` 또는 `inconclusive`로 보고합니다.

화면과 composed view에는 `figma-product-design`, prototype reaction에는 `figma-prototype-flow`, 읽기 전용 검토에는 `figma-design-audit`을 사용합니다. component/library authoring은 `figma:figma-generate-library`, design-to-code는 `figma:figma-design-to-code`의 범위입니다.

## Deterministic Desktop companion

[Figma Workflow Companion](figma-plugin/README.md)은 Codex writer가 아니라 사용자가 Figma Desktop에서 직접 실행하는 수동 companion입니다. 반복적이고 결과가 명확한 version `1` allowlisted JSON 작업만 지원하며 arbitrary JavaScript를 실행하지 않습니다.

- read-only: `inspect-selection`, `audit-auto-layout`, `audit-prototype-links`
- mutation: `rename-exact`, `replace-icon-instance-exact`

mutation은 explicit `nodeId`, expected state, same-plan preview receipt, apply 직전 re-read와 readback을 요구합니다. preview receipt는 UI memory에만 있고 입력 변경 또는 plugin 종료 시 폐기됩니다. schema, reason code, partial failure, `PREVIEW_REQUIRED`, `PLAN_CHANGED`, `PREVIEW_NOT_READY`, `READBACK_FAILED`의 의미는 [deterministic execution](references/deterministic-execution.md)과 [companion README](figma-plugin/README.md)를 따릅니다. companion manifest는 [figma-plugin/manifest.json](figma-plugin/manifest.json)이며 network access를 허용하지 않습니다.

## Evidence와 검증 상태

visual screenshot, native structure/readback, component·variable·icon provenance, reaction readback, prototype playback은 서로 다른 claim을 검증합니다. 하나의 screenshot이나 write response만으로 전체를 통과로 보고하지 않습니다. capability가 없으면 `blocked`, `inconclusive` 또는 `not_run`으로 범위를 분리합니다.

이 repository의 정적 검증은 packaging, schema, test와 bundle을 확인합니다. actual Figma MCP exposure, live canvas mutation, Figma Desktop import와 companion 실행은 별도 환경에서 해야 하며 실행하지 않았다면 `not_run`입니다.

출처와 consulted-only provenance는 [UPSTREAM.md](UPSTREAM.md)에 있습니다.
