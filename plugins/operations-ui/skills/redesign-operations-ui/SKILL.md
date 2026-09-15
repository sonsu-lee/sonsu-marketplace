---
name: redesign-operations-ui
description: 기존 운영형 B2B, admin, back-office 또는 data-work 화면을 현재 기능, 상태, action, permission과 data shape를 보존하거나 명시적으로 변경하며 재설계 제안·Figma·구현을 만들 때 사용한다. 자연어 재설계 요청과 직접 호출을 모두 지원한다. 신규 설계와 수정 없는 감사는 전용 스킬로, 일반 콘텐츠 화면과 Figma 파일 자체의 구조 편집은 해당 전문 스킬로 선택한다.
---

# Redesign Operations UI

기존 화면의 동작을 먼저 증거로 고정하고 Precision Operations Console로 재설계한다. 시각 개선이 기능 손실을 가리지 못하게 inventory ID부터 browser scenario까지 추적한다.

## 산출물을 먼저 정한다

[산출물별 작업 경계](../../references/delivery.md)를 먼저 읽고 제안·Figma·구현을 구분한다.
제안/Figma에서는 현재 기능·값·상태·행동·권한·데이터 관계의 보존/변경을 짧은 명세로 연결하고
실제 시안 또는 Figma 결과를 확인해 해당 산출물 보고에서 끝낸다. 실행 코드·브라우저 매핑을
미리 요구하지 않는다. 일반 UI를 직접 지정한 경우에는 같은 문서의 일반 UI 경로에서 원본의
의미·동작을 보존하며 요청 산출물을 완성한다. 아래 JSON inventory·검증 절차는 운영형 웹 코드 구현 요청에 적용한다.

## 현재 동작 계약

1. repo instruction, implementation, route, test와 실제 화면을 읽는다.
2. [screen contract](../../references/screen-contract.md)의 Current Behavior Inventory 형식으로 feature, state, action, permission, data-shape를 기록한다.
3. 각 inventory ID에 `preserve` 또는 `change`, evidence, reason, implementation target과 scenario ID를 지정한다.
4. decision이나 mapping이 하나라도 없으면 구현하지 않고 `blocked`로 반환한다.

Current Behavior Inventory와 Change Contract를 포함한 Screen Contract JSON을 만든 직후 현재
스킬 위치에서 `../../scripts/validate_contracts.py`의 실제 경로를 해석해 검증한다. 실패하면
재설계를 시작하지 않고 inventory 또는 mapping 단계로 돌아간다.

```bash
python3 <operations-ui-plugin-root>/scripts/validate_contracts.py screen-contract <screen-contract.json>
```

사용자 요청이 읽기 전용 검토라면 `audit-operations-ui`를 사용한다. 기존 화면이 없으면 `design-operations-ui`를 사용한다.

## 재설계

[execution workflow](../../references/execution-workflow.md)의 재설계 흐름과 [design](../../references/design.md), [screen patterns](../../references/screen-patterns.md), [UX patterns](../../references/ux-patterns.md)을 적용한다.

- 기존 stack, component와 token을 먼저 재사용·매핑한다.
- 모든 preserve/change ID를 코드 위치와 browser scenario에 일대일로 연결한다.
- screen summary, filters, table, detail과 action hierarchy를 primary decision 중심으로 재구성한다.
- 실제 loading, empty, error, permission, long data, overflow와 action feedback을 보존하거나 Change Contract대로 변경한다.
- Figma는 사용자가 명시했을 때만 선택형 `figma-operations-flow`를 함께 사용한다.

## 보존 검증

[quality contract](../../references/quality-contract.md), [evidence contract](../../references/evidence-contract.md), [accessibility](../../references/accessibility.md)을 사용한다. preserve/change mapping coverage가 100%인지 확인하고 기존 scenario와 새 scenario를 actual browser에서 실행한다.

하나라도 보존 회귀가 있으면 inventory/change mapping 또는 구현 단계로 되돌린다. screenshot만 있거나 브라우저 실행이 없으면 G7은 통과하지 않는다. 결과에는 inventory, Change Contract, mapping coverage, 변경 파일, checks, Quality Report와 browser receipt를 포함한다.

Quality Report JSON을 만든 뒤에는 같은 validator로 report와 Screen Contract를 함께 검증한다.
실패하면 출력된 contract 또는 gate의 책임 단계로 돌아가며 `overall: passed`를 보고하지 않는다.

```bash
python3 <operations-ui-plugin-root>/scripts/validate_contracts.py quality-report <quality-report.json> <screen-contract.json>
```
