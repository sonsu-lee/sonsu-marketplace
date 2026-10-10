# ADR 0025: Engineering 리뷰 진입점 통합

- 날짜: 2026-10-09
- 상태: 채택
- 관련 결정: [ADR 0007](0007-use-stage-owned-quality-gates.md), [ADR 0015](0015-independent-skills.md)

## 맥락

Engineering은 PR 리뷰 진입점을 `review`와 `review-pr` 두 개로 제공했다. 두 스킬은 같은 [PR 실행·게시 계약](../../plugins/engineering/references/pr-review-execution.md)을 읽고 같은 `pr_review` 기본값(라운드당 새 검토자 1명), 새 세션·memory 격리·별도 워크트리, 고정 SHA와 통합 `COMMENT` 게시·재조회를 사용했다. 차이는 심층·다중 리뷰 요청을 받는 진입점뿐이어서 같은 절차를 두 곳에서 유지해야 했다.

SDD 리뷰 패키지도 `sdd-review-package` wrapper가 계획 파일 인수와 기본 출력 위치만 더한 뒤 정본 `review-package range`에 위임했다.

## 결정

- `review-pr` 스킬을 제거하고 GitHub PR의 일반·심층·다중 리뷰를 `review`의 PR 경로로 처리한다. 심층·다중 리뷰와 사용자 지정 모델·effort·인원은 같은 경로의 요청 옵션이다.
- PR 경로의 기본값, 사용자 지정 우선, 로컬 전용·게시 금지·리뷰 전용 요청 우선, 게시 계약은 그대로 유지한다. PR 외 일반 리뷰·개발 게이트의 기본 5명과 라운드 상한도 유지한다.
- PR의 host·repository·base/head·merge base·고정 SHA·기존 리뷰 ID는 읽기 전용 snapshot 도구로 수집하고 게시 전후 SHA를 대조한다. 전체 diff 고정은 계속 `review-package`가 맡는다.
- `sdd-review-package`를 제거한다. 호출자는 `review-package range BASE HEAD [OUTFILE]`을 직접 호출하고, 계획별 임시 위치가 필요하면 `sdd-workspace`가 만든 경로를 OUTFILE로 넘긴다.

## 대안

- **`review-pr`를 별칭으로 유지**: 기존 호출은 그대로 동작하지만 description이 겹치는 두 스킬이
  같은 PR 요청을 두고 경쟁한다. 옛 호출명은 공개 별칭으로 남기지 않는다는 라우팅 원칙과도 맞지 않는다.
- **`sdd-review-package` wrapper 유지**: 계획 경로에서 기본 출력 위치를 정해 주지만 정본
  `review-package`와 별도로 인자·출력 규칙을 맞춰야 하고, 같은 일은 `sdd-workspace` 경로를 넘기는 한 줄로 대신할 수 있다.

## 결과

PR 리뷰는 `engineering:review` 한 진입점에서 시작하며 `$review-pr` 직접 호출은 `$review`로 바뀐다. 라우팅 표와 평가 사례도 `engineering:review`를 기대한다. 이전 진입점의 구현과 경위는 Git 기록에서 확인한다.

공개 스킬과 스크립트를 제거하는 비호환 변경이므로 Engineering 버전을 4.0.0으로 올린다. 기존 활성 연속성 기록에 저장된 `review-pr` 이름은 계속 읽을 수 있다.

## 다시 볼 때

- PR 리뷰의 기본 인원·격리·게시 계약이 PR 외 리뷰와 다른 방향으로 갈라져 한 스킬 안에서 분기가 커질 때
- 라우팅 평가에서 심층·다중 PR 리뷰 요청이 `review`로 선택되지 않는 사례가 반복될 때
