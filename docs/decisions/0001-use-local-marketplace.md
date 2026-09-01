# 0001 Use a Local Marketplace

- Status: Accepted
- Date: 2026-09-01
- Supersedes: None
- Superseded by: None

## Context

개인적으로 사용할 Codex 플러그인과 외부 플러그인의 로컬 커스텀을 여러 위치에 흩어 두면
등록 방식, 출처와 적용 정책을 추적하기 어렵습니다. 특히 업스트림 원본과 개인 변경을
구분할 수 있어야 합니다.

## Decision

`.agents/plugins/marketplace.json`을 사용하는 저장소 로컬 마켓플레이스를 운영하고,
플러그인은 `plugins/<name>/` 아래에 보관합니다. 외부 플러그인은 `UPSTREAM.md`에 출처,
기준 commit과 포함 범위를 기록합니다.

## Alternatives Considered

- 스킬을 사용자 전역 디렉터리에 개별 복사: 간단하지만 출처와 버전 관리가 분산됩니다.
- 외부 플러그인을 수정 없이 직접 설치: 업데이트는 쉽지만 개인 정책을 버전 관리할 수 없습니다.
- 각 플러그인을 별도 저장소로 운영: 격리는 좋지만 개인용 목록과 등록 관리가 복잡해집니다.

## Consequences

플러그인 목록과 커스텀 이력을 한 저장소에서 검토할 수 있습니다. 대신 업스트림 업데이트 때
원본 변경과 로컬 변경을 구분하고 실제 Codex 로딩을 다시 검증해야 합니다.

## Revisit When

플러그인 수가 늘어 독립 릴리스나 접근 권한 분리가 필요해지면 저장소 분리를 다시 검토합니다.
