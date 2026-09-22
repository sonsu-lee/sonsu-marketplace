# 마켓플레이스 아키텍처

- Status: Current
- Last reviewed: 2026-09-23

## 목적

Sonsu Marketplace는 Codex·Oh My Pi(OMP)의 기본 동작을 복제하지 않습니다. host가 이미 제공하는
계획, 구현, 디버깅, 테스트, Git, 웹 조사, 언어 교정, memory와 session continuity 위에 도메인 판단
기준 또는 외부 artifact 계약이 필요한 얇은 capability pack만 제공합니다.

## 정본과 로딩 경계

| 경로 | 책임 |
| --- | --- |
| `.agents/plugins/marketplace.json` | Codex용 10개 plugin source |
| `.omp-plugin/marketplace.json` | 같은 10개 이름·version·path의 OMP projection |
| `plugins/<name>/.codex-plugin/plugin.json` | package identity와 공통 skill entrypoint; 필요한 Codex-only metadata |
| `plugins/<name>/skills/` | 두 host가 공유하는 31개 skill |
| `plugins/<name>/UPSTREAM.md` | 포함하거나 검토한 upstream과 로컬 차이 |
| `shared/design-quality/` | UI/Figma pack이 package 내부 copy로 배포하는 공통 품질 계약의 정본 |
| `evals/` | 정적 계약, model-free loader probe와 behavior smoke fixture |

```text
Codex: .agents/plugins/marketplace.json
  → ./plugins/<name>/.codex-plugin/plugin.json
  → shared skills + Codex-only apps/MCP metadata

OMP: .omp-plugin/marketplace.json
  → metadata.pluginRoot + source
  → shared skills; OMP-native LSP/tooling
```

모든 package는 version `1.0.0`이며 독립 설치됩니다. manifest dependency, 공통 router, setup skill,
고정 model roster와 task-continuity hook은 없습니다.

## Capability pack

| Pack | 소유하는 capability |
| --- | --- |
| Code Review | focused code-quality 관점과 명시적 3-reviewer PR review/publish protocol |
| Code Intelligence | semantic definition/reference/type/rename; native LSP 우선, Codex MCP fallback |
| Workflow | ticket·PR artifact, provider 상태 조회와 복구 |
| Developer Writing | 근거 상태를 보존하는 개발자 블로그·기술 글 |
| Prompting | 재사용할 prompt artifact |
| Product | discovery, evidence synthesis, domain rules, experiment와 PRD |
| Figma Workflow | Figma native 화면·prototype·audit |
| Interface Design | 일반 UI proposal·implementation 설계와 재설계 |
| Operations UI | 운영 업무 UI 설계·재설계·audit와 요청된 Figma handoff |
| Design Patterns | forces 기반 pattern 선택과 explicit usage review |

Code Review는 일반 구현 lifecycle을 소유하지 않고, Workflow는 branch/commit 기본 동작을 재정의하지
않습니다. Product의 `to-prd`는 PRD만 작성하며 issue 생성은 Workflow입니다. `review-pr`은 explicit
호출만 허용하고 일반 “코드 리뷰”는 host-native review에 남깁니다.

Figma `apps` metadata와 Code Intelligence `codex-mcp.json`은 Codex manifest에만 있습니다. OMP는
그 metadata를 받지 않고 현재 host의 official Figma capability와 native `lsp`를 사용합니다.

## 상태 변경 경계

Plugin 설치, remote ticket/PR 변경, review 게시, Figma mutation과 code intelligence rename은 서로
별도의 상태 변경입니다. 선택된 skill은 권한을 만들지 않으며 사용자 요청과 host approval을 따릅니다.
마켓플레이스는 cache, `.sonsu/continuity` 또는 `.engineering` artifact를 자동 이동·삭제하지 않습니다.

결정 근거는 [ADR 0015](../decisions/0015-use-thin-capability-packs.md), 정확한 라우팅은
[스킬 라우팅](skill-routing.md), package 작성 규칙은 [개발 가이드](../guides/adding-a-plugin.md)에 있습니다.
