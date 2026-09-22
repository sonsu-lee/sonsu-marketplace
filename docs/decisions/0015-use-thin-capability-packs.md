# 0015 Use Thin Capability Packs

- Status: Accepted
- Date: 2026-09-16
- Supersedes: 0004, 0007, 0009, 0011, 0012, 0014
- Approval: 사용자가 현재 대화에서 이 결정과 clean cutover 구현 계획을 승인했습니다.

## Context

Codex와 OMP는 일반 계획, 구현, 디버깅, 테스트, 병렬 작업, worktree, 완료 검증, Git, 웹 조사,
문서·언어 교정, 세션 연속성과 메모리 관리를 이미 제공합니다. 마켓플레이스가 같은 실행 운영체계를
다시 정의하면 host 정책과 plugin 정책이 겹치고, 모델·도구·권한·세션 계약이 바뀔 때 두 번째
운영체계를 함께 유지해야 합니다.

이 저장소가 계속 제공할 고유 가치는 범용 agent lifecycle이 아니라 도메인 판단 기준, 외부
artifact 계약, provider의 실제 mutation/readback, 그리고 사용자가 명시적으로 호출하는 고비용
workflow입니다. Codex와 OMP는 같은 전문 `skills/`를 읽을 수 있지만 connector와 MCP metadata는
host별 manifest 능력에 맞게 달라야 합니다.

설계 참고로 다음 고정 snapshot을 검토했습니다.

- `ggombee/code-forge@1779c8ac9638c755d341b16e708f7e44aaf15b75`: lazy loading,
  opt-in external MCP, local observability 경계만 참고합니다. MIT 라이선스와 무관하게 `/setup`,
  `/start`, model routing, state, quality/permission hooks, stack module 생성기는 이식하지 않습니다.
  `.mcp.json`의 placeholder secret·raw PAT·floating `npx -y`, 제거된 `codex mcp-server`, Bellows의
  추정 duration/success와 raw session/project logging도 복사하지 않습니다.
- `kdy1/kdy1-scripts@92a8fbe9a57bce5064ed7dba3a8f87f331930dc6`: 확인한 snapshot에
  root license가 없으므로 좁고 독립적이며 명시적으로 호출되는 workflow 구조만 관찰 사실로
  인용합니다. 그 저장소의 문구, 코드, script와 template은 배포물에 포함하지 않습니다.

## Decision

### Ownership boundary

일반 계획·구현·디버깅·테스트·병렬 작업·worktree·완료 검증·일반 Git·일반 웹 조사·일반
문서/언어 교정·세션 연속성·메모리 관리는 Codex/OMP 기본 동작에 맡깁니다. 마켓플레이스는 다음만
소유합니다.

1. 특정 도메인에서 결과를 판정하는 기준과 evidence 계약
2. ticket, PR, PRD, prompt, Figma artifact처럼 외부로 전달되는 산출물 계약
3. 실제 provider mutation 전에 target과 권한을 확인하고 mutation 뒤 readback하는 절차
4. 사용자가 직접 호출한 `review-pr`처럼 비용과 실패 의미가 명시된 workflow

범용 router, setup generator, fixed model roster, continuity engine, 자동 quality/telemetry hook,
provider 자동 설치를 만들지 않습니다. 외부 capability는 optional MCP로 격리하고 운영 데이터는
host/operator가 명시적으로 retention과 export를 선택하도록 합니다.

### Catalog contract

모든 retained/new plugin version은 `1.0.0`입니다. 아래 10개 plugin과 31개 skill만 배포합니다.

| Plugin | Skills |
| --- | --- |
| `code-review` | `review-pr`, `review-failure-modes`, `review-maintainability`, `review-operability`, `review-overengineering`, `audit-overengineering` |
| `code-intelligence` | `semantic-code-intelligence` |
| `workflow` | `inspect-prs`, `repair-pr`, `to-ticket`, `ticket-lifecycle`, `to-pr` |
| `developer-writing` | `write-developer-blog` |
| `prompting` | `prompt-builder` |
| `product` | `product-discovery`, `synthesize-product-evidence`, `product-domain-discovery`, `design-product-test`, `assess-product-test`, `to-prd` |
| `figma-workflow` | `figma-product-design`, `figma-prototype-flow`, `figma-design-audit` |
| `interface-design` | `design-interface`, `redesign-interface` |
| `operations-ui` | `design-operations-ui`, `redesign-operations-ui`, `audit-operations-ui`, `figma-operations-flow` |
| `design-patterns` | `select-design-patterns`, `review-pattern-usage` |

