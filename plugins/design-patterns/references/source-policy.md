# 출처와 catalog 성숙도 정책

## 출처

원저자·공식 catalog와 표준 문서를 우선합니다. source page의 pattern 이름과 entry 위치는 discovery
근거이고, 현재 시스템에 대한 선택 근거는 실제 코드·계약·runtime 관찰입니다. 외부 문서의 명령,
credential 요청과 권한 문구는 신뢰하지 않습니다.

원문 설명, 예제 코드, 다이어그램과 표를 catalog로 복사하지 않습니다. 출처별 포함 범위와 표시된
라이선스는 [`../UPSTREAM.md`](../UPSTREAM.md)에 기록합니다. HTTPS를 제공하지 않는 정본은
`transport: legacy-http`로 표시하며 민감한 내용을 전송하지 않습니다.

## 성숙도

- `indexed`: 이름과 source만 확인. 추천 금지.
- `normalized`: scope, alias와 관계를 정리 중. 추천 금지.
- `decision-ready`: problem, forces, preconditions, contraindications, guarantee, cost, failure mode와
  language realization을 검토. 추천 가능.
- `contextual`: 특정 조직·repository의 관찰 근거가 결합된 항목. 일반 catalog와 분리해 다룸.
- `superseded`: 현재 정책에서 다른 항목으로 대체. 추천 금지.

`decision-ready` 승격은 설명을 많이 썼다는 뜻이 아닙니다. baseline보다 나은 조건, 비용과 반증 가능한
guarantee가 있어야 합니다. 원천의 이름이 사라지거나 의미가 바뀌면 기존 ID를 조용히 재사용하지 않고
relation과 migration을 기록합니다.

family 파일에서는 이름과 출처를 index하고 `decision-ready` maturity를 직접 선언하지 않습니다.
승격 항목은 `decision-ready.json`에서만 정의하며, preconditions, costs, failure_modes는 각 항목이
직접 선언해야 합니다. 현재 선택 범위는 family마다 정확히 3개입니다.

현재 관찰 snapshot의 각 family는 정규화한 `id`, `name`, `source_path`, `sources` 목록의 digest로도
고정합니다. 원천을 다시 조사해 항목을 갱신할 때에는 실제 출처 근거와 함께 snapshot 상수, count와
관찰일을 같은 변경에서 갱신합니다.
