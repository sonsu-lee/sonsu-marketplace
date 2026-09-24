# ADR 0015: Claude Code 배포 추가

- Status: Accepted
- Date: 2026-09-24

## 배경

12개 플러그인의 작업 계약과 스킬은 호스트별 설치 방식보다 넓게 사용할 수 있다. 기존
[ADR 0014](0014-use-codex-managed-engineering.md)는 Claude 배포와 runtime adapter를 제거했다.
이번 결정은 현재 Claude Code 2.1.220에서 마켓플레이스 등록과 독립 설치를 지원한다.

## 결정

- `.agents/plugins/marketplace.json`과 각 `.codex-plugin/plugin.json`을 정본으로 유지한다.
- 생성기가 `.claude-plugin/marketplace.json`과 12개 `.claude-plugin/plugin.json`을 만들고
  `--check`로 drift를 검사한다. OMP 카탈로그의 이름·버전·경로도 대조한다.
- 스킬과 hook은 plugin root의 표준 위치에서 발견한다. Claude 전용 매니페스트에 중복 선언하지 않는다.
- 공통 작업·권한·품질 계약은 유지하고 호스트별 도구·모델·세션 기능만 분기한다. Claude에서
  Codex 모델명을 복사하지 않으며 실제 실행 모델과 관찰 결과를 기록한다.
- Engineering의 최초 독립 리뷰 5개와 고위험 red-team 1개, 관리형 게이트의 관찰 전용 Stop hook 등
  ADR 0014의 품질 결정은 유지한다.
- Memory Manager는 Claude auto memory를 명시적 호출로 점검한다. Figma canvas 작업은 연결된
  공식 Figma 플러그인의 현재 capability와 편집 권한을 요구한다.

## 결과와 검증

Claude 카탈로그·매니페스트의 strict validation과 분리된 설정 디렉터리의 설치·발견을 확인한다.
스킬 실행, hook의 컴팩션·재개 및 Stop 관찰, Figma live canvas는 각각 별도 evidence로 기록한다.
Figma 연결·편집 가능한 테스트 파일이 없으면 live canvas 결과를 `not_run`으로 남긴다.
사용자 계정에 플러그인을 자동 설치하거나 인증을 변경하지 않는다.

이 ADR은 ADR 0014의 **Codex 전용 배포** 결정만 변경한다. 기존 품질 게이트와 이력은 유지한다.
