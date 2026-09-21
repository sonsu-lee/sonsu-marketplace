---
name: design-operations-ui
description: 신규 운영형 B2B, admin, back-office 또는 data-work 화면을 제안·Figma·구현으로 설계할 때 사용한다. 반복 판단, 상태, 권한, 위험 행동과 실제 데이터가 핵심인 화면에 적용하며 기존 화면 재설계와 읽기 전용 감사는 전용 스킬을 사용한다.
---

# Design Operations UI

[산출물 경계](../../references/delivery.md)를 읽고 `proposal`, `figma`, `implementation`, `live` 중
현재 범위를 고정한다. [공통 디자인 품질 계약](../../references/design-quality.md)을 판단 기준으로,
[Operations 계약](../../references/screen-contract.md)을 도메인 확장으로 사용한다.

[DESIGN.md 형식과 CLI 검증](../../references/design-quality.md#designmd-형식과-cli-검증)에 따라
제품의 `DESIGN.md`를 작성·갱신하고 공식 CLI lint 결과를 완료 근거에 포함한다.

## 진행

1. 대상 저장소의 instruction, 제품 디자인 시스템, component, data/state boundary와 검증 도구를 읽는다.
2. 사용자·맥락·`primary_question`·오판 비용부터 Design Decision Contract에 고정한다.
3. 과업마다 must-know 정보, 표현 이유, 실제 상태, 환경과 outcome metric을 연결한다.
4. requirement↔scenario, action·permission·risk·state coverage를 완성하고 계약을 검증한다.
5. [디자인 원칙](../../references/design.md)에 따라 제품 token/component에 매핑해 요청 산출물을 만든다.
6. 현재 범위의 DQ gate를 평가한다. DQ1–DQ6은 작성자가 아닌 독립 평가자 2명이 판정한다.
7. implementation/live이면 실제 앱에서 scenario×environment [browser receipt](../../references/evidence-contract.md)를 수집한다.
8. live이면 사전 등록 metric과 위험도에 맞는 사용자 증거로 DQ8을 평가한다.

```bash
python3 <plugin-root>/scripts/validate_contracts.py screen-contract <contract.json>
python3 <plugin-root>/scripts/validate_contracts.py quality-report <report.json> <contract.json>
```

고정 색상·폭·radius를 제품 규칙처럼 강제하지 않는다. Figma는 명시 요청에서만 사용한다.
앞 단계가 통과해도 live 증거 전에는 `end_to_end_status: passed`를 주장하지 않는다.
