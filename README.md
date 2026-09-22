# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

Codex와 Oh My Pi(OMP)의 기본 계획·구현·디버깅·검증 위에 도메인 판단 기준과 외부 artifact 계약만
더하는 얇은 capability pack 모음입니다. 필요한 pack만 설치합니다.

## 설치

### Codex

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
codex plugin add code-review@sonsu-marketplace
codex plugin list --marketplace sonsu-marketplace
```

### Oh My Pi

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install --scope project code-review@sonsu-marketplace
omp plugin discover sonsu-marketplace
```

목적에 맞춰 `code-review`, `workflow`, `code-intelligence`, `product` 또는 UI pack을 선택하세요.
일반 기능 구현, 디버깅, 테스트, branch/commit, 웹 조사, 언어 교정과 session 재개에는 marketplace
plugin이 필요하지 않습니다.

`code-intelligence`는 자동 installer를 실행하지 않습니다. Codex에서 사용할 때에는 plugin과 별도로
PATH에 exact `mcpls 0.6.0`과 대상 언어 server를 설치해야 합니다. OMP는 host-native `lsp`와 대상
언어 server를 사용하며 mcpls MCP를 시작하지 않습니다. 언어 server는 project code/config를 실행할
수 있으므로 신뢰한 workspace에서만 enable하세요. prerequisite가 없으면 text-search fallback 없이
`blocked`로 끝납니다.

## 플러그인

모든 plugin version은 `1.0.0`입니다.

| 플러그인 | 용도 | Skills |
| --- | --- | --- |
| [Code Review](plugins/code-review/README.md) | focused read-only review와 직접 호출형 PR review | `review-pr`, `review-failure-modes`, `review-maintainability`, `review-operability`, `review-overengineering`, `audit-overengineering` |
| [Code Intelligence](plugins/code-intelligence/README.md) | definition/reference/type/rename 등 semantic LSP 작업 | `semantic-code-intelligence` |
| [Workflow](plugins/workflow/README.md) | ticket·PR artifact와 provider 상태 조회·복구 | `inspect-prs`, `repair-pr`, `to-ticket`, `ticket-lifecycle`, `to-pr` |
| [Developer Writing](plugins/developer-writing/README.md) | 근거 기반 개발자 블로그·기술 글 | `write-developer-blog` |
| [Prompting](plugins/prompting/README.md) | 복사 가능한 prompt artifact | `prompt-builder` |
| [Product](plugins/product/README.md) | 제품 탐색·근거·도메인·검증·PRD | `product-discovery`, `synthesize-product-evidence`, `product-domain-discovery`, `design-product-test`, `assess-product-test`, `to-prd` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figma 화면·prototype 제작과 audit | `figma-product-design`, `figma-prototype-flow`, `figma-design-audit` |
| [Interface Design](plugins/interface-design/README.md) | 일반 UI 설계·재설계 | `design-interface`, `redesign-interface` |
| [Operations UI](plugins/operations-ui/README.md) | 운영 UI 설계·재설계·audit·Figma flow | `design-operations-ui`, `redesign-operations-ui`, `audit-operations-ui`, `figma-operations-flow` |
| [Design Patterns](plugins/design-patterns/README.md) | pattern 선택과 explicit usage review | `select-design-patterns`, `review-pattern-usage` |

Codex와 OMP는 같은 31개 `skills/`를 읽습니다. Codex manifest만 Figma `apps`와 Code Intelligence의
`codex-mcp.json`을 선언합니다. OMP catalog에는 두 connector metadata를 투영하지 않습니다.

## 사용 예시

- “이 변경의 도달 가능한 실패 경로를 검토해 줘.” → `code-review:review-failure-modes`
- “`$review-pr` 이 PR을 세 독립 reviewer로 검토해 COMMENT를 게시해 줘.” → explicit `review-pr`
- “이 symbol의 정의와 모든 reference를 LSP로 찾아 줘.” → `semantic-code-intelligence`
- “이 PR의 CI 실패를 수정해 줘.” → `workflow:repair-pr`
- “승인된 결정을 PRD 초안으로 만들어 줘.” → `product:to-prd`
- “운영 화면을 수정 없이 감사해 줘.” → `operations-ui:audit-operations-ui`

일반 “코드 리뷰해 줘”는 host-native review가 처리하며 `review-pr`을 자동 선택하지 않습니다.

## Major migration

이전 catalog 이름에는 alias나 wrapper가 없습니다. 기존 설치를 먼저 제거하고 필요한 새 pack만
설치하세요.

```sh
codex plugin remove engineering@sonsu-marketplace
codex plugin remove research@sonsu-marketplace
codex plugin remove fluent-languages@sonsu-marketplace
codex plugin remove memory-manager@sonsu-marketplace
codex plugin remove writing@sonsu-marketplace

omp plugin uninstall --scope <scope> engineering@sonsu-marketplace
omp plugin uninstall --scope <scope> research@sonsu-marketplace
omp plugin uninstall --scope <scope> fluent-languages@sonsu-marketplace
omp plugin uninstall --scope <scope> memory-manager@sonsu-marketplace
omp plugin uninstall --scope <scope> writing@sonsu-marketplace
```

기존 cache, `.sonsu/continuity`와 `.engineering` artifact를 자동 이동·삭제하지 않습니다.

## 업데이트

```sh
codex plugin marketplace upgrade sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade --scope project code-review@sonsu-marketplace
```

업데이트 뒤 Codex는 새 작업을 시작하고 OMP는 `/reload-plugins` 또는 새 session으로 catalog를
다시 읽습니다.

## 문서와 출처

- [아키텍처와 routing](docs/README.md)
- [플러그인 개발 가이드](docs/guides/adding-a-plugin.md)
- [라이선스와 출처](docs/reference/licenses-and-sources.md)
- [평가](evals/)

저장소 전체에 공통 root license는 선언하지 않았습니다. 각 package의 license와 provenance를
확인하세요.
