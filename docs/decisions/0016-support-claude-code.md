# ADR 0016: Claude Code 마켓플레이스 배포와 호스트별 모델 프로필

- Status: Accepted
- Date: 2026-09-25

## Context

12개 플러그인의 카탈로그와 모델 실행 지침은 Codex를 기준으로 작성돼 있었다. 같은 스킬을
Claude Code CLI에서 사용하려면 별도 marketplace manifest, hook 경로, 모델 지정 방식과
세션 식별이 필요하다. 기존 품질 게이트의 리뷰 인원·판정 계약은 유지해야 한다.

## Decision

Codex catalog와 plugin manifest를 정본으로 유지하고 Claude Code의 marketplace·manifest를
생성한다. 스킬·script·hook은 가능한 한 같은 패키지 파일을 쓴다. Codex 전용 connector
설정은 Claude Code로 복사하지 않으며 외부 MCP는 호스트에서 연결을 확인한다.

Codex 모델 프로필과 Claude Code 모델 프로필을 분리한다. Claude 기본값은 Haiku 4.5,
Sonnet 5, Opus 5.5의 정확한 모델 ID를 역할에 배치한다. 공유 역할 프로필에서
Engineering·Prompting 플러그인의 native `agents/` frontmatter를 생성해 Claude Code가
모델과 effort를 실제 subagent 구성으로 읽게 한다. Sonnet은 공식 모델 기본 effort `high`,
Opus 5.5는 `medium`을 사용하며, effort를 지원하지 않는 Haiku에는 override를 만들지 않는다.
일반 전체 리뷰 5명, 상위 리뷰 1명, 국소 리뷰 1명, 고위험 red-team 1명과 심층 PR 리뷰
5+1 계약은 유지한다. 사용자 지정이 운영 기본값보다 우선한다.

관리형 게이트는 `init --host`를 저장해 해당 호스트의 정책·프로필로 근거를 검증한다.
작업 연속성은 Claude hook의 `session_id`를 사용하고 기존 Codex 세션과 섞지 않는다.
메모리 관리 스킬은 두 호스트에서 명시 호출만 허용한다.

## Alternatives Considered

- Claude 전용 플러그인 소스를 복제: 정책·스킬 드리프트가 커진다.
- 모델 alias 사용: 최신 모델로 묵시 변경될 수 있어 재현 가능한 근거가 약해진다.
- Claude 배포를 보류: 사용자가 요청한 실제 CLI 사용을 지원하지 못한다.

## Consequences

두 호스트의 manifest·스킬 discovery·hook과 모델 접근성을 별도로 검증해야 한다.
정적 검증은 실제 모델 호출이나 자동 스킬 선택의 증거가 아니다. Claude의 모델 접근권이
없는 환경에서는 그 실행을 `blocked`로 보고한다. 기존 [ADR 0014](0014-use-codex-managed-engineering.md)와
[ADR 0015](0015-independent-skills.md)의 Codex 전용 배포 결정을 이 결정이 갱신하며,
독립 스킬·품질 게이트 계약과 기존 연구 근거는 유지한다.

## Revisit When

Claude Code의 plugin schema, 모델 ID, subagent 설정 또는 hook event 계약이 바뀔 때,
혹은 동일 스킬 소스의 호스트별 동작 차이가 실제 평가에서 확인될 때 재검토한다.