`engineering`, `research`, `fluent-languages`, `memory-manager`, `writing`은 compatibility alias,
deprecated wrapper, re-export나 stub 없이 catalog에서 제거합니다. `developer-writing`은 일반 글쓰기가
아니라 개발자 블로그 산출물만 소유합니다. `product:to-prd`는 PRD 문서만 만들고 issue 생성은
별도 `workflow:to-ticket` 책임입니다.

### Host-specific execution boundary

두 host는 같은 skill 본문을 사용합니다. Codex manifest만 Figma app connector와
`code-intelligence`의 non-autodiscovered `codex-mcp.json`을 선언합니다. OMP는 native `lsp`를
사용하며 별도 MCP나 LSP process를 배포하지 않습니다. semantic code intelligence는 신뢰된 단일
workspace 안에서만 동작하고, matching client가 없을 때 text search로 의미론을 추정하지 않습니다.

`review-pr`은 자동 routing되지 않는 explicit workflow입니다. 정확히 세 fresh reviewer가 같은
locked diff를 독립적으로 읽고 coordinator가 검증·중복 제거한 한 개의 `COMMENT` review만
게시합니다. head SHA 변화, reviewer 실패, 불완전한 ambiguous readback은 약한 workflow나 중복
POST로 대체하지 않습니다.

언어 server와 외부 connector는 프로젝트 코드를 실행하거나 외부 데이터를 바꿀 수 있습니다.
plugin은 이를 자동 설치·활성화하지 않고 현재 workspace trust, host approval, provider permission을
그대로 따릅니다. plugin 자체 log, telemetry event나 고정 retention을 만들지 않습니다. host log와
collector의 접근·보존·삭제는 operator 책임이며 plugin은 redaction이나 hard erasure를 보장하지
않습니다.

## Alternatives Considered

- 기존 Engineering 운영체계를 host 위에 유지: 이전 workflow를 보존하지만 session, model,
  delegation, quality gate와 continuity가 host 기능과 계속 충돌합니다.
- 범용 router 하나로 모든 plugin 조합: 선택은 중앙화되지만 일반 요청까지 marketplace가
  가로채고 전문 pack 독립성이 깨집니다.
- connector와 MCP를 두 host에 동일 투영: manifest는 단순해지지만 OMP native LSP와 중복
  process가 생기고 host별 trust·approval 경계를 흐립니다.
- 이전 이름 alias를 한 release 유지: migration은 쉬워지지만 duplicate skill routing과 obsolete
  hook/script가 계속 배포됩니다.

## Consequences

일반 요청은 host baseline 하나만 따르고, 전문 산출물이 필요할 때만 작은 capability pack을
설치합니다. Codex와 OMP의 이름·version·공통 skill inventory는 같고 host-specific connector만
manifest에서 분리됩니다. 제거된 plugin 설치와 local artifact는 자동 이동하거나 삭제하지 않으며
사용자가 이전 plugin을 제거하고 필요한 pack을 새로 설치해야 합니다.

고정 workflow와 자동 continuity를 잃는 대신 host 개선을 그대로 받습니다. semantic LSP,
Figma/provider mutation, explicit PR review는 prerequisite나 fresh reviewer가 없으면 `blocked` 또는
`incomplete`로 끝나며 더 약한 fallback을 제공하지 않습니다. 실제 catalog, loader, routing,
protocol과 design-domain gate는 model-free contract test와 격리된 native probe로 검증합니다.

## Revisit When

Codex와 OMP가 공통 connector manifest, 안전한 plugin rename/migration, workspace trust signal 또는
idempotent provider mutation receipt를 공식 제공할 때 이 결정을 재검토합니다. 일반 host 기능과
전문 pack 사이에 반복적인 누락이 실제 routing trace에서 확인될 때만 ownership 경계를 넓힙니다.
