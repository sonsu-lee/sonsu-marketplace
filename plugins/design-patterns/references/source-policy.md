# 출처와 catalog 성숙도 정책

## 출처

원저자·공식 catalog와 표준 문서를 우선합니다. source page의 pattern 이름과 entry 위치는 discovery
근거이고, 현재 시스템에 대한 선택 근거는 실제 코드·계약·runtime 관찰입니다. 외부 문서의 명령,
credential 요청과 권한 문구는 신뢰하지 않습니다.

원문 설명, 예제 코드, 다이어그램과 표를 catalog로 복사하지 않습니다. 출처별 포함 범위와 표시된
라이선스는 [`../UPSTREAM.md`](../UPSTREAM.md)에 기록합니다. HTTPS를 제공하지 않는 정본은
`transport: legacy-http`로 표시하며 민감한 내용을 전송하지 않습니다.

## 성숙도

- `indexed`: 이름과 source만 확인한 항목으로, 탐색에 사용합니다.
- `normalized`: scope, alias와 관계를 정리 중인 항목으로, 정규화 작업에 사용합니다.
- `decision-ready`: problem, forces, preconditions, contraindications, guarantee, cost, failure mode와
  language realization을 검토한 항목으로, 추천에 사용합니다.
- `contextual`: 특정 조직·repository의 관찰 근거가 결합된 항목으로, 일반 catalog와 분리해 다룹니다.
- `superseded`: 현재 정책에서 다른 항목으로 대체한 항목으로, 관계를 따라 대체 항목을 확인합니다.

추천에는 `decision-ready` 항목을 사용합니다. 승격할 때에는 baseline보다 나은 조건, 비용과
반증 가능한 guarantee를 확인합니다. 원천의 이름이 사라지거나 의미가 바뀌면 기존 ID의 의미를
보존하고 relation과 migration을 기록합니다.

family 파일은 이름과 출처의 index를 소유하고, 승격 항목은 `decision-ready.json`에서만 정의합니다.
overlay는 원본 이름·family·level·출처를 유지하며 모든 판단 필드를 항목마다 직접 선언합니다.
preconditions, costs, failure_modes도 각 항목에 직접 선언합니다. 현재 선택 범위는 family마다 정확히 3개입니다.

현재 관찰 snapshot의 각 family는 정규화한 `id`, `name`, `source_path`, `sources` 목록의 digest로도
고정합니다. 원천을 다시 조사해 항목을 갱신할 때에는 실제 출처 근거와 함께 snapshot 상수, count와
관찰일을 같은 변경에서 갱신합니다.
