# 스킬 라우팅

- Status: Current
- Last reviewed: 2026-09-23

## 첫 번째 규칙: host baseline

일반 계획·구현·디버깅·테스트·Git branch/commit·웹 조사·언어 교정·memory·session 재개는 Codex 또는
OMP의 기본 동작으로 처리합니다. marketplace skill은 아래 표의 도메인 판단이나 외부 artifact 계약을
직접 요청한 경우에만 선택합니다. skill 선택은 수정·게시·remote action 권한이 아닙니다.

자연어 요청은 skill description의 목적·대상·산출물·negative trigger에 따라 선택하고 명시적 호출을
우선합니다. 별도 router, setup skill, model roster, managed evidence gate 또는 continuity hook은 없습니다.
여러 capability가 필요하면 현재 설치된 skill을 runtime에서만 조합하며 plugin dependency를 만들지 않습니다.

## 정확한 ownership matrix

| 직접 목적 | 담당 skill |
| --- | --- |
| 명시적으로 요청한 3-reviewer PR review와 COMMENT 게시 | `code-review:review-pr` |
| 도달 가능한 실패 경로 review | `code-review:review-failure-modes` |
| reader load·유지보수성 review | `code-review:review-maintainability` |
| error ownership·logging·운용성 review | `code-review:review-operability` |
| diff·commit·branch의 over-engineering review | `code-review:review-overengineering` |
| repository/큰 경로의 over-engineering audit | `code-review:audit-overengineering` |
| definition/reference/type/implementation/rename 등 semantic code intelligence | `code-intelligence:semantic-code-intelligence` |
| PR 상태·CI·review·미해결 대화 조회 | `workflow:inspect-prs` |
| 지정 PR의 충돌·review 지적·CI 실패 복구 | `workflow:repair-pr` |
| ticket·issue·backlog 초안 또는 게시 | `workflow:to-ticket` |
| 기존 ticket의 lifecycle·assignee·native relation 변경 | `workflow:ticket-lifecycle` |
| 현재 branch의 GitHub PR 초안 또는 게시 | `workflow:to-pr` |
| 개발자 블로그·TIL·debugging 회고·기술 선택 글 | `developer-writing:write-developer-blog` |
| Codex·ChatGPT·OpenAI API용 prompt artifact | `prompting:prompt-builder` |
| 제품 사용자·문제·결과·범위 discovery | `product:product-discovery` |
| interview·feedback·issue·metric evidence synthesis | `product:synthesize-product-evidence` |
| 제품 용어·상태·사건·규칙·예외 탐색 | `product:product-domain-discovery` |
| 제품 hypothesis의 실행 전 test 설계 | `product:design-product-test` |
| 실행된 product test 판정 | `product:assess-product-test` |
| 승인된 제품 결정을 PRD로 변환 | `product:to-prd` |
| Figma native 제품 화면·responsive layout | `figma-workflow:figma-product-design` |
| Figma prototype connection·overlay·state flow | `figma-workflow:figma-prototype-flow` |
| 기존 Figma artifact의 read-only audit | `figma-workflow:figma-design-audit` |
| 일반 웹·앱의 새 UI 설계 | `interface-design:design-interface` |
| 일반 웹·앱의 기존 UI 재설계 | `interface-design:redesign-interface` |
| 신규 운영형 B2B/admin/back-office UI | `operations-ui:design-operations-ui` |
| 기존 운영 UI 재설계 | `operations-ui:redesign-operations-ui` |
| 기존 운영 UI와 evidence의 read-only audit | `operations-ui:audit-operations-ui` |
| 요청된 운영 Figma flow와 implementation handoff | `operations-ui:figma-operations-flow` |
| 실제 forces에 맞는 named pattern 선택 | `design-patterns:select-design-patterns` |
| 명시적으로 요청한 pattern usage read-only review | `design-patterns:review-pattern-usage` |

## Negative routing

- 일반 “코드 리뷰해 줘”, PR URL만 있는 입력, 현재 diff의 broad review → host-native review. `review-pr`은
  `$review-pr`, OMP `/skill:review-pr` 또는 같은 의미의 명시적 호출에서만 실행합니다.
- 일반 기능 구현·버그 수정·test 작성·refactor → host baseline. Code Review/Design Patterns를 자동 추가하지 않습니다.
- branch/commit/push → host baseline. ticket·PR artifact가 없으면 Workflow를 선택하지 않습니다.
- 웹 조사·공식 문서 확인 → host browser/search. Product evidence synthesis나 Developer Writing을 자동 선택하지 않습니다.
- 일반 문장 교정·번역 → host baseline. Developer Writing은 개발자 글 산출물일 때만 선택합니다.
- memory 정리·작업 재개 → host baseline. marketplace skill이 없습니다.
- Product의 `to-prd`는 PRD만 반환합니다. issue/PR 게시가 추가로 요청되면 별도 Workflow 단계입니다.
- Code Intelligence는 semantic 질문만 소유합니다. 단순 text search에는 선택하지 않고, LSP가 없으면 grep으로
  성공을 모사하지 않습니다.
- Figma capability가 노출되지 않았으면 API나 writer를 추정하지 않고 `blocked`/`not_run`으로 끝냅니다.

## 선택적 runtime 조합

조합은 요청이 실제로 두 산출물을 요구할 때만 사용합니다.

```text
제품 합의 + PRD 게시 ticket
  → product:to-prd
  → workflow:to-ticket

운영 화면의 Figma artifact + 구현
  → operations-ui:figma-operations-flow 또는 figma-workflow의 직접 산출물
  → operations-ui:design-operations-ui의 implementation scope

PR 실패 복구 + focused review
  → workflow:repair-pr
  → 사용자가 요청한 code-review 관점
```

각 단계는 독립 결과·권한·실패 상태를 유지합니다. 한 단계의 성공을 다른 단계의 설치, 실행 또는
검증으로 간주하지 않습니다.

## Semantic code intelligence host 경계

`semantic-code-intelligence`는 current host의 native `lsp`를 먼저 사용합니다. OMP에서는 native LSP만
사용합니다. Codex에서 native LSP가 없고 plugin MCP가 실제 노출된 경우에만 pinned `mcpls 0.6.0`을
fallback으로 사용합니다. project config trust, canonical cwd와 workspace root를 확인한 후 language
server를 시작합니다. write operation은 사용자가 요청한 rename/code action에만 허용하고 preview와
approval을 거칩니다.

## UI/Figma 품질 계약

Interface Design, Operations UI와 Figma Workflow는 같은 DQ0–DQ8 vocabulary를 사용하지만 package별
산출물 scope를 유지합니다. 한 author run과 관계가 명시된 최소 한 evaluator score로 DQ1–DQ6를
판정할 수 있습니다. 여러 evaluator가 있으면 minimum score를 사용하고 finding 불일치는
`inconclusive`입니다. Figma capability와 native artifact readback은 host가 실제 노출한 도구로만 확인합니다.
