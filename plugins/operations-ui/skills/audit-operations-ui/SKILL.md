---
name: audit-operations-ui
description: 기존 운영형 B2B, admin, back-office 또는 data-work UI의 정보 구조, 디자인 시스템, 상태, interaction, responsive layout, accessibility와 browser evidence를 수정 없이 읽기 전용으로 검토할 때 사용한다. 구현, 자동 수정, 신규 화면 생성 또는 Figma canvas 변경 요청에는 사용하지 않는다.
---

# Audit Operations UI

대상 UI와 증거를 Precision Operations Console 품질 계약으로 읽기 전용 감사한다.

## 권한 경계

[execution workflow](../../references/execution-workflow.md)의 감사 흐름을 따른다. 허용되는 행위는 file, DOM, rendered visual 읽기와 application data를 바꾸지 않는 scroll, focus, route/tab navigation뿐이다.

submit, create, update, delete, persisted toggle, test-data creation, code formatting이나 file edit를 하지 않는다. 상태 변경 없이는 검증할 수 없는 항목을 `not_run` 또는 `inconclusive`로 남긴다. 사용자가 fix까지 요청했다면 감사 findings를 먼저 확정한 뒤 적절한 설계 또는 재설계 스킬로 별도 구현 흐름을 시작한다.

## 감사

1. [screen contract](../../references/screen-contract.md)의 필드를 코드, 문서와 현재 화면에서 복원한다. 확인할 수 없는 항목은 `unresolved_decisions`에 `id`, `area`, `reason`, `evidence_needed`, 영향받는 `gate_ids`로 표시한다.
2. [design](../../references/design.md), [screen patterns](../../references/screen-patterns.md), [UX patterns](../../references/ux-patterns.md), [accessibility](../../references/accessibility.md)을 기준으로 관찰한다.
3. [quality contract](../../references/quality-contract.md)의 G0–G7을 실제 증거 범위 안에서만 판정한다.
4. [evidence contract](../../references/evidence-contract.md)에 없는 주장과 screenshot-only interaction 주장을 거부한다.

각 finding에는 severity, target, contract rule, observed behavior, impact, evidence, return stage를 기록한다. evidence가 없으면 finding을 사실처럼 확정하지 않고 해당 gate를 `inconclusive` 또는 `not_run`으로 둔다.

audit의 `unresolved_decisions`가 남아 있으면 G0, 각 항목의 `gate_ids`와 `overall`을 `passed`로 판정하지 않는다. 다른 gate는 독립적인 증거가 있으면 별도로 판정할 수 있다.

감사용 Screen Contract와 Quality Report JSON을 만든 뒤 현재 스킬 위치에서
`../../scripts/validate_contracts.py`의 실제 경로를 해석해 두 명령을 실행한다. 첫 명령이
실패하면 contract 복원 단계로, 두 번째 명령이 실패하면 출력된 gate 판정 단계로 돌아간다.
검증 실패를 finding 부재나 `overall: passed`로 바꾸지 않는다.

```bash
python3 <operations-ui-plugin-root>/scripts/validate_contracts.py screen-contract <screen-contract.json>
python3 <operations-ui-plugin-root>/scripts/validate_contracts.py quality-report <quality-report.json> <screen-contract.json>
```

결과는 findings와 Quality Report이며 대상 파일을 변경하지 않았다고 명시한다.
