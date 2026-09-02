# Quality Engineering

Quality Engineering은 확인된 제품·도메인 계약에 맞는 코드를 작성하고, 불필요한 복잡성,
reader load, 도달 가능한 실패 경로와 운용 가능성을 서로 구분된 관점으로 검토하는 독립 Codex
플러그인입니다.

## 설치

Sonsu Marketplace를 등록한 뒤 이 플러그인만 선택해 설치할 수 있습니다.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
codex plugin add quality-engineering@sonsu-marketplace
```

로컬 변경을 검증할 때는 repository root를 marketplace로 등록합니다.

```sh
codex plugin marketplace add .
codex plugin add quality-engineering@sonsu-marketplace
```

## 스킬

| 스킬 | 역할 | 직접 trigger |
| --- | --- | --- |
| `domain-shaped-code` | 확인된 계약, trust boundary, 타입과 제어 흐름을 직접 반영하는 구현·리팩터링 | 도메인 형태의 코드 구현 또는 리팩터링 요청 |
| `simplify-code` | 삭제 우선, YAGNI와 최소 해법을 적용하는 구현 | 단순화, 최소 구현 또는 YAGNI를 명시한 요청 |
| `review-overengineering` | 선택된 변경의 불필요한 abstraction·state·extension surface 검토 | diff·commit·branch의 over-engineering review 요청 |
| `audit-overengineering` | 큰 경로 또는 repository의 삭제·축소 후보 순위화 | repository/path 전체 over-engineering audit 요청 |
| `review-maintainability` | reader load, 변경 이유, 중복 지식과 public surface 검토 | maintainability 또는 reader-load review 요청 |
| `review-failure-modes` | 도달 가능한 실패, retry, 부분 성공, concurrency와 cleanup 검토 | failure-mode 또는 adversarial review 요청 |
| `review-operability` | error ownership, logging, telemetry와 민감정보 검토 | operability·observability review 요청 |
| `review-quality` | 관련 lens만 골라 중복 없이 통합하는 broad quality review | 여러 품질 관점을 아우르는 quality review 요청 |

review와 audit 스킬은 읽기 전용입니다. `review-quality`는 모든 lens를 기계적으로 실행하지 않고
현재 변경에 실제로 관련된 관점만 선택합니다.

## 공통 판단 순서

모든 스킬은 다음 순서를 공유합니다.

1. 확인된 제품·도메인 계약
2. correctness, security, data integrity, accessibility와 compatibility
3. 실제 실행 흐름을 읽는 사람의 이해 비용
4. 단순성과 제거 가능한 코드
5. 아직 확인되지 않은 확장 가능성

미래 확장성을 위해 현재 계약, 안전성 또는 읽기 쉬운 흐름을 희생하지 않습니다.

## 책임 경계

Quality Engineering은 코드의 shape, simplicity, maintainability, failure mode와 operability를
담당합니다. 계획·TDD·디버깅·branch 완료 같은 개발 lifecycle은 Engineering이, branch·commit·
ticket·PR은 Workflow가, 깊은 보안 감사와 취약점 판정은 전용 security skill이 담당합니다.
도메인 glossary, `CONTEXT.md`, ADR과 미결 architecture decision도 이 플러그인의 범위가 아닙니다.

다른 플러그인의 설치나 특정 skill ID를 전제하지 않습니다. 여러 영역의 요청에서는 runtime이
설치된 독립 스킬을 요청 목적에 맞게 조합할 수 있습니다.

## 출처와 라이선스

고정 upstream commit, 원본 파일, SHA-256, 최종 mapping과 로컬 변경은
[`UPSTREAM.md`](UPSTREAM.md)에 기록합니다. 원본 byte-for-byte baseline은 별도 commit
`538c9e9b8130a0f6cf56780a7700a983f77524de`에 보존되어 있습니다.

플러그인의 배포 라이선스는 [Apache-2.0](LICENSE)입니다. 포함된 MIT 원본의 저작권과 permission
notice는 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)에 유지하며, OpenAI 원본의 NOTICE는
[`NOTICE`](NOTICE)에 보존합니다.
