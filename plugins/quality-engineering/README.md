# Quality Engineering

Quality Engineering은 확인된 제품·도메인 계약에 맞는 코드를 작성하고, 불필요한 복잡성,
reader load, 도달 가능한 실패 경로와 운용 가능성을 서로 구분된 관점으로 검토하는 독립
Codex·Claude Code 플러그인입니다.

## 설치

Sonsu Marketplace를 등록한 뒤 이 플러그인만 선택해 설치할 수 있습니다.

```sh
# Codex
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
codex plugin add quality-engineering@sonsu-marketplace

# Claude Code
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install quality-engineering@sonsu-marketplace
```

로컬 변경을 검증할 때는 repository root를 marketplace로 등록합니다.

```sh
codex plugin marketplace add .
codex plugin add quality-engineering@sonsu-marketplace

# Claude Code
claude plugin marketplace add . --scope local
claude plugin install quality-engineering@sonsu-marketplace --scope local
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
| `review-quality` | 동작·구조·패턴에서 관련 관점만 골라 중복 없이 통합 | 일반 코드·diff 리뷰 또는 여러 품질 관점의 리뷰 요청 |

일반적인 “이 코드/diff 리뷰해줘”는 `review-quality`, 한 관점만 지정한 요청은 해당 집중 리뷰가
담당합니다. 개발 절차가 선언한 리뷰와 명시적 독립 리뷰어 요청은 해당 개발 절차의 범위입니다.
이 플러그인은 독립적으로 직접 리뷰를 완료하며 다른 플러그인·패키지·독립 리뷰어·관찰 도구 등록을
필수 조건으로 요구하지 않습니다. Codex 기본 `/review`·GitHub 자동 PR 리뷰 연결은 포함하지 않습니다.

[공통 리뷰 기준](references/review-criteria.md)은 근거가 현재 변경에 적용되는 이유, 발생 조건·영향과
최소 수정 방향을 설명합니다. 코드·호출자·설정으로 해결되지 않는 중요한 의문만 허용된 읽기 전용
PR·공식 자료·운영 조회로 확인합니다. AI slop는 근거 없는 주장·중복·빈 수사·불필요한 코드와 증적
요구를 제거하되 조건·예외·불확실성과 필요한 보호는 보존하는 기준으로 다룹니다. 선택적 개선을
필수 작업으로 바꾸지 않으며 최종 판단은 사용자에게 남깁니다. `suggestion`은 기본적으로 생략합니다.

review와 audit 스킬은 읽기 전용입니다. `review-quality`는 모든 lens를 기계적으로 실행하지 않고
현재 변경에 실제로 관련된 관점만 선택합니다.

## JavaScript·TypeScript 체크리스트

[`JavaScript·TypeScript 개인 리뷰 체크리스트`](references/javascript-typescript-review.md)는
`null`·`undefined`와 truthiness, `satisfies`의 추론 경계, API trust boundary, type guard, async
실패와 반복되는 코드 냄새를 한곳에 정리합니다. 새 스킬을 추가하지 않고 구현에는
`domain-shaped-code`·`simplify-code`, 리뷰에는 요청 범위에 맞는 `review-quality`,
`review-maintainability`, `review-failure-modes`가 이 기준에서 자기 lens에 해당하는 부분만
불러옵니다.

개인이 PR을 보기 전 빠른 self-review 목록으로 직접 읽어도 되고, Codex에는 다음처럼 요청할 수
있습니다.

```text
이 TypeScript diff를 broad quality review로 봐줘. nullish 의미, satisfies 추론,
API 경계 이후 중복 type guard와 async 실패를 특히 확인해줘. 수정은 하지 마.
```

compiler 반례와 finding/no-finding 쌍은
[`evals/javascript-typescript-review`](../../evals/javascript-typescript-review/README.md)에 고정합니다.
정적 fixture 검증과 실제 모델 판단·native skill loading은 서로 다른 결과로 기록합니다.

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

## 컴팩션 후 작업 재개

[`quality-engineering:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 스킬을
직접 호출해 수동으로 재개할 수 있습니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고하세요.
