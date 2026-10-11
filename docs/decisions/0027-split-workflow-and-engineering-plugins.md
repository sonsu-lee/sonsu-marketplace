# ADR 0027: Workflow·Engineering을 Git·Tickets·Review·Dev Workflow로 분리

- 날짜: 2026-10-11
- 상태: 채택
- 관련 결정: [ADR 0015](0015-independent-skills.md), [ADR 0024](0024-distribute-writing-research-prompting-product-to-omp.md), [ADR 0025](0025-merge-engineering-review-entry-points.md)(이 결정으로 대체)

## 배경

Workflow는 Git 전달·티켓·PR 작성을, Engineering은 개발 절차와 코드 리뷰를 함께 담았다. omp 기본
배포에는 Workflow만 들어 있어 리뷰 기준을 omp에서 쓸 수 없었고, Engineering을 설치하면 쓰지 않는
개발 게이트·역할 agent까지 함께 설치됐다. 티켓·PR·커밋·리뷰 규칙도 여러 파일에 흩어져 같은 기준을
여러 곳에서 고쳐야 했다. 규칙의 근거를 Linear·Bugzilla·GitHub 문서·Google eng-practices·Conventional
Commits 원문으로 다시 정리하면서([근거 문서](../reference/ticket-pr-review-sources.md)), 문서 종류별 책임에
맞춰 플러그인 경계를 다시 나눴다.

## 결정

- 플러그인을 넷으로 나눈다.
  - `git`: `branch`, `commit`, `push`, `write-pr`, `inspect-prs`, `repair-pr`
  - `tickets`: `write-ticket`, `update-ticket`
  - `review`: `review-code`, `review-overengineering`, `review-maintainability`, `review-operability`,
    `review-failure-modes`, `audit-overengineering`, `address-review`
  - `dev-workflow`: 개발 절차 스킬 10개
- omp 기본 배포는 `git`, `tickets`, `review`, `fluent-korean`, `fluent-english`, `fluent-japanese`,
  `design` 7개다. `dev-workflow`는 omp에 배포하지 않는다.
- 여러 플러그인이 같이 쓰는 기준은 `shared/review-core`, `shared/delivery-writing`에 정본 하나로 두고
  `scripts/render-shared-files.py`가 각 플러그인에 복사한다. 플러그인끼리는 링크하지 않는다.
- PR 리뷰 코멘트 대응(조회·수정 push·답글·대화 해결)은 `git`의 `repair-pr`이 계속 맡는다. 작성자
  대응 원칙은 공유 정본 `responding-to-review.md` 하나로 두고 `repair-pr`·`address-review`·
  `execute-plan`에 배포한다.
- omp에서는 순정 `/review`, `/annotate code-review`, 순정 `reviewer` agent를 그대로 쓴다. Review는
  `reviewer`에만 적용되는 규칙 `sonsu-review-standard`(`omp-rules/` → 패키지 `rules/`)로 라벨·판정·
  어조를 얹고 결과 스키마는 바꾸지 않는다. `/review`와 `review-code`는 함께 둔다. `review-code`는
  대상 고정, 커밋 검토, PR 게시, 여러 검토자 결과 통합, 지적 검증을 더한다.
- 커밋 메시지는 Conventional Commits 1.0.0에 type 목록·헤더·본문·breaking change·type 하나·티켓 footer
  확장 규칙(E1–E6)을 더해 쓴다. PR 제목도 같은 헤더 형식이다.
- 브랜치 이름에는 티켓 ID를 넣지 않는다. 티켓 연결은 PR 본문과 커밋 footer로 한다.

## 대안

- **Review를 omp opt-in으로 배포**: 기본 구성은 작아지지만 omp 사용자가 리뷰 기준을 쓰려면 따로
  설치해야 하고, 순정 `/review`에 기준이 얹히지 않는다.
- **PR 리뷰 코멘트 대응을 `address-review`로 이동**: 리뷰 관련 스킬이 한 곳에 모이지만, PR 조회·
  수정 push·답글·대화 해결은 Git 원격 쓰기 권한과 묶여 있어 `git`의 권한 경계를 넘는다.
- **Engineering 유지**: 이동 비용은 없지만 omp에서 리뷰만 쓰는 구성을 만들 수 없다.
- **omp에서 `review-code` 제외**: 순정 `/review`만 남겨 단순하지만 커밋 검토·PR 게시·결과 통합을 omp에서
  쓸 수 없다.
- **omp에서 순정 형식(P0–P3, correct/incorrect)으로만 보고**: 규칙 파일이 필요 없지만 호스트마다 리뷰
  결과 형식이 달라진다.

## 결과

- 기존 `workflow`·`engineering` 설치는 제거하고 새 플러그인을 설치해야 한다
  ([이전 버전에서 이동하기](../guides/migrating-from-earlier-versions.md#workflowengineering에서-이동)).
- `workflow`·`engineering` 이름으로 저장된 진행 중 작업 연속성 기록은 새 플러그인으로 이어지지 않는다.
- 새 플러그인 4개의 refactor inventory는 작성하지 않았다. 인벤토리 검증기는 인벤토리 파일이 없는
  카탈로그 플러그인을 `missing-inventory` 경고로 보고하고 검사를 실패시키지 않는다.
- ADR 0025의 Engineering 리뷰 진입점 통합은 Review의 `review-code`로 대체된다.

## 다시 볼 때

- omp 순정 reviewer가 플러그인 규칙을 더 이상 적용하지 않거나 결과 스키마가 바뀔 때
- `dev-workflow`를 omp에서도 써야 하는 요청이 반복될 때
- Conventional Commits 명세나 확장 규칙과 다른 저장소 규칙이 자주 충돌할 때
