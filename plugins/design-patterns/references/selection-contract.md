# 선택 결과 계약

다음 필드를 순서대로 사용합니다. 확인하지 못한 내용을 빈칸이나 추정으로 채우지 말고
`insufficient-evidence`의 근거로 기록합니다.

```text
Decision: use | no-pattern | insufficient-evidence
Scope: 판단한 component, interaction, transaction 또는 system boundary
Observed forces: 실제로 확인한 반복 문제와 충돌 제약
Baseline: 가장 직접적인 해법과 충분하거나 부족한 이유
Candidates: 최대 3개 pattern ID, 각 적합 근거와 비용
Selected: primary 0~1개, 필요한 supporting pattern만
Rejected: 검토했지만 선택하지 않은 후보와 이유
Implementation shape: language, framework, minimal form
Verification: 선택한 guarantee를 반증할 수 있는 검사
Sources: 사용한 catalog entry와 현재 artifact 근거
```

## Decision 의미

- `use`: `decision-ready` 패턴이 baseline에 없는 필요한 guarantee를 제공하고 비용을 수용할 수 있습니다.
- `no-pattern`: 직접 구현, 언어 idiom, 표준 라이브러리 또는 framework 기능이 필요한 guarantee를 더
  작게 제공합니다.
- `insufficient-evidence`: 반복성, forces, runtime 보장, failure semantics 또는 비용 수용 여부가
  확인되지 않아 선택을 정당화할 수 없습니다.

## 최소 예시

```text
Decision: no-pattern
Scope: 요청별 가격 계산 함수
Observed forces: 할인 규칙은 한 종류이며 두 번째 variation은 확인되지 않음
Baseline: 함수 인자와 직접 분기로 현재 보장을 충족
Candidates: object-oriented-strategy — variation이 반복될 때 재검토
Selected: none
Rejected: Strategy — 지금은 별도 lifecycle이나 교체 요구가 없음
Implementation shape: TypeScript 함수 하나와 exhaustive branch
Verification: 각 할인 입력의 반환값 table test
Sources: current pricing module; object-oriented-strategy
```
