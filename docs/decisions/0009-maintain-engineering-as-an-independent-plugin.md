# 0009 Maintain Engineering as an Independent Plugin

- Status: Accepted
- Date: 2026-09-04
- Supersedes: `0005` (identity-sensitive 예외에 따라 현재 tree에서 제거)
- Superseded by: None
- Approval: 사용자가 2026-09-04 현재 대화에서 Engineering의 독립 전환과 `1.0.0` 버전을 승인했습니다.

## Context

Engineering은 의사코드 우선 계획, 위험 기반 검증, 구현, 디버깅과 코드 리뷰를 담당하는 14개
스킬로 구성됩니다. 현재 기능과 유지관리 방향은 이 저장소의 Engineering 문서와 결정에서 직접
정의합니다.

이전 정체성의 이름, 경로, 시각 자산, 호환 설정과 provenance 문서를 현재 tree에 계속 보존하면
Engineering을 독립적으로 관리한다는 목표와 충돌합니다. 반면 포함된 코드의 MIT 저작권과 허가
고지는 파생 코드를 배포하는 동안 유지해야 합니다.

## Decision

Engineering을 현재 유지관리자가 독립적으로 설계하고 배포하는 플러그인으로 관리합니다.
매니페스트 버전은 `1.0.0`부터 독립 semantic version을 사용합니다. upstream 동기화 대상,
predecessor alias, 이전 scratch 경로와 설치 migration을 현재 배포 계약으로 제공하지 않습니다.

Engineering의 scratch plan, subagent workspace와 brainstorming session은 `.engineering/`만
사용합니다. 기존 설치나 scratch artifact는 자동으로 읽거나 이동하거나 삭제하지 않습니다.
업그레이드 전에 더 이상 사용하지 않는 플러그인 복사본과 로컬 artifact를 정리할 책임은
사용자에게 있습니다.

이전 정체성을 직접 포함한 `0005` 결정과 provenance 기록은 현재 tree에서 제거합니다. 이는
일반적인 결정 보존 규칙의 좁은 예외입니다. 현재 계약과 삭제 이유는 이 문서에 남기되 제거 대상의
이름과 경로는 다시 기록하지 않습니다. 기존 Git object history의 재작성은 이 결정의 범위가
아닙니다.

Engineering의 [`LICENSE`](../../plugins/engineering/LICENSE)는 MIT 저작권과 허가 고지를 계속
보존합니다. 향후 외부 자료나 코드를 새로 포함하면 해당 라이선스가 요구하는 고지와 출처를 그
변경 범위에 맞게 기록합니다.

## Alternatives Considered

- 이전 호환 경로와 설치 안내 유지: 기존 checkout의 전환은 쉬워지지만 현재 tree에 제거 대상
  정체성과 호환 계층이 다시 남습니다.
- provenance 기준선 유지: 외부 변경과의 비교는 쉬워지지만 Engineering을 계속 특정 upstream
  릴리스의 fork로 관리하게 됩니다.
- 전체 Git history 재작성: 과거 object까지 제거할 수 있지만 모든 관련 ref의 force push와
  협업자 checkout 재동기화가 필요하므로 이 변경에 포함하지 않습니다.

## Consequences

Engineering의 버전은 기존 계열에서 `1.0.0`으로 전환됩니다. 현재 검증 대상인 Codex CLI
`0.152.1`은 non-curated plugin의 manifest 버전이 달라지면 새 내용을 설치하고 이전 cache
version을 제거합니다. 기존 설치를 갱신한 뒤에는 새 Codex 작업을 시작해야 최신 skill catalog를
사용합니다.

이전 scratch artifact와 설치 복사본은 자동 migration되지 않습니다. 이를 남긴 checkout에서는
artifact가 untracked로 보이거나 동일 역할의 skill이 중복 노출될 수 있으므로 사용자가 전환 전에
정리해야 합니다.

Engineering에는 일반 upstream update runbook을 적용하지 않습니다. 기능과 정책 변경은 현재
Engineering 문서, 평가와 Git history를 기준으로 검토합니다.

## Revisit When

Engineering이 다시 외부 프로젝트의 릴리스를 정기적으로 동기화하거나 Codex가 안전한 plugin ID
migration과 scratch artifact 이전 계약을 제공할 때 이 결정을 재검토합니다.
