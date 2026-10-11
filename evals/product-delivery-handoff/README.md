# 요구사항·설계·티켓·계획 인계 평가

[인계 계약](../../plugins/product/references/delivery-handoff.md)의 작업 크기 판정, PRD 품질 기대,
Dev Workflow 계획의 REQ 추적과 근거 표기를 행동으로 확인한다. 결정 배경은
[ADR 0021](../../docs/decisions/0021-use-hybrid-product-delivery-handoff.md)에 있다.

## 사례

`cases.json`의 `schema_version`은 `product-delivery-handoff-v1`이다. 각 사례는 `id`, `prompt`,
`installed_plugins`, `entry_skill`, `expected`를 가진다. `expected`는 출력에서 관찰할 수 있는 문장만 담는다.

| ID | 확인하는 것 |
| --- | --- |
| `size-s-skips-prd` | 한 문장 변경에 PRD를 만들지 않는다 |
| `size-m-writes-prd-lite` | M 작업의 실제 초안이 PRD-lite 구조를 따른다 |
| `non-prd-tickets-preserve-source` | PRD 없는 요구 출처에 REQ ID나 PRD 링크를 만들지 않는다 |
| `size-m-prd-lite` | 한 기능 안 변경은 PRD-lite와 구현 계획으로 간다 |
| `size-l-full-handoff` | 외부 계약 변경은 전체 PRD → 외부 설계 → 티켓 → 계획으로 간다 |
| `prd-to-plan-req-column` | 계획의 흐름 표에 `요구사항` 열과 REQ ID가 있다 |
| `nfr-without-number-becomes-open` | 근거 없는 품질 수치를 OPEN 항목으로 남긴다 |
| `evidence-tags-in-plan` | 계획의 판단 근거에 종류가 붙고 `[추론]`을 결정 근거로 쓰지 않는다 |

## 실행 방법

1. 사례마다 대화 이력이 없는 새 컨텍스트 서브에이전트를 띄운다.
2. `installed_plugins`에 속한 `entry_skill`과 그 스킬이 현재 요청에 대해 읽도록 지시하는 필수 reference를 읽게 하고 `prompt`를 준다. reference가 다시 필수로 연결한 자료도 같은 범위에서 읽는다. 설치되지 않은 플러그인의 스킬은 제공하지 않으며, 필요한 자료를 읽을 수 없으면 그 제한을 기록한다. `expected`는 보여 주지 않는다.
3. 판정자가 출력을 `expected`의 각 문장과 대조한다.

## 판정

결과는 사례별로 `pass | fail | not_run | inconclusive`와 근거를 기록한다. `expected` 중 하나라도
어긋나면 `fail`이다. 실행했지만 출력만으로 판정할 수 없으면 `inconclusive`다.

## 현재 상태

모든 사례가 `not_run`이다.
