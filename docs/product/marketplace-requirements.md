# 마켓플레이스 요구사항

- Status: Current
- Last reviewed: 2026-09-03

## 목표

개인적으로 사용할 Codex 플러그인을 발견, 설치하고 업데이트할 수 있는 로컬 마켓플레이스를
Git으로 관리합니다. 외부 플러그인의 원본 기준선과 개인용 정책 변경을 모두 추적할 수 있어야
합니다.

## 요구사항

- 마켓플레이스는 저장소 루트에서 Codex에 등록할 수 있어야 합니다.
- 각 플러그인은 독립된 디렉터리와 유효한 `.codex-plugin/plugin.json`을 가져야 합니다.
- 각 플러그인의 핵심 기능은 다른 마켓플레이스 플러그인의 설치나 선행 실행 없이 동작해야 합니다.
- 외부 플러그인은 저장소, 기준 commit, 라이선스와 포함 범위를 기록해야 합니다.
- 최초 원본 가져오기와 로컬 커스텀은 별도 commit으로 구분해야 합니다.
- 기존 linked worktree에서는 새 worktree를 중복 생성하지 않아야 합니다.
- 새 장기 문서를 만들기 전에 기존 문서를 조사해야 합니다.
- 문서 작성과 Git commit은 사용자의 권한 범위를 분리해야 합니다.
- 검증은 변경 성격에 비례해야 하며 실제 Codex 로딩이 중요한 경우 정적 검사만으로 대체하지 않습니다.
- 외부 design provider를 사용하는 스킬은 현재 tool capability와 permission을 확인하고 screenshot,
  구조 readback과 실행 가능한 interaction evidence를 서로 대신하지 않아야 합니다.
- Figma, FigJam, Paper Design과 draw.io는 최종 artifact의 source of truth를 기준으로 구분하고,
  지원되지 않는 기능을 다른 제품으로 조용히 전환하거나 성공으로 보고하지 않아야 합니다.
- Live design mutation은 page subtree, component set, variable collection, prototype graph와 editor state
  같은 충돌 도메인별 single-writer를 적용하고 writer가 적용 직전 target을 다시 읽어야 합니다.
- Skill은 session model과 reasoning effort를 자동 변경하지 않으며 model 비교, live canvas 평가와
  local Figma plugin 생성은 범위·비용·mutation 권한을 별도로 승인받아야 합니다.
- 비밀 값은 저장소에 저장하지 않습니다.

## 제외 범위

- 공개 마켓플레이스 운영
- 다른 사용자를 위한 자동 배포와 호스팅
- 사용자 계정의 플러그인 자동 설치 또는 활성화
- 사용자의 요청이 없는 원격 push, PR, merge와 배포
- 실제 충돌 근거가 없는 플러그인 간 hard dependency와 공통 router

## 완료 기준

등록된 플러그인의 출처와 로컬 차이를 저장소에서 찾을 수 있고, 로컬 마켓플레이스를 Codex가
실제로 읽을 수 있으며, 관련 문서와 Git 이력이 현재 정책을 정확히 설명해야 합니다.
