# Design Patterns

실제 코드와 시스템 제약에서 반복되는 문제를 확인한 뒤, 필요한 보장을 가장 작은 형태로 제공하는
디자인 패턴을 선택합니다. 패턴 이름을 먼저 정하거나 가능한 패턴을 많이 나열하는 도구가 아닙니다.

현재 카탈로그는 2026-09-08에 확인한 12개 계열의 이름 553개를 `indexed`로 보관합니다. 그중
문제, forces, 사전 조건, 금기, 보장, 비용과 구현 형태를 정규화한 36개만 `decision-ready`이며
선택 스킬은 이 항목만 추천할 수 있습니다.

## 설치

```sh
codex plugin add design-patterns@sonsu-marketplace
```

## 스킬

| 스킬 | 호출 | 책임 |
| --- | --- | --- |
| `select-design-patterns` | 조건부 자동 또는 `$select-design-patterns` | 코드·설계의 forces를 확인하고 최대 3개 후보에서 필요한 패턴만 선택 |
| `review-pattern-usage` | `$review-pattern-usage` 명시 호출 | 기존 패턴이 약속한 보장, 비용과 경계를 실제 구현이 지키는지 읽기 전용 검토 |

`select-design-patterns`는 일반 구현이나 사소한 분기마다 자동 개입하지 않습니다. 표준 라이브러리,
프레임워크 기능이나 직접 구현으로 요구 보장이 충분하면 `no-pattern`을 반환합니다. 증거가 부족하면
패턴 이름을 추측하지 않고 `insufficient-evidence`로 남깁니다.

`review-pattern-usage`는 `policy.allow_implicit_invocation: false`를 적용해 사용자가 명시적으로 호출한 경우에만 실행합니다.

## 선택 게이트

추천 전에 다음 질문에 답할 수 있어야 합니다.

1. 같은 문제가 실제로 반복되는가?
2. 서로 충돌하는 forces가 확인됐는가?
3. 표준 라이브러리나 프레임워크가 이미 해결하지 않는가?
4. 직접적인 baseline 해법이 왜 부족한가?
5. 어떤 보장이 필요한가?
6. 패턴의 비용을 받아들일 수 있는가?
7. 그 보장을 테스트하거나 관찰할 수 있는가?

후보는 최대 3개, 기본 선택은 primary 1개입니다. supporting pattern은 primary의 보장을 위해 실제로
필요할 때만 추가합니다.

## 카탈로그

[`catalog/index.json`](catalog/index.json)은 계열별 파일, 관찰일과 개수를 기록합니다.
[`catalog/source-manifest.json`](catalog/source-manifest.json)은 포함한 553개 항목마다 원천에서 관찰한
이름, 정규화한 이름·ID, 원천 경로와 정규화 사유를 고정합니다.
[`catalog/decision-ready.json`](catalog/decision-ready.json)은 추천 가능한 정규화 내용을 원본 ID에
overlay합니다. overlay는 원본 이름·family·level·출처를 바꿀 수 없고, 모든 판단 필드를 항목마다
직접 선언해야 합니다. family 파일은 index만 소유하고 `decision-ready` 승격은 이 overlay에서만 허용됩니다.
현재 계약은 12개 계열마다 정확히 3개를 요구합니다. `indexed` 이름은 탐색에는 쓸 수 있지만 추천
근거로는 부족합니다.

성숙도는 `indexed`, `normalized`, `decision-ready`, `contextual`, `superseded` 순서입니다.
상세 계약은 [`references/`](references)에 있고 출처·포함 범위·라이선스 주의사항은
[`UPSTREAM.md`](UPSTREAM.md)에 있습니다.

## 검증

```sh
python3 plugins/design-patterns/scripts/validate_catalog.py
python3 -m unittest plugins/design-patterns/tests/test_validate_catalog.py
python3 /path/to/skill-creator/scripts/quick_validate.py plugins/design-patterns/skills/select-design-patterns
python3 /path/to/skill-creator/scripts/quick_validate.py plugins/design-patterns/skills/review-pattern-usage
```

카탈로그 검증기는 승인된 12개 계열과 각 원천별 관찰 개수·전체 553개, 이름·원천 경로·출처의
family snapshot digest, source manifest 매핑과 digest, 계열 prefix를 포함한 ID, 끊어진 관계,
관계가 없는 cross-family 동일 이름, 계열별 정확히 3개인 추천 항목과 직접 선언된 의사결정 정보,
출처 URL 정책을 검사합니다. 모델의 실제 라우팅과 판단 품질은
[`evals/design-patterns/`](../../evals/design-patterns) 시나리오로 별도 평가해야 합니다.
