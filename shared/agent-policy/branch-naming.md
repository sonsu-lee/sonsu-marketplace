# 새 브랜치 이름

새 로컬·원격 브랜치 이름을 제안하거나 정할 때 적용한다. 기존 브랜치를 사용하는 push·PR·복구에서는 이름을 유지한다.

이름은 다음 순서로 결정한다.

1. 사용자가 지정한 정확한 이름
2. repository·team 문서가 정한 접두사·형식
3. 앞선 규칙이 없으면 `<prefix>/<short-kebab-description>`

## 접두사

접두사는 커밋 type(Git 플러그인의 `conventional-commits.md` E1)과 같다. 단 `feat`는 `feature`로 쓴다. 실제 변경 목적에 맞는 하나를 쓴다.

| 접두사 | 변경 목적 |
| --- | --- |
| `feature/` | 새 기능·동작 추가, 변경, 제거 |
| `fix/` | 잘못된 동작 수정 |
| `refactor/` | 동작을 바꾸지 않는 구조 변경 |
| `perf/` | 성능 개선 |
| `docs/` | 문서만 변경 |
| `test/` | 테스트만 추가·수정 |
| `build/` | 빌드 시스템, 의존성 |
| `ci/` | CI 설정 |
| `chore/` | 그 밖의 유지 관리(설정, 생성물) |
| `revert/` | 되돌림 |

## 설명

- `<short-kebab-description>`은 현재 작업 범위를 소문자 kebab-case 몇 단어로 쓴다.
- 티켓 ID, team key, 사용자명은 넣지 않는다.
  - 예외는 사용자가 정확한 이름을 지정했거나 ID를 넣으라고 명시한 경우뿐이다.
  - repository 규칙이 ID를 요구하면, 브랜치를 만들기 전에 그 충돌과 ID 없는 이름을 함께 알리고 사용자가 고른 이름으로 만든다.
  - Linear `Copy git branch name`, 연동 도구의 추천, 기존 branch 관례는 근거로 삼지 않는다.
  - 티켓 연결은 PR 본문과 커밋 footer로 한다. 이름에 ID가 없으면 Linear의 branch 기반 자동 연결은 일어나지 않는다.
- 실행 환경이 강제하는 접두사(`codex/` 등)만 앞에 붙인다. 실행 중인 호스트나 기존 branch 이름만으로는 붙이지 않는다.

## 예시

| 작업 | 이름 |
| --- | --- |
| 로그인 화면에 비밀번호 표시 버튼 추가 | `feature/login-password-toggle` |
| ENG-42: 만료 시각 경계의 세션 판정 수정 | `fix/session-expiry-boundary` |
| 설치 안내 문서 갱신 | `docs/install-guide` |
