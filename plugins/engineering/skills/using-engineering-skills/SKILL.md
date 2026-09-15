---
name: using-engineering-skills
description: 개발 작업을 시작하거나 작업 성격이 바뀔 때 Engineering의 설계·구현·디버깅·리뷰 경로와 필요한 검증을 선택한다.
---

# Engineering 진입점

요청의 목적, 승인 범위, 현재 계약과 실패 영향을 확인한다. 구체적인 작업을 위임받았으면 그
작업의 brief와 해당 스킬부터 수행한다. 일반 코드 리뷰도 Engineering의 책임이다.

| 요청 | 진입점 |
| --- | --- |
| 코드·diff·commit·branch 일반 리뷰 | `engineering:review-quality` |
| 불필요한 복잡성·유지보수·실패 경로·운영성 중 특정 관점 리뷰 | 해당 `review-*` 스킬 |
| 독립된 PR 심층·다중 리뷰 | `engineering:review-pr` |
| 개발 단계의 독립 리뷰 또는 PR 이외의 명시적 독립 리뷰 | `engineering:requesting-code-review` |
| 도메인 계약을 타입·상태·경계에 반영 | `engineering:domain-shaped-code` |
| 현재 코드를 단순화 | `engineering:simplify-code` |
| 범위·요구·설계 결정 | `engineering:brainstorming` |
| 여러 작업의 의존성과 검증 계획 | `engineering:writing-plans` |
| 승인된 작업 실행·재개 | `engineering:executing-plans` |
| 원인이 불명확한 오류 | `engineering:systematic-debugging` |
| 리뷰 피드백 검증 | `engineering:receiving-code-review` |
| 완료 보고 | `engineering:verification-before-completion` |
| 스킬 작성·수정 | `engineering:writing-skills` |

일반 리뷰는 구현 계획·소스 수정으로 확장하지 않는다. 여러 단계의 변경은
[품질 게이트](references/quality-gates.md)에 따라 위험을 분류한다. 기계적 변경은 결정론적 검사,
동작 변경은 독립 리뷰, 고위험 계약은 별도 red-team을 추가한다. 파일 수나 계획 파일 존재로
위험을 정하지 않는다. 현재 근거를 다시 확인하되 재개 자체를 위험 증가로 취급하지 않는다.

## 독립 산출물과 자동 선택

스킬 이름을 지정하지 않은 요청도 description의 시작·제외 조건으로 선택한다. 명시적 호출은
우선하고 이름 지정 자체로 쓰기 권한을 확대하지 않는다. 별도의 만능 router를 만들지 않는다.
PR 상태 조회·복구, 독립적인 심층 PR 리뷰, 일반 UI 설계·재설계는 해당 설치된 전문 스킬이
있으면 바로 시작한다. PR URL만 있는 일반 리뷰는 심층 리뷰로 승격하지 않는다. 웹/앱 설계와
운영 업무·Figma 파일 편집의 목적을 구분하고, 전체 개발 절차가 요청된 경우에만 필요한 단계를
조합한다. 기존에 선언한 필수 검증을 독립 스킬로 임의 대체하지 않는다.

구현에는 [공통 코드 품질](../../references/code-quality.md)을 적용한다. 도메인 발견은 Product,
확정한 규칙의 타입·코드 구현은 Engineering, Git·티켓·PR 전달은 Workflow가 소유한다.
다른 전문 플러그인은 해당 작업이 필요할 때만 호출한다.

[실행 계약](references/agent-execution.md)은 위임·문맥·모델 선택을,
[Codex 대응](references/codex-tools.md)은 현재 도구 사용을,
[관리형 게이트](references/evidence-gates.md)는 등록한 단계의 전이를 다룬다.
주 조정자는 여러 단계의 진행을 [task-continuity](../task-continuity/SKILL.md)에 기록한다.

사용자 지시와 프로젝트 권한을 우선한다. 구현 승인 안의 탐색·내부 선택·수정·검증은 계속한다.
설계·리뷰만 요청받았으면 해당 산출물까지 완성한다. 새 제품 규칙이나 명시적 확인 조건에
의존하는 작업만 사용자 결정을 기다린다. Git·외부 전달 권한은
[전달 권한](../../references/delivery-authority.md)을 따른다.
