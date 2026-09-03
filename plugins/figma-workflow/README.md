# Design

Figma와 Paper Design에서 제품 화면을 생성·수정·감사할 때 native 구조와 실제 검증 기준을
적용하는 개인용 Codex 플러그인입니다.

## 스킬

| 스킬 | 책임 |
| --- | --- |
| `figma-product-design` | Figma 제품 화면의 생성·수정, responsive layout, reusable structure와 exact assets |
| `figma-prototype-flow` | Figma control의 실제 reaction, overlay, 상태 분기와 prototype playback |
| `figma-design-audit` | 기존 Figma artifact의 구조, design-system 사용, resizing, interaction과 handoff에 대한 읽기 전용 감사 |
| `paper-product-design` | Paper의 flex·DOM·token 기반 화면 생성·수정·감사와 code roundtrip |

## 도구 경계

- 제품 화면과 실제 클릭 동선은 Figma Design을 사용합니다.
- 협업용 초기 user journey와 workshop board는 FigJam을 사용합니다.
- AWS, network, UML, ERD와 system architecture는 draw.io를 사용합니다.
- HTML/CSS 구조와 code roundtrip 중심의 화면 탐색은 Paper Design을 사용합니다.

이 플러그인은 공식 Figma 스킬, Paper MCP나 draw.io를 포함하거나 자동 설치하지 않습니다. 현재
환경의 capability를 확인해 사용할 수 있는 provider와 runtime에서 조합하며, capability가 없으면
실행하지 않은 작업을 `not_run` 또는 `blocked`로 보고합니다.

실제 Figma 화면 생성·수정에는 공식 `figma-generate-design`과 `figma-use`, 개별 component와 library
authoring에는 `figma-generate-library`를 사용합니다. Design의 로컬 스킬은 Auto Layout, exact asset,
interaction과 evidence 품질 계약을 보완하며 공식 workflow를 대체하지 않습니다.

Skill은 model이나 reasoning effort를 자동 변경하지 않습니다. 작업별 잠정 model 선택, 승격 순서,
custom agent와 local Figma plugin 도입 조건은
[execution architecture](references/execution-architecture.md)에 기록합니다.

## 검증 원칙

Figma에서는 screenshot, node structure와 prototype playback을 서로 다른 근거로 검증합니다.
Paper에서는 screenshot, DOM/tree, computed styles와 JSX를 분리해 확인합니다. 정적 fixture와
manifest parsing은 실제 모델 routing이나 live canvas 동작을 증명하지 않습니다.

출처와 재사용 범위는 [UPSTREAM.md](UPSTREAM.md)에 기록합니다.
