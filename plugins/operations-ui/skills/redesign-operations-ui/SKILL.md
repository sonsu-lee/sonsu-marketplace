---
name: redesign-operations-ui
description: 기존 운영형 B2B, admin, back-office 또는 data-work 화면을 현재 기능·상태·action·permission·data shape를 보존하거나 명시적으로 변경하며 재설계할 때 사용한다. 신규 화면과 수정 없는 감사는 전용 스킬을 사용한다.
---

# Redesign Operations UI

[공통 디자인 품질 계약](../../references/design-quality.md)과 [Operations 계약](../../references/screen-contract.md)을
사용한다. 현재 화면을 보기 좋게 바꾸기 전에 관찰된 동작을 추적 가능한 계약으로 고정한다.

## 진행

1. 요청 산출물 범위와 쓰기 권한을 고정한다.
2. repo, 실제 화면, test에서 feature, state, action, permission, data-shape를 inventory로 만든다.
3. 모든 inventory ID에 근거, preserve/change, 이유, 구현 대상과 scenario를 지정한다.
4. inventory를 정확히 한 change contract에 연결하고 requirement↔scenario와 공통 scenario를 검증한다.
5. 사용자·맥락·primary question·오판 비용·정보·표현·환경·지표를 포함한 v2 계약을 잠근다.
6. 제품 디자인 시스템을 재사용해 변경하고 preserve/change scenario를 모두 재검증한다.
7. 현재 scope의 DQ gate와 Operations runtime evidence를 평가한다.

```bash
python3 <plugin-root>/scripts/validate_contracts.py screen-contract <contract.json>
python3 <plugin-root>/scripts/validate_contracts.py quality-report <report.json> <contract.json>
```

확인되지 않은 기존 동작을 계약에서 삭제하거나 “불필요”로 추정하지 않는다. critical 미결정은
영향 gate의 통과를 막되 독립 범위의 작업과 유효한 근거는 보존한다.
