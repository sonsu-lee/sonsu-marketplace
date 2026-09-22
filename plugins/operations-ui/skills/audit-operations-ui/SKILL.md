---
name: audit-operations-ui
description: 기존 운영형 B2B, admin, back-office 또는 data-work UI의 사용자 판단, 정보 표현, 상태, interaction, responsive environment, accessibility와 결과 증거를 수정 없이 읽기 전용으로 감사할 때 사용한다. 구현·자동 수정·신규 화면 생성에는 사용하지 않는다.
---

# Audit Operations UI

대상 파일과 application data를 변경하지 않는다. file/DOM/rendered visual 읽기와 scroll, focus,
route/tab navigation만 허용한다. submit, create, update, delete, persisted toggle, test-data 생성은
하지 않으며 상태 변경 없이는 확인할 수 없는 항목을 `not_run` 또는 `inconclusive`로 둔다.

1. 관찰 근거에서 `design-decision-contract-v1`을 복원하고 미확인은 `unresolved_decisions`에 남긴다.
2. [공통 DQ0–DQ8](../../references/design-quality.md)과 [Operations 적용](../../references/quality-contract.md)을 판정한다.
3. DQ1–DQ6은 같은 artifact/contract에 연결된 evaluator run을 최소 하나 사용하고, 여러 run이면 최솟값과 divergence를 보존한다.
4. 실제 runtime을 관찰할 수 있으면 비파괴 scenario×environment receipt를 남긴다.
5. representative user/production 결과가 없으면 live DQ8과 `validated` 주장을 통과시키지 않는다.

각 finding에는 gate, severity, 관찰, 사용자 영향, 근거와 돌아갈 책임 단계를 기록한다. 근거가
부족하면 사실로 단정하지 않는다.

```bash
python3 <plugin-root>/scripts/validate_contracts.py screen-contract <contract.json>
python3 <plugin-root>/scripts/validate_contracts.py quality-report <report.json> <contract.json>
```
