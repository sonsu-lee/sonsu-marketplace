# Operations UI

`operations-ui`는 상태·권한·대량 처리·부분 실패를 다루는 B2B/admin/data-work 화면을 위한
Codex 플러그인입니다. 특정 산업이나 고정된 시각 스타일이 아니라 사용자의 판단과 운영 과업을
기준으로 라우팅합니다.

## 판단 방식

모든 산출물은 [공통 디자인 품질 계약](references/design-quality.md)을 사용합니다.

- 먼저 사용자, 맥락, 화면의 핵심 질문과 오판 비용을 고정합니다.
- must-know 정보가 어떤 표현으로 어떤 과업을 돕는지 추적합니다.
- 대상 제품의 component·semantic token을 사용하고 매핑 근거를 남깁니다.
- viewport를 고정값으로 가정하지 않고 실제 기기·locale·writing mode·입력 방식으로 선언합니다.
- proposal은 DQ0–DQ6, Figma/implementation은 DQ0–DQ7, live 평가는 DQ0–DQ8을 각각 통과해야 합니다.
- DQ1–DQ6은 독립 평가자 2명의 최솟값이 3 이상이어야 하며, 차이가 크면 평균 대신 재판정합니다.

Operations 전용 확장은 requirement↔scenario, 현재 동작 inventory↔change contract,
scenario×environment 브라우저 증거를 보존합니다. 정적 시안·Figma·스크린샷은 실행 증거를
대체하지 않습니다.

## 스킬

- `design-operations-ui`: 신규 운영 화면의 proposal, Figma, 구현
- `redesign-operations-ui`: 기존 동작을 보존하거나 명시적으로 바꾸는 재설계
- `audit-operations-ui`: 대상을 변경하지 않는 읽기 전용 감사
- `figma-operations-flow`: 명시적으로 요청된 Figma 화면·상태·prototype

## 검증

```bash
python3 scripts/validate_contracts.py screen-contract assets/examples/outbound-management/screen-contract.json
python3 scripts/validate_contracts.py quality-report assets/examples/outbound-management/quality-report.json assets/examples/outbound-management/screen-contract.json
python3 scripts/validate_contracts.py evals ../../evals/operations-ui/cases.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

예제 Quality Report는 실제 앱을 실행하지 않았으므로 `not_run`입니다. 구조 검증 성공을 화면 품질이나
사용자 성과 검증으로 해석하지 않습니다.
