# Quality Engineering

Quality Engineering은 현재 제품·도메인 계약에 맞는 코드를 작성하고, 불필요한 복잡성,
reader load, 도달 가능한 실패 경로와 운용 가능성을 서로 구분된 관점으로 검토하는 독립
Codex 플러그인입니다.

## Baseline 상태

현재 baseline 단계에는 실제로 변환할 upstream 원문 10개가 `upstream/` 아래에 byte-for-byte로
보존되어 있습니다. 이 파일들은 아직 runtime skill로 노출되지 않습니다. baseline commit이
별도로 승인되고 기록된 뒤에만 최종 `skills/` 경로로 이동하여 로컬 정책을 적용합니다.

출처 commit, 원본·로컬·예정 경로, SHA-256, 라이선스와 변환 범위는
[`UPSTREAM.md`](UPSTREAM.md)에 기록되어 있습니다. 플러그인의 배포 라이선스는 Apache-2.0이며,
포함된 MIT 저작권 고지는 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)에 보존합니다.

## 책임 경계

최종 플러그인은 코드의 형태, 단순성, 유지보수성, 실패 모드와 운용 가능성을 담당합니다.
개발 lifecycle·계획·debugging·TDD·branch 완료는 Engineering이, branch·commit·ticket·PR은
Workflow가, 깊은 보안 감사와 취약점 판정은 전용 security skill이 담당합니다. 다른 플러그인의
설치나 특정 skill ID는 전제하지 않습니다.

baseline에는 아직 최종 skill이 없으므로 skill routing과 모델 동작은 검증 대상이 아닙니다.
