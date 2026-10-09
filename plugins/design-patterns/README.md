# Design Patterns

코드와 시스템 제약에서 반복 문제와 필요한 보장을 확인하고, 그 보장을 가장 작게 제공하는 디자인 패턴을 고르거나 기존 패턴 사용을 검토합니다.

## 설치

```bash
codex plugin add design-patterns@sonsu-marketplace
claude plugin install design-patterns@sonsu-marketplace
omp plugin install design-patterns@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `select-design-patterns` | 반복되는 설계 문제에 패턴이 필요한지 정할 때 | `use`·`no-pattern`·`insufficient-evidence` 결정과 근거 |
| `review-pattern-usage` | 기존 코드·diff의 패턴 적용 검토를 명시적으로 요청할 때 | 발생 조건이 있는 finding 목록 또는 finding 없음 |

## 사용 예시

요청: “설정값 세 개를 읽는 로더에 Builder 패턴이 필요할까?”

[`references/selection-contract.md`](references/selection-contract.md) 필드로 쓴 결과입니다.

| 필드 | 값 |
| --- | --- |
| `Decision` | `no-pattern` |
| `Baseline` | 기본값이 있는 데이터 객체 하나 |
| `Rejected` | Builder. 생성 단계나 조립 순서가 없다. |
| `Verification` | 누락·잘못된 값의 table test |

## 카탈로그

[`catalog/`](catalog/)가 계열별 패턴 이름과 출처를 보관합니다.
추천에는 [`catalog/decision-ready.json`](catalog/decision-ready.json) 항목만 사용합니다.
성숙도·갱신 규칙은 [`references/source-policy.md`](references/source-policy.md)에, 출처는 [`UPSTREAM.md`](UPSTREAM.md)에 있습니다.

## 검증

```bash
python3 plugins/design-patterns/scripts/validate_catalog.py
python3 -m unittest plugins/design-patterns/tests/test_validate_catalog.py
```
