---
name: design-operations-ui
description: 신규 운영형 B2B, admin, back-office 또는 data-work 화면을 실제 코드로 설계·구현하면서 정보 구조, 상태, table, action, responsive behavior와 browser evidence를 함께 다뤄야 할 때 사용한다. 기존 화면의 기능 보존 재설계, 읽기 전용 감사, Figma-only 요청, marketing·editorial·brand page에는 사용하지 않는다.
---

# Design Operations UI

Precision Operations Console 디자인 언어로 신규 운영 화면을 구현한다. 예쁜 한 장보다 반복 작업, 상태 판단, 위험한 행동과 실제 데이터의 복원력을 우선한다.

## 시작

1. 대상 저장소의 instruction, framework, token, component, route, test와 browser harness를 읽는다.
2. [design](../../references/design.md)에서 적용 범위를 확인한다. operational/admin/data-work가 아니면 이 스킬을 적용하지 않는다.
3. [screen contract](../../references/screen-contract.md)에 따라 Screen Contract를 만든다. `unresolved_decisions`의 영향 영역과 의존성을 확인해 해당 작업만 보류하고, 계약이 확정된 독립 작업은 계속한다. 영향 경계를 확인할 수 없으면 그 경계부터 조사한다.
4. [tool routing](../../references/tool-routing.md)으로 이미 있는 구현·검증 도구를 선택한다.

Screen Contract JSON을 만든 직후 현재 스킬 위치에서 `../../scripts/validate_contracts.py`의
실제 경로를 해석해 다음 검증을 실행한다. 구조 검증 실패는 계약 오류를 먼저 수정한다.
검증 성공은 전체 구현 준비 완료를 뜻하지 않는다. 현재 실행할 작업의 요구·권한·상태가
확정됐는지는 조정자가 확인하며, 미결정 항목이 남은 전체 화면을 완료로 보고하지 않는다.

```bash
python3 <operations-ui-plugin-root>/scripts/validate_contracts.py screen-contract <screen-contract.json>
```

## 구현

[execution workflow](../../references/execution-workflow.md)의 신규 설계 흐름을 따른다.

- primary decision에 맞는 하나의 [screen pattern](../../references/screen-patterns.md)을 고르고 선택 이유를 남긴다.
- requirement와 [UX patterns](../../references/ux-patterns.md)을 evidence scenario에 연결한다.
- 기존 component와 semantic token을 우선하고 [design tokens](../../assets/design-tokens.json)에 mapping한다.
- loading, empty, error, permission-denied, zero, one, many, long-localized와 overflow의 적용 여부를 실제 데이터·호출 경계로 판단한다. 계약에서 도달 가능한 상태만 구현하고, 타입과 입력 경계가 배제한 상태를 위한 분기·guard를 만들지 않는다. 미확인은 도달 불가능으로 처리하지 않는다.
- 존재하지 않는 product behavior를 보기 좋다는 이유로 만들지 않는다.
- Figma는 사용자가 명시하지 않았다면 호출하거나 선행 조건으로 만들지 않는다.

## 검증과 반환

[quality contract](../../references/quality-contract.md), [evidence contract](../../references/evidence-contract.md), [accessibility](../../references/accessibility.md)을 적용한다. actual target app에서 required scenario×viewport Browser Evidence Receipt를 만들고 G0–G7을 판정한다.

required gate가 통과하지 못하면 [execution workflow의 재시도·종료 기준](../../references/execution-workflow.md#재시도와-종료)에 따라 가까운 책임 단계에서 수정하고 affected scenario와 관련 regression scenario를 다시 실행한다. target runtime이나 browser capability가 없으면 G7을 `not_run` 또는 `blocked`로 보고하며 `overall: passed`를 주장하지 않는다.

Quality Report JSON을 만든 뒤에는 같은 validator에 report와 검증한 Screen Contract를 함께
전달한다. 명령이 실패하면 출력된 contract 또는 gate의 책임 단계로 돌아가며 검증 전이나
실패 상태를 완료로 보고하지 않는다.

```bash
python3 <operations-ui-plugin-root>/scripts/validate_contracts.py quality-report <quality-report.json> <screen-contract.json>
```

결과에는 Screen Contract, 선택한 pattern, 변경 파일, deterministic checks, Quality Report, browser receipt와 미실행 항목을 구분해 포함한다.
