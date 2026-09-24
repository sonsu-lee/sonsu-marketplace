# Figma Workflow

Figma Design에서 제품 화면, responsive Auto Layout, component·variant·variable, exact icon과 clickable prototype을 생성·수정·감사할 때 native 구조와 evidence 기준을 제공하는 Codex plugin입니다. 판단이 필요한 canvas read/write의 agent writer는 현재 host에 실제로 등록된 official Figma MCP connection 하나입니다.

Figma 화면도 `사용자·맥락 → 판단/과업 → 정보 → 표현 → 상태/interaction → 증거`의 공통 Design
Decision Contract를 사용합니다. Figma scope는 DQ0–DQ7을 요구하며 DQ1–DQ6은 독립 평가자 2명의
최솟값으로 판정합니다. 이 통과를 production runtime이나 live 사용자 성과로 확대하지 않습니다.

```sh
codex plugin add figma-workflow@sonsu-marketplace
```

Codex manifest의 `apps`는 official Figma connector discovery용 metadata입니다. 설치만으로 canvas
access가 생겼다고 간주하지 않습니다.

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

[Figma Workflow Companion](figma-plugin/README.md)은 agent writer가 아니라 사용자가 Figma Desktop에서 직접 실행하는 수동 companion입니다. 반복적이고 결과가 명확한 version `1` allowlisted JSON 작업만 지원하며 arbitrary JavaScript를 실행하지 않습니다.

- read-only: `inspect-selection`, `audit-auto-layout`, `audit-prototype-links`
- mutation: `rename-exact`, `replace-icon-instance-exact`

mutation은 explicit `nodeId`, expected state, same-plan preview receipt, apply 직전 re-read와 readback을 요구합니다. preview receipt는 UI memory에만 있고 입력 변경 또는 plugin 종료 시 폐기됩니다. schema, reason code, partial failure, `PREVIEW_REQUIRED`, `PLAN_CHANGED`, `PREVIEW_NOT_READY`, `READBACK_FAILED`의 의미는 [deterministic execution](references/deterministic-execution.md)과 [companion README](figma-plugin/README.md)를 따릅니다. companion manifest는 [figma-plugin/manifest.json](figma-plugin/manifest.json)이며 network access를 허용하지 않습니다.

## Evidence와 검증 상태

visual screenshot, native structure/readback, component·variable·icon provenance, reaction readback, prototype playback은 서로 다른 claim을 검증합니다. 하나의 screenshot이나 write response만으로 전체를 통과로 보고하지 않습니다. capability가 없으면 `blocked`, `inconclusive` 또는 `not_run`으로 범위를 분리합니다.

이 repository의 정적 검증은 packaging, schema, test와 bundle을 확인합니다. actual Figma MCP exposure, live canvas mutation, Figma Desktop import와 companion 실행은 별도 환경에서 해야 하며 실행하지 않았다면 `not_run`입니다.

```bash
python3 scripts/validate_design_quality.py contract <contract.json>
python3 scripts/validate_design_quality.py report <report.json> <contract.json>
```

출처와 consulted-only provenance는 [UPSTREAM.md](UPSTREAM.md)에 있습니다.

## 컴팩션 후 작업 재개

[작업 연속성 참고 자료](references/continuity.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 참고 자료·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 참고 자료를
읽고 수동으로 재개할 수 있습니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고하세요.

## 일반·운영 UI 디자인과 조합

일반 UI의 과업·정보 구조는 Interface Design, 운영 업무 기준은 Operations UI가 담당할 수 있습니다.
Figma 파일 자체의 제작·구조·프로토타입은 이 플러그인이 중심이며 다른 플러그인 설치를 요구하지
않습니다. 혼합 요청은 기존 명세와 승인 범위를 이어받아 Figma를 정본으로 제작·검증합니다.
Figma-only 요청에 코드 구현이나 브라우저 검증을 새 완료 조건으로 추가하지 않습니다.
