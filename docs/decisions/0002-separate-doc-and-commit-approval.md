# 0002 Separate Documentation and Commit Approval

- Status: Accepted
- Date: 2026-09-01
- Supersedes: None
- Superseded by: None

## Context

원본 Superpowers는 큰 설계에서 날짜 기반 spec을 작성해 바로 commit하고, 구현 계획의 각
task에도 commit 단계를 넣습니다. 이 방식은 설계 검토, 문서 위치 결정과 Git 이력 변경을
하나의 승인으로 취급합니다. 또한 관련 기존 문서가 있어도 새 날짜 문서가 쌓일 수 있습니다.

## Decision

설계 전에 기존 문서를 조사하고 [`docs/README.md`](../README.md)의 기준으로 문서 영향을
분류합니다. 새 문서나 큰 재구성은 경로와 목적을 사용자에게 먼저 제시합니다. 구현 계획은
기본적으로 대화나 Git에서 제외된 실행 파일에 두며, 날짜 기반 spec과 plan을 자동 생성하지
않습니다.

설계 승인, 문서 작성, 구현, commit, push와 PR은 서로 다른 권한으로 취급합니다. Git
commit은 현재 작업에서 사용자가 명시적으로 요청했거나 승인한 경우에만 수행합니다. 이미
승인한 범위 안에서는 같은 권한을 반복해서 묻지 않습니다.

## Alternatives Considered

- 원본의 날짜 기반 spec과 task별 commit 유지: 이력은 세밀하지만 문서 중복과 승인 범위가 커집니다.
- 모든 설계를 ADR로 기록: 일관성은 있지만 작거나 임시적인 결정까지 영구 문서가 됩니다.
- 구현 계획을 항상 `docs/plans/`에 저장: 실행 인계에는 편하지만 장기 문서와 임시 계획이 섞입니다.

## Consequences

장기 문서는 목적별 정본으로 유지되고 사용자가 commit 전에 실제 diff를 검토할 수 있습니다.
반면 task별 commit이 필요한 subagent 실행은 시작 전에 별도의 commit 승인이 필요합니다.

## Revisit When

계획과 commit을 안전하게 분리하면서도 subagent task diff를 독립적으로 복원할 수 있는
검증된 실행 방식이 생기면 task별 commit 요구를 다시 검토합니다.
