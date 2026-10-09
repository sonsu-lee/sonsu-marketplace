# ADR 0026: Design Patterns를 omp opt-in 패키지로 배포

- 날짜: 2026-10-10
- 상태: 채택
- 관련 결정: [ADR 0013](0013-add-design-patterns-plugin.md), [ADR 0022](0022-add-worklog-plugin.md)

## 배경

Design Patterns는 Codex와 Claude Code에만 배포되었다. omp 기본 묶음은 고정되어 있고, Design Patterns는
[ADR 0022](0022-add-worklog-plugin.md)가 허용한 opt-in 패키지에도 들어 있지 않았다. 플러그인 감사
([refactor-assessment](../research/refactor-assessment.md))에서 Design Patterns의 decision-ready
카탈로그와 관계·성숙도 계약은 omp 기본 리뷰·검색이 제공하지 않는 도메인 자료로 판정되었다. 반면
설계 패턴 선택·검토는 명시적으로 요청할 때만 쓰는 작업이라 모든 omp 사용자에게 설치할 근거는 없다.

## 결정

- `design-patterns`를 `OMP_OPTIN_PLUGINS`에 추가한다. omp 카탈로그에 등록되고 사용자가
  `omp plugin install design-patterns@sonsu-marketplace`로 직접 설치한다.
- omp 기본 묶음은 바꾸지 않는다.
- 별도 omp 패키지를 생성하지 않고 `plugins/design-patterns/`를 그대로 읽게 한다. runtime extension과
  hook은 배포하지 않는다.

## 대안

- **기본 묶음에 추가**: 설치 단계는 줄지만 모든 사용자의 스킬 라우팅에 패턴 스킬이 더해진다.
  일반 구현·리팩터링 요청과 혼동될 여지가 커진다.
- **omp 배포 제외 유지**: 기본 구성은 단순하지만 omp 사용자는 카탈로그 밖 경로로 설치해야 하고
  업데이트를 받지 못한다.

## 결과

- README 3종의 omp 선택 설치에 `design-patterns`를 둔다.
- [이전 버전에서 이동하기](../guides/migrating-from-earlier-versions.md)의 제거 목록에서
  `design-patterns`를 뺀다. 이전 11개 구성으로 설치한 사용자는 `--force` 재설치로 갱신한다.
- ADR 0022의 "현재 opt-in 패키지는 worklog뿐"이라는 서술은 이 결정으로 대체된다.

## 다시 볼 때

- 명시적 요청 없이도 패턴 선택이 반복되어 기본 묶음 승격이 필요할 때
- omp가 같은 범위의 패턴 카탈로그를 기본 기능으로 제공할 때
